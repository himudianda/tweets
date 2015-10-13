import os
import json

# Twitter access credentials is stored on a separate config file
# on the server; the path to it can be set using the CONF_PATH envvar.
# Credentials should never be checked in to repo.
CONSUMER_KEY = "*****"
CONSUMER_SECRET = "*****"
ACCESS_TOKEN = "*****"
ACCESS_TOKEN_SECRET = "*****"

server = "http://localhost:9200"
world_bbox = '-180.00,-90.00,180.00,90.00'

conf_file = os.environ.get('CONF_PATH', '/etc/tweets.conf')
if os.path.exists(conf_file):
    with open(conf_file, 'rb') as f:
        conf = json.load(f)
        CONSUMER_KEY = conf.get('CONSUMER_KEY', CONSUMER_KEY)
        CONSUMER_SECRET = conf.get('CONSUMER_SECRET', CONSUMER_SECRET)
        ACCESS_TOKEN = conf.get('ACCESS_TOKEN', ACCESS_TOKEN)
        ACCESS_TOKEN_SECRET = conf.get('ACCESS_TOKEN_SECRET', ACCESS_TOKEN_SECRET)
        server = conf.get('server', server)
