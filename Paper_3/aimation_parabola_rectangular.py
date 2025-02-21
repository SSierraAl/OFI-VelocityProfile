import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

# Load the text file and skip the first 8 rows (metadata)
file_path = "Speed_Slices.txt"  # Update the path if necessary
data = pd.read_csv(file_path, delim_whitespace=True, skiprows=8, names=["cln1x", "Height"])

# Find indices where 'cln1x' is 0, which indicates the start of a new line
split_indices = data.index[data["cln1x"] == 0].tolist()

# Split the data into separate lines based on these indices
lines = [data.iloc[split_indices[i]:split_indices[i+1]] for i in range(len(split_indices) - 1)]
lines.append(data.iloc[split_indices[-1]:])  # Add the last segment

# Calculate the average height for each detected line (excluding first component)
average_heights = [line["Height"].mean() for line in lines]
line_indices = np.arange(1, len(average_heights) + 1)  # Remove first component
average_heights = np.array(average_heights[1:])
line_indices = np.array(line_indices[1:])

# ---------------- Animation Code ----------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

# Define window width
window_width = 80  

# Set axis limits
ax1.set_xlim(-window_width, len(line_indices) + window_width)  # Start outside and go beyond the range
ax1.set_ylim(0, max(average_heights) * 1.2)
ax1.set_title("Animación de Ventana sobre Alturas Promedio")
ax1.grid(True)

ax2.set_xlim(-window_width, len(line_indices) + window_width)
ax2.set_ylim(0, sum(average_heights) * 1.2)  
ax2.set_title("Suma Acumulada de Alturas Promedio")
ax2.grid(True)

# Plot the average heights as a bar chart
bars = ax1.bar(line_indices, average_heights, color='blue', alpha=0.6, label='Altura Promedio')
ax1.legend()

# Configurar la ventana rectangular (start outside the data range)
window = Rectangle((-window_width, 0), window_width, max(average_heights) * 1.2, 
                   facecolor='orange', alpha=0.5, edgecolor='black')
ax1.add_patch(window)

# Texto para mostrar la suma
sum_text = ax1.text(0.7, 0.9, '', transform=ax1.transAxes, fontsize=12, 
                   bbox=dict(facecolor='white', alpha=0.8))

# Variables de animación
velocidad = 1  # Speed of window movement
suma_visible = False
sum_values = []  # Stores the sum for each frame
window_positions = []  # Stores the window position for plotting

# Línea para la suma acumulada
sum_line, = ax2.plot([], [], 'r-', lw=2, label="Suma en Ventana")
ax2.legend()

def init():
    window.set_x(-window_width)  # Start completely outside
    sum_text.set_text('')
    sum_line.set_data([], [])
    return window, sum_text, sum_line

def animate(frame):
    global suma_visible
    x_pos = -window_width + frame * velocidad  # Move from outside (-window_width) to beyond the data

    # Move window
    window.set_x(x_pos)

    # Compute sum only when the window is fully inside the data range
    if x_pos + window_width > 0 and x_pos < len(line_indices):
        mask = (line_indices >= x_pos) & (line_indices < x_pos + window_width)
        suma = np.mean(average_heights[mask])
        sum_text.set_text(f'Suma: {suma:.2f}')
        suma_visible = True

        # Store values for sum graph
        sum_values.append(suma)
        window_positions.append(x_pos)

        # Update accumulated sum plot
        sum_line.set_data(window_positions, sum_values)
    else:
        sum_text.set_text('')

    return window, sum_text, sum_line

# Crear animación
ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=(len(line_indices) + 2 * window_width) // velocidad, 
                              interval=80, blit=True)

plt.show()
