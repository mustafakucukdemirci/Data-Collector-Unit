from time import sleep
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from database_models import Counter
from threading import Thread
from threading import Lock as threadlock 
from commons import modbus_map as mb
import keyboard
import sys
import commons as cms
import random
import time
import serial
import threading
import re
from sys import platform
import datetime

# GPIO kontrolörü oluştur 
kill_thread_var = False
COM_PORT = "COM9"
BAUD_RATE = 2400
TIMEOUT = 5  # Serial timeout

if platform != "win32":
    COM_PORT = "/dev/ttyUSB0"

comport = serial.Serial(COM_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)
last_received_time = time.time()  # Son veri alınan zaman

def reset_arduino():
    """Arduino'yu resetler (DTR pinini kullanarak)"""
    global comport
    print(datetime.datetime.now().strftime("%HH %mm %SS"), "⚠️  Veri alınamadı, Arduino resetleniyor... ⚠️")
    comport.setDTR(False)  # DTR'yi kapat (Reset işlemi)
    time.sleep(0.5)  # Bekle (Donanımsal reset için)
    comport.setDTR(True)  # DTR'yi tekrar aç
    time.sleep(2)  # Arduino'nun boot olması için bekle
    comport.reset_input_buffer()  # Seri buffer'ı temizle
    print("✅  Arduino resetlendi.")

def reset_counter():
    mb["otomatik uretim adeti"][2] = 0

def get_counter(): 
    """Counter tablosundaki ilk (ve tek) satırı döndürür."""
    counter = mb["otomatik uretim adeti"][2]
    return counter

def update_counter(new_value=None):  
    """Mevcut satırın değerini günceller.""" 
    if new_value is not None:
        mb["otomatik uretim adeti"][2] = new_value
    else:
        mb["otomatik uretim adeti"][2] += 1  # Mevcut değeri artır

def parse_data(data):
    match = re.match(r"<([\d.]+);([\d.]+);([01])>", data)
    if match:
        temp1 = float(match.group(1))
        temp2 = float(match.group(2))
        counter = bool(int(match.group(3)))
        return temp1, temp2, counter
    else:
        return None

def clean_data(raw_data):
    try:
        start = raw_data.find("<")
        end = raw_data.find(">")
        if start != -1 and end != -1 and end > start:
            return raw_data[start:end+1]
        return None
    except Exception as e:
        print(f"Temizleme sırasında hata: {e}")
        return None

def read_from_arduino():
    global last_received_time
    counter_state = False
    try:
        ser = comport 
        ser.reset_input_buffer()
        last_read_bogaz = 0
        last_read_kazan = 0
        while True:
            raw_line = ser.readline().decode("utf-8", errors="ignore").strip()
            cleaned_line = clean_data(raw_line)

            if cleaned_line: 
                parsed_data = parse_data(cleaned_line)
                if parsed_data:
                    temp1, temp2, counter = parsed_data
                    last_received_time = time.time()  # Veri alındı, zamanı güncelle
			
                    if counter_state == False and counter == True:
                        update_counter()
                        counter_state = True

                    if counter == False:
                        counter_state = False
                        
                    # print(last_read_bogaz, temp1, last_read_kazan, temp2, counter)
                    try:
                        if(last_read_bogaz == 0 or int(last_read_bogaz) == int(temp1)):
                            cms.modbus_map["Boğaz Anlık"][2] = temp1
                            last_read_bogaz = temp1
                        else:
                            last_read_bogaz = temp1
                    except:
                        pass
                    
                    try:
                        if(last_read_kazan == 0 or int(last_read_kazan) == int(temp2)):
                            cms.modbus_map["Kazan Gerçek"][2] = temp2
                            last_read_kazan = temp2
                        else:
                            last_read_kazan = temp2
                    except:
                        pass
                    # print(f"Sıcaklık 1: {temp1}°C, Sıcaklık 2: {temp2}°C, Sayaç: {counter}")

            # Belirli bir süre boyunca veri alınmazsa Arduino'yu resetle
            if time.time() - last_received_time > 10:  # 10 saniye boyunca veri yoksa resetle
                reset_arduino()
                last_received_time = time.time()  # Reset sonrası zamanı sıfırla
            
            time.sleep(0.1)

            if kill_thread_var:
                return
    except serial.SerialException as e:
        print(f"Seri bağlantı hatası: {e}")
    except KeyboardInterrupt:
        print("Çıkış yapılıyor...")
    finally:
        if ser.is_open:
            ser.close()
            print("Seri bağlantı kapatıldı.")

# Thread başlat
th = Thread(target=read_from_arduino, args=())
th.setDaemon = True
th.start()

