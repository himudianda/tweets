import os
import json

server = "http://localhost:9200"
num_tweets = 250
mapbox_accessToken = "****"

conf_file = os.environ.get('CONF_PATH', '/etc/tweets.conf')
if os.path.exists(conf_file):
    with open(conf_file, 'rb') as f:
        conf = json.load(f)
        server = conf.get('server', server)
        num_tweets = conf.get('num_tweets', num_tweets)
        mapbox_accessToken = conf.get('mapbox_accessToken', mapbox_accessToken)
