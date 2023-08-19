import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import geopandas as gpd

# Function to fetch the SPC outlook from the GeoJSON URL

# DO NOT TOUCH
def fetch_spc_outlook():
    url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data

# Function to display the SPC outlook

# DO NOT TOUCH
def display_spc_outlook(outlook_data):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set the background
    #fig.patch.set_facecolor('lightblue')

    # Plotting the outlook polygons
    for feature in outlook_data['features']:
        outlook_type = feature['properties']['LABEL']
        outlook_polygon = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Polygon':
            outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
        for polygon in outlook_polygon:
            x = []
            y = []
            for point in polygon[0]:
                x.append(point[0])
                y.append(point[1])
            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=get_outlook_color(outlook_type)))

    # Overlay US state outlines
    
    ### ENTER STATE OUTLINE FILE DIRECTORY BELOW (Use / and not \) ###
    states = gpd.read_file('') 
    states.plot(ax=ax, facecolor='none', edgecolor='black', lw=0.5)

    # Read and plot the U.S. interstate highways shapefile

    ### ENTER HIGHWAY SHAPEFILE BELOW (Use / and not \) ###
    highways_shapefile = ''
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=1)

    # Remove latitude and longitude axes labels and ticks

    # DO NOT TOUCH
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Set the x and y limits for CONUS
    # Base x & y: x (-125, -66) y (23, 50)

    # Use the X and Y limits to create custom views
    ax.set_xlim([-125, -66])
    ax.set_ylim([24, 50])

    # Remove the box around the plot
    
    # NO NOT TOUCH
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Remove the title

    # Code to change title, leave blank for no title
    plt.title('')

    # Add the header image
    ### ENTER HEADER FILE LOCATION BELOW (Use / and not \) ###

    header_img = plt.imread('')  
    header_img = OffsetImage(header_img, zoom=0.25)
    ab = AnnotationBbox(header_img, (0.265, 1.1), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)

    # Save the plot as an image
    ### ENTER FILE PATH BELOW (Use / and not \) ###

    output_directory = ''
    output_filename = 'spc_outlook.png'
    output_path = output_directory + output_filename
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    # Show the plot
    plt.show()

# Function to determine the color for each outlook category
# Use this to determine colors
def get_outlook_color(outlook_type):
    colors = {
        'TSTM': 'lightgreen',
        'MRGL': 'green',
        'SLGT': 'yellow',
        'ENH': 'orange',
        'MDT': 'red',
        'HIGH': 'pink'
    }
    return colors.get(outlook_type, 'blue')  # Default to white color for unknown types

# Function to fetch the SPC outlook and display it
# DO NOT TOUCH
def fetch_and_display_spc_outlook():
    outlook = fetch_spc_outlook()
    display_spc_outlook(outlook)

fetch_and_display_spc_outlook()