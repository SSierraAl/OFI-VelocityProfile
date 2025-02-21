import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve

# Definir la parábola que va solo de -2 a 2 y es cero fuera de este rango
x = np.linspace(-10, 10, 800)
parabola = np.zeros_like(x)
parabola[(x >= -2) & (x <= 2)] = 1 - (x[(x >= -2) & (x <= 2)]**2 / 4)

# Definir la gaussiana
gaussian = np.exp(-x**2)

# Realizar la convolución correcta
conv_result = convolve(parabola, gaussian, mode='same')

# Normalizar las funciones de 0 a 1
parabola_normalized = parabola / np.max(parabola)
gaussian_normalized = gaussian / np.max(gaussian)
conv_result_normalized = conv_result / np.max(conv_result)

# Graficar los resultados normalizados
plt.figure(figsize=(10, 6))
plt.plot(x, parabola_normalized, label='Parábola Normalizada', color='blue')
plt.plot(x, gaussian_normalized, label='Gaussiana Normalizada', color='green')
plt.plot(x, conv_result_normalized, label='Convolución Normalizada', color='red')
plt.title('Convolución entre una Parábola y una Gaussiana (Normalizada)')
plt.xlabel('x')
plt.ylabel('Amplitud Normalizada')
plt.legend()
plt.grid(True)
plt.xlim(-10, 10)  # Mostrar todo el rango entre -10 y 10
plt.show()
