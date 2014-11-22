# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2014 Daniel Truemper <truemped at googlemail.com>
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
from __future__ import (absolute_import, division, print_function,
                        with_statement)

from elasticsearch import Elasticsearch
from twython import TwythonStreamer


class StreamingIndexer(TwythonStreamer):

    def __init__(self, consumer_key=None, consumer_secret=None,
                 access_token=None, access_token_secret=None,
                 es_host=None, es_port=None, es_index=None):

        super(StreamingIndexer, self).__init__(consumer_key, consumer_secret,
                                               access_token,
                                               access_token_secret)

        self._es = Elasticsearch([{'host': es_host, 'port': es_port}])
        self._index = es_index

    def on_success(self, tweet):
        if 'delete' in tweet:
            status_id = tweet['delete']['status']['id']
            self._es.delete(self._index, 'tweet', status_id)
            return

        if 'retweeted_status' in tweet:
            tweet = tweet['retweeted_status']

        for url in tweet['entities']['urls']:
            if 'theguardian.com' in url['expanded_url']:
                url['domain'] = 'theguardian.com'

        self._es.index(index=self._index, doc_type='tweet',
                       id=tweet['id_str'], body=tweet)


_OPT = """Usage: streamer (-t TRACK)... [-u ES_HOST] [-p ES_PORT] [-i ES_INDEX]

Options:

    -t TRACK --track=TRACK                      track keyword

Elasticsearch Options:

    -u ES_HOST --es-host=ES_HOST    Hostname    [default: localhost]
    -p ES_PORT --es-port=ES_PORT    Port        [default: 9200]
    -i ES_INDEX --es-index=ES_INDEX Index name  [default: news-tweets]
    """


def streamer():

    from newsaggregator.config import (CONSUMER_KEY, CONSUMER_SECRET,
                                       ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                                       ES_HOST, ES_PORT, ES_INDEX)

    opts = {
        'consumer_key': CONSUMER_KEY,
        'consumer_secret': CONSUMER_SECRET,
        'access_token': ACCESS_TOKEN,
        'access_token_secret': ACCESS_TOKEN_SECRET,
        'es_host': ES_HOST,
        'es_port': ES_PORT,
        'es_index': ES_INDEX
    }

    from docopt import docopt
    arguments = dict([(k[2:].replace('-', '_'), v)
                      for (k, v) in docopt(_OPT, version='1.0').iteritems()])

    opts.update(dict([(k, v) for (k, v) in arguments.iteritems()
                      if k in opts]))

    stream = StreamingIndexer(**opts)
    stream.statuses.filter(track=','.join(arguments['track']))
