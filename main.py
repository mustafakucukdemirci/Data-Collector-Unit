#!/home/mirai/testenv/bin/python3
# -*- coding: utf-8 -*-

import datetime

import os
from sys import platform
import sys
folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder_path)
if( platform != "win32" and (os.geteuid() != 0)):
    os.system("echo 'mirai' | sudo -S nice -20 /usr/bin/python3 main.py")
    exit()
 
sys.path.append("/home/mirai/mirhpenv/lib/python3.11/site-packages")


from base import UI,textFitter 
import tkinter as tk 
import mdbconnect 
from threading import Thread 
import time
from commons import modbus_map as DataField
import commons 
import History
import DbProcessor as dbp
import work_order_screen as wos
import stops_screen as ss
import timeupdater
import counter_sensor 


plc_connection = mdbconnect.Connector()

timeupdater.updateTime()
 


class CoreScreenFunctions:
    __instance = None
    __set_ui = False

    def __new__(cls,**args):
        if not isinstance(CoreScreenFunctions.__instance, cls):
            CoreScreenFunctions.__instance = object.__new__(cls)

        return CoreScreenFunctions.__instance
    def __init__(self):
        if(not CoreScreenFunctions.__set_ui):
            self.ui = UI()
            CoreScreenFunctions.__set_ui = True

    def getFrame(self,clear = False):
        return self.ui.getFrame(clear)

    def left_menu(self):

        #to change button background on hover
        def on_enter(e :tk.Event):
            e.widget['activebackground'] = commons.button_background 
            

        def on_leave(e):
            e.widget['background'] = commons.common_background


        mainframe = self.ui.getFrame()
        height = mainframe.winfo_height()
        width = mainframe.winfo_width()

        mainframe.configure(highlightbackground="black", highlightthickness=3)
        canvas = tk.Canvas(mainframe, name="main canvas",bg="white")
        canvas["background"] = "white"
        canvas.place(relx=0,rely=0,relwidth=1,relheight=1)



        _images = [(tk.PhotoImage(file='icons/home.png'),"Ana Menü",lambda : MainScreen()),
                   (tk.PhotoImage(file='icons/workorder.png'),"İş Emri",lambda : wos.WorkOrder(CoreScreenFunctions())),
                   (tk.PhotoImage(file='icons/history.png'),"Geçmiş",lambda : History.History(CoreScreenFunctions()))]
        
        
        for tab in range(commons.menu_icon_number):
            canvas.create_rectangle(0,tab*int(height/commons.menu_icon_number),
                                    commons.menu_symbol_space_width,(tab+1)*int(height/commons.menu_icon_number),
                                    width=3)
            

            #Let us create a dummy button and pass the image
            button= tk.Button(canvas,image=_images[tab][0],text=_images[tab][1],command= _images[tab][2],
                              compound=tk.TOP, borderwidth=0, bg=commons.common_background, name=_images[tab][1].lower() )
            button.image = _images[tab][0]

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
            # print(tab*int(height/menu_icon_number),menu_symbol_space_width,int(height/menu_icon_number))
            button.place(x=3,y=tab*int(height/commons.menu_icon_number)+3,width=commons.menu_symbol_space_width-6,height=int(height/commons.menu_icon_number)-3)

            

