import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the provided file
file_path = './COMSOL_Data/10ul-min_50um.txt'
data = pd.read_csv(file_path, delim_whitespace=True, comment='%')

# Rename the columns for better readability
data.columns = ['x', 'y', 'z', 'Color']

# Display the first few rows of the dataframe
print(data.head())

# Plot the data
fig, ax = plt.subplots()
scatter = ax.scatter(data['x'], data['z'], c=data['Color'], cmap='viridis')

# Add a colorbar
cbar = plt.colorbar(scatter)
cbar.set_label('Color Value')

# Set plot labels
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_title('Scatter Plot with Color Value')

plt.show()