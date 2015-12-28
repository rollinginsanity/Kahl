#Getting the configuration objects
import configparser
from misc_helpers import giveMeBool

#Using the exit function.
import sys

#Some vars set here for consistency (So I'm not filling this code with snowflake variables.)
config_file = "config.ini"    #Change at your own risk. If you want the config file somewhere else...
config_file_server_section = "server"

config = configparser.ConfigParser()

#validate the config file
print("Loading " + config_file)

try:
    check_config_file_exists = open(config_file)
except IOError as e:
    print("Missing " + config_file)
    print("Please create a config file.")
    print("See https://github.com/rollinginsanity/Kahl for more info.")
    print(e)
    sys.exit()


config.read(config_file)
if ("server" not in config.sections()):
    print("No [server] section defined in config file. Please create a valid config file (default config.ini).")
    print("See https://github.com/rollinginsanity/Kahl for more info.")
    sys.exit()

ServerBindIP = config[config_file_server_section]['ServerBindIP']
DebugMode = giveMeBool(config[config_file_server_section]['DebugMode'])
ListenPort = int(config[config_file_server_section]['ListenPort'])

from app import app
app.run(host=ServerBindIP, debug=DebugMode, port=ListenPort)
