import base
import tkinter as tk
from tkinter import ttk
import commons
from datetime import datetime,timedelta
import matplotlib
matplotlib.use('TkAgg')
import database_models as dbm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import time
import numpy as np



class History:
    def __init__(self,core_screen_functions):
        frame = base.UI()
        # print(frame.mw.focus_get())
        core_screen_functions = core_screen_functions
        self.ui:tk.Frame = frame.getFrame()
        core_screen_functions.left_menu()
        self.canvas:tk.Canvas = self.ui.nametowidget("main canvas")
        self.create_top_info()
        self.history_subframe = tk.Frame(self.canvas,bg="white")
        rel_x = commons.menu_symbol_space_width/self.ui.winfo_width()
        rel_y = int(self.ui.winfo_height()/commons.menu_icon_number)/self.ui.winfo_height()
        
        self.history_subframe.place(relx=rel_x,rely=rel_y,relheight=1-rel_y,relwidth=1-rel_x)
        PressTab(self.history_subframe)

    def create_top_info(self):
        """
        this function creates rectangles and texts on the upper side of main screen
        """
        data_tags = [("Duruşlar"),
                     ("Baskılar"),
                     ("Grafikler")]
        


        width_for_top_menu = (self.ui.winfo_width()-commons.menu_symbol_space_width)/commons.history_top_number
        height_for_top_menu = int(self.ui.winfo_height()/commons.menu_icon_number)

        _images = [(tk.PhotoImage(file='icons/StopsButtonIcon.png'),lambda : StopsTab(self.history_subframe)),
                   (tk.PhotoImage(file='icons/RecordsButtonIcon.png'),lambda : PressTab(self.history_subframe)),
                   (tk.PhotoImage(file='icons/GraphButtonIcon.png'),lambda : draw_graphs(self.history_subframe) )]

        for tab in range(commons.history_top_number):

            self.canvas.create_rectangle((tab*width_for_top_menu)+commons.menu_symbol_space_width,
                                         0,
                                         ((tab+1)*width_for_top_menu)+commons.menu_symbol_space_width,
                                         height_for_top_menu,width=commons.line_size)
            
            #Let us create a dummy button and pass the image
            button= tk.Button(self.canvas,image=_images[tab][0],command= _images[tab][1],
                              compound=tk.TOP, borderwidth=0, bg=commons.common_background,justify="center")
            button.image = _images[tab][0]

            #this is calculate relative position of button
            _relx = ((tab*width_for_top_menu)+commons.menu_symbol_space_width)/self.ui.winfo_width()
            _rely = 0
            _relwidth = width_for_top_menu/self.ui.winfo_width()
            _relheight = height_for_top_menu / self.ui.winfo_height()

            button.place(relx=_relx,rely=_rely,relheight=_relheight,relwidth=_relwidth)

