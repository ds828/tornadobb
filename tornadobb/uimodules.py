#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       uimodels.py
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
import time
import settings

class Title(tornado.web.UIModule):
    def render(self, category_id=None, forum_id=None, topic_name=None):
		
		category_forum = self.handler.settings["tornadobb.category_forum"]
		for category in category_forum:
			if category_id and category["_id"] == category_id:
				category_name = category["name"]
				for forum in category["forum"]:
					if forum_id and forum["_id"] == forum_id:
						forum_name = forum["name"]
						break

		return self.render_string("module_title.html", data = locals())

class Forum_Crumbs(tornado.web.UIModule):
	
    def render(self, topic_name = None):
		
		
		tornadobb_settings = self.handler.settings
		root_url = tornadobb_settings.get('tornadobb.root_url','/tornadobb')		
		rel_url = self.handler.request.path.partition(root_url)[2]
		id_list = rel_url.split('/')[2:-1]
		
		
		category_forum = tornadobb_settings['tornadobb.category_forum']
		# set a defualt forum name
		forum_name = category_forum[0]["forum"][0]["name"]
		for category in category_forum:
			if id_list[0] == category["_id"]:
				for forum in category["forum"]:
					if id_list[1] == forum["_id"]:
						forum_name = forum["name"]
						break

		query = None
		area = None
		filter_view = self.handler.get_argument("f",None)
		order_by = self.handler.get_argument("o",None)
		
		if order_by:
			order = "&o=" + order_by
		else:
			order = ""
		
		if filter_view == "dist":
			query = "/?f=dist" + order
			area = "Distillate"
		elif filter_view == "hide":
			query = "/?f=hide" + order
			area = "Hide"

		#for forum url
		forum_url = "/".join([root_url,"forum"] + id_list[0:2]) + "/"
		url_list = [forum_url]
		title_list = [forum_name]
		#for area url
		if area:
			url_list.append(forum_url + query)
			title_list.append(area)
			
		#for topic url
		if topic_name:
			topic_url = "/".join([root_url,"topic"] + id_list) + "/"
			url_list.append(topic_url)
			title_list.append(topic_name)
			
		print url_list
		print title_list
		return self.render_string("module_forum_crumbs.html", title_list = title_list,url_list = url_list)


class NewPost(tornado.web.UIModule):
    
    def render(self):
	
		root_url = self.handler.settings.get('tornadobb.root_url','/tornadobb')		
		rel_url = self.handler.request.path.partition(root_url)[2]
		id_list = rel_url.split('/')[2:-1]
		url = '/'.join([root_url,'forum',id_list[0],id_list[1]]) + '/new'
	
		return self.render_string("module_new_post.html", url = url)


class Categories_and_Forums(tornado.web.UIModule):
	 
	 def render(self):
		categories = settings.db_backend.do_show_all_categories_forums_for_homepage()
		return self.render_string("module_category_and_forum.html", categories = categories)
		
class Board_Info(tornado.web.UIModule):
	 
	 def render(self):

		newest_users,total_users = settings.db_backend.do_show_newest_users()
		expire_time = time.time() - self.handler.settings["tornadobb.session_expire"]
		online_users,total_online_users = settings.db_backend.do_show_online_users(expire_time)
		total_online_guests = settings.db_backend.do_show_online_guests_num(expire_time)
		 
		return self.render_string("module_board_info.html", data=locals())

class Pagination(tornado.web.UIModule):
	 
	 def render(self,pagination_obj,target="topic"):
		#pagination_pages_num = self.handler.settings["tornadobb.pagination_pages_num"]
		pagination_pages_num = 5
		pages_num = pagination_obj.get("pages_num")
		
		#quick for less than 9 cells
		if pages_num <= pagination_pages_num + 2:
			begin = 2
			end = pages_num
			print begin
			print end
			if target == "topic":
				return self.render_string("module_topic_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=False,show_next_space=False)
			elif target == "post":
				return self.render_string("module_post_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=False,show_next_space=False)
			else:
				return self.render_string("module_user_topic_post_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=False,show_next_space=False)

		begin = pagination_obj.get("current_page_num")
		
		if begin % pagination_pages_num == 0:
			begin = begin - pagination_pages_num + 1
		else:
			begin = begin/pagination_pages_num * pagination_pages_num + 1
			
		if begin == 1:
			begin = 2
			end = begin + pagination_pages_num + 1
		else:
			end = begin + pagination_pages_num
		
		if end > pages_num:
			end = pages_num
			
		if begin <= pagination_pages_num:
			show_prev_space = False
		else:
			show_prev_space = True
		
		if begin >= pages_num - pagination_pages_num - 1:
			show_next_space = False
		else:
			show_next_space = True
		
		if target == "topic":
			return self.render_string("module_topic_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=show_prev_space,show_next_space=show_next_space)
		elif target == "post":
			return self.render_string("module_post_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=show_prev_space,show_next_space=show_next_space)
		else:
			return self.render_string("module_user_topic_post_pagination.html", pagination_obj = pagination_obj,begin = begin,end = end,pagination_pages_num = pagination_pages_num,show_prev_space=show_prev_space,show_next_space=show_next_space)

class Topic_Detail_List(tornado.web.UIModule):
	 
	 def render(self,category_id,forum_id,topics):
		 
		return self.render_string("module_topic_detail_list.html", category_id = category_id,forum_id = forum_id, topics = topics)
	
class Post_Detail_List(tornado.web.UIModule):
	 
	 def render(self,topic,current_page_num,posts_num_per_page,permission,hide_content,hide_attach):
		 
		base_idx = (current_page_num - 1) * posts_num_per_page + 1
			
		return self.render_string("module_post_detail_list.html", topic = topic, hide_content = hide_content,hide_attach = hide_attach, base_idx = base_idx,permission = permission)
		
class Forum_Jumper(tornado.web.UIModule):
	
	 def render(self):
		return self.render_string("module_forum_jumper.html")
