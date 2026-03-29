import commons
import base
from PIL import Image, ImageTk
import tkinter as tk
from virkeyb import NumKeyb  
from thingsboard import telemetri as tlm
import base64
import io
import datetime
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import database_models as dbm
import stops_screen as stopscr

kalipimg = Image.open("icons/kalip.png")
nextimg = Image.open("icons/nextButton.png")  
work_order_idx = 0

woslist = []

def initialize_counter():
    # Counter tablosunda satır olup olmadığını kontrol et
    counter_entry = dbm.get_session().query(dbm.Counter).first()
    if not counter_entry:
        # Eğer satır yoksa, yeni bir satır ekle
        new_counter = dbm.Counter(counter='0')
        dbm.get_session().add(new_counter)
        dbm.get_session().commit()
        return new_counter
    return counter_entry

def update_counter(new_value):
    # İlk satırı al ve güncelle
    counter_entry = dbm.get_session().query(dbm.Counter).first()
    if counter_entry:
        counter_entry.counter = new_value
        dbm.get_session().commit()
    else:
        # Eğer satır yoksa, yeni bir satır ekle
        new_counter = dbm.Counter(counter=new_value)
        dbm.get_session().add(new_counter)
        dbm.get_session().commit()

def get_counter():
    # İlk satırı al ve değerini döndür
    counter_entry = dbm.get_session().query(dbm.Counter).first()
    if counter_entry:
        return counter_entry.counter
    return None



class wos:
    def __init__(self,idx,output,scrap):
        self.potype = ""
        self.prdorder = ""
        self.confirmation = ""
        self.material = ""
        self.workcenter = ""
        self.outputqlt = ""
        self.setup = ""
        self.machine = ""
        self.labour = ""
        self.confirmdate = ""
        self.workstart = ""
        self.workend = ""
        self.shiftnumber = ""
        self.personelnum = ""
        self.scrap = str(scrap)
        self.failure = ""
        self.createwos(idx,output=output) 

    def createwos(self,idx,output):
        wo = commons.work_order[idx]
        wostatic = commons.work_order_static_vars[wo["IE"]]

        self.potype = wo["IE"].split("-")[0]
        self.prdorder = wo["IE"].split("-")[1]
        self.confirmation = wo["onayno"]
        self.material = wo["malzemenum"]
        self.workcenter = wo["ismerkezi"]
        self.outputqlt = str(output)
        self.setup = str(0)
        self.machine = str(7)
        self.labour = str(0)
        self.confirmdate = datetime.datetime.now().strftime("%d.%m.%Y")
        self.workstart = datetime.datetime.now().replace(hour=datetime.datetime.now().hour - 1).strftime("%d.%m.%Y  %H:%M")
        self.workend = datetime.datetime.now().strftime("%d.%m.%Y  %H:%M") 
        shift = "1"
        if(datetime.datetime.now().hour > 19):
            shift = "2"
        self.shiftnumber = shift
        self.personelnum = "CAP.AYSEGU"
        self.createxml()

    def add_stop(self,root):

        for fail in stopscr.list_of_stops:
            failure = ET.SubElement(root,"failure")
            row = ET.SubElement(failure, 'row')
            failurecode = ET.SubElement(row,"failurecode")
            failurecode.text = "P02"
            breakdownstart = ET.SubElement(row,"breakdownstart")
            breakdownstart.text = fail.breakdownstartstr
            breakdownend = ET.SubElement(row,"breakdownend")
            breakdownend.text = fail.breakdownendstr
            failuretime = ET.SubElement(row,"failuretime")
            failuretime.text = fail.breakdowntime

        stopscr.list_of_stops = []


    def createxml(self):
        global woslist
        root = ET.Element('root')
        potype = ET.SubElement(root, 'potype')
        potype.text = self.potype
        prdorder = ET.SubElement(root, 'prdorder')
        prdorder.text = self.prdorder
        confirmation = ET.SubElement(root, 'confirmation')
        confirmation.text = self.confirmation
        material = ET.SubElement(root, 'material')
        material.text = self.material
        workcenter = ET.SubElement(root, 'workcenter')
        workcenter.text = self.workcenter
        outputqlt = ET.SubElement(root, 'outputqlt')
        outputqlt.text = self.outputqlt
        setup = ET.SubElement(root, 'setup')
        setup.text = self.setup
        machine = ET.SubElement(root, 'machine')
        machine.text = self.machine
        labour = ET.SubElement(root, 'labour')
        labour.text = self.labour
        confirmdate = ET.SubElement(root, 'confirmdate')
        confirmdate.text = self.confirmdate
        workstart = ET.SubElement(root, 'workstart')
        workstart.text = self.workstart
        workend = ET.SubElement(root, 'workend')
        workend.text = self.workend
        shiftnumber = ET.SubElement(root, 'shiftnumber')
        shiftnumber.text = self.shiftnumber
        personelnum = ET.SubElement(root, 'personelnum')
        personelnum.text = self.personelnum
 
        self.add_stop(root)


        scraps = ET.SubElement(root, 'scraps')
        row = ET.SubElement(scraps, 'row')
        scrapkey = ET.SubElement(row, 'scrapkey')
        scrapkey.text = "S01"
        scrap = ET.SubElement(row, 'scrap')
        scrap.text = self.scrap

        
        woslist.append(str(ET.tostring(root))[2:-1])
 