class draw_graphs:
    def __init__(self,subframe,deger="kazan",days = 1):
        frame = base.UI()
        self.ui:tk.Frame = frame.getFrame() 
        self.canvas:tk.Canvas = self.ui.nametowidget("main canvas") 
        
        for widget in subframe.winfo_children():
            widget.destroy()
        #Zaman kalırsa bu fonksiyonun düzenlenmesi lazım.
        __start = time.time()
        try:
            self.draw_canvas
            del(self.draw_canvas)
        except:
            pass
        self.draw_canvas = subframe
         
        start = time.time()
        session = dbm.get_session()
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            if(deger == "kazan"):   results = session.query(dbm.TemperatureReading).with_entities(dbm.TemperatureReading.timestamp,dbm.TemperatureReading.kazan).filter(
                                    dbm.TemperatureReading.timestamp >= start_date,
                                    dbm.TemperatureReading.timestamp <= end_date)

            
            if(deger == "bogaz"):   results = session.query(dbm.TemperatureReading).with_entities(dbm.TemperatureReading.timestamp,dbm.TemperatureReading.bogaz).filter(
                                    dbm.TemperatureReading.timestamp >= start_date,
                                    dbm.TemperatureReading.timestamp <= end_date)
            if(deger == "hidrolik"):   results = session.query(dbm.TemperatureReading).with_entities(dbm.TemperatureReading.timestamp,dbm.TemperatureReading.hidrolik).filter(
                                    dbm.TemperatureReading.timestamp >= start_date,
                                    dbm.TemperatureReading.timestamp <= end_date)
            
        except Exception as e:
            print("couldn't retrieve data.",e)
        finally:
            session.close()
        # print("veritabanı çekim süresi",time.time()-start)


        # Grafik oluşturma
        fig, ax = plt.subplots()
        
        timestamps = mdates.date2num([result.timestamp for result in results])
        # print(timestamps)
        
        start = time.time()
        if(deger == "kazan"):
            kazan_values = [result.kazan for result in results]
            # print("time for plotting1:",time.time()-start)
            # print(kazan_values)
            line_kazan, = ax.plot(timestamps, kazan_values, label=deger)
            # print("time for plotting2:",time.time()-start)
        if(deger == "bogaz"):
            bogaz_values = [result.bogaz for result in results]
            line_bogaz, = ax.plot(timestamps, bogaz_values, label='Bogaz')
        if(deger == "hidrolik"):
            hidrolik_values = [result.hidrolik for result in results]
            line_hidrolik, = ax.plot(timestamps, hidrolik_values, label='Hidrolik')
        
        ax.set_xlabel('Zaman')
        ax.set_ylabel('Değerler')
        ax.set_title('Verilerin Grafiği')
        """
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        
        ax.xaxis.set_major_locator(plt.MaxNLocator(8))
        """
    

        ax.legend()
        #plt.close() 
        start = time.time()
        
        # Matplotlib figürünü Tkinter penceresine yerleştirme
        __canvas = FigureCanvasTkAgg(fig, master=self.draw_canvas)
        __canvas.draw()
        # print("time for drawing:",time.time()-start)
        __canvas.get_tk_widget().place(relx=0,rely=0,relwidth=1,relheight=0.9) 
        


        kazan_button = tk.Button(self.draw_canvas,bg="white",font=("Times New Roman",30),text="Kazan Sıcaklıkları",command= lambda :draw_graphs(subframe,"kazan"))
        kazan_button.place(relx=0,rely=0.91,relwidth=0.33,relheight=0.08)

        bogaz_button = tk.Button(self.draw_canvas,bg="white",font=("Times New Roman",30),text="Bogaz Sıcaklıkları",command= lambda :draw_graphs(subframe,"bogaz"))
        bogaz_button.place(relx=0.33,rely=0.91,relwidth=0.33,relheight=0.08)

        hidrolik_button = tk.Button(self.draw_canvas,bg="white",font=("Times New Roman",30),text="Hidrolik Sıcaklıkları",command= lambda :draw_graphs(subframe,"hidrolik"))
        hidrolik_button.place(relx=0.66,rely=0.91,relwidth=0.33,relheight=0.08)
        
        # print("Toplam Süre",time.time()-__start)



