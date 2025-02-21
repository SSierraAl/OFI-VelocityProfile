import matplotlib.pyplot as plt
import pandas as pd
# Load the CSV file
file_path = 'Scanning_Moments_CSV.csv'
data = pd.read_csv(file_path)

data = pd.read_csv(file_path, header=None)

# Extract the x values from the header row
x_values = data.iloc[0, 1:].values

# Plot each subsequent row as an independent line
plt.figure(figsize=(10, 6))

# Plot only the rows after the header
for i in range(1, data.shape[0]):
    y_values = data.iloc[i, 1:].values
    plt.plot(x_values, y_values, label=f'Row {i}')

# Adding labels and title
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Independent Line Plots of Each Row Against X values')
plt.legend()
plt.show()