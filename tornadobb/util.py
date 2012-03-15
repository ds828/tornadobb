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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import settings
import logging

def send_mail(receiver,subject,message):
	
	smtp_settings = settings.tornadobb_settings["tornadobb.smtp_settings"]
	
	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = smtp_settings["username"]
	msg['To'] = receiver
	# Record the MIME type
	part = MIMEText(message, 'html')
	msg.attach(part)

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
	smtp.sendmail(sender, receiver, msg.as_string())
	smtp.quit()

def main():
	
	send_mail("songdi19@gmail.com")
	
	return 0

if __name__ == '__main__':
	main()

