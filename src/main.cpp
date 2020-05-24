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
//Local
#include "StreamCopyCutter.hpp"
#include "MainWindow.hpp"

void Cut()
{
	FileSystem::Path inputFilePath = String(u8"/home/amir/Desktop/123.mp4");
	FileSystem::Path outputFilePath = String(u8"/home/amir/Desktop/1234.mp4");

	FileInputStream fileInputStream(inputFilePath);
	FileOutputStream fileOutputStream(outputFilePath, true); //TODO: REMOVE THE OVERWRITE

	const Format* outputFormat = Format::FindByExtension(outputFilePath.GetFileExtension());

	StreamCopyCutter streamCopyCutter(fileInputStream, fileOutputStream);
	streamCopyCutter.Cut(*outputFormat, 1000000 * 20, 1000000 * 40);
}

int32 Main(const String& programName, const FixedArray<String>& args)
{
	EventHandling::StandardEventQueue eventQueue;
	MainWindow *mainWindow = new MainWindow(eventQueue);

	if (!args.IsEmpty())
		mainWindow->OpenFile(args[0]);
	mainWindow->Show();

	eventQueue.ProcessEvents();
	return EXIT_SUCCESS;
}