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
import os;
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer;
from PyQt5.QtMultimediaWidgets import QVideoWidget;
from PyQt5.QtWidgets import *;

class VideoPlayerWidget(QVideoWidget):
	#Constructor
	def __init__(this, parent):
		QVideoWidget.__init__(this);
		
		this.__parent = parent;		
		this.__mediaPlayer = None;
		this.__keyFrameList = [];
		this.__currentKeyFrameIdx = 0;
		
		this.setAutoFillBackground(True);
		
	#Public methods
	def IsPlaying(this):
		if(this.__mediaPlayer is None):
			return False;
		return this.__mediaPlayer.state() == QMediaPlayer.PlayingState;
		
	def JumpToKeyFrame(this, keyFrame):
		this.__currentKeyFrameIdx = keyFrame;
		ts = this.__GetScaledKeyFrameTime(this.__currentKeyFrameIdx);
		this.__mediaPlayer.setPosition(ts);
		
		this.__parent.OnKeyFrameChangedByPlayback(this.__currentKeyFrameIdx);
		
	def JumpToNextKeyFrame(this):
		this.JumpToKeyFrame(this.__currentKeyFrameIdx + 1);
		
	def JumpToPrevKeyFrame(this):
		this.JumpToKeyFrame(this.__currentKeyFrameIdx - 1);
		
	def PlayPause(this):
		if(this.__mediaPlayer is not None):
			if(this.IsPlaying()):
				this.__mediaPlayer.pause();
			else:
				this.__mediaPlayer.play();
			
	def SetFile(this, path):
		this.__currentKeyFrameIdx = 0;
		
		path = os.path.abspath(path);
		this.__mediaPlayer = QMediaPlayer();
		this.__mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)));
		this.__mediaPlayer.setVideoOutput(this);
		
		this.__mediaPlayer.positionChanged.connect(this.__OnPositionChanged);
		
		this.__mediaPlayer.play();
		this.__mediaPlayer.pause();
		
	def SetKeyFrameList(this, keyFrameList):
		this.__keyFrameList = keyFrameList;
		
		this.JumpToKeyFrame(this.__currentKeyFrameIdx);
		
	#Event handlers
	def mousePressEvent(this, event):
		if(event.button() == Qt.LeftButton):
			fltPos = event.x() / float(this.width());
			duration = this.__mediaPlayer.duration();
			pos = fltPos * duration;
			keyFrame = this.__GetNextKeyFrame(pos);
			this.JumpToKeyFrame(keyFrame);
			
	#Private methods
	def __GetNextKeyFrame(this, pos):
		for i in range(0, len(this.__keyFrameList)):
			ts = this.__GetScaledKeyFrameTime(i);
			if(ts > pos):
				return i;
				
		return None;
		
	def __GetScaledKeyFrameTime(this, keyFrame):
		ts = this.__keyFrameList[keyFrame];
		
		return ts // 1000000;
		
	#Event handlers
	def __OnPositionChanged(this, pos):
		if(this.IsPlaying()):
			oldIdx = this.__currentKeyFrameIdx;
			while(this.__currentKeyFrameIdx < len(this.__keyFrameList)):
				if(this.__currentKeyFrameIdx < len(this.__keyFrameList)-1 and pos > this.__GetScaledKeyFrameTime(this.__currentKeyFrameIdx+1) ):
					this.__currentKeyFrameIdx += 1;
				elif(pos < this.__GetScaledKeyFrameTime(this.__currentKeyFrameIdx)):
					this.__currentKeyFrameIdx -= 1;
				else:
					break;
					
			if(not(oldIdx == this.__currentKeyFrameIdx)):
				this.__parent.OnKeyFrameChangedByPlayback(this.__currentKeyFrameIdx);
"""
		this.__currentVideo = None;
		this.__currentSection = None;
		this.__queryNewEntries = False;
		
		this.__mediaPlayer.durationChanged.connect(this.__OnDurationChanged);
		this.__mediaPlayer.mediaStatusChanged.connect(this.__OnMediaStatusChanged);
		this.__mediaPlayer.stateChanged.connect(this.__OnStateChanged);
		
	def __OnDurationChanged(this, duration):
		this.duration = duration;
		
	def __OnMediaStatusChanged(this, status):
		if(status == QMediaPlayer.EndOfMedia):
			this.__mediaPlayer.stop();
			
	def __OnStateChanged(this, state):
		if(state == QMediaPlayer.StoppedState):
			this.__currentVideo = None;
			if(this.__queryNewEntries):
				this.Play();
			
	def keyReleaseEvent(this, keyEvent):
		if(keyEvent.key() == Qt.Key_Escape):
			this.__container.InformStop();
			
	#Private methods
	def __GetEndTime(this):
		if(this.__currentSection is not None):
			if(this.__currentSection.endTime is not None):
				return this.__currentSection.endTime;
				
		return None;
		
	def __GetStartTime(this):
		if(this.__currentSection is not None):
			if(this.__currentSection.startTime is not None):
				return this.__currentSection.startTime;
				
		return None;
"""
