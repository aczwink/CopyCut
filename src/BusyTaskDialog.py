__license__ = u"""
Copyright (c) 2017-2018 Amir Czwink (amir130@hotmail.de)

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

class BusyTaskDialog(QDialog):
	#Constructor
	def __init__(this, parent, title):
		QDialog.__init__(this, parent);
		
		this.__statusText = "";		
		this.finished = False;
		
		this.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.MSWindowsFixedSizeDialogHint);
		this.setSizeGripEnabled(False);
		this.setWindowTitle("Executing Task: " + title);
		
		layout = QVBoxLayout();
		
		bar = QProgressBar();
		bar.setRange(0, 0);
		bar.setTextVisible(False);
		bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed));
		layout.addWidget(bar);
		layout.setAlignment(bar, Qt.AlignHCenter);
		
		this.__status = QLabel();
		layout.addWidget(this.__status);
		layout.setAlignment(this.__status, Qt.AlignHCenter);
		
		this.__timer = QTimer();
		this.__timer.timeout.connect(this.__OnTimerUpdate);
		
		this.setLayout(layout);
		
	#Public methods
	def Run(this):
		this.__OnTimerUpdate();
		this.__timer.start(100);
		this.exec_();
		
	def UpdateStatus(this, newStatus):
		this.__statusText = newStatus;
		
	#Event handlers
	def __OnTimerUpdate(this):
		if(this.finished):
			this.close();
			
		if(this.__status.text() != this.__statusText):
			this.__status.setText(this.__statusText);