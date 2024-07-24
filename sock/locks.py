import asyncio

class ReadWriteLock:
    def __init__(self):
        self.readers = 0
        self.writer = False
        self.read_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()
        self.read_event = asyncio.Event()
        self.read_event.set()

    async def acquire_read(self):
        async with self.read_lock:
            while self.writer:
                await self.read_event.wait()
            self.readers += 1

    async def release_read(self):
        async with self.read_lock:
            self.readers -= 1
            if self.readers == 0:
                self.read_event.set()

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
