/*
 * Copyright (c) 2020 Amir Czwink (amir130@hotmail.de)
 *
 * This file is part of CopyCut.
 *
 * CopyCut is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * CopyCut is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with CopyCut.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <StdXX.hpp>
using namespace StdXX;
using namespace StdXX::Multimedia;

class StreamCopyCutter
{
public:
	//Constructor
	StreamCopyCutter(SeekableInputStream& inputStream, SeekableOutputStream& outputStream);

	//Methods
	void Cut(const Format& outputFormat, uint64 startTime_us = 0, uint64 endTime_us = Unsigned<uint64>::Max());
	void Cut(const Format& outputFormat, const BinaryTreeSet<uint32>& streamsToInclude, uint64 startTime_us = 0, uint64 endTime_us = Unsigned<uint64>::Max());

private:
	//Members
	SeekableInputStream& inputStream;
	SeekableOutputStream& outputStream;
	UniquePointer<Demuxer> demuxer;
	UniquePointer<Muxer> muxer;
	Map<uint32, uint32> streamMapping;
	uint64 startTime_us;
	uint64 endTime_us;
	TimeScale microsecondsTimeScale;

	//Methods
	bool IsPacketPastEnd(uint32 sourceStreamIndex, uint64 ts);
	void MapStreams(const BinaryTreeSet<uint32>& streamsToInclude);
	void ProcessPacket(const IPacket& sourcePacket);
	void Run();
	void SeekTo(uint64 startTime_us);
};