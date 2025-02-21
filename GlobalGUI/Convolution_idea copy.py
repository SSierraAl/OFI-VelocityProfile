import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
from numpy.fft import fft, ifft, fftshift
from scipy.optimize import curve_fit

# Define the Gaussian function
def gaussian(x, amp, mean, stddev):
    return amp * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

# Deconvolution using Tikhonov regularization
def deconvolve_tikhonov(C, A, alpha):
    C_fft = fft(C)
    A_fft = fft(A)
    A_conj_fft = np.conj(A_fft)
    deconv_fft = (A_conj_fft / (A_fft * A_conj_fft + alpha**2)) * C_fft
    deconv = ifft(deconv_fft)
    return np.real(deconv)

# Perform Gaussian fit
def perform_gaussian_fit(x, y):
    # Initial guess for the parameters: amplitude, mean, and standard deviation
    initial_guess = [max(y), np.mean(x), np.std(x)]
    
    # Perform the curve fitting
    popt, _ = curve_fit(gaussian, x, y, p0=initial_guess)
    
    # Extract the parameters
    amp, mean, stddev = popt
    return amp, mean, stddev

# Normalize a signal
def normalize(signal):
    return signal / np.max(np.abs(signal))

# Create x values
x = np.linspace(-20, 20, 1000)

# Define the Gaussian signals
X1 = gaussian(x, 5, -5, 2)
X2 = gaussian(x, 4, 0, 3)
X3 = gaussian(x, 6, 5, 1.5)
X4 = gaussian(x, 3, -10, 2)
L = gaussian(x, 5, 0, 2)

# Normalize the signals
X1 = normalize(X1)
X2 = normalize(X2)
X3 = normalize(X3)
X4 = normalize(X4)
L = normalize(L)

# Perform convolution
C1 = convolve(X1, L, mode='same')
C2 = convolve(X2, L, mode='same')
C3 = convolve(X3, L, mode='same')
C4 = convolve(X4, L, mode='same')

# Regularization parameter
alpha = 0.1

# Perform deconvolution
L_retrieved1 = deconvolve_tikhonov(C1, X1, alpha)
L_retrieved2 = deconvolve_tikhonov(C2, X2, alpha)
L_retrieved3 = deconvolve_tikhonov(C3, X3, alpha)
L_retrieved4 = deconvolve_tikhonov(C4, X4, alpha)

# Normalize the retrieved signals
L_retrieved1 = normalize(fftshift(L_retrieved1))
L_retrieved2 = normalize(fftshift(L_retrieved2))
L_retrieved3 = normalize(fftshift(L_retrieved3))
L_retrieved4 = normalize(fftshift(L_retrieved4))

# Fit the retrieved signals to Gaussian
amp1, mean1, stddev1 = perform_gaussian_fit(x, L_retrieved1)
amp2, mean2, stddev2 = perform_gaussian_fit(x, L_retrieved2)
amp3, mean3, stddev3 = perform_gaussian_fit(x, L_retrieved3)
amp4, mean4, stddev4 = perform_gaussian_fit(x, L_retrieved4)

# Plot the signals
plt.figure(figsize=(12, 8))
plt.plot(x, X1, label='Signal X1 (Gaussian)')
plt.plot(x, X2, label='Signal X2 (Gaussian)')
plt.plot(x, X3, label='Signal X3 (Gaussian)')
plt.plot(x, X4, label='Signal X4 (Gaussian)')
plt.plot(x, L, label='Signal L (Gaussian)', linestyle='dashed')
plt.legend()
plt.title('Original Gaussian Signals')
plt.show()

plt.figure(figsize=(12, 8))
plt.plot(x, C1, label='Convolution X1 * L')
plt.plot(x, C2, label='Convolution X2 * L')
plt.plot(x, C3, label='Convolution X3 * L')
plt.plot(x, C4, label='Convolution X4 * L')
plt.legend()
plt.title('Convolved Signals')
plt.show()

plt.figure(figsize=(12, 8))
plt.plot(x, L, label='Original Signal L (Gaussian)', linestyle='dashed')
plt.plot(x, L_retrieved1, label='Retrieved Signal L from X1')
plt.plot(x, L_retrieved2, label='Retrieved Signal L from X2')
plt.plot(x, L_retrieved3, label='Retrieved Signal L from X3')
plt.plot(x, L_retrieved4, label='Retrieved Signal L from X4')
plt.legend()
plt.title('Original and Retrieved Signals L')
plt.show()

# Print the fitted parameters
print(f"Retrieved Signal from X1: Amplitude={amp1}, Mean={mean1}, Stddev={stddev1}")
print(f"Retrieved Signal from X2: Amplitude={amp2}, Mean={mean2}, Stddev={stddev2}")
print(f"Retrieved Signal from X3: Amplitude={amp3}, Mean={mean3}, Stddev={stddev3}")
print(f"Retrieved Signal from X4: Amplitude={amp4}, Mean={mean4}, Stddev={stddev4}")

# Combine the retrieved signals to estimate the real signal L
L_combined = (L_retrieved1 + L_retrieved2 + L_retrieved3 + L_retrieved4) / 4

plt.figure(figsize=(12, 8))
plt.plot(x, L, label='Original Signal L (Gaussian)', linestyle='dashed')
plt.plot(x, L_combined, label='Combined Retrieved Signal L')
plt.legend()
plt.title('Original and Combined Retrieved Signal L')
plt.show()
