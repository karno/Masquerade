#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from twitter import *

from config import *

def switch_profile(key: str):
    api = Twitter(auth=OAuth(
        config['token']['key'],
        config['token']['secret'],
        config['consumer']['key'],
        config['consumer']['secret']))

    prof = _find_profile(key)

    print('uploading profile image...')

    with open(prof['image'], "rb") as image:
        params = {"image": image.read()}
    api.account.update_profile_image(**params)

    print('updating profile...')

    api.account.update_profile(
            name=prof['name'],
            url=prof['url'],
            location=prof['location'],
            description=prof['description'])

    if 'auto_intro' in prof and prof['auto_intro'] == True and \
        'intro' in prof and prof['intro'] is not None:
            post_intro(key)

    print('successfully changed to ' + prof['name'] + '.')

def post_intro(key: str):
    api = Twitter(auth=OAuth(
        config['token']['key'],
        config['token']['secret'],
        config['consumer']['key'],
        config['consumer']['secret']))

    prof = _find_profile(key)
    print('tweeting introduction...')
    api.statuses.update(status=prof['intro'])

def _find_profile(key: str):
    # find matching profile
    for cp in config['profiles']:
        if cp['key'] == key:
            return cp

    try:
        return config['profiles'][int(key)]
    except ValueError:
        pass

    raise KeyError

if __name__ == '__main__':
    try:
        if len(sys.argv) >= 2:
            switch_profile(sys.argv[1])
        else:
            switch_profile('')
    except KeyError:
        print('invalid key:' + sys.argv[1])
        exit(-1)
    exit(0)
