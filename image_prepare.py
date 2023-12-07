#**************************************************
#*      Imege conditioner for qPCR analizer
#*     Developer: Miguel Orozco (Necrovalle)
#* Version: 0.3 alpha
#* URL: <internal documet>
#**************************************************

#************************************************** LIBRERIES
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
from PIL import Image
import numpy as np
import os

#**************************************** GLOBAL DECLARATIONS

#******************************************** LOCAfdL FUNCTIONS
#***************************************************
#* Function: fcnSelectIamge
#* Description: Open dialoge faile to select an  
#*              image and open it to process.
#* @Param : No Parameters
#* @Return: path and file image name 
#***************************************************
def fcnSelectIamge():
	if saveImagesOpc.get() == 1:
		SAVEimage = True
	else:
		SAVEimage = False
	if saveDataOpc.get() == 1:
		SAVEdata = True
	else:
		SAVEdata = False
	ftypes = (
		('image', '*.jpg'),
		('All files', '*.*')
	)
	filename = fd.askopenfilename(
        title='Open image:',
        filetypes=ftypes)
	totChar = len(filename)
	cutChar = filename.rfind("/")
	fName= filename[0:(cutChar+1)]
	fDir = filename[(cutChar+1):totChar]
	#print(filename)
	RGBData = ImageToData(filename, SAVEimage, SAVEdata)
	

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
	imData5 = np.asarray(imCrop4)
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

#******************************************************* MAIN
window = Tk()
saveImagesOpc = IntVar()
saveDataOpc = IntVar()
window.geometry("250x120+100+60")
window.resizable(False, False)
window.title('Convert image to numerical Data GenomeSacan...')
SelectImageBTN = Button(window, text='Select image...', command=fcnSelectIamge)
SelectImageBTN.place(x=10, y=10)
saveImageCHK = Checkbutton(window, text="Save crop images", variable=saveImagesOpc)
saveImageCHK.place(x=10, y=40)
saveDataCHK = Checkbutton(window, text="Save numerical data", variable=saveDataOpc)
saveDataCHK.place(x=10, y=60)
window.mainloop()
#************************************************* SCRIPT END
