from mdbconnect import Connector
from threading import Thread
from commons import modbus_map as DataField
import time
import database_models
import datetime
import thingsboard.telemetri as tlm
import commons
import json
import hashlib
from sqlalchemy import desc
import traceback
import database_models 
import sys

DEBUG = "--debug" in sys.argv


kill_db_thread = False
plc = Connector()

class Stops:
    def __init__(self):
        pass


def stable_hash(input_string):
    return int(hashlib.md5(input_string.encode()).hexdigest(), 16)

class Temperatures:
    def __init__(self):
         
        Thread(target=self.__handler,args=()).start()
    

    def __handler(self):
        counter = 0
        while not kill_db_thread:
            kazan = plc.read_address(DataField["Kazan Gerçek"][1])
            bogaz = plc.read_address(DataField["Boğaz Anlık"][1])
            hidrolik_yag_sicakligi = plc.read_address(DataField["Hidrolik Yağ Sıcaklık"][1])
            if(-1 not in [kazan,bogaz,hidrolik_yag_sicakligi] and 
               (None not in [kazan,bogaz,hidrolik_yag_sicakligi])):
                self.__save_into_db(kazan,bogaz,hidrolik_yag_sicakligi)
            #saatlik kontrol
            if(counter % 144 == 0):
                self.__remove_old_data()
            counter += 1
            __subcounter=0
            while not kill_db_thread and __subcounter <7:
                time.sleep(1)
                __subcounter += 1
            

    def __remove_old_data(self,days=7):
        
        day_limit = datetime.datetime.now() - datetime.timedelta(days=days)

        try:
            session = database_models.get_session()
            # print("7 günden eski verilerin silinmesi başladı.")
            session.query(database_models.TemperatureReading).filter(database_models.TemperatureReading.timestamp < day_limit).delete()
            session.commit()
            # print("7 günden eski verilerin silinmesi bitti.")

        except Exception as e:
            print("7 günden eski verilerin silinmesi başarılamadı.",e)
        finally:
            session.close()

    def __save_into_db(self,kazan,bogaz,hidrolik_yag_sicakligi):
        
        temperature1 = database_models.TemperatureReading(kazan=kazan, bogaz=bogaz, hidrolik=hidrolik_yag_sicakligi, timestamp=datetime.datetime.now())
        try:
            session = database_models.get_session()
            session.add_all([temperature1])
            session.commit()  
        except Exception as e:
            print("temperature couldn't written.",e)
        finally:
            session.close()

        try:
            self.__send_temps_temeletry(kazan,bogaz,hidrolik_yag_sicakligi)
        except Exception as e:
            print("sıcaklık verileri telemetri ile göndeirlemedi:",e)

    def __send_temps_temeletry(self,kazan,bogaz,hidrolik_yag_sicakligi):
        data = {"kazan":kazan,"bogaz":bogaz,"hidrolik_yag_sicakligi":hidrolik_yag_sicakligi}
        tlm.upload_telemetry(data)


def create_counter(initial_value=0):
    session = database_models.get_session()
    """Tabloya ilk satırı ekler, eğer tablo boşsa."""
    if session.query(database_models.Counter).count() == 0:
        new_counter = database_models.Counter(counter=initial_value)
        session.add(new_counter)
        session.commit()
        print(f"Yeni satır eklendi: {new_counter.counter}")
    else:
        print("Tablo zaten dolu, yeni satır eklenmedi.")

def start_counter():
    create_counter()
    """Counter tablosundaki ilk (ve tek) satırı döndürür."""
    session = database_models.get_session() 
    DataField["otomatik uretim adeti"][2] = int(session.query(database_models.Counter).first().counter) 
    print("COUNTER NEW VALUE:",DataField["otomatik uretim adeti"])

def set_counter(value):
    session = database_models.get_session() 
    line = session.query(database_models.Counter).first()
    line.counter = value
    session.commit()

class Products:



    def __init__(self):
        create_counter()
        
        Thread(target=self.__handler,args=()).start()


    def __handler(self):


        print("prod handler started")
        baslangic_uretim_adeti = DataField["otomatik uretim adeti"][2]
        
        while (baslangic_uretim_adeti == -1):
            time.sleep(0.5)
            baslangic_uretim_adeti = plc.read_address(DataField["otomatik uretim adeti"][1]) 

        while not kill_db_thread:
            uretim = plc.read_address(DataField["otomatik uretim adeti"][1])

            if(uretim == 1):
                baslangic_uretim_adeti = 1
                continue
            
            if(uretim > baslangic_uretim_adeti and uretim > 0):
                print("üretim:",uretim,"baslangic uretim adeti",baslangic_uretim_adeti)
                self.__save_into_db(uretim)
                baslangic_uretim_adeti = uretim
                set_counter(uretim)
                
                    

            time.sleep(0.5)

    

    def __save_into_db(self,prod):
        __value = prod

        prod = database_models.PressRecords(fire = False,production_id = prod, timestamp=datetime.datetime.now())
        try:
            session = database_models.get_session()
            print("writing into table...")
            session.add(prod)
            session.commit()  
        except Exception as e:
            print("press products couldn't written.",e)
        finally:
            
            session.close()

        try:
            print("saving into telemetryy")
            self.__save_into_telemetry(__value)
        except Exception as e:
            print("baskı verisi telemetri ile göndeirlemedi:",e)

    def __save_into_telemetry(self,prod):
        data = {"prod":prod}
        tlm.upload_telemetry(data)

