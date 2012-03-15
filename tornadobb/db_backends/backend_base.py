#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       backend_base.py
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



class backend_base(object):
	
	def __init__(self,db_param):
		pass
		
	def do_create_first_admin(self,user,password):
		pass
	
	def do_user_login(self,username,password):

		pass

	def do_check_user_name(self,user_name):
		
		pass
		
	def do_user_register(self,user):
		
		pass
		
	def do_show_user_info(self,user_id):
		"""
		return one dict
		such as below
		admin = {
				"_id":"1234",
				"name":"disong",
				"registered_time":datetime.datetime.today().strftime(" %Y-%m-%d %H:%M "),
				"last_login":datetime.datetime.today().strftime(" %Y-%m-%d %H:%M "),
				"avatar":"songdi.jpg",
				"total_topics_num":2000,
				"total_posts_num":2000,
				"role":"admin",
				}
		"""
		pass
	
	def do_show_user_signature(self,user_id):
		pass
	
	def do_save_user_signature(self,user_id,signature):
		
		pass
	
	def do_reset_user_password(self,user_id,old_password,new_password):
		pass
	
	def do_show_all_categories(self):
		"""
		category_1 = {
						"_id":"1234",
						"name":"Picutes",
						"forums":["Asian Girls","West Girls"],
						"position": 1,
						"alias" : "pictures",
		}
		category_2 = {
						"_id":"1234",
						"name":"V_ideos",
						"forums":["Asian Girls","West Girls"],
						
						"position": 2,
						"alias" : "video",
		}
		category_set= [category_1,category_2]
		"""
		pass
	
	def do_show_one_category(self,category_id):
		"""
		category = {
						"_id":"1234",
						"name":"Picutes",
						"forums":["Asian Girls","West Girls"],
						"position": 1,
						"alias" : "pictures",
		}
		"""
		pass
		
	def do_create_category(self,category):
		
		pass
	
	def do_update_category(self,category):
		
		pass
	
	def do_open_close_category(self,category_id,closed=False):
		
		pass
		
	def do_update_position_category(self,positions):
		
		pass

	def do_create_forum(self,category_id,forum):
		
		pass

	def do_update_forum(self,category_id,old_category_id,forum):
		
		pass
		
	def do_open_close_forum(self,category_id,forum_id,closed=False):
		
		pass
	
	def do_update_position_forum(self,category_id,positions):
		
		pass

