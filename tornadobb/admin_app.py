#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       user_app.py
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

import tornado.web
from base import *
from settings import db_backend
import datetime, time

class AdminDashboardHandler(AdminBaseHandler):
	@authenticated
	@tornado.web.addslash
	def get(self):
		database_info = db_backend.do_show_database_info()
		self.render('admin_dashboard.html',data=locals())

class AdminCategoryHandler(AdminBaseHandler):
	@authenticated
	@tornado.web.addslash
	def get(self):
		
		category_set = db_backend.do_show_all_categories()
		#print category_set
		self.render('admin_category.html',data=locals())
		
	@authenticated	
	def post(self):
		#print self.request.arguments
		name = self.get_argument("category_name",None)
		position = self.get_argument("category_position",None)
		if name and position:
			category = {
						"name" : name.strip(),
						"position" : int(position),
						"closed":False,
						}
			if db_backend.do_create_category(category):
				self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
				self.redirect(self.request.path)
			else:
				self.write_error(500)
		else:
			self.write_error(404)
	
class AdminCategoryEditHandler(AdminBaseHandler):

	@authenticated
	@tornado.web.addslash
	def post(self):
		#print self.request.arguments
		
		_id = self.request.arguments["category_id"]
		name = self.request.arguments["category_name"]
		position = self.request.arguments["category_position"]

		for i,one_id in enumerate(_id):
			if not db_backend.do_update_category(one_id,name[i],int(position[i])):
				self.write_error(500)
		
		self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
		self.redirect(self.reverse_url("admin_category_page"))

class AdminCategoryOpenCloseHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):

		category_id = self.get_argument("id",None)
		cmd = self.get_argument("c",None)
		if category_id and cmd:
		
			if cmd == "close":
				result = db_backend.do_open_close_category(category_id,closed=True)
			elif cmd == "open":
				result = db_backend.do_open_close_category(category_id,closed=False)
			else:
				self.write_error(404)
				return
		if result:
			self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
			self.redirect(self.reverse_url("admin_category_page"))
		else:
			self.write_error(500)
		
class AdminCategoryDeleteHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):

		self.write_error(404)
	

class AdminForumHandler(AdminBaseHandler):
	@authenticated
	@tornado.web.addslash
	def get(self):

		category_set = db_backend.do_show_all_categories()
		self.render('admin_forum.html',data=locals())
	
	@authenticated
	def post(self):
		#print self.request.arguments
		
		category_id = self.get_argument("category_id",None)
		name = self.get_argument("forum_name",None)
		position = self.get_argument("forum_position",None)
		des = self.get_argument("forum_des","")
		if category_id and name and position:
			forum = {
						"name" : name.strip(),
						"position" : int(position),
						"des" : des,
						"closed":False,
						}
			if db_backend.do_create_forum(category_id,forum):
				self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
				self.redirect(self.request.path)
			else:
				self.write_error(500)
		else:
			self.write_error(404)

class AdminForumEditHandler(AdminBaseHandler):
	
	@authenticated
	def post(self):
		#print self.request.arguments
		
		old_category_id = self.request.arguments["old_category_id"]
		new_category_id = self.request.arguments["new_category_id"]
		forum_id = self.request.arguments["forum_id"]
		name = self.request.arguments["forum_name"]
		position = self.request.arguments["forum_position"]
		des = self.request.arguments["forum_des"]
		
		for i,one_forum_id in enumerate(forum_id):
			#print one_forum_id
			if not db_backend.do_update_forum(new_category_id[i],old_category_id[i],one_forum_id,name[i],int(position[i]),des[i]):
				
				self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
				self.write_error(500)
				return

		self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
		self.redirect(self.reverse_url("admin_forum_page"))
		return
		
class AdminForumOpenCloseHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):
		#print self.request.arguments
		category_id = self.get_argument("c_id",None)
		forum_id = self.get_argument("f_id",None)
		cmd = self.get_argument("c",None)
		if category_id and forum_id and cmd:
		
			if cmd == "close":
				result = db_backend.do_open_close_forum(category_id,forum_id,closed=True)
			elif cmd == "open":
				result = db_backend.do_open_close_forum(category_id,forum_id,closed=False)
			else:
				self.write_error(404)
				return
			if result:
				self.settings["tornadobb.category_forum"] = db_backend.do_show_all_categories_forums_name_and_id()
				self.redirect(self.reverse_url("admin_forum_page"))
		else:
			self.write_error(404)
			return

class AdminForumDeleteHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):

		self.write_error(404)

