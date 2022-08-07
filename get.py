
#https://curlconverter.com/

import requests
import pyrebase
import time
from datetime import datetime
from pytz import timezone    
from bs4 import BeautifulSoup
from string import Template

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'http://192.168.1.1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://192.168.1.1/admin/login.asp',
    'Accept-Language': 'en-US,en;q=0.9',
    'dnt': '1',
    'sec-gpc': '1',
}

data = {
  'username': 'tmadmin',
  'password': 'password',
  'save': 'Login',
  'submit-url': '/admin/login.asp'
}
data2 = {
  'save': 'Logout',
  'submit-url': '/admin/login.asp'
}

config = {     
  "apiKey": "xxxxxxxxxxxxxxxxxxxxx",
  "authDomain": "xxxxxxxxxxxxxxx",
  "databaseURL": "xxxxxxxxxxxxxxxxxxx",
  "storageBucket": "xxxxxxxxxxxxxxxxxxxxxxx"
}

#s = requests.Session()
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
#user = auth.sign_in_with_email_and_password("xxxxxx@gmail.com", "password")
#id = user['localId']

def get_real_ip():
    s= requests.post('http://192.168.1.1/boaform/admin/formLogin', headers=headers, data=data, verify=False)
    ip = BeautifulSoup(requests.get('http://192.168.1.1/status.asp').content, 'html.parser').find("div", class_="data_common data_vertical").find_next('table').find_all('tr')[1].find_all('td')[4].text
    s= requests.post('http://192.168.1.1/boaform/admin/formLogout', headers=headers, data=data2, verify=False)
    return ip

def get_external_ip():
    return requests.get('http://v4.ident.me/').content.decode('utf8')

def update_duckdns(oldip, newip):
    params = {
        "domains": "xxxxxxxxxxxxxxxxxxxx",
        "token": "xxxxxxxxxxxxxxxxxxxxxxxxx",
        "ip": newip,
        "verbose": True
    }
    r = requests.get("https://www.duckdns.org/update", params)

    datas = {
        "old-ip": oldip,
        "new-ip": newip,
    }
    db.child("ipv4").update(datas)
    
    return r.text.strip().replace('\n', '-')

def update_firebase(ex, re, duckdns, ctime, utime, c="false", d="false", u="false"):
    datas = {
        "external-ip": ex,
        "real-ip": re,
        "duckdns": duckdns,
        "ctime": ctime,
        "utime": utime,
        "cstate": c,
        "dstate": d,
        "ustate": u,
    }
    db.child("ipv4").update(datas) #.child("users").child(id) , user['idToken']

def get_time():
    return datetime.now(timezone('Asia/Kuala_Lumpur')).strftime("%Y-%m-%d~%H.%M.%S")

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

#initialize

start = datetime.now(timezone('Asia/Kuala_Lumpur'))
utime = get_time()
ctime = get_time()
real_ip = get_real_ip()
external_ip = get_external_ip()
#print(real_ip)
old_ip = real_ip
new_ip = real_ip
duck = update_duckdns(old_ip, external_ip)
update_firebase(external_ip, real_ip, duck, ctime, utime)


#print (db.child("ipv4").child("cstate").get().val())

#loop
try:
    while True:
        try:
            #auto
            ex_tmp = get_external_ip()
            ctime = get_time()
            update_firebase(external_ip, real_ip,duck, ctime, utime)
            #print(ex_tmp)
            if external_ip != ex_tmp:
                external_ip = ex_tmp
                real_tmp = get_real_ip()
                if real_ip != real_tmp:
                    real_ip = real_tmp
                    old_ip = new_ip
                    new_ip = real_ip
                    duck = update_duckdns(old_ip, external_ip)
                    utime = get_time()
                    update_firebase(get_external_ip(), new_ip, duck, ctime, utime)
                    
            #manual
            uptime = datetime.now(timezone('Asia/Kuala_Lumpur')) - start
            db.child("ipv4").update({"uptime": strfdelta(uptime, "%D~%H.%M.%S")})
            for x in range(60):
                time.sleep(5)
                #print (strfdelta(uptime, "%D~%H.%M.%S"))
                #print (uptime.strftime("%d~%H.%M.%S"))
                if db.child("ipv4").child("cstate").get().val() == "true":
                    print("check")
                    real_tmp = get_real_ip()
                    if real_ip != real_tmp:
                        real_ip = real_tmp
                        db.child("ipv4").update({"change": "true"})
                    new_ip=real_ip()
                    external_ip = get_external_ip()
                    ctime = get_time()
                    update_firebase(external_ip, new_ip, duck, ctime, utime)
                if db.child("ipv4").child("dstate").get().val() == "true":
                    print("duck")
                    old_ip = new_ip
                    new_ip = real_ip
                    duck = update_duckdns(old_ip, new_ip)
                    utime = get_time()
                    external_ip = get_external_ip()
                    update_firebase(external_ip, new_ip, duck, ctime, utime)
                    db.child("ipv4").update({"change": "false"})
                if db.child("ipv4").child("ustate").get().val() == "true":
                    print("update")
                    old_ip = new_ip
                    real_ip = get_real_ip()
                    new_ip = real_ip
                    ctime = get_time()
                    duck = update_duckdns(old_ip, external_ip)
                    utime = get_time()
                    external_ip = get_external_ip()
                    update_firebase(external_ip, new_ip, duck, ctime, utime)
        except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError,):
            print("error")
            pass

                
except KeyboardInterrupt:
    print("exiting")

