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
using namespace StdXX::UI;

class MainWindow : public MainAppWindow
{
public:
	//Constructor
	MainWindow(EventHandling::EventQueue &eventQueue);

	//Methods
	void OpenFile(const FileSystem::Path &path);

private:
	//Members
	VideoWidget *videoWidget;
	Slider *videoPos;
	PushButton* playPauseButton;

	UniquePointer<FileInputStream> inputFile;
	UniquePointer<Multimedia::MediaPlayer> mediaPlayer;
	Multimedia::TimeScale ms;

	//Methods
	void TogglePlayPause();

	//Event handlers
	void OnSeek();
};