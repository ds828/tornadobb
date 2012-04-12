#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       settings.py
#       
#       Copyright 2011 Di SONG <di@di-debian>
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

import os
import tornado.web
import tornado.locale
import uimodules
import datetime,time
import logging

__all__ = [	"tornadobb_handlers",
			"tornadobb_settings",
			]

###########################################
#
#	You can change below
#
###########################################
# Forum title
FORUM_TITLE = "TornadoBB Forum"	

# Forum sub title
FORUM_SUB_TITLE = "A Simple & Fast Forum based on Tornodo written by Python and MongoDB"

#html page template
FORUM_TEMPLATE = "fluxbb"

# selected default style
# required, css file name without extend file name
FORUM_STYLE = "Air"

#root url
TORNADOBB_ROOT_URL = r"/tornadobb"

###########################################
#
#	setup administrator
#
###########################################

# admin url, access it with TORNADOBB_ROOT_URL/TORNADOBB_ADMIN_URL
# You can write a very complicated url for security, such as: HQr7$OP, whatever
TORNADOBB_ADMIN_URL = r"/admin"

TORNADOBB_FIRST_ADMIN_NAME="admin"
TORNADOBB_FIRST_ADMIN_PASSWORD="admin"
TORNADOBB_FIRST_ADMIN_EMAIL="songdi19@gmail.com"

# expired time for session
TORNADOBB_SESSION_EXPIRE = 30 #mins

# default time zone
TORNADOBB_TIME_ZONE="Australia/Sydney"

#TORNADOBB_TIME_ZONE="Asia/Shanghai"

###########################################################
#
# setup database
#
###########################################################

# for mongodb
DATABASE_SETTINGS = {
		"engine": "db_backends.mongodb", # name of monogdb moduel
        "host": "localhost",             # Set host address
        "port": 27017,                   # Set port
        "data_file":"db_tornadobb",		 # Set database file
        "safe_mode": True,				 # True is to run as safe mode
        "last_error_options":{"j":False,"w":1,"wtimeout":5000,"fsync":False}, #if safe_mode is True, mongodb will use this as last_error_options
}

# for sqlit3, NO IMPLEMENT yet
#DATABASE_SETTINGS = {
#		"engine": "db_backends.sqlite3",
#        "data_file":"db_tornadobb",		 # Set database file for mongodb
#}


###########################################################
#
#	SMTP settings
#
###########################################################
SMTP_SETTINGS = {

					"server":"smtp.gmail.com",
					"use_authentication": True,
					"tls_port": 587,
					"ssl_port": 465,
					"port":None,
					"username":"tornadobb1@gmail.com",
					"password":"4nE7dbMk",
					"email_address":"tornadobb1@gmail.com",
				}

###########################################################
#
#	Do NOT change below, ONLY IF YOU KNOW WHAT YOU ARE DOING
#
###########################################################

version="0.1"

###########################################################
#
#	Add current path into system path
#
###########################################################
TORNADOBB_ROOT_PATH = os.path.dirname(__file__)
import sys
sys.path.append(TORNADOBB_ROOT_PATH)

##########################################################
#
#	Database backends
#
###########################################################

_db_backends_name = DATABASE_SETTINGS["engine"]
_class_name = _db_backends_name.split('.')[1]
_db_backends_model =__import__(_db_backends_name,globals(),locals(),[_class_name],-1)
db_backend = getattr(_db_backends_model,_class_name)(DATABASE_SETTINGS)

###########################################################
#
#	create the first admin account
#
###########################################################
import hashlib
m = hashlib.md5()
m.update(TORNADOBB_FIRST_ADMIN_PASSWORD)
passowrd = m.hexdigest().upper()
db_backend.do_create_first_admin(TORNADOBB_FIRST_ADMIN_NAME,passowrd,TORNADOBB_FIRST_ADMIN_EMAIL,time.time())

###########################################################
#
#	create a cache for categories and forums
#
###########################################################

_category_forum = db_backend.do_show_all_categories_forums_name_and_id()

###########################################################
#
#	Tornadobb default timezone
#
###########################################################
try:
	from pytz import common_timezones
	from pytz import timezone
except ImportError:

    raise ImportError

_tornadobb_timezone = timezone(TORNADOBB_TIME_ZONE)

###########################################################
#
#	expired_tatal_seconds
#
###########################################################

#for python 2.7.2
#_expired_total_seconds = datetime.timedelta(minutes=settings.tornadobb_default_settings["session_expire"]).total_seconds()
#for blow python 2.7.2
td = datetime.timedelta(minutes=TORNADOBB_SESSION_EXPIRE)
_expired_total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
###########################################################
#
#	Logging
#
###########################################################	

#logging.basicConfig(filename=os.path.join(TORNADOBB_ROOT_PATH, "tornadobb.log"),level=logging.DEBUG,format='%(asctime)s %(message)s')

###########################################################
#
#	i18n support
#
###########################################################

