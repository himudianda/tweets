from flask import Flask, jsonify, make_response, render_template
from admin.tweets_api.blueprint import tweets as tweets_blueprint
from admin.settings import mapbox_accessToken

# Creating a new application
app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify(dict(error=error.name, code=error.code, description=error.description)),
        error.code
    )


# curl -i http://localhost:3000/
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', mapbox_accessToken=mapbox_accessToken)


# Register Blueprints
app.register_blueprint(tweets_blueprint)


def run_debug(host=None, debug=True, user=None, port=3000):
    app.debug = debug
    app.run(host=host, port=port)
