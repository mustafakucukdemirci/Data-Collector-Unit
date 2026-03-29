import tkinter
from tkinter.font import Font
import time

class fullKeyb:
    def __init__(self,mainWindow,entry):
        self.callbacks = []
        self.mw = mainWindow
        self.newWindow = tkinter.Toplevel(mainWindow)
        self.newWindow.resizable(True,False)
        self.newWindow.lift()
        self.newWindow.attributes('-topmost', 1)
        buttonNums = ["q","w","e","r","t","y","u","ı","o","p","ü","0","1","2","3","a","s","d","f","g","h","j","k","l","ş","i","KAYDR","4","5","6","z","x","c","v","b","n",
                   "m","ö","ç",".","SİL","KAPAT","7","8","9"]
        #buttonNums = ["1","2","3","4","5","6","7","8","9","0","clear",",","close"]
        height = mainWindow.winfo_screenheight()
        width = mainWindow.winfo_screenwidth()
        
        keyPerRow = 15
        
        widthPerKey = int(width/keyPerRow)-2
        heightPerKey = int(height/7)
        self.newWindow.geometry(str(width)+"x"+str(int(heightPerKey)*3)+"+10+10")
        
        keyboardFont = Font(family='times new roman', size=50, weight='bold')
        self.entry = entry
        buttonsArray = []
        for i in range(3):
            for y in range(keyPerRow):
                buttonsArray.append(tkinter.Button(self.newWindow,text=buttonNums[(i*keyPerRow)+y],font=keyboardFont))
                buttonsArray[(i*keyPerRow)+y].place(x=widthPerKey*y,y=heightPerKey*i,height=heightPerKey,width=widthPerKey)
                buttonsArray[(i*keyPerRow)+y].configure(command=lambda text = buttonsArray[(i*keyPerRow)+y]["text"]:self.fillEntryBox(text))
                if(buttonNums[(i*keyPerRow)+y] == "KAPAT"):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",10,"bold"),command=lambda: [self.newWindow.destroy(),self.callback()] )
                elif("SİL" in buttonNums[(i*keyPerRow)+y]):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",25,"bold"),command=lambda:self.entry.delete(0,"end"))
                elif("KAYDR" in buttonNums[(i*keyPerRow)+y]):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",10,"bold"))
                    buttonsArray[(i*keyPerRow)+y].bind("<B1-Motion>", lambda x:self.moveWindow(x))
                    
        self.newWindow.bind("<FocusOut>",lambda x:self.newWindow.destroy())
    def moveWindow(self,event):
        old_y = event.y
        y=self.mw.winfo_pointery() - self.mw.winfo_rooty()
        self.newWindow.geometry("+0+"+str(int(y)))
        
    def fillEntryBox(self,text):
        if(text != "KAYDR"):
            self.entry.insert("end",text)

    def addCallback(self,function,*args):
        self.callbacks.append({function:args})

    def callback(self):
        for i in self.callbacks:
            for func,params in i.items():
                func(params)
        

class NumKeyb:
    def __init__(self,mainWindow,entry):
        self.mw = mainWindow
        self.newWindow = tkinter.Toplevel(mainWindow)
        self.newWindow.resizable(True,False)
        self.newWindow.lift()
        self.newWindow.attributes('-topmost', 1) 
        buttonNums = ["1","2","3","SİL","KAYDIR","4","5","6",".","KAPAT","7","8","9","0"]
        height = mainWindow.winfo_screenheight()
        width = mainWindow.winfo_screenwidth()
        
        keyPerRow = 5
        
        widthPerKey = int(width/keyPerRow)-10
        heightPerKey = int(height/9)
        self.newWindow.geometry(str(width)+"x"+str(int(heightPerKey)*3)+"+10+10")
        
        keyboardFont = Font(family='times new roman', size=50, weight='bold')
        self.entry = entry
        buttonsArray = []

        # self.newWindow.bind("<B1-Motion>", lambda x:self.moveWindow(x))


        for i in range(3):
            for y in range(keyPerRow):
                if((keyPerRow*i)+y >= len(buttonNums)):
                    break
                buttonsArray.append(tkinter.Button(self.newWindow,text=buttonNums[(i*keyPerRow)+y],font=keyboardFont))
                buttonsArray[(i*keyPerRow)+y].place(x=widthPerKey*y,y=heightPerKey*i,height=heightPerKey,width=widthPerKey)
                buttonsArray[(i*keyPerRow)+y].configure(command=lambda text = buttonsArray[(i*keyPerRow)+y]["text"]:self.fillEntryBox(text))
                if(buttonNums[(i*keyPerRow)+y] == "KAPAT"):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",25,"bold"),command=lambda: self.newWindow.destroy())
                elif("SİL" in buttonNums[(i*keyPerRow)+y]):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",25,"bold"),command=lambda:self.entry.delete(0,"end"))
                elif("KAY" in buttonNums[(i*keyPerRow)+y]):
                    buttonsArray[(i*keyPerRow)+y].configure(font=("times new roman",25,"bold"))
                    buttonsArray[(i*keyPerRow)+y].bind("<B1-Motion>", lambda x:self.moveWindow(x))
                    
        self.newWindow.bind("<FocusOut>",lambda x:self.newWindow.destroy())

    def moveWindow(self,event):
        y=self.mw.winfo_pointery() - self.mw.winfo_rooty()
        self.newWindow.geometry("+0+"+str(int(y)))
        
    def fillEntryBox(self,text):
        self.entry.insert("end",text)

