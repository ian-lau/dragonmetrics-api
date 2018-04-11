import requests
import base64
import json
from googletrans import Translator

username = '' # API user name goes here
password = '' # API password goes here
target_campaign = '' # Campaigns goes here

credentials = base64.b64encode(bytes(username+':'+password, 'utf-8')).decode('utf-8')
headers = {'Accept': 'application/json','Authorization': 'Basic '+credentials,'Content-Type': 'application/json'}

url = 'https://api.dragonmetrics.com/v1.3/campaigns?limit=500&start=0'
r = requests.get(url, headers=headers)
r_json = r.json()

campaigns = []

for campaign in r_json['results']:
	campaigns.append({
		'id': campaign['id'],
		'name': campaign['name']
		})
	print('Finding campaigns...')
	while r_json['paging']['next'] is not None:
		url = r_json['paging']['next']
		r = requests.get(url, headers=headers)
		r_json = r.json()
		for campaign in r_json['results']:
			campaigns.append({
				'id': campaign['id'],
				'name': campaign['name']
				})

keyword_list = []

for campaign in campaigns:
	if campaign['name'] == target_campaign:
		print('Campaign "'+target_campaign+'" found, getting keywords...')
		global target_campaign_id
		target_campaign_id = campaign['id']
		url = 'https://api.dragonmetrics.com/v1.3/campaigns/'+str(target_campaign_id)+'/keywords?start=0&limit=500'
		r = requests.get(url, headers=headers)
		r_json = r.json()
		for keyword in r_json['results']:
			keyword_list.append(keyword['keyword'])
		while r_json['paging']['next'] is not None:
			url = r_json['paging']['next']
			r = requests.get(url, headers=headers)
			r_json = r.json()
			for keyword in r_json['results']:
				keyword_list.append(keyword['keyword'])

print('Total keywords: '+str(len(keyword_list)))
print('Getting translations...')

def chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

translator = Translator()
translated_list = []
translations = []

for chunk in chunks(keyword_list,1000):
	translations = translator.translate(chunk)
	for i in translations:
		translated_list.append({'keyword':i.origin,'translation':i.text,})
	print('Transalting keywords... '+str(len(translated_list))+' keywords translated')

print('Translation completed.')

print('Adding translations to your keywords...')
url = 'https://api.dragonmetrics.com/v1.3/campaigns/'+str(target_campaign_id)+'/keywords'

for chunk in chunks(translated_list,100):
	r = requests.put(url, data=json.dumps(chunk), headers=headers)
	print(r.json())
	print('Updating keywords... '+str(len(chunk))+' keywords just got updated')

print('Done')
