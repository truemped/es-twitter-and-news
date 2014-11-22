# Simple twitter news aggregator

This is the code for my talk at the 2014 DevFest in Berlin. It basically
consists of two parts: indexing tweets from twitter and rendering a simple
website with the most insteresting news.


## Prerequesite

This project uses buildout. To get started simply call::

    $ python bootstrap.py
    $ bin/buildout

This will download all dependencies and create the executables in *bin/*.


## Configuration

Get your API credentials from Twitter and edit the values in
*newsaggregator/config.py*. The ES connection and index details can also be
configured there.


## Index Tweets

Right now the script supports simple tracking of keywords::

    $ bin/streamer -t 'theguardian com' -t 'wired com'

This will start a process that connects to the Twitter streaming API and index
tweets in the configured ES index.


## Frontend

To start the frontend simple run::

    $ bin/frontend

This will start a simple [Flask](http://flask.pocoo.org/) web app. The queries
used to create the page are defined in *newsaggregator/query.py*.
