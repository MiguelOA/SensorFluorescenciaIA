import time
import board
import busio
from mcp9600 import MCP9600

mcp9600 = MCP9600(i2c_addr=0x66)
mcp9600.set_thermocouple_type('J')

while True:
	print(mcp9600.get_hot_junction_temperature())
	time.sleep(1)

