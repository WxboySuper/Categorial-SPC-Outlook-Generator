# Severe Weather Outlook Display
# Created by WeatherboySuper under the WeatherTrackUS Group

'''Purpose of this program as of 3/18/2024 is to display the Severe Weather Outlook from the 
Storm Prediction Center (SPC) under the National Weather Service (NWS) in a graphically friendly way
for WeatherTrackUS and other users'''


# Import all necessary modules
import os
import requests
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import tkinter as tk 
import ttkbootstrap as ttk
import customtkinter as ctk
import contextily as ctx
import sys
import logging as log
import pystray
import feedparser
import time
import threading

# Import specific functions from modules
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from tkinter import TclError
from PIL import Image, ImageTk
from customtkinter import CTkImage
from plyer import notification

from CTkMessagebox import CTkMessagebox

matplotlib.use('TkAgg')

root = tk.Tk()
root.withdraw()

# Icons
tornado_icon = ctk.CTkImage(dark_image=Image.open('Tornado.png'), light_image=Image.open('Tornado.png'), size=(50,40))
home_icon = ctk.CTkImage(dark_image=Image.open('Home.png'), light_image=Image.open('Home.png'), size=(50,40))
lightning_icon = ctk.CTkImage(dark_image=Image.open('Lightning.png'), light_image=Image.open('Lightning.png'), size=(50,40))
logo_icon = ctk.CTkImage(dark_image=Image.open('My_project.png'), light_image=Image.open('My_project.png'), size=(120,120))

# Variables
log_directory = 'C:\\log'
current_directory = os.path.dirname(os.path.abspath(__file__))
instance = 0
rss_url = 'https://www.spc.noaa.gov/products/spcacrss.xml'
check_interval = 60
refresh_interval = 15 # Refresh the list every 15 seconds
notified_titles = [] # List to store notified titles
first_message_title = None # Title of the first message encountered

# Create a Tkinter root window
root = tk.Tk()
root.withdraw()

def check_rss_feed(url, interval, refresh_interval):
    last_refresh_time = time.time() # Time of the last refresh

    while True:
        current_time = time.time()
        if current_time - last_refresh_time >= refresh_interval:
            # Refresh the list every refresh_interval seconds
            last_refresh_time = current_time

        feed = feedparser.parse(url)
        if feed.entries:
            for entry in feed.entries:
                # Check if the message is new
                if entry.title not in notified_titles:
                    # Process the message here
                    # For example, send a notification
                    truncated_title = entry.title[:256]
                    log.info(f'RSS - New RSS Notification. {entry.title}')
                    notification.notify( # type: ignore
                        title="New RSS Feed Update",
                        message=(f'{truncated_title}. Check it out in the App!'),
                        timeout=10
                    )
                    # Add the title to the notified_titles list
                    notified_titles.append(entry.title)
        log.info(f'RSS - {notified_titles}')
        time.sleep(interval)
        log.info('RSS - Interval Passed')


