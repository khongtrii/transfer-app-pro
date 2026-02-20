import sys
from PyQt6 import QtWidgets, uic
from functions import *

print("""
    FILE TRANSFER APPLICATION
      1. I am a sender.
      2. I am a receiver.
""")

while True:
    option = input("Choose: ").strip()
    if option in ("1", "2"):
        break
    print("Invalid choice. Please choose 1 or 2.\n")

app = QtWidgets.QApplication(sys.argv)

if option == "1":
    window = SenderWindow()
else:
    window = ReceiverWindow()

window.show()
sys.exit(app.exec())