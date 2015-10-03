#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import re
import threading
import time

from twitter import *

from config import *
from masquerade import *


def server_process():
    # overwrite output encoding
    auth = OAuth(
        config['token']['key'],
        config['token']['secret'],
        config['consumer']['key'],
        config['consumer']['secret'])
    api = Twitter(auth=auth)
    curprofkey = get_current_prof_key(api)
    if curprofkey is None:
        curprofkey = config['profiles'][0]['key']
    print('* current profile is ' + curprofkey)
    # backoff interval is 5 upto 320 (sec)
    backoff = 5 
    shutdown = False
    streamer = TwitterStream(domain='userstream.twitter.com', auth=auth)
    while not shutdown:
        try:
            for status in streamer.user():
                backoff = 5
                if "text" in status and "retweeted_status" not in status:
                    # tweet (not retweet) received
                    if status['user']['screen_name'] in config['accept_accounts']:
                        # tweet from acceptable account
                        print_safely('accept:' + status['user']['screen_name'] + ': ' + status['text'])
                        text = status['text']
                        # process tweet
                        fired = False
                        # stage 1 - simple trigger
                        for pattern, keyOrObject in config['simple_trigger'].items():
                            if re.match(pattern, text):
                                if isinstance(keyOrObject, str):
                                    curprofkey = keyOrObject
                                    switch_profile_async(keyOrObject)
                                else:
                                    curprofkey = keyOrObject['key']
                                    if 'intro' in keyOrObject and keyOrObject['intro'] is not None:
                                        switch_profile_async(keyOrObject['key'], keyOrObject['intro'])
                                    else:
                                        switch_profile_async(keyOrObject['key'])
                                    if 'delete' in keyOrObject:
                                        delete_tweet(api, int(status['id_str']))
                                fired = True
                                break
                        if fired:
                            continue
                        # stage 2 - global trigger
                        for pattern in config['global_trigger']:
                            result = re.match(pattern, text)
                            if result:
                                gd = result.groupdict()
                                for prof in config['profiles']:
                                    # check global_trigger_key existence
                                    if 'global_trigger_key' not in prof:
                                        continue
                                    # check global_trigger_key all contains required keys
                                    gtkeys = prof['global_trigger_key']
                                    for key, value in gd.items():
                                        if key not in gtkeys or gtkeys[key] != value:
                                            break
                                    else:
                                        # fired!
                                        curprofkey = prof['key']
                                        switch_profile_async(prof['key'])
                                        if config['delete_on_hit_global_trigger']:
                                            delete_tweet(api, int(status['id_str']))
                                        fired = True
                                        break
                            if fired:
                                break # the profile loop
                        if fired:
                            continue
                        # before stage 3, 4 - check existence of currrent profile key
                        curprof = None
                        for prof in config['profiles']:
                            if prof['key'] == curprofkey:
                                curprof = prof
                                break
                        else:
                            continue
                        # stage 3 - local trigger
                        if 'local_trigger' in curprof:
                            for pattern, key in curprof['local_trigger'].items():
                                if re.match(pattern, text):
                                    curprofkey = key
                                    switch_profile_async(key)
                                    fired = True
                                    break
                            if fired:
                                continue
                        # stage 4 - intro trigger
                        if 'intro' in curprof and curprof['intro'] is not None and \
                                'intro_trigger' in curprof:
                            for pattern in curprof['intro_trigger']:
                                if re.match(pattern, text):
                                    post_intro_async(curprofkey)
                                    break
        except KeyboardInterrupt:
            shutdown = True
        except:
            print('user-stream error: ' + str(sys.exc_info()))
            print('user-stream disconnected. try to reconnect...')
            time.sleep(backoff)
            backoff = backoff * backoff;
            if backoff > 320:
                backoff = 320
    print('shutting down...')


def print_safely(text: str):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print('contains unicode error')

def delete_tweet(api: Twitter, tweet_id: int):
    print("deleting hit status...")
    api.statuses.destroy(_id=tweet_id, _method='POST')

def get_current_prof_key(api: Twitter):
    """ get current profile, or default """
    # acquire recent status of user's
    try:
        timeline = api.statuses.user_timeline(count=1)
        user = timeline[0]['user']
        targets = config['profile_match_key']
        for prof in config['profiles']:
            for target in targets:
                if target not in user or target not in prof:
                    continue
                if user[target] != prof[target]:
                    break
            else:
                return prof['key']
    except:
        # fail to acquision recent tweet
        print("fail to acquire user's tweet.")
    return None

def switch_profile_async(key: str, post_intro:bool = False):
    switcher = AsyncProfSwitcher(key, post_intro)
    switcher.start()

class AsyncProfSwitcher(threading.Thread):
    """ update twitter profile asynchronously. """
    def __init__(self, key: str, post_intro:bool = False):
        super(AsyncProfSwitcher, self).__init__()
        self.key = key
        self.post_intro = post_intro

    def run(self):
        print('switch profile:' + self.key + ', intro? ' + str(self.post_intro))
        switch_profile(self.key)
        if self.post_intro:
            post_intro(self.key)

def post_intro_async(key: str):
    poster = AsyncIntroPoster(key)
    poster.start()

class AsyncIntroPoster(threading.Thread):
    """ update twitter profile asynchronously. """
    def __init__(self, key: str):
        super(AsyncIntroPoster, self).__init__()
        self.key = key

    def run(self):
        post_intro(self.key)

if __name__ == '__main__':
    server_process()

