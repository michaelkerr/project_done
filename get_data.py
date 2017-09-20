# -*- coding: utf-8 -*-

import json
import csv
from os import path
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth

from sys import exit
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
data_file = "data.json"


def search_issues(creds, url, data):
    params = {
        'jql': data,
        'expand': 'changelog',
        'maxResults': 250
        }

    try:
        req = requests.Request('GET', url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)
        prepared = req.prepare()

        #'''
        def pretty_print_POST(req):
            """
            At this point it is completely built and ready
            to be fired; it is "prepared".

            However pay attention at the formatting used in
            this function because it is programmed to be pretty
            printed and may differ from the actual request.
            """
            print('{}\n{}\n{}\n\n{}'.format(
                '-----------START-----------',
                req.method + ' ' + req.url,
                '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                req.body,
            ))

        pretty_print_POST(prepared)

        exit()
        #'''
        #url = 'https://magicleap.atlassian.net/rest/api/latest/issue/ID-1918'

        response = requests.Session()
        print response.send(prepared)

        #response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)
        return response.json()
    except Exception as e:
        print e
        exit()


def get_changelog(creds, url, issue_key):
    query_url = url + 'issue/' + issue_key + '/changelog'
    try:
        response = requests.get(query_url, headers=headers, auth=(creds['uname'], creds['pword']))
        return response.json()
    except Exception as e:
        print e
        exit()



### MAIN ###
if __name__ == '__main__':
    #TODO Get the Project ID

    ##################################################
    # LOAD EXISTING DATA FROM DATA.json
    ##################################################
    try:
        with open(data_file, 'r') as infile:
            epic_data = json.load(infile)
    except Exception as e:
        epic_data = []

    existing_epics = []
    for issue in epic_data:
        existing_epics.append(issue['key'])

    ##################################################
    # GET ALL THE COMPLETED EPICS IN THE PROJECT
    ##################################################
    epic_search_data = 'project = ID AND issuetype = "Epic" AND status = Done AND (Labels not in ("exclude") or labels is EMPTY)'
    print "Getting Epics....."


    epics = search_issues(credentials, search_url, epic_search_data)
    print "Done."
    exit()

    # FOR EACH EPIC (FEATURE)
    for epic in epics['issues']:
        ##################################################
        # FOR EACH EPIC - GET THE START DATE(S) [LIST], END DATE(S) [LIST]
        ##################################################
        if epic['key'] not in existing_epics:
            print "Processing Epic: " + str(epic['key'])

            #TODO hjandle updating of data

            changelog = get_changelog(credentials, api_url, epic['key'])

            epic_dates = {
                'key': epic['key'],
                'start': [],
                'done': [],
                'issues': []
                }

            for entry in changelog['values']:
                for item in entry['items']:
                    if item['field'] == 'status' and item['toString'] == 'In Progress':
                        epic_dates['start'].append(entry['created'].split('T')[0])
                    elif item['field'] == 'status' and item['toString'] == 'Done':
                        epic_dates['done'].append(entry['created'].split('T')[0])

            #TODO DONT ADD IF END DATE IS EMPTY

            if len(epic_dates['start']) != 0 and len(epic_dates['done']) !=0:
                ##################################################
                #GET THE LIST OF ALL THE ISSUES IN THE EPICS [TASKS, STORIES, ETC (NOT BUGS, DESIGN TASKS)]
                ##################################################
                issue_search_data = '"Epic Link" = %s and issuetype not in (Bug, "Design Task")' % (epic['key'])
                issues = search_issues(credentials, search_url, issue_search_data)

                ##################################################
                #FOR EACH ISSUE IN THE EPIC - GET THE DATES
                ##################################################
                issue_data = []
                print "Parsing issues"
                for issue in issues['issues']:
                    changelog = get_changelog(credentials, api_url, issue['key'])

                    issue_dates = {
                        'key': epic['key'],
                        'start': [],
                        'done': []
                        }

                    for entry in changelog['values']:
                        for item in entry['items']:
                            if item['field'] == 'status' and item['toString'] == 'In Progress':
                                issue_dates['start'].append(entry['created'].split('T')[0])
                            elif item['field'] == 'status' and item['toString'] == 'Done':
                                issue_dates['done'].append(entry['created'].split('T')[0])

                    #ADD THE ISSUE DATES TO THE EPIC ISSUE LIST
                    if len(issue_dates['start']) != 0:
                        epic_dates['issues'].append(issue_dates)
                    if issue_dates['start'] == 0:
                        print issue_dates['key']

                epic_data.append(epic_dates)
                pprint(epic_dates)
            else:
                print "No staert date.  Skipping"

    pprint(epic_data)
    #TODO FEATURE START, FEATURE END, [ISSUE END DATES]
    #TODO

    with open(data_file, 'w') as outfile:
        json.dump(epic_data, outfile)
