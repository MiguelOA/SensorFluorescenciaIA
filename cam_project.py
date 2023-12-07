#*************************************************************************
#*              Camera project for Raspberry py                          *
#*                    Desarrollado por: Luis Barrera                     *
#* VERSION:     0.1 alpha                                                *
#* REPOSITORIO: <url de github>                                          *
#*************************************************************************

#*************************************************************** LIBRERIAS
print ("Cargando librerias...")
from picamera import PiCamera, Color
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
import threading
from io import BytesIO
from PIL import Image, ImageGrab, ImageTk
from multiprocessing import  Process
from pathlib import Path
from datetime import datetime
from datetime import date
import numpy as np
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
import tflite_runtime.interpreter as tfl
import serial
print ("Librerias cargadas: OK")


#************************************************** DECLARACIONES GLOBALES
camera = PiCamera()
video_width = 600
video_height = 360
fps = 2
label_video = None
window = None
image = None
imageRes = None
imagePath = ''
image_tk1 = None
image_tk2 = None
print("Cargando modelo...")
interpreter = tfl.Interpreter(model_path='modelo_lite.tflite')
interpreter.allocate_tensors()
print("Modelo cargado : OK")
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
name = ''
idPac = ''
playTemp = False
medicion = ''
ser = serial.Serial(port='/dev/ttyS0',
	baudrate=115200)

#*************************************************************** FUNCIONES
#Funcion obsoleta
def fnStream():
	global image
	global image_tk1
	stream = BytesIO()
	camera.capture(stream, format='jpeg')
	image = Image.open(stream)
	image_tk1 = ImageTk.PhotoImage(image)
	label_video.configure(image=image_tk1)
		#sleep(1.0 / fps)
#---------------

def fn_registro_temperatura(TAco, TTra, TCic, NCic):
	global playTemp
	i = 0
	valle = False
	parte2 = True
	sendDataCOMM('S')
	print(readDataCOMM())
	sendDataCOMM(str(TAco))
	print(readDataCOMM())
	sendDataCOMM('R')
	print(readDataCOMM())
	dif = 0
	while playTemp:
		if dif <= 0:
			if valle:
				sendDataCOMM('0')
			else:
				if(i > 0):
					fnCapture()
				i = i + 1
				if(i > NCic):
					if parte2:
						parte2 = False
						i = 1
						sendDataCOMM('S')
						print(readDataCOMM())
						sendDataCOMM(str(TTra))
						print(readDataCOMM())
						sendDataCOMM('R')
						print(readDataCOMM())
					else:
						lblCAct.config(text='Ciclo Actual: NA')
						lblTMed.config(text='Temperatura: NA')
						playTemp = False
						sendDataCOMM('X')
						return True
				s2 = 'Ciclo Actual: ' + str(i)
				lblCAct.config(text=s2)
				sendDataCOMM('A')
			valle = not(valle)
			zero = time.time()
		sendDataCOMM('M')
		
		s = 'Temperatura: ' + readDataCOMM()
		lblTMed.config(text=s)
		dif = TCic + zero - time.time()
	sendDataCOMM('X')
	return False
		
		  



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



def fnPlay():
	global playTemp
	playTemp = True
	try:
		TAco = float(entTAco.get())
		TTra = float(entTTra.get())
		TCic = float(entTCic.get())
		NCic = int(entNCic.get())
		formulario()
		cheDirMed.select()
		cheSaveData.select()
		cheSaveImgs.select()
		x = threading.Thread(target=fn_registro_temperatura, args=(TAco, TTra, TCic, NCic), daemon=True)
		x.start()
	except:
		print('Entradas invalidas')
	
	

def fnPause():
	global playTemp
	playTemp = False


def imgExist(img_path):
	try:
		i = Image.open(img_path)
		return False
	except:
		return True
	return True

def showImg():
	global image
	global image_tk2
	img = image.convert('RGBA')
	image_tk2 = ImageTk.PhotoImage(img)
	lblImgRes.config(image=image_tk2)
	lblImgRes.update()


