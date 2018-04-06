import requests
import base64
import json
import csv

username = '' # Your API username
password = '' # Your API password
campaigns = 'bulk_create_campaigns_template.csv' ### Your new campaigns

credentials = base64.b64encode(bytes(username+':'+password, 'utf-8')).decode('utf-8')
headers = {'Accept': 'application/json','Authorization': 'Basic '+credentials,'Content-Type': 'application/json'}
url = 'https://api.dragonmetrics.com/v1.3/campaigns'
reader = csv.DictReader(open(campaigns, 'r'))
for row in reader:
	r = requests.post(url, data=json.dumps(row), headers=headers)
	print(r.json())
