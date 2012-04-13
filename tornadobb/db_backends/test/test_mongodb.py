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
import sys
sys.path.append("..")
from mongodb import *
import hashlib
import time


db_settings = {
        "host": "localhost",             # Set to localhost for localhost. Not used with sqlite3.
        "port": 27017,                   # Set to 27017 for mongodb default. Not used with sqlite3."
        "data_file":"db_tornadobb",		 # Set database file for mongodb
        "max_pool_size":10,				 # default connection pool size
}

db_conn = Connection(db_settings['host'], db_settings['port'],db_settings['max_pool_size'])
database = db_conn[db_settings["data_file"]]

db = mongodb(db_settings)

m = hashlib.md5()
m.update("123456")
passowrd = m.hexdigest().upper()

user = {
		'name' : "disong",
		'password': passowrd,
		'email' : "songdi19@gmail.com",
		'last_login':time.time(),
		"registered_time":time.time(),
		}
category_obj_1 = {"name":"Pictures","position":1,"des":"pic","closed":False}
category_obj_2 = {"name":"Video","position":1,"des":"video","closed":False}

forum_obj = {
			"name" : "Asian Girls",
			"position":1,
			"des":"asian",
			"closed":False,
			}
			
class TestMongodb(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):	
		
		print '-------------- setUpClass----------------------'
		collections = database.collection_names()
		print collections
		for collection in collections:
			if collection != "system.indexes":
				database[collection].drop()
	
	def get_category_id(self):
		
		return database["category_forum"].find({},{ "_id" : 1 })[0]["_id"]
		
	
	def test_user_register(self):
		
		result = db.do_user_register(user)
		self.assertEqual(result,True)
		
		result = db.do_user_register(None)
		self.assertEqual(result,False)
	
	def test_user_login(self):
		
		user_obj = db.do_user_login(user["name"],user["password"])
		self.assertNotEqual(user_obj,None)
		print user_obj
		
		user_obj = db.do_user_login(user["name"],"adfaeadsg")
		self.assertEqual(user_obj,None)
		
		user_obj = db.do_user_login(None,"adfaeadsg")
		self.assertEqual(user_obj,None)
		
		user_obj = db.do_user_login(None,None)
		self.assertEqual(user_obj,None)
	
	def test_create_category(self):
		
		result = db.do_create_category(category_obj_1)
		self.assertEqual(result,True)
		
		_id = self.get_category_id()
		
		added_category = database["category_forum"].find_one({"_id":_id})
		self.assertEqual(category_obj_1["name"],added_category["name"])
		self.assertEqual(category_obj_1["position"],added_category["position"])
		self.assertEqual(category_obj_1["des"],added_category["des"])
		
	
	def test_update_category(self):
		
		_id = self.get_category_id()
		
		category = {
					"_id" : _id,
					"name" : "new title",
					"des" : "new",
		}
		
		result = db.do_update_category(category)
		self.assertEqual(result,True)
		
		updated_category = database["category_forum"].find_one({"_id":_id})
		self.assertEqual(category["name"],updated_category["name"])
		self.assertEqual(category_obj_1["position"],updated_category["position"])
		self.assertEqual(category["des"],updated_category["des"])
		
	def test_open_close_category(self):
		
		_id = self.get_category_id()
		
		#close it
		result = db.do_open_close_category(_id,closed=True)
		self.assertEqual(result,True)
		closed_category = database["category_forum"].find_one({"_id":_id})
		self.assertEqual(closed_category["closed"],True)
		
		#open it
		result = db.do_open_close_category(_id,closed=False)
		self.assertEqual(result,True)
		closed_category = database["category_forum"].find_one({"_id":_id})
		self.assertEqual(closed_category["closed"],False)
	
	def test_do_update_position_category(self):
		
		self.setUpClass()
		#add 3 categories
		category_1 = {"name":"category_1","position":1,"des":"pic"}
		category_2 = {"name":"category_2","position":2,"des":"pic"}
		category_3 = {"name":"category_3","position":3,"des":"pic"}
		db.do_create_category(category_1)
		db.do_create_category(category_2)
		db.do_create_category(category_3)
		
		#new positioins
		positions = [3,2,1]
		
		db.do_update_position_category(positions)
		
		new_category_1 = database["category_forum"].find_one({"name":category_1["name"]})
		self.assertEqual(new_category_1["position"],positions[0])
		
		new_category_2 = database["category_forum"].find_one({"name":category_2["name"]})
		self.assertEqual(new_category_2["position"],positions[1])
		
		new_category_3 = database["category_forum"].find_one({"name":category_3["name"]})
		self.assertEqual(new_category_3["position"],positions[2])
				 
	def test_create_forum(self):
				
		db.do_create_category(category_obj_1)
		db.do_create_category(category_obj_2)
		
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		result = db.do_create_forum(str(category_1_id),forum_obj)
		self.assertEqual(result,True)
		print database["category_forum"].find_one({"_id":category_1_id})
		
		
	def test_update_forum(self):
		
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		
		category_2 = database["category_forum"].find_one({"name":category_obj_2["name"]})
		category_2_id = category_2["_id"]
		
		forum = {
					"_id":category_1["forum"][0]["_id"],
					"name":"new forum name",
					"des":"new forum des",
		}
		
		result = db.do_update_forum(str(category_1_id),str(category_1_id),forum["_id"],forum["name"],forum["des"])
		result_set = database["category_forum"].find_one({"_id":category_1_id})
		print "------------------------ update in one category---------------------------"
		print result_set
		self.assertNotEqual(result_set,None)
		self.assertEqual(result_set["forum"][0]["name"],forum["name"])
		
		result = db.do_update_forum(str(category_2_id),str(category_1_id),forum["_id"],forum["name"],forum["des"])
		
		result_set = database["category_forum"].find_one({"_id":category_2_id})
		print "------------------------ update in 2 category---------------------------"
		print result_set
		
		self.assertNotEqual(result_set,None)
		self.assertEqual(result_set["forum"][0]["name"],forum["name"])
		
		
		result_set = database["category_forum"].find_one({"_id":category_1_id})
		print result_set
		self.assertEqual(result_set["forum"],[])
		
	def test_open_close_forum(self):
		category_2 = database["category_forum"].find_one({"name":category_obj_2["name"]})
		category_2_id = category_2["_id"]
		forum_id = category_2["forum"][0]["_id"]
		
		result = db.do_open_close_forum(str(category_2_id),str(forum_id),True) #close it
		
		result_set = database["category_forum"].find_one({"_id":category_2_id})
		self.assertNotEqual(result_set,None)
		self.assertEqual(result_set["forum"][0]["closed"],True)
		
		result = db.do_open_close_forum(str(category_2_id),str(forum_id),False) #open it
		
		result_set = database["category_forum"].find_one({"_id":category_2_id})
		self.assertNotEqual(result_set,None)
		self.assertEqual(result_set["forum"][0]["closed"],False)
		
	def test_update_position_forum(self):
		
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		#add 3 forum
		forum_1 = {"name":"forum_1","position":1,"des":"f1"}
		forum_2 = {"name":"forum_2","position":2,"des":"f2"}
		forum_3 = {"name":"forum_3","position":3,"des":"f3"}
		db.do_create_forum(category_1_id,forum_1)
		db.do_create_forum(category_1_id,forum_2)
		db.do_create_forum(category_1_id,forum_3)
		
		#new positioins
		positions = [30,20,10]
		
		db.do_update_position_forum(category_1_id,positions)
		
		category = database["category_forum"].find_one({"_id":category_1_id})
		print category
		self.assertEqual(category["forum"][0]["position"],positions[0])
		self.assertEqual(category["forum"][1]["position"],positions[1])
		self.assertEqual(category["forum"][2]["position"],positions[2])
	
	def test_create_moderator(self):
		
		#add one user
		db.do_user_register(user)
		
		user_1 = database["user"].find_one({"name":user["name"]})
		user_id = user_1["_id"]
		user_name = user["name"]
		#add one category
		db.do_create_category(category_obj_1)
		#add one forum
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		db.do_create_forum(str(category_1_id),forum_obj)
		category = database["category_forum"].find_one({"name":category_obj_1["name"]})
		forum_id = category["forum"][0]["_id"]
		
		permissions = ["sticky","distillate","hide_topic","delete_topic","move_topic","delete_post","edit_post","highlight"]
		
		result = db.do_create_moderator(category_1_id,forum_id,user_id,user_name,permissions)
		self.assertEqual(result,True)
		
		time.sleep(2)
		
		category = database["category_forum"].find_one({"name":category_obj_1["name"]})
		print category
		self.assertEqual( user_id,category["forum"][0]["moderator"][0]["_id"])

		user_1 = database["user"].find_one({"name":user["name"]})
		print user_1
		self.assertEqual("moderator",user_1["role"])
		self.assertEqual(permissions,user_1["perm_"+str(forum_id)])
		
	def test_update_moderator(self):
		
		user_1 = database["user"].find_one({"name":user["name"]})
		user_id = user_1["_id"]
		user_name = user["name"]
		
		category = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_id = category["_id"]
		forum_id = category["forum"][0]["_id"]
		
		new_permissions = ["sticky","distillate"]
		
		#same category and forum
		result = db.do_update_moderator(category_id,forum_id,category_id,forum_id,user_id,user_name,new_permissions)
		self.assertEqual(result,True)
		
		category = database["category_forum"].find_one({"name":category["name"]})
		print "------------------------ same forum -------------------------------"
		print category
		self.assertEqual( user_id,category["forum"][0]["moderator"][0]["_id"])
		user_1 = database["user"].find_one({"name":user["name"]})
		print user_1
		self.assertEqual("moderator",user_1["role"])
		self.assertEqual(new_permissions,user_1["perm_"+str(forum_id)])
		
		
		#deferent forum
		#add one forum
		db.do_create_forum(str(category_id),forum_obj)
		category = database["category_forum"].find_one({"name":category_obj_1["name"]})
		forum_2_id = category["forum"][1]["_id"]
				
		result = db.do_update_moderator(category_id,forum_id,category_id,forum_2_id,user_id,user_name,new_permissions)
		self.assertEqual(result,True)
		
		category = database["category_forum"].find_one({"name":category["name"]})
		print "------------------------ diffierent forum -------------------------------"
		print category
		
		for forum in category["forum"]:
			if forum["_id"] == forum_id:
				for moderator in forum["moderator"]:
					self.assertNotEqual(user_id, moderator["_id"])
			if forum["_id"] == forum_2_id:
				self.assertEqual(forum["moderator"][0]["_id"],user_id)
				
		user_1 = database["user"].find_one({"name":user["name"]})
		print user_1
		self.assertEqual("moderator",user_1["role"])
		self.assertEqual(new_permissions,user_1["perm_" + str(forum_2_id)])
			
	def test_delete_moderator(self):
		
		user_1 = database["user"].find_one({"name":user["name"]})
		user_id = user_1["_id"]
		
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		forum_id = category_1["forum"][1]["_id"]
		
		result = db.do_delete_moderator(category_1_id,forum_id,user_id)
		self.assertEqual(result,True)
		
		category = database["category_forum"].find_one({"name":category_obj_1["name"]})
		
		for forum in category["forum"]:
			if forum["_id"] == forum_id:
				for moderator in forum["moderator"]:
					self.assertNotEqual(user_id, moderator["_id"])
				
		user_1 = database["user"].find_one({"name":user["name"]})
		self.assertEqual("role" not in user_1,True)
		
		print user_1
		
	def test_open_close_user(self):
		#add one user
		db.do_user_register(user)
		user_1 = database["user"].find_one({"name":user["name"]})
		user_id = user_1["_id"]
		
		regex_user =  db.do_show_user_info_with_name("dis")
		print regex_user
		self.assertNotEqual(regex_user,[])
		
		result = db.do_open_close_user(user_id,True)
		self.assertEqual(result,True)
		user_1 = database["user"].find_one({"name":user["name"]})
		self.assertEqual(user_1["closed"],True)
		
		result = db.do_open_close_user(user_id,False)
		self.assertEqual(result,True)
		user_1 = database["user"].find_one({"name":user["name"]})
		self.assertEqual(user_1["closed"],False)
		
	def test_postable_dispostable_user(self):
		
		user_1 = database["user"].find_one({"name":user["name"]})
		user_id = user_1["_id"]
		
		result = db.do_postable_dispostable_user(user_id,True)
		self.assertEqual(result,True)
		user_1 = database["user"].find_one({"name":user["name"]})
		self.assertEqual(user_1["postable"],True)
		
		result = db.do_postable_dispostable_user(user_id,False)
		self.assertEqual(result,True)
		user_1 = database["user"].find_one({"name":user["name"]})
		self.assertEqual(user_1["postable"],False)
	
	def test_init_evn(self):
		
		#add 1 category
		db.do_create_category(category_obj_1)
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		#add 3 forum
		forum_1 = {"name":"forum_1","position":1,"des":"f1","closed":False,}
		forum_2 = {"name":"forum_2","position":2,"des":"f2","closed":False,}
		forum_3 = {"name":"forum_3","position":3,"des":"f3","closed":False,}
		db.do_create_forum(category_1_id,forum_1)
		db.do_create_forum(category_1_id,forum_2)
		db.do_create_forum(category_1_id,forum_3)
		
		forum_id_list = database["category_forum"].find_one({"_id":category_1_id},fields=["forum._id"])
		#print forum_id_list
		forum_id_1 = forum_id_list["forum"][0]["_id"]
		forum_id_2 = forum_id_list["forum"][1]["_id"]
		forum_id_3 = forum_id_list["forum"][2]["_id"]
		
		#add 3 user
		user_1_id = db.do_user_register(user)
		
		user2 = {
		'name' : "songdi",
		'password': passowrd,
		'email' : "songdi19@gmail.com",
		'last_login':time.time(),
		}
		user3 = {
		'name' : "songdidi",
		'password': passowrd,
		'email' : "songdi19@gmail.com",
		'online': True,
		'last_login':time.time(),
		}
		user_2_id = db.do_user_register(user2)
		user_3_id = db.do_user_register(user3)
		"""
		#add 4 topics
		
		topic_1 = {
				"subject":"Hello tornado BBS",
				"topic_type":"text",
				"high_light":["red"],
				"sticky":False,
				"closed":False,
				"hidden":False,
				"distillate":False,
				"created_on":time.time(),
				"created_by":"disong",
				"last_post_time":time.time(),
				"last_posted_by":"disong",
			}
		topic_2 = {
				"subject":"Manual of Torndobb",
				"topic_type":"text",
				"high_light":["red"],
				"sticky":False,
				"closed":False,
				"hidden":False,
				"distillate":False,
				"created_on":time.time()+10,
				"created_by":"disong",
				"last_post_time":time.time()+10,
				"last_posted_by":"disong",
			}
		topic_3 = {
				"subject":"This is the first topic",
				"topic_type":"text",
				"high_light":["red"],
				"sticky":False,
				"closed":False,
				"hidden":False,
				"distillate":False,
				"created_on":time.time()+20,
				"created_by":"disong",
				"last_post_time":time.time()+20,
				"last_posted_by":"disong",
			}
		
		topic_4 = {
				"subject":"How to use this bbs?",
				"topic_type":"text",
				"high_light":["red"],
				"sticky":False,
				"closed":False,
				"hidden":False,
				"distillate":False,
				"created_on":time.time()+30,
				"created_by":"disong",
				"last_post_time":time.time()+30,
				"last_posted_by":"disong",
			}
		"""	
		#db.do_post_topic(category_1_id,forum_id_1,topic_1)
		#db.do_post_topic(category_1_id,forum_id_1,topic_2)
		#db.do_post_topic(category_1_id,forum_id_1,topic_3)
		#db.do_post_topic(category_1_id,forum_id_1,topic_4)
		

		#add 10 topics again
		
		topic_names = [
						"topic_0",
						"topic_1",
						
						"topic_2",
						"topic_3",
						
						"topic_4",
						"topic_5",
						
						"topic_6",
						"topic_7",
						
						"topic_8",
						"topic_9",
						
						"topic_10",
						"topic_11",
						
						"topic_12",
						"topic_13",
						
						"topic_14",
						"topic_15",
						
						"topic_16",
						"topic_17",
						
						"topic_18",
						"topic_19",
					]
		
		
		for i,topic_name in enumerate(topic_names):
			now = time.time() + i*10
			post_sample = {
					"poster_id":user_1_id,
					"post_time":now,
					#"editer_id":str(user_1_id),
					#"editer_name":"disong",
					#"edite_time":time.time(),
					"content":"[b]This is post content[/b][code]<a href=''>bbb</a>[/code] [topic]1[/topic] [img]/tornadobb/static/images/emoticon/emoticon-happy.png[/img]",
				}	
			topic_obj = {
				"topic_type":"text",
				"high_light":["red"],
				"sticky":False,
				"closed":False,
				"hidden":False,
				"dist":False,
				"dist_level":0,
				"creater_id":str(user_1_id),
				"creater_name":"disong",
				"last_poster_id":str(user_1_id),
				"last_poster_name":"disong",
				"posts" : [post_sample]
				}
			topic_obj["subject"] = topic_name
			now = time.time() + i*10
			topic_obj["create_time"] = now
			topic_obj["last_post_time"] = now
			#add one topic
			topic_id = db.do_create_new_topic(category_1_id,forum_id_1,topic_obj)
			
			# add 40 reply
			for i in xrange(0,40):
				post_sample = {
					"poster_id":user_1_id,
					"post_time":time.time() + i*100,
					#"editer_id":str(user_1_id),
					#"editer_name":"disong",
					#"edite_time":time.time(),
					"content":"[b]This is post content[/b][code]<a href=''>bbb</a>[/code] [topic]1[/topic] [img]/tornadobb/static/images/emoticon/emoticon-happy.png[/img]",
				}
				db.do_reply_topic(category_1_id,forum_id_1,topic_id,"disong",post_sample)
									
			print '-------------- add topic finish -------------------'
	
		print list(database[str(forum_id_1)].find())		
		
		for topic in database[str(forum_id_1)].find():
			print "%s   %f" % (topic["subject"],topic["last_post_time"])
			
		items_num_pre_page = 2
		begin = time.time()+2000
		#go to next page
		topics = list(database[str(forum_id_1)].find({"last_post_time":{"$lt":begin}},sort=[("sticky",-1),("last_post_time",-1)],fields={"posts":0},limit=items_num_pre_page))
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[9])
		self.assertEqual(topics[1]["subject"],topic_names[8])
		begin = topics[1]["last_post_time"]
		
		topics = list(database[str(forum_id_1)].find({"last_post_time":{"$lt":begin}},sort=[("sticky",-1),("last_post_time",-1)],fields={"posts":0},limit=items_num_pre_page))
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[7])
		self.assertEqual(topics[1]["subject"],topic_names[6])
		begin = topics[1]["last_post_time"]
		
		topics = list(database[str(forum_id_1)].find({"last_post_time":{"$lt":begin}},sort=[("sticky",-1),("last_post_time",-1)],fields={"posts":0},limit=items_num_pre_page))
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[5])
		self.assertEqual(topics[1]["subject"],topic_names[4])
		begin = topics[1]["last_post_time"]
		
		top_begin = topics[0]["last_post_time"]
		
		print top_begin
		#go back to perv page
		topics =list(database[str(forum_id_1)].find({"last_post_time":{"$gt":top_begin}},sort=[("sticky",-1),("last_post_time",1)],fields={"posts":0},limit=items_num_pre_page))
		print topics
		topics.reverse()
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[7])
		self.assertEqual(topics[1]["subject"],topic_names[6])
		
		top_begin = topics[0]["last_post_time"]
		
		print top_begin		
		#go back to first page
		topics = list(reversed(list(database[str(forum_id_1)].find({"last_post_time":{"$gt":top_begin}},sort=[("sticky",-1),("last_post_time",1)],fields={"posts":0},limit=items_num_pre_page))))
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[9])
		self.assertEqual(topics[1]["subject"],topic_names[8])
		
		begin = topics[1]["last_post_time"]
		#jump to last page
		
		topics = list(database[str(forum_id_1)].find({"last_post_time":{"$lt":begin}},sort=[("sticky",-1),("last_post_time",-1)],fields={"posts":0}).skip(3 * items_num_pre_page).limit(items_num_pre_page))
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[1])
		self.assertEqual(topics[1]["subject"],topic_names[0])
		
		#jump back to 2 pages
		
		top_begin = topics[0]["last_post_time"]
		
		print top_begin		

		topics = list(database[str(forum_id_1)].find({"last_post_time":{"$gt":top_begin}},sort=[("sticky",-1),("last_post_time",1)],fields={"posts":0}).skip(1 * items_num_pre_page).limit(items_num_pre_page))
		print topics
		print topics.reverse()
		print topics
		self.assertEqual(len(topics),items_num_pre_page)
		self.assertEqual(topics[0]["subject"],topic_names[5])
		self.assertEqual(topics[1]["subject"],topic_names[4])
		
		
		topics = list(database[str(forum_id_1)].find({"$or" : [ { "dist":True } , { "dist_level" : { "$gt" : 20}}]},sort=[("sticky",-1),("last_post_time",1)],fields={"posts":0}))
		print topics
		
		#select out a sub set of posts in one topic
		
		#topic = database[str(forum_id_1)].find_one({"subject":"topic_0","$and" : [  { "posts._id" : { "$gt" : 20}} , { "posts._id" : { "$lt" : 30}}]},fields=["posts"])
		topic = database[str(forum_id_1)].find_one({"subject":"topic_0"},fields = {"posts":{"$slice": [20, 10]}})
		print topic
		print len(topic["posts"])

	def test_topic_management(self):
		
		#add 1 category
		db.do_create_category(category_obj_1)
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		#add 2 forum
		forum_1 = {"name":"forum_1","position":1,"des":"f1"}
		forum_2 = {"name":"forum_2","position":2,"des":"f2"}
		db.do_create_forum(category_1_id,forum_1)
		db.do_create_forum(category_1_id,forum_2)
		
		time.sleep(2)
		
		forum_id_list = database["category_forum"].find_one({"_id":category_1_id},fields=["forum._id"])
		#print forum_id_list
		forum_id_1 = forum_id_list["forum"][0]["_id"]
		forum_id_2 = forum_id_list["forum"][1]["_id"]
		
		#add 1 user
		user_id = db.do_user_register(user)
		
		#add 1 topic	
		topic_1 = {
				"subject":"Hello tornado BBS",
				"create_time":now,
				"creater_id":str(user_id),
				"creater_name":"disong",
				"last_post_time":now,
				"last_poster_id":str(user_id),
				"last_poster_name":"disong",
			}
			
		topic_id = db.do_post_topic(category_1_id,forum_id_1,topic_1)
		
		category = database["category_forum"].find_one({"_id":category_1_id,"forum._id":forum_id_1},fields=["forum._id","forum.topics_num"])
		print category	
		for forum in category["forum"]:
			if forum_id_1 == forum["_id"]:
				self.assertEqual(forum["topics_num"],1)
				break
		
		user2 = database["user"].find_one({"_id":user_id},fields=["topic_" + str(forum_id_1)])
		
		print user2
		self.assertEqual(topic_id in user2["topic_" + str(forum_id_1)],True)
				
		#test_make_topic_sticky
		db.do_make_topic_sticky(forum_id_1,topic_id,True)
		#test_make_topic_close
		db.do_make_topic_close(forum_id_1,topic_id,True)
		#test_make_topic_distillate
		db.do_make_topic_distillate(forum_id_1,topic_id,True)
		#test_make_topic_hidden
		db.do_make_topic_hidden(forum_id_1,topic_id,True)
		#test_make_topic_highlight
		db.do_make_topic_highlight(forum_id_1,topic_id,"red")
		
		time.sleep(2)
		
		topic = database[str(forum_id_1)].find_one({"_id":topic_id},fields=["sticky","closed","distillate","hidden","high_light"])
		
		self.assertEqual(topic["sticky"],True)
		self.assertEqual(topic["closed"],True)
		self.assertEqual(topic["distillate"],True)
		self.assertEqual(topic["hidden"],True)
		self.assertEqual("red" in topic["high_light"],True)
		
		#test_make_topic_move
		db.do_make_topic_move(category_1_id,forum_id_1,category_1_id,forum_id_2,topic_id)
		
		time.sleep(2)
		
		topic_should_be_none = database[str(forum_id_1)].find_one({"_id":topic_id})
		self.assertEqual(topic_should_be_none,None)
		
		topic_should_be = database[str(forum_id_2)].find_one({"_id":topic_id})
		self.assertNotEqual(topic_should_be,None)
		self.assertEqual(topic_should_be["subject"],topic_1["subject"])
		
		user3 = database["user"].find_one({"_id":user_id})
		print user3
		self.assertEqual(topic_id not in user3["topic_" + str(forum_id_1)],True)
		self.assertEqual(topic_id  in user3["topic_" + str(forum_id_2)],True)
		
		#test_make_topic_delete
		db.do_make_topic_delete(category_1_id,forum_id_2,topic_id)
		
		time.sleep(2)
		
		user4 = database["user"].find_one({"_id":user_id})
		self.assertEqual(topic_id not in user4["topic_" + str(forum_id_2)],True)
		
		category = database["category_forum"].find_one({"_id":category_1_id,"forum._id":forum_id_2},fields=["forum._id","forum.topics_num"])
		print category	
		for forum in category["forum"]:
			if forum_id_2 == forum["_id"]:
				self.assertEqual(forum["topics_num"],0)
				break
		
		topic_should_be_None = database[str(forum_id_2)].find_one({"_id":topic_id})
		self.assertEqual(topic_should_be_None,None)

	def test_post_topic(self):
		
		#add 1 category
		db.do_create_category(category_obj_1)
		category_1 = database["category_forum"].find_one({"name":category_obj_1["name"]})
		category_1_id = category_1["_id"]
		#add 1 forum
		forum_1 = {"name":"forum_1","position":1,"des":"f1"}
		db.do_create_forum(category_1_id,forum_1)
		
		time.sleep(2)
		
		forum_id_list = database["category_forum"].find_one({"_id":category_1_id},fields=["forum._id"])
		#print forum_id_list
		forum_id_1 = forum_id_list["forum"][0]["_id"]
		
		#add 1 user
		user_id = db.do_user_register(user)
		
		now = time.time()
		#add 1 topic	
		topic_1 = {
				"subject":"Hello tornado BBS",
				"create_time":now,
				"creater_id":str(user_id),
				"creater_name":"disong",
				"last_post_time":now,
				"last_poster_id":str(user_id),
				"last_poster_name":"disong",
			}
		
		#add one post
		post_sample = {
				"poster_id":user_id,
				"post_time":now,
				#"editer_id":str(user_1_id),
				#"editer_name":"disong",
				#"edited_on":time.time(),
				"content":"[b]This is post content[/b][code]<a href=''>bbb</a>[/code] [topic]1[/topic] [img]/forum/static/images/emoticon/emoticon-happy.png[/img]",
				}
				
		topic_1["posts"] = [post_sample]
		
		#test create new post
		topic_id = db.do_create_new_topic(category_1_id,forum_id_1,topic_1)
		
		category = database["category_forum"].find_one({"_id":category_1_id,"forum._id":str(forum_id_1)})
		self.assertEqual(category["forum"][0]["topics_num"],1)
		self.assertEqual(category["forum"][0]["last_post_time"],now)
		self.assertEqual(category["forum"][0]["last_poster_name"],user["name"])
		self.assertEqual(category["forum"][0]["last_poster_id"],str(user_id))
		
		topic = database[str(forum_id_1)].find_one({"_id":topic_id})
		self.assertNotEqual(topic,None)
		self.assertEqual(topic["subject"],topic_1["subject"])
		
		user2 = database["user"].find_one({"_id":user_id})
		self.assertNotEqual(user2,None)
		self.assertEqual(topic_id in user2["topic_"+str(forum_id_1)],True)
			
		#test view post
		db.do_view_topic(forum_id_1,topic_id)
		topic = database[str(forum_id_1)].find_one({"_id":topic_id})
		self.assertNotEqual(topic,None)
		self.assertEqual(topic["views_num"],1)
			
		#test reply post
		now2 = time.time()
		post_sample2 = {
						"poster_id":user_id,
						"post_time":now2,
						#"editer_id":str(user_1_id),
						#"editer_name":"disong",
						#"edited_on":time.time(),
						"content":"reply it",
						}
		db.do_reply_topic(category_1_id,forum_id_1,topic_id,user["name"],post_sample2)
		
		category = database["category_forum"].find_one({"_id":category_1_id,"forum._id":str(forum_id_1)})
		self.assertEqual(category["forum"][0]["replies_num"],1)
		self.assertEqual(category["forum"][0]["last_post_time"],now2)
		self.assertEqual(category["forum"][0]["last_poster_name"],user["name"])
		self.assertEqual(category["forum"][0]["last_poster_id"],str(user_id))
		
		topic = database[str(forum_id_1)].find_one({"_id":topic_id})
		self.assertNotEqual(topic,None)
		self.assertEqual(len(topic["posts"]),2)
		self.assertEqual(topic["posts"][1]["content"],post_sample2["content"])
		self.assertEqual(topic["posts"][1]["post_time"],now2)
		self.assertEqual(topic["replies_num"],1)
		self.assertEqual(topic["dist_level"],1)
		
		user2 = database["user"].find_one({"_id":user_id})
		self.assertNotEqual(user2,None)
		self.assertEqual(topic_id in user2["reply_"+str(forum_id_1)],True)
		
		#test edit post
		
		topic = database[str(forum_id_1)].find_one({"_id":topic_id})
		#will edit this one
		post_id = topic["posts"][1]["_id"]
		
		now3 = time.time()
		post_sample3 = {
				"_id" : post_id,
				"editer_id":str(user_id),
				"editer_name":"disong",
				"edit_time":now3,
				"content":"edit this content",
				}
		db.do_edit_post(forum_id_1,topic_id,post_sample3)
		topic = database[str(forum_id_1)].find_one({"_id":topic_id})
		self.assertEqual(topic["posts"][1]["editer_id"],post_sample3["editer_id"])
		self.assertEqual(topic["posts"][1]["editer_name"],post_sample3["editer_name"])
		self.assertEqual(topic["posts"][1]["edit_time"],post_sample3["edit_time"])
		
		
		
