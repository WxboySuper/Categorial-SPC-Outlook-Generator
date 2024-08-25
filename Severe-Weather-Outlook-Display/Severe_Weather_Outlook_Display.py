# Severe Weather Outlook Display
# Created by WeatherboySuper under the WeatherTrackUS Group

"""
Purpose of this program as of 3/18/2024 is to display the Severe Weather Outlook from the
Storm Prediction Center (SPC) under the National Weather Service (NWS) in a graphically friendly way
for WeatherTrackUS and other users
"""

# skipcq: PYL-W1203
# skipcq: PYL-E501

# Import all necessary modules
import os
import requests
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import tkinter as tk
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
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from PIL import Image
from plyer import notification

matplotlib.use('TkAgg')

root = tk.Tk()
root.withdraw()

# Variables
log_directory = 'C:\\log'
current_directory = os.path.dirname(os.path.abspath(__file__))
instance = 0
rss_url = 'https://www.spc.noaa.gov/products/spcacrss.xml'
check_interval = 60
refresh_interval = 15  # Refresh the list every 15 seconds
notified_titles = []  # List to store notified titles
first_message_title = None  # Title of the first message encountered
question = None

# Icons
tornado_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_directory, '../files/icons/Tornado.png')),
                            light_image=Image.open(os.path.join(current_directory, '../files/icons/Tornado.png')), size=(50, 40))

home_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_directory, '../files/icons/Home.png')),
                         light_image=Image.open(os.path.join(current_directory, '../files/icons/Home.png')), size=(50, 40))

lightning_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_directory, '../files/icons/Lightning.png')),
                              light_image=Image.open(os.path.join(current_directory, '../files/icons/Lightning.png')), size=(50, 40))

logo_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_directory, '../files/icons/My_project.png')),
                         light_image=Image.open(os.path.join(current_directory, '../files/icons/My_project.png')), size=(120, 120))

# Create a Tkinter root window
root = tk.Tk()
root.withdraw()


def check_rss_feed(url, interval):
    """
    Checks the RSS feed at the specified URL for new entries and sends a notification for each new entry.

    Parameters:
        url (str): The URL of the RSS feed to check.
        interval (int): The interval in seconds to wait between checks.
        refresh_interval (int): The interval in seconds to refresh the list of notified titles.

    Returns:
        None
    """
    last_refresh_time = time.time()  # Time of the last refresh

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
                    log.info(f'RSS - New RSS Notification. {entry.title}')  # skipcq: PYL-W1203
                    notification.notify(  # type: ignore
                        title="New RSS Feed Update",
                        message=(f'{truncated_title}. Check it out in the App!'),
                        timeout=10
                    )
                    # Add the title to the notified_titles list
                    notified_titles.append(entry.title)
        log.info(f'RSS - {notified_titles}')  # skipcq: PYL-W1203
        time.sleep(interval)
        log.info('RSS - Interval Passed')


