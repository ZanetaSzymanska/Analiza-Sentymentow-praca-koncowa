#!/home/sshuser/gettweets/gettweets/bin/python

from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
from progressbar import ProgressBar, Percentage, Bar
import json
import sys
from textblob import TextBlob

#Twitter app information
consumer_secret='RhMrZKPB7FKxliNy0v1gq8dnhE4c1ubXIaz7K2GdFVi9BOfycq'
consumer_key='mFHJNCItDv4cRiizWDCXuEmtH'
access_token='1244207442642247681-hJGqesRnGiGJm5WXYYgGQtw5B25RjP'
access_token_secret='VK26HSQ8aJ8SsLasQ3J97pvkaH2ijnf7ohOEi0zuwPhv0'

#The number of tweets we want to get
max_tweets=10000
max_files=10
#filename = 'tweets_pandemic_10K_1.json'

#Create the listener class that receives and saves tweets
class listener(StreamListener):
    #On init, set the counter to zero and create a progress bar
    def __init__(self, api=None):
        self.num_tweets = 0
        self.num_files = 1
        self.filename = 'tweets_pandemic_10K_1.json'
        self.pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=max_tweets).start()

    #When data is received, do this
    def on_data(self, data):
        data.lower()
        tweet = json.loads(data)
        #tweet.lower()
        if 'text' in data and 'location' in data and tweet['user']['location']:
            blob = TextBlob(tweet["text"])
            tweet['polarity'] = round(blob.sentiment.polarity,5)
            #print(data['polarity'])
            #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            tweet['subjectivity'] = blob.sentiment.subjectivity
            tweet['sentiment'] = str(blob.sentiment)
            #print(data['subjectivity'])
            #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            #Append the tweet to the 'tweets.txt' file
            with open(self.filename, 'a') as tweet_file:
                tweet_file.write(json.dumps(tweet))
                tweet_file.write("\n")
                #Increment the number of tweets
                self.num_tweets += 1
                #Check to see if we have hit max_tweets and exit if so
                if self.num_tweets >= max_tweets:
                    self.pbar.finish()
                    #sys.exit(0)
                    if self.num_files >= max_files:
                        sys.exit(0)
                    else:
                        self.num_files += 1
                        self.filename = 'tweets_pandemic_10K_'+str(self.num_files)+'.json'
                        self.num_tweets = 0
                        self.pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=max_tweets).start()
                        print(self.filename) 
                else:
                    #increment the progress bar
                    self.pbar.update(self.num_tweets)
        return True

    #Handle any errors that may occur
    def on_error(self, status):
        print(status)


#print(filename)
#Get the OAuth token
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
#Use the listener class for stream processing
twitterStream = Stream(auth, listener())
#Filter for these topics
twitterStream.filter(track=["pandemic","coronavirus","COVID-19"])
