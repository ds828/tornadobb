#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       util.py
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
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

def send_mail(receiver,subject,plainText,htmlText,smtp_settings):
	
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
	
def memory_stat():
	
	mem = {}
	f = open("/proc/meminfo")
	lines = f.readlines()
	f.close()
	for line in lines:
		if len(line) < 2: continue
		name = line.split(':')[0]
		var = line.split(':')[1].split()[0]
		mem[name] = long(var) * 1024.0
	mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
	return mem

def cpu_stat():
	cpu = []
	cpuinfo = {}
	f = open("/proc/cpuinfo")
	lines = f.readlines()
	f.close()
	for line in lines:
		if line == 'n':
			cpu.append(cpuinfo)
			cpuinfo = {}
		if len(line) < 2: continue
		name = line.split(':')[0].rstrip()
		var = line.split(':')[1]
		cpuinfo[name] = var
	return cpu

def load_stat():
	loadavg = {}
	f = open("/proc/loadavg")
	con = f.read().split()
	f.close()
	loadavg['lavg_1']=con[0]
	loadavg['lavg_5']=con[1]
	loadavg['lavg_15']=con[2]
	loadavg['nr']=con[3]
	loadavg['last_pid']=con[4]
	return loadavg
	
def uptime_stat():
	uptime = {}
	f = open("/proc/uptime")
	con = f.read().split()
	f.close()
	all_sec = float(con[0])
	MINUTE,HOUR,DAY = 60,3600,86400
	uptime['day'] = int(all_sec / DAY )
	uptime['hour'] = int((all_sec % DAY) / HOUR)
	uptime['minute'] = int((all_sec % HOUR) / MINUTE)
	uptime['second'] = int(all_sec % MINUTE)
	uptime['Free rate'] = float(con[1]) / float(con[0])
	return uptime

def net_stat():
	net = []
	f = open("/proc/net/dev")
	lines = f.readlines()
	f.close()
	for line in lines[2:]:
		con = line.split()
		intf = dict(
			zip(
				( 	'interface','ReceiveBytes','ReceivePackets',
					'ReceiveErrs','ReceiveDrop','ReceiveFifo',
					'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',
					'TransmitBytes','TransmitPackets','TransmitErrs',
					'TransmitDrop', 'TransmitFifo','TransmitFrames',
					'TransmitCompressed','TransmitMulticast' ),
				( 	con[0].rstrip(":"),int(con[1]),int(con[2]),
					int(con[3]),int(con[4]),int(con[5]),
					int(con[6]),int(con[7]),int(con[8]),
					int(con[9]),int(con[10]),int(con[11]),
					int(con[12]),int(con[13]),int(con[14]),
					int(con[15]),int(con[16]), )
				)
			)
		net.append(intf)
	return net
	
def disk_stat():
	import os
	hd={}
	disk = os.statvfs("/")
	hd['available'] = disk.f_bsize * disk.f_bavail
	hd['capacity'] = disk.f_bsize * disk.f_blocks
	hd['used'] = disk.f_bsize * disk.f_bfree
	return hd

def main():
	
	smtp_settings = {

					"server":"smtp.gmail.com",
					"use_authentication": True,
					"tls_port": 587,
					"ssl_port": 465,
					"port":None,
					"username":"tornadobb1@gmail.com",
					"password":"",
					"email_address":"tornadobb1@gmail.com",
				}
	receiver = "songdi19@gmail.com"
	subject = "test subject"
	plainText = "test content"
	htmlText = "<a href="">link</a>"
	send_mail(receiver,subject,plainText,htmlText,smtp_settings)
	return 0

if __name__ == '__main__':
	main()

