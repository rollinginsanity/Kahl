#Some of the logic for the server.
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Does it work?"
