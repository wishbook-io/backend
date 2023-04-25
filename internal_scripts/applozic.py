import requests
import json
import base64
applozic_credential = 'tech@wishbooks.io:sakambari5298'
applozic_credential = base64.b64encode(applozic_credential)

applicationId = 'wishbooks2162de324db40828f8c8a64186a03d3d7'

print "applozic (((((((((9"
print applozic_credential

APPLOZIC_HEADERS = {'Content-Type': 'application/json',
	'Apz-AppId': applicationId,
	'Apz-Token': 'Basic '+applozic_credential,
}

print "======================="

'''
#get profile
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/user/info?userIds=lalutyagi'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text
'''

'''
#register user
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/register/client'
payload = {
  "userId":"aks123",
  "deviceType":"1",
  "applicationId":applicationId,
  "contactNumber":"+919586773322"
}
r = requests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''

'''
#get user detail
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/user/detail?userIds=adminnistrator'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
#user update
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/user/update?ofUserId=lalutyagi'
payload = {
  "userId":"lalutyagi",
  "deviceType":"1",
  "applicationId":applicationId,
  "contactNumber":"+919586773322",
  "displayName":"lalutyagi"
}
r = requests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
#user exist?
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/user/exist?userId=admin'#lalutyagi'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text'''
'''
jsonr = json.load(r.text)
print jsonr['status']'''

'''
#Contact List
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/user/filter'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text
'''

'''
#send message
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/message/send?ofUserId=lalutyagi'
payload = {
  #"to":"aks123",
  "clientGroupId":"727744",
  "message":"Hi John",
}
r = requests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''

'''#send broadcast message
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/message/sendall?ofUserId=lalutyagi'
payload = {
  "userNames":["lalutyagi", "aks123"],
  "clientGroupIds":["728141", "727744", "372250"],
  "messageObject" : {
    "message":"broadcast message"
  }
}
r = requests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
#list of messages
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/message/list?ofUserId=aks123'
payload = {
  "startIndex":"0",
  "pageSize":"50"
}
r = requests.get(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''

'''
#create group
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/group/v2/create?ofUserId=aks123'
payload = {
  #"clientGroupId":"372351",
  "groupName":"wisbook-group1",
  "groupMemberList":["aks123","lalutyagi"]
  #"ofUserId":"lalutyagi",
  #"deviceType":"1",
  #"applicationId":applicationId
  
}
#"clientGroupId":"Client Group Id",
#"imageUrl": "http://images.wishbooks.io/__sized__/catalog_image/blob_bvKvHZM-thumbnail-150x210-100.jpg"
r = requests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
#group info
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/group/v2/info?groupId=372351'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
#add member to group
APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/group/add/member?clientGroupId=728141&userId=bbbbbb&ofUserId=aks123'
r = requests.get(APPLOZIC_URL, headers=APPLOZIC_HEADERS)
print r
print r.text
'''
'''
##sms
SMS_HEADERS = {'Content-type': 'Application/json',
    'X-Token': 'GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw=='
}
SMS_URL = 'https://iproapi.com/api/sms/sendotp'
smspayload = {"Mobile":"919586773322","Message":"Your OTP Password is XXXX","MessageType":"promo"}
requests.packages.urllib3.disable_warnings()
#r = requests.post(SMS_URL, data=json.dumps(smspayload), headers=SMS_HEADERS, verify=False)

#requests.post('https://iproapi.com/api/sms/sendotp', data={"Mobile":"919586773322","Message":"Your OTP Password is XXXX","MessageType":"promo"}, headers={'Content-type': 'Application/json', 'X-Token': 'GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw=='}, timeout=100)

#r = 
#
#print r
#print r.text

import urllib
import urllib2
#from urllib

request = urllib2.Request(SMS_URL, urllib.urlencode(smspayload), SMS_HEADERS)
#request.add_header('Content-type', 'Application/json')
#request.add_header('X-Token', 'GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw==')
#json = urllib2.urlopen(request).read()
#print(json)
'''

from datetime import datetime
print str(datetime.now())

import pycurl, json
'''
#github_url = 'https://api.postmarkapp.com/email'
SMS_URL = 'https://iproapi.com/api/sms/sendotp'

