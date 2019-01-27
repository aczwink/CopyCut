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

class StreamSourceController(QAbstractItemModel):
	def __init__(this, videoAnalyzer):
		QAbstractItemModel.__init__(this);
		
		this.__choices = [];
		if(videoAnalyzer.GetCombinedKeyFrameList()): #only offer streams with keyframes
			this.__choices.append(("Combined (safest) - " + str(len(videoAnalyzer.GetCombinedKeyFrameList())) + " keyframes", -1));
		for streamIndex in sorted(videoAnalyzer.GetStreams()):
			streamType = videoAnalyzer.GetStreams()[streamIndex];
			if(videoAnalyzer.GetStreamKeyFrameList(streamIndex)): #only offer streams with keyframes
				this.__choices.append(("Stream " + str(streamIndex) + " - " + streamType + " - " + str(len(videoAnalyzer.GetStreamKeyFrameList(streamIndex))) + " keyframes", streamIndex));
		
	#Public methods
	def GetStreamIndexForControllerIndex(this, index):
		_,streamIndex = this.__choices[index];
		
		return streamIndex;
		
	#Interface
	def columnCount(this, parent):
		return 1;
		
	def data(this, index, role):
		if(role == Qt.DisplayRole):
			string, _ = this.__choices[index.row()];
			return QVariant(string);
	
	def index(this, row, col, parent):
		return this.createIndex(row, col);
		
	def parent(this, child):		
		return QModelIndex();
		
	def rowCount(this, parent):
		if(not parent.isValid()):
			return len(this.__choices);
			
		return 0;