
import tkinter as tk
import commons as data
import datetime
import database_models as dbm
import time
import mdbconnect as mdb
from main import MainScreen as ms
from PIL import Image, ImageTk
from thingsboard import telemetri as tlm
import base
import json
from threading import Thread
from virkeyb import NumKeyb 

connector = mdb.Connector()
kill_production_follower_thread = False
wait_production_follower_thread = False
seconds_for_non_production_alarm = 9999999999


dataImage = Image.open("icons/warning256.png")

list_of_stops = [] 
current_stop = None
 


class SubStops:
    """
        Bu sınıf duruşlar oluşturup, bunları arayüzde kullanıp database modelda ki stops sınıfı ile eşlemek için oluşturulmuştur
    """
    def __init__(self,durus_nedeni,durus_kodu, durus_tipi, planli_durus):
        self.durus_nedeni = durus_nedeni
        self.durus_alt_nedenleri = []
        self.durus_kodu = durus_kodu
        self.durus_tipi = durus_tipi
        self.planli_durus_mu = planli_durus
        self.durus_ana_neden = None
    
    def set_ana_neden(self, ana_durus):
        self.durus_ana_neden = ana_durus

    def set_alt_neden(self, alt_durus):
        self.durus_alt_nedenleri.append(alt_durus)
        alt_durus.set_ana_neden(self)

    def set_alt_neden(self, alt_durus):
        for durus in alt_durus:
            self.durus_alt_nedenleri.append(durus)
            durus.set_ana_neden(self)

    def get_ana_sebep(self):
        if(self.durus_ana_neden != None):
            return self.durus_ana_neden
        else:
            raise Exception("duruş ana neden bulunmamaktadır.")


durus_1 = SubStops("duruş 1","110","tip1",False)

duruslar = [durus_1]



def trigger_alarm(alarm:SubStops): 
    a = stop_screen(False,False)
    a.set_durus(alarm)



class _Stop:
    def __init__(self):
        self.stop = dbm.Stops()
        self.stop.durus_baslangic = datetime.datetime.now().replace(microsecond=0)
        self.breakdownstart = datetime.datetime.now()
        self.breakdownstartstr = self.breakdownstart.strftime("%d.%m.%Y %H:%M:%S")
        self.stop.is_emri_idsi = None
        self.substop_durus = None
        self.stop.Personel = data.worker_name
    
    def set_durus(self,durus : SubStops):
        self.stop.durus_nedeni = durus.durus_nedeni
        self.stop.durus_kodu = durus.durus_kodu
        self.stop.durus_tipi = durus.durus_tipi
        self.stop.planliDurus = durus.planli_durus_mu
        self.substop_durus = durus
 
    def durus_bitir(self):
        self.stop.durus_bitis = datetime.datetime.now().replace(microsecond=0)
        self.breakdownend = datetime.datetime.now()
        self.breakdownendstr = self.breakdownend.strftime("%d.%m.%Y %H:%M:%S")

        # İki datetime nesnesi arasındaki farkı hesaplama
        time_difference = self.breakdownend - self.breakdownstart

        # Farkı dakika cinsinden hesaplama
        minutes_difference = time_difference.total_seconds() / 60
        self.breakdowntime = str(round(minutes_difference,2))

        list_of_stops.append(self)
        
        self.__save_into_db()
 

    def set_is_emri(self,is_emri_id):
        self.stop.is_emri_idsi = is_emri_id

    def __save_into_db(self):
        try:
            session = dbm.get_session()
            session.add(self.stop)
            session.commit()
        except Exception as e:
            print("Duruşu veritabanına kaydederken hata:",e)
        finally:
            session.close()


        
