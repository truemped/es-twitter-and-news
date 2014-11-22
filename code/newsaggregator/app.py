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
import delorean
from elasticsearch import Elasticsearch
from flask import Flask, render_template, request
import humanize

from newsaggregator.query import (base_query, function_score, top_hashtags,
                                  top_domains, domain_date_histogram,
                                  group_by_domain)


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.debug = app.config['DEBUG']
es = Elasticsearch([app.config['ES_HOST']])


def humanize_tweet_published(tweet):
    t = delorean.parse(tweet['created_at'])
    tweet['humanized_time'] = humanize.naturaltime(
        delorean.Delorean().datetime - t.datetime)
    return tweet


@app.route('/')
def index():
    q = domain_date_histogram(top_domains(top_hashtags(function_score(
        base_query()))))

    ctx = {'query': q, 'tags': None}

    tag = request.args.get('tag', None)
    if tag:
        # add filter for selected hashtag
        ctx['selected_tag'] = tag
        f = q['query']['function_score']['query']['filtered']['filter']
        f['bool']['must'].append({'term': {
            'entities.hashtags.text': tag}})

    domain = request.args.get('domain', None)
    if domain:
        # add filter for selected domain
        ctx['selected_domain'] = domain
        f = q['query']['function_score']['query']['filtered']['filter']
        f['bool']['must'].append({'term': {
            'entities.urls.domain': domain}})

    result = es.search(app.config['ES_INDEX'], body=q)
    ctx['result'] = result

    tweets = [hit['_source'] for hit in result['hits']['hits']]
    ctx['tweets'] = [humanize_tweet_published(tweet)
                     for tweet in tweets]

    date_hist_buckets = []
    for bucket in result['aggregations']['date_hist']['buckets']:
        t = delorean.parse(bucket['key_as_string'])
        d = {
            'key': t.shift('Europe/Berlin').datetime.strftime(
                '%Y-%m-%d %H:00'),
        }

        for subbucket in bucket['domains']['buckets']:
            k = subbucket['key'].replace('.', '')
            d[k] = subbucket['doc_count']

        date_hist_buckets.append(d)

    ctx['date_hist_buckets'] = date_hist_buckets

    return render_template('index.html', **ctx)


@app.route('/grouped')
def grouped(groupkey=None):
    q = group_by_domain(function_score(base_query()))
    q['size'] = 0

    result = es.search(app.config['ES_INDEX'], body=q)

    buckets = []
    for raw_bucket in result['aggregations']['top_news']['buckets']:
        hits = raw_bucket['top_tweets']['hits']['hits']
        bucket = {'name': raw_bucket['key'],
                  'doc_count': raw_bucket['doc_count'],
                  'tweets': [humanize_tweet_published(hit['_source'])
                             for hit in hits]}

        buckets.append(bucket)

    return render_template('grouped.html', groups=buckets, result=result,
                           query=q)


def run():
    app.run(host=app.config['FE_HOST'], port=app.config['FE_PORT'])
