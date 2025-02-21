import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy.fft import fft, ifft, fftshift
from scipy.optimize import curve_fit
import os

# Define a function to calculate the moving average
def moving_average(values, window):
    avg_data = pd.Series(values).rolling(window=window).mean()
    avg_data = avg_data.fillna(method='bfill').astype('float')
    avg_data = avg_data.values
    return avg_data

# Define the directory containing the files
file_path = './Moments_Comp/'

# Initialize a figure for plotting
plt.figure(figsize=(10, 6))

# Iterate over all files in the directory
for file_name in os.listdir(file_path):
    if file_name.endswith('.csv'):
        data = pd.read_csv(file_path + file_name, header=None)
        
        # Extract the x values from the header row
        x_values = data.iloc[0, 1:].values
        x_values = x_values - (max(x_values)) / 2
        
        # Plot each subsequent row as an independent line
        window_size = 2  # Adjust the window size as needed
        
        # Iterate over each row (after the header) in the file
        for row in range(1, len(data)):
            y_values = data.iloc[row, 1:].values
            y_invert = abs(max(y_values) - y_values)
            y_smooth = moving_average(y_invert, window_size)
            plt.plot(x_values, y_smooth, label=f'{file_name} row {row}')
        
plt.title('Flow Rate')
#plt.legend()
plt.show()