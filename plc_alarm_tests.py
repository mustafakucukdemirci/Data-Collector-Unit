from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer
import time
import os
from dotenv import load_dotenv

load_dotenv()

modbuslist : ModbusClient = []
# server = ModbusServer(host="0.0.0.0")
# server.start()

# PLC IP addresses - configure via environment variables
# e.g. PLC_SUBNET=192.168.1 and PLC_TEST_NODES=235
plc_subnet = os.environ.get("PLC_SUBNET", "192.168.x")
plc_test_nodes = os.environ.get("PLC_TEST_NODES", "").split(",")

for i in plc_test_nodes:
    i = i.strip()
    if not i:
        continue
    client_handler = ModbusClient(host=f"{plc_subnet}.{i}", port=502, unit_id=1, auto_open=True)
    client_handler.open()
    print(f"connection of {i} provided")
    modbuslist.append(client_handler)

counter = 2
start = 1
for i in modbuslist:
    print(i.host, end="  ")
    value = i.read_holding_registers(220)
    print(value)

    if(value is not None):

        i.write_single_register(220, value[0] + 1)

    value = i.read_holding_registers(220)
    print(value, end="--")
    print()
start += 1


client_handler.close()
