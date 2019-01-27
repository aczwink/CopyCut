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
import os;
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer;
from PyQt5.QtMultimediaWidgets import QVideoWidget;
from PyQt5.QtWidgets import *;

class VideoPlayerWidget(QVideoWidget):
	#Constructor
	def __init__(this, keyFrameCounter):
		QVideoWidget.__init__(this);
		
		this.__keyFrameCounter = keyFrameCounter;		
		this.__mediaPlayer = None;
		this.__activeStreamIndex = None;
		this.__videoAnalyzer = None;
		
	#Public methods
	def IsPlaying(this):
		if(this.__mediaPlayer is None):
			return False;
		return this.__mediaPlayer.state() == QMediaPlayer.PlayingState;
		
	def JumpToKeyFrame(this, keyFrame):
		if(keyFrame is None):
			return;
			
		this.__currentKeyFrameIdx = keyFrame;
			
		ts = this.__GetScaledKeyFrameTime(keyFrame);
		this.__mediaPlayer.setPosition(ts);
		
		if(not this.IsPlaying()):
			this.__keyFrameCounter.SetKeyFrame(keyFrame);
		
	def PlayPause(this):
		if(this.__mediaPlayer is not None):
			if(this.IsPlaying()):
				this.__mediaPlayer.pause();
			else:
				this.__mediaPlayer.play();
				
	def SetActiveStreamIndex(this, activeStreamIndex):
		this.__activeStreamIndex = activeStreamIndex;
			
	def SetFile(this, path):
		this.__currentKeyFrameIdx = 0;
		
		path = os.path.abspath(path);
		this.__mediaPlayer = QMediaPlayer();
		this.__mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)));
		this.__mediaPlayer.setVideoOutput(this);
		
		this.__mediaPlayer.positionChanged.connect(this.__OnPositionChanged);
		
		this.__mediaPlayer.play();
		this.__mediaPlayer.pause();
		
	def SetVideoAnalyzer(this, analyzer):
		this.__videoAnalyzer = analyzer;
		
	#Event handlers
	def mousePressEvent(this, event):
		if(event.button() == Qt.LeftButton):
			fltPos = event.x() / float(this.width());
			duration = this.__mediaPlayer.duration();
			pos = fltPos * duration;
			keyFrame = this.__GetClosestKeyFrame(pos);
			if(keyFrame is not None):
				this.JumpToKeyFrame(keyFrame);
			
	#Private methods
	def __GetClosestKeyFrame(this, pos):
		keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
		
		lastDistance = 1e100;		
		for i in range(0, len(keyFrameList)):
			ts = this.__GetScaledKeyFrameTime(i);
			d = abs(ts - pos);
			if(d > lastDistance):
				return i - 1;
			lastDistance = d;
				
		return len(keyFrameList) - 1;
		
	def __GetScaledKeyFrameTime(this, keyFrame):
		keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
		ts = keyFrameList[keyFrame];
		
		return ts // 1000000;
		
	#Event handlers
	def __OnPositionChanged(this, pos):
		if(this.IsPlaying()):
			oldIdx = this.__currentKeyFrameIdx;
			keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
			
			while(this.__currentKeyFrameIdx < len(keyFrameList)):
				if(this.__currentKeyFrameIdx < len(keyFrameList)-1 and pos > this.__GetScaledKeyFrameTime(this.__currentKeyFrameIdx+1) ):
					this.__currentKeyFrameIdx += 1;
				elif(pos < this.__GetScaledKeyFrameTime(this.__currentKeyFrameIdx)):
					this.__currentKeyFrameIdx -= 1;
				else:
					break;
					
			if(not(oldIdx == this.__currentKeyFrameIdx)):
				this.__keyFrameCounter.SetKeyFrame(this.__currentKeyFrameIdx);