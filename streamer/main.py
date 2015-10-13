from streamer import StreamClient
import requests
from requests.exceptions import ConnectionError
import json
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from settings import server, world_bbox
import time


class Worker(object):
    def __init__(self):
        self.client = StreamClient(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


    def __map_es_schema(self, server):
        """ 
            Creates ElasticSearch Mappings
            Note: geohash_precision is set to 1km. So, the minimum
            search radius is limited to 1km on the web app.
            This assumption however speeds up queries & saves on
            space required to index the geohashes.
         """
        data = dict(
            mappings = dict(
                tweet = dict(
                    properties = dict(
                        text = dict(type="string"),
                        coordinates = dict(type="geo_point", geohash_prefix=True, geohash_precision="1km"),
                        created_at = dict(type="date"),
                        hashtags = dict(type="string", index="not_analyzed")
                    )
                )
            )
        )
        try:
            r = requests.put(server+"/tweets", data=json.dumps(data))
        except ConnectionError:
            raise


    def __serialize_tweet(self, data):
        """
            Serailizes tweets to be stored in ElasticSearch
        """
        # Tweet Text
        text = data.get("text", None)

        # Tweet created_at serialize
        created_at = data.get("created_at", None)
        if not text or not created_at:
            return None
        created_at = time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y'))

        # Tweet Hashtags serialize
        hashtags = [ tag.get("text") for tag in data.get("entities").get("hashtags") ] if "entities" in data else []

        # Tweet coordinates serialize
        coordinates = data.get("coordinates", None)
        if not coordinates:
            place = data.get("place", None)
            if not place:
                return None

            place_bbox = place.get('bounding_box', None)
            if not place_bbox:
                return None

            place_coords = place_bbox['coordinates'][0]
            place_lng = (place_coords[0][0] + place_coords[2][0])/2
            place_lat = (place_coords[0][1] + place_coords[1][1])/2

            coordinates = [place_lng, place_lat]
        else:
            coordinates = coordinates['coordinates']

        # Serialized tweet ready to be indexed to ElasticSearch
        tweet = dict(text = text, coordinates = coordinates, created_at=created_at, hashtags=hashtags)
        return tweet


    def run(self):
        try:
            self.__map_es_schema(server)
        except ConnectionError as err:
            print err.message
            return

        # Index tweets from whole world
        locations = world_bbox
        resource = self.client.stream.statuses.filter.get(locations=locations)
        for data in resource.stream():
            tweet = self.__serialize_tweet(data)
            if not tweet:
                continue
            r = requests.post(server+"/tweets/tweet/", data=json.dumps(tweet))
            print r.text


if __name__ == "__main__":
    worker = Worker()
    worker.run()
