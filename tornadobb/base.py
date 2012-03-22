#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       base.py
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

from tornado.web import *
import datetime, time
from pytz import timezone
from settings import db_backend
from util import *
import functools

class BaseHandler(tornado.web.RequestHandler):

	def get_current_user(self):

		is_auth = self.get_secure_cookie("is_auth")
		locale = self.get_secure_cookie("locale")
		interval = self.settings["tornadobb.set_access_log_interval"]
		
		if not is_auth:
			#This is a guest or offline user
			# guest cookies
			#guest_id:
			#locale:
			#count:	
			
			guest_id = self.get_secure_cookie("guest_id")
			count = self.get_secure_cookie("count")
			
			if guest_id and count:
				count = int(count)
				if count / interval == 1:
					db_backend.do_set_guest_access_log(guest_id,time.time())
					count = 0
					
			else:
				guest_id = db_backend.do_create_guest_access_log(time.time())
				if guest_id:
					self.set_secure_cookie("guest_id",guest_id)
					count = 0
				else:
					raise HTTPError(500)

			self.set_secure_cookie("count",str(count + 1))
			
			
			if locale:
				return {"locale":locale}
			else:	
				return None
		
		#This is a online user
		
		user = {
				"_id" : self.get_secure_cookie("_id"),
				"name" : self.get_secure_cookie("name"),
		}
		#["locale","postable","closed","avatar","permission","role","tz","is_auth"]
		user["locale"] = locale
		
		postable = self.get_secure_cookie("postable")
		if postable:
			user["postable"] = False
		
		closed = self.get_secure_cookie("closed")
		if closed:
			user["closed"] = True
		
		avatar = self.get_secure_cookie("avatar")
		if avatar:
			user["avatar"] = avatar
		
		role = self.get_secure_cookie("role")
		if role:
			user["role"] = role
		
		tz = self.get_secure_cookie("tz")
		if tz:
			user["tz"] = tz
			tz_obj = timezone(tz)
		else:
			tz_obj = self.settings["tornadobb.timezone_obj"]
		
		style = self.get_secure_cookie("style")
		if style:
			user["style"] = style
		
		#each 10 access, write one time access log
		is_auth = int(is_auth)
		if is_auth / interval == 1:
			db_backend.do_set_user_access_log(user["_id"],time.time())
			is_auth = 0
		user["is_auth"] = True
			
		expires = datetime.datetime.now(tz_obj) + datetime.timedelta(seconds=self.settings["tornadobb.session_expire"])
		self.set_secure_cookie("is_auth", str(is_auth + 1),expires=expires)
		
		return user

	def get_login_url(self):
		self.require_setting("tornadobb.login_url", "@tornado.web.authenticated")
		return self.settings["tornadobb.login_url"]
	
	def get_template_path(self):
		return self.settings.get("tornadobb.template_path")
	
	def get_user_locale(self):

		if not self.current_user or "locale" not in self.current_user:
			# Use the Accept-Language header
			return tornado.locale.get(self.settings["tornadobb.default_locale"])
		else:
			return tornado.locale.get(self.current_user["locale"])
	
	def check_xsrf_cookie(self):
		"""
		jump off xsrf check for avatar upload
		upload plugin can NOT send cookies with POST method
		"""
		if "profile/avatar" in self.request.path:
			return
		else:
			super(BaseHandler, self).check_xsrf_cookie()
			
	__error = {
					403:'403.html',
					404:'404.html',
					500:'500.html',
			}
			
	def write_error(self,status_code, **kwargs):
		
		self.render(self.__class__.__error[status_code],data={})
	
	def get(self):
		self.write_error(404)

	def post(self):
		self.write_error(404)

class AdminBaseHandler(BaseHandler):

	def get_current_user(self):
		
		user = super(AdminBaseHandler, self).get_current_user()
		if user and user.get("role","") == "admin":
			return user
		else:
			return None


def authenticated(method):
	"""Decorate methods with this to require that the user be logged in."""
	@functools.wraps(method)
	def wrapper(self, *args, **kwargs):

		if not self.current_user or not self.get_secure_cookie("is_auth"):
			if self.request.method in ("GET", "HEAD"):
				url = self.get_login_url()
				if "?" not in url:
					if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
						next_url = self.request.full_url()
					else:
						next_url = self.request.uri
					url += "?" + urllib.urlencode(dict(next=next_url))
				self.redirect(url)
				return
			raise HTTPError(403)
		return method(self, *args, **kwargs)
	return wrapper
	
def check_url_avaliable(method):
	
	@functools.wraps(method)
	def wrapper(self, *args, **kwargs):
		
		category_id_and_forum_id_and_topic_id = self.request.path.partition(self.settings["tornadobb.root_url"])[2].split("/")
		category_id = category_id_and_forum_id_and_topic_id[2]
		forum_id = category_id_and_forum_id_and_topic_id[3]
		topic_id = None
		if len(category_id_and_forum_id_and_topic_id) >= 5:
			topic_id = category_id_and_forum_id_and_topic_id[4]
		
		for category in self.settings["tornadobb.category_forum"]:
			if category_id == category["_id"] and category.get("closed",False) == False:
				for forum in category["forum"]:
					if forum_id == forum["_id"] and forum.get("closed",False) == False:
						return method(self,category_id,forum_id,topic_id,*args, **kwargs)

		self.write_error(404)
		return
	return wrapper

def load_permission(method):
	
	@functools.wraps(method)
	def wrapper(self, *args, **kwargs):
					
		permission = None
		if self.current_user and self.current_user.get("is_auth"):
			role = self.current_user.get("role",None)
			if role:
				if role == "moderator":
					user_id = self.current_user["_id"]		
					permission = db_backend.do_show_moderator_permission(user_id,forum_id)
				elif role == "admin":
					permission = self.settings["tornadobb.permission_settings"]
		return method(self,*args, permission=permission,**kwargs)

	return wrapper

class SendEmailHandler(BaseHandler):
		
	def post(self):
			
		receiver = self.get_argument("receiver")
		subject = self.get_argument("subject")
		plain = self.get_argument("plain")
		html = self.request.arguments["html"][0]
		send_mail(receiver,subject,plain,html)
