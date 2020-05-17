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

extern "C"
{
#include <libavformat/avformat.h>


	int BLA(const char *out_filename)
	{
		AVOutputFormat *ofmt = NULL;
		AVFormatContext *ifmt_ctx = NULL, *ofmt_ctx = NULL;
		AVPacket pkt;
		int ret, i;
		int *stream_mapping = NULL;
		int stream_mapping_size = 0;

		avformat_alloc_output_context2(&ofmt_ctx, NULL, NULL, out_filename);
		if (!ofmt_ctx) {
			fprintf(stderr, "Could not create output context\n");
			ret = AVERROR_UNKNOWN;
			goto end;
		}

		ofmt = ofmt_ctx->oformat;

		for (i = 0; i < ifmt_ctx->nb_streams; i++) {
			AVStream *out_stream;
			AVStream *in_stream = ifmt_ctx->streams[i];
			AVCodecParameters *in_codecpar = in_stream->codecpar;

			out_stream = avformat_new_stream(ofmt_ctx, NULL);
			if (!out_stream) {
				fprintf(stderr, "Failed allocating output stream\n");
				ret = AVERROR_UNKNOWN;
				goto end;
			}

			ret = avcodec_parameters_copy(out_stream->codecpar, in_codecpar);
			if (ret < 0) {
				fprintf(stderr, "Failed to copy codec parameters\n");
				goto end;
			}
			out_stream->codecpar->codec_tag = 0;
		}
		av_dump_format(ofmt_ctx, 0, out_filename, 1);

		if (!(ofmt->flags & AVFMT_NOFILE)) {
			ret = avio_open(&ofmt_ctx->pb, out_filename, AVIO_FLAG_WRITE);
			if (ret < 0) {
				fprintf(stderr, "Could not open output file '%s'", out_filename);
				goto end;
			}
		}

		ret = avformat_write_header(ofmt_ctx, NULL);
		if (ret < 0) {
			fprintf(stderr, "Error occurred when opening output file\n");
			goto end;
		}

		while (1) {
			AVStream *in_stream, *out_stream;

			in_stream = ifmt_ctx->streams[pkt.stream_index];
			if (pkt.stream_index >= stream_mapping_size ||
				stream_mapping[pkt.stream_index] < 0) {
				av_packet_unref(&pkt);
				continue;
			}

			pkt.stream_index = stream_mapping[pkt.stream_index];
			out_stream = ofmt_ctx->streams[pkt.stream_index];

			/* copy packet */
			pkt.pts = av_rescale_q_rnd(pkt.pts, in_stream->time_base, out_stream->time_base,
									   static_cast<AVRounding>(AV_ROUND_NEAR_INF | AV_ROUND_PASS_MINMAX));
			pkt.dts = av_rescale_q_rnd(pkt.dts, in_stream->time_base, out_stream->time_base,
									   static_cast<AVRounding>(AV_ROUND_NEAR_INF | AV_ROUND_PASS_MINMAX));
			pkt.duration = av_rescale_q(pkt.duration, in_stream->time_base, out_stream->time_base);
			pkt.pos = -1;

			ret = av_interleaved_write_frame(ofmt_ctx, &pkt);
			if (ret < 0) {
				fprintf(stderr, "Error muxing packet\n");
				break;
			}
			av_packet_unref(&pkt);
		}

		av_write_trailer(ofmt_ctx);
		end:

		avformat_close_input(&ifmt_ctx);

		/* close output */
		if (ofmt_ctx && !(ofmt->flags & AVFMT_NOFILE))
			avio_closep(&ofmt_ctx->pb);
		avformat_free_context(ofmt_ctx);

		return 0;
	}
}



int32 Main(const String& programName, const FixedArray<String>& args)
{
	FileSystem::Path inputFilePath = String(u8"/home/amir/Desktop/123.avi");
	FileSystem::Path outputFilePath = String(u8"/home/amir/Desktop/123.mp4");

	FileInputStream fileInputStream(inputFilePath);
	const Format* inputFormat = Format::Find(fileInputStream);

	FileOutputStream fileOutputStream(outputFilePath, true); //TODO: REMOVE THE OVERWRITE

	UniquePointer<Demuxer> demuxer = inputFormat->CreateDemuxer(fileInputStream);
	demuxer->FindStreamInfo();

	//BLA(reinterpret_cast<const char *>(outputFilePath.String().ToUTF8().GetRawZeroTerminatedData()));

	return EXIT_SUCCESS;
}