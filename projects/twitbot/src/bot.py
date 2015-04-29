#!/usr/bin/env python
import tweepy
#from our keys module (keys.py), import the keys dictionary
from keys import keys
from pprint import pprint
import time
import urllib
import os
import magic
from glob import iglob
import shutil
import random

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

SAVED_IMAGES  = "incoming-images"
SNOWDEN_DOCUMENT_SOURCE = "snowden-documents/txt"

api = None

def find_mentions(txt):
	""" find all the people mentioned in a tweet """
	mention_re = re.compile(r'@([A-Za-z0-9_]+)')
	return mention_re.findall(txt)

def grab_audio_from_tweet():
	pass

def choose_snowden_document():
	""" pick a random snowden document """
	lst = []
	for txt in iglob(os.path.join(SNOWDEN_DOCUMENT_SOURCE, '*.txt')):
		lst.append(txt)

	return random.choice(lst)

def merge_files(txt, img):
	""" merge a text into an image """
	destination = open(img, 'wb')
	shutil.copyfileobj(open(txt, 'rb'), destination)
	destination.close()
	return img


def grab_images_from_tweet(tweet):
	""" get all the images associated with the tweet that we pass as parameter """
	count = 0
	for media in tweet.extended_entities['media']:
		count += 1
		if media['type'] == 'photo':
			image_uri = media['media_url'] + ':large'
			print image_uri
			#filename = date + '-twitter.com_' + screen_name + '-' + status_id + '-' + str(count)
			#filepath = directory + '/' + filename
			filepath = "{0}/savedimage-{1}".format(SAVED_IMAGES, tweet.id)
			# download image
			urllib.urlretrieve(image_uri, filepath)
			# identify mime type and attach extension
			if os.path.exists(filepath):
				mime = magic.from_file(filepath, mime=True)
				if mime == "image/gif":
					newfilepath = filepath + ".gif"
				elif mime == "image/jpeg":
					newfilepath = filepath + ".jpg"
				elif mime == "image/png":
					newfilepath = filepath + ".png"
				else:
					err = filepath + ": unrecgonized image type"
					print_error(err)
					continue
				os.rename(filepath, newfilepath)
				return newfilepath
			else:
				# donwload failed for whatever reason
				err = filename + ": failed to download " + image_uri
				print_error(err)
				continue


def connect():
	""" connect to twitter user the keys we got from the website """
	global api
	print "Connecting to the twitter API"
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

def does_tweet_have_image(tweet):
	""" determine if the tweet has image attachments (return true or false) """
	return ( hasattr(tweet, 'extended_entities') )

def main():
	connect()

	mentions = api.mentions_timeline()
	if mentions:
		#print "We have some mentions"
		for m in mentions:
			if does_tweet_have_image(m):
				imagefile = grab_images_from_tweet(m)
				document = choose_snowden_document()
				# now merge both files into an image
				merged = merge_files(document, imagefile)
				# @TODO get from mention the name / screenname (m.user.screen_name) of the tweeter
				# @TODO now get the image in 'merged' and tweet it back to the original tweeter 
			else:
				print "Tweet doesn't have an image"
	else:
		print "no mentions"


if __name__ == "__main__":
	main()
