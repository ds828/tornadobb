#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       mongodb.py
#       
#       Copyright 2012 Di SONG <songdi19@gmail.com>
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

import logging
import time
from backend_base import backend_base
try:
	from pymongo import Connection
	from bson.objectid import ObjectId
	from bson.errors import *
	from pymongo import ASCENDING, DESCENDING
	from pymongo.errors import *
except ImportError:

    raise ImportError

class mongodb(backend_base):
	
	_db_conn = None
	_database = None
	
	def __init__(self,db_param):
		try:
			self.__class__._db_conn = Connection(db_param['host'], db_param['port'])			
			self.__class__._database = self.__class__._db_conn[db_param.get("db_file","db_tornadobb")]
			
			#setup safe_mode
			safe_mode = db_param.get("safe_mode",False)
			if safe_mode:
				self.__class__._database.safe = True
				last_error_options = db_param.get("last_error_options",{})
				self.__class__._database.set_lasterror_options(j=last_error_options.get("j",False), w=last_error_options.get("w",1), wtimeout=last_error_options.get("wtimeout",5000), fsync=last_error_options.get("fsync",False))
			else:
				self.__class__._database.safe = False
				self.__class__._database.unset_lasterror_options()
			
			#judge whether does guest_access_log exist
			
			has_guest = False
			all_collections = self.__class__._database.collection_names()
			for collection_name in all_collections:
				if collection_name == "guest_access_log":
					has_guest = True
			
			# if not, create it
			if not has_guest:
				self.__class__._database.create_collection("guest_access_log",size = 100000,capped = True, max = 500)
				self.__class__._database["guest_access_log"].create_index([("last_access",DESCENDING)])
			
			#create index
			# for user
			self.__class__._database["user"].create_index([("name",DESCENDING)])
			self.__class__._database["user"].create_index([("email",DESCENDING)])
			self.__class__._database["user"].create_index([("name",DESCENDING),("password",DESCENDING)])
			self.__class__._database["user"].create_index([("_id",DESCENDING),("password",DESCENDING)])
			self.__class__._database["user"].create_index([("last_access",DESCENDING)])
			
			
		except Exception, e:
			logging.exception(e)

	@property
	def _database(self):
		return self.__class__._database
		
	def do_create_first_admin(self,admin_name,password,email,register_time):
		""" create a admin account ,if this admin account exists, just update it"""
		try:
			self._database["user"].ensure_index([("name",DESCENDING)])
			if self._database["user"].find_one({"name":admin_name}):
				self._database["user"].update({"name":admin_name},{"$set":{"password":password,"role":"admin","email":email,"registered_time":register_time,"verify":True}})
				logging.info("update admin name: %s" % admin_name)
				return True
			else:
				admin = { 
					"name":admin_name, 
					"password":password,
					"role":"admin",
					"email":email,
					"registered_time":register_time,
					"verify":True,
					}
				self._database["user"].insert(admin)
				logging.info("create admin name: %s" % admin_name)
				return True
			
		except OperationFailure,e:
			logging.exception(e) 
			return False

			
	def do_check_user_name(self,user_name):
		""" 
			check this user account whether already been registered before
			If used, return True, or False
		"""
		self._database["user"].ensure_index([("name",DESCENDING)])
		print self._database["user"].find_one({"name":user_name},fields=["_id"])
		if user_name and self._database["user"].find_one({"name":user_name},fields=["_id"]):
			return True
		else:
			return False
			
	def do_check_user_email(self,email):
		
		self._database["user"].ensure_index([("email",DESCENDING)])
		if email and self._database["user"].find_one({"email":email},fields=["_id"]):
			return True
		else:
			return False
	
	def do_user_login(self,user_name,password,current_time,xsrf_value):
		"""  
			do user login action 
			If the account is not verifed, return "not_verify",None
			OR return "ok", user dict
			If some error cccures, return "fail",None
			the fields of user dict MUST have:
				"name",
				"locale",
				"postable",
				"closed",
				"avatar",
				"permission",
				"role",
				"tz",
				"verify",
		"""

		if user_name and password and current_time:
			fields = [
						"name",
						"locale",
						"postable",
						"closed",
						"avatar",
						"permission",
						"role",
						"tz",
						"verify",
						"style",
					]
			
			user = self._database["user"].find_and_modify({"name":user_name,"password":password},{"$set":{"last_access":current_time,"xsrf":xsrf_value}},fields=fields)
			if user:
				if not user.get("closed",False):
					if not user.get("verify",False):
						return "not_verify",None
					else:
						return "ok",user
				else:
					return "closed",user
		
		return "fail",None
	
	def do_set_user_access_log(self,user_id,current_time):
		"""
			according to the interval setting in tornadobb_settings
			after each interval, set a access time for user
		"""
		
		try:
			if type(user_id) is not ObjectId:
				user_id = ObjectId(user_id)
			self._database["user"].update({"_id":user_id},{"$set":{"last_access" : current_time}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False			

	def do_user_logout(self,user_id):
		"""
			for mongodb, this method is useless
			the judgement of user online status depends on "last_access"
		"""
		return True

	def do_user_register(self,user):
		
		"""
			do user register
			user is dict which MUST have:
			user = {
					"name" : username,
					"password": password,
					"email" : email,
					"registered_time":time.time(),
					"display_email":display_email,
					}
			OR
			add user_list for admin 
			user_list [{
					"name" : username,
					"password": password,
					"email" : email,
					"registered_time":time.time(),
					"display_email":display_email,
					"verify":True|False
					}]	
		"""
		try:
			user_id = self._database["user"].insert(user)
			return str(user_id)
		except OperationFailure,e:
			logging.exception(e)
			return None
		
	def do_show_user_id_with_name(self,name):
		
		"""
			find one user id weith its name
			this method only is used by AdminModeratorHandler in admin_app.py
			
		"""
		
		return self._database["user"].find_one({"name":name},fields=["_id"])
		
	def do_show_user_info_with_id(self,user_id):
		
		"""
			find one user with user id
			return user dict
			the fields MUST have
					"name",
					"email",
					"registered_time",
					"last_access",
					"topics_num",
					"replies_num",
					"display_email",
					"role",
					"avatar",
		"""
		
		try:
			if type(user_id) is not ObjectId:
				user_id = ObjectId(user_id)
		except InvalidId,e:
			return None
		
		fields = [
					"name",
					"email",
					"registered_time",
					"last_access",
					"topics_num",
					"replies_num",
					"display_email",
					"role",
					"avatar",
					"tz",
				]
		return self._database["user"].find_one({"_id":user_id},fields=fields)
		
	def do_show_user_info_with_name(self,name):
		
		"""
			find one user with user name
			return user dict
			the fields MUST have
					"name",
					"email",
					"registered_time",
					"last_access",
					"topics_num",
					"replies_num",
					"display_email",
					"role",
					"avatar",
		"""
		
		fields = [
					"name",
					"email",
					"registered_time",
					"last_access",
					"topics_num",
					"replies_num",
					"postable",
					"closed",
				]
		return list(self._database["user"].find({"name":{"$regex":"^%s" % name}},fields=fields))
				
	def do_show_user_signature(self,user_id):
		
		"""
			shoud the signature of user with user id
		
		"""
		
		try:
			if type(user_id) is not ObjectId:
				user_id = ObjectId(user_id)
		except InvalidId,e:
			return None
		
		user = self._database["user"].find_one({"_id":user_id},fields=["signature"])
		if user:
			return user.get("signature","")
		else:
			return None
		
	def do_save_user_signature(self,user_id,signature):
		
		"""
			save the signature for user
		"""
		
		try:
			if type(user_id) is not ObjectId:
				user_id = ObjectId(user_id)
		
			self._database["user"].update({"_id":user_id},{"$set":{"signature":signature}})
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False		
			
	def do_update_user_password(self,user_id,old_password,new_password):
		
		"""
			update user password
		"""
		
		try:
			if type(user_id) is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id,"password":old_password},{"$set":{"password":new_password}})
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False		
	
	def do_show_newest_users(self,limit=20):
		
		"""
			show the newest users with limit count
			return user list, user count
			
		"""
		
		users = self._database["user"].find(sort=[("_id",-1)],fields=["_id","name"],limit=limit)
		count = users.count()
		return list(users),count
		
	def do_show_online_users(self,expired_time,limit=50):
		
		"""
			show online users with limit count
			If last_access is great than expired time, the user is online
			return user_list, user count
		"""
		
		users = self._database["user"].find({"last_access":{"$gt":expired_time}},fields=["_id","name"],limit=limit)
		count = users.count()
		return list(users),count

	def do_create_guest_access_log(self,current_time):
		
		"""
			for a guest, create a access log for it
			return gest_id as string
		"""
		
		try:
			guest_id = self._database["guest_access_log"].insert({"last_access":current_time})
			return str(guest_id)
		
		except OperationFailure as e:
			logging.exception(e)
			return None			

	def do_set_guest_access_log(self,guest_id,current_time):
		
		"""
			according to the interval setting in tornadobb_settings
			after each interval, set a access time for guest
		"""
		
		try:
			if type(guest_id) is not ObjectId:
				guest_id = ObjectId(guest_id)
	
			self._database["guest_access_log"].update({"_id":guest_id},{"$set":{"last_access":current_time}})
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False	
	
	def do_show_online_guests_num(self,expire_time):
		
		"""
			show online guest count
		"""
		
		return self._database["guest_access_log"].find({"last_access":{"$gt":expire_time}}).count()
	
	def do_show_all_categories(self):
		"""
		file: admin_app
		method: AdminCategoryHandler , AdminForumHandler
		"""
		return list(self._database["category_forum"].find(sort=[("position",1),("forum.position",1)]))
	
	def do_show_all_categories_forums_for_homepage(self):
		
		"""
			for homepage , show category and forum info which the homepage need
			the fields are:
					"name",
					"forum._id",
					"forum.name",
					"forum.des",
					"forum.topics_num",
					"forum.replies_num",
					"forum.last_post_time",
					"forum.last_poster_name",
					"forum.last_post_topic_id",
					"forum.position",
					"forum.closed",
					"forum.moderator",
		"""

		fields = [
					"name",
					"forum._id",
					"forum.name",
					"forum.des",
					"forum.topics_num",
					"forum.replies_num",
					"forum.last_post_time",
					"forum.last_poster_name",
					"forum.last_post_topic_id",
					"forum.position",
					"forum.closed",
					"forum.moderator",
				]
		
		category = list(self._database["category_forum"].find({"closed":False},sort=[("position",1)],fields=fields))
		return category
		
		
	def do_show_all_categories_forums_name_and_id(self):
		
		"""
			for cache categories and forums, only load their ids and names
		"""
		
		categories = list(self._database["category_forum"].find({"closed":False},sort=[("position",1)],fields=["name","forum._id","forum.name","forum.closed"]))
		
		for category in categories:
			category["_id"] = str(category["_id"])
			for forum in category.get("forum",[]):
				forum["_id"] = str(forum["_id"])
		
		return categories

	def do_create_category(self,category):
		
		"""
			create a new category
			the category dict MUST have:
			category = {
						"name" : name.strip(),
						"position" : int(position),
						"closed":False,
						}
		"""
		
		try:
			self._database["category_forum"].insert(category)
			return True
			
		except OperationFailure,e:
			logging.exception(e)
			return False
	
	def do_update_category(self,category_id,category_name,category_position):
		
		"""
			update a category
		
		"""
		
		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)

			self._database["category_forum"].update({"_id":category_id},{"$set": {"name": category_name, "position": category_position}})
			return True
			
		except InvalidId,e:
			return False	
		except OperationFailure,e:
			logging.exception(e)
			return False
			
	def do_open_close_category(self,category_id,closed=False):
		
		"""
			set the category to close or open
		"""
		
		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
		
			self._database["category_forum"].update({"_id":category_id},{"$set": {"closed": closed}})
			return True

		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False		

	def do_create_forum(self,category_id,forum):
		
		"""
			create a new forum
			forum dict:
			forum = {
						"name" : name.strip(),
						"position" : int(position),
						"des" : des,
						"closed":False,
						}
		"""
		
		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
	
			forum["_id"] = str(ObjectId())

			self._database["category_forum"].update({"_id":category_id},{ "$addToSet" : { "forum" : forum }})
			#TODO: HERE create collection for forum and create index
			self._database[forum["_id"]].create_index([("dist",DESCENDING),("dist_level",DESCENDING)])
			self._database[forum["_id"]].create_index([("last_post_time",DESCENDING)])
			self._database[forum["_id"]].create_index([("last_post_time",DESCENDING),("dist",DESCENDING),("dist_level",DESCENDING)])
			self._database[forum["_id"]].create_index([("subject",ASCENDING)])
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
			
	def do_update_forum(self,new_category_id,old_category_id,forum_id,forum_name,forum_position,forum_des):
		
		try:
			if type(new_category_id) is not ObjectId:
				new_category_id = ObjectId(new_category_id)
				
			if type(old_category_id) is not ObjectId:
				old_category_id = ObjectId(old_category_id)	
	
			if new_category_id == old_category_id:
				self._database["category_forum"].update({"_id":old_category_id,"forum._id":forum_id},{"$set": {"forum.$.name": forum_name,"forum.$.position":forum_position,"forum.$.des":forum_des}})
				return True
			else:
				result_set = self._database["category_forum"].find_one({"_id":old_category_id,"forum._id":forum_id},fields=["forum"])
				if result_set:
					for forum in result_set["forum"]:
						if forum_id == forum["_id"]:
							forum["name"] = forum_name
							forum["position"] = forum_position
							forum["des"] = forum_des		
							self._database["category_forum"].update({"_id":new_category_id},{"$addToSet": {"forum": forum}})
							self._database["category_forum"].update({"_id":old_category_id},{"$pull": {"forum" : {"_id" : forum_id}}})
							break
					return True
				else:
					return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		
	def do_open_close_forum(self,category_id,forum_id,closed=False):
		
		"""
			set one forum to open or close
		
		"""
		
		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
		
			self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},{"$set": {"forum.$.closed": closed}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_all_moderators(self):
		
		all_categories =  list(self._database["category_forum"].find(sort=[("position",1)],field=["_id","name","forum._id","forum.name","forum.moderator"]))
		for category in all_categories:
			for forum in category.get("forum",[]):
				for moderator in forum.get("moderator",[]):
					wanted_moderator = self._database["user"].find_one({"_id":moderator["_id"]},fields=["perm_"+str(forum["_id"])])
					if wanted_moderator:
						moderator["permission"] = wanted_moderator.get("perm_"+str(forum["_id"]))
					
		return 	all_categories
			
	def do_create_moderator(self,category_id,forum_id,moderator_id,moderator_name,permission):

		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
			if type(moderator_id)is not ObjectId:
				moderator_id = ObjectId(moderator_id)
			
			moderator = {
						"_id" : moderator_id,
						"name" : moderator_name,	
					}

			self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},{"$addToSet":{"forum.$.moderator":moderator}})
			update = {
						"$addToSet":{"moderator":forum_id},
						"$set":{"perm_" + forum_id : permission ,"role":"moderator" },
					}
			self._database["user"].update({"_id":moderator_id},update)
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_update_moderator(self,forum_id,moderator_id,permission):
		
		try:
			
			if type(moderator_id)is not ObjectId:
				moderator_id = ObjectId(moderator_id)

			self._database["user"].update({"_id":moderator_id},{"$set":{"perm_"+forum_id : permission}})		
			return True
			
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_delete_moderator(self,category_id,forum_id,moderator_id):

		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
			if type(moderator_id)is not ObjectId:
				moderator_id = ObjectId(moderator_id)
	
			self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},{"$pull":{"forum.$.moderator":{"_id":moderator_id}}})
			user = self._database["user"].find_and_modify({"_id":moderator_id},{"$unset":{"perm_" + forum_id : 1 },"$pull":{"moderator":forum_id}},new=True)
			if user and not user["moderator"]:			
				self._database["user"].update({"_id":moderator_id},{"$unset":{"role":1}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_moderator_permission(self,moderator_id,forum_id):
		
		try:
			if type(moderator_id)is not ObjectId:
				moderator_id = ObjectId(moderator_id)
		except InvalidId,e:
			return None

		moderator = self._database["user"].find_one({"_id":moderator_id},fields=["perm_" + forum_id])
		if moderator:			
			return moderator.get("perm_"+ forum_id,None)
		return None
	

	def do_open_close_user(self,user_id,closed=False):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
				
			self._database["user"].update({"_id":user_id},{"$set":{"closed":closed}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_postable_dispostable_user(self,user_id,postable=False):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
				
			self._database["user"].update({"_id":user_id},{"$set":{"postable":postable}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_jump_to_first_page(self,forum_id,items_num_per_page,filter_view="all",order_by="post",dist_level=60):

		collection_name = forum_id
		
		sort = ("last_post_time",-1)	
		if order_by == "create":
			sort = ("create_time",-1)
		
		query = {}
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
			
		elif filter_view == "dist":
			query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level }}]}
			self._database[collection_name].ensure_index([("dist",DESCENDING),("dist_level",DESCENDING)])
			
		return list(self._database[collection_name].find(query,sort=[("sticky",-1),sort],fields={"posts":0},limit=items_num_per_page))
		
		
	def do_jump_to_lastest_page(self,forum_id,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
					
		items_num_lastest_page = self._database[forum_id].count() % items_num_per_page
		
		if items_num_lastest_page == 0:
			items_num_lastest_page = items_num_per_page
		
		collection_name = forum_id
		
		sort = ("last_post_time",1)	
		if order_by == "create":
			sort = ("create_time",1)
		
		query = {}
		if filter_view == "hide":
			
			collection_name = forum_id + "_hide"
			
		elif filter_view == "dist":
			query = { "$or" : [{ "dist":True } , { "dist_level" : { "$gt" : dist_level}}]}
			self._database[collection_name].create_index([("dist",DESCENDING),("dist_level",DESCENDING)])
			
		topics =  list(self._database[collection_name].find(query,sort=[("sticky",-1),sort],fields={"posts":0},limit=items_num_lastest_page))
		topics.reverse()
		return topics
	
	def do_show_prev_page_topics(self,forum_id,begin,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
		
		begin = begin + 0.005
		collection_name = forum_id
		
		sort = ("last_post_time",1)
		if order_by == "create":
			sort = ("create_time",1)
		
		query = {"last_post_time":{"$gt":begin}}
		
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
			
		elif filter_view == "dist":
			query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level}}],"last_post_time":{"$gt":begin}}
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING),("dist",DESCENDING),("dist_level",DESCENDING)])
			
		else:
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
				
		topics = list(self._database[collection_name].find(query,sort=[sort],fields={"posts":0},limit=items_num_per_page))
		topics.reverse()
		return topics
		
	def do_show_next_page_topics(self,forum_id,begin,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
		
		begin = begin - 0.005
		collection_name = forum_id
		
		sort = ("last_post_time",-1)	
		if order_by == "create":
			sort = ("create_time",-1)
		
		query = {"last_post_time":{"$lt":begin}}
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
			
		elif filter_view == "dist":
			query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level}}],"last_post_time":{"$lt":begin}}	
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING),("dist",DESCENDING),("dist_level",DESCENDING)])
			
		else:
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
			
		return list(self._database[collection_name].find(query,sort=[("sticky",-1),sort],fields={"posts":0},limit=items_num_per_page))
		
	def do_jump_back_to_show_topics(self,forum_id,begin,items_num_per_page,current_page_no,jump_to_page_no,filter_view="all",order_by="post",dist_level=60):
		
		begin = begin - 0.005
		offset = jump_to_page_no - current_page_no - 1
		collection_name = forum_id

		sort = ("last_post_time",-1)
		if order_by == "create":
			sort = ("create_time",-1)
		
		query = {"last_post_time":{"$lt":begin}}
		
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
			
		elif filter_view == "dist":
			query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level}}],"last_post_time":{"$lt":begin}}	
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING),("dist",DESCENDING),("dist_level",DESCENDING)])
		
		else:
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
			
		return list(self._database[collection_name].find(query,sort=[("sticky",-1),sort],fields={"posts":0}).skip(offset * items_num_per_page).limit(items_num_per_page))	
		
	def do_jump_forward_to_show_topics(self,forum_id,begin,items_num_per_page,current_page_no,jump_to_page_no,filter_view="all",order_by="post",dist_level=60):
		
		begin = begin + 0.005
		offset = current_page_no - jump_to_page_no - 1
		collection_name = forum_id
		
		sort = ("last_post_time",1)	
		if order_by == "create":
			sort = ("create_time",1)
		
		query = {"last_post_time":{"$gt":begin}}
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
		elif filter_view == "dist":
			query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level}}],"last_post_time":{"$gt":begin}}
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING),("dist",DESCENDING),("dist_level",DESCENDING)])
		else:
			self._database[collection_name].ensure_index([("last_post_time",DESCENDING)])
					
		topics = list(self._database[collection_name].find(query,sort=[("sticky",-1),sort],fields={"posts":0}).skip(offset * items_num_per_page).limit(items_num_per_page))
		topics.reverse()
		return topics
		
	def do_create_topic_pagination(self,forum_id,current_page_no,current_page_top,current_page_bottom,items_num_per_page,pages_num,topics_num,filter_view="all",order_by="post",dist_level=60):
		
		if not pages_num:
			
			query = {}
			collection_name = forum_id
			if filter_view == "hide":
				
				collection_name = forum_id + "_hide"
				
			elif filter_view == "dist":
				query = { "$or" : [ { "dist":True } , { "dist_level" : { "$gt" : dist_level}}]}
				self._database[collection_name].ensure_index([("dist",DESCENDING),("dist_level",ASCENDING)])
				
			topics_num = self._database[collection_name].find(query,fields=["_id"]).count()
			
			quotient,remainder = divmod(topics_num,items_num_per_page)
			if remainder == 0:
				pages_num = quotient
			else:
				pages_num = quotient + 1

		else:
			pages_num = int(pages_num)

		pagination_obj = {
							"has_previous": current_page_no > 1,
							"has_next": current_page_no < pages_num,
							"pages_num": pages_num,
							"current_page_num":current_page_no,
							"current_page_top":current_page_top,
							"current_page_bottom":current_page_bottom,
							"filter_view":filter_view,
							"order_by" : order_by,
							"total_items_num":topics_num,
						}
		return pagination_obj
	
	def do_create_post_pagination(self,forum_id,topic_id,current_page_no,items_num_per_page,pages_num,total_items_num,filter_view="all"):
		
		if not pages_num:
			
			try:
				if type(topic_id)is not ObjectId:
					topic_id = ObjectId(topic_id)
			except InvalidId,e:
				return None
			
			collection_name = forum_id
			if filter_view == "hide":
				collection_name = forum_id + "_hide"
			
			topic = self._database[collection_name].find_one({"_id":topic_id},fields=["posts"])
			if topic:
				
				total_items_num = len(topic.get("posts",[]))
				quotient,remainder = divmod(total_items_num,items_num_per_page)
				if remainder == 0:
					pages_num = quotient
				else:
					pages_num = quotient + 1
			else:
				return None
		else:
			pages_num = int(pages_num)

		pagination_obj = {
							"has_previous": current_page_no > 1,
							"has_next": current_page_no < pages_num,
							"pages_num": pages_num,
							"current_page_num":current_page_no,
							"total_items_num":total_items_num,
						}
		return pagination_obj
		
	def do_create_user_topics_pagination(self,user_id,category_id,forum_id,current_page_no,items_num_per_page,pages_num,total_items_num):
		
		bk_user_id = user_id
		
		if not pages_num:
			
			try:
				if type(user_id)is not ObjectId:
					user_id = ObjectId(user_id)
			except InvalidId,e:
				return None
			
			user = self._database["user"].find_one({"_id":user_id},fields=["topic_" + forum_id])
			if user:
				total_items_num = len(user.get("topic_" + forum_id,[]))
				quotient,remainder = divmod(total_items_num,items_num_per_page)
				if remainder == 0:
					pages_num = quotient
				else:
					pages_num = quotient + 1
			else:
				return None
		else:
			pages_num = int(pages_num)

		pagination_obj = {
							"user_id" : bk_user_id,
							"category_id" : category_id, 
							"forum_id" : forum_id,
							"has_previous": current_page_no > 1,
							"has_next": current_page_no < pages_num,
							"pages_num": pages_num,
							"current_page_num":current_page_no,
							"total_items_num":total_items_num,
						}
		return pagination_obj
		
	def do_create_user_replies_pagination(self,user_id,category_id,forum_id,current_page_no,items_num_per_page,pages_num,total_items_num):
		
		bk_user_id = user_id
		
		if not pages_num:
			
			try:
				if type(user_id)is not ObjectId:
					user_id = ObjectId(user_id)
			except InvalidId,e:
				return None
			
			user = self._database["user"].find_one({"_id":user_id},fields=["reply_" + forum_id])
			if user:
				
				total_items_num = len(user.get("reply_" + forum_id,[]))
				quotient,remainder = divmod(total_items_num,items_num_per_page)
				if remainder == 0:
					pages_num = quotient
				else:
					pages_num = quotient + 1
			else:
				return None
		else:
			pages_num = int(pages_num)

		pagination_obj = {
							"user_id" : bk_user_id,
							"category_id" : category_id, 
							"forum_id" : forum_id,
							"has_previous": current_page_no > 1,
							"has_next": current_page_no < pages_num,
							"pages_num": pages_num,
							"current_page_num":current_page_no,
							"total_items_num":total_items_num,
						}
		return pagination_obj		
		
	def do_show_topic_posts(self,forum_id,topic_id,current_page_no,items_num_per_page,expire_time,filter_view="all"):

		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
		except InvalidId,e:
			return None
	
		begin = (current_page_no - 1) * items_num_per_page
		
		fields = {
					"subject":1,
					"need_reply":1,
					"need_reply_for_attach":1,
					"sticky":1,
					"dist_level":1,
					"dist":1,
					"closed":1,
					"posts":{"$slice": [begin, items_num_per_page]}
					}
		
		collection_name = forum_id
		if filter_view == "hide":
			collection_name = forum_id + "_hide"
		
		topic = self._database[collection_name].find_one({"_id":topic_id},fields=fields)
		
		if not topic:
			return None
		
		posts = topic.get("posts",[])
			
		user_list = list(set([post["poster_id"] for post in posts]))

		fields = [
					"name",
					"role",
					"avatar",
					"signature",
					"registered_time",
					"topics_num",
					"replies_num",
					"last_access",
					"display_email",
					"email",
				]
		
		users = list(self._database["user"].find({"_id":{"$in":user_list}},fields=fields))
		
		for post in posts:
			for user in users:
				if post["poster_id"] == user["_id"]:
					post["poster_name"] = user["name"]
					post["poster_role"] = user.get("role","Member")
					post["poster_display_email"] = user.get("display_email",False)
					post["poster_email"] = user["email"]
					if "avatar" in user:
						post["poster_avatar"] = user["avatar"]
					if "signature" in user:
						post["poster_signature"] = user["signature"]
					if "registered_time" in user:
						post["poster_registered_time"] = user["registered_time"]
					if "topics_num" in user or "replies_num" in user:
						post["poster_posts_num"] = user.get("topics_num",0) + user.get("replies_num",0)

					post["poster_online"] = user.get("last_access",0) >= expire_time
		
		return topic

	def do_make_topic_sticky(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)

			topic = self._database[forum_id].find_one({"_id":topic_id},fields=["sticky"])
			if topic:
				self._database[forum_id].update({"_id":topic_id},{"$set":{"sticky": not topic.get("sticky",False)}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		
	def do_make_topic_dist(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)

			topic = self._database[forum_id].find_one({"_id":topic_id},fields=["dist"])
			if topic:
				self._database[forum_id].update({"_id":topic_id},{"$set":{"dist": not topic.get("dist",False)}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		
	def do_make_topic_close(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)

			topic = self._database[forum_id].find_one({"_id":topic_id},fields=["closed"])
			if topic:
				self._database[forum_id].update({"_id":topic_id},{"$set":{"closed": not topic.get("closed",False)}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_make_topic_hidden(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)

			topic = self._database[forum_id].find_one({"_id":topic_id})
			if topic:
				self._database[forum_id + "_hide"].save(topic)
				self._database[forum_id].remove({"_id":topic_id})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
	
	def do_make_topic_unhidden(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)

			topic = self._database[forum_id + "_hide"].find_one({"_id":topic_id})
			if topic:
				self._database[forum_id].save(topic)
				self._database[forum_id + "_hide"].remove({"_id":topic_id})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		
	def do_make_topic_delete(self,category_id,forum_id,topic_id):
		
		try:
			if type(category_id) is not ObjectId:
				category_id = ObjectId(category_id)
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
			
			topic = self._database[forum_id].find_one({"_id":topic_id},fields=["creater_id"])
			if topic:
				user_id = ObjectId(topic["creater_id"])
				self._database["user"].update({"_id":user_id},{"$addToSet":{"topic_"+ forum_id : str(topic_id)}})
				self._database[forum_id].remove({"_id":topic_id})
				self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},{"$inc":{"forum.$.topics_num":-1}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_make_topic_move(self,old_category_id,old_forum_id,new_category_id,new_forum_id,topic_id):
		
		str_topic_id = str(topic_id)
		try:
			if type(old_category_id) is not ObjectId:
				old_category_id = ObjectId(old_category_id)
			if type(new_category_id) is not ObjectId:
				new_category_id = ObjectId(new_category_id)
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)	
			
			topic = self._database[old_forum_id].find_one({"_id":topic_id})
			if topic:
				user_id = ObjectId(topic["creater_id"])
				self._database[old_forum_id].remove({"_id":topic_id})
				self._database[new_forum_id].save(topic)
				self._database["user"].update({"_id":user_id},{"$addToSet":{"topic_" + old_forum_id:str_topic_id},"$addToSet":{"topic_" + new_forum_id:str_topic_id}})
				self._database["category_forum"].update({"_id":old_category_id,"forum._id":old_forum_id},{"$inc":{"forum.$.topics_num":-1}})
				self._database["category_forum"].update({"_id":new_category_id,"forum._id":new_forum_id},{"$inc":{"forum.$.topics_num":1}})
				return True
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
			
	def do_make_topic_highlight(self,forum_id,topic_id,highlight):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
		
			topic = self._database[forum_id].find_one({"_id":topic_id},fields=["high_light"])
			if topic and highlight in topic.get("high_light",[]):
				self._database[forum_id].update({"_id":topic_id},{"$pull":{"high_light":highlight}})
			else:
				self._database[forum_id].update({"_id":topic_id},{"$addToSet":{"high_light":highlight}})
			
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_check_xsrf_for_avatar_upload(self,user_id,xsrf_value):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
		except InvalidId,e:
			return False
		
		user = self._database["user"].find_one({"_id":user_id},fields=["xsrf"])

		if user and user.get("xsrf","") == xsrf_value:
			return True
		else:
			return False
			
	
	def do_show_current_avatar_name(self,user_id):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
		except InvalidId,e:
			return None
			
		return self._database["user"].find_one({"_id":user_id},fields=["avatar"])


	def do_change_avatar_name(self,user_id,avatar_ext):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
		
			self._database["user"].update({"_id":user_id},{"$set":{"avatar":avatar_ext}})
			return True
			
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
			
	def do_create_new_topic(self,category_id,forum_id,topic_obj):
		
		try:
			if type(category_id)is not ObjectId:
				category_id = ObjectId(category_id)
			user_id = topic_obj["creater_id"]
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
		
			topic_obj["posts"][0]["_id"] = str(ObjectId())
			topic_obj["posts"][0]["poster_id"] = user_id
			topic_id = self._database[forum_id].insert(topic_obj)
			self._database["user"].update({"_id":user_id},{"$addToSet":{"topic_" + forum_id:topic_id},"$inc":{"topics_num":1}})
			update = {
						"$inc":{"forum.$.topics_num":1},
						"$set":{
								"forum.$.last_post_time":topic_obj["create_time"],
								"forum.$.last_poster_id":topic_obj["creater_id"],
								"forum.$.last_poster_name":topic_obj["creater_name"],
								"forum.$.last_post_topic_id":str(topic_id),
								},
					}
			self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},update)
			return str(topic_id)
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_reply_topic(self,category_id,forum_id,topic_id,poster_name,reply_obj):
		
		str_topic_id = str(topic_id)
		
		try:
			if type(category_id)is not ObjectId:
				category_id = ObjectId(category_id)
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
			user_id = reply_obj["poster_id"]
			str_user_id = str(user_id)
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
				reply_obj["poster_id"] = user_id
				
			update = {
						"$inc":{"forum.$.replies_num":1},
						"$set":{
								"forum.$.last_post_time":reply_obj["post_time"],
								"forum.$.last_poster_id":str_user_id,
								"forum.$.last_poster_user":poster_name,
								"forum.$.last_post_topic_id":str_topic_id,
								},
					}
			self._database["category_forum"].update({"_id":category_id,"forum._id":forum_id},update)
			reply_obj["_id"] = str(ObjectId())
			update = {
						"$push":{"posts":reply_obj},
						"$inc":{"replies_num":1,"dist_level":1},
						"$set":{
								"last_poster_name":poster_name,
								"last_poster_id":str_user_id,
								"last_post_time":reply_obj["post_time"],
								},
					}
			self._database[forum_id].update({"_id":topic_id},update)
			self._database["user"].update({"_id":user_id},{"$addToSet":{"reply_" + forum_id:topic_id},"$inc":{"replies_num":1}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
	
	"""		
	def do_view_topic(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
		
			self._database[forum_id].update({"_id":topic_id},{"$inc":{"views_num":1}})
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
	"""	
	def do_edit_post(self,forum_id,topic_id,post_obj):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
			
			set_value = {
							"posts.$.content":post_obj["content"],
							"posts.$.editer_id":post_obj["editer_id"],
							"posts.$.editer_name":post_obj["editer_name"],
							"posts.$.edit_time":post_obj["edit_time"],
						}			
			update = {
						"$set":set_value,
					}
			
			self._database[forum_id].update({"_id":topic_id,"posts._id":post_obj["_id"]},update)	
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		
	def do_delete_post(self,forum_id,topic_id,post_obj):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
			
			set_value = {
							"posts.$.deleted":True,
							"posts.$.editer_id":post_obj["editer_id"],
							"posts.$.editer_name":post_obj["editer_name"],
							"posts.$.edit_time":post_obj["edit_time"],
						}
						
			update = {
						"$set":set_value,
					}
			
			self._database[forum_id].update({"_id":topic_id,"posts._id":post_obj["_id"]},update)	
			return True
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_check_already_reply(self,forum_id,topic_id,user_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
				
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			reply_field = "reply_" + forum_id
			topic_field = "topic_" + forum_id
			user = self._database["user"].find_one({"_id":user_id},fields=[reply_field,topic_field])
			
			reply_list = user.get(reply_field,[])
			if topic_id in reply_list:
				return True
				
			topic_list = user.get(topic_field,[])
			if topic_id in topic_list:
				return True

			return False
		
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_update_user_display(self,user_id,style):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id},{"$set":{"style":style}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_update_user_email(self,user_id,password,new_email):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id,"password":password},{"$set":{"email":new_email,"verify":False}})
			return True
				
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_user_email_with_username_password(self,username,password):
		
		try:
			user = self._database["user"].find_one({"name":username,"password":password},fields=["email"])
			if user:
				return user["email"]
			return None
				
		except OperationFailure as e:
			logging.exception(e)
			return None
		
	def do_active_user_account(self,username,password):
		
		try:
			self._database["user"].find_and_modify({"name":username,"password":password},{"$set":{"verify":True}})
			return True
			
		except OperationFailure as e:
			logging.exception(e)
			return Fasle
		
	def do_update_user_timezone(self,user_id,timezone):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id},{"$set":{"tz":timezone}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_user_id_with_username_email(self,username,email):
		
		try:
			user = self._database["user"].find_one({"name":username},fields=["email"])
			if user and email == user["email"]:
				return user["_id"]
			return None
				
		except OperationFailure as e:
			logging.exception(e)
			return None

	def do_reset_user_password(self,user_id,password):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id},{"$set":{"password":password}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
	
	def do_show_display_email_option(self,user_id):
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			user = self._database["user"].find_one({"_id":user_id},fields=["display_email"])
			if user and "display_email" in user:
				return user["display_email"]
			else:
				return False
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False
		

	def do_update_user_privacy(self,user_id,display_email):
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			
			self._database["user"].update({"_id":user_id},{"$set":{"display_email":display_email}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_user_topics(self,user_id,forum_id,current_page_no,items_num_per_page):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			field = "topic_" + forum_id
			begin = (current_page_no - 1) * items_num_per_page
			user = self._database["user"].find_one({"_id":user_id},fields={"_id":1,field:{"$slice": [begin, items_num_per_page]}})
			if user and field in user:
				topics_id = user[field]
				return list(self._database[forum_id].find({"_id":{"$in":topics_id}},fields={"posts":0}))
			else:
				return None
		except InvalidId:
			return None
		except OperationFailure as e:
			logging.exception(e)
			return None

	def do_show_user_replies(self,user_id,forum_id,current_page_no,items_num_per_page):
		
		try:
			if type(user_id)is not ObjectId:
				user_id = ObjectId(user_id)
			field = "reply_" + forum_id
			begin = (current_page_no - 1) * items_num_per_page
			user = self._database["user"].find_one({"_id":user_id},fields={"_id":1,field:{"$slice": [begin, items_num_per_page]}})

			if user and field in user:
				topics_id = user[field]
				return list(self._database[forum_id].find({"_id":{"$in":topics_id}},fields={"posts":0}))
			else:
				return None
		except InvalidId:
			return None
		except OperationFailure as e:
			logging.exception(e)
			return None

	def do_search_topic_name(self,forum_id,search_field):
		
		self._database[forum_id].ensure_index([("subject",ASCENDING)])
		return list(self._database[forum_id].find({"subject":{"$regex":r".*%s.*" % search_field}},fields={"posts":0}))
		
		
	def do_add_topic_views_num(self,forum_id,topic_id):
		
		try:
			if type(topic_id)is not ObjectId:
				topic_id = ObjectId(topic_id)
			
			self._database[forum_id].update({"_id":topic_id},{"$inc":{"views_num":1}})
			return True
		except InvalidId:
			return False
		except OperationFailure as e:
			logging.exception(e)
			return False

	def do_show_database_info(self):
		
		conn = self.__class__._db_conn
		
		db_info = {
					"host": conn.host,
					"port": conn.port,
					"nodes":conn.nodes,
					"read_preference":conn.read_preference,
					
				}
		
		return db_info

	def do_show_topics_replies_number(self):
		
		category_forum = list(self._database["category_forum"].find({},fields=["forum.topics_num","forum.replies_num"]))
		
		topics_num = 0
		replies_num = 0
		for category in category_forum:
			for forum in category.get("forum",[]):
				topics_num += forum.get("topics_num",0)
				replies_num += forum.get("replies_num",0)
				
		return topics_num,replies_num
				
		