def fnCapture():
	global image
	global imagePath
	global playTemp
	stream = BytesIO()
	camera.capture(stream, format='jpeg', quality=90)
	image = Image.open(stream)
	ftypes = (
		('image', '*.jpg'),
		('All files', '*.*')
	)

	
	now = datetime.now()
	currentTime = now.strftime('%H_%M_%S')
	today = str(date.today())
	directory = str(Path.home()) + '/'
	imagePath = directory + today + '__' + currentTime + '.jpg'
	#predeName = 'set1-img000-0.00_0.00_0.00_0.00_0.00.jpg'
	#imagePath = fd.asksaveasfilename(defaultextension='.txt', initialfile=predeName, initialdir=directory)
	try:	
		image.save(imagePath)
		showImg()
		if opcDirMed.get():
			if not(playTemp):
				formulario()
			fnMedir()
	except:
		print('No se ha guardado archivo')
	
	


def fnOpen():
	global image
	global imagePath
	ftypes = (
		('image', '*.jpg'),
		('All files', '*.*')
	)
	directory = str(Path.home())
	imagePath = fd.askopenfilename(
		initialdir=directory,
        title='Open image:',
        filetypes=ftypes)
    
	print(imagePath)
	
	if imagePath:
		image = Image.open(imagePath)
		showImg()
	

def fnMedir():
	global imagePath
	global idPac
	global name
	#imageName = imagePath.split('.')
	#imageName = imageName[0]
	SAVEimage = False
	SAVEdata = False
	if opcSaveImgs.get():
		SAVEimage = True
	if opcSaveData.get():
		SAVEdata = True
	RGBData = ImageToData(imagePath, SAVEimage, SAVEdata)
	RGBData = np.array(RGBData, dtype=np.float32)
	min_val = np.min(RGBData)
	max_val = np.max(RGBData)
	resultados = predecir(RGBData)
	guardarPDF(idPac, name, resultados[0], resultados[1], resultados[2], resultados[3], resultados[4])
	print(imagePath)

#***************************************************
#* Function: ImageToData
#* Description: Convert image file in to a 
#*              unidimensional normalized np array.
#* @Param : image file name, boolean to save crop
#*          images and boolan to save numerical
#*          data in to .csv file
#* @Return: normalaized np array from RGB image data
#***************************************************
def ImageToData(imageName, saveImages, saveDataFile):
	IM = Image.open(imageName)
	nameFileENT = imageName
	nameFileENT = nameFileENT[0:len(nameFileENT)-4]
	IMsmall = IM.resize((60,36))
	# Crop images
	imCrop1 = IMsmall.crop((0,0,12,12))
	imCrop2 = IMsmall.crop((12,12,24,24))
	imCrop3 = IMsmall.crop((24,12,36,24))
	imCrop4 = IMsmall.crop((36,12,48,24))
	imCrop5 = IMsmall.crop((48,12,60,24))
	# Save iamges
	if saveImages:
		imCrop1.save(nameFileENT+'_cl0.jpg')
		imCrop2.save(nameFileENT+'_pt1.jpg')
		imCrop3.save(nameFileENT+'_pt2.jpg')
		imCrop4.save(nameFileENT+'_pt3.jpg')
		imCrop5.save(nameFileENT+'_cnt.jpg')
	#Convert to a number  
	imData1 = np.asarray(imCrop1)
	imData2 = np.asarray(imCrop2)
	imData3 = np.asarray(imCrop3)
	imData4 = np.asarray(imCrop4)
	imData5 = np.asarray(imCrop5)
	DataFull = [None]
	DataFull = np.append(DataFull,imData1[0])
	DataFull = DataFull[1:]
	for i in range(1, 12):
		DataFull = np.append(DataFull,imData1[i])
	for i in range(0, 12):
		DataFull = np.append(DataFull,imData2[i])
	for i in range(0, 12):
		DataFull = np.append(DataFull,imData3[i])
	for i in range(0, 12):
		DataFull = np.append(DataFull,imData4[i])
	for i in range(0, 12):
		DataFull = np.append(DataFull,imData5[i])
	# Normalizing data
	DataFull = DataFull / 255.0
	#Sava numeric data in a file
	if saveDataFile:
		dataFileName = nameFileENT + '_data.csv'
		f = open(dataFileName, "w")
		for i in range(0, 2160):
			f.write(str(DataFull[i]))
			f.write("\n")
		f.close()
	return DataFull

