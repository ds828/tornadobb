#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       util.py
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


import settings
import logging
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

def send_mail(receiver,subject,plainText,htmlText):
	
	smtp_settings = settings.tornadobb_settings["tornadobb.smtp_settings"]
	
	msgRoot = MIMEMultipart('related')
	msgRoot['Subject'] = subject
	msgRoot['From'] = smtp_settings["email_address"]
	msgRoot['To'] = receiver

	# Encapsulate the plain and HTML versions of the message body in an
	# ‘alternative’ part, so message agents can decide which they want to display.
	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	msgText = MIMEText(plainText, 'plain', 'utf-8')
	msgAlternative.attach(msgText)

	msgText = MIMEText(htmlText, 'html', 'utf-8')
	msgAlternative.attach(msgText)

	# Send the message via local SMTP server.
	if smtp_settings["use_authentication"]:
		try:
			smtp = smtplib.SMTP_SSL(smtp_settings["server"],smtp_settings["ssl_port"])	
		except Exception as e:
			logging.exception(e)
			try:
				smtp = smtplib.SMTP_SSL(smtp_settings["server"],smtp_settings["tls_port"])
			except Exception as e:
				logging.exception(e)
				raise Exception
	else:
		smtp = smtplib.SMTP(smtp_settings["server"],smtp_settings["port"])
	smtp.login(smtp_settings["username"],smtp_settings["password"])
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	smtp.sendmail(smtp_settings["email_address"], receiver, msgRoot.as_string())
	smtp.quit()

def main():
	
	send_mail("songdi19@gmail.com","中文内容","中文内容")
	
	return 0

if __name__ == '__main__':
	main()

