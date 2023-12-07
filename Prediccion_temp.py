import time
import board
import busio
from mcp9600 import MCP9600

mcp9600 = MCP9600(i2c_addr=0x66)
mcp9600.set_thermocouple_type('J')

temperaturas = []
c = 0
while True:
	temperaturas.append(mcp9600.get_hot_junction_temperature())
	print('Temperatura: ', temperaturas[c])
	if c >= 5:
		m = (temperaturas[c] - temperaturas [c - 5]) / 5
		print('Pendiente: ', m)
	c += 1
	time.sleep(1)