def predecir(data):
	global input_details
	global output_details
	interpreter.set_tensor(input_details[0]['index'], [data])
	interpreter.invoke()
	prediction = interpreter.get_tensor(output_details[0]['index'])
	results = []
	for item in prediction[0]:
		item = float(item)
		if item < 0.0:
			item = 0.0
		if item > 1.0:
			item = 1.0
		results.append(item)
	return results



def guardarPDF(idPac ,nombre, cl0, pt1, pt2, pt3, cnt):
	w, h = letter
	#nombre, cl0, pt1, pt2, pt3, cnt
	now = datetime.now()
	currentTime = now.strftime('%H_%M_%S')
	today = str(date.today())
	directory = str(Path.home()) + '/'
	pdfPath = directory + today + '__' + currentTime + '.pdf'
	c = canvas.Canvas(pdfPath, pagesize=letter)
	s = 'ID:' + idPac
	c.drawString(50, h-50, s)
	s = 'Paciente:' + nombre
	c.drawString(50, h-100, s)
	s = 'CL0:' + str(cl0)
	c.drawString(50, h-150, s)
	s = 'PT1:' + str(pt1)
	c.drawString(50, h-200, s)
	s = 'PT2:' + str(pt2)
	c.drawString(50, h-250, s)
	s = 'PT3:' + str(pt3)
	c.drawString(50, h-300, s)
	s = 'CNT:' + str(cnt)
	c.drawString(50, h-350, s)
	c.save()


def fnSubmit():
	global window_form
	global entName
	global entId
	global name
	global idPac
	name = entName.get()
	idPac = entId.get()
	window_form.destroy()
	window_form = None
	

def formulario():
	global window_form
	global entName
	global entId
	global name
	global idPac
	window_form = Toplevel()
	window_form.resizable(False, False)
	window_form.geometry('400x600+10+10')
	window_form.title('Formulario paciente')
	# Create widgets
	entId = Entry(window_form, width=20)
	entId.delete(0, END)
	entId.insert(0, idPac)
	lblId = Label(window_form, text='N de identidad')
	entName = Entry(window_form, width=20)
	entName.delete(0, END)
	entName.insert(0, name)
	lblName = Label(window_form, text='Nombre del paciente')
	btnSub = Button(window_form, text='Submit', command=fnSubmit)
	# Place widgets
	entId.place(x=200, y = 20)
	lblId.place(x=20, y = 20)
	entName.place(x=200, y = 60)
	lblName.place(x=20, y = 60)
	btnSub.place(x=200, y = 100)
	#Bloquear ventana
	window_form.wait_window()
	
	

#******************************************************************** MAIN
#Control de resolucion (ancho alto)
#Tamaño maximo (2592, 1944) 4:3


#camera.annotate_text_size = 46
#camera.annotate_background = Color('black')
#camera.annotate_foreground = Color('white')

#camera.rotation = 180
#camera.start_recording('video1.h264')
#camera.stop_recording()
#camera.annotate_text = "_mini pro_"




camera.preview_fullscreen = False
camera.preview_window = (505, 161, 600, 360)

camera.awb_mode = 'off'
#camera.exposure_mode = 'off'
camera.image_effect = 'none'
camera.resolution = (600,360)

camera.sensor_mode = 2

camera.awb_mode = 'off'
camera.awb_gains = (1.4, 1.4)
camera.image_effect = 'none'
camera.resolution = (600,360)


#****************************************************************** WINDOW
window = Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f'{screen_width}x{screen_height}')
window.resizable(False, False)
window.title('Proyecto')

window_form = None
entName = None
entId = None
#window.attributes('-fullscreen', True)

opcDirMed = IntVar()
opcSaveImgs = IntVar()
opcSaveData = IntVar()