tornado.locale.load_translations(os.path.join(TORNADOBB_ROOT_PATH, "i18n"))

###########################################################
#
#	Tornadobb itself settings
#
###########################################################

_emoticon_1_settings = {
		":D" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-happy.png",
		":(" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-unhappy.png",
		":o" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-surprised.png",
		":p" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-tongue.png",
		";)" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-wink.png",
		":)" : TORNADOBB_ROOT_URL + "/static/images/emoticon/emoticon-smile.png",
		}
		
_emoticon_2_settings = {
		"m1" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood1.gif",
		"m2" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood2.gif",
		"m3" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood3.gif",
		"m4" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood4.gif",
		"m5" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood5.gif",
		"m6" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood6.gif",
		"m7" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood7.gif",
		"m8" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood8.gif",
		"m9" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood9.gif",
		"m10" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood10.gif",
		"m11" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood11.gif",
		"m12" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood12.gif",
		"m13" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood13.gif",
		"m14" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood14.gif",
		"m15" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood15.gif",
		"m16" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood16.gif",
		"m17" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood17.gif",
		"m18" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood18.gif",
		"m19" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood19.gif",
		"m20" : TORNADOBB_ROOT_URL + "/static/images/emoticon2/mood20.gif",
		
		}

###########################################################
#
#	load all permissions settings
#
###########################################################	

_permission_settings = [
						"sticky",
						"distillate",
						"close_topic",
						"hide_topic",
						"unhide_topic",
						"delete_topic",
						"move_topic",
						"delete_post",
						"edit_post",
						"highlight",
					] 
# for topic type, NOT implement yet
"""
_topic_type_settings = [
						"text",
						"vote",
						"picture",
						"video",
						]
"""
###########################################################
#
#	load highlight settings
#
###########################################################	
_highlight_settings = [
						"red",
						"black",
						"underline",
					]
					
###########################################################
#
#	load css style settings
#
###########################################################				

_css_style_settings = [
						"Air",
						"Cobalt",
						"Earth",
						"Fire",
						"Lithium",
						"Mercury",
						"Oxygen",
						"Radium",
						"Sulfur",
						"Technetium",
					]
###########################################################
#
#	Application settings
#
###########################################################

tornadobb_settings = {
		#tornado framework required
		"xsrf_cookies" : True,
		"ui_modules" : uimodules,
		#"static_path" : os.path.join(TORNADOBB_ROOT_PATH, "static"),
		#tornadobb required
		"tornadobb.version":version,
		"tornadobb.root_url": TORNADOBB_ROOT_URL,
		"tornadobb.admin_url": TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL,
		"tornadobb.login_url" : TORNADOBB_ROOT_URL + "/login",
		"tornadobb.template_path" : os.path.join(TORNADOBB_ROOT_PATH, "templates/" + FORUM_TEMPLATE),
		"tornadobb.forum_title" : FORUM_TITLE,
		"tornadobb.forum_sub_title" : FORUM_SUB_TITLE,
		"tornadobb.root_path" : TORNADOBB_ROOT_PATH,
		"tornadobb.timezone_name":TORNADOBB_TIME_ZONE,
		"tornadobb.timezone_obj" : _tornadobb_timezone,
		"tornadobb.session_expire" : _expired_total_seconds,
		"tornadobb.style" : FORUM_STYLE,
		"tornadobb.style_settings" : _css_style_settings,
		#"tornadobb.verify_new_topic": False, #NOT implement yet
		#"tornadobb.topic_default_type" : "text",#NOT implement yet
		#"tornadobb.topic_type_settings": _topic_type_settings,#NOT implement yet
		"tornadobb.topic_default_highlight":"",
		"tornadobb.emoticon_settings" : _emoticon_2_settings,
		"tornadobb.permission_settings" : _permission_settings,
		"tornadobb.highlight_settings" : _highlight_settings,
		"tornadobb.category_forum" : _category_forum,
		"tornadobb.datetime_format": " %Y-%m-%d %H:%M ",
		"tornadobb.default_locale" : "en-US",
		"tornadobb.smtp_settings" : SMTP_SETTINGS,
		"tornadobb.set_access_log_interval" : 10,
		"tornadobb.pagination_pages_num" : 5,
		"tornadobb.topics_num_per_page" : 20,
		"tornadobb.posts_num_per_page" : 20,
		"tornadobb.distillat_threshold" : 60, # replies number
		"tornadobb.subject_min_chars_num":1,
		"tornadobb.subject_max_chars_num":100,
		"tornadobb.post_min_chars_num":20,
		"tornadobb.post_max_chars_num":5000,
		"tornadobb.signature_max_chars_num":400,
		"tornadobb.username_min_chars_num" : 2,
		"tornadobb.username_max_chars_num" : 25,
		"tornadobb.password_min_chars_num" : 5,
		"tornadobb.password_max_chars_num" : 25,
		"tornadobb.category_min_chars_num" : 5,
		"tornadobb.category_max_chars_num" : 25,
		"tornadobb.forum_min_chars_num" : 5,
		"tornadobb.forum_max_chars_num" : 20,
		"tornadobb.forum_des_min_chars_num" : 0,
		"tornadobb.forum_des_max_chars_num" : 50,
        }

