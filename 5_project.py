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

in_file = "generate.json"
metric_file = "metric.json"
out_file = "project.json"
csv_file = 'project.csv'


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
    # Get the generate metrics
    try:
        with open(in_file, 'r') as infile:
            data = json.load(infile)
    except Exception as e:
        print e
        exit()

    # Get the generate metrics
    try:
        with open(metric_file, 'r') as infile:
            metrics = json.load(infile)
    except Exception as e:
        print e
        exit()

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

    epic_forecasts = {}

    # Get All Epics that arent Done and all issues in them
    for status, value in statuses.iteritems():
        epic_search_data = 'project = ID AND issuetype = Epic AND status = "%s"' % status
        epics = search_issues(credentials, search_url, epic_search_data)
        print "Getting Epics in Status %s" % (status)
        if epics['total'] > 0:
            for epic in epics['issues']:
                statuses[status]['epics'].append(epic['key'])

    # TODO Calculate the expected duration of the epic
    for status, value in statuses.iteritems():
        for epic in value['epics']:
            print "Calculating for %s" % (epic)
            issue_search_data = 'issuetype not in (Bug, "Design Task") AND "Epic Link" = "%s"' % epic
            issues = search_issues(credentials, search_url, issue_search_data)

            epic_issues = []

            for issue in issues['issues']:
                issue_status = status_map[issue['fields']['status']['name']]
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

                        # If the elapsed work time > average, use 2x the mdoe
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

            epic_forecasts[epic] = round(sum(epic_issues), 0)

    pprint(epic_forecasts)

    # Write to json
    with open(out_file, 'w') as outfile:
        json.dump(epic_forecasts, outfile)


    # Write to csv
    my_dict = {"test": 1, "testing": 2}

    with open(csv_file, 'wb') as f:
        w = csv.DictWriter(f, epic_forecasts.keys())
        w.writeheader()
        w.writerow(epic_forecasts)
