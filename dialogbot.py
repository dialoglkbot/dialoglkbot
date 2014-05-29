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
    auth = {}
    options = []
    records = {}
    messages = ["Please DM your contact number, we'll get back to you shortly.",
                "Please DM us your e-mail address. We'll look into this.",
                "We understand your request, we'll incorporate your address in future.",
                "Thank You for your feedback. We have escalated your concern to our Product team.",
                "We are sorry to hear that, can you kindly DM us with more details about the issue!",
                "We are sorry you feel this way, DM your connection no and contact no, We'll look into it.",
                "We have noted your concern. We'll make sure that this will not happen in future.",
                "Please inbox us your contact number. We'll get back to you with assistance.",
                "DM your connection no. we'll keep you posted.",
                "Thank you for letting us know, We'll look into it and get back to soon with assistance.",
                "Please DM us your connection number, exact location, phone model & Displayed Cell. Thanks.",
                "Please DM us your contact number & exact location details to inform our Network Team.",
                "Please DM us your connection number for us to assist you better.",
                "Awww, DM your contact no and we'll get an expert assist you.",
                "Is it possible for you to DM us your connection number to check further please?",
                "We will look into your concern. Please DM us your issue and we'll get back to you with assistance.",
                "Thank you for getting in touch with us. Please give us a shout if there is anything else. :) ",
                "DM your connection no and contact no, Expert will connect you to assist."
                ]

    bot_agents = ["Riya", "Niky", "Suzy", "Hkk", "Mili", "Naz", "Nabs"]

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
            pass  # ignoring check conditions for testing
        else:
            if not tweet.in_reply_to_screen_name == "dialoglk":
                return  # no point replying if tweet isn't directed at @dialoglk
            if tweet.in_reply_to_status_id is not None:
                return  # ignoring tweets that are not the start of a conversation
            if '?' not in tweet.text:
                return  # ignoring tweets without a question
            if not self.check_time(tweet.author.screen_name):
                return  # ignoring authors that have been replied to in the last 24 hours

        # conditions passed. send the tweet.
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
        random_message = self.messages[randint(0, len(self.messages) - 1)]
        random_bot = "^" + self.bot_agents[randint(0, len(self.bot_agents) - 1)] + "Bot"
        print "update tweet " + '@%s %s %s' % (name, random_message, random_bot)
        if not self.options.dry:
            # Don't tweet on dry run. It's not nice
            api.update_status('@%s %s %s' % (name, random_message, random_bot), tweetid)

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
