import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
try:
	while True:
		GPIO.output(17, GPIO.HIGH)
		print('Led encendido')
		time.sleep(2)

		GPIO.output(17, GPIO.LOW)
		print('Led apagado')
		time.sleep(2)
except KeyboardInterrupt:
	pass
print('Programa finalizado')
