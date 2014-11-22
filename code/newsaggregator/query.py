# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2013 Daniel Truemper <truemped at googlemail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
import time


def base_query(now=None, size=50, lang=None):
    if not lang:
        lang = ['de', 'en']

    return {
        "query": {
            "function_score": {
                "query": {
                    "filtered": {
                        "query": {
                            "match_all": {}
                        },
                        "filter": {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "lang": lang
                                        }
                                    },
                                    {
                                        "range": {
                                            "created_at": {
                                                "gt": "now/h-12h"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
            }
        },
        'aggregations': {},
        "size": size
    }


def function_score(query, now=None, g=1.8):
    if not now:
        now = int(time.time() * 1000)

    query['query']['function_score']['script_score'] = {
        'params': {
            'g': g,
            'now': now
        },
        "script": ("(doc['favorite_count'].value + " +
                   "doc['retweet_count'].value) / " +
                   "pow((now - doc['created_at'].value + 2), g)")}
    return query


def top_hashtags(query):
    query['aggregations']['hashtags'] = {
        'terms': {
            'field': 'entities.hashtags.text',
            'size': 20}}
    return query


def top_domains(query):
    query['aggregations']['domains'] = {
        'terms': {
            'field': 'entities.urls.domain', 'size': 20}}
    return query


def domain_date_histogram(query):
    query['aggregations']['date_hist'] = {
        'date_histogram': {
            'field': 'created_at',
            'interval': '1h'},
        'aggregations': {
            'domains': {'terms': {
                'field': 'entities.urls.domain'}}}}
    return query


def group_by_domain(query):
    query['aggregations']['top_news'] = {
        'terms': {
            'field': 'entities.urls.domain',
            'order': {
                'top_hit': 'desc'}},
        'aggregations': {
            'top_tweets': {
                'top_hits': {}
            },
            'top_hit': {
                'max': {
                    'script': '_score'}}}}
    return query
