# Changelog
# v0.1 11/4/2021 6am - building fundamental framework
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
import map_bounds # used for internal data matrix 
import pandas as pd # used to read & analyze csv files
import numpy as np
from tkinter import * # Main GUI library
from PIL import ImageTk, Image # used to support jpeg/png formats in tkinter

# global constants
project_path = "C:/Users/pacot/Documents/Python Projects/crime_heatmap"
map_img_path = project_path + "/images/map.png" # background map of west campus
data_path = project_path + "/data/crime_reports01-2020_11-2021.csv" # data from Jan 2020-Nov 2021
digits_precision = 4

# Initializes GUI and backend
def main():
    lat_long = data_lat_long(data_path)
    empty_heatmap = init_matrix(lat_long)
    heatmap = fill_matrix(empty_heatmap, lat_long)
    print(heatmap)
    #root = Tk()
    #init_gui(root)

# Fills the heatmap with values
def fill_matrix(empty_heatmap, lat_long):
    # pandas init
    data_frame = pd.read_csv(data_path)
    data_frame = data_frame.fillna(0) # replace NaN's with 0s to avoid corrutpion
    # translate values to doubles, only fetch coordinate data
    data_frame = data_frame[["Latitude","Longitude"]].astype(float) 
    max_latitude, max_longitude, min_latitude, min_longitude = lat_long[0], lat_long[1], lat_long[2], lat_long[3]

    i = 0
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
            # *TODO better solution to this&
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


# Initializes the GUI of the system, loads background map image
def init_gui(root):
    canvas = Canvas(root, width = 1166, height = 787)  
    canvas.pack()  
    img = ImageTk.PhotoImage(Image.open(map_img_path)) 
    # Map basics: (longitude, latitude) (N/S, W/E)
    # Top Left Corner of Map: 
    # 30.298507512984692, -97.7550797158131
    # 
    # Bottom Right Corner of Map:
    # 30.280448469396532, -97.7242274875346 
    canvas.create_image(0, 0, anchor=NW, image=img) 
    root.mainloop() 
    return None


# Driver function for scripting
if __name__ == '__main__':
    main()
