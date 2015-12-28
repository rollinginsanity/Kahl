#Getting the configuration objects
import configparser
from misc_helpers import giveMeBool

config = configparser.ConfigParser()

config.read('config.ini')

ServerBindIP = config['server']['ServerBindIP']
DebugMode = giveMeBool(config['server']['DebugMode'])
ListenPort = int(config['server']['ListenPort'])

from app import app
app.run(host=ServerBindIP, debug=DebugMode, port=ListenPort)
