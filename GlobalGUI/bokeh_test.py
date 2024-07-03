import random
import numpy as np
from bokeh.plotting import figure, show
from bokeh.layouts import row

def vectorize_color():
    # generate some data (1-10 for x, random values for y)
    x = list(range(0, 26))
    y = random.sample(range(0, 100), 26)

    # generate list of rgb hex colors in relation to y
    colors = [f"#{255:02x}{int((value * 255) / 100):02x}{255:02x}" for value in y]

    # create new plot
    p = figure(
        title="Vectorized colors example",
        sizing_mode="stretch_width",
        max_width=500,
        height=250,
    )

    # add line and scatter renderers
    p.line(x, y, line_color="blue", line_width=1)
    p.scatter(x, y, fill_color=colors, line_color="blue", size=15)

    # show the results
    show(p)

def vectorize_color_and_size():


    # generate some data
    N = 1000
    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100

    # generate radii and colors based on data
    radii = y / 100 * 2
    colors = [f"#{255:02x}{int((value * 255) / 100):02x}{255:02x}" for value in y]

    # create a new plot with a specific size
    p = figure(
        title="Vectorized colors and radii example",
        sizing_mode="stretch_width",
        max_width=500,
        height=250,
    )

    # add circle renderer
    p.circle(
        x,
        y,
        radius=radii,
        fill_color=colors,
        fill_alpha=0.6,
        line_color="lightgrey",
    )

    # show the results
    show(p)
    
    
def combining_plots():
    # prepare some data
    x = list(range(11))
    y0 = x
    y1 = [10 - i for i in x]
    y2 = [abs(i - 5) for i in x]

    # create three plots with one renderer each
    s1 = figure(width=250, height=250, background_fill_color="#fafafa")
    s1.scatter(x, y0, marker="circle", size=12, color="#53777a", alpha=0.8)

    s2 = figure(width=250, height=250, background_fill_color="#fafafa")
    s2.scatter(x, y1, marker="triangle", size=12, color="#c02942", alpha=0.8)

    s3 = figure(width=250, height=250, background_fill_color="#fafafa")
    s3.scatter(x, y2, marker="square", size=12, color="#d95b43", alpha=0.8)

    # put the results in a row and show
    show(row(s1, s2, s3))
    
    
combining_plots()

