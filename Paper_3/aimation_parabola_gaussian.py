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
line_indices = np.arange(1, len(average_heights) + 1)
average_heights = np.array(average_heights[1:])
line_indices = np.array(line_indices[1:])

average_heights = average_heights / max(average_heights)
window_size = 90
cumulative_avg = []

for i in range(1, len(average_heights) + window_size):
    start_idx = max(0, i - window_size)  # Ensure the window stays within bounds
    end_idx = min(i, len(average_heights))  # Ensure we don't go past the list length
    if start_idx < len(average_heights):
        cumulative_avg.append(np.mean(average_heights[start_idx:end_idx]))
    else:
        cumulative_avg.append(0)  # Go back to zero when the window moves out

average_heights=cumulative_avg
line_indices = np.arange(1, len(average_heights) + 1)
average_heights = np.array(average_heights[1:])
line_indices = np.array(line_indices[1:])
# ---------------- Animation Code ----------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

# Define window width
window_width = 90  

# Gaussian parameters
mu = window_width / 2  # Center of the Gaussian
sigma = window_width / 2  # Spread (adjustable)

x = np.arange(window_width)  # Position values
gaussian_vector = np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))
gaussian_vector = gaussian_vector / max(gaussian_vector)

# Set axis limits
ax1.set_xlim(-window_width, len(line_indices) + window_width)
ax1.set_ylim(0, max(average_heights) * 1.2)
ax1.set_title("Animation of Gaussian Window Over Average Heights")
ax1.grid(True)

ax2.set_xlim(-window_width, len(line_indices) + window_width)
ax2.set_ylim(0, 100)
ax2.set_title("Accumulated Sum of Average Heights")
ax2.grid(True)

# Plot the average heights as a bar chart
bars = ax1.bar(line_indices, average_heights, color='blue', alpha=0.6, label='Average Height')
ax1.legend()

# Configure the rectangular window (start outside the data range)
window = Rectangle((-window_width, 0), window_width, max(average_heights) * 1.2, 
                   facecolor='orange', alpha=0.5, edgecolor='black')
ax1.add_patch(window)

# Text to show the sum
sum_text = ax1.text(0.7, 0.9, '', transform=ax1.transAxes, fontsize=12, 
                     bbox=dict(facecolor='white', alpha=0.8))

# Animation variables
velocity = 1  # Speed of window movement
sum_values = []  # Stores the sum for each frame
window_positions = []  # Stores the window position for plotting

# Line for accumulated sum
sum_line, = ax2.plot([], [], 'r-', lw=2, label="Sum in Window")
ax2.legend()

def init():
    window.set_x(-window_width)  # Start completely outside
    sum_text.set_text('')
    sum_line.set_data([], [])
    return window, sum_text, sum_line

def animate(frame):
    x_pos = -window_width + frame * velocity  # Move from outside (-window_width) to beyond the data
    window.set_x(x_pos)

    # Compute sum only when the window is inside the data range
    if x_pos + window_width > 0 and x_pos < len(line_indices):
        mask = (line_indices >= x_pos) & (line_indices < x_pos + window_width)
        
        # Get indices within the window
        selected_line_indices = line_indices[mask]
        x_in_window = (selected_line_indices - x_pos).astype(int)
        
        # Ensure valid indices
        valid_indices = (x_in_window >= 0) & (x_in_window < window_width)
        x_in_window = x_in_window[valid_indices]
        selected_heights = average_heights[mask][valid_indices]
        



        # Create vector_data with correct positioning
        vector_data = np.zeros(window_width)
        vector_data=average_heights[mask]
        #nuevo_vector = np.pad(nuevo_vector, (0, window_width - len(nuevo_vector)), constant_values=0)

        #vector_data[nuevo_vector != 0] = nuevo_vector[nuevo_vector != 0]

        
        # Apply Gaussian weighting

        weighted_sum=np.mean((vector_data))
        
        sum_text.set_text(f'Sum: {weighted_sum:.2f}')
        
        # Store values for sum graph
        sum_values.append(weighted_sum)
        window_positions.append(x_pos)

        # Update accumulated sum plot
        sum_line.set_data(window_positions, sum_values)
    else:
        sum_text.set_text('')
    
    return window, sum_text, sum_line

# Create animation
ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=(len(line_indices) + 2 * window_width) // velocity, 
                              interval=20, blit=True)

plt.show()
