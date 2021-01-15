#!/usr/bin/python
# Pi Hole data fetching as described by adafruit in...
# https://learn.adafruit.com/pi-hole-ad-blocker-with-pi-zero-w/install-pioled

import json
import requests
import time

api_url = 'http://192.168.1.172/admin/api.php'
while True:
	try:
		r = requests.get(api_url)
		data = json.loads(r.text)
		DNSQUERIES = data['dns_queries_today']
		ADSBLOCKED = data['ads_blocked_today']
		CLIENTS = data['unique_clients']
	except:
		time.sleep(1)
		continue
	print ("DNS queries=",DNSQUERIES, "ADs blocked=",ADSBLOCKED, "Clients=",CLIENTS)
	time.sleep(2)
	  
	  