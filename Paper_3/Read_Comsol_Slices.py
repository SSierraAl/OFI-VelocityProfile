import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
from scipy.stats import skewnorm
from scipy.ndimage import gaussian_filter1d
# Load the text file and skip the first 8 rows (metadata)
file_path = "Speed_Slices_vascular.txt"  # Update the path if necessary
data = pd.read_csv(file_path, delim_whitespace=True, skiprows=8, names=["cln1x", "Height"])

# Find indices where 'cln1x' is 0, which indicates the start of a new line
split_indices = data.index[data["cln1x"] == 0].tolist()

# Split the data into separate lines based on these indices
lines = [data.iloc[split_indices[i]:split_indices[i+1]] for i in range(len(split_indices) - 1)]
lines.append(data.iloc[split_indices[-1]:])  # Add the last segment

# Calculate the average height for each detected line and remove the first component
average_heights = [line["Height"].mean() for line in lines]
line_indices = np.arange(1, len(average_heights) + 1)  # Remove first component
average_heights = average_heights[1:]
line_indices = line_indices[1:]


# Compute the cumulative moving average with a rectangular window of size 20
window_size =100
cumulative_avg = []

for i in range(1, len(average_heights) + window_size):
    start_idx = max(0, i - window_size)  # Ensure the window stays within bounds
    end_idx = min(i, len(average_heights))  # Ensure we don't go past the list length
    if start_idx < len(average_heights):
        cumulative_avg.append(np.mean(average_heights[start_idx:end_idx]))
    else:
        cumulative_avg.append(0)  # Go back to zero when the window moves out

# Create subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 15))
plt.rcParams.update({
    "font.family": "serif",  # Uses the closest available serif font
    "font.size": 20
})
# First subplot: Original multiple line plots
for i, line in enumerate(lines[1:]):  # Skip first line
    axes[0].plot(line["cln1x"], line["Height"], label=f'Line {i + 2}')  # Adjust labels

axes[0].set_xlabel("cln1x")
axes[0].set_ylabel("Height")
#axes[0].set_title("Multiple Line Plots from Speed Slices Data")
#axes[0].legend()
axes[0].grid(True)
# Second subplot: Average height per line (after removing first component)
axes[1].plot(line_indices, average_heights,  marker='o', linestyle='-')
axes[1].set_xlabel("Line Number")
axes[1].set_ylabel("Average Height")
#axes[1].set_title("Average Height for Each Line")
axes[1].set_xticks(line_indices)
#axes[1].grid(True)

# Third subplot: Cumulative moving average with a window of size 20, going back to zero
full_indices = np.arange(1, len(cumulative_avg) + 1)

#cumulative_avg=cumulative_avg/max(cumulative_avg)


axes[2].plot(full_indices, cumulative_avg, marker='o', linestyle='-', color='red', label="Cumulative Moving Average")
axes[2].set_xlabel("Window Step")
axes[2].set_ylabel("Cumulative Average Height")
#axes[2].set_title("Cumulative Moving Average of Heights (Window Size = 20)")
#axes[2].legend()
#axes[2].grid(True)

# Show the plots
plt.tight_layout()
#plt.show()

# Define padding size
padding_size = 100
sigma = 10
# Extend cumulative_avg with zero padding
padded_cumulative_avg = np.pad(cumulative_avg, (padding_size, padding_size), mode='constant', constant_values=0)
#padded_cumulative_avg/= np.max(padded_cumulative_avg)


# Apply Gaussian smoothing using scipy's Gaussian filter
smoothed_signal = gaussian_filter1d(padded_cumulative_avg, sigma=sigma)

# Crop to focus on the main part of the signal (optional)
start_crop = padding_size // 2
end_crop = len(smoothed_signal) - padding_size // 2
cropped_signal = smoothed_signal[start_crop:end_crop]  # Crop center part

# Plot Results
plt.figure(figsize=(10, 5))
plt.rcParams.update({
    "font.family": "serif",  # Uses the closest available serif font
    "font.size": 20
})

num_points = len(padded_cumulative_avg)
x_values = np.linspace(-0.5, 0.5, num_points)

plt.plot(x_values,padded_cumulative_avg, label='Rectangular', color='red', linestyle='dashed', alpha=0.8, linewidth=2.0)
plt.plot(x_values,smoothed_signal, label='Gaussian', linewidth=2.0)
#plt.plot(cropped_signal, label='Cropped Smoothed Signal', color='green', linestyle='dotted')

plt.xlabel("y/w")
plt.ylabel("[mm/s]")
#plt.title("Smoothed and Shortened Signal Using Gaussian Kernel")
plt.legend(loc='upper right')
plt.grid()
plt.show()