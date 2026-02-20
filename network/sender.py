from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import threading

class SenderServer(QObject):

    ping_started = pyqtSignal()
    ping_failed = pyqtSignal(str)


    def __init__(self, host='0.0.0.0', port='8888'):
        super().__init__()
        self.host = host
        self.port = port
        self._server = None
        self._loop = None
        self._task = None

    def _ping(self):
        threading.Thread(
            target=self._active,
            daemon=True
        ).start()
    
    def _active(self):
        try:
            asyncio.run(
                self._main()
            )
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                self.ping_failed.emit(str(e))
    
    async def _main(self):
        self._loop = asyncio.get_running_loop()

        self._server = await asyncio.start_server(
            client_connected_cb=self._handle,
            host=self.host,
            port=self.port
        )

        self.ping_started.emit()

        self._serve_task = asyncio.create_task(self._server.serve_forever())

        try:
            await self._serve_task
        except asyncio.CancelledError:
            pass
        finally:
            self._server.close()
            await self._server.wait_closed()

    async def _handle(self, reader, writer):
        pass

    def _stop(self):
        if self._loop and self._serve_task:
            def shutdown():
                self._serve_task.cancel()

            self._loop.call_soon_threadsafe(shutdown)