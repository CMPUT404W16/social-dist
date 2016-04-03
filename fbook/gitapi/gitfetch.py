#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, URLError, HTTPError
import json
import re


def fetch_events(user_id):
    returned_list = []
    try:
        html = urlopen('https://api.github.com/users/' + user_id + '/events')
        avatar = urlopen('https://api.github.com/users/' + user_id)
    # In python 3, add .decode('UTF-8') after read()
    except URLError as e:
        print(e.reason)
    else:
        json_str = (html.read())
        json_dict = json.loads(json_str)
        ava_json_str = (avatar.read())
        pattern = '"avatar_url":".*?"'
        ava_url = re.findall(pattern, ava_json_str)[0][14:-1]
        print ava_url
        for event in json_dict:
            result = {'id': event['id'],
                      'type': event['type'],
                      'actor': user_id,
                      'repo': event['repo']['name'],
                      'repo_url': event['repo']['url'],
                      'public': event['public'],
                      'created_at': event['created_at'],
                      'ava_url': ava_url
                      }
                      # 'avatar': ava_json_dict[0]['avatar_url']

            returned_list.append(result)
    # print returned_list
    if len(returned_list) is not 0:
        return returned_list

fetch_events('JiYangE')
