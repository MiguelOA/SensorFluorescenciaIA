import tflite_runtime.interpreter as tfl
import numpy as np
import pandas as pd

path = 'dataset.csv'
df = pd.read_csv(path, header=None)
#df = df.sample(frac=1, random_state=42)
x, y = df.values[:, : -5], df.values[:, -5 :]
#Todo debe ser float
x = x.astype('float32')
y = y.astype('float32')



print("Cargando modelo...")
interpreter = tfl.Interpreter(model_path='modelo_lite.tflite')
interpreter.allocate_tensors()
print("Modelo cargado : OK")

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Realizando prediccion...")
n = len(y)
y_predict_temp = []
for i in range(n):
    interpreter.set_tensor(input_details[0]['index'], [x[i]])
    interpreter.invoke()
    y_predict_temp.append(interpreter.get_tensor(output_details[0]['index']))
    print(i)

#Eilimina dimension inutil
y_predict = [item for sublist in y_predict_temp for item in sublist]
print('Fin de la prediccion')
totalMax = 0
iMax = 0
promErr = []
for i in range(n):
    max = 0
    err = 0
    for j in range(5):
        res = abs(y_predict[i][j] - y[i][j])
        err = err + res
        if res >= max:
            max = res
    if max >= totalMax:
        totalMax = max
        iMax = i
    err = err / 5
    promErr.append(max)
    print('Error de ', y[i], ' es: ', max)
print('El maximo error es ', totalMax)
print(iMax,y_predict[iMax], y[iMax])
num_bins = 20
bin_ranges = np.linspace(0, totalMax, num_bins + 1)







