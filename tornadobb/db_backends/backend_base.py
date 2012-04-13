#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       backend_base.py
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



class backend_base(object):
	
		
	def __init__(self,db_param):
		pass
		
	def do_create_first_admin(self,admin_name,password,email,register_time):
		
		raise NotImplementedError
			
	def do_check_user_name(self,user_name):
		
		raise NotImplementedError
	
	def do_user_login(self,user_name,password,current_time,xsrf_value):

		raise NotImplementedError
	
	def do_set_user_access_log(self,user_id,current_time):
		
		raise NotImplementedError

	def do_user_logout(self,user_id):
		
		raise NotImplementedError

	def do_user_register(self,user):
		
		raise NotImplementedError

	def do_show_user_info(self,user_id):
		
		raise NotImplementedError
		
	def do_show_user_id_with_name(self,name):
		
		raise NotImplementedError
		
	def do_show_user_info_with_id(self,user_id):
		
		raise NotImplementedError
		
	def do_show_user_info_with_name(self,name):
		
		raise NotImplementedError
				
	def do_show_user_signature(self,user_id):
		
		raise NotImplementedError
		
	def do_save_user_signature(self,user_id,signature):
		
		raise NotImplementedError		
			
	def do_update_user_password(self,user_id,old_password,new_password):
		
		raise NotImplementedError		
	
	def do_show_newest_users(self,limit=20):
		
		raise NotImplementedError
		
	def do_show_online_users(self,expired_time,limit=50):
		
		raise NotImplementedError

	def do_create_guest_access_log(self,current_time):
		
		raise NotImplementedError

	def do_set_guest_access_log(self,guest_id,current_time):
		
		raise NotImplementedError
	
	def do_show_online_guests_num(self,expire_time):
		
		raise NotImplementedError
	
	def do_show_all_categories(self):
		
		raise NotImplementedError
	
	def do_show_all_categories_forums_for_homepage(self):
		
		raise NotImplementedError
		
	def do_show_all_categories_forums_name_and_id(self):
		
		raise NotImplementedError
		
	def do_only_show_all_categories_name_and_id(self):
		
		raise NotImplementedError
		
	def do_show_one_category(self,category_id):
		
		raise NotImplementedError
		
	def do_create_category(self,category):
		
		raise NotImplementedError
	
	def do_update_category(self,category_id,category_name,category_position):
		
		raise NotImplementedError
			
	def do_open_close_category(self,category_id,closed=False):
		
		raise NotImplementedError	

	def do_show_all_forums(self):
		
		raise NotImplementedError
		
	def do_show_one_forum(self,category_id,forum_id):
		
		raise NotImplementedError

	def do_create_forum(self,category_id,forum):
		
		raise NotImplementedError
			
	def do_update_forum(self,new_category_id,old_category_id,forum_id,forum_name,forum_position,forum_des):
		
		raise NotImplementedError
		
	def do_open_close_forum(self,category_id,forum_id,closed=False):
		
		raise NotImplementedError

	def do_show_all_moderators(self):
		
		raise NotImplementedError
			
	def do_create_moderator(self,category_id,forum_id,moderator_id,moderator_name,permission):

		raise NotImplementedError

	def do_update_moderator(self,forum_id,moderator_id,permission):
		
		raise NotImplementedError

	def do_delete_moderator(self,category_id,forum_id,moderator_id):

		raise NotImplementedError

	def do_show_moderator_permission(self,moderator_id,forum_id):
		
		raise NotImplementedError
	

	def do_open_close_user(self,user_id,closed=False):
		
		raise NotImplementedError

	def do_postable_dispostable_user(self,user_id,postable=False):
		
		raise NotImplementedError

	def do_show_forum_topics_and_num(self,category_id,forum_id):
		
		raise NotImplementedError
	
	
	def do_jump_to_first_page(self,forum_id,items_num_per_page,filter_view="all",order_by="post",dist_level=60):

		raise NotImplementedError
		
	def do_jump_to_lastest_page(self,forum_id,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
	
	def do_show_prev_page_topics(self,forum_id,begin,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
		
	def do_show_next_page_topics(self,forum_id,begin,items_num_per_page,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
		
	def do_jump_back_to_show_topics(self,forum_id,begin,items_num_per_page,current_page_no,jump_to_page_no,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
		
	def do_jump_forward_to_show_topics(self,forum_id,begin,items_num_per_page,current_page_no,jump_to_page_no,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
		
	def do_create_topic_pagination(self,forum_id,current_page_no,current_page_top,current_page_bottom,items_num_per_page,pages_num,topics_num,filter_view="all",order_by="post",dist_level=60):
		
		raise NotImplementedError
	
	def do_create_post_pagination(self,forum_id,topic_id,current_page_no,items_num_per_page,pages_num,total_items_num):
		
		raise NotImplementedError
		
	def do_create_user_topics_pagination(self,user_id,category_id,forum_id,current_page_no,items_num_per_page,pages_num,total_items_num):
		
		raise NotImplementedError
		
	def do_create_user_replies_pagination(self,user_id,category_id,forum_id,current_page_no,items_num_per_page,pages_num,total_items_num):
		
		raise NotImplementedError
		
	def do_show_topic_posts(self,forum_id,topic_id,current_page_no,items_num_per_page,expire_time):

		raise NotImplementedError

	def do_make_topic_sticky(self,forum_id,topic_id):
		
		raise NotImplementedError
		
	def do_make_topic_dist(self,forum_id,topic_id):
		
		raise NotImplementedError
		
	def do_make_topic_close(self,forum_id,topic_id):
		
		raise NotImplementedError

	def do_make_topic_hidden(self,forum_id,topic_id):
		
		raise NotImplementedError
		
	def do_make_topic_delete(self,category_id,forum_id,topic_id):
		
		raise NotImplementedError

	def do_make_topic_move(self,old_category_id,old_forum_id,new_category_id,new_forum_id,topic_id):
		
		raise NotImplementedError
			
	def do_make_topic_highlight(self,forum_id,topic_id,highlight):
		
		raise NotImplementedError

	def do_check_xsrf_for_avatar_upload(self,user_id,xsrf_value):
		
		raise NotImplementedError
			
	
	def do_show_current_avatar_name(self,user_id):
		
		raise NotImplementedError

	def do_change_avatar_name(self,user_id,avatar_ext):
		
		raise NotImplementedError
			
	def do_create_new_topic(self,category_id,forum_id,topic_obj):
		
		raise NotImplementedError

	def do_reply_topic(self,category_id,forum_id,topic_id,poster_name,reply_obj):
		
		raise NotImplementedError
			
	def do_view_topic(self,forum_id,topic_id):
		
		raise NotImplementedError
		
	def do_edit_post(self,forum_id,topic_id,post_obj):
		
		raise NotImplementedError
		
	def do_delete_post(self,forum_id,topic_id,post_obj):
		
		raise NotImplementedError

	def do_check_already_reply(self,forum_id,topic_id,user_id):
		
		raise NotImplementedError

	def do_update_user_display(self,user_id,style):
		
		raise NotImplementedError

	def do_update_user_email(self,user_id,password,new_email):
		
		raise NotImplementedError

	def do_show_user_email_with_username_password(self,username,password):
		
		raise NotImplementedError
		
	def do_active_user_account(self,username,password):
		
		raise NotImplementedError
		
	def do_update_user_timezone(self,user_id,timezone):
		
		raise NotImplementedError

	def do_show_user_id_with_username_email(self,username,email):
		
		raise NotImplementedError

	def do_reset_user_password(self,user_id,password):
		
		raise NotImplementedError
	
	def do_show_display_email_option(self,user_id):
		
		raise NotImplementedError
		

	def do_update_user_privacy(self,user_id,display_email):
		
		raise NotImplementedError

	def do_show_user_topics(self,user_id,forum_id,current_page_no,items_num_per_page):
		
		raise NotImplementedError

	def do_show_user_replies(self,user_id,forum_id,current_page_no,items_num_per_page):
		
		raise NotImplementedError

	def do_search_topic_name(self,forum_id,search_field):
		
		raise NotImplementedError
		
	def do_add_topic_views_num(self,forum_id,topic_id):
		
		raise NotImplementedError
