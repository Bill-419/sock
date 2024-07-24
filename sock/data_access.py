import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from database import save_data, load_data, append_row, delete_last_row
from redis_client import get_data, save_data_to_redis

executor = ThreadPoolExecutor(max_workers=10)

async def read_data(table_name):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, get_data, table_name, table_name)

def write_data_task(table_name, data):
    save_data(table_name, data)
    save_data_to_redis(table_name, data)

async def write_data(table_name, data):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, Thread(target=write_data_task, args=(table_name, data)).start)

def append_row_task(table_name, data):
    append_row(table_name, data)
    new_data = load_data(table_name)
    save_data_to_redis(table_name, new_data)

async def append_row_data(table_name, data):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, Thread(target=append_row_task, args=(table_name, data)).start)

def delete_last_row_task(table_name):
    delete_last_row(table_name)
    new_data = load_data(table_name)
    save_data_to_redis(table_name, new_data)

async def delete_last_row_data(table_name):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, Thread(target=delete_last_row_task, args=(table_name)).start)
