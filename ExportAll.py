#!/usr/bin/python3

import urllib3
import sys
import os
import subprocess
import glob
import io
urllib3.disable_warnings()
from redcap import Project, RedcapError
from requests import post
from pathlib import Path
import smtplib
import datetime
import pycurl
import certifi
import json
import argparse


parser = argparse.ArgumentParser(description='RedCap REST client')
parser.add_argument('records_of_interest', metavar='ID', type=str, nargs='+',
                    help='a list of subject IDs to fetch metadata from')
parser.add_argument('--all', dest='export_disabled', action='store_const',
                    const=True, default=False,
                    help='export all subject sessions even when marked as disabled (default: exclude disabled)')

args = parser.parse_args()

records_of_interest = args.records_of_interest
outfile_name = (records_of_interest[0] if 1 == len(records_of_interest) else "subjects_metadata") + ".json"

fields_of_interest = [
    'participationid', 
    'scan_validation', 
    'scan_req_ack',
    'baby_ga_at_birth_weeks', 
    'baby_gender', 
    'baby_birth_weight', 
    'baby_babyhc', 
    'baby_baby_length',
    'fscan_ga_at_scan_weeks', 
    'scan_disabled',
    'nscan_ga_at_scan_weeks', 
    'nscan_age_at_scan_days',
    'xscan_baby_weight', 
    'xscan_head_circumference',
    'xscan_baby_length', 
    'xscan_baby_skin_fold'
]

events_of_interest = [
    'fetal_scan_arm_1', 
    'neonatal_scan_arm_1',
    'baby_born_arm_1'
]

# fetch API key from ~/.redcap-key ... don't keep in the source
key_filename = os.path.expanduser('~') + '/.redcap-key'
if not os.path.isfile(key_filename):
    print('redcap key file {} not found'.format(key_filename))
    sys.exit(1)
api_key = open(key_filename, 'r').read().strip()

# print(records_of_interest, fields_of_interest)

fields = {
    'content': 'arm',
    'format': 'json'
}
fields['token'] = api_key

api_url = 'https://externalredcap.isd.kcl.ac.uk/api/'
project = Project(api_url, api_key)


# get data for this participant
data = project.export_records(records=records_of_interest,
                              fields=fields_of_interest,
                              events=events_of_interest,
                              format='json')

# output is a list of do dictionaries where each dictionary corresponds to 
# a baby_born, fetal_scan or neonatal_scan event

# each field of interest will appera in every dictionary so we've got a lot 
# of nulls.  We'd also like to fix some of the naming so it's common betweem 
# fetal and neonatal scans

baby_born = {}
data_strip = [] # new container for stripped down list of dictionaries

for event in data:
    event_strip = {}
         
    for key, value in event.items():
        if value != "":

            key = key.replace("fscan", "scan")
            key = key.replace("nscan", "scan")
            key = key.replace("xscan", "scan")
            if key == 'baby_gender':
                if value == '1':
                    value = "M"
                elif value == '2':
                    value = "F"
           
            event_strip[key] = value

    if args.export_disabled or ('scan_disabled' not in event_strip.keys()):
      data_strip.append(event_strip)

# now pop the baby born event out
for idx, event in enumerate(data_strip):
    if event['redcap_event_name'] == 'baby_born_arm_1':
        baby_born = data_strip.pop(idx)

# now get the event name out of baby_born so it doesn't override
baby_born.pop('redcap_event_name', None)

for event in data_strip:
    event.update(baby_born)


with open(outfile_name, 'w') as outfile:
	json.dump(data_strip,outfile)
