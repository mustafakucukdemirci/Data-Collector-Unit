from pyModbusTCP.client import ModbusClient
from commons import modbus_map as DataField
import commons
import socket
import time
import datetime
from threading import Thread
import os
from dotenv import load_dotenv
import thingsboard.telemetri as tlm
import database_models as dbm

load_dotenv()

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)

url_phone_connection = os.environ.get("PLC_URL_PHONE", "192.168.x.x")
url_home = os.environ.get("PLC_URL_HOME", "192.168.x.x")
url_ethernet = os.environ.get("PLC_URL_ETHERNET", "192.168.x.x")
url_plc = os.environ.get("PLC_URL_PLC", "192.168.x.x")

kill_modbus_thread = False

class Connector:
    __instance = None
    __thread = False
    __read_adress_lock = False

    def __new__(cls,**args):
        if not isinstance(Connector.__instance, cls):
            Connector.__instance = object.__new__(cls)

        return Connector.__instance

    def __init__(self):
        # self.client_handler = ModbusClient(host=url_plc, port=502, unit_id=1, auto_open=True)
        if(not Connector.__thread):
            status = False
            # while not status:
            #     status = self.client_handler.open()
            Thread(target=self._update_tables,args=()).start()


            # Connector.__thread = True
            print("thread run. Status of connection:",status)

    def formatter(self,val):
        if(not isinstance(val,str)):  val = str(val)
        if(len(val)==1):
            return "0." + val
        val = val[0:-1] + "." + val[-1]
        return val

    def read_address(self,address):
        for key,value in DataField.items():
            if(value[1] == address):
                return value[2]


    # def __read_address(self,address,totaltime=0):
    #     # return "0.1s"
    #     if(totaltime>1):
    #         return -1
    #     __start = time.time()
    #     val = self.client_handler.read_holding_registers(address)
    #     time.sleep(0.01)
    #     val_2 = self.client_handler.read_holding_registers(address)

    #     if(val == val_2):
    #         pass
    #     else:
    #         self.__read_address(address,time.time()-__start+totaltime)


    #     if val == None:
    #         return -1
    #     val = str(val[0])
    #     if(len(val)==1):
    #         return "0." + val
    #     val = val[0:-1] + "." + val[-1]
    #     return val


    def _update_tables(self):
        pass
        # records = []

        # while not kill_modbus_thread:


        #     for key,value in commons.modbus_map.items():
        #         if(key == "otomatik uretim adeti"):
        #             continue
        #         if(value[0] == 0):#if its register
        #             if(kill_modbus_thread):
        #                 return
        #             ___start = time.time()
        #             # val = self.__read_address(value[1])
        #             # print(key," read time",round(time.time()-___start,2))
        #             if(val != -1):
        #                 value[2] = val




        #     records.append([time.time(),___start,time.time()-___start])

        #     with open("data.txt","w") as f:
        #         for key,value in commons.modbus_map.items():
        #             if(value[0] == 0):#if its register

        #                 f.write(str(key)+str(value)+"\n")

        #         for rec in records:
        #             f.write(str(rec)+"\n")


        #     time.sleep(0.2)

    def __save_into_telemetry(self,prod):
        data = {"prod":prod}
        tlm.upload_telemetry(data)