def suite():
	tests_user = [
				"test_user_register",
				"test_user_login",
				]
	tests_category = [
				"test_create_category",
				"test_update_category",
				"test_open_close_category",
				"test_do_update_position_category",
			]
	tests_forum = [
				"test_create_forum",
				"test_update_forum",
				"test_open_close_forum",
				"test_update_position_forum",
			]
	tests_moderator = [
				"test_create_moderator",
				"test_update_moderator",
				"test_delete_moderator",
		]
	tests_member = [
				"test_open_close_user",
				"test_postable_dispostable_user",
	
		]
	
	tests_evn = [
				"test_init_evn",
		]
	
	tests_topic_management = [
				"test_topic_management",
	
		]
	
	tests_post_topic = [
				"test_post_topic",
		]
	
	#return unittest.TestSuite(map(TestMongodb, tests_user))
	#return unittest.TestSuite(map(TestMongodb, tests_category))
	return unittest.TestSuite(map(TestMongodb, tests_forum))
	#return unittest.TestSuite(map(TestMongodb, tests_moderator))
	#return unittest.TestSuite(map(TestMongodb, tests_member))
	#return unittest.TestSuite(map(TestMongodb, tests_evn))
	#return unittest.TestSuite(map(TestMongodb, tests_topic_management))
	#return unittest.TestSuite(map(TestMongodb, tests_post_topic))
	
	
if __name__ == '__main__':

	TestMongodb.setUpClass()
	unittest.TextTestRunner(verbosity=2).run(suite())