no_bubbles_row = 5
class stop_screen:
    def __init__(self,no_press_stop = False,trigger_bubbles = True):
        
        # self.ui:tk.Frame = base.UI().getFrame(True)
        self.start_time = datetime.datetime.now().replace(microsecond=0)
        self.stop_frame = tk.Frame(base.UI().mw,bg="white")
        self.stop_frame.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.stop_instance = _Stop()

        self.no_press_stop = no_press_stop

        # connector.write_to_coil(4,1)
        global wait_production_follower_thread
        wait_production_follower_thread = True
        if(trigger_bubbles):
            self.bubbles()

    def bubbles(self,stops = duruslar, quality_stop = False):
        self.upload_telemetry_stop("Arıza Girilmedi")
        #DURUŞ BURADA BAŞLIYOOR!


        for child in self.stop_frame.winfo_children():
            child.destroy()

        width_per_stop = 1 / (no_bubbles_row + 1)
        space_between = width_per_stop / no_bubbles_row
        space_between *= 1.05
        counter = 0

        if(quality_stop):
            stops.append(SubStops("KALİTE KONT\nROL DURUŞ","A00","tip1",False))

        for durus in stops:
            btn = tk.Button(self.stop_frame,text=durus.durus_nedeni,bg="skyblue",font=("Times New Roman",30))
            if(durus.durus_nedeni == "geri"):
                btn.configure(command= lambda:self.bubbles())
            elif(not durus.durus_alt_nedenleri):
                btn.configure(command=lambda durus=durus:self.set_durus(durus))
            else:
                btn.configure(command=lambda val = durus.durus_alt_nedenleri:self.bubbles(val))

            btn.place(relx=(space_between/2)+((space_between+width_per_stop)*(counter%no_bubbles_row)),
                      relwidth=width_per_stop,
                      rely=(space_between)+(0.2*(counter//no_bubbles_row)),
                      relheight=0.15)
            counter += 1
        

        if(quality_stop):
            stops.pop()

        if(self.no_press_stop):
            self.__bubbles_glowing(True)
            

    def __bubbles_glowing(self, even:bool):
        if(even):
            self.stop_frame.configure(bg="red")
        else:
            self.stop_frame.configure(bg="white")
        
        self.stop_frame.after(1000,lambda :self.__bubbles_glowing(not even))
    
    def set_durus(self,durus):
        self.stop_instance.set_durus(durus)
        self.failure_condition()
        
    def upload_telemetry_stop(self, state=None):
        if(not state):
            state = self.stop_instance.stop.durus_nedeni
        try:
            tlm.upload_telemetry({"state":state})
        except Exception as e:
            print("State güncellenemedi.")

        

    def failure_condition(self):
        global dataImage

        for child in self.stop_frame.winfo_children():
            child.destroy()

        
        if(type(dataImage) != ImageTk.PhotoImage):
            dataImage = ImageTk.PhotoImage(dataImage)

        imglbl = tk.Label(self.stop_frame,bg="white",image=dataImage)
        imglbl.image = dataImage
        imglbl.place(relx=0,rely=0,relheight=0.3,relwidth=1)

        self.stop_frame.bind("b",lambda x:self.ask_user_for_end_stop())
        imglbl.bind("<Button-1>", lambda x: self.ask_user_for_end_stop())
        self.stop_frame.focus()

        lbl = tk.Label(self.stop_frame,bg="white",
                       text=f"Şu anda cihaz duruş modundadır.\nSebep:{self.stop_instance.stop.durus_nedeni}\n{data.worker_name}\nAçmak için sembole tıklayın ve şifreyi giriniz",
                       font=("Times New Roman",70))
        lbl.place(relx=0,rely=0.3,relheight=0.7,relwidth=1)


        self.upload_telemetry_stop()




    def ask_user_for_end_stop(self):
        self.durus_bitir()
    def durus_bitir(self):
        global wait_production_follower_thread

        # connector.write_to_coil(409,0)
        print("bitir duruş")
        self.stop_instance.durus_bitir()
        wait_production_follower_thread = False
        self.upload_telemetry_stop("Active")
        self.stop_frame.destroy()
        ms()




def production_follower():
      
    
    baslangic = data.modbus_map["otomatik uretim adeti"][2]
    _start = time.time()

    check_updated_stops()

    while not kill_production_follower_thread:
        # print("Başlangıç:",baslangic,"Anlık:",data.modbus_map["otomatik uretim adeti"][2],"Kalan Zaman:",time.time() - _start - seconds_for_non_production_alarm)
        # print(int(time.time() - _start),"------------------------------------------")
        # print(time.time() - _start) 
        if(data.modbus_map["otomatik uretim adeti"][2] > baslangic):
            _start = time.time()
            baslangic = data.modbus_map["otomatik uretim adeti"][2]
        elif(time.time() - _start > seconds_for_non_production_alarm):
            _ss = stop_screen(True)
        else:
            time.sleep(1)
        while(wait_production_follower_thread and not kill_production_follower_thread):
            time.sleep(1)
            _start = time.time()


def check_updated_stops():
    return
    try:
        time.sleep(2)
        __duruslar = tlm.read_attributes("stops")
        while __duruslar == None and not kill_production_follower_thread:
            __duruslar = tlm.read_attributes("stops")
            time.sleep(1) 
 
        if(kill_production_follower_thread):
            return
        
        __duruslar = json.loads(__duruslar)["shared"]["stops"] 
        _drs = {}
        for i,j in __duruslar:
            _drs[i] = j
        
        while duruslar:
            duruslar.pop()
        
        for i,j in _drs.items():
            if len(j) > 11:
                j = j[0:10] + "\n" + j[10:]
            _ = SubStops(i+"\n"+j,i,"tip1",False)
            duruslar.append(_)
        
        
    except Exception as e:
        print("duruşlar okunamadı.",e)

def fill_footer_hole():
    global __tkimage


    def login(): 
        frame = base.UI().getFrame(True)
        updatescrframe = tk.Frame(frame)
        updatescrframe.place(relheight=1,relwidth=1,relx=0,rely=0)

        tk.Label(updatescrframe,text="Şifrenizi Giriniz",font=("Times New Roman",55)).place(relheight=0.2,relwidth=1,relx=0,rely=0.5)

        entry = tk.Entry(updatescrframe,font=("Times New Roman",35))
        entry.place(relheight=0.1,relwidth=0.2,relx=0.4,rely=0.65)
        entry.bind("<Button-1>",lambda x :NumKeyb(updatescrframe,entry))

        backbtn = tk.Button(updatescrframe,font=("Times New Roman",35),text="Geri",command=lambda:[updatescrframe.destroy(),ms()])
        backbtn.place(relheight=0.1,relwidth=0.1,relx=0.5,rely=0.8)


        def __check(val): 
            with open("credentials.json","r") as f:
                crd = json.load(f)

            val = str(val)
            for i,j in crd["Employees"].items():
                if((j == val)):
                    updatescrframe.destroy()
                    if("kalite" in i.lower()):
                        a = stop_screen(trigger_bubbles=False)
                        a.set_durus(SubStops("Kalite Kontrol Duruşu","110","tip1",False))
                        return
                    else:
                        data.worker_name = str(i)
                        stop_screen()

        btn = tk.Button(updatescrframe, text="Onayla",font=("Times New Roman",35), command= lambda : __check(int(entry.get()))  )
        btn.place(relheight=0.1,relwidth=0.09,relx=0.4,rely=0.8)


    hole_frame = base.UI(destroy_shortcut="a").get_footer_hole()
    subframe = tk.Frame(hole_frame)
    subframe.bind("<Button-1>", lambda x:login())
    subframe.place(relheight=1,relwidth=1,relx=0,rely=0)

    lbl = tk.Label(subframe,bg="gray97")
    lbl.place(relheight=1,relwidth=1,relx=0,rely=0)
    lbl.update()

    __img = Image.open("icons/StopButtonTrigger.png")
    size = min(lbl.winfo_width(),lbl.winfo_height())
    
    try:
        __img = __img.resize((size,size), Image.ANTIALIAS)
    except:
        from PIL.Image import Resampling
        __img = __img.resize((size,size), Resampling.LANCZOS) 

 
    __tkimage = ImageTk.PhotoImage(__img)
    lbl.configure(image=__tkimage)
    lbl["image"] = __tkimage


    
    lbl.bind("<Button-1>", lambda x:login())
    
fill_footer_hole()















