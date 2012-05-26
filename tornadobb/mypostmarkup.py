#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
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

from urlparse import urlparse
from postmarkup import *
import settings
__all__ = ["render_bbcode"]

pygments_available = True
try:
	from pygments import highlight
	from pygments.lexers import get_lexer_by_name, ClassNotFound
	from pygments.formatters import HtmlFormatter
except ImportError:
	# Make Pygments optional
	pygments_available = False
	
class MyVideoTag(TagBase):
	
	def __init__(self, name, **kwargs):
		super(MyVideoTag, self).__init__(name, strip_first_newline=True)
	
	def render_open(self, parser, node_index):

		contents = self.get_contents(parser)
		self.skip_contents(parser)
		if self.params:
			url = self.params.strip()
		else:
			url = strip_bbcode(contents)
		if not url:
			return u''
		scheme, netloc, path, params, query, fragment = urlparse(url)
		if not scheme:
			url = u'http://' + url
			scheme, netloc, path, params, query, fragment = urlparse(url)
		if scheme.lower() not in (u'http', u'https', u'ftp'):
			return u''
		url = PostMarkup.standard_replace_no_break(url)	
		#return u'<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="600" height="450"><param name="allowScriptAccess" value="sameDomain"><param name="movie" value="%s"><param name="quality" value="high"><param name="bgcolor" value="#ffffff"><embed src="%s" quality="high" bgcolor="#ffffff" width="600" height="450" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /></object>' % (url,url)
		return u'<object width="600" height="450"><param name="movie" value="%s"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="%s" type="application/x-shockwave-flash" width="600" height="450" allowscriptaccess="always" allowfullscreen="true"></embed></object>' % (url,url)
		
class MyQuoteTag(TagBase):
	
	def __init__(self, name, **kwargs):
		super(MyQuoteTag, self).__init__(name, strip_first_newline=True)
	
	def render_open(self, parser, node_index):
		if self.params:
			return u'<div class="quotebox"><cite>%s:</cite><blockquote><p>' % (PostMarkup.standard_replace(self.params))
		else:
			return u'<div class="quotebox"><cite></cite><blockquote><p>'
	
	def render_close(self, parser, node_index):
		return u"</p></blockquote></div>"

class EmoticonTag(TagBase):
	
	def __init__(self, name, **kwargs):
		super(EmoticonTag, self).__init__( name, inline=True)
	
	def open(self, parser, params, *args):
		if params.strip():
			self.auto_close = True
		super(EmoticonTag, self).open(parser, params, *args)
	
	def render_open(self, parser, node_index):
		contents = self.get_contents(parser)
		self.skip_contents(parser)
		# Validate url to avoid any XSS attacks
		if self.params:
			url = self.params.strip()
		else:
			url = strip_bbcode(contents)
		url = url.replace(u'"', u"%22").strip()
		emoticon_url = settings.tornadobb_settings["tornadobb.emoticon_settings"].get(url,"")
		return u'<img src="%s"></img>' % PostMarkup.standard_replace_no_break(emoticon_url)


class MyImgTag(ImgTag):

    def __init__(self, name, **kwargs):
        super(MyImgTag, self).__init__( name, inline=True)
        

    def render_open(self, parser, node_index):

        contents = self.get_contents(parser)
        self.skip_contents(parser)

        # Validate url to avoid any XSS attacks
        if self.params:
            url = self.params.strip()
        else:
            url = strip_bbcode(contents)
            
        url = url.replace(u'"', u"%22").strip()
        if not url:
            return u''
        scheme, netloc, path, params, query, fragment = urlparse(url)
        if not scheme:
            url = u'http://' + url
            scheme, netloc, path, params, query, fragment = urlparse(url)
        if scheme.lower() not in (u'http', u'https', u'ftp'):
            return u''
        
        img_url = PostMarkup.standard_replace_no_break(url)

        return u'<a href="%s" target="_blank"><img src="%s" onload="scale_image(this)"></img></a>' % (img_url,img_url)

class MyLinkTag(LinkTag):
	
    def __init__(self, name, **kwargs):
        super(MyLinkTag, self).__init__( name, inline=True)
        
    def render_open(self, parser, node_index):

        self.domain = u''
        tag_data = parser.tag_data
        nest_level = tag_data[u'link_nest_level'] = tag_data.setdefault(u'link_nest_level', 0) + 1

        if nest_level > 1:
            return u""

        if self.params:
            url = self.params.strip()
        else:
            url = self.get_contents_text(parser).strip()
            url = PostMarkup.standard_unreplace(url)

        self.domain = u""

        if u':' not in url:
            url = u'http://' + url

        scheme, uri = url.split(u':', 1)

        if scheme not in [u'http', u'https']:
            return u''

        try:
            domain_match = self._re_domain.search(uri.lower())
            if domain_match is None:
                return u''
            domain = domain_match.group(1)
        except IndexError:
            return u''

        domain = domain.lower()
        if domain.startswith(u'www.'):
            domain = domain[4:]

        def percent_encode(s):            
            safe_chars = self._safe_chars
            def replace(c):
                if c not in safe_chars:
                    return u"%%%02X" % ord(c)
                else:
                    return c
            return u"".join([replace(c) for c in s])

        #self.url = percent_encode(url.encode(u'utf-8', u'replace'))
        self.url = percent_encode(url)
        self.domain = domain

        if not self.url:
            return u""

        if self.domain:
            return u'<a href="%s" target="_blank">' % PostMarkup.standard_replace_no_break(self.url)
        else:
            return u""
	
_my_postmarkup = create(use_pygments=pygments_available, annotate_links=False)
#cover default behaive of quote tag
_my_postmarkup.add_tag(MyVideoTag,u"video")
_my_postmarkup.add_tag(MyQuoteTag,u"quote")
_my_postmarkup.add_tag(EmoticonTag,u"emo")
_my_postmarkup.add_tag(MyImgTag,u"img")
_my_postmarkup.add_tag(MyLinkTag,u"url")
render_bbcode = _my_postmarkup.render_to_html
