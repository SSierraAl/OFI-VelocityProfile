"""Module for reading, processing and displaying .csv measurement data
"""
import numpy as np

from math import pi

import pandas as pd

from bokeh.models import LogColorMapper
from bokeh.models import BasicTicker, PrintfTickFormatter
from bokeh.plotting import figure, show
from bokeh.sampledata.unemployment1948 import data
from bokeh.transform import linear_cmap

class Data_processing:
    def __init__ (self, main_window):
        main_window = main_window
        self.moments = None    
        
    def read_moments(self, folder_name):
        """Function for reading .csv moments
        """
        # read_csv with pandas of scanning_moments_csv.csv
        # save it to pandas series in such a way that it can easily be manipulated
        
        #index_col = 0 takes the first column in the csv file and uses those as the pandas series index
        path = f"../measurements_to_analyse/{folder_name}/Scanning_Moments_CSV.csv"
        moments = pd.read_csv(path, index_col=0)
        
        #TEMPORARY:
        self.moments = moments
        
        return moments
        
    def change_moments(self):
        """Function for manipulating the moments read from the CSV file
        """
        self.moments = self.moments.add(100)
        
    def normal2d(self,X, Y, sigx=1.0, sigy=1.0, mux=0.0, muy=0.0):
        z = (X-mux)**2 / sigx**2 + (Y-muy)**2 / sigy**2
        return np.exp(-z/2) / (2 * np.pi * sigx * sigy)
        
    def display_moments_plot_test2(self):
        global data 
        data['Year'] = data['Year'].astype(str)
        data = data.set_index('Year')
        data.drop('Annual', axis=1, inplace=True)
        data.columns.name = 'Month'

        years = list(data.index)
        months = list(reversed(data.columns))

        # reshape to 1D array or rates with a month and year for each row.
        df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()

        # this is the colormap from the original NYTimes plot
        colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]

        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

        p = figure(title=f"US Unemployment ({years[0]} - {years[-1]})",
                x_range=years, y_range=months,
                x_axis_location="above", width=900, height=400,
                tools=TOOLS, toolbar_location='below',
                tooltips=[('date', '@Month @Year'), ('rate', '@rate%')])

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.grid.visible = False
        p.xgrid.visible = False
        p.ygrid.visible = False
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "7px"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi / 3

        # Putting width and height to 1.01/1.02 removes the white spacing between blocks.
        r = p.rect(x="Year", y="Month", width=1, height=1, source=df,
                fill_color=linear_cmap("rate", colors, low=df.rate.min(), high=df.rate.max()),
                line_color=None)
        
        r = p.rect(x="Year", y="Month", width=1.02, height=1.02, source=df,
                fill_color=linear_cmap("rate", colors, low=df.rate.min(), high=df.rate.max()),
                line_color=None)

        p.add_layout(r.construct_color_bar(
            major_label_text_font_size="7px",
            ticker=BasicTicker(desired_num_ticks=len(colors)),
            formatter=PrintfTickFormatter(format="%d%%"),
            label_standoff=6,
            border_line_color=None,
            padding=5,
        ), 'right')

        show(p)

    def display_moments_lines(self):
        """Plots multiple rows of moments in separate lines
        NOTE: not finished, just for testing purposes
        """
        
        
        moments_plot = figure(title='Moments', x_axis_label='Index', y_axis_label='Moment')

        x = self.moments.columns.to_list()
        print(x)
        
        y = self.moments.iloc[0]
        print(y)
        
        y2= self.moments.iloc[1]
        print(y2)
        
        moments_plot.line(x, y, legend_label="Scan Row 1", line_width=2, color="red")
        moments_plot.line(x, y2, legend_label="Scan Row 2", line_width=2, color="blue")
        moments_plot.scatter(x, y2, legend_label="test", line_width=2, color="pink")
        
        scatter = moments_plot.scatter(
            x,
            y,
            marker="circle",
            size=10,
            legend_label="Objects",
            fill_color="red",
            fill_alpha=0.5,
            line_color="blue",
        )
        # edit scatter
        glyph = scatter.glyph
        glyph.fill_color = 'blue'
        
        show(moments_plot)
        
data_processing_instance = Data_processing(None)
data_processing_instance.read_moments()
print(data_processing_instance.moments)

data_processing_instance.change_moments()
print(data_processing_instance.moments)

#data_processing_instance.display_moments_plot_test2()
data_processing_instance.display_moments_lines()