# Set the global exception handler
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Handles uncaught exceptions by logging the error and exiting the program.

    Parameters:
        exc_type (type): The type of the exception.
        exc_value (Exception): The instance of the exception.
        exc_traceback (traceback): The traceback object associated with the exception.

    Returns:
        None
    """
    log.error('uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(0)


sys.excepthook = global_exception_handler


def fetch_cat_outlooks(day):
    """
    Fetches the categorial outlook data for a specified day.

    Parameters:
        day (int or str): The day for which to fetch the outlook data. Can be 1, 2, 3, or 'test'.

    Returns:
        dict: The outlook data in JSON format.
    """
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
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 153')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)  # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the Outlook


def fetch_tor_outlooks(day):
    """
    Fetches the tornado outlook data for a specified day.

    Parameters:
        day (int or str): The day for which to fetch the outlook data. Can be 1, 2, or 'test'.

    Returns:
        dict: The outlook data in JSON format.

    Raises:
        requests.exceptions.RequestException: If the request to the GeoJSON URL fails.

    Exits the program with status code 0 if the specified day is invalid.
    """
    log.info('Fetching a Tornado Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_torn.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_torn.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210317_1630_torn.lyr.geojson'
    else:
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 185')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
    response = requests.get(url)  # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the Outlook


def fetch_wind_outlooks(day):
    """
    Fetches the wind outlook data for a specified day.

    Parameters:
        day (int or str): The day for which to fetch the outlook data. Can be 1, 2, or 'test'.

    Returns:
        dict: The outlook data in JSON format.
    """
    log.info('Fetching a Wind Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_wind.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_wind.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210325_1630_wind.lyr.geojson'
    else:
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 211')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)  # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the outlook


def fetch_hail_outlooks(day):
    """
    Fetches the hail outlook data for a specified day.

    Parameters:
        day (int or str): The day for which to fetch the outlook data. Can be 1, 2, or 'test'.

    Returns:
        dict: The outlook data in JSON format.

    Raises:
        requests.exceptions.RequestException: If the request to the GeoJSON URL fails.

    Exits the program with status code 0 if the specified day is invalid.
    """
    log.info('Fetching a Hail Outlook')
    if day == 1:
        url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_hail.nolyr.geojson'
    elif day == 2:
        url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_hail.nolyr.geojson'
    elif day == 'test':
        url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210526_1630_hail.lyr.geojson'
    else:
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 243')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the outlook


def fetch_d48_outlooks(day):
    """
    Fetches the 48 hour outlook data for a specified day.

    Parameters:
        day (int): The day for which to fetch the outlook data. Can be 4, 5, 6, 7, or 8.

    Returns:
        dict: The outlook data in JSON format.
    """
    log.info('Fetching Day ' + str(day) + ' outlook')
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
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 274')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the outlook


def fetch_prob_outlooks(day):
    """
    Fetches a probabilistic outlook for a given day.

    Parameters:
        day (int): The day for which to fetch the outlook.

    Returns:
        dict: The outlook data in JSON format.

    Raises:
        requests.exceptions.RequestException: If the request to the GeoJSON URL fails.

    Exits the program with status code 0 if the specified day is invalid.
    """
    log.info('Fetching a Probabilistic Outlook')
    if day == 3:
        url = 'https://www.spc.noaa.gov/products/outlook/day3otlk_prob.lyr.geojson'
    else:
        log.error('Invalid Date. Day = ' + str(day) + 'Error on line 302')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
        sys.exit(0)
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data  # Returns the data from the outlook


# Function to create the output directory
def create_output_directory():
    """
    Creates an output directory in the specified current directory.

    Parameters:
        current_directory (str): The path of the current directory.

    Returns:
        str: The path of the newly created output directory.
    """
    log.info('running create_output_directory')
    output_directory = os.path.join(current_directory, 'output')  # Creates a folder named "output"
    os.makedirs(output_directory, exist_ok=True)
    return output_directory  # Returns where the output directory is


def setup_plot():
    """
    Sets up a plot with a specified size and aspect ratio.

    Returns:
        fig (matplotlib.figure.Figure): The figure object.
        ax (matplotlib.axes.Axes): The axes object.
    """
    log.info('running setup_plot')
    fig, ax = plt.subplots(figsize=(10, 8))  # Set the size of the plot
    fig.set_facecolor('black')
    ax.set_aspect('auto', adjustable='box')
    return fig, ax  # Return the variables holding the data about the plot


# Function to set the limits of the plot
def set_plot_limits(ax):
    """
    Sets the x and y limits of a plot.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to set the limits for.

    Returns:
        None
    """
    log.info('running set_plot_limits')
    ax.set_xlim([-125, -66])  # Base for x: (-125, -66)
    ax.set_ylim([20, 60])  # Base for y: (23, 50)


# Function to remove all labels and axes
def remove_axes_labels_boxes_title(ax):
    """
    Removes axes, labels, boxes, and titles from a plot.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to modify.

    Returns:
        None
    """
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
def add_overlays(ax, outlook_type):
    """
    Adds overlays and shapefiles to a plot.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to add overlays to.
        current_directory (str): The path of the current directory.
        type (str): The type of header image to add.

    Returns:
        None
    """
    log.info('Adding all Overlays and Shapefiles')

    # State Outlines
    states_shapefile = os.path.join(current_directory, '../files/mapping/s_11au16.shp')
    states = gpd.read_file(states_shapefile)
    states.plot(ax=ax, edgecolor='black', lw=0.75, alpha=0.75)
    ax.set_facecolor("black")  # Background of the CONUS Shapefile will be Black

    # Interstate Lines
    highways_shapefile = os.path.join(current_directory, '../files/mapping/USA_Freeway_System.shp')
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=0.6, alpha=0.75)

    # Header Image
    if outlook_type == 'cat':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_cat_header.png'))
    elif outlook_type == 'tor':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_tor_header.png'))
    elif outlook_type == 'wind':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_wind_header.png'))
    elif outlook_type == 'hail':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_hail_header.png'))
    elif outlook_type == 'd4-8':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_d48_header.png'))
    elif outlook_type == 'prob':
        header_img = plt.imread(os.path.join(current_directory, '../files/overlays/wtus_prob_header.png'))
    else:
        log.error('Header Error. Outlook_type ' + outlook_type + 'Error on line 429')
        popup('error', 'Header Error', 'An error has occured getting the header image. The program will now quit.')
        sys.exit(0)
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 0.95), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)


# Function to control the basemap
def add_basemap(ax):
    """
    Adds a basemap to a plot.

    Parameters:
        ax (matplotlib.axes.Axes): The axes object to add the basemap to.

    Returns:
        None
    """
    log.info('running add_basemap')
    ctx.add_basemap(ax, zoom=6, crs='EPSG:4326', source='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=63fe7729-f786-444d-8787-817db15f3368')  # type: ignore  # skipcq: FLK-E501
    log.info('basemap loaded')


# Function to check if there is a outlook to display
def check_outlook_availability(outlook_data):
    """
    Checks if there is an available outlook in the given outlook data.

    Parameters:
        outlook_data (dict): The outlook data to check for availability.

    Returns:
        bool: True if an outlook is available, False otherwise.
    """
    log.info('running check_outlook_availability')
    for feature in outlook_data['features']:
        # Check is there is a LABEL if there is coordinates in the geometry portion of the feature from the Source
        if 'coordinates' in feature['geometry']:
            log.info('There is an outlook')
            return True
    return False


# Function to plot the polygons
def plot_outlook_polygons(ax, outlook_type, outlook_data):  # skipcq: PY-R1000
    """
    Plots outlook polygons on a given axis.

    Parameters:
        ax (matplotlib.axes.Axes): The axis to plot the outlook polygons on.
        outlook_type (str): The type of outlook to plot (e.g. 'cat', 'tor', 'wind', etc.).
        outlook_data (dict): A dictionary containing the outlook data, including features and geometry.

    Returns:
        None
    """
    log.info('Plotting Outlook Polygons')
    if outlook_type == 'cat':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
            for polygon in outlook_polygon:  # Find the properties of each polygon
                ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('cat', outlook_label)))
    elif outlook_type == 'tor':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon:  # Find the properties of each polygon
                    if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('tor', outlook_label),
                                                      edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('tor', outlook_label)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon:  # Find the properties of each polygon
                    for polygon in multipolygon:
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('tor', outlook_label),
                                                          edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('tor', outlook_label)))
    elif outlook_type == 'wind':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon:  # Find the properties of each polygon
                    if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('wind', outlook_label),
                                                      edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('wind', outlook_label)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon:  # Find the properties of each polygon
                    for polygon in multipolygon:
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('wind', outlook_label),
                                                          edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('wind', outlook_label)))
    elif outlook_type == 'hail':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon:  # Find the properties of each polygon
                    if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('hail', outlook_label),
                                                      edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('hail', outlook_label)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon:  # Find the properties of each polygon
                    for polygon in multipolygon:
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('hail', outlook_label),
                                                          edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('hail', outlook_label)))
    elif outlook_type == 'd4-8':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
            for polygon in outlook_polygon:  # Find the properties of each polygon
                ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('d4-8', outlook_label)))
    elif outlook_type == 'prob':
        for feature in outlook_data['features']:
            outlook_label = feature['properties']['LABEL']
            outlook_polygon = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon:  # Find the properties of each polygon
                    if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('prob', outlook_label),
                                                      edgecolor='black', hatch='x'))
                    else:
                        ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('prob', outlook_label)))
            elif feature['geometry']['type'] == 'MultiPolygon':
                outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for multipolygon in outlook_polygon:  # Find the properties of each polygon
                    for polygon in multipolygon:
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=color('prob', outlook_label),
                                                          edgecolor='black', hatch='x'))
                        else:
                            ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=color('prob', outlook_label)))
    else:
        log.error('Plotting Error. Outlook_Type' + outlook_type + 'error on line 598')
        popup('error', 'Plotting Error', 'An error has occured plotting the outlook. The program will now quit.')
        sys.exit(0)


# Function to display a popup and end the program if no outlook is available
def no_outlook_available():  # skipcq: PYL-R1711
    """
    Displays an error message when no severe weather outlook is available.

    Parameters:
        None

    Returns:
        None

    Logs:
        info: No outlook available
    """
    log.info('There is no outlook available')
    popup('warning', 'No Outlook', "There is no outlook available at this time")
    return  # skipcq: PYL-R1711


# Function to display the outlook
def display_cat_outlook(day, outlook_data):
    """
    Displays the categorical outlook for a given day.

    Parameters:
        day (int): The day for which to display the outlook.
        outlook_data (dict): The data containing the outlook information.

    Returns:
        None
    """
    log.info('Displaying Categorial Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    if not check_outlook_availability(outlook_data):
        no_outlook_available()
        start_gui()

    add_overlays(ax, 'cat')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'cat', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        Parameters:
            None

        Returns:
            None
        """
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
    """
    Displays a tornado outlook for a given day.

    Parameters:
        day (int): The day for which to display the tornado outlook.
        outlook_data (dict): The data containing the tornado outlook information.

    Returns:
        None
    """
    log.info('Displaying Tornado Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, 'tor')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'tor', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        Parameters:
            None

        Returns:
            None
        """
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
    """
    Displays a wind outlook for a given day.

    Parameters:
        day (int): The day for which to display the wind outlook.
        outlook_data (dict): The data containing the wind outlook information.

    Returns:
        None
    """
    log.info('Displaying Wind Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, 'wind')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'wind', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        Parameters:
            None

        Returns:
            None
        """
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
    """
    Displays a hail outlook for a given day.

    Parameters:
        day (int): The day for which to display the hail outlook.
        outlook_data (dict): The data containing the hail outlook information.

    Returns:
        None
    """
    log.info('Displaying Hail Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, 'hail')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'hail', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        Parameters:
            None

        Returns:
            None
        """
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
    """
    Displays a Day 4-8 outlook for a given day.

    Parameters:
        day (int): The day for which to display the Day 4-8 outlook.
        outlook_data (dict): The data containing the Day 4-8 outlook information.

    Returns:
        None
    """
    log.info('Displaying a Day 4-8 Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, 'd4-8')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'd4-8', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        This function closes the current figure using the `plt.close()` function.
        It then withdraws the root window using the `root.withdraw()` function.
        Finally, it starts the GUI by calling the `start_gui()` function.

        Parameters:
            None

        Returns:
            None
        """
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
    """
    Displays a probabilistic outlook for a given day.

    Parameters:
        day (int): The day for which to display the probabilistic outlook.
        outlook_data (dict): The data containing the probabilistic outlook information.

    Returns:
        None
    """
    log.info('Displaying Probabilistic Outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    add_overlays(ax, 'prob')
    set_plot_limits(ax)
    add_basemap(ax)
    remove_axes_labels_boxes_title(ax)

    plot_outlook_polygons(ax, 'prob', outlook_data)

    output_directory = create_output_directory()
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
        """
        Closes the current figure, withdraws the root window, and starts the GUI.

        Parameters:
            None

        Returns:
            None
        """
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
def color(outlook_type, outlook_level):
    # skipcq: FLK-W505
    """
    Returns the color associated with a given outlook type.

    Parameters:
        type (str): The type of outlook (e.g., 'cat', 'tor', 'wind', 'hail', 'prob', 'd4-8').
        outlook_type (str): The specific outlook type (e.g., 'TSTM', 'MRGL', 'SLGT', 'ENH', 'MDT', 'HIGH', '0.02', '0.05', '0.10', '0.15', '0.30', '0.45', '0.60', 'sig').  # skipcq: FLK-W505

    Returns:
        str: The color associated with the given outlook type, or 'blue' if not found.
    """
    log.info('Getting ' + outlook_level + ' for ' + outlook_type + ' outlook')
    if outlook_type == 'cat':
        colors = {
            'TSTM': 'lightgreen',
            'MRGL': 'green',
            'SLGT': 'yellow',
            'ENH': 'orange',
            'MDT': 'red',
            'HIGH': 'magenta'
        }
    if outlook_type == 'tor':
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
    if outlook_type in ('wind', 'hail', 'prob'):
        colors = {
            '0.05': 'saddlebrown',
            '0.15': 'gold',
            '0.30': 'red',
            '0.45': 'fuchsia',
            '0.60': 'blueviolet',
            'sig': 'black'
        }
    if outlook_type == 'd4-8':
        colors = {
            '0.15': 'gold',
            '0.30': 'sandybrown'
        }
    if outlook_type not in ('cat', 'tor', 'wind', 'hail', 'prob', 'd4-8'):
        log.error("There was an error accessing colors. Error on line 751")
        popup('warning', 'Invalid Outlook Type', 'There was an error when trying to get colors. The program will now quit.')
        sys.exit(0)

    return colors.get(outlook_level, 'blue')  # Returns the color, blue if not found


# Displaying Popups
def popup(popup_type, title, message):  # skipcq: PYL-R1710
    """
    The `popup` function displays different types of popups based on the input parameters such as
    info, error, warning, or question.

    :param type: The `type` parameter in the `popup` method specifies the type of popup to display.
    :param title: The `title` parameter in the `popup` function refers to the title of the popup
    window that will be displayed. It is the text that appears at the top of the popup window to
    provide context or information about the message being shown to the user.
    :param message: The `message` parameter in the `popup` function is the text that will be
    displayed in the popup dialog box. It is the information, error message, warning message, or
    question that you want to show to the user depending on the type of popup being displayed.
    :return: The `popup` method returns the value of `question` when the `type` parameter is
    set to 'question'.
    """
    log.info('Showing a ' + popup_type + ' popup titled ' + title + 'with the following message: ' + message)
    if popup_type == 'info':
        messagebox.showinfo(title, message)
    elif popup_type == 'error':
        messagebox.showerror(title, message)
    elif popup_type == 'warning':
        messagebox.showwarning(title, message)
    elif popup_type == 'question':
        global question  # skipcq: PYL-W0603
        question = messagebox.askquestion(title, message)
        return question  # skipcq: PYL-R1710
    else:
        messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup. The program will now quit.')
        sys.exit(0)


# Start the GUI
def start_gui():  # skipcq: PY-R1000
    """
    This function initializes and runs the graphical user interface (GUI) for the Severe Weather Outlook Display program.
    It creates the main window, sets up the layout, and defines the behavior for various buttons and events.
    The function does not take any parameters and does not return any values.
    """
    # Initialize a window
    log.info('GUI - Initializing window')
    window = ctk.CTkToplevel()
    window.geometry('1700x900+50+50')
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
        """
        Initializes the sidebar buttons for the GUI.

        Creates and configures the following buttons:
        - Logo Button: Displays the logo image and is disabled.
        - Home Button: Changes the frame to the home frame when clicked.
        - Day 1 Button: Changes the frame to the frame corresponding to day 1 when clicked.
        - Day 2 Button: Changes the frame to the frame corresponding to day 2 when clicked.
        - Day 3 Button: Changes the frame to the frame corresponding to day 3 when clicked.
        - Day 4-8 Button: Changes the frame to the frame corresponding to days 4-8 when clicked.

        Parameters:
            None

        Returns:
            None
        """
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
        D1_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 1', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: frame_change(1),
                                       hover_color='#2191aa', image=tornado_icon)
        D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

        # Day 2 Button
        D2_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 2', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: frame_change(2),
                                       hover_color='#2191aa', image=tornado_icon)
        D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

        # Day 3 Button
        D3_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 3', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: frame_change(3),
                                       hover_color='#2191aa', image=lightning_icon)
        D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)

        # Day 4-8 Button
        D48_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 4-8', width=200, corner_radius=12, fg_color='transparent',
                                        font=Description_Font, command=lambda: frame_change('d4-8'),
                                        hover_color='#2191aa', image=lightning_icon)
        D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)

    risk_level_mapping_cat = {
        'TSTM': 1,  # Thunderstorm
        'MRGL': 2,  # Marginal
        'SLGT': 3,  # Slight
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
        """
        Determines the highest risk level category from the given outlook data.

        Args:
            outlook_data (dict): A dictionary containing the outlook data with 'features' key.

        Returns:
            str: The highest risk level category, or 'None' if no risk level is found.
        """
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
        """
        Determines the highest risk level for tornadoes from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for tornadoes as a string, or 'None' if no risk level is found.
        """
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
        """
        Determines the highest wind risk level from the given outlook data.

        Args:
            outlook_data (dict): A dictionary containing the outlook data with 'features' key.

        Returns:
            str: The highest wind risk level category, or 'None' if no risk level is found.
        """
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
        """
        Determines the highest risk level for hail from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for hail as a string, or 'None' if no risk level is found.
        """
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
        """
        Determines the highest risk level for probability from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for probability as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        Determines the highest risk level for day 4-8 from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for day 4-8 as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        This function handles the frames for different days of the week. It takes a day parameter and
        based on that, it creates the corresponding frame with the required buttons and labels.

        Parameters:
        day (str or int): The day of the week. It can be 'home', 1, 2, 3, 'd4-8', or 'test'.

        Returns:
        None
        """
        if day == 'home':
            side_bar()

            # Home Button
            Home_Side_Button = ctk.CTkButton(sidebar_frame, text='Home', width=200, corner_radius=10,
                                             fg_color='transparent',
                                             font=('karla', 26), command=lambda: frame_change('home'),
                                             state='disabled', image=home_icon, compound='top')
            Home_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.place(x=1285, y=15)

            # Hide Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.place(x=1075, y=15)

            # Title Label
            Title_Label = ctk.CTkLabel(main_frame, text='Severe Weather Outlook Display',
                                       font=('Montserrat', 72, 'bold'), width=1200)
            Title_Label.place(x=150, y=350)

            # Welcome Label
            Welcome_Label = ctk.CTkLabel(main_frame,
                                         text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.',
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
            D1_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 1', width=200, corner_radius=12, fg_color='transparent',
                                           font=('karla', 26), command=lambda: frame_change(1),
                                           state='disabled', image=tornado_icon)
            D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.grid(row=1, column=3, padx=20, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 1 Heading Label
            D1_Label = ctk.CTkLabel(main_frame, text='Day 1 Outlooks', font=Title_Font)
            D1_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 1 Categorical Button
            D1_Cat_Button = ctk.CTkButton(main_frame, text='Day 1 Categorical', width=150, height=50, font=('karla', 28),
                                          command=lambda: button_run('cat', 1))
            D1_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Categorial Risk Label
            highest_risk_label_cat_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_1}',
                                                        font=('karla', 25))
            highest_risk_label_cat_day_1.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 1 Tornado Button
            D1_Tor_Button = ctk.CTkButton(main_frame, text='Day 1 Tornado', width=150, height=50, font=('karla', 28),
                                          command=lambda: button_run('tor', 1))
            D1_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Tornado Risk Label
            highest_risk_label_tor_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_1}',
                                                        font=('karla', 25))
            highest_risk_label_tor_day_1.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 1 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(main_frame, text='Day 1 Wind', width=150, height=50, font=('karla', 28),
                                           command=lambda: button_run('wind', 1))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_1}',
                                                         font=('karla', 25))
            highest_risk_label_wind_day_1.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 1 Hail Outlook
            D1_Hail_Button = ctk.CTkButton(main_frame, text='Day 1 Hail', width=150, height=50, font=('karla', 28),
                                           command=lambda: button_run('hail', 1))
            D1_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Hail Risk Label
            highest_risk_label_hail_day_1 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_1}',
                                                         font=('karla', 25))
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
            D2_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 2', width=200, corner_radius=12,
                                           fg_color='transparent',
                                           font=('karla', 26), command=lambda: frame_change(2),
                                           state='disabled', image=tornado_icon)
            D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 2 Heading Label
            D2_Label = ctk.CTkLabel(main_frame, text='Day 2 Outlooks', font=Title_Font)
            D2_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 2 Categorical Button
            D2_Cat_Button = ctk.CTkButton(main_frame, text='Day 2 Categorical', width=150, height=50, font=('karla', 28),
                                          command=lambda: button_run('cat', 2))
            D2_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Categorial Risk Label
            highest_risk_label_cat_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_2}',
                                                        font=('karla', 25))
            highest_risk_label_cat_day_2.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 2 Tornado Button
            D2_Tor_Button = ctk.CTkButton(main_frame, text='Day 2 Tornado', width=150, height=50, font=('karla', 28),
                                          command=lambda: button_run('tor', 2))
            D2_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Tornado Risk Label
            highest_risk_label_tor_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_2}',
                                                        font=('karla', 25))
            highest_risk_label_tor_day_2.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 2 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(main_frame, text='Day 2 Wind', width=150, height=50, font=('karla', 28),
                                           command=lambda: button_run('wind', 2))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_2}',
                                                         font=('karla', 25))
            highest_risk_label_wind_day_2.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 2 Hail Outlook
            D2_Hail_Button = ctk.CTkButton(main_frame, text='Day 2 Hail', width=150, height=50, font=('karla', 28),
                                           command=lambda: button_run('hail', 2))
            D2_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Hail Risk Label
            highest_risk_label_hail_day_2 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_2}',
                                                         font=('karla', 25))
            highest_risk_label_hail_day_2.grid(row=6, column=2, columnspan=1, sticky='nsew')
        elif day == 3:
            outlook_data_cat_day_3 = fetch_cat_outlooks(3)
            highest_risk_level_cat_day_3 = determine_highest_risk_level_cat(outlook_data_cat_day_3)

            outlook_data_prob_day_3 = fetch_prob_outlooks(3)
            highest_risk_level_prob_day_3 = determine_highest_risk_level_prob(outlook_data_prob_day_3)

            side_bar()

            # Day 3 Button
            D3_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 3', width=200, corner_radius=12,
                                           fg_color='transparent',
                                           font=('karla', 26), command=lambda: frame_change(3),
                                           state='disabled', image=lightning_icon)
            D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 3 Heading Label
            D3_Label = ctk.CTkLabel(main_frame, text='Day 3 Outlooks', font=Title_Font)
            D3_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 3 Categorical Button
            D3_Cat_Button = ctk.CTkButton(main_frame, text='Day 3 Categorical', width=150, height=50, font=('karla', 28),
                                          command=lambda: button_run('cat', 3))
            D3_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Categorial Risk Label
            highest_risk_label_cat_day_3 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_3}',
                                                        font=('karla', 25))
            highest_risk_label_cat_day_3.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 3 Probabilistic Outlook
            D3_Prob_Button = ctk.CTkButton(main_frame, text='Day 3 Probabilistic', width=150, height=50, font=('karla', 28),
                                           command=lambda: button_run('prob', 3))
            D3_Prob_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Probabilistic Risk Label
            highest_risk_label_prob_day_3 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_prob_day_3}',
                                                         font=('karla', 25))
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
            D48_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 4-8', width=200, corner_radius=12,
                                            fg_color='transparent',
                                            font=Description_Font, command=lambda: frame_change('d4-8'),
                                            state='disabled', image=lightning_icon)
            D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 4-8 Heading Label
            D48_Label = ctk.CTkLabel(main_frame, text='Day 4-8 Outlooks', font=Title_Font)
            D48_Label.grid(row=2, column=1, columnspan=2, padx=400, pady=50, sticky='nsew')

            # Day 4 Button
            D4_Cat_Button = ctk.CTkButton(main_frame, text='Day 4 Outlook', font=('karla', 28),
                                          height=50, command=lambda: button_run('d4-8', 4))
            D4_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 4 Probabilistic Risk Label
            highest_risk_label_d48_day_4 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_4}',
                                                        font=('karla', 25))
            highest_risk_label_d48_day_4.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 5 Button
            D5_Cat_Button = ctk.CTkButton(main_frame, text='Day 5 Outlook', font=('karla', 28),
                                          width=150, height=50, command=lambda: button_run('d4-8', 5))
            D5_Cat_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 5 Probabilistic Risk Label
            highest_risk_label_d48_day_5 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_5}',
                                                        font=('karla', 25))
            highest_risk_label_d48_day_5.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 6 Button
            D6_Cat_Button = ctk.CTkButton(main_frame, text='Day 6 Outlook', font=('karla', 28),
                                          width=150, height=50, command=lambda: button_run('d4-8', 6))
            D6_Cat_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 6 Probabilistic Risk Label
            highest_risk_label_d48_day_6 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_6}',
                                                        font=('karla', 25))
            highest_risk_label_d48_day_6.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 7 Button
            D7_Cat_Button = ctk.CTkButton(main_frame, text='Day 7 Outlook', font=('karla', 28),
                                          width=150, height=50, command=lambda: button_run('d4-8', 7))
            D7_Cat_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 7 Probabilistic Risk Label
            highest_risk_label_d48_day_7 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_7}',
                                                        font=('karla', 25))
            highest_risk_label_d48_day_7.grid(row=6, column=2, columnspan=1, sticky='nsew')

            # Day 8 Button
            D8_Cat_Button = ctk.CTkButton(main_frame, text='Day 8 Outlook', font=('karla', 28),
                                          width=150, height=50, command=lambda: button_run('d4-8', 8))
            D8_Cat_Button.grid(row=7, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 8 Probabilistic Risk Label
            highest_risk_label_d48_day_8 = ctk.CTkLabel(main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_8}',
                                                        font=('karla', 25))
            highest_risk_label_d48_day_8.grid(row=7, column=2, columnspan=1, sticky='nsew')
        elif day == 'test':
            # Close Button
            Close_Button = ctk.CTkButton(main_frame, text='Close', width=200, font=Description_Font,
                                         command=close_program)
            Close_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(main_frame, text='Hide', width=200, font=Description_Font,
                                        command=hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Heading Label
            Test_Label = ctk.CTkLabel(main_frame, text='Outlook Tests', font=Title_Font)
            Test_Label.grid(row=2, column=1, columnspan=1, padx=450, pady=50, sticky='nsew')

            # Test Categorial Button
            Test_Button = ctk.CTkButton(main_frame, text='(Test) March 31st, 2023', width=300,
                                        font=Description_Font, command=lambda: button_run('cat', 'test'))
            Test_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Test Tornado Button
            Test_Tor_Button = ctk.CTkButton(main_frame, text='(Test) March 17th, 2021', width=300,
                                            font=Description_Font, command=lambda: button_run('tor', 'test'))
            Test_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Test Wind Button
            Test_Wind_Button = ctk.CTkButton(main_frame, text='(Test) March 25th, 2021', width=300,
                                             font=Description_Font, command=lambda: button_run('wind', 'test'))
            Test_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Test Hail Button
            Test_Hail_Button = ctk.CTkButton(main_frame, text='(Test) May 26th, 2021', width=300,
                                             font=Description_Font, command=lambda: button_run('hail', 'test'))
            Test_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')
        else:
            log.error('Invalid Button. Day = ' + str(day) + 'Error on line 1798')
            popup('error', 'Invalid Button', "An error has occured where the button isn't programmed correctly. The program will now quit.")
            sys.exit(0)

    def frame_change(day):  # skipcq: PTC-W0065
        """
        This function changes the frame of the GUI based on the provided day.

        It destroys all the widgets in the main frame and then calls the frames function to recreate the frame for the specified day.

        Parameters:
            day (int): The day for which the frame needs to be changed.

        Returns:
            None
        """
        for widget in main_frame.winfo_children():
            widget.destroy()

        frames(day)

    def button_run(outlook_type, day):  # skipcq: PTC-W0065
        """
        Handles the button press event for running a specific outlook type for a given day.

        Parameters:
            type (str): The type of outlook to be run.
            day (int): The day for which the outlook needs to be run.

        Returns:
            None
        """
        log.info('GUI - ' + outlook_type + str(day) + ' button has been pressed.')
        window.withdraw()
        run(outlook_type, day, window, instance)

    def hide_to_system_tray():  # skipcq: PTC-W0065
        """
        Hides the application window to the system tray.

        Parameters:
            None

        Returns:
            None
        """
        window.withdraw()
        image = Image.open('My_project.png')
        menu = (pystray.MenuItem("Show", show_from_system_tray),
                pystray.MenuItem("Exit", close_program))
        global logo_icon_tray  # skipcq: PYL-W0601
        logo_icon_tray = pystray.Icon("name", image, "My System Tray Icon", menu)
        logo_icon_tray.run()

    def close_program():
        """
        Closes the program after prompting the user for confirmation.

        This function displays a popup asking the user if they want to close the program.
        If the user responds with 'yes', it stops the system tray icon, withdraws the main window, and exits the program.

        Parameters:
            None

        Returns:
            None
        """
        log.info('GUI - Now Closing Program')
        popup('question',
              'Close Program?',
              'Are you sure you want to close the program? You will not receive notifications for new outlooks when the program is closed. Use "Hide" instead to hide the program and still receive new outlook notifications!')  # skipcq: FLK-E501
        if question == 'yes':
            if 'icon' in globals() and logo_icon_tray is not None:
                logo_icon_tray.stop()
            window.withdraw()
            os._exit(0)
        else:
            return

<<<<<<< HEAD
=======

>>>>>>> 587d733f5bac8c930e931dd01cd7e2a1ad106b6a
    def show_from_system_tray(logo_icon_tray_1, item):  # skipcq: PYL-W0613  # skipcq: PTC-W0065
        """
        Shows the application window from the system tray.

        Parameters:
            icon: The system tray icon object.
            item: The item that triggered this function call.

        Returns:
            None
        """
        logo_icon_tray_1.stop()
        window.deiconify()

    window.protocol("WM_DELETE_WINDOW", close_program)

    side_bar()
    frames('home')

    log.info('GUI - Created widgets')

    # Run the Window
    log.info('GUI - Running window')
    window.mainloop()


# Function to Run the Program
def run(outlook_type, day, window, instance_run):
    """
    Runs the severe weather outlook program for a specified outlook type and day.

    This function logs the start of the program, fetches the outlook data, checks its availability,
    and displays it on the map if available. If the outlook data is not available, it displays a
    warning message. It also checks if the outlook type is valid and exits the program if it's not.

    Parameters:
        outlook_type (str): The type of severe weather outlook (e.g., 'cat', 'tor', 'wind', etc.).
        day (int): The day of the outlook (e.g., 1, 2, 3, etc.).
        window: The GUI window object.

    Returns:
        None
    """
    log.info('Running outlook' + outlook_type + 'day' + str(day))

    outlook_functions = {
        'cat': fetch_cat_outlooks,
        'tor': fetch_tor_outlooks,
        'wind': fetch_wind_outlooks,
        'hail': fetch_hail_outlooks,
        'd4-8': fetch_d48_outlooks,
        'prob': fetch_prob_outlooks
    }

    fetch_function = outlook_functions.get(outlook_type)
    if fetch_function is None:
        log.error('Invalid Outlook Type. Outlook Type = ' + outlook_type)
        popup('error', 'Invalid Outlook Type', "An error has occurred where the outlook type wasn't read correctly. The program will now quit.")
        sys.exit(0)

    outlook_data = fetch_function(day)

    if check_outlook_availability(outlook_data):
        if instance_run == 0:
            popup('info', 'Program is Running',
                  'The Severe Weather Outlook Display is now running. The program may take some time to load so be patient. Click "Ok" or Close the Window to Continue')  # skipcq: FLK-E501
            instance_run = 1

        window.withdraw()
        display_function = getattr(sys.modules[__name__], f'display_{outlook_type}_outlook')
        display_function(day, outlook_data)
    else:
        popup('warning', 'No Outlook Available', f'There is no {outlook_type} outlook available for day {day}.')
        start_gui()

    if outlook_type not in ['cat', 'tor', 'wind', 'hail', 'd4-8', 'prob']:
        log.error('Invalid Outlook Type. Outlook Type = ' + outlook_type)
        popup('error', 'Invalid Outlook Type',
              "An error has occurred where the outlook type wasn't read correctly. The program will now quit.")
        sys.exit(0)


# Startup Function
def startup():
    """
    Initializes the application by setting up the log directory and starting the RSS feed monitoring thread.

    Parameters:
        None

    Returns:
        None
    """
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log.basicConfig(
        level=log.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='C:\\log\\cod.log',
        filemode='w'
    )

    rss_feed_thread = threading.Thread(target=check_rss_feed,
                                       args=(rss_url, check_interval))
    rss_feed_thread.daemon = True
    rss_feed_thread.start()


startup()
start_gui()
