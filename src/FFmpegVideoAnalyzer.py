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
import os;
import re;
import subprocess;
import tempfile;

from VideoAnalyzer import VideoAnalyzer;

class FFmpegVideoAnalyzer(VideoAnalyzer):
	#constructor
	def __init__(this):
		VideoAnalyzer.__init__(this);
		
	#Public methods
	def AnalyzeVideo(this, path, dlg):
		fd, probeFileName = tempfile.mkstemp();
		
		#run ffprobe
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
			path
		];
		subprocess.run(args, stdout=probeFile, stderr=probeFile, shell=False);
		probeFile.close();
		
		#read ffprobe results
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
			this._AddStream(int(streamIndex), streamType);
			
		#step 3: read key frames			
		dlg.UpdateStatus("Reading in found key-frames.");
		
		keyFrameSets = this.__ReadKeyFrames(content);
		for streamIndex in keyFrameSets:
			this._SetStreamKeyFrames(streamIndex, keyFrameSets[streamIndex]);
			
	def GetDuration(this):
		return this.__endTs;
		
	#Private methods
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
		if(len(matches) == 0):
			return None;
		assert len(matches) == 1;
		match = matches[0];
			
		return this.__ParseFractional(match[1]) + int(match[0]) * 1000000000;
		
	def __ReadKeyFrames(this, content):
		result = {};
		
		for streamIndex in this.GetStreams():
			result[streamIndex] = set();
		
		#matches = re.findall('\[FRAME\]\nstream_index=(.*?)\nkey_frame=1\npkt_dts_time=(.*?)\n\[/FRAME\]', content, re.MULTILINE);
		matches = re.findall('\[PACKET\]\nstream_index=(.*?)\ndts_time=(.*?)\nflags=(?:.*?K.*?)\n\[/PACKET\]', content, re.MULTILINE);
		
		for (streamIndex, dts) in matches:
			streamIndex = int(streamIndex);
			if(streamIndex not in this.GetStreams()):
				continue; #skip invalid streams

			ts = this.__ParseTimeStamp(dts);
			if(ts is None): #sometimes ffprobe outputs dts_time=N/A
				continue;
			
			result[streamIndex].add(ts);
			
		return result;
