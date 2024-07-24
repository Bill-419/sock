import socketio
import threading
from time import sleep

class DataClient:
    def __init__(self, server_url):
        self.sio = socketio.Client()
        self.server_url = server_url

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('write_response', self.on_write_response)
        self.sio.on('append_row_response', self.on_append_row_response)
        self.sio.on('delete_last_row_response', self.on_delete_last_row_response)
        self.sio.on('read_response', self.on_read_response)
        self.sio.on('write_broadcast', self.on_write_broadcast)
        self.sio.on('append_row_broadcast', self.on_append_row_broadcast)
        self.sio.on('delete_last_row_broadcast', self.on_delete_last_row_broadcast)

    def on_connect(self):
        print('Connected to server')

    def on_disconnect(self):
        print('Disconnected from server')

    def on_write_response(self, data):
        print('Write completed:', data)
        self.read(data['table'])

    def on_append_row_response(self, data):
        print('Append row completed:', data)
        self.read(data['table'])

    def on_delete_last_row_response(self, data):
        print('Delete last row completed:', data)
        self.read(data['table'])

    def on_read_response(self, data):
        print('Read completed:', data)

    def on_write_broadcast(self, data):
        print('Write broadcast received:', data)

    def on_append_row_broadcast(self, data):
        print('Append row broadcast received:', data)

    def on_delete_last_row_broadcast(self, data):
        print('Delete last row broadcast received:', data)

    def connect(self):
        self.sio.connect(self.server_url)

    def disconnect(self):
        self.sio.disconnect()

    def write(self, table, rows):
        self.sio.emit('write', {'table': table, 'rows': rows})

    def append_row(self, table, row):
        self.sio.emit('append_row', {'table': table, 'row': row})

    def delete_last_row(self, table):
        self.sio.emit('delete_last_row', {'table': table})

    def read(self, table):
        self.sio.emit('read', {'table': table})

def test_client_operations():
    client = DataClient('http://localhost:5000')
    client.connect()
    client.write('test_table', [{'row': 1, 'col': 1, 'text': 'Hello', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': True, 'size': 14}, 'row_height': 20, 'column_width': 100}])
    client.append_row('test_table', {'row': 2, 'col': 2, 'text': 'World', 'foreground': '#FF0000', 'background': '#00FF00', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 25, 'column_width': 150})
    client.delete_last_row('test_table')
    sleep(5)
    client.disconnect()

if __name__ == "__main__":
    test_threads = []
    for _ in range(10):
        t = threading.Thread(target=test_client_operations)
        t.start()
        test_threads.append(t)
        sleep(1)

    for t in test_threads:
        t.join()

    print("All client tasks completed.")
