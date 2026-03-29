import tkinter as tk
from PIL import Image, ImageTk

from tkinter import ttk

import virkeyb
import time
import mdbconnect
import os
from dotenv import load_dotenv
from commons import modbus_map as DataFields

load_dotenv()

dataImage = Image.open("icons/datascreen.png")


plc = mdbconnect.Connector()

FieldPerRow = 3

password = os.environ.get("SETTINGS_PASSWORD", "changeme")


class Settings:
    def __init__(self,frame,menu_symbol_size, core_screen_functions, MainScreen):
        self.ms = MainScreen
        self.ui:tk.Frame = frame.getFrame(True)
        self._core_screen_functions = core_screen_functions
        self._core_screen_functions.left_menu()
        self.canvas:tk.Canvas = self.ui.nametowidget("main canvas")
        self.canvas.update()
        self._menu_symbol_size = menu_symbol_size

        self.subFrame = tk.Frame(self.canvas,bg="white")
        self.subFrame.place(x=menu_symbol_size,y=0,relheight=1,relwidth=((self.ui.winfo_width() - menu_symbol_size) / self.ui.winfo_width()))

        self.hardcoded_params_area()



        # self.login_area()

    def clear_sub_frame(self):
        for child in self.subFrame.winfo_children():
            child.destroy()

    def hardcoded_params_area(self):
        global dataImage
        self.clear_sub_frame()
        __start = time.time()
        print("params area started")


        def read_and_update_data(label,register_address):
            #eğer pot göstergesiyse
            if(register_address == DataFields["Pot çalışma"][1]):
                pot_val = str(plc.read_address(DataFields["Pot çalışma"][1]))[-1]

                if(pot_val =="0"):
                    pot_val = "Kapalı"
                    label.configure(background="firebrick1",text = pot_val)
                if(pot_val =="1"):
                    pot_val = "Yarı Otomatik"
                    label.configure(background="chocolate1",text = pot_val)
                if(pot_val =="2"):
                    pot_val = "Tam Otomatik"
                    label.configure(background="chartreuse2",text = pot_val)
                return

            if(DataFields["Isılar açık kapalı"][1] == register_address):
                val = plc.read_from_coil(DataFields["Isılar açık kapalı"][1])
                if(val):
                    label.configure(background="chartreuse2",text = "Açık")
                else:
                    label.configure(background="firebrick",text = "Kapalı")
                return

            label["text"] = plc.read_address(register_address)
            label.after(1000,read_and_update_data,label,register_address)


        # image = image.resize((60, 60), Image.ANTIALIAS)

        if(type(dataImage) != ImageTk.PhotoImage):
            dataImage = ImageTk.PhotoImage(dataImage)

        # data_image = ImageTk.PhotoImage(dataImage)
        datalabel = tk.Label(self.subFrame,bg="white",image=dataImage)
        datalabel.image = dataImage
        datalabel.place(relx=0,rely=0,relheight=1,relwidth=1)
        tk.Label(self.subFrame,bg="white",font=("Times New Roman",32,"bold"),text="Pot\nÇalışma").place(relx=0.6,rely=0.64,relheight=0.09,relwidth=0.15)
        tk.Label(self.subFrame,bg="white",font=("Times New Roman",32,"bold"),text="Isıtıcılar").place(relx=0.225,rely=0.42,relwidth=0.125,relheight=0.06)


        dummy = tk.Label(self.subFrame,bg="azure2",font=("Times New Roman",32),text=plc.read_address(DataFields["Kazan Gerçek"][1]))
        dummy.after(2000,read_and_update_data,dummy,DataFields["Kazan Gerçek"][1])
        dummy.place(relx=0.105,rely=0.37,relwidth=0.065,relheight=0.055)

        dummy = tk.Label(self.subFrame,bg="azure2",font=("Times New Roman",32),text=plc.read_address(DataFields["Boğaz Anlık"][1]))
        dummy.after(2000,read_and_update_data,dummy,DataFields["Boğaz Anlık"][1])
        dummy.place(relx=0.55,rely=0.11,relwidth=0.065,relheight=0.055)


        self.subFrame.update()
