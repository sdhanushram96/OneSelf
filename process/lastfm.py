import sys
import datetime
import json
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from utils import loadConfig
import utils
import generator

ENUMERATE = False

config = loadConfig.getConfig()

try:
    json_data = utils.load_record_json('lastfm-data.json')
except:
    print('Make sure you\'ve synced or exported your Nomie data')
    sys.exit()

songs_recorded = len(json_data['data'])
print("Songs recorded: {0}".format(songs_recorded))

# Now generate HTML report
parts = [
        ['header', ['Last.fm Report']],
        ['big_num', ['Songs recorded', songs_recorded]]
        ]
generator.build_report('lastfm_main', parts)
