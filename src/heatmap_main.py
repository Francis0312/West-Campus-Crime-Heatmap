# Changelog
# v0.7 11/4/2021 - cleaned up a bit
# v0.5 11/4/2021 8am - basic heatmap function working
# v0.2 11/4/2021 6am - filling matrix data
# v0.1 11/4/2021 5am - building fundamental framework
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
data_path = project_path + "/data/crime_reports01-2020_11-2021.csv" # data from Jan 2020-Nov 2021
digits_precision = 4

# gui info
green = '#00FF00'
yellow = '#FFFF00'
red = '#FF0000'
circle_radius = 18 # px
alpha = 0.2
circle_imgs = []

# Initializes GUI and backend
def main():
    # init backend data
    lat_long = data_lat_long(data_path)
    empty_heatmap = init_matrix(lat_long)
    heatmap = fill_matrix(empty_heatmap, lat_long)
    
    # init frontend data
    root = Tk()
    canvas = Canvas(root, width = 1166, height = 787)  
    canvas.pack()  
    img = ImageTk.PhotoImage(Image.open(map_img_path)) 
    canvas.create_image(0, 0, anchor=NW, image=img) 
    init_circles(root)
    draw_on_map(heatmap, map_img_path, root, canvas)
    root.mainloop() 
    

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
            y1 = int(pixels_per_lat * lat)   
            if 1 <= intensity < 5:
                canvas.create_image(x1, y1, image=circle_imgs[0], anchor='nw')
            elif 5 <= intensity < 10:
                canvas.create_image(x1, y1, image=circle_imgs[1], anchor='nw')
            elif intensity >= 10:
                canvas.create_image(x1, y1, image=circle_imgs[2], anchor='nw')
            

# Creates a circle with alpha value
def create_circle(x1, y1, x2, y2, root, canvas, **kwargs):      
    canvas.create_oval(x1, y1, x2, y2, outline='#000000', **kwargs)
            

# Tkinter hack to add opacity values
def init_circles(root):
    alpha_val = int(alpha * 255)
    red_fill = root.winfo_rgb(red) + (alpha_val,)
    orange_fill = root.winfo_rgb(yellow) + (alpha_val,)
    yellow_fill = root.winfo_rgb(green) + (alpha_val,)

    # Change radii offsets here
    red_cir = Image.new('RGBA', (circle_radius+5, circle_radius+5), red_fill)
    orange_cir = Image.new('RGBA', (circle_radius+5, circle_radius+5), orange_fill)
    yellow_cir = Image.new('RGBA', (circle_radius, circle_radius), yellow_fill)

    circle_imgs.append(ImageTk.PhotoImage(yellow_cir))
    circle_imgs.append(ImageTk.PhotoImage(orange_cir))
    circle_imgs.append(ImageTk.PhotoImage(red_cir))
    

# Fills the heatmap with values
def fill_matrix(empty_heatmap, lat_long):
    # pandas init
    data_frame = pd.read_csv(data_path)
    data_frame = data_frame.fillna(0) # replace NaN's with 0s to avoid corrutpion
    # translate values to doubles, only fetch coordinate data
    data_frame = data_frame[["Latitude","Longitude"]].astype(float) 
    max_latitude, max_longitude, min_latitude, min_longitude = lat_long[0], lat_long[1], lat_long[2], lat_long[3]

    # extract min and max latitudes
    for index, row in data_frame.iterrows():
        cur_lat = truncate(row["Latitude"], digits_precision)
        cur_long = truncate(row["Longitude"], digits_precision)
        # Avoid erroneous data points
        if (cur_lat != 0 and cur_long != 0):
            # round values to integers for matrix indexing
            lat_ind = round((cur_lat - min_latitude) * 10**digits_precision)
            long_ind = round((cur_long - min_longitude) * (10**digits_precision))

            # Avoid index out of bound on edge case coordinates
            # *TODO better solution to this*
            if (lat_ind == empty_heatmap.shape[0]):
                lat_ind -= 1
            if (long_ind == empty_heatmap.shape[1]):
                long_ind -= 1
            # increment value and values of surrounding cells!
            empty_heatmap[lat_ind, long_ind] += 1.0

    return empty_heatmap


# Initializes the 2D matrix that will encompass all of our data values
def init_matrix(lat_long):
    # calculate len and width
    max_latitude, max_longitude, min_latitude, min_longitude = lat_long[0], lat_long[1], lat_long[2], lat_long[3]
    max_height = (max_latitude - min_latitude) * (10**digits_precision)
    max_length = (max_longitude - min_longitude) * (10**digits_precision)

    # round from floats to integers
    max_height = round(max_height) 
    max_length = round(max_length)

    # numpy tings
    mat_shape = (max_height, max_length)
    empty_heatmap = np.zeros(shape=mat_shape)
    print(mat_shape)
    return empty_heatmap


# Reads the minimum and maximum latitude and longitude values from the data csv
# @return [max_latitude, max_longitude, min_latidude, min_longitude]
def data_lat_long(data_path):
    # pandas init
    data_frame = pd.read_csv(data_path)
    data_frame = data_frame.fillna(0) # replace NaN's with 0s to avoid corrutpion

    # translate values to doubles, only fetch coordinate data
    data_frame = data_frame[["Latitude","Longitude"]].astype(float) 
    # print(data_frame.head())
    max_latitude = -999.0
    min_latidude = 999.0
    max_longitude = -999.0
    min_longitude = 999.0

    # extract min and max latitudes
    for latitude in data_frame["Latitude"]:
        if latitude != 0.0:
            max_latitude = max(max_latitude, latitude)
            min_latidude = min(min_latidude, latitude)

    # extract min and max longitudes
    for longitude in data_frame["Longitude"]:
        if longitude != 0.0:
            max_longitude = max(max_longitude, longitude)
            min_longitude = min(min_longitude, longitude)
    
    # Truncate each float value
    lat_longs = [max_latitude, max_longitude, min_latidude, min_longitude]
    for i in range(len(lat_longs)):
        lat_longs[i] = truncate(lat_longs[i], digits_precision)
    return lat_longs
    

# Truncates a float to N digits past the decimal point
def truncate(float_param, N):
    integer = int(float_param * (10**N))/(10**N)
    return float(integer)


# Driver function for scripting
if __name__ == '__main__':
    main()
