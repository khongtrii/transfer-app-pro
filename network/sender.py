from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import threading
import os
import shutil
import json
class SenderServer(QObject):

    ping_started = pyqtSignal()
    ping_failed = pyqtSignal(str)
    ping_shared = pyqtSignal(list)
    ping_client = pyqtSignal(str)


    def __init__(self, host='0.0.0.0', port='8888'):
        super().__init__()
        self.host = host
        self.port = port
        self._server = None
        self._loop = None
        self._task = None

        self.shared_dir = os.path.join(os.getcwd(), "shared")
        os.makedirs(self.shared_dir, exist_ok=True)

        self.shared_files = []

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
        client = writer.get_extra_info("peername")
        self.ping_client.emit(f"{client[0]}:{client[1]}")
        
        try:
            data = await reader.read(1024)
            msg = data.decode().strip()

            if msg == 'PING_LIST':
                payload = json.dumps(self.shared_files)
                writer.write(payload.encode())
                await writer.drain()
            elif msg.startswith("PING_GET"):
                _, filename = msg.split(" ", 1)
                for file in self.shared_files:
                    if file["name"] == filename:
                        with open(file["path"], "rb") as f:
                            while chunk := f.read(8192):
                                writer.write(chunk)
                                await writer.drain()
                        break

        except Exception as e:
            print("Error :", e)
            
        finally:
            writer.close()
            await writer.wait_closed()

    def _reload_shared(self):
        self.shared_files.clear()

        for filename in os.listdir(self.shared_dir):
            full_path = os.path.join(self.shared_dir, filename)
            if os.path.isfile(full_path):
                file_info = {
                    "name": filename,
                    "size": os.path.getsize(full_path),
                    "path": full_path
                }
                self.shared_files.append(file_info)

        self.ping_shared.emit(self.shared_files)

    def _addFile(self, paths):
        for path in paths:
            if not os.path.isfile(path):
                continue

            filename = os.path.basename(path)
            dest_path = os.path.join(self.shared_dir, filename)

            base, ext = os.path.splitext(filename)
            counter = 1

            while os.path.exists(dest_path):
                new_name = f"{base}_{counter}{ext}"
                dest_path = os.path.join(self.shared_dir, new_name)
                counter += 1

            shutil.copy2(path, dest_path)

        self._reload_shared()

    def _refreshFile(self):
        if hasattr(self, "shared_dir") and os.path.exists(self.shared_dir):
            for filename in os.listdir(self.shared_dir):
                file_path = os.path.join(
                    self.shared_dir, filename
                )
                if os.path.isfile(file_path):
                    os.remove(file_path)
        self.shared_files.clear()
        self.ping_shared.emit(self.shared_files)


    def _stop(self):
        if self._loop and self._serve_task:
            def shutdown():
                self._serve_task.cancel()

            self._loop.call_soon_threadsafe(shutdown)