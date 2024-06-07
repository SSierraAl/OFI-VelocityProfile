import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt


def plot_grouped_error_bars(filename, num_groups):
    # Load the CSV file, assuming the first column is an index
    df = pd.read_csv(filename, index_col=0)
    

    # Invert the values in the DataFrame
    #df = df.apply(lambda row: row.max() + row.min() - row, axis=1)
        #df[column] = max_val + min_val - df[column]
    
    # Calculate mean and standard deviation for each column after inversion
    means = df.mean()
    std_devs = df.std()

    # Determine the number of columns per group
    num_columns = len(df.columns)
    columns_per_group = num_columns // num_groups
    remainder = num_columns % num_groups

    fig, axes = plt.subplots(num_groups, 1, figsize=(10, 8))  # Adjust the figure size as necessary
    fig.suptitle('Inverted Mean Values with Standard Deviation Error Bars by Group')

    for i in range(num_groups):
        start_idx = i * columns_per_group
        if i == num_groups - 1:  # Last group takes the remainder
            end_idx = start_idx + columns_per_group + remainder
        else:
            end_idx = start_idx + columns_per_group

        group_means = means[start_idx:end_idx]
        group_stds = std_devs[start_idx:end_idx]
        x = np.arange(len(group_means))  # the label locations for this subgroup

        # Plotting for this subgroup
        axes[i].errorbar(x, group_means, yerr=group_stds, fmt='o', ecolor='red', capthick=2, alpha=0.6, label='Mean ± 1 SD')
        axes[i].plot(x, group_means, 'bo-', label='Mean Trendline')  # Line connecting the means
        axes[i].set_ylabel('Values')
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(df.columns[start_idx:end_idx])
        axes[i].legend()

        for tick in axes[i].get_xticklabels():
            tick.set_rotation(45)

    plt.xlabel('Columns')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the global title
    plt.show()


plot_grouped_error_bars('./Angle_Impact/100_20degree/Scanning_Moments_Dev.csv', 4)
