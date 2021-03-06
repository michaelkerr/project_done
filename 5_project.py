# -*- coding: utf-8 -*-
import csv
from datetime import datetime
import json
from os import path
from pprint import pprint
import requests
from sys import exit
from urllib import urlencode
import yaml


### CONFIGURATION ###
config_file = path.join(path.dirname(path.realpath(__file__)), 'config/config.yml')
if path.exists(config_file):
    config = yaml.load(open(config_file, 'r'))
else:
    print config_file + ' not found'
    exit()

server = config['server']
credentials = {'uname': config['username'], 'pword': config['password']}
api_url = server + 'api/latest/'
search_url = api_url + 'search?'

headers = {'content-type': 'application/json;charset=UTF-8'}

#TODO get this from command line or comnfig file
project = 'ID'

in_file = "data_4.json"
metric_file = "data_metrics.json"
history = "database.json"
today = datetime.now()
out_file = '%s-%s-%s_project.json' % (today.year, today.month, today.day)
csv_file = '%s-%s-%s_project.csv' % (today.year, today.month, today.day)


def get_changelog(creds, url, issue_key):
    query_url = url + 'issue/' + issue_key + '/changelog'
    try:
        response = requests.get(query_url, headers=headers, auth=(creds['uname'], creds['pword']))
        return response.json()
    except Exception as e:
        print e
        exit()


def search_issues(creds, url, data):
    params = {
        'jql': data,
        'maxResults': 250
        }

    try:
        response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)
        return response.json()
    except Exception as e:
        print e
        exit()


### MAIN ###
if __name__ == '__main__':
    ##################################################
    # Get the generated metrics
    ##################################################
    try:
        with open(in_file, 'r') as infile:
            data = json.load(infile)
    except Exception as e:
        print e
        exit()

    ##################################################
    # Get the calculated metrics
    ##################################################
    try:
        with open(metric_file, 'r') as infile:
            metrics = json.load(infile)
    except Exception as e:
        print e
        exit()


    ##################################################
    # LOAD EXISTING DATA FROM THE "DATABASE"
    ##################################################
    try:
        with open(history, 'r') as infile:
            historic_data = json.load(infile)
    except Exception as e:
        historic_data = []

    existing_epics = []
    for issue in historic_data:
        existing_epics.append(issue['key'])


    # TODO Adapt for the z Curve

    # TODO Get the Statuses for the project
    # TODO TEMP = HARDCODED
    statuses = {
        'Backlog': {
                'type': 'To Do',
                'epics': []
            },
        'Not Started': {
                'type': 'To Do',
                'epics': []
            },
        'In Progress': {
                'type': 'In Progress',
                'epics': []
            },
        'At Risk': {
                'type': 'In Progress',
                'epics': []
            },
        'Late-Blocked': {
                'type': 'In Progress',
                'epics': []
            },
        'Blocked': {
                'type': 'In Progress',
                'epics': []
            }
    }

    status_map = {
        'Backlog': 'To Do',
        'Selected for Development': 'To Do',
        'In Progress': 'In Progress',
        'PR Review': 'In Progress',
        'Manual Review': 'In Progress',
        'Passed': 'In Progress',
        'Done': 'Done'
    }

    epic_forecasts = []

    # Get All Epics that arent Done
    for status, value in statuses.iteritems():
        epic_search_data = 'project = %s AND issuetype = Epic AND status = "%s"' % (project, status)
        epics = search_issues(credentials, search_url, epic_search_data)
        print "Getting %s Epics" % (status)
        if epics['total'] > 0:
            for epic in epics['issues']:

                epic_info = {'key': epic['key'],
                    'summary': epic['fields']['summary'],
                    'status': epic['fields']['status']['name'],
                    'release': epic['fields']['fixVersions'][0]['name'],
                    'target date': epic['fields']['customfield_11503']
                    }

                #statuses[status]['epics'] = info
                statuses[status]['epics'].append(epic_info)

    # Calculate the expected duration of the epic
    for status, value in statuses.iteritems():
        for epic in value['epics']:
            issue_search_data = 'issuetype not in (Bug, "Design Task") AND "Epic Link" = "%s"' % epic['key']
            issues = search_issues(credentials, search_url, issue_search_data)

            epic_issues = []

            for issue in issues['issues']:
                issue_status = status_map[issue['fields']['status']['name']]
                print '.',
                #pprint(issue.keys())
                #pprint(issue['target date'] + 2)
                #exit()

                if issue_status != 'Done':
                    if issue_status == 'To Do':
                        # Use the Average
                        remaining = metrics['meta_average']
                        #print round(metrics['meta_average'], 2)

                    elif issue_status == 'In Progress':
                        changelog = get_changelog(credentials, api_url, issue['key'])
                        for entry in changelog['values']:
                            for item in entry['items']:
                                if item['field'] == 'status' and item['toString'] == 'In Progress':
                                    issue_start = datetime.strptime(entry['created'].split('T')[0], "%Y-%m-%d")
                        # Now ;-)
                        now = datetime.now()
                        diff = metrics['meta_average'] - float((now - issue_start).days)

                        # If the elapsed work time > average, use 2x the mode
                        if diff < 0:
                            remaining = 2 * metrics['meta_mode']

                        else:
                            remaining = diff
                            # TODO If it exceeds the 85th Percentile
                            #if (metrics['meta_85th'] - float((now - issue_start).days)) < 0:
                            #    print '85th'
                            #else:
                            #    print 'Mode'
                        #print issue_status

                else:
                    remaining = 0

                epic_issues.append(remaining)
                #print str(round(sum(epic_issues), 0)) + " days."

            epic['estimate'] = round(sum(epic_issues), 0)
            epic_forecasts.append(epic)

            #epic_forecasts[epic] = round(sum(epic_issues), 0)

    for epic in epic_forecasts:
        print '%s, %s' % (epic['key'], epic['estimate'])
        #TODO Calculate the dates

    print today

    # Write to json
    with open(out_file, 'w') as outfile:
        json.dump(epic_forecasts, outfile)

    # Write to csv`
    with open(csv_file, 'wb') as f:
        fieldnames = epic_forecasts[0].keys()
        csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
        csvwriter.writeheader()

        for row in epic_forecasts:
            csvwriter.writerow(row)

        #csvwriter = csv.DictWriter(f, epic_forecasts.keys())
        #csvwriter.writeheader()
        #csvwriter.writerow(epic_forecasts)
"""
Input format:
{
	"p(t)": [0.12396694214876033, 0.256198347107438, 0.1115702479338843, ...0.008264462809917356],
	"days": [0, 1, 2, ...131],
	"time": [30, 62, 27, ...2]
}

Output Format 1:
[{
	"status": "In Progress",
	"target date": "2017-10-15",
	"summary": "Device Linking",
	"key": "ID-2295",
	"release": "S2 Platform",
	"estimate": 9.0
}, {
	"status": "In Progress",
	"target date": "2017-11-05",
	"summary": "Profile Redesign (Reveal)",
	"key": "ID-2080",
	"release": "December Reveal",
	"estimate": 37.0
},
...
...
...
]

Output Format 2:
status,target date,summary,key,release,estimate
In Progress,2017-10-15,Device Linking,ID-2295,S2 Platform,9.0
In Progress,2017-11-05,Profile Redesign (Reveal),ID-2080,December Reveal,37.0
...
...
...

"""
