#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "consumer": {
        # application consumer key & secret
        "key": "******************",
        "secret": "******************",
    },
    "token": {
        # user token & secret
        "key": "******************",
        "secret": "******************",
    },
    "accept_accounts": ["your_screen_name"],
    "profile_match_key": ["name", "description"],
    # simple_trigger > global_trigger > (local)trigger > intro_trigger
    "simple_trigger": {
        # (regex) => key
        # or
        # (regex) => {'key': key, 'intro': True}
        "^prof(ile)1$": "prof1",
        "^prof(ile)?2$": {"key": "prof2", "intro": True, "delete": True},
    },
    "global_trigger": [
        # use named-group (?P<name>...)
        # switch if regex is accepted and group content is fully matched
        "^switch to (?P<trigger_key>.+)$",
        "^switch to (?P<alt_key>.+)$",
    ],
    "delete_on_hit_global_trigger": True,
    "profiles": [
        # {
        #    "key": "",
        #    "name: "",
        #    "url": "",
        #    "location": "",
        #    "description": "",
        #    "image": ""
        # }
        {
            "key": "prof1",
            "global_trigger_key": {
                "trigger_key": "profile1",
                "alt_key": "prof1",
            },
            "local_trigger": {
                "^sw2$": "prof2",
            },
            "intro_trigger": None,
            # --- bio ---
            "name": "My",
            "url": "example.com",
            "location": "nowhere",
            "description": "Hello!",
            "image": "./pass_to_image.png",
            "auto_intro": False, 
            "intro": "Something tweet when switched to this account",
        },
        {
            "key": "prof2",
            "global_trigger_key": {
                "trigger_key": "profile2",
                "alt_key": "prof2",
            },
            "local_trigger": {
                "^sw1$": "prof1",
                "^switch1$": "prof1",
            },
            # --- bio ---
            "name": "Me",
            "url": "example.jp",
            "location": "everywhere",
            "description": "",
            "image": "./pass_to_another_image.png",
            "auto_intro": True, 
            "intro": "Hello, World!",
        }
    ]
}
