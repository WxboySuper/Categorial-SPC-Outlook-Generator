import os
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import tkinter as tk # New Module: Handles the GUI Popup

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Function to create the output directory
def create_output_directory():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(current_directory, 'output')
    os.makedirs(output_directory, exist_ok=True)
    return output_directory

# Function to fetch the SPC outlook from the GeoJSON URL
def fetch_spc_outlook():
    url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data

# Function to display the SPC outlook
def display_spc_outlook(outlook_data):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Set the background
    fig.patch.set_facecolor('black')

    outlook_available = False #NEW: Variable to track if the outlook is available

    # Plotting the outlook
    for feature in outlook_data['features']:
        if 'LABEL' in feature['properties']: #NEW: Check is there is a LABEL from the Source
            outlook_type = feature['properties']['LABEL']
            if 'geometry' in feature and 'coordinates' in feature['geometry']: #NEW: Check if there is coordinates in the geometry portion of the feature from the source
                outlook_available = True #NEW: Make the outlook_available variable true because there is a outlook
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'polygon':
                    outlook_polygon = [outlook_polygon] #Convert single polygon to a list for consistancy
                for polygon in outlook_polygon:
                    x = []
                    y = []
                    for point in polygon[0]:
                        x.append(point[0])
                        y.append(point[1])
                    ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ex='k', lw=1, fc=get_outlook_color(outlook_type)))
            else:
                outlook_available = False #NEW: Make the outlook_available variable false because there is no outlook
        else:
            outlook_available = False #NEW: Make the outlook_available variable false because there is no outlook
        
        if not outlook_available: #NEW: show a popup is a outlook is not available
            show_popup("There is no outlook available at this time") #NEW: Popup message to be shown
            return #NEW: Exit the function if a outlook is not available

    # Overlay US state outlines
    current_directory = os.path.dirname(os.path.abspath(__file__))
    states_shapefile = os.path.join(current_directory, 's_11au16.shp')  
    states = gpd.read_file(states_shapefile)  
    states.plot(ax=ax, edgecolor='white', lw=0.5) #CHANGED: Remove facecolor (Added right below), and changed edgecolor to 'white' to contrast with the black 
    ax.set_facecolor("black") #NEW: Background of the CONUS Shapefile will be Black

    # Read and plot the U.S. interstate highways shapefile
    highways_shapefile = os.path.join(current_directory, 'USA_Freeway_System.shp')
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=0.6)

    # Remove latitude and longitude axes labels and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Set the x and y limits for CONUS
    # Base x & y: x (-125, -66) y (23, 50)
    ax.set_xlim([-125, -66])
    ax.set_ylim([23, 50])

    # Remove the box around the plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Remove the title
    plt.title('')

    # Add the header image
    header_img = plt.imread(os.path.join(current_directory, 'WTUS_SPC_Banner_nobg.png'))
    #header_img = plt.imread(os.path.join(current_directory, 'SPC_Outlook-full.png'))  
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 1.1), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)

    # Save the plot as an image
    output_directory = create_output_directory()
    output_filename = 'spc_cat_outlook.png'
    output_path = os.path.join(output_directory, output_filename)
    plt.savefig(output_path, dpi=500, bbox_inches='tight')

    # Show the plot
    plt.show()

#NEW: Function to display the popup message
def show_popup(message):
    root = tk.Tk()
    root.withdraw() #NEW: Hide the root window
    tk.messagebox.showinfo("No Outlook", message) #NEW: Display the Popup Message

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

# Function to fetch the SPC outlook and display it
def fetch_and_display_spc_outlook():
    outlook = fetch_spc_outlook()
    display_spc_outlook(outlook)

fetch_and_display_spc_outlook()
