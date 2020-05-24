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
#include "MainWindow.hpp"

//Constructor
MainWindow::MainWindow(EventHandling::EventQueue &eventQueue) : MainAppWindow(eventQueue), ms(1, 1000)
{
	this->SetTitle(u8"Copy Cut");

	//Main container
	this->GetContentContainer()->SetLayout(new VerticalLayout);

	WidgetFrameBufferSetup frameBufferSetup;
	frameBufferSetup.nSamples = 1;

	this->videoWidget = new VideoWidget(frameBufferSetup);
	this->AddContentChild(this->videoWidget);

	//Playback Control
	GroupBox *playbackControl = new GroupBox();
	this->AddContentChild(playbackControl);

	this->videoPos = new Slider();
	this->videoPos->onValueChangedHandler = Function<void()>(&MainWindow::OnSeek, this);
	playbackControl->AddContentChild(this->videoPos);

	//actions panel
	CompositeWidget *actionsPanel = new CompositeWidget();
	actionsPanel->SetLayout(new HorizontalLayout);
	playbackControl->AddContentChild(actionsPanel);

	this->playPauseButton = new PushButton();
	this->playPauseButton->SetText(u8"Play");
	this->playPauseButton->onActivatedHandler = Function<void()>(&MainWindow::TogglePlayPause, this);
	actionsPanel->AddChild(this->playPauseButton);
}

//Public methods
void MainWindow::OpenFile(const FileSystem::Path &path)
{
	this->inputFile = new FileInputStream(path);
	this->mediaPlayer = new Multimedia::MediaPlayer(*this->inputFile);
	this->mediaPlayer->SetVideoOutput(this->videoWidget);
	
	
	Multimedia::Demuxer *demuxer = this->mediaPlayer->GetDemuxer();
	uint64 count = ms.Rescale(demuxer->GetStartTime() + demuxer->GetDuration(), this->ms);
	this->videoPos->SetRange(0, count);
}

//Private methods
void MainWindow::TogglePlayPause()
{
	if(this->mediaPlayer->IsPlaying())
	{
		this->mediaPlayer->Pause();
		this->playPauseButton->SetText(u8"Play");
	}
	else
	{
		this->mediaPlayer->Play();
		this->playPauseButton->SetText(u8"Pause");
	}
}

//Event handlers
void MainWindow::OnSeek()
{
	Multimedia::Demuxer *demuxer = this->mediaPlayer->GetDemuxer();
	uint64 seekPos = this->ms.Rescale(this->videoPos->GetPosition(), demuxer->TimeScale());
	demuxer->Seek(seekPos, demuxer->TimeScale());
}
