import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data from the provided file
file_name='10ul-min_50um'


ext='.txt'
path='./COMSOL_Data/'
file_path = path+file_name+ext
data = pd.read_csv(file_path, delim_whitespace=True, comment='%')
# Rename the columns
data.columns = ['x', 'y', 'z', 'Speed']
Full_data=data.copy()
data=data[['x','Speed']]
# Bin edges
bins = np.arange(0, data['x'].max() + 2, 2)
# Bin the data
data['bin'] = pd.cut(data['x'], bins)
# Group by bins and calculate the average color for each bin
grouped = data.groupby('bin')['Speed'].mean().reset_index()
# Extract the bin centers for plotting
bin_centers = 0.5 * (bins[:-1] + bins[1:])

# Surface plot
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
scatter = axs[0].scatter(Full_data['x'], Full_data['z'], c=Full_data['Speed'], cmap='viridis')
axs[0].set_title(file_name)
# Add a colorbar
cbar = plt.colorbar(scatter)
cbar.set_label('Speed Value')

# 
axs[1].plot(bin_centers, grouped['Speed'], marker='o', linestyle='-')
# Set plot labels
axs[1].set_xlabel('X Coordinate Bin Center')
axs[1].set_ylabel('Average Speed Value')
axs[1].set_title(file_name)
plt.show()
# Display the averaged data
#print(grouped)
