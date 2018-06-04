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

class DragHintWidget(QWidget):
	#Event handlers
	def PlayPause(this):
		pass
		
	def paintEvent(this, event):		
		painter = QPainter(this);
		
		painter.fillRect(this.rect(), QColor());
		
		font = painter.font();
		font.setPixelSize(48);
		painter.setFont(font);
		
		pen = painter.pen();
		pen.setColor(QColor(Qt.white));
		painter.setPen(pen);
		
		painter.drawText(this.rect(), Qt.AlignHCenter | Qt.AlignVCenter, "Drag your video files in here...");