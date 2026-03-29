from pyModbusTCP.client import ModbusClient
import os
from dotenv import load_dotenv

load_dotenv()

# PLC IP addresses - configure via environment variables
# e.g. PLC_SUBNET=192.168.1 and PLC_NODES=236,237,238
plc_subnet = os.environ.get("PLC_SUBNET", "192.168.x")
plc_nodes = os.environ.get("PLC_NODES", "").split(",")

for i in plc_nodes:
    i = i.strip()
    if not i:
        continue
    client_handler = ModbusClient(host=f"{plc_subnet}.{i}", port=502, unit_id=1, auto_open=True)
    client_handler.open()

    result = client_handler.read_holding_registers(226)

    print(f"ip adresi:{plc_subnet}.{i}   yazıldığı adres: 226   yazma işlemi sonucu: {result}")
