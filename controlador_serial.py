# Graficador del driver para qPCR

#************************************************** IMPORTACIONES
from tkinter import *
from tkinter import ttk
from tkinter import messagebox  # Ventana de mensajes
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
import serial
import serial.tools.list_ports
import time
from datetime import datetime
from threading import Thread

#************************************************** DECLARACIONES GLOBALES
ports = []
ser = serial.Serial()
ser.baudrate = 115200
NCA = 1 #Numero de ciclos de acondicionamiento
NCT = 1 #Numero de ciclos de tratamiento
TA  = 30 #Temperatura de acondicionamiento
TT  = 35 #Temperatura de tratamiento
tC = 60 #Tiempo de ciclo en segundos
y   = [0] * 600 # lista de valores a graficar
plot1 = ""
canvas = ""
DataCSV = "Data Driver temperatura qPCR \nHora:,Temperatura:\n"

#************************************************** FUNCIONES PROPIAS
def saveCSV():
    global DataCSV
    fl = open("salida.csv", "w")
    fl.write(DataCSV)
    fl.close()

def plotNewData(ND):
    global canvas
    global plot1
    global DataCSV
    #Conevrtir a float
    Di = float (ND)
    #Insertar el dato nuevo en los datos a gusrdar CSV
    now = datetime.now()
    DataCSV = DataCSV + now.strftime("%H:%M:%S") + "," + str(Di) + "\n"
    #Insertar el dato nuevo a graficar
    for i in range(599):
        y[i] = y[i+1]
        y[599] = Di
    plot1.cla()
    #canvas.figure.clear()
    #fig = Figure(figsize = (7.2, 5.5),dpi = 100)
    #plot1 = fig.add_subplot(111)
    plot1.plot(y)
    #canvas = FigureCanvasTkAgg(fig,master = window)  
    canvas.draw()

def sendDataCOMM(Data):
    global ser
    Salida = Data.encode('utf-8')
    ser.write(Salida)
    #print(Salida)

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

def getData():
global DataCSV
global ser
global NCA
global NCT
global TA
global TT
global tC
global y
# Ciclos de acondicionamiento
# gets a los valores de los entry
NCA = int(ent01.get())
NCT = int(ent02.get())
TA  = int(ent03.get())
TT  = int(ent04.get())
tC = int(ent05.get())
#Acondicionamiento
Sal1 = str(TA).encode('utf-8')
sendDataCOMM("S")

INdata = readDataCOMM()
#print(INdata)
sendDataCOMM(str(TA))
INdata = readDataCOMM()
#print(INdata)
sendDataCOMM("R")
INdata = readDataCOMM()
#print(INdata)
for j in range(int(NCA)):
sendDataCOMM("A")
time.sleep(0.2)
#print("Ciclo no: " + str(j))
for x in range(int(tC)):
sendDataCOMM("M")
INdata = readDataCOMM()
plotNewData(INdata)
#print(x)
#print(INdata)
time.sleep(0.98)
sendDataCOMM("0")
time.sleep(0.2)
for x in range(int(tC)):
sendDataCOMM("M")
INdata = readDataCOMM()
plotNewData(INdata)
#print(x)
#print(INdata)
time.sleep(0.98)

#Tratamiento
Sal1 = str(TT).encode('utf-8')
sendDataCOMM("S")
INdata = readDataCOMM()
#print(INdata)
sendDataCOMM(str(TT))
INdata = readDataCOMM()
#print(INdata)
sendDataCOMM("R")
INdata = readDataCOMM()
#print(INdata)
for j in range(int(NCT)):
sendDataCOMM("A")
time.sleep(0.2)
#print("Ciclo no: " + str(j))
for x in range(int(tC)):
sendDataCOMM("M")
INdata = readDataCOMM()
plotNewData(INdata)
#print(x)
#print(INdata)
time.sleep(0.98)
sendDataCOMM("0")
time.sleep(0.2)
for x in range(int(tC)):
sendDataCOMM("M")
INdata = readDataCOMM()
plotNewData(INdata)
#print(x)
#print(INdata)
time.sleep(0.99)
sendDataCOMM("X")
INdata = readDataCOMM()
ser.close()
save_button.config(state=NORMAL)
#print(DataCSV)


def conexionInicial():
global ser
# Tomar valores de los entry
NC = 1
NCA = int(ent01.get())
NCT = int(ent02.get())
TA  = int(ent03.get())
TT  = int(ent04.get())
tC = int(ent05.get())
# Conectar al driver
portSel = cmb01.get()

