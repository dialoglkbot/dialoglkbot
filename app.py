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
import sys
from tweepy import Stream, StreamListener, OAuthHandler
from dialogbot import DialogBot
from settings import settings
from optparse import OptionParser


# ----- Error Handling is for the weak -----

class TweetListener(StreamListener):
    """
    A listener handles tweets are the received from the stream.
    """
    def on_status(self, status):
        db = DialogBot(options, auth)
        db.fire(status)  # Do things, Gandalf.

    def on_error(self, status_code):
        sys.stderr.write("Error in status. %s\n" % status_code)
        sys.stderr.flush()

if __name__ == "__main__":
    ### Parse command-line args ###
    parser = OptionParser()
    # -d option for dryrun. File will be updated, but nothing tweeted.
    parser.add_option("-d", "--dryrun", action="store_true", dest="dry", default=False,
                      help="If specified, output won't be tweeted")
    (options, args) = parser.parse_args()

    # Tweepy auth object
    auth = OAuthHandler(settings['tw-consumer-key'], settings['tw-consumer-secret'])
    auth.set_access_token(settings['tw-app-key'], settings['tw-app-secret'])

    # Create listener for search stream
    listner = TweetListener()
    stream = Stream(auth, listner, timeout=None)
    stream.filter(track="@dialoglk")
