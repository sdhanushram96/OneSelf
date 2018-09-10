import sys
import datetime
import json
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from utils import loadConfig
import utils

ENUMERATE = False

config = loadConfig.getConfig()

try:
    json_data = utils.load_record_json('nomie-backup.nomie.json')
except:
    print('Make sure you\'ve synced or exported your Nomie data')
    sys.exit()

trackers = json_data['trackers'] # Main keys: charge, config->uom, label, math (mean, etc.)

TRACKER_ID_TO_NAME = {}
for i in trackers:
    TRACKER_ID_TO_NAME[i['_id']] = i['label']

raw_events = json_data['events']

def tracker_id_to_name(id):
    try:
        return TRACKER_ID_TO_NAME[id]
    except:
        return None

def process_events(raw_events):
    to_return = []
    for i in raw_events:
        to_yield = {
                'tracker_id': i['parent'],
                'time': i['time']
                }
        try:
            to_yield['value'] = i['value']
        except:
            pass
        try:
            to_yield['geo'] = i['geo']
        except:
            pass
        # yield to_yield
        to_return += [to_yield]
    return to_return

events = process_events(raw_events)


def pretty_print_trackers():
    global trackers
    for i in trackers:
        try:
            if not i['config']['uom'] == None:
                print(i['label'], 'with type', i['config']['uom'])
            else:
                print(i['label'], 'with no defined type')
        except KeyError as e:
            print(i['label'])

if ENUMERATE:
    pretty_print_trackers()

def highest_trackers_used():
    global events, trackers, TRACKER_ID_TO_NAME
    tracker_map = {}
    for i in events:
        try:
            tracker_map[i['tracker_id']] += 1
        except:
            tracker_map[i['tracker_id']] = 1
    hit_list = []
    for i in tracker_map.keys():
        try:
            hit_list += [ [TRACKER_ID_TO_NAME[i], tracker_map[i]] ]
        except KeyError as e:
            pass # Tracker no longer exists
    return sorted(hit_list, key=lambda x: x[1], reverse=True)

def overview_report():
    tracker_counts = highest_trackers_used()
    print('Your most used trackers by count where {0}, {1}, {2}, {3} and {4}'.format(
        tracker_counts[0][0],
        tracker_counts[1][0],
        tracker_counts[2][0],
        tracker_counts[3][0],
        tracker_counts[4][0]
        ))

def recent_changes_report():
    global events, trackers, TRACKER_ID_TO_NAME
    water_average = 0
    average = {}
    average['Water'] = 0
    current_day = ''
    recent_days = {}
    recent_days['Water'] = {}
    average_pre = {}
    average_pre['Water'] = 0
    late_days = {}
    late_days['Water'] = {}
    good_values = {
            'Water': 3.0 # 3 quarts
            }
    # Compatible trackers, Water in Ounces
    for i in events:
        # Water work
        for j in ['Water']:
            if tracker_id_to_name(i['tracker_id']) == j:
                log_time = i['time']
                date = utils.timestamp_to_datetime(log_time, True)
                day_id = utils.day_to_id(date)
                val = int(i['value'])
                if utils.is_within_days(date, 7):
                    try:
                        recent_days[j][day_id] += val
                    except:
                        recent_days[j][day_id] = val
                else:
                    try:
                        late_days[j][day_id] += val
                    except:
                        late_days[j][day_id] = val
    # Water
    for j in ['Water']:
        length = len(recent_days[j].keys())
        for i in recent_days[j].keys():
            average[j] += recent_days[j][i]
        if length > 0:
            average[j] /= length
        fraction_off_perfection = average[j] / good_values[j]
        if (fraction_off_perfection < 0.8):
            print('WARNING: ', j, 'is just', fraction_off_perfection*100, '% of recommendation this week')
        length = len(late_days[j].keys())
        for i in late_days[j].keys():
            average_pre[j] += late_days[j][i]
        if length > 0:
            average_pre[j] /= length
        print(j, 'recent average: ', average[j])
        print(j, 'previous average: ', average_pre[j])
    pass

# Now Show Report
overview_report()
recent_changes_report()
