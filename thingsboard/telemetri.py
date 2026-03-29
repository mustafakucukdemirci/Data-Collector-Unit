import requests
import json
from thingsboard import session as ss
from thingsboard import datas
import time
from threading import Thread
import datetime


session = ss.session()

class Pipeline:
    __instance = None 
    initialized = False
    
    def __new__(cls,**args):
        if not isinstance(Pipeline.__instance, cls):
            Pipeline.__instance = object.__new__(cls)
        return Pipeline.__instance
    
    def __init__(self):
        if(self.initialized):
            return
            
        self.messages = []
        self.states = []
        self.initialized = True
        Thread(target=self.__message_handler,args=()).start()

    def addMessage(self,msg):
        self.messages.append({"ts":str(1000*int((datetime.datetime.now()).timestamp())),"values":msg})
 
        # print("message added",(datetime.datetime.now()).timestamp())
    def addState(self,msg):
        
        self.states.append({"ts":datetime.datetime.now().timestamp(),"values":msg})
        print("state added")
    def __message_handler(self):
        while True and not ss.kill_session_thread:
            if(self.messages):
                try: 
                    res = self.upload_telemetry(self.messages[0])
                    if(res):
                        self.messages.remove(self.messages[0])
                except Exception as e:
                    print("error",e)
                    print("-----------------------------------")
                    print("this is where everything get fucked up")
                    time.sleep(0.25) 
                    continue
            if(self.states):
                try:
                    res = self.update_attributes(self.states[0])
                    if(res):
                        self.states.remove(self.states[0])
                except Exception as e:
                    time.sleep(0.25) 
                    print("cannot update attributes.",res)  
                    continue

 

    def upload_telemetry(self,data):
        # print("data to upload:",data)

        if(ss.session().headers == ""):
            print("Headers doesn't exist. Returning...")
            session.create_session()
            if(session.jwtToken == 0):
                return False
            session.get_ids()
            return False  

        result = requests.post(f"http://{datas.url}/api/plugins/telemetry/DEVICE/{datas.device_id}/timeseries/ANY?scope=ANY",json=data,headers=ss.session().headers) 

         

        if(result.status_code != 200):
            session.create_session()
            if(session.jwtToken == 0):
                return False
            session.get_ids()
            return False 
        else:
            return True 
    
    def update_attributes(self,data):
        result = requests.post(f"http://{datas.url}/api/plugins/telemetry/{datas.device_id}/SHARED_SCOPE",json=data,headers=ss.session().headers)
        if(result.status_code != 200):
            session.create_session()
            session.get_ids()
            return False 
        else:
            return True 


Pipe = Pipeline()

def upload_telemetry(data):
    Pipe.addMessage(data)

def update_attributes(data):
    Pipe.addState(data)

def read_attributes(data):
    
    headers = {
        'accept': 'application/json',
    }

    params = {
        'sharedKeys': data,
    }
    try:
        response = requests.get(f'http://{datas.url}/api/v1/{datas.device_access_token}/attributes', params=params, headers=ss.session().headers)
        
        return response.text
    except Exception as e : 
        return None


