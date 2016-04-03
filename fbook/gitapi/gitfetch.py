#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, URLError, HTTPError
import json
import re


class GitAPI:

    def __init__(self):
        pass

    def fetch_events(self, user_id):
        returned_list = []
        try:
            ht = urlopen('https://api.github.com/users/' + user_id + '/events')
            avatar = urlopen('https://api.github.com/users/' + user_id)
        # In python 3, add .decode('UTF-8') after read()
        except URLError as e:
            print(e.reason)
        else:
            json_str = (ht.read())
            json_dict = json.loads(json_str)
            ava_json_str = (avatar.read())
            pattern = '"avatar_url":".*?"'
            ava_url = re.findall(pattern, ava_json_str)[0][14:-1]
            count = 0
            for event in json_dict:
                if count < 6:
                    result = {'id': event['id'],
                              'type': event['type'],
                              'actor': user_id,
                              'repo': event['repo']['name'],
                              'repo_url': event['repo']['url'],
                              'public': event['public'],
                              'created_at': event['created_at'],
                              'ava_url': ava_url
                              }
                    returned_list.append(result)
                count += 1
        print returned_list
        if len(returned_list) is not 0:
            return returned_list