def clear_product_list():
        # session.query(database_models.PressRecords).delete()
    try:
        session = database_models.get_session()
        
        # Select the IDs of the last 100 records to keep
        subquery = session.query(database_models.PressRecords.id).order_by(database_models.PressRecords.production_id.desc()).limit(100).subquery()
        
        # Delete records that are not in the subquery
        records_to_delete = session.query(database_models.PressRecords).filter(~database_models.PressRecords.id.in_(subquery))
        records_to_delete.delete(synchronize_session='fetch')

        session.commit()
    except Exception as e:
        print("press products couldn't removed.",e)
    finally: 
        session.close()

def set_params(vars):
    vars["boğaz set"] = int(float(vars["boğaz set"])*10)
    vars["kazan set"] = int(float(vars["kazan set"])*10)
    vars["mum ileri set"] = int(float(vars["mum ileri set"])*10)
    vars["mum geri set"] = int(float(vars["mum geri set"])*10)
    vars["kalip soguma set"] = int(float(vars["kalip soguma set"])*10)
    vars["pot cikma set"] = int(float(vars["pot cikma set"])*10)
    vars["pot bekleme set"] = int(float(vars["pot bekleme set"])*10)
    vars["pot inme set"] = int(float(vars["pot inme set"])*10)
    print(vars)
    Connector().write_to_register(commons.modbus_map["Boğaz Hedef"][1],vars["boğaz set"])
    Connector().write_to_register(commons.modbus_map["Kazan Hedef"][1],vars["kazan set"])
    Connector().write_to_register(commons.modbus_map["Mum ileri bekleme"][1],vars["mum ileri set"])
    Connector().write_to_register(commons.modbus_map["Mum Geri Çekme Zamanı"][1],vars["mum geri set"])
    Connector().write_to_register(commons.modbus_map["Kalıp Soğuma Bekleme"][1],vars["kalip soguma set"])
    Connector().write_to_register(commons.modbus_map["Pot yukarı çıkma zamanı"][1],vars["pot cikma set"])
    Connector().write_to_register(commons.modbus_map["pot yukarıda bekleme"][1],vars["pot bekleme set"])
    Connector().write_to_register(commons.modbus_map["Pot aşağı inme zamanı"][1],vars["pot inme set"])



class WorkOrderTracker:
    def __init__(self):
        self.old_work_order =stable_hash("")
        Thread(target=self.__handler,args=()).start()

    def __handler(self):
        while not kill_db_thread:
            try:
                self.__read_from_telemetry("workorders")
            except Exception as e:
                if(DEBUG):    
                    traceback.format_exc(e)
                    print("db problem")
                else:
                    pass
            time.sleep(2)

    def __read_from_telemetry(self,prod):
        # print("iş emirleri okunuyor:",end=" ")
        
        data = tlm.read_attributes(prod)
        if(data == None):
            # print("iş emirleri okunması başarısız")
            return
        # print("iş emirleri okunması başarılı")
        data = json.loads(data)

        #eğer yeni açılmış ise
        if(self.old_work_order ==stable_hash("")):
            try:
                commons.work_order = data["shared"]["workorders"]
            except KeyError:
                raise Exception("Shared alanı bulunmuyor.")
            
            wo = None
            for wo in commons.work_order:
                commons.work_order_static_vars[wo["IE"]] = {"fire" : 0, "mumagirlik":0}
                commons.cast = wo["kalipadno"]


            self.old_work_order =stable_hash(str(data["shared"]["workorders"]))
            return

        #Farklı iş emri var demektir
        if( stable_hash(str(data["shared"]["workorders"])) != self.old_work_order):
            # print("Yeni iş emirleri tetiklendi:",stable_hash(str(data["shared"]["workorders"])),self.old_work_order)
            import work_order_screen as wos
            wos.work_order_idx = 0
            commons.work_order = data["shared"]["workorders"]
            
            wo = None
            for wo in commons.work_order:
                commons.work_order_static_vars[wo["IE"]] = {"fire" : 0, "mumagirlik":0}
                commons.cast = wo["kalipadno"]
            

            self.old_work_order =stable_hash(str(data["shared"]["workorders"])) 

            # Connector().write_to_register(commons.modbus_map["otomatik uretim adeti"][1],1) 
            # Connector().sayac_sifirla()
            clear_product_list()
            #İŞ EMRİ SİSTEMİ OTURUNCA BURAYI YENİDEN AYARLA.
            # set_params({"boğaz set":wo["boğaz set"],
            #             "kazan set":wo["kazan set"],
            #             "mum ileri set":wo["mum ileri set"],
            #             "mum geri set":wo["mum geri set"],
            #             "kalip soguma set":wo["kalip soguma set"],
            #             "pot cikma set":wo["pot cikma set"],
            #             "pot bekleme set":wo["pot bekleme set"],
            #             "pot inme set":wo["pot inme set"]
            #             })
            
            

start_counter()

