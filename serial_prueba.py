import time
import serial
import threading

ser = serial.Serial(port='/dev/ttyS0',
	baudrate=115200)

def escribir_datos():
	while True:
		mensaje = input()
		sendDataCOMM(mensaje)
		respuesta = readDataCOMM()
		print('Respuesta: ', respuesta)
		


		

def sendDataCOMM(Data):
    global ser
    Salida = Data.encode('utf-8')
    ser.write(Salida)
    print(Salida)

def readDataCOMM():
	global ser
	c = 0
	while c < 40:
		NB = ser.in_waiting
		if NB == 0:
			c = c + 1
		else:
			c = 41
		time.sleep(0.2)
	if c == 41:
		time.sleep(0.2)
		NB = ser.in_waiting
		Salida = ser.read(NB)
		return Salida.decode('utf-8')
	else:
		return "ERR: no read"



hilo_escritura = threading.Thread(target=escribir_datos, daemon = True)


hilo_escritura.start()

hilo_escritura.join()

