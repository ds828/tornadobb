#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#       
#       Copyright 2012 Di SONG <di@di-debian>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import unittest
import logging
try:
	from pytz import common_timezones
	from pytz import timezone
	from pytz import all_timezones
	from pytz import all_timezones_set, common_timezones_set
	from pytz import country_timezones
	import pytz
except ImportError:

    raise ImportError

class CommonTest(unittest.TestCase):
	
	def test_pytz(self):
		
		prefix = "Asia"
		print filter(lambda x:prefix in x,common_timezones)
		
		for tz in common_timezones:
			print tz
		

def main():
	
	unittest.main()
	return 0

if __name__ == '__main__':
	main()