# Set the global exception handler
def global_exception_handler(exc_type, exc_value, exc_traceback):
    log.error('uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(0)

sys.excepthook = global_exception_handler

### Fetch Functions ###
def fetch_cat_outlooks(day):
    log.info('Fetching a Categorial Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_cat.nolyr.geojson'
    elif day == 3:
        url = 'https://www.spc.noaa.gov/products/outlook/day3otlk_cat.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2023/day1otlk_20230331_1630_cat.lyr.geojson'
    else:
        log.error(f'Invalid Date. Day = {day}. Error on Line 75')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the Outlook

def fetch_tor_outlooks(day):
    log.info('Fetching a Tornado Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_torn.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_torn.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210317_1630_torn.lyr.geojson'
    else:
        log.error(f'Invalid Date. Day = {day}. Error on line 91')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the Outlook

def fetch_wind_outlooks(day):
    log.info('Fetching a Wind Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_wind.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_wind.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210325_1630_wind.lyr.geojson'
    else: 
        log.error(f'Invalid Date. Day = {day}. Error on line 107')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the outlook

def fetch_hail_outlooks(day):
    log.info('Fetching a Hail Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_hail.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_hail.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210526_1630_hail.lyr.geojson'
    else: 
        log.error(f'Invalid Date. Day = {day}. Error on line 123')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the outlook

def fetch_d48_outlooks(day):
    log.info(f'Fetching Day {day} outlook')
    if day == 4: 
        url = 'https://www.spc.noaa.gov/products/exper/day4-8/day4prob.lyr.geojson'
    elif day == 5:
        url = 'https://www.spc.noaa.gov/products/exper/day4-8/day5prob.lyr.geojson'
    elif day == 6:
        url = 'https://www.spc.noaa.gov/products/exper/day4-8/day6prob.lyr.geojson'
    elif day == 7:
        url = 'https://www.spc.noaa.gov/products/exper/day4-8/day7prob.lyr.geojson'
    elif day == 8:
        url = 'https://www.spc.noaa.gov/products/exper/day4-8/day8prob.lyr.geojson'
    else:
        log.error(f'Invalid Date. Day = {day}. Error on line 148')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the outlook

def fetch_prob_outlooks(day):
    log.info('Fetching a Probabilistic Outlook')
    if day == 3:
        url = 'https://www.spc.noaa.gov/products/outlook/day3otlk_prob.lyr.geojson'
    else: 
        log.error(f'Invalid Date. Day = {day}. Error on line 123')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the outlook

# Function to create the output directory
def create_output_directory(current_directory):
    log.info('running create_output_directory')
    output_directory = os.path.join(current_directory, 'output') # Creates a folder named "output"
    os.makedirs(output_directory, exist_ok=True)
    return output_directory # Returns where the output directory is

def setup_plot():
    log.info('running setup_plot')
    fig, ax = plt.subplots(figsize=(10,8)) # Set the size of the plot
    fig.patch.set_facecolor('black') # Set the background color of the plot
    ax.set_aspect('auto', adjustable='box')
    return fig, ax # Return the variables holding the data about the plot

# Function to set the limits of the plot
def set_plot_limits(ax):
    log.info('running set_plot_limits')
    ax.set_xlim([-125, -66]) # Base for x: (-125, -66)
    ax.set_ylim([20,60]) # Base for y: (23, 50)

# Function to remove all labels and axes
def remove_axes_labels_boxes_title(ax):
    log.info('running remove_axes_labels_boxes_title')
    # Remove the Axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Remove the Labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Remove the Box around the Plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Remove the Title
    plt.title('')
    
# Function to control the CONUS State Outlines  
def add_overlays(ax, current_directory, type):
    log.info('Adding all Overlays and Shapefiles')
    
    # State Outlines
    states_shapefile = os.path.join(current_directory, 's_11au16.shp') 
    states = gpd.read_file(states_shapefile)  
    states.plot(ax=ax, edgecolor='black', lw=0.75, alpha=0.75) # Remove facecolor (Added right below), and changed edgecolor to 'white' to contrast with the black 
    ax.set_facecolor("black") # Background of the CONUS Shapefile will be Black

    # Interstate Lines
    highways_shapefile = os.path.join(current_directory, 'USA_Freeway_System.shp')
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=0.6, alpha=0.75)

    # Header Image
    if type == 'cat':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_cat_header.png'))  
    elif type == 'tor':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_tor_header.png'))
    elif type == 'wind':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_wind_header.png'))
    elif type == 'hail':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_hail_header.png'))
    elif type == 'd4-8':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_d48_header.png'))
    elif type == 'prob':
        header_img = plt.imread(os.path.join(current_directory, 'wtus_prob_header.png'))
    else:
        log.error(f"There was an error getting the {type} header. Error on line 199.")
        popup('error', 'Header Error', 'An error has occured getting the header image. The program will now quit.')
        sys.exit(0)
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 0.95), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)

# Function to control the basemap
def add_basemap(ax):
    log.info('running add_basemap')
    ctx.add_basemap(ax, zoom=6, crs='EPSG:4326', source='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=63fe7729-f786-444d-8787-817db15f3368') # type: ignore
    log.info('basemap loaded')

# Function to check if there is a outlook to display
def check_outlook_availability(outlook_data):
    log.info('running check_outlook_availability')
    for feature in outlook_data['features']:
        # Check is there is a LABEL if there is coordinates in the geometry portion of the feature from the Source
        if 'coordinates' in feature['geometry']: 
            log.info('There is an outlook')
            return True
    return False

# Function to plot the polygons
def plot_outlook_polygons(ax, outlook_data, type):
    log.info('Plotting Outlook Polygons')
    if type == 'cat':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
            for polygon in outlook_polygon: # Find the properties of each polygon
                x, y = zip(*polygon[0])
                ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('cat', outlook_type)))
    elif type == 'tor':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('tor', outlook_type), edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('tor', outlook_type)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon: # Find the properties of each polygon
                    for polygon in multipolygon:
                        x, y = zip(*polygon[0])
                        if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('tor', outlook_type), edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('tor', outlook_type)))
    elif type == 'wind':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('wind', outlook_type), edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('wind', outlook_type)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon: # Find the properties of each polygon
                    for polygon in multipolygon:
                        x, y = zip(*polygon[0])
                        if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('wind', outlook_type), edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('wind', outlook_type)))
    elif type == 'hail':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('hail', outlook_type), edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('hail', outlook_type)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon: # Find the properties of each polygon
                    for polygon in multipolygon:
                        x, y = zip(*polygon[0])
                        if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('hail', outlook_type), edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('hail', outlook_type)))
    elif type == 'd4-8':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
            for polygon in outlook_polygon: # Find the properties of each polygon
                x, y = zip(*polygon[0])
                ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('d4-8', outlook_type)))
    elif type == 'prob':
        for feature in outlook_data['features']:
            outlook_type = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('prob', outlook_type), edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('prob', outlook_type)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon: # Find the properties of each polygon
                    for polygon in multipolygon:
                        x, y = zip(*polygon[0])
                        if outlook_type == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.2, ec='k', lw=1, fc=color('prob', outlook_type), edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=color('prob', outlook_type)))
    else:
        log.error(f"There was an error plotting the {type} outlook. Error on line 331.")
        popup('error', 'Plotting Error', 'An error has occured plotting the outlook. The program will now quit.')
        sys.exit(0)
    