class MainScreen:
    def __init__(self):
        self.ui:tk.Frame = UI().getFrame(True)
        core_screen_functions = CoreScreenFunctions()
        core_screen_functions.left_menu()
        self.canvas:tk.Canvas = self.ui.nametowidget("main canvas")
        self.create_top_info()
        self.create_info_texts_with_labels() 
        
        
    def create_top_info(self):
        """
        this function creates rectangles and texts on the upper side of main screen
        """
        def read_and_update_data(label,text,register_address):
            if(not label):
                return
            val = plc_connection.read_address(register_address)
            if(val > 1150):
                val = "Prob Hatası" 
                label["text"] = str(val)
                label["fg"] = "red"
            else:
                label["text"] = text + "\n" + str(val) 
                label["fg"] = "black"

            label.after(1000,read_and_update_data,label,text,register_address)
            
        bogaz_anlik_sicaklik = plc_connection.read_address(DataField["Boğaz Anlık"][1])
        kazan_anlik_sicaklik = plc_connection.read_address(DataField["Kazan Gerçek"][1])
        if(int(kazan_anlik_sicaklik) > 1100):
            kazan_anlik_sicaklik = "Prob Hata"
        if(int(bogaz_anlik_sicaklik) > 1100):
            bogaz_anlik_sicaklik = "Prob Hata"

        data_tags = [("Yağ Kazanı\nSıcaklığı",kazan_anlik_sicaklik,DataField["Kazan Gerçek"][1]),
                     ("Boğaz\nSıcaklığı",bogaz_anlik_sicaklik,DataField["Boğaz Anlık"][1])]
        
        width_for_top_menu = (self.ui.winfo_width()-commons.menu_symbol_space_width)/commons.main_menu_top_number
        height_for_top_menu = int(self.ui.winfo_height()/commons.menu_icon_number)

        total_perc_for_top_menu = (self.ui.winfo_width() - commons.menu_symbol_space_width-4) / self.ui.winfo_width() 
        rel_x = 1-total_perc_for_top_menu
        for datapoint in range(commons.main_menu_top_number):
            if(len(data_tags)>datapoint):
                a = tk.Label(self.canvas,bg="white",text=data_tags[datapoint][0]+"\n"+str(data_tags[datapoint][1]),
                             font=("Times New Roman",42),borderwidth=2,highlightthickness=2)
                a.place(relx=rel_x,rely=0,relwidth=total_perc_for_top_menu/commons.main_menu_top_number,
                        relheight=0.2)
                a.after(1000,read_and_update_data,a,data_tags[datapoint][0],data_tags[datapoint][2])
                rel_x += total_perc_for_top_menu/commons.main_menu_top_number

    def create_info_texts_with_labels(self):

        def record_reset_counter():
            current_time = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
            
            # Dosyaya yazılacak metin
            log_message = f"{current_time} > Sayacı sıfırla butonuna bastınız.\n"
            
            # Dosyaya yazma işlemi
            with open("log.txt", "a") as file:
                file.write(log_message)

            counter_sensor.reset_counter()
                

        _width = self.ui.winfo_width()
        _height = self.ui.winfo_height()

        half_text_width = (_width-commons.menu_symbol_space_width)/2
        half_text_height = (_height- (_height/commons.menu_icon_number))/2
        text_final_height = (_height/commons.menu_icon_number) + half_text_height

        _subframe = tk.Frame(self.canvas,bg = self.canvas["bg"])
        _subframe.place(relx=((commons.line_size+commons.menu_symbol_space_width)/_width),
                        rely=int((self.ui.winfo_height()/commons.menu_icon_number)+commons.line_size)/_height,
                        relwidth=1-((commons.line_size+commons.menu_symbol_space_width)/_width),
                        relheight=1-int((self.ui.winfo_height()/commons.menu_icon_number)+commons.line_size)/_height)
        
        label_1 = tk.Label(_subframe,text="Hedeflenen",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.1,relwidth=0.3,rely=0,relheight=0.1)
        label_2 = tk.Label(_subframe,text="Üretilen",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.1,relwidth=0.3,rely=0.1,relheight=0.1) 
        label_4 = tk.Label(_subframe,text="İstasyon Durumu",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.1,relwidth=0.3,rely=0.2,relheight=0.1)
        label_5 = tk.Label(_subframe,text="KPI",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.1,relwidth=0.3,rely=0.3,relheight=0.1)
        label_6 = tk.Label(_subframe,text="OEEE",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.1,relwidth=0.3,rely=0.4,relheight=0.1) 

        
        
        label_1_answer = tk.Label(_subframe,text=":"+str(plc_connection.read_address(DataField["otomatik uretim hedef"][1])),bg=_subframe["bg"],font=("Times New Roman",50),justify="left",anchor="w").place(relx=0.4,relwidth=0.3,rely=0,relheight=0.1)
        label_2_answer = tk.Label(_subframe,text=":"+str(plc_connection.read_address(DataField["otomatik uretim adeti"][1])),bg=_subframe["bg"],font=("Times New Roman",50),anchor="w")
        label_2_answer.place(relx=0.4,relwidth=0.3,rely=0.1,relheight=0.1)
        label_4_answer = tk.Label(_subframe,text=":Çalışıyor",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.4,relwidth=0.3,rely=0.2,relheight=0.1)
        label_5_answer = tk.Label(_subframe,text=":iyi",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.4,relwidth=0.3,rely=0.3,relheight=0.1)
        label_6_answer = tk.Label(_subframe,text=":87",bg=_subframe["bg"],font=("Times New Roman",50),anchor="w").place(relx=0.4,relwidth=0.3,rely=0.4,relheight=0.1) 


        sayacSifirla = tk.Button(_subframe, text="Sayaç Sıfırla", font=("Times New Roman",50), command=record_reset_counter).place(relx=0.3,relwidth=0.3,rely=0.6,relheight=0.2) 

        def update_answers(label:tk.Label,address):
            val = plc_connection.read_address(address) 
            if(val >= 0):
                label.configure(text=":"+str(plc_connection.read_address(address)))
            time.sleep(1)
            _subframe.after(1000,update_answers,label_2_answer,DataField["otomatik uretim adeti"][1])

        _subframe.after(1000,update_answers,label_2_answer,DataField["otomatik uretim adeti"][1])


