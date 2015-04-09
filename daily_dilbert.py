#!/usr/bin/python

##
# Daily Dilbert
# 
# A simple scraper that picks up the day's Dilbert comic and emails it to people.
##

import os
import sys
import urllib2
import logging
import time
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

email_list_file = 'dilbert_list.txt'
log_file = 'dilbert_log.txt'
comic_file = 'dilbert.gif'

# Empty log file.
open(log_file, 'w').close()

# Logging setup.
logger = logging.getLogger('DailyDilbert')
logger.filemode = 'w'
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Fake headers.
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36',
           'Pragma': 'no-cache', 'Host': 'assets.amuniversal.com'}
comic_site = 'http://dilbert.com'

mail_server = 'smtp.mail.com'  # SMTP server
mail_port = 587  # SMTP Port
mail_username = 'username'  # SMTP Username
mail_password = 'password'  # SMTP Password

logger.info('Starting up script...')

try:
	#print email_list_file
	email_dl_file = open(email_list_file)
	email_dl_ids = email_dl_file.readlines()
	email_dl_file.close()
	logger.info('Read ' + str(len(email_dl_ids)) + ' email IDs from file.')

	today = datetime.datetime.now()
	formatted_date = '{0}-{1}-{2}'.format(today.year, today.month, today.day)
	todays_page = 'http://dilbert.com/strip/{0}/'.format(formatted_date)
	headers['Referer'] = todays_page
	request = urllib2.Request(todays_page, None, headers)
	logger.info('Opened Dilbert RSS feed...')
	comic_page_source = urllib2.urlopen(request).read()
	logger.info('Finished reading Dilbert RSS feed content.')
	comic_image_url = comic_page_source.split(' img-comic')[1].split('src="')[1].split('" ')[0]
	logger.info('Finished parsing for comic image\'s URL - ' + comic_image_url)
	request = urllib2.Request(comic_image_url, None, headers)
	comic_image_content = urllib2.urlopen(request)
	logger.info('Opened image. Now writing to file...')
	with open(comic_file, 'wb') as comic_local_image:
		comic_local_image.write(comic_image_content.read())
	logger.info('Finished writing to file. Now preparing to generate rich email..')
	# Define these once; use them twice!
	email_from = '"Sender"<sender@website.com>'

	# Create the root message and fill in the from, to, and subject headers
	msgRoot = MIMEMultipart('related')
	msgRoot['Subject'] = 'Daily Dilbert'
	msgRoot['From'] = email_from
	# This, non-intuitively, doesn't work.
	# msgRoot['Bcc'] = email_ids
	msgRoot.preamble = 'This is today\'s Dilbert comic.'

	# Encapsulate the plain and HTML versions of the message body in an
	# 'alternative' part, so message agents can decide which they want to display.
	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	msgText = MIMEText('If you cannot view the comic, visit {0}.'.format(comic_site))
	msgAlternative.attach(msgText)

	# We reference the image in the IMG SRC attribute by the ID we give it below
	msgText = MIMEText('<img src="cid:dilbert"><br><br><em><small>This email is sent automatically by v2 (updated 22nd January, 2015) of a badass script running on Python and magic! If you\'d like to unsubscribe, please <a href="mailto:exchequer598@gmail.com?subject=Unsubscribe - Daily Dilbert">write</a> to me!<small></em><br><br><small>The <a href="http://www.dilbert.com/">Dilbert</a> comic strip by <a href="http://www.dilbert.com/about/">Scott Adams</a> is copyrighted & trademarked material.</small>', 'html')
	msgAlternative.attach(msgText)

	# Assume the image is in the current directory
	fp = open(comic_file, 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()
	# Define the image's ID as referenced above
	msgImage.add_header('Content-ID', '<dilbert>')
	msgRoot.attach(msgImage)
	logger.info('Comic image added to multipart email.')

	start_time = time.time()
	# Send the email (this example assumes SMTP authentication is required)
	logger.info('Connecting to SMTP server...')
	server = smtplib.SMTP(mail_server, mail_port)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(mail_username, mail_password)
	logger.info('Logged in to SMTP server. Now sending email...')
	# This is how you actually add a bunch of IDs to BCC...
	# I know, right?!
	server.sendmail(email_from, [] + [] + email_dl_ids, msgRoot.as_string())
	end_time = time.time()
	logger.info('Email sent in {0:.2f} seconds!'.format(end_time - start_time))
	server.close()
	logger.info('Exiting script now... Bye!')
except:
	logger.exception('Encountered unrecoverable error. Writing stacktrace to file and quitting...')
