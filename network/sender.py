from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import threading

class SenderServer(QObject):
    server_started = pyqtSignal()
    server_failed = pyqtSignal(str)

    def __init__(self, host="0.0.0.0", port=8888):
        super().__init__()
        self.host = host
        self.port = port
        self._server = None
        self._loop = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            asyncio.run(self._main())
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                self.server_failed.emit(str(e))

    async def _main(self):
        self._loop = asyncio.get_running_loop()

        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        self.server_started.emit()

        async with self._server:
            try:
                await self._server.serve_forever()
            except asyncio.CancelledError:
                pass

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(1024)
            writer.write(b"Connected\n")
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    def stop(self):
        if self._server:
            self._loop.call_soon_threadsafe(self._server.close)
