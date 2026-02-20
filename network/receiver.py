from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import threading

class ReceiverClient(QObject):
    connected = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, host, port=8888):
        super().__init__()
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    def connect(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            asyncio.run(self._connect())
        except Exception as e:
            self.failed.emit(str(e))

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port
        )

        msg = await self.reader.read(1024)
        self.connected.emit(msg.decode().strip())

    def close(self):
        if self.writer:
            self.writer.close()