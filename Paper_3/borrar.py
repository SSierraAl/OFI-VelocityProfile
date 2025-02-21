import numpy as np
import matplotlib.pyplot as plt

# Define the window size and Gaussian parameters
window_size = 65
sigma = window_size / 2  # Standard deviation for Gaussian kernel

# Compute the Gaussian kernel
gaussian_kernel = np.exp(-1 * ((np.arange(window_size) - (window_size / 2)) / sigma) ** 2)
gaussian_kernel /= gaussian_kernel.sum()  # Normalize the kernel
gaussian_kernel=gaussian_kernel/max(gaussian_kernel)

# Plot the Gaussian kernel
plt.figure(figsize=(8, 5))
plt.plot(gaussian_kernel, marker='o', linestyle='-', color='blue', label="Gaussian Kernel")
plt.xlabel("Window Index")
plt.ylabel("Weight")
plt.title("Gaussian Kernel (Window Size = 65)")
plt.legend()
plt.grid(True)
plt.show()