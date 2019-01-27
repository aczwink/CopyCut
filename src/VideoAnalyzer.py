__license__ = u"""
Copyright (c) 2018 Amir Czwink (amir130@hotmail.de)

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
class VideoAnalyzer:
	#Constructor
	def __init__(this):
		this.__streams = {}; #maps valid stream indices from input to stream type (string)
		this.__keyFrames = {}; #maps stream indices to sets of key-frame time stamps in nanoseconds
		this.__keyFramesOrdered = {}; #maps stream indices to lists of key-frame time stamps in nanoseconds ordered by time stamp
		this.__combinedKeyFrames = []; #list of combination of all shared time stamps accross all streams
		
	#Public methods
	def FindSharedKeyFrames(this):
		keys = list(this.__keyFrames.keys());
		key = keys.pop();
		
		this.__combinedKeyFrames = set();
		
		for ts in this.__keyFrames[key]:
			store = True;
			for otherKey in keys:
				if(ts not in this.__keyFrames[otherKey]):
					store = False;
					break;
			if(store):
				this.__combinedKeyFrames.add(ts);
				
		#convert to ordered list				
		l = list(this.__combinedKeyFrames);
		l.sort();
		this.__combinedKeyFrames = l;
		
	def GetCombinedKeyFrameList(this):
		return this.__combinedKeyFrames;
		
	def GetStreamKeyFrameList(this, streamIndex):
		if(streamIndex == -1):
			return this.GetCombinedKeyFrameList();
			
		return this.__keyFramesOrdered[streamIndex];
				
	def GetStreams(this):
		return this.__streams;
		
	#Protected methods
	def _AddStream(this, streamIndex, streamType):
		this.__streams[int(streamIndex)] = streamType;
		
	def _SetStreamKeyFrames(this, streamIndex, keyFrames):
		this.__keyFrames[streamIndex] = keyFrames;
		l = list(keyFrames);
		l.sort();
		this.__keyFramesOrdered[streamIndex] = l;