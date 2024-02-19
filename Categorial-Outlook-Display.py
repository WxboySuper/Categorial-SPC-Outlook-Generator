# Import all necessary modules
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import tkinter as tk # Handles the GUI Popup
import contextily as ctx

# Import specific functions from modules
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from tkinter import messagebox

# Set up important program wide variables
current_directory = os.path.dirname(os.path.abspath(__file__))


### Functions to Set Up the Program ###

# Function to create the output directory
def create_output_directory(current_directory):
    output_directory = os.path.join(current_directory, 'output') # Creates a folder named "output"
    os.makedirs(output_directory, exist_ok=True)
    return output_directory # Returns where the output directory is

# Function to fetch the SPC outlook from the GeoJSON URL
def fetch_spc_outlook():
    url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the GeoJSON URL

def setup_plot():
    fig, ax = plt.subplots(figsize=(10,8)) # Set the size of the plot
    fig.patch.set_facecolor('black') # Set the background color of the plot
    ax.set_aspect('equal', adjustable='box')
    return fig, ax # Return the variables holding the data about the plot

# Function to set the limits of the plot
def set_plot_limits(ax):
    ax.set_xlim([-125, -66]) # Base for x: (-125, -66)
    ax.set_ylim([20, 50]) # Base for y: (23, 50)

# Function to remove all labels and axes
def remove_axes_labels_boxes_title(ax):
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


### Functions controlling the overlays and header ###
    
# Function to control the CONUS State Outlines
def overlay_us_state_outline(ax, current_directory):
    states_shapefile = os.path.join(current_directory, 's_11au16.shp')  
    states = gpd.read_file(states_shapefile)  
    states.plot(ax=ax, edgecolor='black', lw=0.75, alpha=0.75) # Remove facecolor (Added right below), and changed edgecolor to 'white' to contrast with the black 
    ax.set_facecolor("black") # Background of the CONUS Shapefile will be Black

# Function to control the US Interstate Lines
def overlay_us_interstate_lines(ax, current_directory):
    highways_shapefile = os.path.join(current_directory, 'USA_Freeway_System.shp')
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=0.6, alpha=0.75)

# Function to control the basemap
def add_basemap(ax):
    ctx.add_basemap(ax, zoom=6, crs='EPSG:4326', source='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=63fe7729-f786-444d-8787-817db15f3368') # type: ignore

# Function to control the header
def add_header_image(ax, current_directory):
    header_img = plt.imread(os.path.join(current_directory, 'WTUS_SPC_Banner_nobg.png'))  
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 1.1), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)


### Functions to handle the outlook ###

# Function to check if there is a outlook to display
def check_outlook_availability(outlook_data):
    for feature in outlook_data['features']:
        # Check is there is a LABEL if there is coordinates in the geometry portion of the feature from the Source
        if 'LABEL' in feature['properties'] and 'geometry' in feature and 'coordinates' in feature ['geometry']: 
            return True
    return False

# Function to plot the polygons
def plot_outlook_polygons(ax, outlook_data):
    for feature in outlook_data['features']: 
        outlook_type = feature['properties']['LABEL']
        outlook_polygon = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Polygon':
            outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
        for polygon in outlook_polygon: # Find the properties of each polygon
            x, y = zip(*polygon[0])
            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=get_outlook_color(outlook_type))) 

# Function to display a popup and end the program if no outlook is available
def no_outlook_available():
    show_popup('No Outlook', "There is no outlook available at this time")
    return # Ends Program


### Functions to Plot and Save the Outlook Image

# Functino to save and show the figure
def save_and_show_plot(fix, ax, output_path):
    plt.savefig(output_path, dpi=96, bbox_inches='tight')
    plt.show()

# Function to display the outlook
def display_outlook(current_directory, outlook_data):
    fig, ax = setup_plot()

    overlay_us_state_outline(ax, current_directory)
    overlay_us_interstate_lines(ax, current_directory)
    set_plot_limits(ax)
    add_basemap(ax)

    remove_axes_labels_boxes_title(ax)
    add_header_image(ax, current_directory)

    if not check_outlook_availability(outlook_data):
        no_outlook_available()
        return

    plot_outlook_polygons(ax, outlook_data)

    output_directory = create_output_directory(current_directory)
    output_filename = 'spc_cat_outlook.png'
    output_path = os.path.join(output_directory, output_filename)
    
    save_and_show_plot(fig, ax, output_path)


### Other Functions ###

# Function to display the popup message
def show_popup(title, message):
    root = tk.Tk()
    root.withdraw() # Hide the root window
    messagebox.showinfo(title, message) # Display the Popup Message

# Function to determine the color for each outlook category
def get_outlook_color(outlook_type):
    colors = {
        'TSTM': 'lightgreen',
        'MRGL': 'green',
        'SLGT': 'yellow',
        'ENH': 'orange',
        'MDT': 'red',
        'HIGH': 'magenta'
    }
    return colors.get(outlook_type, 'blue')  # Default to white color for unknown types


### Function to Run the Program ###
def run_program():
    show_popup('Program is Running', "Program is now running and may take some time to run. Click 'OK' or Close to Continue")
    outlook_data = fetch_spc_outlook()
    display_outlook(current_directory, outlook_data)

run_program()