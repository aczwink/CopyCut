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

def TimeStampToString(ts):
	fractional = ts % 1000000000;
	ts = ts // 1000000000;
	s = ts % 60;
	ts = (ts // 60);
	m = ts % 60;
	ts = (ts // 60);
	h = ts;
	
	return "%02d:%02d:%02d.%09d" % (h, m, s, fractional);