import requests
import base64
import pandas as pd
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# nltk.download('stopwords')
# nltk.download('punkt')

username = '' # API user name goes here
password = '' # API password goes here
target_campaign = '' # Campaign name goes here
tags_to_add = 20 # Number of tags to add

credentials = base64.b64encode(bytes(username+':'+password, 'utf-8')).decode('utf-8')
headers = {'Accept': 'application/json','Authorization': 'Basic '+credentials,'Content-Type': 'application/json'}

url = 'https://api.dragonmetrics.com/v1.3/campaigns?limit=50&start=0'
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

bag_of_words = ''
keyword_list = []

for campaign in campaigns:
	if campaign['name'] == target_campaign:
		print('Campaign "'+target_campaign+'" found, getting keywords...')
		global target_campaign_id
		target_campaign_id = campaign['id']
		url = 'https://api.dragonmetrics.com/v1.3/campaigns/'+str(target_campaign_id)+'/keywords?start=0&limit=50'
		r = requests.get(url, headers=headers)
		r_json = r.json()
		for keyword in r_json['results']:
			keyword_list.append({'keyword':keyword['keyword'],'tags':keyword['tags']})
			bag_of_words = bag_of_words + ' ' + keyword['keyword']
		while r_json['paging']['next'] is not None:
			url = r_json['paging']['next']
			r = requests.get(url, headers=headers)
			r_json = r.json()
			for keyword in r_json['results']:
				keyword_list.append({'keyword':keyword['keyword'],'tags':keyword['tags']})
				bag_of_words = bag_of_words + ' ' + keyword['keyword']

print('Total keywords: '+str(len(keyword_list)))
print('Generating list of tags...')
stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(bag_of_words.lower())
 
filtered_sentence = [w for w in word_tokens if not w in stop_words]
 
for w in word_tokens:
    if w not in stop_words:
        filtered_sentence.append(w)

freq = {}
 
for word in filtered_sentence:
    count = freq.get(word,0)
    freq[word] = count + 1

df = pd.Series(freq).to_frame()
df = df.sort_values(by=0, ascending=False)

tags = df.head(tags_to_add).index.tolist()
print('The following tags will be created:')
print(tags)

for keyword in keyword_list:
	for tag in tags:
		if tag in keyword['keyword']:
			if tag not in keyword['tags']:
				keyword['tags'].append(tag)

print('Adding tags to your keywords...')
url = 'https://api.dragonmetrics.com/v1.3/campaigns/'+str(target_campaign_id)+'/keywords'
r = requests.put(url, data=json.dumps(keyword_list), headers=headers)
print('Done')
