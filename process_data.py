# -*- coding: utf-8 -*-

from datetime import datetime
import json
import numpy as np
from pprint import pprint
from sys import exit

data_file = "data.json"
processed_file = "processed.json"


def get_date(issue):
    #TODO
    return


def get_duration(start_date, end_date):
    return (end_date - start_date).days


def duration_list(data):
    numbers = []
    for entry in data:
        numbers.append(entry['metrics']['duration'])
    return numbers


def moving_average(data, n=3) :
    ret = np.cumsum(data, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def sort_done(data):
    data_dict = {}
    for entry in data:
        data_dict[entry['done']] = entry['metrics']['duration']
    return data_dict



### MAIN ###
if __name__ == '__main__':
    #GET THE FEATURE DATA
    try:
        with open(data_file, 'r') as infile:
            epic_data = json.load(infile)
    except Exception as e:
        print e

    processed_data = []

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
        # Add the delivery dates of the issues, correct Epic start/end if req'd
        ##################################################
        epic_dict['issues'] = epic['issues']
        for issue in epic_dict['issues']:
            epic_dict['delivery'].append(datetime.strptime(str(issue['done'][0]), "%Y-%m-%d"))

            # If the delivery date is before the epic start, update epic_dict['start']
            if get_duration(epic_dict['start'], datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")) < 0:
                epic_dict['start'] = datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")

            # If the delivery date is after the epic end, update epic_dict['done']
            if get_duration(datetime.strptime(str(issue['done'][0]), "%Y-%m-%d"), epic_dict['done']) < 0:
                epic_dict['done'] = datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")

        # Sort the delivery list in order of completion
        epic_dict['delivery'] = sorted(epic_dict['delivery'], key=lambda x: x)

        ##################################################
        # Get the Duration of the feature (EPIC)
        ##################################################
        epic_dict['metrics']['duration'] = get_duration(epic_dict['start'], epic_dict['done'])

        # Add the data
        if len(epic_dict['delivery']) > 0:
            processed_data.append(epic_dict)

    ##################################################
    # "Takt" delivery time
    # TODO Move this into the first loop since its per epic????
    ##################################################
    temp_list = []

    for epic in processed_data:
        takt_list = []
        start_date = epic['start']
        last = 0

        for done_date in sorted(epic['delivery'], key=lambda x: x):
            duration = get_duration(start_date, done_date)
            if duration == 0:
                duration = last
            start_date = done_date
            last = duration
            takt_list.append(duration)

        epic['metrics']['takt'] = takt_list
        temp_list.append(epic)

    processed_data = temp_list

    ##################################################
    # Epic Macro Metrics
    ##################################################
    epic_metrics = {}

    #Average (days/feature)
    #epic_metrics['average'] = average_duration(processed_data)
    epic_metrics['epic_average'] = np.average(duration_list(processed_data))
    #print str(int(epic_metrics['average'])) + ' days/feature.'

    # Median
    #epic_metrics['median'] = median_duration(processed_data)
    epic_metrics['epic_median'] = np.median(duration_list(processed_data))

    # Std Deviation
    epic_metrics['epicstd_dev'] = np.std(duration_list(processed_data))


    ##################################################
    # TODO Rolling Average (days)
    # NEED TO SORT PROCESSED_DATA BY DELIVERY DATE
    ##################################################
    #pprint(sort_done(processed_data))
    #print moving_average(processed_data)


    ##################################################
    # TODO Running average of # Features in Progress
    ##################################################



    # Remove the issues.....
    temp_list = []
    for epic in processed_data:
        epic.pop('issues')
        temp_list.append(epic)

    processed_data = temp_list
    pprint(processed_data)

    #pprint(processed_data)
    pprint(epic_metrics)


'''
    with open(processed_file, 'w') as outfile:
        json.dump(epic_dict, outfile)
'''