###########################################################
#
#	Application handlers
#
###########################################################

from user_app import *
from admin_app import *

tornadobb_handlers = [
			#for the tornadobb can share with other tornado app, it can not have a "static_path" setting, so using below
			(TORNADOBB_ROOT_URL + "/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(TORNADOBB_ROOT_PATH, "static")}),
			(TORNADOBB_ROOT_URL + "/mp$", MarkitupPreviewHandler),
			(TORNADOBB_ROOT_URL + "/sendmail$", SendEmailHandler),
			(TORNADOBB_ROOT_URL + "/tz$", TimezoneHandler),
			url(TORNADOBB_ROOT_URL + "/search/*$", SearchHandler,name="search_page"),
			url(TORNADOBB_ROOT_URL + "/?$", MainHandler,name="home_page"),
			(TORNADOBB_ROOT_URL + "/forum/[a-z0-9]+/[a-z0-9]+/new/*$", PostNewTopicHandler),#post new topic
		    (TORNADOBB_ROOT_URL + "/forum/[a-z0-9]+/[a-z0-9]+/?$", ForumHandler),
		    (TORNADOBB_ROOT_URL + "/topic/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/?$", TopicHandler),
		    (TORNADOBB_ROOT_URL + "/topic/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/cmd$", TopicManagementHandler),
		    (TORNADOBB_ROOT_URL + "/topic/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/reply$", ReplyTopicHandler),#reply a topic
		    (TORNADOBB_ROOT_URL + "/topic/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/edit$", PostEditHandler),#edit a topic
		    (TORNADOBB_ROOT_URL + "/topic/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/delete$", PostDeleteHandler),#delete a topic
		    url(TORNADOBB_ROOT_URL + "/login/*$", UserLoginHandler,name="login_page"),
		    (TORNADOBB_ROOT_URL + "/logout/*$", UserLogoutHandler),
		    (TORNADOBB_ROOT_URL + "/register/*?$", UserRegisterHandler),
		    (TORNADOBB_ROOT_URL + "/resend/*?$", ResendVerifyMailHandler),
		    (TORNADOBB_ROOT_URL + "/active$", UserActiveHandler),
		    (TORNADOBB_ROOT_URL + "/forget/*?$", UserForgetPasswordHandler),
		    (TORNADOBB_ROOT_URL + "/user-info$", UserInfoHandler),
		    url(TORNADOBB_ROOT_URL + "/profile/?$", UserProfileHandler,name="profile_page"),
		    (TORNADOBB_ROOT_URL + "/profile/avatar/*$", UserAvatarHandler),
		    (TORNADOBB_ROOT_URL + "/profile/personality/*$", UserSignatureHandler),
		    (TORNADOBB_ROOT_URL + "/profile/display/*$", UserDisplayHandler),
			(TORNADOBB_ROOT_URL + "/profile/topics/*$", UserTopicsHandler),
			(TORNADOBB_ROOT_URL + "/profile/replies/*$", UserRepliesHandler),
			(TORNADOBB_ROOT_URL + "/profile/pwd/*$", UserPasswordHandler),
			(TORNADOBB_ROOT_URL + "/profile/email/*$", UserEmailHandler),
			(TORNADOBB_ROOT_URL + "/profile/privacy/*$", UserPrivacyHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/?$", AdminDashboardHandler),
			url(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/category/?$", AdminCategoryHandler,name="admin_category_page"),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/category/edit$", AdminCategoryEditHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/category/close$", AdminCategoryOpenCloseHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/category/delete$", AdminCategoryDeleteHandler),
			url(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/forum/?", AdminForumHandler,name="admin_forum_page"),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/forum/edit", AdminForumEditHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/forum/close$", AdminForumOpenCloseHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/forum/delete$", AdminForumDeleteHandler),
			url(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/moderator/?$", AdminModeratorHandler,name="admin_moderator_page"),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/moderator/edit$", AdminModeratorEditHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/moderator/delete$", AdminModeratorDeleteHandler),
			url(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/member/?$", AdminMemberHandler,name="admin_member_page"),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/member/close$", AdminMemberOpenCloseHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/member/postable$", AdminMemberShutHandler),
			(TORNADOBB_ROOT_URL + TORNADOBB_ADMIN_URL + "/member/add$", AdminMemberAddHandler),
			(TORNADOBB_ROOT_URL + "/rules/*$", ForumRulesHandler),
			(TORNADOBB_ROOT_URL + "/language/*$", ChangeLanguageHandler),
			]

