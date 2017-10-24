from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtWidgets import *;
import sys;

from MainWindow import MainWindow;

app = QApplication(sys.argv);

mainWindow = MainWindow();
if(len(sys.argv) == 2):
	mainWindow.LoadFile(sys.argv[1]);

mainWindow.show();
app.exec_();
