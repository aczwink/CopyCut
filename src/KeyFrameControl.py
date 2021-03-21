__license__ = u"""
Copyright (c) 2018,2021 Amir Czwink (amir130@hotmail.de)

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
from enum import Enum;
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtWidgets import *;

from Util import TimeStampToString;

class StreamChangeBehavior(Enum):
	JumpToStart = 1
	JumpToEnd = 2
	MinimizeDistance = 3

class KeyFrameControl(QWidget):
	#Constructor
	def __init__(this, streamChangeBehavior, includeEnd = False, includeStart = False):
		QWidget.__init__(this);
		
		this.__streamChangeBehavior = streamChangeBehavior;
		this.__activeStreamIndex = None;
		this.__videoAnalyzer = None;
		this.__includeStart = includeStart;
		this.__includeEnd = includeEnd;
		
		layout = QHBoxLayout();
		
		this.__spinBox = QSpinBox();
		this.__spinBox.setEnabled(False);
		this.OnKeyFrameChanged(this.__OnKeyFrameChanged);
		layout.addWidget(this.__spinBox);
		
		this.__keyFrameTime = QLabel();
		layout.addWidget(this.__keyFrameTime);
		
		this.setLayout(layout);
		
	#Public methods
	def GetCurrentKeyFrame(this):
		if(this.__activeStreamIndex is None):
			return None;
		if(this.__spinBox.maximum() == -1):
			return None; #empty key frame list
		return this.__spinBox.value();
		
	def OnKeyFrameChanged(this, callback):
		this.__spinBox.valueChanged.connect(callback);
		
	def SetActiveStreamIndex(this, activeStreamIndex):
		oldT = 0;
		if((this.__streamChangeBehavior == StreamChangeBehavior.MinimizeDistance) and (this.__activeStreamIndex is not None)):
			keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
			if(this.GetCurrentKeyFrame() is not None):
				oldT = keyFrameList[this.GetCurrentKeyFrame()];
		
		this.__activeStreamIndex = activeStreamIndex;
		
		keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
		
		delta = 0;
		if(this.__includeEnd):
			delta = 1; #+ the end of video marker
			
		if(this.__includeStart):
			this.__spinBox.setMinimum(-1);
		else:
			this.__spinBox.setMinimum(0);
		
		maxKeyFrame = len(keyFrameList) - 1;
		this.__spinBox.setMaximum(maxKeyFrame + delta);
		
		if(this.__streamChangeBehavior == StreamChangeBehavior.JumpToStart):
			this.__spinBox.setValue(0);
		elif(this.__streamChangeBehavior == StreamChangeBehavior.JumpToEnd):
			this.__spinBox.setValue(maxKeyFrame + delta);
		else:
			bestIdx = 0;
			bestDistance = 1e100;
			
			for i in range(0, len(keyFrameList)):
				d = abs(keyFrameList[i] - oldT);
				if(d < bestDistance):
					bestIdx = i;
					bestDistance = d;
			this.__spinBox.setValue(bestIdx);
			
		this.__UpdateKeyFrameTime();		
		this.__spinBox.setEnabled(maxKeyFrame != -1);
		
	def SetKeyFrame(this, keyFrame):
		this.__spinBox.blockSignals(True);
		this.__spinBox.setValue(keyFrame);
		this.__UpdateKeyFrameTime();
		this.__spinBox.blockSignals(False);
		
	def SetVideoAnalyzer(this, analyzer):
		this.__videoAnalyzer = analyzer;
		
	#Private methods
	def __UpdateKeyFrameTime(this):
		keyFrameNumber = this.GetCurrentKeyFrame();
		if((this.__activeStreamIndex is None) or (keyFrameNumber is None)):
			text = "--:--:--.-";
		else:
			keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
			if(this.__includeStart and (keyFrameNumber == -1)):
				text = "--:--:--.-" + " (start of video)";
			elif(this.__includeEnd and (keyFrameNumber == len(keyFrameList))):
				text = TimeStampToString(this.__videoAnalyzer.GetDuration()) + " (end of video)";
			else:
				ts = keyFrameList[keyFrameNumber];
				text = TimeStampToString(ts);
				
		this.__keyFrameTime.setText("@ " + text);
		
	#Event handlers
	def __OnKeyFrameChanged(this):
		this.__UpdateKeyFrameTime();
