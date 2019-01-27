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
import subprocess;
import threading;

from BusyTaskDialog import BusyTaskDialog;
from DragHintWidget import DragHintWidget;
from FFmpegVideoAnalyzer import FFmpegVideoAnalyzer;
from KeyFrameControl import KeyFrameControl, StreamChangeBehavior;
from StreamSourceController import StreamSourceController;
from Util import TimeStampToString;

class MainWindow(QWidget):
	#Constructor
	def __init__(this):
		super(MainWindow, this).__init__(None);
		
		#Private members
		this.__path = None;
		this.__videoAnalyzer = None;
		
		#children
		mainLayout = QVBoxLayout();
		
		this.__videoWidget = DragHintWidget(this);
		this.__videoWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding));
		mainLayout.addWidget(this.__videoWidget);
		
		#current panel
		currentPanel = QHBoxLayout();
		
		currentPanel.addWidget(QLabel("Current key frame: "));
		this.__keyFrameCounter = KeyFrameControl(StreamChangeBehavior.MinimizeDistance);
		this.__keyFrameCounter.OnKeyFrameChanged(this.__OnKeyFrameChanged);
		currentPanel.addWidget(this.__keyFrameCounter);
		
		mainLayout.addLayout(currentPanel);
		
		#status panel
		statusPanel = QHBoxLayout();
		
		this.__cutFromBtn = QPushButton("Cut from:");
		this.__cutFromBtn.setEnabled(False);
		this.__cutFromBtn.clicked.connect(this.__OnSetFrom);
		statusPanel.addWidget(this.__cutFromBtn);
		
		this.__cutFrom = KeyFrameControl(StreamChangeBehavior.JumpToStart);
		statusPanel.addWidget(this.__cutFrom);
		
		this.__cutToBtn = QPushButton("Cut to:");
		this.__cutToBtn.setEnabled(False);
		this.__cutToBtn.clicked.connect(this.__OnSetTo);
		statusPanel.addWidget(this.__cutToBtn);
		
		this.__cutTo = KeyFrameControl(StreamChangeBehavior.JumpToEnd, True);
		statusPanel.addWidget(this.__cutTo);
		#this.__cutTo.valueChanged.connect(this.__OnCutToChanged);
		
		mainLayout.addLayout(statusPanel);
		
		#actions panel
		actionsPanel = QHBoxLayout();
		
		this.__sourceStream = QComboBox();
		this.__sourceStream.setEnabled(False);
		this.__sourceStream.currentIndexChanged.connect(this.__OnSourceStreamChanged);
		actionsPanel.addWidget(this.__sourceStream);
				
		this.__playBtn = QPushButton("Play/Pause");
		this.__playBtn.setEnabled(False);
		this.__playBtn.clicked.connect(lambda: this.__videoWidget.PlayPause());
		actionsPanel.addWidget(this.__playBtn);
		
		this.__cutBtn = QPushButton("Cut");
		this.__cutBtn.setEnabled(False);
		this.__cutBtn.clicked.connect(this.__OnCut);
		actionsPanel.addWidget(this.__cutBtn);
		
		this.__offset = QSpinBox();
		this.__offset.setEnabled(False);
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
	def LoadFile(this, path):
		#reset state
		this.__path = path;
			
		this.__RunTask("Analyzing video", this.__AnalyzeInput);
		
		this.__keyFrameCounter.SetVideoAnalyzer(this.__videoAnalyzer);
		this.__cutFrom.SetVideoAnalyzer(this.__videoAnalyzer);
		this.__cutTo.SetVideoAnalyzer(this.__videoAnalyzer);
		
		this.__cutFromBtn.setEnabled(True);
		this.__cutToBtn.setEnabled(True);		
		this.__sourceStream.setEnabled(True);
		this.__playBtn.setEnabled(True);
		this.__cutBtn.setEnabled(True);
		this.__offset.setEnabled(True);
		
		#update ui
		from VideoWidget import VideoPlayerWidget;
		realVideoWidget = VideoPlayerWidget(this.__keyFrameCounter);
		realVideoWidget.SetVideoAnalyzer(this.__videoAnalyzer);
		this.layout().replaceWidget(this.__videoWidget, realVideoWidget);
		this.__videoWidget = realVideoWidget;
		this.__videoWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding));
		this.__videoWidget.SetFile(this.__path);
		this.__sourceStream.setModel(StreamSourceController(this.__videoAnalyzer));
	
	#Private methods
	def __AnalyzeInput(this, dlg):
		this.__videoAnalyzer = FFmpegVideoAnalyzer();
		
		#step 1: analyze video
		dlg.UpdateStatus("Analyzing video and looking for all key-frames.\nDepending on the video size, this might take a while...");		
		this.__videoAnalyzer.AnalyzeVideo(os.path.abspath(this.__path), dlg);
		
		dlg.UpdateStatus("Updating shared key frame list");
		this.__videoAnalyzer.FindSharedKeyFrames();
		
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
			TimeStampToString(startPos),
		];
		if(duration is not None):
			args.append('-t');
			args.append(TimeStampToString(duration));
		args.append(outputPath);
		
		with open(os.devnull, 'w') as pipe:
			subprocess.run(args, stdout = pipe, stderr = pipe);
		
	def __RunTask(this, taskTitle, task):
		dlg = BusyTaskDialog(this, taskTitle);
		def __executeTask():
			task(dlg);
			dlg.finished = True;
		thread = threading.Thread(target = __executeTask, args = ());
		thread.start();
		dlg.Run();
		
	#Event handlers
	def __OnCut(this):
		if(this.__videoWidget.IsPlaying()):
			this.__videoWidget.PlayPause();
			
		startKeyFrame = this.__cutFrom.GetCurrentKeyFrame();
		endKeyFrame = this.__cutTo.GetCurrentKeyFrame();
			
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
		keyFrameList = this.__videoAnalyzer.GetStreamKeyFrameList(this.__activeStreamIndex);
		startPos = keyFrameList[startKeyFrame] + delta;
		if(endKeyFrame == len(keyFrameList)):
			#cut to end of video
			duration = None;
		else:
			endPos = keyFrameList[endKeyFrame];
			duration = endPos - startPos;
		
		#print(TimeStampToString(startPos));
		
		this.__RunTask("Cutting Video", functools.partial(this.__CutVideo, inputPath, outputPath, startPos, duration));		
		QMessageBox.information(this, "Done", "File was successfully cut.");
		
	def __OnKeyFrameChanged(this):
		this.__videoWidget.JumpToKeyFrame(this.__keyFrameCounter.GetCurrentKeyFrame());
			
	def __OnSetFrom(this):
		keyFrame = this.__keyFrameCounter.GetCurrentKeyFrame();
		this.__cutFrom.SetKeyFrame(keyFrame);
		
	def __OnSetTo(this):
		keyFrame = this.__keyFrameCounter.GetCurrentKeyFrame();
		this.__cutTo.SetKeyFrame(keyFrame);
		
	def __OnSourceStreamChanged(this):
		this.__activeStreamIndex = this.__sourceStream.model().GetStreamIndexForControllerIndex(this.__sourceStream.currentIndex());
		
		playing = this.__videoWidget.IsPlaying();
		if(playing):
			this.__videoWidget.PlayPause();
		
		#inform controls
		this.__videoWidget.SetActiveStreamIndex(this.__activeStreamIndex);
		this.__keyFrameCounter.SetActiveStreamIndex(this.__activeStreamIndex);
		this.__cutFrom.SetActiveStreamIndex(this.__activeStreamIndex);
		this.__cutTo.SetActiveStreamIndex(this.__activeStreamIndex);
		
		if(playing):
			this.__videoWidget.PlayPause();
		
	def dragEnterEvent(this, event):
		if (event.mimeData().hasUrls()):
			event.acceptProposedAction();
			
	def dropEvent(this, event):
		url = event.mimeData().urls()[0];
		path = url.toLocalFile();
		this.LoadFile(path);