class AdminModeratorHandler(AdminBaseHandler):
	
	@authenticated
	@tornado.web.addslash
	def get(self):
				
		category_forum_set = db_backend.do_show_all_moderators()
		self.render('admin_moderator.html',data=locals())
	
	@authenticated	
	def post(self):
		#print self.request.arguments
		category_forum_id = self.get_argument("category_forum_id",None)
		moderator_name = self.get_argument("moderator_name",None)
		if category_forum_id and moderator_name and "permission" in self.request.arguments:
			permission = self.request.arguments["permission"]
			category_id_and_forum_id = category_forum_id.split('/')
			category_id = category_id_and_forum_id[0]
			forum_id = category_id_and_forum_id[1]
			moderator = db_backend.do_show_user_id_with_name(moderator_name)
			if moderator:
				if db_backend.do_create_moderator(category_id,forum_id,moderator["_id"],moderator_name,permission):
					self.redirect(self.request.path)
				else:
					self.write_error(500)
			else:
				errors = ["Fail to find one user named " + moderator_name]
				category_forum_set = db_backend.do_show_all_categories()
				self.render('admin_moderator.html',data=locals())
		else:
			self.write_error(404)
			
class AdminModeratorEditHandler(AdminBaseHandler):
		
	@authenticated
	def post(self):
		#print self.request.arguments
		
		forum_id = self.get_argument("forum_id",None)
		moderator_id = self.get_argument("moderator_id",None)
		if forum_id and moderator_id and "permission" in self.request.arguments:
			permission = self.request.arguments["permission"]
			if db_backend.do_update_moderator(forum_id,moderator_id,permission):
				self.redirect(self.reverse_url("admin_moderator_page"))
			else:
				self.write_error(500)
		else:
			self.write_error(404)

class AdminModeratorDeleteHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):

		category_id = self.get_argument("c_id",None)
		forum_id = self.get_argument("f_id",None)
		moderator_id = self.get_argument("u_id",None)
		if category_id and forum_id and moderator_id:
			if db_backend.do_delete_moderator(category_id,forum_id,moderator_id):
				self.redirect(self.reverse_url("admin_moderator_page"))
				return
		self.write_error(500)

class AdminMemberHandler(AdminBaseHandler):
	
	@authenticated
	@tornado.web.addslash
	def get(self):
		
		self.render('admin_member.html',data=locals())
	
	@authenticated
	@tornado.web.addslash
	def post(self):
		
		#print self.request.arguments
		member_name = self.get_argument("member_name",None)
		if member_name:
			member_set = db_backend.do_show_user_info_with_name(member_name)
			if not member_set:
				errors = ["Fail to find members with the name " + member_name]
			self.render('admin_member.html',data=locals())
		else:
			self.write_error(404)
			
class AdminMemberOpenCloseHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):
		
		member_id = self.get_argument("m_id",None)
		cmd = self.get_argument("c",None)
		
		if member_id and cmd:
			if cmd == "close":
				result = db_backend.do_open_close_user(member_id,closed=True)
			elif cmd == "open":
				result = db_backend.do_open_close_user(member_id,closed=False)
			if result:
				self.redirect(self.reverse_url("admin_member_page"))
			else:
				self.write_error(500)
		else:
			self.write_error(404)

class AdminMemberShutHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):
		
		member_id = self.get_argument("m_id",None)
		cmd = self.get_argument("c",None)
		
		if member_id and cmd:			
			if cmd == "shut":
				result = db_backend.do_postable_dispostable_user(member_id,postable=False)
			elif cmd == "open":
				result = db_backend.do_postable_dispostable_user(member_id,postable=True)
			if result:
				self.redirect(self.reverse_url("admin_member_page"))
			else:
				self.write_error(500)
		else:
			self.write_error(404)

class AdminMemberAddHandler(AdminBaseHandler):
	
	@authenticated
	def get(self):
		
		self.render('admin_member_add.html',data=locals())
	
	@authenticated
	def post(self):
		#print self.request.arguments	
		username = self.get_argument('username')
		email = self.get_argument('email',None)
		#check username and email
		if not db_backend.do_check_user_name(username):
			errors = ["This username: %s has already been used" % username]
		else:
			display_email = bool(self.get_argument('display_email',False))
			password = self.get_argument('password1')
			m = hashlib.md5()
			m.update(password)
			password = m.hexdigest().upper()
			
			active = bool(self.get_argument('active',False))
			
			user = {
					"name" : username,
					"password": password,
					"email" : email,
					"registered_time":time.time(),
					"display_email":display_email,
					}
					
			if db_backend.do_user_register(user):
				if active and db_backend.do_active_user_account(username,password):
					pass
				else:
					self.write_error(500)
					return
			else:
				self.write_error(500)
				return
		
		self.render('admin_member_add.html',data=locals())
		return

class AdminMemberAddWithFileHandler(AdminBaseHandler):
	
	@authenticated
	def post(self):
		
		file1 = self.request.files['Filedata'][0]
		print file1['body']
		
