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
from PyQt5.QtWidgets import *;
import re;
import subprocess;

class MainWindow(QWidget):
	#Constructor
	def __init__(this):
		super(MainWindow, this).__init__(None);
		
		#Private members
		this.__path = None;
		this.__keyFrames = {};
		this.__combinedKeyFrames = [];
		
		#children
		mainLayout = QVBoxLayout();
		
		from VideoWidget import VideoPlayerWidget;
		this.__videoWidget = VideoPlayerWidget(this);
		mainLayout.addWidget(this.__videoWidget);
		
		#status panel
		statusPanel = QHBoxLayout();
		
		this.__cutFromBtn = QPushButton("Cut from:");
		this.__cutFromBtn.clicked.connect(this.__OnSetFrom);
		statusPanel.addWidget(this.__cutFromBtn);
		this.__cutFrom = QSpinBox();
		this.__cutFrom.setMaximum(2147483647);
		statusPanel.addWidget(this.__cutFrom);
		
		statusPanel.addWidget(QLabel("Current key frame: "));
		this.__keyFrameCounter = QSpinBox();
		this.__keyFrameCounter.setMaximum(2147483647);
		statusPanel.addWidget(this.__keyFrameCounter);
		
		this.__cutToBtn = QPushButton("Cut to:");
		this.__cutToBtn.clicked.connect(this.__OnSetTo);
		statusPanel.addWidget(this.__cutToBtn);
		this.__cutTo = QSpinBox();
		this.__cutTo.setMaximum(2147483647);
		statusPanel.addWidget(this.__cutTo);
		
		mainLayout.addLayout(statusPanel);
		
		#actions panel
		actionsPanel = QHBoxLayout();
		
		prevKeyBtn = QPushButton("Jump to previous key frame");		
		prevKeyBtn.clicked.connect(this.__videoWidget.JumpToPrevKeyFrame);
		actionsPanel.addWidget(prevKeyBtn);
		
		nextKeyBtn = QPushButton("Jump to next key frame");
		nextKeyBtn.clicked.connect(this.__videoWidget.JumpToNextKeyFrame);
		actionsPanel.addWidget(nextKeyBtn);
		
		playBtn = QPushButton("Play/Pause");
		playBtn.clicked.connect(this.__videoWidget.PlayPause);
		actionsPanel.addWidget(playBtn);
		
		cutBtn = QPushButton("Cut");
		cutBtn.clicked.connect(this.__OnCut);
		actionsPanel.addWidget(cutBtn);
		
		mainLayout.addLayout(actionsPanel);
		
		this.setLayout(mainLayout);
		
		this.setGeometry(0, 0, 800, 600);		
		this.__CenterOnScreen();
		
	#Public methods
	def LoadFile(this, path):
		#reset state
		this.__path = path;
		this.__keyFrames = {};
		this.__combinedKeyFrames = [];
		
		this.__AnalyzeInput();
		
		this.__videoWidget.SetFile(this.__path);
		this.__videoWidget.SetKeyFrameList(this.__combinedKeyFrames);
	
	#Private methods
	def __AnalyzeInput(this):
		probeFileName = "test.txt";
		
		#step 1: let ffprobe find all key frames
		probeFile = open(probeFileName, "wb");
		args = [
			'ffprobe',
			'-show_frames',
			'-show_entries',
			'frame=key_frame,stream_index,pkt_dts_time',
			'-pretty',
			#"'" + os.path.abspath(this.__path) + "'",
			os.path.abspath(this.__path)
		];
		subprocess.run(args, stdout=probeFile, stderr=probeFile, shell=False);
		probeFile.close();
		
		#step 2: read in key frames
		probeFile = open(probeFileName, "r");
		content = probeFile.read();
		probeFile.close();
		
		matches = re.findall('\[FRAME\]\nstream_index=(.*?)\nkey_frame=1\npkt_dts_time=(.*?)\n\[/FRAME\]', content, re.MULTILINE);
		for (streamIndex, dts) in matches:
			streamIndex = int(streamIndex);
			ts = this.__ParseTimeStamp(dts);
			
			if(streamIndex in this.__keyFrames):
				this.__keyFrames[streamIndex].add(ts);
			else:
				s = set();
				s.add(ts);
				this.__keyFrames[streamIndex] = s;
				
		#step 3: find shared key frames
		keys = list(this.__keyFrames.keys());
		key = keys.pop();
		
		for ts in this.__keyFrames[key]:
			store = True;
			for otherKey in keys:
				if(ts not in this.__keyFrames[otherKey]):
					store = False;
					break;
			if(store):
				this.__combinedKeyFrames.append(ts);
				
		this.__combinedKeyFrames.sort();
		
	def __CenterOnScreen(this):
		resolution = QDesktopWidget().screenGeometry();
		this.move((resolution.width() / 2) - (this.frameSize().width() / 2), (resolution.height() / 2) - (this.frameSize().height() / 2));
		
	def __ParseTimeStamp(this, timeStamp):
		matches = re.findall('(.*?):(.*?):(.*?)\.(.+?)', timeStamp);
		match = matches[0];
		
		result = int(match[3]);
		result += int(match[2]) * 1000;
		result += int(match[1]) * 60 * 1000;
		result += int(match[0]) * 60 * 60 * 1000;
		
		return result;
		
	def __TimeStampToString(this, ts):
		ms = ts % 1000;
		ts = int(ts / 1000);
		s = ts % 60;
		ts = int(ts / 60);
		m = ts % 60;
		ts = int(ts / 60);
		h = ts;
		
		return "%d:%02d:%02d.%d" % (h, m, s, ms);
		
	#Event handlers
	def __OnCut(this):
		if(this.__videoWidget.IsPlaying()):
			this.__videoWidget.PlayPause();
			
		startKeyFrame = this.__cutFrom.value();
		endKeyFrame = this.__cutTo.value();
		
		startPos = this.__combinedKeyFrames[startKeyFrame];
		endPos = this.__combinedKeyFrames[endKeyFrame];
		duration = endPos - startPos;
			
		name, ext = os.path.splitext(this.__path);
		args = [
			'ffmpeg',
			'-i',
			os.path.abspath(this.__path),
			'-acodec',
			'copy',
			'-vcodec',
			'copy',
			'-ss',
			this.__TimeStampToString(startPos),
			'-t',
			this.__TimeStampToString(duration),
			'out'+ext
		];
		subprocess.run(args);
		
		QMessageBox.message("Done");
			
	def __OnSetFrom(this):
		v = int(this.__keyFrameCounter.value());
		this.__cutFrom.setValue(v);
		
	def __OnSetTo(this):
		v = int(this.__keyFrameCounter.value());
		this.__cutTo.setValue(v);
		
	def OnKeyFrameChanged(this, keyFrameNumber):
		this.__keyFrameCounter.setValue(keyFrameNumber);
