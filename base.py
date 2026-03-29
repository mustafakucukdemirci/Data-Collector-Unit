"""
All coyprights belong to Mirai Industrial Solutions inc
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import mdbconnect as plc
import sys
import counter_sensor
import time
import DbProcessor
from thingsboard.session import killprogram
from PIL import Image, ImageTk
import timeupdater

width = 1080
height = 960

CameraResolution = (1280,1024)
COLOR_MAIN = "#f9642c"
COLOR_SECONDARY = "#3b4151"
COLOR_TEXT_HEADER = "#284DAE"
COLOR_TEXT = "#CEE8FF"
#E3F0FF

LOGO_IMAGE = Image.open("icons/logo.png")

 

def textFitter(label : tk.Label):
    _font = tkFont.Font(font=label["font"])

    length = _font.measure(label["text"])
    height = _font.metrics('linespace')
    while((label.winfo_width()<length or label.winfo_height() < height) and (_font["size"] > 10)):
        _font["size"] = _font.actual()["size"]-3
        label.configure(font = _font)
        length = _font.measure(label["text"])
        height = _font.metrics('linespace')
        print(_font["size"],label.winfo_width(),length)
        


class UI:
    __instance = None
    __started = False

    def __new__(cls,**args):
        if not isinstance(UI.__instance, cls):
            UI.__instance = object.__new__(cls)
        return UI.__instance


    def __init__(self,destroy_shortcut=None): 
        if(not UI.__started):
            self.starter(destroy_shortcut=destroy_shortcut)
            UI.__started = True

    # def __new__(class_, *args, **kwargs):
    #     if not isinstance(class_.__instance, class_):
    #         class_._instance = object.__new__(class_, *args, **kwargs)
    #     return class_.__instance
    

    def starter(self,destroy_shortcut=None):
        print("UI initialization started. Destroy Shortcut:",destroy_shortcut)
        self.__coreFunctions = [self.__initializeUi,self.createInnerFrame]
        if(destroy_shortcut != None): self.__destroy_shortcut = destroy_shortcut; self.__coreFunctions.append(self.destroyShortcut)
        self.__loadCoreFunctions()


    def destroyShortcut(self):
        self.mw.bind(f"<{self.__destroy_shortcut}>",lambda x:self.onDestroy())
    
    def onDestroy(self):
        import stops_screen as ss
        DbProcessor.kill_db_thread = True
        plc.kill_modbus_thread = True
        killprogram()
        ss.kill_production_follower_thread = True 
        counter_sensor.kill_thread_var = True
        timeupdater.kill_time_updater = True

        self.mw.destroy()
        

    def run(self):
        self.__startUi()
    

    def __loadCoreFunctions(self):


        for i in self.__coreFunctions:
            i()
        self.mw.update_idletasks()

    def __initializeUi(self):
        self.mw = tk.Tk()
        self.mw.attributes("-fullscreen",True)
        if(sys.platform != "win32"):
            self.mw.attributes("-topmost",True)
        self.mw["bg"] = "white"
        self.mw.update()
        
        
    def getFrame(self,clear = False) -> tk.Frame:
        
        if(clear):
            for child in self.__InnerFrame.winfo_children():
                child.destroy()
        
        return self.__InnerFrame

        

    def __startUi(self):
        self.mw.mainloop()

        
    def createInnerFrame(self):
        self.__InnerFrame = tk.Frame(self.mw,bg="white")
        self.__InnerFrame.place(relx=0,rely=0,relwidth=1,relheight=0.9)

        self.create_footer()

    def create_footer(self): 
        global logoImage
        self.__foterFrame = tk.Frame(self.mw,bg="white")
        self.__foterFrame.place(relx=0,rely=0.9,relwidth=1,relheight=0.1)

        mirai_label = tk.Label(self.__foterFrame,bg="white")
        mirai_label.place(relheight=0.9,relwidth=0.15,relx=0.02,rely=0.05)
        mirai_label.update()
        try:
            logoImage = LOGO_IMAGE.resize((mirai_label.winfo_width(),mirai_label.winfo_height()), Image.ANTIALIAS)
        except:
            from PIL.Image import Resampling
            logoImage = LOGO_IMAGE.resize((mirai_label.winfo_width(),mirai_label.winfo_height()), Resampling.LANCZOS)

        logoImage = ImageTk.PhotoImage(logoImage)
        mirai_label.configure(image=logoImage)
        mirai_label["image"] = logoImage
 
        self.create_middle_button_hole = tk.Frame(self.__foterFrame,bg="white")
        self.create_middle_button_hole.place(relx=0.4,relheight=1,relwidth=0.2,rely=0)

    def get_footer_hole(self):
        self.mw.focus()
        return self.create_middle_button_hole
