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
import functools;
import os;
from PyQt5.QtCore import *;
from PyQt5.QtGui import *;
from PyQt5.QtWidgets import *;
import re;
import subprocess;
import tempfile;
import threading;

from BusyTaskDialog import BusyTaskDialog;
from DragHintWidget import DragHintWidget;

class StreamSourceController(QAbstractItemModel):
	def __init__(this, mainWindow):
		QAbstractItemModel.__init__(this);
		
		this.__choices = [];
		this.__choices.append(("Combined (safest) - " + str(len(mainWindow.GetCombinedKeyFrameSet())) + " keyframes", -1));
		for streamIndex in sorted(mainWindow.GetStreams()):
			streamType = mainWindow.GetStreams()[streamIndex];
			this.__choices.append(("Stream " + str(streamIndex) + " - " + streamType + " - " + str(len(mainWindow.GetStreamKeyFrameSet(streamIndex))) + " keyframes", streamIndex));
		
	#Public methods
	def GetStreamIndexForControllerIndex(this, index):
		_,streamIndex = this.__choices[index];
		
		return streamIndex;
		
	#Interface
	def columnCount(this, parent):
		return 1;
		
	def data(this, index, role):
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

class MainWindow(QWidget):
	#Constructor
	def __init__(this):
		super(MainWindow, this).__init__(None);
		
		#Private members
		this.__path = None;
		this.__streams = {}; #maps valid stream indices from input to stream type (string)
		this.__keyFrames = {}; #maps stream indices to lists of key-frame time stamps in nanoseconds
		this.__combinedKeyFrames = []; #list of combination of all shared time stamps accross all streams
		this.__activeKeyFrameList = []; #the keyframe set that is in use for playback and cutting
		
		#children
		mainLayout = QVBoxLayout();
		
		this.__videoWidget = DragHintWidget(this);
		this.__videoWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding));
		mainLayout.addWidget(this.__videoWidget);
		
		#current panel
		currentPanel = QHBoxLayout();
		
		currentPanel.addWidget(QLabel("Current key frame: "));
		this.__keyFrameCounter = QSpinBox();
		this.__keyFrameCounter.valueChanged.connect(this.__OnKeyFrameChanged);
		currentPanel.addWidget(this.__keyFrameCounter);
		this.__keyFrameTime = QLabel("@ 00:00:00.0");
		currentPanel.addWidget(this.__keyFrameTime);
		
		mainLayout.addLayout(currentPanel);
		
		#status panel
		statusPanel = QHBoxLayout();
		
		this.__cutFromBtn = QPushButton("Cut from:");
		this.__cutFromBtn.clicked.connect(this.__OnSetFrom);
		statusPanel.addWidget(this.__cutFromBtn);
		this.__cutFrom = QSpinBox();
		this.__cutFrom.valueChanged.connect(this.__OnCutFromChanged);
		statusPanel.addWidget(this.__cutFrom);
		this.__cutFromTime = QLabel("@ 00:00:00.0");
		statusPanel.addWidget(this.__cutFromTime);
		
		this.__cutToBtn = QPushButton("Cut to:");
		this.__cutToBtn.clicked.connect(this.__OnSetTo);
		statusPanel.addWidget(this.__cutToBtn);
		this.__cutTo = QSpinBox();
		this.__cutTo.valueChanged.connect(this.__OnCutToChanged);
		statusPanel.addWidget(this.__cutTo);
		this.__cutToTime = QLabel("@ 00:00:00.0");
		statusPanel.addWidget(this.__cutToTime);
		
		mainLayout.addLayout(statusPanel);
		
		#actions panel
		actionsPanel = QHBoxLayout();
		
		this.__sourceStream = QComboBox();
		this.__sourceStream.currentIndexChanged.connect(this.__OnSourceStreamChanged);
		actionsPanel.addWidget(this.__sourceStream);
				
		playBtn = QPushButton("Play/Pause");
		playBtn.clicked.connect(this.__videoWidget.PlayPause);
		actionsPanel.addWidget(playBtn);
		
		cutBtn = QPushButton("Cut");
		cutBtn.clicked.connect(this.__OnCut);
		actionsPanel.addWidget(cutBtn);
		
		this.__offset = QSpinBox();
		this.__offset.setMinimum(-10000);
		this.__offset.setMaximum(10000);
		actionsPanel.addWidget(QLabel("Time offset (ms): "));
		actionsPanel.addWidget(this.__offset);
		
		mainLayout.addLayout(actionsPanel);
		
		this.setLayout(mainLayout);
		
		this.setGeometry(0, 0, 800, 600);
		this.setAcceptDrops(True);
		this.setWindowTitle("CopyCut");
		this.__CenterOnScreen();
		
	#Public methods
	def GetCombinedKeyFrameSet(this):
		return this.__combinedKeyFrames;
		
	def GetStreamKeyFrameSet(this, streamIndex):
		return this.__keyFrames[streamIndex];
	
	def GetStreams(this):
		return this.__streams;
		
	def LoadFile(this, path):
		#reset state
		this.__path = path;
		this.__keyFrames = {};
			
		this.__RunTask("Analyzing video", this.__AnalyzeInput);
		
		#update ui
		from VideoWidget import VideoPlayerWidget;
		realVideoWidget = VideoPlayerWidget(this);
		this.layout().replaceWidget(this.__videoWidget, realVideoWidget);
		this.__videoWidget = realVideoWidget;
		this.__videoWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding));
		this.__videoWidget.SetFile(this.__path);
		this.__sourceStream.setModel(StreamSourceController(this));
	
	#Private methods
	def __AnalyzeInput(this, dlg):
		fd, probeFileName = tempfile.mkstemp();
		
		#step 1: let ffprobe find all key frames
		dlg.UpdateStatus("Looking for all key-frames.\nDepending on the video size, this might take a while...");
		probeFile = open(probeFileName, "wb");
		args = [
			'ffprobe',
			'-show_packets',
			'-show_entries',
			'packet=flags,stream_index,dts_time',
			#'-show_frames',
			#'-show_entries',
			#'frame=key_frame,stream_index,pkt_dts_time',
			#"'" + os.path.abspath(this.__path) + "'",
			os.path.abspath(this.__path)
		];
		subprocess.run(args, stdout=probeFile, stderr=probeFile, shell=False);
		probeFile.close();
		
		dlg.UpdateStatus("Querying video info.");
		
		with open(probeFileName, "r") as probeFile:
			content = probeFile.read();
		os.close(fd);
		os.remove(probeFileName);
			
		#find end of video
		matches = re.findall('Duration: (.+?),', content);
		assert len(matches) == 1;
		this.__endTs = this.__ParseSexasegimalTimeStamp(matches[0]);
		
		#step 2: find valid streams
		matches = re.findall('Stream #0:([0-9]+)(?:\(.*?\))?(?:\[.+?\])?: (Video|Audio)', content);
		for (streamIndex, streamType) in matches:
			this.__streams[int(streamIndex)] = streamType;
			
		dlg.UpdateStatus("Reading in found key-frames.");
			
		keyFrameSets = this.__ReadKeyFrames(content);
		this.__FindSharedKeyFrames(keyFrameSets);
		
		#convert keyframe sets to lists
		for streamIndex in keyFrameSets:
			l = list(keyFrameSets[streamIndex]);
			l.sort();
			this.__keyFrames[streamIndex] = l;
			
		l = list(this.__combinedKeyFrames);
		l.sort();
		this.__combinedKeyFrames = l;
		
	def __CenterOnScreen(this):
		resolution = QDesktopWidget().screenGeometry();
		this.move((resolution.width() / 2) - (this.frameSize().width() / 2), (resolution.height() / 2) - (this.frameSize().height() / 2));
		
	def __CutVideo(this, inputPath, outputPath, startPos, duration, dlg):
		dlg.UpdateStatus("FFmpeg is cutting your video...");
		#call ffmpeg	
		args = [
			'ffmpeg',
			'-i',
			inputPath,
			'-acodec',
			'copy',
			'-vcodec',
			'copy',
			'-ss',
			this.__TimeStampToString(startPos),
		];
		if(duration is not None):
			args.append('-t');
			args.append(this.__TimeStampToString(duration));
		args.append(outputPath);
		
		with open(os.devnull, 'w') as pipe:
			subprocess.run(args, stdout = pipe, stderr = pipe);
		
	def __FindSharedKeyFrames(this, keyFrameSets):
		keys = list(keyFrameSets.keys());
		key = keys.pop();
		
		this.__combinedKeyFrames = set();
		
		for ts in keyFrameSets[key]:
			store = True;
			for otherKey in keys:
				if(ts not in keyFrameSets[otherKey]):
					store = False;
					break;
			if(store):
				this.__combinedKeyFrames.add(ts);
				
	def __ParseFractional(this, fractional):
		assert len(fractional) <= 9;
		
		return int(fractional) * (10 ** (9 - len(fractional)));
				
	def __ParseSexasegimalTimeStamp(this, string):
		matches = re.findall("([0-9]{2}):([0-9]{2}):([0-9]*)\.([0-9]*)", string);
		assert len(matches) == 1;
		match = matches[0];
		
		hours,mins,secs,fractional = match;
		return this.__ParseFractional(fractional) + int(secs) * 1000000000 + int(mins) * 60 * 1000000000 + int(hours) * 60 * 60 * 1000000000;
		
	def __ParseTimeStamp(this, timeStamp):
		matches = re.findall("([0-9]*)\.([0-9]*)", timeStamp);
		assert len(matches) == 1;
		match = matches[0];
			
		return this.__ParseFractional(match[1]) + int(match[0]) * 1000000000;
		
	def __ReadKeyFrames(this, content):
		result = {};
		
		for streamIndex in this.__streams:
			result[streamIndex] = set();
		
		#matches = re.findall('\[FRAME\]\nstream_index=(.*?)\nkey_frame=1\npkt_dts_time=(.*?)\n\[/FRAME\]', content, re.MULTILINE);
		matches = re.findall('\[PACKET\]\nstream_index=(.*?)\ndts_time=(.*?)\nflags=(?:.*?K.*?)\n\[/PACKET\]', content, re.MULTILINE);
		
		for (streamIndex, dts) in matches:
			streamIndex = int(streamIndex);
			if(streamIndex not in this.__streams):
				continue; #skip invalid streams
			
			ts = this.__ParseTimeStamp(dts);
			
			result[streamIndex].add(ts);
			
		return result;
		
	def __RunTask(this, taskTitle, task):
		dlg = BusyTaskDialog(this, taskTitle);
		def __executeTask():
			task(dlg);
			dlg.finished = True;
		thread = threading.Thread(target = __executeTask, args = ());
		thread.start();
		dlg.Run();
		
	def __TimeStampToString(this, ts):
		fractional = ts % 1000000000;
		ts = ts // 1000000000;
		s = ts % 60;
		ts = (ts // 60);
		m = ts % 60;
		ts = (ts // 60);
		h = ts;
		
		return "%02d:%02d:%02d.%09d" % (h, m, s, fractional);
		
	def __UpdateKeyFrameTime(this, spinBox, timeLabel):
		keyFrameNumber = spinBox.value();
		ts = this.__activeKeyFrameList[keyFrameNumber];
		timeLabel.setText("@ " + this.__TimeStampToString(ts));
		
	#Event handlers
	def __OnCut(this):
		if(this.__videoWidget.IsPlaying()):
			this.__videoWidget.PlayPause();
			
		startKeyFrame = this.__cutFrom.value();
		endKeyFrame = this.__cutTo.value();
			
		inputPath = os.path.abspath(this.__path);
			
		#output file
		name, ext = os.path.splitext(inputPath);
		outputPath = name + "_cut_" + str(startKeyFrame) + "_-_" + str(endKeyFrame) + ext;
		if(os.path.exists(outputPath)):
			result = QMessageBox.question(this, "Target file exists!", "The target file does already exist. Should '" + outputPath + "' be overwritten?");
			if(result == QMessageBox.Yes):
				os.remove(outputPath);
			else:
				QMessageBox.information(this, "Aborted", "Cutting was aborted.");
				return;
				
		#evaluate start and duration
		delta = this.__offset.value() * 1000000;
		startPos = this.__activeKeyFrameList[startKeyFrame] - delta;
		if(endKeyFrame == len(this.__activeKeyFrameList)):
			#cut to end of video
			duration = None;
		else:
			endPos = this.__activeKeyFrameList[endKeyFrame];
			duration = endPos - startPos;
		
		#print(this.__TimeStampToString(startPos));
		
		this.__RunTask("Cutting Video", functools.partial(this.__CutVideo, inputPath, outputPath, startPos, duration));		
		QMessageBox.information(this, "Done", "File was successfully cut.");
		
	def __OnCutFromChanged(this):
		this.__UpdateKeyFrameTime(this.__cutFrom, this.__cutFromTime);
		
	def __OnCutToChanged(this):
		if(this.__cutTo.value() == len(this.__activeKeyFrameList)):
			this.__cutToTime.setText("@ " + this.__TimeStampToString(this.__endTs) + " (end of video)");
		else:
			this.__UpdateKeyFrameTime(this.__cutTo, this.__cutToTime);
		
	def __OnKeyFrameChanged(this):
		this.__UpdateKeyFrameTime(this.__keyFrameCounter, this.__keyFrameTime);
		
		this.__videoWidget.JumpToKeyFrame(this.__keyFrameCounter.value());
			
	def __OnSetFrom(this):
		v = int(this.__keyFrameCounter.value());
		this.__cutFrom.setValue(v);
		
	def __OnSetTo(this):
		v = int(this.__keyFrameCounter.value());
		this.__cutTo.setValue(v);
		
	def __OnSourceStreamChanged(this):
		streamIndex = this.__sourceStream.model().GetStreamIndexForControllerIndex(this.__sourceStream.currentIndex());
		if(streamIndex == -1):
			this.__activeKeyFrameList = this.__combinedKeyFrames;
		else:
			this.__activeKeyFrameList = this.__keyFrames[streamIndex];
		this.__videoWidget.SetKeyFrameList(this.__activeKeyFrameList);
		
		maxKeyFrame = len(this.__activeKeyFrameList) - 1;
		this.__keyFrameCounter.setMaximum(maxKeyFrame);
		this.__cutFrom.setMaximum(maxKeyFrame);
		this.__cutTo.setMaximum(maxKeyFrame + 1); #+ the end of video marker
		
		#always default to the full video		
		this.__cutFrom.setValue(0);		
		this.__cutTo.setValue(maxKeyFrame + 1);
		
	def OnKeyFrameChangedByPlayback(this, keyFrameNumber):
		this.__keyFrameCounter.blockSignals(True);
		this.__keyFrameCounter.setValue(keyFrameNumber);
		this.__UpdateKeyFrameTime(this.__keyFrameCounter, this.__keyFrameTime);
		this.__keyFrameCounter.blockSignals(False);
		
	def dragEnterEvent(this, event):
		if (event.mimeData().hasUrls()):
			event.acceptProposedAction();
			
	def dropEvent(this, event):
		url = event.mimeData().urls()[0];
		path = url.toLocalFile();
		this.LoadFile(path);