# Function to display a popup and end the program if no outlook is available
def no_outlook_available():
    log.info('There is no outlook available')
    popup('warning', 'No Outlook', "There is no outlook available at this time")
    return # Ends Program

# Function to display the outlook
def display_cat_outlook(day, outlook_data):
    log.info('Displaying Categorial Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    if not check_outlook_availability(outlook_data):
        no_outlook_available()
        start_gui()

    add_overlays(ax, current_directory, 'cat')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'cat')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}cat_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

def display_tor_outlook(day, outlook_data):
    log.info('Displaying Tornado Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, current_directory, 'tor')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'tor')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}_tor_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

def display_wind_outlook(day, outlook_data):
    log.info('Displaying Wind Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, current_directory, 'wind')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'wind')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}_wind_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

def display_hail_outlook(day, outlook_data):
    log.info('Displaying Hail Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, current_directory, 'hail')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'hail')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}_hail_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

def display_d48_outlook(day, outlook_data):
    log.info('Displaying a Day 4-8 Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, current_directory, 'd4-8')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'd4-8')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

def display_prob_outlook(day, outlook_data):
    log.info('Displaying Probabilistic Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, current_directory, 'prob')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, outlook_data, 'prob')

    output_directory = create_output_directory(current_directory)
    output_filename = f'spc_day_{day}_prob_outlook.png'
    output_path = os.path.join(output_directory, output_filename)

    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas and add it to the root window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a custom toolbar with a close button
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    def close_figure():
        plt.close(fig)
        root.withdraw()
        start_gui()

    close_button = tk.Button(toolbar, text='Close', command=close_figure)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", close_figure)

    # Show the Tkinter root window with the canvas and toolbar
    root.deiconify()
    root.mainloop()

    log.info('Showing the plot')
    plt.savefig(output_path, dpi=96, bbox_inches='tight')

# Colors for Display
def color(type, outlook_type):
    log.info(f'Getting {outlook_type} for {type} outlook')
    if type == 'cat':
        colors = {
        'TSTM': 'lightgreen',
        'MRGL': 'green',
        'SLGT': 'yellow',
        'ENH': 'orange',
        'MDT': 'red',
        'HIGH': 'magenta'
        }
        return colors.get(outlook_type, 'blue') # Returns the Color, Blue if not found
    elif type == 'tor':
        colors = {
            '0.02': 'green',
            '0.05': 'brown',
            '0.10': 'yellow',
            '0.15': 'red',
            '0.30': 'pink',
            '0.45': 'purple',
            '0.60': 'blue',
            'sig': 'black'
        }
        return colors.get(outlook_type, 'blue') # Returns the color, Blue if not found
    elif type == 'wind' or type == 'hail' or type == 'prob':
        colors = {
            '0.05': 'saddlebrown',
            '0.15': 'gold',
            '0.30': 'red',
            '0.45': 'fuchsia',
            '0.60': 'blueviolet',
            'sig': 'black'
        }
        return colors.get(outlook_type, 'blue') # Returns the color, Blue if not found
    elif type == 'd4-8':
        colors = {
            '0.15': 'gold',
            '0.30': 'sandybrown'
        }
        return colors.get(outlook_type, 'blue') # Returns the color, blue if not found
    else:
        log.error(f"There was an error accessing colors. Error on line 533")
        popup('warning', 'Invalid Outlook Type', 'There was an error when trying to get colors. The program will now quit.')
        sys.exit(0)

# Displaying Popups
def popup(type, title, message):
    global question
    log.info(f'Showing a {type} popup titled {title} with the following message: {message}')
    if type == 'info':
        messagebox.showinfo(title, message)
    elif type == 'error':
        messagebox.showerror(title, message)
    elif type == 'warning':
        messagebox.showwarning(title, message)
    elif type == 'question':
        question = messagebox.askquestion(title, message)
        return question
    else:
        messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup. The program will now quit.')
        sys.exit(0)

# Start the GUI
def start_gui():
    global home_icon
    global lightning_icon
    global tornado_icon 

    # Initialize a window
    log.info('GUI - Initializing window')
    window = ctk.CTkToplevel()
    window.geometry('1700x900')
    window.title('Severe Weather Outlook Display')

    # Configure Layout
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(2, weight=1)

    # Fonts
    Title_Font = ctk.CTkFont(family='Montserrat', size=50, weight='bold')
    Description_Font = ctk.CTkFont(family='karla', size=21)

    # Frames
    sidebar_frame = ctk.CTkFrame(window, height=550, fg_color='#103157')
    sidebar_frame.grid(row=0, column=0, sticky='ns')

    main_frame = ctk.CTkFrame(window)
    main_frame.grid(row=0, column=1, columnspan=2, sticky='nsew')

    def side_bar():
        ## Sidebar Buttons ##
        # Logo
        logo_Button = ctk.CTkButton(sidebar_frame, text='', width=200, height=250, corner_radius=10, fg_color='transparent', 
                                    state='disabled', image=logo_icon, compound='top')
        logo_Button.grid(row=0, column=0, columnspan=1, padx=5, pady=10)
        
        # Home Button
        Home_Side_Button = ctk.CTkButton(sidebar_frame, text='Home', width=200, corner_radius=10, fg_color='transparent',
                                        font=('karla', 26), command=lambda: frame_change('home'),
                                        hover_color='#2191aa', image=home_icon, compound='top')
        Home_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

        # Day 1 Button
        D1_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 1',width=200, corner_radius=12, fg_color='transparent',
                                    font=('karla', 26), command=lambda: frame_change(1),
                                    hover_color='#2191aa', image=tornado_icon)
        D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

        # Day 2 Button
        D2_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 2',width=200, corner_radius=12, fg_color='transparent',
                                    font=('karla', 26), command=lambda: frame_change(2),
                                    hover_color='#2191aa', image=tornado_icon)
        D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

        # Day 3 Button
        D3_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 3',width=200, corner_radius=12, fg_color='transparent', 
                                    font=('karla', 26), command=lambda: frame_change(3),
                                    hover_color='#2191aa', image=lightning_icon)
        D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)

        # Day 4-8 Button
        D48_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 4-8',width=200, corner_radius=12, fg_color='transparent', 
                                        font=Description_Font, command=lambda: frame_change('d4-8'),
                                        hover_color='#2191aa', image=lightning_icon)
        D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)

        # Day Test Button
        Test_Side_Button = ctk.CTkButton(sidebar_frame, text='Test',width=200, height=50, font=Description_Font, command=lambda: frame_change('test'))
        #Test_Side_Button.grid(row=6, column=0, columnspan=1, padx=5, pady=10)

    risk_level_mapping_cat = {
        'TSTM': 1, # Thunderstorm
        'MRGL': 2, # Marginal
        'SLGT': 3, # Slight
        'ENH': 4,   # Enhanced
        'MDT': 5,   # Moderate
        'HIGH': 6   # High
    }

    risk_level_mapping_tor = {
        '0.02': 1,
        '0.05': 2,
        '0.10': 3,
        '0.15': 4,
        '0.30': 5,
        '0.45': 6,
        '0.60': 7
    }

    risk_level_mapping_prob = {
        '0.05': 1,
        '0.15': 2,
        '0.30': 3,
        '0.45': 4,
        '0.60': 5,
    }

    risk_level_mapping_d48 = {
        '0.15': 1,
        '0.30': 2
    }

    def determine_highest_risk_level_cat(outlook_data):
        highest_risk_level = 0
        for feature in outlook_data['features']:
            risk_level_label = feature['properties'].get('LABEL')
            if risk_level_label:
                risk_level = risk_level_mapping_cat.get(risk_level_label)
                if risk_level is not None and (highest_risk_level is None or risk_level > highest_risk_level):
                    highest_risk_level = risk_level
        if highest_risk_level == 0:
            highest_risk_level = 'None'
        elif highest_risk_level == 1:
            highest_risk_level = 'Thunderstorm'
        elif highest_risk_level == 2:
            highest_risk_level = 'Marginal'
        elif highest_risk_level == 3:
            highest_risk_level = 'Slight'
        elif highest_risk_level == 4:
            highest_risk_level = 'Enhanced'
        elif highest_risk_level == 5:
            highest_risk_level = 'Moderate'
        elif highest_risk_level == 6: 
            highest_risk_level = 'High'
        return highest_risk_level

    def determine_highest_risk_level_tor(outlook_data):
        highest_tor_risk_level = 0
        for feature in outlook_data['features']:
            tor_risk_level_label = feature['properties'].get('LABEL')
            if tor_risk_level_label:
                risk_level = risk_level_mapping_tor.get(tor_risk_level_label)
                if risk_level is not None and (highest_tor_risk_level is None or risk_level > highest_tor_risk_level):
                    highest_tor_risk_level = risk_level
        if highest_tor_risk_level == 0:
            highest_tor_risk_level = 'None'
        elif highest_tor_risk_level == 1:
            highest_tor_risk_level = '2%'
        elif highest_tor_risk_level == 2:
            highest_tor_risk_level = '5%'
        elif highest_tor_risk_level == 3:
            highest_tor_risk_level = '10%'
        elif highest_tor_risk_level == 4:
            highest_tor_risk_level = '15%'
        elif highest_tor_risk_level == 5:
            highest_tor_risk_level = '30%'
        elif highest_tor_risk_level == 6:
            highest_tor_risk_level = '45%'
        elif highest_tor_risk_level == 7: 
            highest_tor_risk_level = '60%'
        return highest_tor_risk_level

    def determine_highest_risk_level_wind(outlook_data):
        highest_wind_risk_level = 0
        for feature in outlook_data['features']:
            wind_risk_level_label = feature['properties'].get('LABEL')
            if wind_risk_level_label:
                risk_level = risk_level_mapping_prob.get(wind_risk_level_label)
                if risk_level is not None and (highest_wind_risk_level is None or risk_level > highest_wind_risk_level):
                    highest_wind_risk_level = risk_level
        if highest_wind_risk_level == 0:
            highest_wind_risk_level = 'None'
        elif highest_wind_risk_level == 1:
            highest_wind_risk_level = '5%'
        elif highest_wind_risk_level == 2:
            highest_wind_risk_level = '15%'
        elif highest_wind_risk_level == 3:
            highest_wind_risk_level = '30%'
        elif highest_wind_risk_level == 4:
            highest_wind_risk_level = '45%'
        elif highest_wind_risk_level == 5: 
            highest_wind_risk_level = '60%'
        return highest_wind_risk_level

    def determine_highest_risk_level_hail(outlook_data):
        highest_hail_risk_level = 0
        for feature in outlook_data['features']:
            hail_risk_level_label = feature['properties'].get('LABEL')
            if hail_risk_level_label:
                risk_level = risk_level_mapping_prob.get(hail_risk_level_label)
                if risk_level is not None and (highest_hail_risk_level is None or risk_level > highest_hail_risk_level):
                    highest_hail_risk_level = risk_level
        if highest_hail_risk_level == 0:
            highest_hail_risk_level = 'None'
        elif highest_hail_risk_level == 1:
            highest_hail_risk_level = '5%'
        elif highest_hail_risk_level == 2:
            highest_hail_risk_level = '15%'
        elif highest_hail_risk_level == 3:
            highest_hail_risk_level = '30%'
        elif highest_hail_risk_level == 4:
            highest_hail_risk_level = '45%'
        elif highest_hail_risk_level == 5: 
            highest_hail_risk_level = '60%'
        return highest_hail_risk_level

    def determine_highest_risk_level_prob(outlook_data):
        highest_prob_risk_level = 0
        for feature in outlook_data['features']:
            prob_risk_level_label = feature['properties'].get('LABEL')
            if prob_risk_level_label:
                risk_level = risk_level_mapping_prob.get(prob_risk_level_label)
                if risk_level is not None and (highest_prob_risk_level is None or risk_level > highest_prob_risk_level):
                    highest_prob_risk_level = risk_level
        if highest_prob_risk_level == 0:
            highest_prob_risk_level = 'None'
        elif highest_prob_risk_level == 1:
            highest_prob_risk_level = '5%'
        elif highest_prob_risk_level == 2:
            highest_prob_risk_level = '15%'
        elif highest_prob_risk_level == 3:
            highest_prob_risk_level = '30%'
        elif highest_prob_risk_level == 4:
            highest_prob_risk_level = '45%'
        elif highest_prob_risk_level == 1:
            highest_prob_risk_level = '60%'
        return highest_prob_risk_level

    def determine_highest_risk_level_d48(outlook_data):
        highest_d48_risk_level = 0
        for feature in outlook_data['features']:
            d48_risk_level_label = feature['properties'].get('LABEL')
            if d48_risk_level_label:
                risk_level = risk_level_mapping_d48.get(d48_risk_level_label)
                if risk_level is not None and (highest_d48_risk_level is None or risk_level > highest_d48_risk_level):
                    highest_d48_risk_level = risk_level
        if highest_d48_risk_level == 0:
            highest_d48_risk_level = 'None'
        elif highest_d48_risk_level == 1:
            highest_d48_risk_level = '15%'
        elif highest_d48_risk_level == 2:
            highest_d48_risk_level = '30%'
        return highest_d48_risk_level

    def frames(day):
        if day == 'home':
            side_bar()
            
            # Home Button
            Home_Side_Button = ctk.CTkButton(sidebar_frame, text='Home', width=200, corner_radius=10, fg_color='transparent',
                                     font=('karla', 26), command=lambda: frame_change('home'),
                                     state='disabled', image=home_icon, compound='top')
            Home_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.place(x=1285, y=15)

            # Hide Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.place(x=1075, y=15)

            # Title Label
            Title_Label = ctk.CTkLabel(main_frame, text='Severe Weather Outlook Display', 
                                       font=('Montserrat', 72, 'bold'), width=1200)
            Title_Label.place(x=150, y=350)

            # Welcome Label
            Welcome_Label = ctk.CTkLabel(main_frame, text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.', 
                                        font=('karla', 25))
            Welcome_Label.place(x=200, y=450)
        elif day == 1:
            outlook_data_cat_day_1 = fetch_cat_outlooks(1)
            highest_risk_level_cat_day_1 = determine_highest_risk_level_cat(outlook_data_cat_day_1)
            
            outlook_data_tor_day_1 = fetch_tor_outlooks(1)
            highest_risk_level_tor_day_1 = determine_highest_risk_level_tor(outlook_data_tor_day_1)

            outlook_data_wind_day_1 = fetch_wind_outlooks(1)
            highest_risk_level_wind_day_1 = determine_highest_risk_level_wind(outlook_data_wind_day_1)

            outlook_data_hail_day_1 = fetch_hail_outlooks(1)
            highest_risk_level_hail_day_1 = determine_highest_risk_level_hail(outlook_data_hail_day_1)

            side_bar()
            
            # Day 1 Button
            D1_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 1',width=200, corner_radius=12, fg_color='transparent',
                                   font=('karla', 26), command=lambda: frame_change(1),
                                   state='disabled', image=tornado_icon)
            D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.grid(row=1, column=3, padx=20, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 1 Heading Label
            D1_Label = ctk.CTkLabel(main_frame, text='Day 1 Outlooks', font=Title_Font)
            D1_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 1 Categorical Button
            D1_Cat_Button = ctk.CTkButton(main_frame, text='Day 1 Categorical', width=150, height=50, font=('karla', 28), command=lambda: button_run('cat', 1))
            D1_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Categorial Risk Label
            highest_risk_label_cat_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_1}', font=('karla', 25))
            highest_risk_label_cat_day_1.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 1 Tornado Button
            D1_Tor_Button = ctk.CTkButton(main_frame, text='Day 1 Tornado', width = 150, height=50, font=('karla', 28), command=lambda: button_run('tor', 1))
            D1_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Tornado Risk Label
            highest_risk_label_tor_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_1}', font=('karla', 25))
            highest_risk_label_tor_day_1.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 1 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(main_frame, text='Day 1 Wind', width=150, height=50, font=('karla', 28), command=lambda: button_run('wind', 1))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_1}', font=('karla', 25))
            highest_risk_label_wind_day_1.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 1 Hail Outlook
            D1_Hail_Button = ctk.CTkButton(main_frame, text='Day 1 Hail', width=150, height=50, font=('karla', 28), command=lambda: button_run('hail', 1))
            D1_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Hail Risk Label
            highest_risk_label_hail_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_1}', font=('karla', 25))
            highest_risk_label_hail_day_1.grid(row=6, column=2, columnspan=1, sticky='nsew')
        elif day == 2:
            outlook_data_cat_day_2 = fetch_cat_outlooks(2)
            highest_risk_level_cat_day_2 = determine_highest_risk_level_cat(outlook_data_cat_day_2)
            
            outlook_data_tor_day_2 = fetch_tor_outlooks(2)
            highest_risk_level_tor_day_2 = determine_highest_risk_level_tor(outlook_data_tor_day_2)

            outlook_data_wind_day_2 = fetch_wind_outlooks(2)
            highest_risk_level_wind_day_2 = determine_highest_risk_level_wind(outlook_data_wind_day_2)

            outlook_data_hail_day_2 = fetch_hail_outlooks(2)
            highest_risk_level_hail_day_2 = determine_highest_risk_level_hail(outlook_data_hail_day_2)

            side_bar()
            
            # Day 2 Button
            D2_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 2',width=200, corner_radius=12, fg_color='transparent',
                                   font=('karla', 26), command=lambda: frame_change(2),
                                   state='disabled', image=tornado_icon)
            D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 2 Heading Label
            D2_Label = ctk.CTkLabel(main_frame, text='Day 2 Outlooks', font=Title_Font)
            D2_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 2 Categorical Button
            D2_Cat_Button = ctk.CTkButton(main_frame, text='Day 2 Categorical', width=150, height=50, font=('karla', 28), command=lambda: button_run('cat', 2))
            D2_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Categorial Risk Label
            highest_risk_label_cat_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_2}', font=('karla', 25))
            highest_risk_label_cat_day_2.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 2 Tornado Button
            D2_Tor_Button = ctk.CTkButton(main_frame, text='Day 2 Tornado', width = 150, height=50, font=('karla', 28), command=lambda: button_run('tor', 2))
            D2_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Tornado Risk Label
            highest_risk_label_tor_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_2}', font=('karla', 25))
            highest_risk_label_tor_day_2.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 2 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(main_frame, text='Day 2 Wind', width=150, height=50, font=('karla', 28), command=lambda: button_run('wind', 2))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_2}', font=('karla', 25))
            highest_risk_label_wind_day_2.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 2 Hail Outlook
            D2_Hail_Button = ctk.CTkButton(main_frame, text='Day 2 Hail', width=150, height=50, font=('karla', 28), command=lambda: button_run('hail', 2))
            D2_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Hail Risk Label
            highest_risk_label_hail_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_2}', font=('karla', 25))
            highest_risk_label_hail_day_2.grid(row=6, column=2, columnspan=1, sticky='nsew')
        elif day == 3:
            outlook_data_cat_day_3 = fetch_cat_outlooks(3)
            highest_risk_level_cat_day_3 = determine_highest_risk_level_cat(outlook_data_cat_day_3)

            outlook_data_prob_day_3 = fetch_prob_outlooks(3)
            highest_risk_level_prob_day_3 = determine_highest_risk_level_prob(outlook_data_prob_day_3)
            
            side_bar()

            #Day 3 Button
            D3_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 3',width=200, corner_radius=12, fg_color='transparent', 
                                   font=('karla', 26), command=lambda: frame_change(3),
                                   state='disabled', image=lightning_icon)
            D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 3 Heading Label
            D3_Label = ctk.CTkLabel(main_frame, text='Day 3 Outlooks', font=Title_Font)
            D3_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 3 Categorical Button
            D3_Cat_Button = ctk.CTkButton(main_frame, text='Day 3 Categorical', width=150, height=50, font=('karla', 28), command=lambda: button_run('cat', 3))
            D3_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Categorial Risk Label
            highest_risk_label_cat_day_3 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_3}', font=('karla', 25))
            highest_risk_label_cat_day_3.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 3 Probabilistic Outlook
            D3_Prob_Button = ctk.CTkButton(main_frame, text='Day 3 Probabilistic', width=150, height=50, font=('karla', 28), command=lambda: button_run('prob', 3))
            D3_Prob_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Probabilistic Risk Label
            highest_risk_label_prob_day_3 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_prob_day_3}', font=('karla', 25))
            highest_risk_label_prob_day_3.grid(row=4, column=2, columnspan=1, sticky='nsew')
        elif day == 'd4-8':
            outlook_data_d48_day_4 = fetch_d48_outlooks(4)
            highest_risk_level_d48_day_4 = determine_highest_risk_level_d48(outlook_data_d48_day_4)
            
            outlook_data_d48_day_5 = fetch_d48_outlooks(5)
            highest_risk_level_d48_day_5 = determine_highest_risk_level_d48(outlook_data_d48_day_5)

            outlook_data_d48_day_6 = fetch_d48_outlooks(6)
            highest_risk_level_d48_day_6 = determine_highest_risk_level_d48(outlook_data_d48_day_6)

            outlook_data_d48_day_7 = fetch_d48_outlooks(7)
            highest_risk_level_d48_day_7 = determine_highest_risk_level_d48(outlook_data_d48_day_7)

            outlook_data_d48_day_8 = fetch_d48_outlooks(8)
            highest_risk_level_d48_day_8 = determine_highest_risk_level_d48(outlook_data_d48_day_8)

            side_bar()
            
            # Day 4-8 Button
            D48_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 4-8', width=200, corner_radius=12, fg_color='transparent', 
                                    font=Description_Font, command=lambda: frame_change('d4-8'),
                                    state='disabled', image=lightning_icon)
            D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 4-8 Heading Label
            D48_Label = ctk.CTkLabel(main_frame, text='Day 4-8 Outlooks', font=Title_Font)
            D48_Label.grid(row=2, column=1, columnspan=2, padx=400, pady=50, sticky='nsew')

            # Day 4 Button
            D4_Cat_Button = ctk.CTkButton(main_frame, text='Day 4 Outlook', font=('karla', 28), height=50, command=lambda: button_run('d4-8', 4))
            D4_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 4 Probabilistic Risk Label
            highest_risk_label_d48_day_4 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_4}', font=('karla', 25))
            highest_risk_label_d48_day_4.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 5 Button
            D5_Cat_Button = ctk.CTkButton(main_frame, text='Day 5 Outlook', font=('karla', 28), width=150, height=50, command=lambda: button_run('d4-8', 5))
            D5_Cat_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 5 Probabilistic Risk Label
            highest_risk_label_d48_day_5 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_5}', font=('karla', 25))
            highest_risk_label_d48_day_5.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 6 Button
            D6_Cat_Button = ctk.CTkButton(main_frame, text='Day 6 Outlook', font=('karla', 28), width=150, height=50, command=lambda: button_run('d4-8', 6))
            D6_Cat_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 6 Probabilistic Risk Label
            highest_risk_label_d48_day_6 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_6}', font=('karla', 25))
            highest_risk_label_d48_day_6.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 7 Button
            D7_Cat_Button = ctk.CTkButton(main_frame, text='Day 7 Outlook', font=('karla', 28), width=150, height=50, command=lambda: button_run('d4-8', 7))
            D7_Cat_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 7 Probabilistic Risk Label
            highest_risk_label_d48_day_7 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_7}', font=('karla', 25))
            highest_risk_label_d48_day_7.grid(row=6, column=2, columnspan=1, sticky='nsew')

            # Day 8 Button
            D8_Cat_Button = ctk.CTkButton(main_frame, text='Day 8 Outlook', font=('karla', 28), width=150, height=50, command=lambda: button_run('d4-8', 8))
            D8_Cat_Button.grid(row=7, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 8 Probabilistic Risk Label
            highest_risk_label_d48_day_8 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_8}', font=('karla', 25))
            highest_risk_label_d48_day_8.grid(row=7, column=2, columnspan=1, sticky='nsew')
        elif day == 'test':
            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font, command=close_program)
            Close_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font, command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Heading Label
            Test_Label = ctk.CTkLabel(main_frame, text='Outlook Tests', font=Title_Font)
            Test_Label.grid(row=2, column=1, columnspan=1, padx=450, pady=50, sticky='nsew')

            # Test Categorial Button
            Test_Button = ctk.CTkButton(main_frame, text='(Test) March 31st, 2023', width=300, font=Description_Font, command=lambda: button_run('cat', 'test'))
            Test_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')
        
            # Test Tornado Button
            Test_Tor_Button = ctk.CTkButton(main_frame, text='(Test) March 17th, 2021', width = 300, font=Description_Font, command=lambda: button_run('tor', 'test'))
            Test_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Test Wind Button
            Test_Wind_Button = ctk.CTkButton(main_frame, text='(Test) March 25th, 2021', width = 300, font=Description_Font, command=lambda: button_run('wind', 'test'))
            Test_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Test Hail Button
            Test_Hail_Button = ctk.CTkButton(main_frame, text='(Test) May 26th, 2021', width = 300, font=Description_Font, command=lambda: button_run('hail', 'test'))
            Test_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')
        else:
            log.error(f'Invalid Button. Day = {day}. Error on line 436')
            popup('error', 'Invalid Button', "An error has occured where the button isn't programmed correctly. The program will now quit.")
            sys.exit(0)
        
    def frame_change(day):
        for widget in main_frame.winfo_children():
            widget.destroy()
        
        frames(day)

    def button_run(type, day):
        log.info(f'GUI - {type} {day} button has been pressed. Running Day {day} {type} outlook')
        window.withdraw()
        run(type, day)

    def hide_to_system_tray():
        global icon
        window.withdraw()
        image = Image.open('My_project.png')
        menu = (pystray.MenuItem("Show", show_from_system_tray), pystray.MenuItem("Exit", close_program))
        icon = pystray.Icon("name", image, "My System Tray Icon", menu)
        icon.run()

    def close_program():
        global question # Declare question as a global variable
        log.info('GUI - Now Closing Program')
        popup('question', 
              'Close Program?', 
              'Are you sure you want to close the program? You will not receive notifications for new outlooks when the program is closed. Use "Hide" instead to hide the program and still receive new outlook notifications!')
        if question == 'yes':
            if 'icon' in globals() and icon is not None:
                icon.stop() 
            window.withdraw() 
            os._exit(0)
        else:
            return

    def show_from_system_tray(icon, item):
        icon.stop()
        window.deiconify()

    window.protocol("WM_DELETE_WINDOW", close_program)

    side_bar()
    frames('home')

    log.info('GUI - Created widgets')

    # Run the Window
    log.info('GUI - Running window')
    window.mainloop()

