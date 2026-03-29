import requests
import subprocess
import datetime
from threading import Thread
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

gateway_url = os.environ.get("GATEWAY_URL", "http://localhost")
gateway_api_port = os.environ.get("GATEWAY_API_PORT", "5001")
kill_time_updater = False


def checkKill(timer):
    while timer > 0:
        timer -= 1
        time.sleep(1)
        if(kill_time_updater):
            print("time updater killed")
            return
    return

def update_time_continously(url):
    while not kill_time_updater:
        try:
            get_timestamp(url)
            checkKill(1800)
        except:
            checkKill(30)
            pass


def get_timestamp(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Hata kontrolü
        timestamp = int(float(response.text))  # Metni integer'a çevir
        print("timestamp:",timestamp)
        update_system_time(timestamp)
    except requests.RequestException as e:
        raise Exception(f"Request Hata: {e}")
    except ValueError as ve:
        raise Exception(f"Timestamp dönüşüm hatası: {ve}")
    except Exception as ex:
        raise Exception(f"Genel bir hata oluştu: {ex}")

def update_system_time(timestamp):
    if(sys.platform == "win32"):
        return
    try:
        # Timestamp'i datetime objesine çevir
        new_time = datetime.datetime.fromtimestamp(timestamp)
        # Sistemin saatini güncellemek için 'date' komutunu formatla
        date_str = new_time.strftime('%Y-%m-%d %H:%M:%S')
        subprocess.run(['sudo', 'date', '-s', date_str], check=True)
        print(f"Sistem saati güncellendi: {date_str}")
    except Exception as e:
        print(f"Saat güncellenirken hata oluştu: {e}")

def updateTime():
    url = f"{gateway_url}:{gateway_api_port}/getTimestamp"
    th = Thread(target=update_time_continously, args=(url,))
    th.start()

if __name__ == "__main__":
    updateTime()
