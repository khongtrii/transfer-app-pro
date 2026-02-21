import asyncio
import threading
from PyQt6.QtCore import QObject, pyqtSignal


class ReceiverClient(QObject):
    connected = pyqtSignal(str)
    failed = pyqtSignal(str)
    file_received = pyqtSignal(bytes)

    def __init__(self, host, port=8888):
        super().__init__()
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.loop = None

    def host(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._connect())
            self.loop.run_forever()
        except Exception as e:
            self.failed.emit(str(e))

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port
        )
        self.connected.emit("Connected")

    def send_list(self):
        if self.writer and self.loop:
            asyncio.run_coroutine_threadsafe(
                self._send_list(),
                self.loop
            )

    async def _send_list(self):
        self.writer.write(b"PING_LIST\n")
        await self.writer.drain()
        data = await self.reader.read(4096)
        self.connected.emit(data.decode())

    def send_get(self, filename):
        if self.writer and self.loop:
            asyncio.run_coroutine_threadsafe(
                self._send_get(filename),   
                self.loop
            )

    async def _send_get(self, filename):
        cmd = f"GET {filename}\n"
        self.writer.write(cmd.encode())
        await self.writer.drain()

        file_data = bytearray()
        while True:
            chunk = await self.reader.read(8192)
            if not chunk:
                break
            file_data.extend(chunk)

        self.file_received.emit(bytes(file_data))

    def close(self):
        if self.writer and self.loop:
            asyncio.run_coroutine_threadsafe(
                self._close(),
                self.loop
            )

    async def _close(self):
        self.writer.close()
        await self.writer.wait_closed()
        self.loop.stop()