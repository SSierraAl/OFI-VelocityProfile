import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
from numpy.fft import fft, ifft, fftshift
from scipy.optimize import curve_fit

# Create x values
x = np.linspace(-20, 20, 1000)

# Define two Gaussian signals A and B
Laser = gaussian(x, mean=0, std_dev=3)
Real_Vel = gaussian(x, mean=0, std_dev=2)

# Perform convolution
Moments = convolve(Laser, Real_Vel, mode='same')

# Deconvolution using Tikhonov regularization
def deconvolve_tikhonov(C, A, alpha):
    C_fft = fft(C)
    A_fft = fft(A)
    A_conj_fft = np.conj(A_fft)
    deconv_fft = (A_conj_fft / (A_fft * A_conj_fft + alpha**2)) * C_fft
    deconv = ifft(deconv_fft)
    return np.real(deconv)

# Regularization parameter
alpha = 0.1

# Perform deconvolution
Laser_retrived = deconvolve_tikhonov(Moments, Laser, alpha)

# Center the retrieved signal B
Laser_retrived = fftshift(Laser_retrived)

# Since the length of B_retrieved will not match x, we need to truncate or pad
Laser_retrived = np.pad(Laser_retrived, (0, len(x) - len(Laser_retrived)), 'constant')

# Define the Gaussian function
def gaussian(x, amp, mean, stddev):
    return amp * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

def perform_gaussian_fit(x, y):
    # Initial guess for the parameters: amplitude, mean, and standard deviation
    initial_guess = [max(y), np.mean(x), np.std(x)]
    
    # Perform the curve fitting
    popt, _ = curve_fit(gaussian, x, y, p0=initial_guess)
    
    # Extract the parameters
    amp, mean, stddev = popt
    return amp, mean, stddev

amp, mean, stddev = perform_gaussian_fit(x, Laser_retrived)
print(amp)
print(mean)
print(stddev)

# Plot the signals
plt.figure(figsize=(12, 8))
plt.plot(x, Laser, label='Signal A (Gaussian)')
plt.plot(x, Real_Vel, label='Signal B (Gaussian)')
plt.plot(x, Moments, label='Convolution (A * B)')
plt.legend()
plt.title('Gaussian Signals and Their Convolution')
#plt.show()

# Plot the original and retrieved B signals using Tikhonov regularization
plt.figure(figsize=(12, 8))
plt.plot(x, Laser, label='Original Signal B (Gaussian)')
plt.plot(x, Laser_retrived, label='Retrieved Signal B (Tikhonov Deconvolution)')
plt.legend()
plt.title('Original and Retrieved Signal B with Tikhonov Regularization')
plt.show()