### Function to Run the Program ###
def run(type, day):
    global instance
    log.info(f'Running the Program under day {day}')
    if type == 'cat':
        outlook_data = fetch_cat_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_cat_outlook(day, outlook_data)
    elif type == 'tor':
        outlook_data = fetch_tor_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_tor_outlook(day, outlook_data)
    elif type == 'wind':
        outlook_data = fetch_wind_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_wind_outlook(day, outlook_data)
    elif type == 'hail':
        outlook_data = fetch_hail_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_hail_outlook(day, outlook_data)
    elif type == 'd4-8':
        outlook_data = fetch_d48_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_d48_outlook(day, outlook_data)
    elif type == 'prob':
        outlook_data = fetch_prob_outlooks(day)
        if not check_outlook_availability(outlook_data):
            no_outlook_available()
            start_gui()
        if instance == 0:
            popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
            instance = 1
        display_prob_outlook(day, outlook_data)
    else:
        log.error(f'Invalid Outlook Type. Outlook Type = {type}')
        popup('error', 'Invalid Outlook Type', "An error has occured where the outlook type wasn't read correctly. The program will now quit.")
        sys.exit(0)

# Startup Function
def startup():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log.basicConfig(
        level = log.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='C:\\log\\cod.log',
        filemode='w'
    )

    rss_feed_thread = threading.Thread(target=check_rss_feed, args=(rss_url, check_interval, refresh_interval))
    rss_feed_thread.daemon = True
    rss_feed_thread.start()

startup()
start_gui()