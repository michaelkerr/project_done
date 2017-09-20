# -*- coding: utf-8 -*-

from datetime import datetime
import json
from pprint import pprint
from sys import exit

data_file = "data.json"

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
            'key': epic['key'],
            'start': '',
            'done': '',
            'metics': {}
            }

        #TODO FIND EPIC START Date

        epic_start = datetime.strptime(str(epic['start'][0]), "%Y-%m-%d")

        if len(epic['start']) > 1:
            for start_date in epic['start']:
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
                if start_date < epic_start:
                     epic_start = datetime.strptime(str(start_date), "%Y-%m-%d")
        try:
            epic_done = datetime.strptime(str(epic['done'][0]), "%Y-%m-%d")
        except Exception as e:
            print # coding=utf-8
            pprint(epic['done'])
            exit()

        if len(epic['done']) > 1:
            for done_date in epic['done']:
                done_date = datetime.strptime(str(done_date), "%Y-%m-%d")
                if done_date < epic_done:
                    epic_done = datetime.strptime(str(done_date), "%Y-%m-%d")
        print epic_start.strftime("%Y-%m-%d") + ' to ' + epic_done.strftime("%Y-%m-%d")

        #TODO FIND DONE
        #TODO FOR EACH ISSUE
        #TODO FOR EACH ISSUE, USE THE FIRST "DONE" DATE
        #TODO CALCULATE BASIC METRIC (ISSUES/DAY)
