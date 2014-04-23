"""The MIT License (MIT)

Copyright (c) 2014 dialoglkbot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

__author__ = 'dialoglkbot'
import tweepy
import sys
from datetime import datetime, timedelta
from time import mktime, strptime
from random import randint


class DialogBot:
    REC_FILE_NAME = "records.txt"
    shouldtweet = False
    auth = {}
    options = []
    records = {}
    messages = ["Please DM your contact number, we'll get back to you shortly ^BotAgent",
                "Please DM us your e-mail address. We'll look into this. ^BotAgent",
                "We understand your request, we'll incorporate your address in future ^BotAgent",
                "Thank You for your feedback. We have escalated your concern to our Product team. ^BotAgent",
                "We are sorry to hear that, can you kindly DM us with more details about the issue! ^BotAgent",
                "We are sorry you feel this way, DM your connection no and contact no, We'll look into it. ^BotAgent",
                "We have noted your concern. We'll make sure that this will not happen in future. ^BotAgent",
                "Please inbox us your contact number. We'll get back to you with assistance. ^BotAgent",
                "DM your connection no. we'll keep you posted ^BotAgent",
                "Thank you for letting us know, We'll look into it and get back to soon with assistance. ^BotAgent"]

    def __init__(self, options, auth):
        """
        Accepts the command line options and the tweepy auth object
        """
        self.options = options
        self.auth = auth

    def fire(self, tweet):
        """
        Botmagic starts here. Checks a few conditions to see if this idiot is worth replying to.
        Then moves onto the good stuff.
        """
        self.load_record()

        if self.options.dry:
            self.shouldtweet = True  # ignore check conditions for testing
        else:
            if tweet.in_reply_to_screen_name == "dialoglk":
                self.shouldtweet = True
            else:
                self.shouldtweet = False
                return
            if tweet.in_reply_to_status_id is not None:
                self.shouldtweet = False
                return
            if self.check_time(tweet.author.screen_name):
                self.shouldtweet = True
            else:
                return

        if self.shouldtweet:
            self.tweet(tweet.author.screen_name, tweet.id)

    def check_time(self, name):
        """
        Iterates over the records loaded from the records.txt file and checks the last
        tweeted time for the user. Only tweet if another tweet hasn't been sent for that
        user in the last 24 hours. Good bots don't spam.
        """
        if name in self.records:
            last_time = self.records[name]
            if datetime.now() - last_time > timedelta(days=1):
                return True
            else:
                return False
        else:
            self.records[name] = datetime.now()
            self.update_record()
            return True

    def tweet(self, name, tweetid):
        """
        This really should be obvious. Tweets the.. uh.. tweet.
        """
        api = tweepy.API(self.auth)
        print "update tweet " + '@%s %s' % (name, self.messages[randint(0, len(self.messages) - 1)])
        if not self.options.dry:
            # Don't tweet on dry run. It's not nice
            api.update_status('@%s %s' % (name, self.messages[randint(0, len(self.messages) - 1)]), tweetid)

    def update_record(self):
        """
        If a tweet was sent, update the records.txt file with the new times.
        """
        try:
            f = open(self.REC_FILE_NAME, "w")
        except IOError, e:
            sys.stderr.write("Records file could not be opened for reading. %s\n" % e)
            sys.stderr.flush()
            sys.exit(1)

        for key, value in self.records.iteritems():
            f.write(key + "|" + value.strftime('%Y%m%d %H:%M:%S') + "\n")

    def load_record(self):
        """
        Reads the record.txt file and loads into records dictionary
        """
        try:
            f = open(self.REC_FILE_NAME, "r")
        except IOError, e:
            sys.stderr.write("Records file could not be opened for reading. %s\n" % e)
            sys.stderr.flush()
            sys.exit(1)

        while 1:
            line = f.readline().strip()
            if not line:
                break
            name = line.split("|")[0]
            time = line.split("|")[1]
            try:
                timestamp = strptime(time, '%Y%m%d %H:%M:%S')
            except ValueError, e:
                sys.stderr.write("Error in records file. %s\n" % e)
                sys.stderr.flush()
                continue  # ignore this and move on

            self.records[name] = datetime.fromtimestamp(mktime(timestamp))
