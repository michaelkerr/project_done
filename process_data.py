# -*- coding: utf-8 -*-

from datetime import datetime
import json
import numpy as np
from pprint import pprint
from sys import exit

data_file = "data.json"
processed_file = "processed.json"


def average_duration(data):
    numbers = []
    for entry in data:
        numbers.append(entry['metrics']['duration'])

    return float(sum(numbers)) / max(len(numbers), 1)


def get_date(issue):
    #TODO
    return


def get_duration(data_dict):
    epic_duration = (data_dict['done'] - data_dict['start']).days
    if epic_duration > 0:
        return epic_duration
    else:
        return 0


def moving_average(data, n=3) :
    a= []

    for entry in data:
        a.append(entry['metrics']['duration'])

    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


### MAIN ###
if __name__ == '__main__':
    #GET THE FEATURE DATA
    try:
        with open(data_file, 'r') as infile:
            epic_data = json.load(infile)
    except Exception as e:
        print e

    processed_data = []

    epic_metrics = []
    #TODO FOR EACH EPIC
    for epic in epic_data:
        epic_dict = {
            'start': '',
            'done': '',
            'issues': [],
            'delivery': [],
            'metrics': {}
            }

        #TODO move to get_date()
        epic_start = datetime.strptime(str(epic['start'][0]), "%Y-%m-%d")

        if len(epic['start']) > 1:
            for start_date in epic['start']:
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
                if start_date < epic_start:
                    epic_start = datetime.strptime(str(start_date), "%Y-%m-%d")

        epic_dict['start'] = epic_start

        #TODO move to get_date()
        epic_done = datetime.strptime(str(epic['done'][0]), "%Y-%m-%d")

        if len(epic['done']) > 1:
            for done_date in epic['done']:
                done_date = datetime.strptime(str(done_date), "%Y-%m-%d")
                if done_date < epic_done:
                    epic_done = datetime.strptime(str(done_date), "%Y-%m-%d")

        epic_dict['done'] = epic_done

        ##################################################
        # Add the delivery dates of the issues
        ##################################################
        epic_dict['issues'] = epic['issues']
        for issue in epic_dict['issues']:
            epic_dict['delivery'].append(issue['done'][0])

        ##################################################
        # Get the Duration of the feature (EPIC)
        ##################################################
        epic_dict['metrics']['duration'] = get_duration(epic_dict)

        # Add the data
        if len(epic_dict['delivery']) > 0:
            processed_data.append(epic_dict)

    ##################################################
    # Average (days/feature)
    ##################################################
    print str(int(average_duration(processed_data))) + ' days/feature.'

    ##################################################
    # TODO Rolling Average (days)
    # NEED TO SORT PROCESSED_DATA BY DELIVERY DATE
    ##################################################
    #print moving_average(processed_data)

    #pprint(processed_data)

'''
    with open(processed_file, 'w') as outfile:
        json.dump(epic_dict, outfile)
'''
