__license__ = u"""
Copyright (c) 2017 Amir Czwink (amir130@hotmail.de)

This file is part of CopyCut.

CopyCut is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CopyCut is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CopyCut.  If not, see <https://www.gnu.org/licenses/>.
"""
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
