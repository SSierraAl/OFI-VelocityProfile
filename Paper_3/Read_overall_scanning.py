import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
import numpy as np
# Cargar el archivo CSV
file_path = "Scanning_Moments_CSV_3.csv"
df = pd.read_csv(file_path, header=None)

# Eliminar la primera fila y la primera columna
df_cleaned = df.iloc[1:, 1:].astype(float)



# Aplicar el preprocesamiento a cada fila
processed_data = []

for row in range(df_cleaned.shape[0]):
    y_values = df_cleaned.iloc[row, :].values  # Obtener los valores de la fila
    average_min_value = np.mean(pd.Series(y_values).nsmallest(10))
    average_max_value = np.mean(pd.Series(y_values).nlargest(10))
    y_values_short = (abs(average_min_value) - y_values) + average_max_value
    y_values_short = y_values_short - min(y_values_short)  # Ajustar valores mínimos
    processed_data.append(y_values_short)

# Convertir a DataFrame
df_processed = pd.DataFrame(processed_data)

# Función de escalado
def scale_value(value):
    return (value * 0.001550) / (2 * math.cos(math.radians(72)))

# Aplicar la función de escalado a toda la data
df_scaled = df_processed.applymap(scale_value)



# Configurar el tamaño de la figura
plt.figure(figsize=(10, 8))

sns.set(font="serif")  # Usar una fuente serif
ax = sns.heatmap(df_scaled, cmap="mako", annot=False, cbar=True)

# Etiquetas de los ejes
plt.xlabel("X-Steps", fontsize=18, fontfamily="serif")
plt.ylabel("Y-Steps", fontsize=18, fontfamily="serif")

# Ajustar el tamaño de los números en los ejes
ax.tick_params(axis='x', labelsize=20)  # Tamaño de los números en el eje X
ax.tick_params(axis='y', labelsize=20)  # Tamaño de los números en el eje Y

# Mostrar solo algunas etiquetas en el eje X
num_labels = 5  # Número de etiquetas que quieres mostrar
x_ticks = np.linspace(0, df_scaled.shape[1] - 1, num_labels, dtype=int)  # Posiciones de los ticks
ax.set_xticks(x_ticks)  # Aplicar las posiciones de los ticks
ax.set_xticklabels(x_ticks, rotation=0)  # Mantener las etiquetas horizontales



# Mostrar solo algunas etiquetas en el eje X
num_labels = 5  # Número de etiquetas que quieres mostrar
y_ticks = np.linspace(0, df_scaled.shape[0]-1, num_labels, dtype=int)  # Posiciones de los ticks
ax.set_yticks(y_ticks)  # Aplicar las posiciones de los ticks
ax.set_yticklabels(y_ticks, rotation=0)  # Mantener las etiquetas horizontales
# Mantener las etiquetas del eje Y horizontales
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

# Invertir el eje Y para que el 0 esté abajo
ax.invert_yaxis()

# Ajustar el tamaño de los números en la escala de color
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=20) 
cbar.set_label("[mm/s]", fontsize=20, fontfamily="serif", rotation=-90, labelpad=20)  # Nombre del mapa de color

# Mostrar el heatmap
plt.show()