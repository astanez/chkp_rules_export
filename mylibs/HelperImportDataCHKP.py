import sys, os, csv
import sqlite3
import itertools
import ipaddress



from PySide2.QtWidgets import (
    QMainWindow,    
    QMessageBox,
)


def ip_valid(_ip, _varName):
    result = True
    ip=""
    try:
        ip = ipaddress.ip_address(_ip)
    except:
        msg = QMessageBox()
        msg.setWindowTitle("IP validation")
        msg.setText(
            "Provided " + _varName + " is invalid. Please correct them and try again."
        )
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()  # this will show our messagebox
        result = False

    return result