def update_field(workorderclass : "WorkOrder",frame:tk.Frame ,field : str ):
    def __update(field,value:tk.Entry):
        commons.work_order_static_vars[commons.work_order[work_order_idx]["IE"]][field] = value.get()
        workorderclass.__init__(workorderclass.csf)

    for child in frame.winfo_children():
        child.destroy()

    tk.Label(frame,text=f"{field} için yeni değeri giriniz:",font=("Times New Roman",25),bg="white").place(relx=0.3,rely=0.3,relheight=0.2,relwidth=0.4)

    entry = tk.Entry(frame,width=20,font=("Times New Roman",25))
    entry.place(relx=0.4,relwidth=0.2,relheight=0.1,rely=0.5)

    entry.bind("<Button-1>",lambda x :NumKeyb(frame,entry))

    btn = tk.Button(frame,text="ONAYLA",font=("Times New Roman",25),command = lambda field=field, entry=entry:__update(field,entry))
    btn.place(relx=0.4,rely=0.6,relheight=0.1,relwidth=0.2)

class WorkOrder:
    def __init__(self,core_screen_functions):
        frame = base.UI()
        core_screen_functions = core_screen_functions
        self.csf = core_screen_functions
        self.ui:tk.Frame = frame.getFrame()
        core_screen_functions.left_menu()

        self.wos_subframe = tk.Frame(self.ui,bg="white")
        rel_x = commons.menu_symbol_space_width/self.ui.winfo_width()
        rel_y = 0
        
        self.wos_subframe.place(relx=rel_x,rely=rel_y,relheight=1-rel_y,relwidth=1-rel_x)
        
        self.__fill_screen()

    def change_work_order(self):
        global work_order_idx
        if(len(commons.work_order)-1 == work_order_idx):
            work_order_idx = 0
        else:
            work_order_idx += 1

        WorkOrder(self.csf)

    def __fill_screen(self):
        global kalipimage, urun_img, next_img
        bg_color = "lightskyblue"
        bg_color_2 = "skyblue"

        for child in self.wos_subframe.winfo_children():
            child.destroy()

        header_frame = tk.Frame(self.wos_subframe,bg="white",borderwidth=2)
        header_frame.place(relx=0,rely=0,relwidth=1,relheight=0.15)
        
        if(not commons.work_order):
            is_emri_adi = tk.Label(header_frame,text="İş Emri Bilgileri Çekilemedi",font=("Times New Roman",35),bg=bg_color)
            is_emri_adi.place(relheight=1,relwidth=1,relx=0,rely=0)
            return

        if(commons.work_order == "Açık iş emri yok"):
            is_emri_adi = tk.Label(header_frame,text="Açık iş emri bulunmamaktadır.",font=("Times New Roman",35),bg=bg_color)
            is_emri_adi.place(relheight=1,relwidth=1,relx=0,rely=0)
            return

        sub_header_frame = tk.Frame(self.wos_subframe,borderwidth=2)
        sub_header_frame.place(relx=0,relwidth=1,rely=0.15,relheight=0.08)

        body_frame = tk.Frame(self.wos_subframe,bg="white")
        body_frame.place(relx=0,rely=0.23,relwidth=1,relheight=0.77)



        header_label_1 = tk.Label(header_frame,text="İş Emri\nKontrol Kartı",font=("Times New Roman",35),bg=bg_color)
        header_label_1.place(relheight=1,relwidth=0.18,relx=0,rely=0)

        
        isim = commons.work_order[work_order_idx]["isim"]
        for i in range(1,(len(isim)//12)+1):
            idx = 12 * i
            isim = isim[:idx] + "\n" + isim[idx:]

        is_emri_adi = tk.Label(header_frame,text=isim,font=("Times New Roman",35),bg=bg_color)
        is_emri_adi.place(relheight=1,relwidth=0.25, relx= 0.18,rely=0)

        ie_tip = tk.Label(header_frame,text="İE Tip ve NO\n"+commons.work_order[work_order_idx]["IE"],font=("Times New Roman",35),bg=bg_color)
        ie_tip.place(relheight=1,relwidth=0.2,relx=0.43,rely=0)

        aisi = tk.Label(header_frame,text="AISI\n"+str(commons.work_order[work_order_idx]["aisi"]),font=("Times New Roman",40),bg=bg_color)
        aisi.place(relheight=1,relwidth=0.17,relx=0.63,rely=0)

        next_button = tk.Label(header_frame,bg=bg_color)
        next_button.place(relheight=1,relwidth=0.1,relx=0.9,rely=0)
        next_button.bind("<Button-1>",lambda a: self.change_work_order())
        next_button.update() 
        
        size = min(next_button.winfo_width(),next_button.winfo_height())
        
        
        try:
            next_img = nextimg.resize((size,size), Image.ANTIALIAS)
        except:
            from PIL.Image import Resampling
            next_img = nextimg.resize((size,size), Resampling.LANCZOS) 

        
        next_img = ImageTk.PhotoImage(next_img) 
        next_button.configure(image=next_img)
        next_button["image"] = next_img


        next_wo = tk.Label(header_frame,text="Sıradaki\nİş Emri",font=("Times New Roman",32),bg=bg_color)
        next_wo.place(relheight=1,relwidth=0.1,relx=0.8,rely=0)

        



        stock_code = tk.Label(sub_header_frame,bg=bg_color_2,text="Stok Kodu:"+commons.work_order[work_order_idx]["stokkod"],font=("Times New Roman",20))
        stock_code.place(relheight=1,relwidth=0.2,relx=0,rely=0)

        aciklama= tk.Label(sub_header_frame,bg=bg_color_2,text="Ürün Açıklaması:"+str(commons.work_order[work_order_idx]["urunaciklama"]),font=("Times New Roman",20))
        aciklama.place(relheight=1,relwidth=0.55,relx=0.2,rely=0)

        salkimbaskisayisi = tk.Label(sub_header_frame,bg = bg_color_2, text="Parça/Salkım Sayısı:"+str(commons.work_order[work_order_idx]["parcasalkimsayisi"]),font=("Times New Roman",28,"bold"))
        salkimbaskisayisi.place(relheight=1,relwidth=0.25,relx=0.75,rely=0)
  
        

        kaliplabel = tk.Label(body_frame,borderwidth=2,highlightthickness=3)
        kaliplabel.place(relx=0.3,relheight=0.8,relwidth=0.5,rely=0)
        kaliplabel.update()


        __data = None
        if(commons.work_order[work_order_idx]["kalip resmi"] != ""):

            __data = io.BytesIO(base64.b64decode(commons.work_order[work_order_idx]["kalip resmi"]))
        
        else:#if workorder doesnt have cast image.
            for wo in commons.work_order:
                if("kalip resmi" in wo and wo["kalip resmi"] != ""): 
                    __data = io.BytesIO(base64.b64decode(wo["kalip resmi"][2:-1]))

        
        if(__data != None and __data.read() != b"" ):

            # print("---kalip img",commons.work_order[work_order_idx]["kalip resmi"])
            kalipimg = Image.open(__data)

            
            try:
                kalipimage = kalipimg.resize((kaliplabel.winfo_width(),kaliplabel.winfo_height()), Image.ANTIALIAS)
            except:
                from PIL.Image import Resampling
                kalipimage = kalipimg.resize((kaliplabel.winfo_width(),kaliplabel.winfo_height()), Resampling.LANCZOS) 

 

            kalipimage = ImageTk.PhotoImage(kalipimage)
            kaliplabel.configure(image=kalipimage)
            kaliplabel["image"] = kalipimage


        else:
            kaliplabel.configure(text="Kalıp resmi sistemde bulunamadı.",font=("times new roman",25,"bold"))


        urun_label = tk.Label(body_frame,highlightthickness=3)
        urun_label.place(relx=0,rely=0.35,relheight=0.45,relwidth=0.3)
        urun_label.update()
        try:
            __data = io.BytesIO(base64.b64decode(commons.work_order[work_order_idx]["urun resmi"]))
            
            urun_img = Image.open(__data)



    

            try:
                urun_img = urun_img.resize((urun_label.winfo_width(),urun_label.winfo_height()), Image.ANTIALIAS)
            except:
                from PIL.Image import Resampling
                urun_img = urun_img.resize((urun_label.winfo_width(),urun_label.winfo_height()), Resampling.LANCZOS) 
            
            urun_img = ImageTk.PhotoImage(urun_img)
            urun_label.configure(image=urun_img)
            urun_label["image"] = urun_img

            urun_label.update()
        except:
            urun_label.configure(text="RESİM BULUNAMADI.")

        __kalip_ismi_text = commons.work_order[work_order_idx]["kalipadno"]
        for i in range(1,(len(__kalip_ismi_text)//15)+1):
            idx = 15 * i
            __kalip_ismi_text = __kalip_ismi_text[:idx] + "\n" + __kalip_ismi_text[idx:]


        ####iş emri ekranı alt kısımda ki veriler
        kalip_ismi_label = tk.Label(body_frame,bg="white",text=__kalip_ismi_text,font=("Times New Roman",35),highlightthickness=1)
        kalip_ismi_label.place(relx=0,rely=0,relwidth=0.3,relheight=0.15)

        press_baski_say_label = tk.Label(body_frame,bg="white",text="Pres Baskı Sayısı\n"+str(commons.work_order[work_order_idx]["presbaskisayisi"]),highlightthickness=1,font=("Times New Roman",35))
        press_baski_say_label.place(relx=0.8,relwidth=0.2,relheight=0.2,rely=0.6)


        kalip_sira_label = tk.Label(body_frame,bg="white",text="Kalıptaki\nSırası:\n"+str(commons.work_order[work_order_idx]["kalipsira"]),font=("Times New Roman",35),highlightthickness=1)
        kalip_sira_label.place(relx=0,relwidth=0.15,relheight=0.2,rely=0.15)


        kalip_sayi_label = tk.Label(body_frame,bg="white",text="Kalıptaki\nSayısı:\n"+str(commons.work_order[work_order_idx]["kalipsayi"]),font=("Times New Roman",35),highlightthickness=1)
        kalip_sayi_label.place(relx=0.15,relwidth=0.15,relheight=0.2,rely=0.15)

        is_merkezi_label = tk.Label(body_frame,bg="white",text="İş Merkezi:"+str(commons.work_order[work_order_idx]["ismerkezi"]),font=("Times New Roman",20),highlightthickness=1)
        is_merkezi_label.place(relx=0,rely=0.8,relheight=0.1,relwidth=0.2)

        araclar_label = tk.Label(body_frame,bg="white",text="Araçlar:"+str(commons.work_order[work_order_idx]["araçlar"]),font=("Times New Roman",20),highlightthickness=1)
        araclar_label.place(relx=0.2,rely=0.8,relheight=0.1,relwidth=0.2)

        operasyon_label = tk.Label(body_frame,bg="white",text="Operasyon:\n"+str(commons.work_order[work_order_idx]["operasyon"]),font=("Times New Roman",20),highlightthickness=1)
        operasyon_label.place(relx=0.4,rely=0.8,relheight=0.1,relwidth=0.1)

        mum_font = 20

        __operasyon_tanim_text = commons.work_order[work_order_idx]["operasyontanim"]
        __operasyon_tanim_font_size = 20 if (len(__operasyon_tanim_text) // 19) < 3 else 12
        for i in range(1,(len(__operasyon_tanim_text)//19)+1):
            idx = 19 * i   
            __operasyon_tanim_text = __operasyon_tanim_text[:idx] + "\n" + __operasyon_tanim_text[idx:]
        


        operasyon_tanim_label = tk.Label(body_frame,bg="white",text="Operasyon Tanımı:\n"+__operasyon_tanim_text,font=("Times New Roman",__operasyon_tanim_font_size),highlightthickness=1)
        operasyon_tanim_label.place(relx=0.5,rely=0.8,relheight=0.1,relwidth=0.2)


        hazirlik_suresi_label=tk.Label(body_frame,bg="white",text="Hazırlık Süresi:"+str(commons.work_order[work_order_idx]["hazirliksure"]),font=("Times New Roman",20),highlightthickness=1)
        hazirlik_suresi_label.place(relx=0,rely=0.9,relheight=0.1,relwidth=0.2)

        birim_uretim_suresi_label=tk.Label(body_frame,bg="white",text="Birim Üretim Süresi:"+str(commons.work_order[work_order_idx]["birimuretimsuresi"]),font=("Times New Roman",20),highlightthickness=1)
        birim_uretim_suresi_label.place(relx=0.2,rely=0.9,relheight=0.1,relwidth=0.2)

        toplam_uretim_suresi=tk.Label(body_frame,bg="white",text="Toplam Üretim Süresi:"+str(commons.work_order[work_order_idx]["toplamuretimsuresi"]),font=("Times New Roman",20),highlightthickness=1)
        toplam_uretim_suresi.place(relx=0.4,rely=0.9,relheight=0.1,relwidth=0.2)
        
        malzeme_num_suresi=tk.Label(body_frame,bg="white",text="Malzeme Num:"+str(commons.work_order[work_order_idx]["malzemenum"]),font=("Times New Roman",20),highlightthickness=1)
        malzeme_num_suresi.place(relx=0.6,rely=0.9,relheight=0.1,relwidth=0.2)

        uretim_adet_label=tk.Label(body_frame,bg="white",text="Baskı Sayısı\n"+str(commons.modbus_map["otomatik uretim adeti"][2]),font=("Times New Roman",20),highlightthickness=1)
        uretim_adet_label.place(relx=0.7,rely=0.8,relheight=0.1,relwidth=0.1)

        onay_no_label = tk.Label(body_frame,bg="white",text="Onay No:\n"+str(commons.work_order[work_order_idx]["onayno"]),font=("Times New Roman",20),highlightthickness=1)
        onay_no_label.place(relx=0.8,rely=0.9,relheight=0.1,relwidth=0.1)


        
        totalCount = 0
        if("totalCount" in commons.work_order_static_vars[commons.work_order[work_order_idx]["IE"]].keys() ):
            totalCount = commons.work_order_static_vars[commons.work_order[work_order_idx]["IE"]]["totalCount"]
        else:
            totalCount = int(commons.modbus_map["otomatik uretim adeti"][2]) * int(commons.work_order[work_order_idx]["kalipsayi"])  

        toplam_uretim_label = tk.Label(body_frame,bg="white",text="Toplam Üretim:\n"+str(totalCount),font=("Times New Roman",20),highlightthickness=1)
        toplam_uretim_label.place(relx=0.8,rely=0.8,relheight=0.1,relwidth=0.1)

        __val = int(commons.work_order[work_order_idx]["kalipsayi"])
        if(__val == 0):
            __val = 1
        kalanbaskisayisi = int(commons.work_order[work_order_idx]["presbaskisayisi"]) - (int(commons.work_order[work_order_idx]["onaylanan miktar"]) / __val)

        kalanbaskilabel = tk.Label(body_frame,bg="white",text="Gerekli Baskı:\n"+str(int(kalanbaskisayisi)),font=("Times New Roman",20),highlightthickness=1)
        kalanbaskilabel.place(relx=0.9,rely=0.8,relheight=0.1,relwidth=0.1)


        onaylimiktarlabel = tk.Label(body_frame,bg="white",text="Onaylı Miktar\n"+str(commons.work_order[work_order_idx]["onaylanan miktar"]),
                                         highlightthickness=1,font=("Times New Roman",20))
        onaylimiktarlabel.place(relx=0.9,relwidth=0.1,relheight=0.1,rely=0.9)
        ##########################
        ###iş emri ekranı sağda ki butonlar
  
        mum_agirlik_buton = tk.Button(body_frame,text=f"Mum Ağırlığı:{commons.work_order_static_vars[commons.work_order[work_order_idx]['IE'] ]['mumagirlik']}\nDeğiştirmek için Tıkla",
                                      font=("Times New Roman",25),command=lambda : update_field(self,body_frame,"mumagirlik"))
        mum_agirlik_buton.place(relx=0.8,relwidth=0.2,relheight=0.2,rely=0)

        fire_guncelle_buton = tk.Button(body_frame,text=f"Fire:{commons.work_order_static_vars[commons.work_order[work_order_idx]['IE'] ]['fire']}\nDeğiştirmek için Tıkla",
                                        font=("Times New Roman",25),command=lambda : update_field(self,body_frame,"fire"))
        fire_guncelle_buton.place(relx=0.8,relwidth=0.2,relheight=0.2,rely=0.2)
        
        is_emri_onay_buton = tk.Button(body_frame,text="İş Emrini Onayla",bg="pale green",font=("Times New Roman",25),command = lambda:self.approve_screen())
        is_emri_onay_buton.place(relx=0.8,relwidth=0.2,relheight=0.2,rely=0.4)

    def updateScreen(self,idx):
        updatescrframe = tk.Frame(self.approve_screen_frame)
        updatescrframe.place(relheight=1,relwidth=1,relx=0,rely=0)

        tk.Label(updatescrframe,text="Yeni Değeri Giriniz",font=("Times New Roman",55)).place(relheight=0.2,relwidth=1,relx=0,rely=0.5)

        entry = tk.Entry(updatescrframe,font=("Times New Roman",35))
        entry.place(relheight=0.1,relwidth=0.2,relx=0.4,rely=0.65)
        entry.bind("<Button-1>",lambda x :NumKeyb(updatescrframe,entry))

        def __update(val):
            commons.work_order_static_vars[commons.work_order[idx]["IE"]]["totalCount"] = val

        btn = tk.Button(updatescrframe, text="Onayla",font=("Times New Roman",35), command= lambda : [__update(int(entry.get())),self.approve_screen_frame.destroy(), self.approve_screen(idx)]  )
        btn.place(relheight=0.1,relwidth=0.1,relx=0.45,rely=0.8)


    def approve_screen(self, idx = 0):
        global urun_img

        #hepsi onaylanmıştır.
        if(idx == len(commons.work_order)): 
            tlm.upload_telemetry({"workorders_approve":woslist.copy()})
            woslist.clear()
            self.__fill_screen()
            return
        
        
        self.approve_screen_frame = tk.Frame(self.wos_subframe)
        self.approve_screen_frame.place(relx=0,relheight=1,relwidth=1,rely=0)

        
        urun_label = tk.Label(self.approve_screen_frame,highlightthickness=1)
        urun_label.place(relx=0.3,rely=0.002,relheight=0.5,relwidth=0.4)
        urun_label.update()
        
        if(commons.work_order[idx]["urun resmi"] != ""):
            __data = io.BytesIO(base64.b64decode(commons.work_order[idx]["urun resmi"]))
            urun_img = Image.open(__data)

            try:
                urun_img = urun_img.resize((urun_label.winfo_width(),urun_label.winfo_height()), Image.ANTIALIAS)
            except:
                from PIL.Image import Resampling
                urun_img = urun_img.resize((urun_label.winfo_width(),urun_label.winfo_height()),  Resampling.LANCZOS) 

            urun_img = ImageTk.PhotoImage(urun_img)
            urun_label.configure(image=urun_img)
            urun_label["image"] = urun_img
            urun_label.update()

        else:
            urun_label.configure(text="Resim yüklenemedi.")



        


        
        


        #eğer fire hiç belirlenmemişse:
        if(commons.work_order[idx]['fire'] == ""):
            session = dbm.get_session()
            fire = session.query(dbm.PressRecords).filter(dbm.PressRecords.fire == 1).count()
            commons.work_order[idx]['fire'] = fire
        totalCount = 0
        if("totalCount" in commons.work_order_static_vars[commons.work_order[idx]["IE"]].keys() ):
            totalCount = commons.work_order_static_vars[commons.work_order[idx]["IE"]]["totalCount"]
        else:
            totalCount = int(commons.modbus_map["otomatik uretim adeti"][2]) * int(commons.work_order[idx]["kalipsayi"])

        lbl = tk.Label(self.approve_screen_frame,font=("Times New Roman",25),
                        text="İş Emri\n"+str(commons.work_order[idx]["IE"]),highlightthickness=1,highlightbackground="black")
        lbl.place(relheight=0.1,relwidth=1,relx=0,rely=0.4)

        lbl = tk.Label(self.approve_screen_frame,font=("Times New Roman",25),
                        text="Toplam Miktar:"+str(totalCount),highlightthickness=1,highlightbackground="black")
        lbl.place(relheight=0.1,relwidth=1,relx=0,rely=0.5)
        
        update_button = tk.Button(self.approve_screen_frame,text="Güncelle",font=("Times New Roman",35), bd=5)
        update_button.configure(command=lambda idx=idx: self.updateScreen(idx))
        update_button.place(relheight=0.08,relwidth=0.13,relx=0.85,rely=0.51)
        
        lbl = tk.Label(self.approve_screen_frame,font=("Times New Roman",25),
                        text="Fire:"+str(commons.work_order[idx]['fire']),highlightthickness=1,highlightbackground="black")
        lbl.place(relheight=0.1,relwidth=1,relx=0,rely=0.6)


        lbl = tk.Label(self.approve_screen_frame,font=("Times New Roman",25),
                        text="Mum Ağırlık:"+str(commons.work_order_static_vars[commons.work_order[idx]['IE'] ]['mumagirlik']),highlightthickness=1,highlightbackground="black")
        lbl.place(relheight=0.1,relwidth=1,relx=0,rely=0.7)

        backbutton = tk.Button(self.approve_screen_frame,text="Geri",command=lambda:self.approve_screen_frame.destroy(),font=("Times New Roman",35),bd=7)
        backbutton.place(relx=0.3, relheight=0.12,relwidth=0.15,rely=0.85)

        approvebutton = tk.Button(self.approve_screen_frame,text="Onayla",font=("Times New Roman",35),bd=7,command=lambda waste = commons.work_order_static_vars[commons.work_order[idx]['IE'] ]['fire']: [wos(idx,totalCount,waste),
                                                                                                                             self.approve_screen(idx + 1)])
        approvebutton.place(relx=0.55, relheight=0.12,relwidth=0.15,rely=0.85)