#data = json.dumps({"Mobile":"919586773322","Message":"Your OTP Password is mavaji","MessageType":"trans"})
data = json.dumps({"Mobile":"919586773322","Message":"Dear Customer, One Time Password (OTP) for Wishbook is %s. Do NOT share it with anyone","MessageType":"trans"})

c = pycurl.Curl()
c.setopt(pycurl.URL, SMS_URL)
c.setopt(pycurl.HTTPHEADER, ['Content-type: Application/json',
    'X-Token: GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw=='
])
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, data)
c.perform()
#print c

print str(datetime.now())'''


def smsUrl():
	SMS_URL = 'https://iproapi.com/api/sms/sendotp'
	
	c = pycurl.Curl()
	c.setopt(pycurl.URL, SMS_URL)
	c.setopt(pycurl.HTTPHEADER, ['Content-type: Application/json',
		'X-Token: GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw=='
	])
	c.setopt(pycurl.POST, 1)
	
	return c

data = json.dumps({"Mobile":"+919586773322","Message":"Dear Customer, One Time Password (OTP) for Wishbook is %s. Do NOT share it with anyone","MessageType":"trans"})
c = smsUrl()
c.setopt(pycurl.POSTFIELDS, data)
c.perform()

print c

'''import grequests
reqs = []

APPLOZIC_URL = 'https://apps.applozic.com/rest/ws/register/client'
payload = {
  "userId":"aks123112",
  "deviceType":"1",
  "applicationId":applicationId,
  "contactNumber":"+919586711112"
}

res = grequests.post(APPLOZIC_URL, data=json.dumps(payload), headers=APPLOZIC_HEADERS)
reqs.append(res)

rdata = grequests.map(reqs)
print rdata
'''
'''
import urllib
import pycurl, json
from cStringIO import StringIO

mobile_nos = ["+919586773322"]
message = urllib.quote_plus("Dear Customer, One Time Password (OTP) for Wishbook is %s. Do NOT share it with anyone")

SMS_URL = 'https://iproapi.com/api/sms/sendotp'

reqs = []
m = pycurl.CurlMulti()

for mobile_no in mobile_nos: 
    response = StringIO()
    handle = pycurl.Curl()
    handle.setopt(pycurl.URL, SMS_URL)
    handle.setopt(pycurl.HTTPHEADER, [
        'Content-type: Application/json',
        'X-Token: GDlzmhRvigEjbkk4TxCi5SMFD8XDK+pOiMS5v09SDAByqDOq+S6VpK0mXgdO3HjinCChyk/GYS+4h4xGPfTEBe41gIZSFSxTPIpgLiNQPuIUYUQoA2Pz2FB+ixoTATlA6A16/G4R5gmCSlBI9vrQW6VwZimyuHUEsOJbEzZjdjJUvjcSAM/+Xn4MiuzsCo6kVRVrgvBVG/Usx5etX3MzXzMZr8qJEChXonw4b/IkQ9qUGnecOILIdVTutPAJbSIBbCVX8Prz6/sHrS2Si3BVRpBTmKlu9VZSNNOU1KK4XypA/xGnP7y7y2Glw8jcsU055wil2nwTLDV9mXYxxCDpiw=='
    ])
    handle.setopt(pycurl.POST, 1)
    
    data = json.dumps({"Mobile":mobile_no,"Message":message,"MessageType":"trans"})
    
    handle.setopt(pycurl.POSTFIELDS, data)
    
    handle.setopt(pycurl.WRITEFUNCTION, response.write)
    req = (SMS_URL, response, handle)
    # Note that the handle must be added to the multi object
    # by reference to the req tuple (threading?).
    m.add_handle(req[2])
    reqs.append(req)

SELECT_TIMEOUT = 1.0
num_handles = len(reqs)
while num_handles:
    ret = m.select(SELECT_TIMEOUT)
    if ret == -1:
        continue
    while 1:
        ret, num_handles = m.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM: 
            break
            
'''
