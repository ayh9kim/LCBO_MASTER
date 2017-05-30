# -*- coding: utf-8 -*-
"""
Created on Mon May 22 17:44:42 2017

@author: ayh9k
"""

import urllib2
import json
import csv

req = urllib2.Request('https://lcboapi.com/datasets.csv')
req.add_header('Authorization', 'Token MDozNjBmYTA2NC0zZjM4LTExZTctOWM1OS1mZjVjOWJkMjk5Y2Y6Y0FlR2M4cjlsNEZTYnhkYVpGVFh5MEVNQmw2bmgwdU9STzdv')

#data = json.load(urllib2.urlopen(req))


cr = csv.reader(urllib2.urlopen(req))

path = 'D://Doc//Project//Blog//sup.csv'
csv_file = 'sup'

with open(path, "wb") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for row in cr:
        writer.writerow(row)

# This create csv file with CSV DUMP attribute, take the most recent update.
