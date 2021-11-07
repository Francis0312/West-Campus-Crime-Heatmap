# Changelog
# v1.3 11/7/2021 - style fixes
# v1.2 11/5/2021 - fixed erronouos implementation completely!
# v1.1 11/5/2021 - cleanup unused methods from old erroneous implementation
# v1.0 11/5/2021 - fixed bug with incorrect lat/long calculation, is correct now
# v0.7 11/4/2021 - cleaned up a bit
# v0.5 11/4/2021 - basic heatmap function working (might be slightly off)
# v0.2 11/4/2021 - filling matrix data
# v0.1 11/4/2021 - building fundamental framework
#
# *****************************************************************************
# A program used to draw a heatmap of all the crime in West Campus, 
# which has been quite a serious issue in recent times here at UT
#
# The data here is from January 1, 2020 to November 3, 2021
# and is located in the zip code of 78705, which is outlined in red on the map
# *****************************************************************************
# @author Francisco Reyna
# UT Austin Computer Science

# imports
import cv2 # openCV2 used for image handling
import pandas as pd # used to read & analyze csv files
import numpy as np
from tkinter import * # Main GUI library
from PIL import ImageTk, Image # used to support jpeg/png formats in tkinter

# global constants
project_path = "C:/Users/pacot/Documents/Python Projects/crime_heatmap"
map_img_path = project_path + "/images/map.png" # background map of west campus
# data from Jan 2020-Nov 2021
#data_path = project_path + "/data/crime_reports01-2020_11-2021.csv" 
# data from Jan 2020-Nov 2021
data_path = project_path + "/data/crime_report2.csv" 
output_path = project_path + "/output/"
digits_precision = 4 # 4 is standard, 5 is slower but more accurate

# gui info constants
green = '#00FF00'
yellow = '#FFFF00'
red = '#FF0000'
radius = 18 # px
size_offset = 5 # px to make yellow & red larger
alpha = 0.2
circle_imgs = []

# constants from map img
MAX_LAT = 30.29850750
MAX_LONG = -97.72422740
MIN_LAT = 30.2804484
MIN_LONG = -97.75507970

# Initializes GUI and backend
def main():
    # init backend data
    empty_heatmap = init_matrix()
    heatmap = fill_matrix(empty_heatmap)
    
    # init frontend data
    root = Tk()
    canvas = Canvas(root, width = 1166, height = 787)  
    canvas.pack()  
    img = ImageTk.PhotoImage(Image.open(map_img_path)) 
    canvas.create_image(0, 0, anchor=NW, image=img) 
    
    # display backend data
    init_circles(root)
    draw_on_map(heatmap, map_img_path, root, canvas)
    
    # save to jpg file
    filename = ""
    canvas.update()
    #save_as_png(canvas, 'heatmap')
    root.mainloop() 
    
    
# Saves the Tkinter canvas object as an image for sharing :)
def save_as_png(canvas, fileName):
    # save postscipt image 
    canvas.postscript(file = fileName + '.eps') 
    # use PIL to convert to PNG 
    img = Image.open(fileName + '.eps') 
    img = img.save(fileName + '.png', 'png') 


# Draws each shape point of the 2D matrix onto the canvas image (map)_
def draw_on_map(heatmap, map_img_path, root, canvas):
    # loading image
    map_image = cv2.imread(map_img_path)
    map_height_px = map_image.shape[0]
    map_length_px = map_image.shape[1]

    # conversion factors
    pixels_per_lat = float(map_height_px) / heatmap.shape[0]
    pixels_per_long = float(map_length_px) / heatmap.shape[1]

    # loop through all coordinates
    for lat in range(heatmap.shape[0]):
        for long in range(heatmap.shape[1]):
            # create circle at this point
            intensity = heatmap[lat][long]
            x1 = int(pixels_per_long * long)
            # since lat grows south to north, we have to flip the y values 
            y1 = int(pixels_per_lat * (heatmap.shape[0]-lat)  )
            # * subtractions are to center the squares over the actual point 
            # they represent *
            # draw green points
            if 1 <= intensity < 5: 
                canvas.create_image(x1-radius, y1-radius, image=circle_imgs[0],
                                    anchor='nw')
            # draw yellow points
            elif 5 <= intensity < 10:
                canvas.create_image(x1-radius-size_offset, y1-radius-size_offset,
                                    image=circle_imgs[1], anchor='nw')
            # draw red points
            elif intensity >= 10:
                canvas.create_image(x1-radius-size_offset, y1-radius-size_offset,
                                    image=circle_imgs[2], anchor='nw')
            