class WoOrder:
    def __init__(self):
        frame = UI()
        core_screen_functions = CoreScreenFunctions()
        self.ui:tk.Frame = frame.getFrame()
        core_screen_functions.left_menu()
        self.canvas:tk.Canvas = self.ui.nametowidget("main canvas")
        self.create_info_texts()

    def on_enter(self,event: tk.Event, color):
        btn = event.widget
        btn["activebackground"] = color

    def on_leave(self,event,color):
        btn = event.widget
        btn["background"] = color


    def create_info_texts(self):
        _width = self.ui.winfo_width()
        _height = self.ui.winfo_height()

        half_text_width = (_width-commons.menu_symbol_space_width)/2
        half_text_height = (_height- (_height/commons.menu_icon_number))/2
        text_final_height = (_height/commons.menu_icon_number) + half_text_height

        _subframe = tk.Frame(self.canvas,bg=self.canvas["bg"])
        # _subframe.config(bg="red")

        _subframe.place(relx=((commons.line_size+commons.menu_symbol_space_width)/_width),
                        rely=0,
                        relwidth=1-((commons.line_size+commons.menu_symbol_space_width)/_width),
                        relheight=1)
        
        # def response_text_creater(text:str):
        #     good_color = "green"
        #     bad_color = "red"


        #     cnt = 1
        #     for txt in text:
        #         _ = tk.Label(_subframe,text=txt[0]+":"+txt[1], 
        #                      font=("Times New Roman",52),
        #                      bg=self.canvas["bg"], justify="left")
        #         # _.grid(row=cnt,column=2)
        #         _.place(relx=0.5,rely=0.1*cnt,anchor="center")
        #         _.update()
        #         textFitter(_)

        #         _subframe.grid_rowconfigure(cnt,weight=1) 
        #         cnt += 1


        # response_text_creater(mdbconnect.return_work_order())
        
        waste_button = tk.Button(_subframe,text="Fire",bg=commons.warning_color,command=lambda:print("waste clicked"),
                                 font=("Times New Roman",25))
        waste_button.bind("<Enter>", lambda e: self.on_enter(e,commons.warning_color_2))
        waste_button.bind("<Leave>", lambda e: self.on_leave(e,commons.warning_color))

        waste_button.place(relx=0.35,rely=0.8,anchor="center",relwidth=0.15,relheight=0.15)


        validation_button = tk.Button(_subframe,text="İş Emri Onay",bg=commons.positive_color,command=lambda:print("valid clicked"),
                                 font=("Times New Roman",25))
        validation_button.bind("<Enter>", lambda e: self.on_enter(e,commons.positive_color_2))
        validation_button.bind("<Leave>", lambda e: self.on_leave(e,commons.positive_color))

        validation_button.place(relx=0.65,rely=0.8,anchor="center",relwidth=0.15,relheight=0.15)
        



                
if __name__ == "__main__": 
    dbp.Temperatures()
    dbp.Products()
    Thread(target=ss.production_follower,args=()).start()
    dbp.WorkOrderTracker()

    ui = UI(destroy_shortcut="a")
    ui.mw.bind("d",lambda event: ss.stop_screen())
    csf = CoreScreenFunctions()
    MainScreen() 
    ui.run()




