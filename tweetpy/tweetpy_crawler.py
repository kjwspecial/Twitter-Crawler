import tweepy
from tweepy import OAuthHandler, API
import pandas as pd

def auth(consumer_key, consumer_secret, access_token, access_secret):
    auth = OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_secret)
    api = API(auth)
    return api

def tweet_search(api, num_tweets, keyword):
    num_tweets = 100
    total_tweet =[]
    last_id = -1
    
    while len(total_tweet) < num_tweets:
        count = num_tweets - len(total_tweet)
        try : 
            new_tweets = api.search(q = keyword, count = count)
            if not new_tweets:
                break
            total_tweet.extend(new_tweets)
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            break
    return total_tweet


def data_to_pd(total_tweet):
    name, ids, mention, date, time = [], [], [], [], []
    
    for tweet in total_tweet:
        created_time = str(tweet.created_at)
        time_split = created_time.split()
        
        name.append(tweet.user.name)
        ids.append('@'+ tweet.user.screen_name)
        mention.append(tweet.text)
        date.append(time_split[0])
        time.append(time_split[1])
    data ={}
    data['name'] =name
    data['id'] = ids
    data['mention'] = mention
    data['date'] = date
    data['time'] = time
    return pd.DataFrame(data)