# Creates a circle with alpha value
def create_circle(x1, y1, x2, y2, root, canvas, **kwargs):      
    canvas.create_oval(x1, y1, x2, y2, outline='#000000', **kwargs)
            

# Tkinter hack to add opacity values
def init_circles(root):
    alpha_val = int(alpha * 255)
    red_fill = root.winfo_rgb(red) + (alpha_val,)
    orange_fill = root.winfo_rgb(yellow) + (alpha_val,)
    green_fill = root.winfo_rgb(green) + (alpha_val,)

    # Change radii offsets here
    red_cir = Image.new('RGBA', (radius+size_offset, radius+size_offset),
                                 red_fill)
    yellow_cir = Image.new('RGBA', (radius+size_offset, radius+size_offset),
                                    orange_fill)
    green_cir = Image.new('RGBA', (radius, radius), green_fill)

    circle_imgs.append(ImageTk.PhotoImage(green_cir))
    circle_imgs.append(ImageTk.PhotoImage(yellow_cir))
    circle_imgs.append(ImageTk.PhotoImage(red_cir))
    

# Fills the heatmap with values
def fill_matrix(empty_heatmap):
    # pandas init
    data_frame = pd.read_csv(data_path)
    data_frame = data_frame.fillna(0) # replace NaN's with 0s to avoid corrutpion
    # translate values to doubles, only fetch coordinate data
    data_frame = data_frame[["Latitude","Longitude"]].astype(float) 

    # extract min and max latitudes
    for index, row in data_frame.iterrows():
        cur_lat = truncate(row["Latitude"], digits_precision)
        cur_long = truncate(row["Longitude"], digits_precision)
        # Avoid erroneous data points
        if (cur_lat != 0 and cur_long != 0 and fit_in_img(cur_lat, cur_long)):
            # round values to integers for matrix indexing
            lat_ind = round((cur_lat - MIN_LAT) * 10**digits_precision)
            long_ind = round((cur_long - MIN_LONG) * (10**digits_precision))

            # Avoid index out of bound on edge case coordinates
            # *TODO better solution to this*
            if (lat_ind == empty_heatmap.shape[0]):
                lat_ind -= 1
            if (long_ind == empty_heatmap.shape[1]):
                long_ind -= 1
            # increment value and values of surrounding cells!
            empty_heatmap[lat_ind, long_ind] += 1.0

    return empty_heatmap


# Makes sure a point fits in the image
def fit_in_img(cur_lat, cur_long):
    return cur_lat <= MAX_LAT and cur_long <= MAX_LONG


# Initializes the 2D matrix that will encompass all of our data values
def init_matrix():
    # calculate len and width
    max_height = (MAX_LAT - MIN_LAT) * (10**digits_precision)
    max_length = (MAX_LONG - MIN_LONG) * (10**digits_precision)

    # round from floats to integers bc array len and height 
    max_height = round(max_height) 
    max_length = round(max_length)

    # numpy tings - create empty heatmap with values
    mat_shape = (max_height, max_length)
    empty_heatmap = np.zeros(shape=mat_shape)
    return empty_heatmap
    

# Truncates a float to N digits past the decimal point
def truncate(float_param, N):
    integer = int(float_param * (10**N))/(10**N)
    return float(integer)


# Driver function for scripting
if __name__ == '__main__':
    # TODO implement scripting by accepting a csv file and filename
    main()