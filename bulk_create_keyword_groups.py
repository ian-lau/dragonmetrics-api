import requests
import base64
import json
import csv

username = '' # Your API username
password = '' # Your API password
target_campaigns = [] # List of campaigns you wish to create keyowrd groups for
keyword_groups = 'bulk_create_keyword_groups_template.csv' # Your new keyword groups

credentials = base64.b64encode(bytes(username+':'+password, 'utf-8')).decode('utf-8')
headers = {'Accept': 'application/json','Authorization': 'Basic '+credentials,'Content-Type': 'application/json'}

url = 'https://api.dragonmetrics.com/v1.3/campaigns?limit=50&start=0'
r = requests.get(url, headers=headers)
r_json = r.json()

campaigns = []

for campaign in r_json['results']:
	campaigns.append({'id': campaign['id'],'name': campaign['name']})
	print('Campaigns count: '+str(len(campaigns)))
	while r_json['paging']['next'] is not None:
		url = r_json['paging']['next']
		r = requests.get(url, headers=headers)
		r_json = r.json()
		for campaign in r_json['results']:
			campaigns.append({'id': campaign['id'],'name': campaign['name']})
			print('Campaigns count: '+str(len(campaigns)))

for campaign in campaigns:
	for target_campaign in target_campaigns:
		if campaign['name'] == target_campaign:
			print('Campaign found')
			url = 'https://api.dragonmetrics.com/v1.3/campaigns/'+str(campaign['id'])+'/keyword_groups'
			reader = csv.DictReader(open(keyword_groups, 'r'))
			for row in reader:
				row['search_engines'] = row['search_engines'].replace(' ','').split(",")
				row['competitors'] = row['competitors'].replace(' ','').split(",")
				r = requests.post(url, data=json.dumps(row), headers=headers)
				print(r.json())
