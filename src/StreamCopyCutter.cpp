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
//Class header
#include "StreamCopyCutter.hpp"

//Constructor
StreamCopyCutter::StreamCopyCutter(SeekableInputStream &inputStream, SeekableOutputStream &outputStream)
	: inputStream(inputStream), outputStream(outputStream), microsecondsTimeScale(1, 1000000)
{
	const Format* inputFormat = Format::Find(this->inputStream);

	this->demuxer = inputFormat->CreateDemuxer(this->inputStream);
	this->demuxer->ReadHeader();
	this->demuxer->FindStreamInfo();
}

//Public methods
void StreamCopyCutter::Cut(const Format& outputFormat, uint64 startTime_us, uint64 endTime_us)
{
	BinaryTreeSet<uint32> streamsToInclude;
	for(uint32 i = 0; i < this->demuxer->GetNumberOfStreams(); i++)
		streamsToInclude.Insert(i);
	this->Cut(outputFormat, streamsToInclude, startTime_us, endTime_us);
}

void StreamCopyCutter::Cut(const Format &outputFormat, const BinaryTreeSet<uint32>& streamsToInclude, uint64 startTime_us, uint64 endTime_us)
{
	this->muxer = outputFormat.CreateMuxer(this->outputStream);

	this->MapStreams(streamsToInclude);
	this->SeekTo(startTime_us);
	this->endTime_us = endTime_us;
	this->Run();
}

//Private methods
bool StreamCopyCutter::IsPacketPastEnd(uint32 sourceStreamIndex, uint64 ts)
{
	Stream* sourceStream = demuxer->GetStream(sourceStreamIndex);

	const uint64 mapped_ts = sourceStream->timeScale.Rescale(ts, this->microsecondsTimeScale);

	return mapped_ts > this->endTime_us;
}

void StreamCopyCutter::MapStreams(const BinaryTreeSet<uint32>& streamsToInclude)
{
	for(uint32 i = 0; i < demuxer->GetNumberOfStreams(); i++)
	{
		if(!streamsToInclude.Contains(i))
			continue;

		Stream* sourceStream = demuxer->GetStream(i);

		Stream* targetStream;
		switch(sourceStream->codingParameters.dataType)
		{
			case DataType::Audio:
				targetStream = new AudioStream();
				break;
			case DataType::Subtitle:
				targetStream = new SubtitleStream();
				break;
			case DataType::Video:
				targetStream = new VideoStream();
				break;
		}
		targetStream->codingParameters = sourceStream->codingParameters;

		uint32 mappedIndex = muxer->AddStream(targetStream);
		streamMapping[i] = mappedIndex;
	}
}

void StreamCopyCutter::ProcessPacket(const IPacket& sourcePacket)
{
	PacketWrapper mappedPacket(sourcePacket);

	mappedPacket.streamIndex = streamMapping[sourcePacket.GetStreamIndex()];

	Stream* sourceStream = demuxer->GetStream(sourcePacket.GetStreamIndex());
	Stream* destStream = muxer->GetStream(mappedPacket.streamIndex);

	const uint64 delta_ts = this->microsecondsTimeScale.Rescale(this->startTime_us, destStream->timeScale);
	mappedPacket.dts = sourceStream->timeScale.Rescale(sourcePacket.GetDecodeTimestamp(), destStream->timeScale) - delta_ts;
	mappedPacket.pts = sourceStream->timeScale.Rescale(sourcePacket.GetPresentationTimestamp(), destStream->timeScale) - delta_ts;

	muxer->WritePacket(mappedPacket);
}

void StreamCopyCutter::Run()
{
	muxer->WriteHeader();

	BinaryTreeSet<uint32> leftStreamIndices;
	for(const auto& kv : this->streamMapping)
		leftStreamIndices.Insert(kv.key);
	while(!leftStreamIndices.IsEmpty())
	{
		UniquePointer<IPacket> packet = demuxer->ReadFrame();
		if(packet.IsNull())
			break;

		if(!this->streamMapping.Contains(packet->GetStreamIndex()))
			continue;

		if(this->IsPacketPastEnd(packet->GetStreamIndex(), packet->GetPresentationTimestamp()))
		{
			leftStreamIndices.Remove(packet->GetStreamIndex());
			continue;
		}

		this->ProcessPacket(*packet);
	}

	muxer->Finalize();
}

void StreamCopyCutter::SeekTo(uint64 startTime_us)
{
	if(startTime_us != 0)
		this->demuxer->Seek(startTime_us, this->microsecondsTimeScale);
	this->startTime_us = startTime_us;
}