#***************************************************************** WIDGETS
#********************************************************* WIDGET CREATION
frameTemp = Frame(window, background='blue')
frameMed = Frame(window, background='red')
frameRes = Frame(window, background='green')
sep1 = ttk.Separator(window, orient='vertical')
sep2 = ttk.Separator(window, orient='vertical')
lblTemp = Label(frameTemp, text='Temperatura')
lblMed = Label(frameMed, text='Medicion')
lblRes = Label(frameRes, text='Resultados')
frameTAco = Frame(frameTemp, background='blue')
lblTAco = Label(frameTAco, text='Temperatura Acondicionamiento')
entTAco = Entry(frameTAco, width=10)
entTAco.insert(0, '65.0')
frameTTra = Frame(frameTemp, background='blue')
lblTTra = Label(frameTTra, text='Temperatura Tratamiento') #Mayor que
entTTra = Entry(frameTTra, width=10)
entTTra.insert(0, '95.0')
frameTCic = Frame(frameTemp, background='blue')
lblTCic = Label(frameTCic, text='Tiempo del Ciclo')
entTCic = Entry(frameTCic, width=10)
entTCic.insert(0, '5')
frameEST = Frame(frameTemp, background='blue')
lblTMed = Label(frameEST, text='Temperatura: NA')
lblCAct = Label(frameEST, text='Ciclo actual: NA')
frameNCic = Frame(frameTemp, background='blue')
lblNCic = Label(frameNCic, text='Num Ciclos')
entNCic = Entry(frameNCic, width=10)
entNCic.insert(0, '2')
framePlayPause = Frame(frameTemp, background='#FF00FF')
btnPlay = Button(framePlayPause, text='Play', command=fnPlay)
btnPause = Button(framePlayPause, text='Pause', command=fnPause)
label_video = Label(frameMed, background='red')
btnCap = Button(frameMed, text='Capture', command=fnCapture)
cheDirMed = Checkbutton(frameMed, text='Pasar medir', variable=opcDirMed)
btnOpen = Button(frameRes, text='Open', command=fnOpen)
lblImgRes = Label(frameRes, background='green')
btnMedir = Button(frameRes, text='Medir', command=fnMedir)
cheSaveImgs = Checkbutton(frameRes, text='Save images', variable=opcSaveImgs)
cheSaveData = Checkbutton(frameRes, text='Save data', variable=opcSaveData)

#********************************************************* WIDGET POSITION
frameTemp.pack(fill='both', expand=1, side='left')
sep1.pack(fill='y', side='left')
frameMed.pack(fill='both', expand = 1, side='left')
sep2.pack(fill='y', side='left')
frameRes.pack(fill='both', expand=1, side='left')
lblTemp.pack(side='top')
lblMed.pack(side='top')
lblRes.pack(side='top', padx=(270,270) )
frameTAco.pack(fill='both', expand=1, side='top')
lblTAco.pack(expand=1, side='left')
entTAco.pack(expand=1, side='left')
frameTTra.pack(fill='both', expand=1, side='top')
lblTTra.pack(expand=1, side='left')
entTTra.pack(expand=1, side='left')
frameTCic.pack(fill='both', expand=1, side='top')
lblTCic.pack(expand=1, side='left')
entTCic.pack(expand=1, side='left')
frameEST.pack(fill='both', expand=1, side='top')
lblTMed.pack(expand=1, side='left')
lblCAct.pack(expand=1, side='left')
frameNCic.pack(fill='both', expand=1, side='top')
lblNCic.pack(expand=1, side='left')
entNCic.pack(expand=1, side='left')
framePlayPause.pack(fill='both', expand=1, side='top')
btnPlay.pack(expand=1, side='left')
btnPause.pack(expand=1, side='left')
label_video.pack(expand=1, side='top')
btnCap.pack(expand=1, side='top')
cheDirMed.pack(expand=1, side='top')
btnOpen.pack(expand=1, side='top')
lblImgRes.pack(side='top')
btnMedir.pack(expand=1, side='top')
cheSaveImgs.pack(side='top')
cheSaveData.pack(expand=1, side='top')

#************************************************************* END WIDGETS
fnStream()
camera.start_preview()

window.mainloop()
playTemp = False
camera.stop_preview()


#*********************************************************** FIN DE SCRIPT
