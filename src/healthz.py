"""
We create a simple Flask app for a health check on the script. If healthy, it will return simply "OK".
"""

from flask import Flask
app = Flask(__name__)


@app.route('/healthz')
def healthz():
    return "OK"
