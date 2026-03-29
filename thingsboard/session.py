import requests
import json
import time
from threading import Thread
from . import datas 

kill_session_thread = False

def killprogram():
    global kill_session_thread
    kill_session_thread = True

class session:
    __instance = None 
    initialized = False
    headers = ""
    jwtToken = 0

    def __new__(cls,**args):
        if not isinstance(session.__instance, cls):
            session.__instance = object.__new__(cls)
        return session.__instance
    
    def __init__(self):
        if(not session.initialized):
            print("session initialized")
            self.session_active = False
            session.initialized = True
            Thread(target=self.login,args=()).start()
            return



    def login(self):
        while True and not kill_session_thread: 
            if(self.create_session()):
                self.get_ids()
                self.session_active = True
                break
            else:
                print("trying to conenct")
                time.sleep(1)
                return

    def create_session(self): 
        try:  
            self.session.close()
        except:
            pass
        session = requests.Session()

        headers = {
            'accept': 'application/json',
        }

        json_data = {
            'username': datas.USERNAME,
            'password': datas.PASSWORD,
        }
        try:
            response = session.post(f'http://{datas.url}/api/auth/login', headers=headers, json=json_data,timeout=3)
        except requests.exceptions.ConnectionError:
            session.close()
            return False
        except requests.exceptions.ReadTimeout:
            session.close()
            return False

        jwtToken = json.loads(response.text)["token"]

        self.session = session
        self.jwtToken = jwtToken
        return True


    def get_ids(self):   
        auth_code = f'Bearer {self.jwtToken}'
        print("headers created")
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authorization': auth_code}


        __response = requests.get(f"http://{datas.url}/api/deviceProfileInfo/default",headers=self.headers)
        __response = json.loads(__response.text)

        self.default_device_profile_id = __response["id"]["id"]
        self.default_tenant_id = __response["tenantId"]["id"]


 

