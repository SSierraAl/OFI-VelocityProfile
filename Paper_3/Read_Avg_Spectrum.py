import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from scipy.signal import butter, filtfilt,spectrogram, hilbert
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.signal import butter, filtfilt

def butter_bandpass_filter(data, lowcut, highcut, order, fs):
    """
    Apply a Butterworth bandpass filter to the input data.
    """
    nyquist = 0.5 * fs  # Nyquist frequency (half of the sampling frequency)
    
    # Normalize the cutoff frequencies by the Nyquist frequency
    lowcut = lowcut / nyquist
    highcut = highcut / nyquist
    
    # Design a Butterworth bandpass filter
    b, a = butter(order, [lowcut, highcut], btype='band', analog=False)
    
    # Apply the filter to the data using filtfilt (zero-phase filtering)
    y = filtfilt(b, a, data)
    
    return y

# Scaling function based on the given equation
def scale_value(value):
    return (value * 0.001550) / (2 * math.cos(math.radians(72)))




# Ruta de los archivos CSV
csv_files = glob.glob("./*.csv")
print(csv_files)

# Crear figura y subgráficos
fig, axes = plt.subplots(3, 1, figsize=(12, 12))

i = 0
scatter_data = []  # Para almacenar datos de dispersión

for file in csv_files:
    # Cargar el CSV, omitir la primera fila y eliminar la primera columna
    df = pd.read_csv(file, skiprows=1).iloc[:, 500:950]

    # **Subplot 1: Filtrado de una sola columna (solo para el primer archivo)**
    if i == 0:
        column_to_plot = df.iloc[:1501, 5]  # Primera columna
        filtered_column = butter_bandpass_filter(column_to_plot, 100, 100000, 3, 500000)
        axes[0].plot(filtered_column, linestyle='-', label=f"Filtered Column - {file.split('/')[-1]}")
        axes[0].set_title("Filtered Column from First CSV File")
        axes[0].set_xlabel("Index")
        axes[0].set_ylabel("Filtered Value")
        axes[0].grid(True)
        axes[0].legend()

    # **Subplot 2: Promedio de cada columna**
    average_values_limited = df.mean()
    smoothed_vector = butter_bandpass_filter(average_values_limited, 1000, 100000, 3, 500000)
    
    # Aplicar media móvil para suavizar los valores
    smoothed_vector = np.convolve(average_values_limited, np.ones(40)/40, mode='valid')
    smoothed_vector = np.array([scale_value(v) for v in smoothed_vector])

    axes[1].plot(range(len(smoothed_vector)), smoothed_vector, marker='o', linestyle='-', label=file.split('/')[-1])

    # **Preparar datos para el scatter plot**
    scatter_data.append(smoothed_vector)

    i += 1

# Configuración del segundo subplot
axes[1].set_title("Promedio de cada columna en múltiples archivos CSV")
axes[1].set_xlabel("Índice de columna")
axes[1].set_ylabel("Valor promedio")
axes[1].grid(True)
axes[1].legend()

# **Subplot 3: Error plot with mean and standard deviation**
scatter_data = np.array(scatter_data)


# Compute mean and standard deviation across files
mean_values = np.mean(scatter_data, axis=0)
std_values = np.std(scatter_data, axis=0)


# Define the step size (plot every N-th point)
step_size = 5  # Change this value to adjust density
# Select only every N-th point
indices = np.arange(0, len(mean_values), step_size)
mean_values = mean_values[indices]
std_values = std_values[indices]



# Create an error bar plot
axes[2].errorbar(range(len(mean_values)), mean_values, yerr=std_values, fmt='o', capsize=5, capthick=2, linestyle='-')

axes[2].set_title("Error Plot: Mean ± Standard Deviation Across CSV Files")
axes[2].set_xlabel("Column Index")
axes[2].set_ylabel("Value")
axes[2].grid(True)

# Mostrar la gráfica
plt.tight_layout()
plt.show()