if portSel == "":
messagebox.showinfo(message="Selecciona un puerto por favor", title="Error:")
else:
#print(portSel)
ser.port = portSel
ser.open()
lbl13.config(text='Conectando...')
while NC < 30:
NB = ser.in_waiting
#print(NB)
if NB > 0:
time.sleep(0.1)
ENT = ser.read(NB)
time.sleep(0.1)
NC = 31
NC = NC + 1
time.sleep(0.5)
if ser.is_open:
sendDataCOMM("I")
Sal = readDataCOMM()
lbl13.config(text=Sal)
time.sleep(0.1)
startGet = Thread(target=getData)
startGet.start()
else:
messagebox.showinfo(message="No se pudo acceder al puerto", title="Error:")
lbl13.config(text='Error de conección')

# Iniciar proceso termico

def plot():
global y
global plot1
global canvas
# the figure that will contain the plot
fig = Figure(figsize = (7.2, 5.5),dpi = 100)
# list of squares
# y = [i**2 for i in range(101)]
# adding the subplot
plot1 = fig.add_subplot(111)
# plotting the graph
plot1.plot(y)
# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,master = window)  
canvas.draw()
# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack()
# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas,window)
toolbar.update()
# placing the toolbar on the Tkinter window
canvas.get_tk_widget().place(x=260, y=20)

def startTT():
startCon = Thread(target=conexionInicial)
startCon.start()

#************************************************** MAIN
for port in serial.tools.list_ports.comports():
    ports.append(port.name)

if len(ports)>0:
    lisPortsInPC = ports
else:
    lisPortsInPC = ['Sin puertos']

window = Tk()
Opc1 = IntVar()
window.geometry("1000x600+30+20")
window.resizable(False, False)
window.title('Grafidaor driver temperatura qPCR')

lbl01 = Label(window, text="Configuración")
lbl02 = Label(window, text="# Ciclos:")
ent01 = Entry(window, width=10, justify="right")
ent01.insert(0, NCA)
lbl03 = Label(window, text="Acondicionamiento")
lbl04 = Label(window, text="# Ciclos:")
ent02 = Entry(window, width=10, justify="right")
ent02.insert(0, NCT)
lbl05 = Label(window, text="Tratamiento")
lbl06 = Label(window, text="SP [°C]:")
ent03 = Entry(window, width=10, justify="right")
ent03.insert(0, TA)
lbl07 = Label(window, text="Acondicionamiento")
lbl08 = Label(window, text="SP [°C]:")
ent04 = Entry(window, width=10, justify="right")
ent04.insert(0, TT)
lbl09 = Label(window, text="Tratamiento")
lbl10 = Label(window, text="Tiempo")
ent05 = Entry(window, width=10, justify="right")
ent05.insert(0, tC)
lbl11 = Label(window, text="s/ciclo")
lbl12 = Label(window, text="Puerto:")
cmb01 = ttk.Combobox(window,
values=lisPortsInPC,
width=16,)

plot_button = Button(master = window,
command = startTT,
height = 1,
width = 33,
text = "Inicio")

lbl13 = Label(window, text="Desconectado")

save_button = Button(master = window,
command = saveCSV,
height = 1,
width = 33,
text = "Guardar CSV",
state = DISABLED)

lbl01.place(x=60,  y=20)
lbl02.place(x=10,  y=60)
ent01.place(x=65,  y=60)
lbl03.place(x=140, y=60)
lbl04.place(x=10,  y=100)
ent02.place(x=65,  y=100)
lbl05.place(x=140, y=100)
lbl06.place(x=15,  y=140)
ent03.place(x=65,  y=140)
lbl07.place(x=140, y=140)
lbl08.place(x=15,  y=180)
ent04.place(x=65,  y=180)
lbl09.place(x=140, y=180)
lbl10.place(x=15,  y=220)
ent05.place(x=65,  y=220)
lbl11.place(x=140, y=220)
lbl12.place(x=15,  y=260)
cmb01.place(x=65,  y=260)
plot_button.place(x=10, y=300)
save_button.place(x=10, y=400)
lbl13.place(x=10,  y=340)
plt.ion()
plot()

window.mainloop()
#************************************************** FIN DEL SCRIPT
#cmd /k cd "$(CURRENT_DIRECTORY)" && python "$(FILE_NAME)"
