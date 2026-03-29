import database_models as dbm


menu_symbol_space_width = 188
menu_icon_size = 128
menu_icon_number = 3
line_size = 3
common_background = "white"
button_background = "orange"
warning_color = "#f0ad4e"
warning_color_2 = "coral"

positive_color = "chartreuse4"
positive_color_2 = "chartreuse3"


main_menu_top_number = 2
history_top_number = 3

modbus_map = {"Hidrolik Basınç":[0,30,0],
              "Hidrolik Yağ Sıcaklık":[0,22,0],
              "Pot yukarı çıkma zamanı":[0,200,0],
              "pot yukarıda bekleme":[0,202,0],"Pot aşağı inme zamanı":[0,204,0],
              "Koç Aşağı Basınç":[0,206,0],"Mum ileri bekleme":[0,208,0],
              "Mum Geri Çekme Zamanı":[0,210,0],"Kalıp Soğuma Bekleme":[0,212,0],
              "Boğaz Hedef":[0,214,0],
              "Kazan Gerçek":[0,20,0],
              "Boğaz Anlık":[0,21,0],
              "Kazan Hedef":[0,218,0],
              "Pot çalışma":[0,224,0],
              "otomatik uretim adeti":[0,220,-1], "otomatik uretim hedef":[0,222,0],


              "Hid termik alarm":(1,400),"Acil alarm":(1,401),
              "Bariyer alarm":(1,402),"Hidrolik kirli alarm":(1,403),
              "Hidrolik seviye alarm":(1,404),"Kazan TC hata":(1,405),
              "Bogaz TC hata":(1,406),"Hidrolik TC hata":(1,407),
              "Hedef uretim tamamlandi":(1,408),"Acil durus but":(1,409),

              "erp durdurma bit":(1,409),"Isılar açık kapalı":(1,501)}




work_order = {
}

worker_name = ""
cast = ""

work_order_static_vars = {}

fire_miktarı = 0
