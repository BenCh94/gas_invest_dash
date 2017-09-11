import requests
import json
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "accept-encoding": "gzip, deflate"
}
data = {
    "username": "bchadwick94",
    "password": "passw0rd",
    "appTypeID": "2000",
    "appVersion": "0.1",
    "languageID": "en_US",
    "osType": "Windows",
    "osVersion": "Windows 7",
    "scrRes": "1920x1080",
    "ipAddress": "95.45.253.58"
}
data = json.dumps(data)

print type(data)
r = requests.post("https://api.drivewealth.io/v1/userSessions", data=data, headers=headers)
print r.content
print r.json()
# 252dd22d-d46c-4167-9c70-d36dab067aec.2017-09-11T13:13:51.050Z
