import requests
import json
import csv
import re

# I used the Socrata Discovery API to get metadata for all datasets on NYCOpenData
# https://socratadiscovery.docs.apiary.io

# I'm interested in how well-documented NYC Open Datasets are, and whether this differs by agency

# This will likely be the beginning of my final project - just need to figure out pagination and how to do the calculations of the completeness of contextual metadata

base_url = "http://api.us.socrata.com/api/catalog/v1"

payload = {
'domains' : 'data.cityofnewyork.us',
'search_context' : 'data.cityofnewyork.us',
'limit' : 1000,
'offset' : 0
}

r = requests.get(base_url, params=payload)

datasets = json.loads(r.text)

html_tags = re.compile('<.*?>') 

print(r.text)

# pagination that will happen later..
# for large numbers of results Socrata recommends using deep scrolling via the scroll_id param
# the scroll_id needs to be the id of the last resource returned
# fetch the results and then append them to datasets

# I want to build a csv that tells me whether each dataset has:
# - a contact email
# - a description
# - what percent of its columns have a datatype listed
# - what percent of its columns have descriptions
# I want to include the agency that uploaded the dataset as well as the name of the dataset

with open('nycopen_metadata.csv', 'w', newline='') as csvfile:
	field_names = ['name', 'agency', 'description', 'contact', 'percent_datatypes', 'percent_descriptions']
	writer = csv.DictWriter(csvfile, fieldnames = field_names)

	writer.writeheader()

	for d in datasets['results']:
		current_dict = {}

		current_dict['name'] = d['resource']['name']

		for k in d['classification']['domain_metadata']:
			if k['key'] == 'Dataset-Information_Agency':
				current_dict['agency'] = k['value']

		#use regex to remove rogue html from the descriptions field

		current_dict['description'] = re.sub(html_tags, '', d['resource']['description'])

		current_dict['contact'] = d['resource']['contact_email']

		if not d['resource']['columns_datatype']:
			current_dict['percent_datatypes'] = 0

		else:
			denom = len(d['resource']['columns_datatype'])
			numer = 0
			for col in d['resource']['columns_datatype']:
				if len(col) > 0:
					numer = numer + 1
			current_dict['percent_datatypes'] = numer/denom

		if not d['resource']['columns_description']:
			current_dict['percent_descriptions'] = 0

		else:
			denom = len(d['resource']['columns_description'])
			numer = 0
			for col in d['resource']['columns_description']:
				if len(col) > 0:
					numer = numer + 1
			current_dict['percent_descriptions'] = numer/denom


		writer.writerow(current_dict)

