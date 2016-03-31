#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import urlopen, URLError, HTTPError # In python 3 change to urllib.*
import json

def fetch_events(user_id):
    try:
        html = urlopen('https://api.github.com/users/' + user_id + '/events')
    # In python 3, add .decode('UTF-8') after read()
    except URLError as e:
        print(e.reason)
    else:
        json_str = (html.read())
        json_dict = json.loads(json_str)
        for event in json_dict:
            print event
