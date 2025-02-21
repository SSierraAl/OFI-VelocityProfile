import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import convolve
from numpy.fft import fft, ifft, fftshift
from scipy.optimize import curve_fit



# Deconvolution using Tikhonov regularization
def deconvolve_tikhonov(C, A, alpha):
    C_fft = fft(C)
    A_fft = fft(A)
    A_conj_fft = np.conj(A_fft)
    deconv_fft = (A_conj_fft / (A_fft * A_conj_fft + alpha**2)) * C_fft
    deconv = ifft(deconv_fft)
    return np.real(deconv)


# Define the Gaussian function
def gaussian(x, amp, mean, stddev):
    return amp * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

# Define parabolic function
def parabola(x, a, b, c):
    return a * (x - b)**2 + c

# Normalize a signal
def normalize(signal):
    return signal / np.max(np.abs(signal))


def perform_parabolic_fit(x,y):
    popt, pcov = curve_fit(parabola, x, y, p0=[0.1, 70, 0])
    y_fit = parabola(x, *popt)

    return x, y_fit
    
# Perform Gaussian fit
def perform_gaussian_fit(x, y):
    # Initial guess for the parameters: amplitude, mean, and standard deviation
    initial_guess = [max(y), np.mean(x), np.std(x)]
    
    # Perform the curve fitting
    popt, _ = curve_fit(gaussian, x, y, p0=initial_guess)
    
    # Extract the parameters
    amp, mean, stddev = popt
    return amp, mean, stddev

# Define a function to calculate the moving average
def moving_average(values, window):
    avg_data= pd.Series(values).rolling(window=window).mean()
    avg_data=avg_data.fillna(method='bfill').astype('float')
    avg_data=avg_data.values
    return avg_data

# Load the CSV file
file_path = 'Scanning_Moments_CSV.csv'
data = pd.read_csv(file_path, header=None)
# Extract the x values from the header row
x_values = data.iloc[0, 1:].values
x_values= x_values-(max(x_values))/2
# Plot each subsequent row as an independent line
plt.figure(figsize=(10, 6))
# Plot only the rows after the header
window_size = 5  # Adjust the window size as needed


#Row ONE
y_values = data.iloc[1, 1:].values
y_invert=abs(max(y_values)-y_values)
y_smooth = moving_average(y_invert, window_size)
# Fit the retrieved signals to Gaussian
amp1, mean1, stddev1 = perform_gaussian_fit(x_values, y_smooth)
X1 = gaussian(x_values, amp1, mean1, stddev1)
#just to test
X1 = normalize(X1)
y_smooth = normalize(y_smooth)
plt.plot(x_values, y_smooth, label=f'Row {0}')
plt.plot(x_values, X1, label=f'Gaussian fit {0}')



#Row TWO
y2_values = data.iloc[2, 1:].values
y2_invert=abs(max(y2_values)-y2_values)
y2_smooth = moving_average(y2_invert, window_size)
# Fit the retrieved signals to Gaussian
amp2, mean2, stddev2 = perform_gaussian_fit(x_values, y2_smooth)
X2 = gaussian(x_values, amp2, mean2, stddev2)
#just to test
X2 = normalize(X2)
y2_smooth = normalize(y2_smooth)
plt.plot(x_values, y2_smooth, label=f'Row {1}')
plt.plot(x_values, X2, label=f'Gaussian fit {1}')


# Load the data from the text file Parabolic velocity profile
file_path = '100um_10ulmin.txt'

# Initialize lists to hold the data
x_valuesa = []
y_valuesa = []

# Read the file and parse the data
with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        # Skip metadata lines
        if line.startswith('%'):
            continue
        # Parse the data lines
        parts = line.split()
        if len(parts) == 2:
            x_valuesa.append(float(parts[0]))
            y_valuesa.append(float(parts[1]))

# Convert lists to pandas DataFrame
data = pd.DataFrame({'x': x_valuesa, 'y': y_valuesa})
#Center data arround zero
data['x']=data['x']-(max(data['x'])/2)
amp3, mean3, stddev3 = perform_gaussian_fit(data['x'], data['y'])
X_vel= gaussian(x_values, amp3, mean3, stddev3)
#just to test
X_vel = normalize(X_vel)
y_smooth_vel = normalize(data['y'])
# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(data['x'],y_smooth_vel, label='Speed')
plt.plot(x_values, X_vel, label='speed fit')




"""
# Regularization parameter
alpha = 2
# Perform deconvolution
L_retrieved1 = deconvolve_tikhonov(X1, X_vel, alpha)
L_retrieved1 = normalize(fftshift(L_retrieved1))
#plt.plot(x_values, L_retrieved1, label='Laser signal')
plt.plot(x_values, X1, label='Momento')


#Gaussian fit of the laser signal
amp_laser, mean_laser, stddev_laser = perform_gaussian_fit(x_values, L_retrieved1)
X_Laser = gaussian(x_values, amp_laser, 0, stddev_laser)
plt.plot(x_values, X_Laser, label='Laser_fit')

#check if i can reach the moment 2
"""

# Load the data from the CSV file
df = pd.read_csv('data_laser.csv')
X_Laser = df['X_Laser']

alpha=2
plt.figure(figsize=(10, 6))
thep_speed = deconvolve_tikhonov(X_Laser, X1,alpha)
thep_speed = normalize(fftshift(thep_speed))
amp_momento, mean_momento, stddev_momento = perform_gaussian_fit(x_values, thep_speed)
#thep_speed = gaussian(x_values, amp_momento, 40, stddev_momento)
#thep_speed = normalize(fftshift(thep_speed))
plt.plot(x_values, thep_speed, label='Convolution X1 * L')
plt.plot(x_values, X_vel, label=f'Real speed {1}')


# Assuming x_values and X_Laser are numpy arrays or lists
#data = np.column_stack((x_values, X_Laser))
#df = pd.DataFrame(data, columns=['x_values', 'X_Laser'])
#df.to_csv('data.csv', index=False)






# Adding labels and title
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Independent Line Plots of Each Row Against X values')
plt.legend()
plt.show()
plt.show()