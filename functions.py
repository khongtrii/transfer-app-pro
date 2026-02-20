import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog
from network.functions import *
from network.sender import *
from network.receiver import *
    
class ReceiverWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"UI\fileReceiveUI.ui", self)

        self.client = ReceiverClient(host=self.hostIPadd.text())
        self.getBtn.clicked.connect(self.client.connect())
        


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
        self.server.server_started.connect(self.on_server_started)
        self.server.server_failed.connect(self.on_server_failed)
        self.server.start()

        self.browseFileBtn.clicked.connect(self.browse_file)

        self.label_2.setText(getIp())

        self.filePaths.clear()

        self.sentBtn.clicked.connect(self.updateProgressBar)
        self.sentBtn.setEnabled(False)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

    def on_server_started(self):
        self.serverStatus.setStyleSheet("""
            min-width:10px;
            min-height:10px;
            max-width:10px;
            max-height:10px;
            border-radius:5px;
            background-color:#00c853;
        """)

    def on_server_failed(self, msg):
        self.serverStatus.setStyleSheet("""
            min-width:10px;
            min-height:10px;
            max-width:10px;
            max-height:10px;
            border-radius:5px;
            background-color:orange;
        """)
        print("Server error:", msg)

    def browse_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File")
        if file_paths:
            self.filePaths.clear()
            self.filePaths.addItems(file_paths)
            self.sentBtn.setEnabled(True)

    def updateProgressBar(self):
        current = self.progressBar.value()
        if current < 100:
            self.progressBar.setValue(current + 10)

    def closeEvent(self, event):
        self.server.stop()
        event.accept()