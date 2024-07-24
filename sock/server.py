from flask import Flask
from flask_socketio import SocketIO, emit
import asyncio
from data_access import read_data, write_data, append_row_data, delete_last_row_data
from threading import Thread
from database import create_table, init_db

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Initialize the database and create the table
init_db()
create_table('test_table')

class ReadWriteLock:
    def __init__(self):
        self.readers = 0
        self.writer = False
        self.read_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()
        self.read_event = asyncio.Event()
        self.read_event.set()

    async def acquire_read(self):
        await self.read_lock.acquire()
        while self.writer:
            await self.read_event.wait()
        self.readers += 1
        self.read_lock.release()

    async def release_read(self):
        await self.read_lock.acquire()
        self.readers -= 1
        if self.readers == 0:
            self.read_event.set()
        self.read_lock.release()

    async def acquire_write(self):
        await self.write_lock.acquire()
        self.writer = True
        self.read_event.clear()
        while self.readers > 0:
            await asyncio.sleep(0.1)

    async def release_write(self):
        self.writer = False
        self.read_event.set()
        self.write_lock.release()

read_write_lock = ReadWriteLock()

@app.route('/')
def index():
    return 'Server is running!'

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('write')
def handle_write_event(json_data):
    table_name = json_data['table']
    rows = json_data['rows']
    thread = Thread(target=write_and_broadcast, args=(table_name, rows))
    thread.start()

def write_and_broadcast(table_name, rows):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(write_and_read_back(table_name, rows))
    finally:
        loop.close()

async def write_and_read_back(table_name, rows):
    await read_write_lock.acquire_write()
    try:
        await write_data(table_name, rows)
        socketio.emit('write_response', rows)
        socketio.emit('write_broadcast', {'table': table_name}, broadcast=True, include_self=False)
    finally:
        await read_write_lock.release_write()

@socketio.on('append_row')
def handle_append_row_event(json_data):
    table_name = json_data['table']
    row = json_data['row']
    thread = Thread(target=append_row_and_broadcast, args=(table_name, row))
    thread.start()

def append_row_and_broadcast(table_name, row):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(append_row_and_read_back(table_name, row))
    finally:
        loop.close()

async def append_row_and_read_back(table_name, row):
    await read_write_lock.acquire_write()
    try:
        await append_row_data(table_name, row)
        socketio.emit('append_row_response', row)
        socketio.emit('append_row_broadcast', {'table': table_name}, broadcast=True, include_self=False)
    finally:
        await read_write_lock.release_write()

@socketio.on('delete_last_row')
def handle_delete_last_row_event(json_data):
    table_name = json_data['table']
    thread = Thread(target=delete_last_row_and_broadcast, args=(table_name,))
    thread.start()

def delete_last_row_and_broadcast(table_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(delete_last_row_and_read_back(table_name))
    finally:
        loop.close()

async def delete_last_row_and_read_back(table_name):
    await read_write_lock.acquire_write()
    try:
        await delete_last_row_data(table_name)
        socketio.emit('delete_last_row_response', {'table': table_name})
        socketio.emit('delete_last_row_broadcast', {'table': table_name}, broadcast=True, include_self=False)
    finally:
        await read_write_lock.release_write()

@socketio.on('read')
def handle_read_event(json_data):
    table_name = json_data['table']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(read_data_with_lock(table_name))
        emit('read_response', result)
    finally:
        loop.close()

async def read_data_with_lock(table_name):
    await read_write_lock.acquire_read()
    try:
        result = await read_data(table_name)
        return result
    finally:
        await read_write_lock.release_read()

if __name__ == '__main__':
    socketio.run(app, debug=True)
