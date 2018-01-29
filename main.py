# coding: utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta, date
from IgnoreList import IgnoreList
from Logger import Logger
from Config import Config
import random
import tweepy
import json

# Don't edit these unless you know what you're doing.
api = None #Its initialized if this is main
post_list = list()
ratelimit = [999, 999, 100]
ratelimit_search = [999, 999, 100]
ignore_list = None

def random_time(start, end):
	sec_diff = int((end-start).total_seconds())
	secs_to_add = random.randint(0, sec_diff)
	return start + timedelta(seconds=secs_to_add)

def get_daily_tweets_random_times(n, start, end):
	times = []
	for i in range(0, Config.daily_tweets):
	    times.append(random_time(start, end))
	times.sort()
	return times

def CheckBlockedUsers():
    if not ratelimit_search[2] < Config.min_ratelimit_search:
        for b in api.blocks_ids():
            if not b in ignore_list:
                ignore_list.append(b)
                logger.info("Blocked user {0} added to ignore list".format(b))
    else:
        logger.warn("Update blocked users skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list), ratelimit_search[1], ratelimit_search[0], ratelimit_search[2]))

def CheckRateLimit():

    global ratelimit
    global ratelimit_search

    if ratelimit[2] < Config.min_ratelimit:
        logger.warn("Ratelimit too low -> Cooldown ({}%)".format(ratelimit[2]))
        time.sleep(30)

    r = api.rate_limit_status()

    for res_family in r['resources']:
        for res in r['resources'][res_family]:
            limit = r['resources'][res_family][res]['limit']
            remaining = r['resources'][res_family][res]['remaining']
            percent = float(remaining) / float(limit) * 100

            if res == "/search/tweets":
                ratelimit_search = [limit, remaining, percent]

            if res == "/application/rate_limit_status":
                ratelimit = [limit, remaining, percent]

            #print(res_family + " -> " + res + ": " + str(percent))
            if percent < 5.0:
                message = "{0} Rate Limit-> {1}: {2} !!! <5% Emergency exit !!!".format(res_family, res, percent)
                logger.critical(message)
                sys.exit(message)
            elif percent < 30.0:
                logger.warn("{0} Rate Limit-> {1}: {2} !!! <30% alert !!!".format(res_family, res, percent))
            elif percent < 70.0:
                logger.info("{0} Rate Limit-> {1}: {2}".format(res_family, res, percent))

def ClearQueue():
    post_list_length = len(post_list)

    if post_list_length > Config.min_posts_queue:
        del post_list[:post_list_length - Config.min_posts_queue]
        logger.info("===THE QUEUE HAS BEEN CLEARED===")

# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():

    logger.info("=== CHECKING RETWEET QUEUE ===")
    logger.info("Queue length: {}".format(len(post_list)))

    if len(post_list) > 0:
        if ratelimit[2] < Config.min_ratelimit_retweet:
        	logger.info("Ratelimit at {0}% -> pausing retweets".format(ratelimit[2]))
        	return

        post = post_list[0]
        logger.info("Retweeting: {0} {1}".format(post.id, post.text.encode('utf8')))

        if r.user.id in ignore_list:
        	post_list.pop(0)
        	logger.info("Blocked user's tweet skipped")
        	return

        # r = api.retweet(post.id)
        post_list.pop(0)
        CheckForFollowRequest(post)
        #CheckForFavoriteRequest(post)

# Schedule random times over the course of the day to call UpdateQueue,
# giving the application the appearance of manual interaction.
# Number of tweets per day can be defined in config - daily-tweets.
def RandomTimes():
	# we need to parse today's state to properly
	# schedule the tweet times
	dadate = datetime.now()
	year = dadate.year
	month = dadate.month
	day = dadate.day

	# the lower bound
	lower_bound = datetime.now()
	logger.info("[{}] - the lower bound is {}".format(datetime.now(), lower_bound))

	# the upper bound
	upper_bound = lower_bound + timedelta(hours=22)
	logger.info("[{}] - the upper bound is {}".format(datetime.now(), upper_bound))

	times = get_daily_tweets_random_times(Config.daily_tweets, lower_bound, upper_bound)
	logger.info("[{}] - Received {} times to schedule".format(datetime.now(), len(times)))

	for ind, atime in enumerate(times):
	    if ind == (Config.daily_tweets-1):
	        scheduler.add_job(UpdateQueue, 'date', run_date=atime)
	        logger.info("[{}] - added last task at {}".format(datetime.now(), atime))
	    else:
	        scheduler.add_job(UpdateQueue, 'date', run_date=atime)
	        logger.info("[{}] - added task at {}".format(datetime.now(), atime))

# Scan for new contests, but not too often because of the rate limit.
def ScanForContests():

    global ratelimit_search

    if ratelimit_search[2] < Config.min_ratelimit_search:
    	logger.warn("Search skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list), ratelimit_search[1], ratelimit_search[0], ratelimit_search[2]))
    	return

    logger.info("=== SCANNING FOR NEW CONTESTS ===")

    for search_query in Config.search_queries:
        logger.info("Getting new results for: {0}".format(search_query))
        try:

            c = 0

            for tweet in tweepy.Cursor(api.search, q=search_query, lang="fr").items(50):

                c += 1
                user_item = tweet.user
                screen_name = user_item.screen_name
                text = tweet.text.replace("\n", "")
                id = tweet.id
                original_id = id

                if hasattr(tweet, 'retweeted_status'):
                    original_item = tweet.retweeted_status
                    original_id = original_item.id
                    original_user_item = original_item.user
                    original_screen_name = original_user_item.screen_name

                    if original_id in ignore_list:
                    	logger.info("{0} ignored {1} in ignore list".format(id, original_id))
                    	continue

                    if original_user_item.id in ignore_list:
                    	logger.info("{0} ignored {1} blocked and in ignore list".format(id, original_screen_name))
                    	continue

                    post_list.append(original_item)
                    logger.info("{0} - {1} retweeting {2} - {3} : {4}".format(id, screen_name, original_id, original_screen_name,text))
                    ignore_list.append(original_id)
                else:
                    if id in ignore_list:
                    	logger.info("{0} in ignore list".format(id))
                    	continue

                    if user_item.id in ignore_list:
                    	logger.info("{0} ignored {1} blocked user in ignore list".format(id, screen_name))
                    	continue

                    post_list.append(tweet)
                    logger.info("{0} - {1} : {2}".format(id, screen_name, text))
                    ignore_list.append(id)

            logger.info("Got {0} results".format(c))

        except Exception as e:
            logger.exception("Could not connect to Twitter - are your credentials correct?")

if __name__ == '__main__':
    Config.load('config.json')
    logger = Logger('twitter-contestant')

    # Intilialize Tweepy
    auth = tweepy.OAuthHandler(Config.consumer_key, Config.consumer_secret)
    auth.set_access_token(Config.access_token_key, Config.access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

    #Initialize ignorelist
    ignore_list = IgnoreList("ignorelist")

    #Initialize scheduler
    scheduler = BlockingScheduler()

    #First run
    RandomTimes()
    ClearQueue()
    CheckRateLimit()
    #CheckBlockedUsers()
    ScanForContests()

    scheduler.add_job(RandomTimes, 'interval', hours=24)
    scheduler.add_job(ClearQueue, 'interval', seconds=Config.clear_queue_time)
    scheduler.add_job(CheckRateLimit, 'interval', seconds=Config.rate_limit_update_time)
    #scheduler.add_job(CheckBlockedUsers, 'interval', seconds=Config.blocked_users_update_time)
    scheduler.add_job(ScanForContests, 'interval', seconds=Config.scan_update_time)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
