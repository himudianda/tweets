from flask import Flask

# Creating a new application
app = Flask(__name__)


# curl -i http://localhost:5000/
@app.route('/', methods=['GET'])
def index():
    return "Web App"


def run_debug(host=None, debug=True, user=None, port=3000):
    app.debug = debug
    app.run(host=host, port=port)
