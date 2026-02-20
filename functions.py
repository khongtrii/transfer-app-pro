import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog, QListWidget
from network.functions import *
from network.sender import *
from network.receiver import *

import numpy as np

class ReceiverWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"UI\fileReceiveUI.ui", self)

        self.getBtn.clicked.connect(self.start_connect)

    def start_connect(self):
        host = self.hostIPadd.text()
        self.client = ReceiverClient(host=host)

        self.client.connected.connect(self.on_connected)
        self.client.failed.connect(self.on_failed)

        self.client.connect()

    def on_connected(self, msg):
        print("Server says:", msg)

    def on_failed(self, msg):
        print("Connection failed:", msg)

    def closeEvent(self, event):
        if hasattr(self, "client"):
            self.client.close()
        event.accept()       


class SenderWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"UI\fileTransferUI.ui", self)

        self.serverStatus.setStyleSheet("""
            min-width:10px;
            min-height:10px;
            max-width:10px;
            max-height:10px;
            border-radius:5px;
            background-color:red;
        """)
        
        self.server = SenderServer()
        self.server.ping_started.connect(self._ping_successed)
        self.server.ping_failed.connect(self._ping_failed)
        self.server._ping()

        self.browseFileBtn.clicked.connect(self._fileBrowse)

        self.progressBar.setValue(0)

    def _ping_successed(self):
        self.serverStatus.setStyleSheet("""
            min-width:10px;
            min-height:10px;
            max-width:10px;
            max-height:10px;
            border-radius:5px;
            background-color:#00c853;
        """)

    def _ping_failed(self, msg):
        self.serverStatus.setStyleSheet("""
            min-width:10px;
            min-height:10px;
            max-width:10px;
            max-height:10px;
            border-radius:5px;
            background-color:orange;
        """)
        print("Server error:", msg)

    def _fileBrowse(self):
        files = QFileDialog.getOpenFileNames(caption="Select File")
        if files[0]:
            self.filePaths.clear()
            self.filePaths.addItems(files[0])
            self.filePaths.show()

    def _updateProgress(self, cur, total):
        if total <= 0:
            percent = 0
        else:
            ratio = cur / total
            ratio = max(0.0, min(1.0, ratio))
            percent = round(ratio * 100)

        self.progressBar.setValue(percent)


    def closeEvent(self, a0):
        self.server._stop()
        a0.accept()