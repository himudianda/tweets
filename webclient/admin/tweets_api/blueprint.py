from flask import Blueprint, abort, request, jsonify
import requests
import json
tweets = Blueprint("tweets", __name__, template_folder='../')
from admin.settings import server
from admin.settings import num_tweets

# curl -i -H "Content-Type: application/json" -X POST -d '{"lat":"37", "lng":"-122", "radius":"1000"}' http://localhost:3000/tweets/api/v1.0/coordinates
@tweets.route('/tweets/api/v1.0/coordinates', methods=['POST'])
def get_tweets_by_coordinates():
    if not request.json:
        abort(400)

    if 'lat' not in request.json:
        abort(400)

    if 'lng' not in request.json:
        abort(400)

    if 'radius' not in request.json:
        abort(400)

    lat = request.json.get('lat', None)
    lng = request.json.get('lng', None)
    radius = request.json.get('radius', None)
    hashtag = request.json.get('hashtag', None)

    data = {
        "query": {
            "filtered": {
                "filter": {}
            }
        },
        "sort": { "created_at": { "order": "desc" }},
        "from" : 0,
        "size" : num_tweets
    }


    if not hashtag:
        data['query']['filtered']['filter'] = {
            "geohash_cell": {
                "coordinates": {
                    "lat": float(lat),
                    "lon": float(lng)
                },
                "precision": radius+'km',
                "neighbors": True,
                "_cache": True,
            }
        }

    else:
        hashtag = hashtag[1:] if hashtag[0] == '#' else hashtag
        data['query']['filtered']['filter'] = {
            "bool" : {
              "must" : [
                { "term" : {"hashtags" : hashtag}},
                {
                    "geohash_cell": {
                        "coordinates": {
                            "lat": float(lat),
                            "lon": float(lng)
                        },
                        "precision": radius+'km',
                        "neighbors": True,
                        "_cache": True,
                    }
                }
              ]
           }
         }

    r = requests.get("%s/tweets/tweet/_search" % (server), data=json.dumps(data))

    features = list()
    for tweet in r.json()['hits']['hits']:

        if not tweet:
            continue

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": tweet['_source'].get('coordinates')
            },
            "properties": {
                "title": tweet['_source'].get("text", ""),
                "created_at": tweet['_source'].get("created_at")
            }
        }
        features.append(feature)

    response = dict(type="FeatureCollection", features=features)
    return jsonify(dict(data=response)), 200