class PressTab:
    def __init__(self,subframe: tk.Frame): 
        frame = base.UI()
        self.ui:tk.Frame = frame.getFrame() 
        # self.canvas:tk.Canvas = self.ui.nametowidget("main canvas")
        self.canvas = subframe
        for widget in self.canvas.winfo_children():

            widget.destroy()
        self.__selecteds = []
        self.place_tree()
        

    def place_tree(self):
        arrow_size = 100
        scrollbar_width = arrow_size/self.ui.winfo_width() 

        button_height = 0.12
        
        style = ttk.Style(self.canvas)
        style.map('my.Treeview', background=[], foreground=[])
        style.configure('Treeview', rowheight=110)

        self.tree = ttk.Treeview(self.canvas,style='my.Treeview', columns=("Üretim Numarası", "Fire", "Zaman"), selectmode="extended",height=20)
        self.tree.tag_configure("fire",background="pale violet red", font=("Times New Roman",25))
        self.tree.tag_configure("normal",background="white", font=("Times New Roman",25))
        self.tree.tag_configure("selection",background="goldenrod", font=("Times New Roman",25))
        rel_x = 0
        rel_y = 0

        self.tree['show'] = 'headings'
        # Sütunlar için başlıkları belirle
        self.tree.heading("Üretim Numarası", text="Üretim Numarası")
        self.tree.heading("Fire", text="Fire")
        self.tree.heading("Zaman", text="Zaman")

        self.tree.column(0, anchor="center")
        self.tree.column(1, anchor="center")
        self.tree.column(2, anchor="center")



        self.tree.place(relx=rel_x,rely=rel_y,relheight=1-rel_y-button_height,relwidth=1-rel_x-scrollbar_width)
        self.tree.bind("<Button-1>",self.selection_manaeger)


        try:
            style.element_create("My.Vertical.TScrollbar.trough", "from", "clam")
            style.element_create("My.Vertical.TScrollbar.thumb", "from", "clam")
            style.element_create("My.Vertical.TScrollbar.grip", "from", "clam")
        except tk.TclError:
            pass

        except Exception as e:
            print("Error while creating styles ",e)


        style.layout("My.Vertical.TScrollbar",
        [('My.Vertical.TScrollbar.trough',
            {'children': [('My.Vertical.TScrollbar.thumb',
                            {'unit': '1',
                            'children':
                                [('My.Vertical.TScrollbar.grip', {'sticky': ''})],
                            'sticky': 'nswe'})
                        ],
            'sticky': 'ns'})])

        style.configure("My.Vertical.TScrollbar", gripcount=0, background="#b0b0b0",
                        troughcolor='#252526', borderwidth=2, bordercolor='#252526',
                        lightcolor='#252526', darkcolor='#252526',
                        arrowsize=100) 

        y_scrollbar = ttk.Scrollbar(self.canvas, orient="vertical", command=self.tree.yview, style="My.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=y_scrollbar.set)
        y_scrollbar.place(relx=1-scrollbar_width, rely=rel_y,relwidth=scrollbar_width,relheight=1-rel_y-button_height)

        mark_button = tk.Button(self.canvas,text="Onayla",command=self.mark,font=("Times New Roman",25))
        mark_button.place(relx=0.4,relwidth=0.2,rely=1-button_height,relheight=button_height)

        self.insert_into_table()
    def mark(self):
        try:
            session = dbm.get_session()
            results = session.query(dbm.PressRecords).all()[::-1]

            marked_indexes = [self.tree.index(i) for i in self.__selecteds]
            for idx in range(len(results)):
                if(idx not in marked_indexes):
                    continue
                results[idx].fire = not results[idx].fire
            
            session.commit()
        except Exception as e:
            print("error while uploading wasteds.",e)

        finally:
            # print(commons.work_order)
            for wo in commons.work_order:
                wo["fire"] = session.query(dbm.PressRecords).filter(dbm.PressRecords.fire == 1).count()
                # print("fire:",session.query(dbm.PressRecords).filter(dbm.PressRecords.fire == 1).count())
            session.close()
            PressTab(self.canvas)



    def insert_into_table(self):
        
        if(not self.tree):
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except tk.TclError as e:

            print("tree is:",self.tree)
            print("self.tree silinirken minik problem oluştu devam ediliyor.",e)
            return

        try:
            session = dbm.get_session()
            results = session.query(dbm.PressRecords).order_by(dbm.PressRecords.id.desc()).limit(100)
            session.close()
            idx = 0
            for result in results[::]:
                self.tree.insert("","end",iid=f"item{idx}",values=(result.production_id,"Fire" if result.fire else "Normal",result.timestamp.strftime('%Y-%m-%d %H:%M:%S')))
                idx += 1
            for child in self.tree.get_children():
                if self.tree.item(child)["values"][1] == "Normal":
                    self.tree.item(child,tag = "normal")

                if self.tree.item(child)["values"][1] == "Fire":
                    self.tree.item(child,tag = "fire")

                if child in self.__selecteds:
                    self.tree.item(child, tag="selection")

            self.tree.update()

        except Exception as e:
            print("press records couldn't taken.",e)
            session.close()

        self.tree.after(1000,self.insert_into_table)



    def selection_manaeger(self,event):
        item = self.tree.identify('item',event.x,event.y)
        
        if(item in self.__selecteds):
            self.__selecteds.remove(item)
            if(self.tree.item(item)["values"][1] == "Fire"):
                self.tree.item(item, tags='fire')
            else:
                self.tree.item(item, tags='normal')

        else:
            self.__selecteds.append(item)
            self.tree.item(item, tags='selection')


class StopsTab:
    def __init__(self,subframe: tk.Frame): 
        frame = base.UI()
        self.ui:tk.Frame = frame.getFrame()  
        self.canvas = subframe
        for widget in self.canvas.winfo_children():
            widget.destroy()
            
        self.place_tree()


    def place_tree(self):
        arrow_size = 100
        scrollbar_width = arrow_size/self.ui.winfo_width() 

        
        style = ttk.Style(self.canvas)
        style.map('my.Treeview', background=[], foreground=[])
        style.configure('Treeview', rowheight=110)
        style.configure("Treeview.Heading", font=(None, 17))

        self.tree = ttk.Treeview(self.canvas,style='my.Treeview',
                                  columns=("Duruş_Nedeni", "Personel", "Başlangıç", "Toplam_Zaman"),
                                  selectmode="extended",
                                  height=20)
        self.tree.tag_configure("normal",background="white", font=("Times New Roman",25)) 
        rel_x = 0
        rel_y = 0

        self.tree['show'] = 'headings'
        # Sütunlar için başlıkları belirle
        self.tree.heading("Duruş_Nedeni", text="Duruş Nedeni")
        self.tree.heading("Personel", text="Personel")
        self.tree.heading("Başlangıç", text="Başlangıç")
        self.tree.heading("Toplam_Zaman", text="Toplam Zaman")

        self.tree.column(0, anchor="center")
        self.tree.column(1, anchor="center")
        self.tree.column(2, anchor="center")
        self.tree.column(3, anchor="center")



        self.tree.place(relx=rel_x,rely=rel_y,relheight=1-rel_y,relwidth=1-rel_x-scrollbar_width)


        try:
            style.element_create("My.Vertical.TScrollbar.trough", "from", "clam")
            style.element_create("My.Vertical.TScrollbar.thumb", "from", "clam")
            style.element_create("My.Vertical.TScrollbar.grip", "from", "clam")
        except tk.TclError:
            pass

        except Exception as e:
            print("Error while creating styles ",e)


        style.layout("My.Vertical.TScrollbar",
        [('My.Vertical.TScrollbar.trough',
            {'children': [('My.Vertical.TScrollbar.thumb',
                            {'unit': '1',
                            'children':
                                [('My.Vertical.TScrollbar.grip', {'sticky': ''})],
                            'sticky': 'nswe'})
                        ],
            'sticky': 'ns'})])

        style.configure("My.Vertical.TScrollbar", gripcount=0, background="#b0b0b0",
                        troughcolor='#252526', borderwidth=2, bordercolor='#252526',
                        lightcolor='#252526', darkcolor='#252526',
                        arrowsize=100) 

        y_scrollbar = ttk.Scrollbar(self.canvas, orient="vertical", command=self.tree.yview, style="My.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=y_scrollbar.set)
        y_scrollbar.place(relx=1-scrollbar_width, rely=rel_y,relwidth=scrollbar_width,relheight=1-rel_y)

        self.insert_into_table()

    def insert_into_table(self):
        def calculate_time_difference(start_time, end_time):
            time_difference = end_time - start_time
            total_seconds = time_difference.total_seconds()

            hours = str(int(total_seconds // 3600))
            minutes = str(int((total_seconds % 3600) // 60))
            seconds = str(int(total_seconds % 60))

            hours = "0" + hours if len(hours) == 1 else hours
            minutes = "0" + minutes if len(minutes) == 1 else minutes
            seconds = "0" + seconds if len(seconds) == 1 else seconds

            return f"{hours}:{minutes}:{seconds}"

        
        if(not self.tree):
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except tk.TclError as e:

            print("tree is:",self.tree)
            print("self.tree silinirken minik problem oluştu devam ediliyor.",e)
            return

        try:
            session = dbm.get_session()
            results = session.query(dbm.Stops).all()
            for result in results[::-1]:
                self.tree.insert("","end",values=(result.durus_nedeni,
                                                  result.Personel,
                                                  result.durus_baslangic.strftime('%Y-%m-%d %H:%M:%S'),
                                                  calculate_time_difference(result.durus_baslangic,result.durus_bitis)),tags="normal")
            
        except Exception as e:
            print("error while reading from database-stops.",e)

        finally:
            session.close()
