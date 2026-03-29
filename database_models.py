from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Text,Boolean, String
from sqlalchemy.ext.declarative import declarative_base
import datetime, time
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
# SQLite veritabanına bağlantı oluştur

Base = declarative_base()
engine = create_engine('sqlite:///mirdb.db', echo=False)

# Tablo sınıfını tanımla
class TemperatureReading(Base):
    __tablename__ = 'temperature_readings'
    id = Column(Integer, primary_key=True)
    kazan = Column(Float)
    bogaz = Column(Float)
    hidrolik = Column(Float)
    timestamp = Column(DateTime)

class PressRecords(Base):
    __tablename__ = 'production_records'
    id = Column(Integer, primary_key=True)
    production_id = Column(Integer)
    fire = Column(Boolean)
    timestamp = Column(DateTime)

class Stops(Base):
    __tablename__ = 'Stops'
    id = Column(Integer, primary_key=True)
    durus_nedeni=Column(String)
    durus_alt_nedeni = Column(String,nullable=True)
    durus_kodu = Column(String)
    Personel=Column(String)
    durus_baslangic = Column(DateTime)
    durus_bitis = Column(DateTime)
    durus_tipi = Column(String)
    planliDurus = Column(Boolean)
    is_emri_idsi = Column(String)

class Counter(Base):
    __tablename__ = 'Counter'
    id = Column(Integer, primary_key=True)
    counter=Column(String) 


Base.metadata.create_all(engine)


# # Veritabanı üzerinde işlem yapmak için bir Session oluştur
__session_factory = sessionmaker(bind=engine)
__Session = scoped_session(__session_factory)
def get_session(): return __Session()
