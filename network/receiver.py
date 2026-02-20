import asyncio
import json

CHUNK_SIZE = 65536

class ReceiverClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        msg = await self.reader.readline()
        print(msg.decode().strip())
        
    async def get_file_list(self):
        self.writer.write(b"GET_FILE_LIST\n")
        await self.writer.drain()

        data = await self.reader.readline()
        files = json.loads(data.decode())
        return files

    async def download_file(self, filename, save_path):
        self.writer.write(f"REQUEST {filename}\n".encode())
        await self.writer.drain()

        header = await self.reader.readline()
        header = header.decode().strip()

        if not header.startswith("FILE"):
            return False

        _, size = header.split(" ")
        size = int(size)

        received = 0
        with open(save_path, "wb") as f:
            while received < size:
                chunk = await self.reader.read(min(CHUNK_SIZE, size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        return True

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
