import praw
import json
import requests
import tweepy
import time

from keys import *

# Initiate connection with Reddit
def setup_connection_reddit(subreddit):
	print "[bot] setting up connection with Reddit"
	r = praw.Reddit('yasoob_python reddit twitter bot '
				'monitoring %s' %(subreddit)) 
	subreddit = r.get_subreddit(subreddit)
	return subreddit

# Get posts and links from Reddit
def tweet_creator(subreddit_info):
	post_dict = {}
	post_ids = []
	print "[bot] Getting posts from Reddit"
	for submission in subreddit_info.get_hot(limit=1):
                # strip_title function is defined later
		post_dict[strip_title(submission.title)] = submission.url
		post_ids.append(submission.id)
	print "[bot] Generating short link using goo.gl"
	mini_post_dict = {}
	for post in post_dict:
		post_title = post
		post_link = post_dict[post]   
                # the shorten function is defined later		
		short_link = shorten(post_link)
		mini_post_dict[post_title] = short_link 
	return mini_post_dict, post_ids

# No one likes long links
def shorten(url):
	headers = {'content-type': 'application/json'}
	payload = {"longUrl": url}
	url = "https://www.googleapis.com/urlshortener/v1/url"
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	try:
		link = json.loads(r.text)['id']
		return link
	except:
		return "http://yahoo.com"

# Twitter hates more than 140 characters
def strip_title(title):
	if len(title) < 94:
		return title
	else:
		return title[:93] + "..."

# Dealing with duplicate posts
def add_id_to_file(id):
	with open('posted_posts.txt', 'a') as file:
		file.write(str(id) + "\n")

def duplicate_check(id):
	found = 0
	with open('posted_posts.txt', 'r') as file:
		for line in file:
			if id in line:
				found = 1
	return found

def tweeter(post_dict, post_ids):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	for post, post_id in zip(post_dict, post_ids):
		found = duplicate_check(post_id)
		if found == 0:
			print "[bot] Posting this link on twitter"
			print post
			try:
				api.update_status(status=post + " " + post_dict[post])
			except:
				print "[BOT] Status already posted, passing"
			# add_id_to_file(post_id)
			# time.sleep(10)
		else:
			print "[bot] Already posted"

def main():
	subreddit = setup_connection_reddit('mediaquotes')
	post_dict, post_ids = tweet_creator(subreddit)
	tweeter(post_dict, post_ids)

if __name__ == '__main__':
	main()