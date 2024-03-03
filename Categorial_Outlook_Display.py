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

# Import specific functions from modules
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from tkinter import TclError

matplotlib.use('TkAgg')

# Set up important program wide variables
current_directory = os.path.dirname(os.path.abspath(__file__))

# Set up log directory
log_directory = 'C:\\log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Set up logging
log.basicConfig(
    level=log.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='C:\\log\\cod.log',
    filemode='w'
)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    log.error('uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

# Set the global exception handler
sys.excepthook = global_exception_handler

# Create a Tkinter root window
root = tk.Tk()
root.withdraw()


### Fetch Functions ###

def fetch_test_cat_outlook():
    log.info('running fetch_test_cat_outlook function (March 31st, 2023)')
    url = 'https://www.spc.noaa.gov/products/outlook/archive/2023/day1otlk_20230331_1630_cat.lyr.geojson'
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the GeoJSON URL

# Day 1 Categorial
def fetch_d1_cat_outlook():
    log.info('running fetch_d1_cat_outlook function')
    url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the GeoJSON URL

# Day 2 Categorial
def fetch_d2_cat_outlook():
    log.info('Fetching D2 Cat Outlook')
    url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_cat.nolyr.geojson'
    response = requests.get(url)
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data


### Functions to Set Up the Program ###

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
    ax.set_aspect('equal', adjustable='box')
    return fig, ax # Return the variables holding the data about the plot

# Function to set the limits of the plot
def set_plot_limits(ax):
    log.info('running set_plot_limits')
    ax.set_xlim([-125, -66]) # Base for x: (-125, -66)
    ax.set_ylim([20, 50]) # Base for y: (23, 50)

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


### Functions controlling the overlays and header ###
    
# Function to control the CONUS State Outlines
def overlay_us_state_outline(ax, current_directory):
    log.info('running overlay_us_state_outline')
    states_shapefile = os.path.join(current_directory, 's_11au16.shp')  
    states = gpd.read_file(states_shapefile)  
    states.plot(ax=ax, edgecolor='black', lw=0.75, alpha=0.75) # Remove facecolor (Added right below), and changed edgecolor to 'white' to contrast with the black 
    ax.set_facecolor("black") # Background of the CONUS Shapefile will be Black

# Function to control the US Interstate Lines
def overlay_us_interstate_lines(ax, current_directory):
    log.info('running overlay_us_interstate_lines')
    highways_shapefile = os.path.join(current_directory, 'USA_Freeway_System.shp')
    highways_gdf = gpd.read_file(highways_shapefile)
    highways_gdf.plot(ax=ax, color='red', linewidth=0.6, alpha=0.75)

# Function to control the basemap
def add_basemap(ax):
    log.info('running add_basemap')
    ctx.add_basemap(ax, zoom=6, crs='EPSG:4326', source='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=63fe7729-f786-444d-8787-817db15f3368') # type: ignore
    log.info('basemap loaded')

# Function to control the header
def add_header_image(ax, current_directory):
    log.info('running add_header_image')
    header_img = plt.imread(os.path.join(current_directory, 'WTUS_SPC_Banner_nobg.png'))  
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 1.1), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)


### Functions to handle the outlook ###

# Function to check if there is a outlook to display
def check_outlook_availability(outlook_data):
    log.info('running check_outlook_availability')
    for feature in outlook_data['features']:
        # Check is there is a LABEL if there is coordinates in the geometry portion of the feature from the Source
        if 'LABEL' in feature['properties'] and 'geometry' in feature and 'coordinates' in feature ['geometry']: 
            log.info('There is an outlook')
            return True
    return False

# Function to plot the polygons
def plot_cat_outlook_polygons(ax, outlook_data):
    log.info('running plot_outlook_polygons')
    for feature in outlook_data['features']: 
        outlook_type = feature['properties']['LABEL']
        outlook_polygon = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Polygon':
            outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
        for polygon in outlook_polygon: # Find the properties of each polygon
            x, y = zip(*polygon[0])
            ax.add_patch(mpatches.Polygon(list(zip(x, y)), alpha=0.5, ec='k', lw=1, fc=get_cat_outlook_color(outlook_type))) 

# Function to display a popup and end the program if no outlook is available
def no_outlook_available():
    log.info('There is no outlook available')
    show_popup('No Outlook', "There is no outlook available at this time")
    return # Ends Program


### Functions to Plot and Save the Outlook Image

# Function to display the outlook
def display_cat_outlook(current_directory, outlook_data):
    log.info('running display_outlook')
    fig, ax = setup_plot()

    # Clear the figure and axes before displaying a new outlook
    fig.clear()
    ax = fig.add_subplot(111)

    if not check_outlook_availability(outlook_data):
        no_outlook_available()
        sys.exit(0)

    overlay_us_state_outline(ax, current_directory)
    overlay_us_interstate_lines(ax, current_directory)
    set_plot_limits(ax)
    add_basemap(ax)

    remove_axes_labels_boxes_title(ax)
    add_header_image(ax, current_directory)

    plot_cat_outlook_polygons(ax, outlook_data)

    output_directory = create_output_directory(current_directory)
    output_filename = 'spc_cat_outlook.png'
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



### Other Functions ###

# Function to display the popup message
def show_popup(title, message):
    log.info(f'Showing a popup titled "{title}"')
    root = tk.Tk()
    root.withdraw() # Hide the root window
    root.attributes('-topmost', True) # Make the window appear on top
    root.lift() # Bring the window to the front
    messagebox.showinfo(title, message) # Display the Popup Message
    root.destroy() # Destroy the root window after the messagebox is closed

# Function to determine the color for each outlook category
def get_cat_outlook_color(outlook_type):
    colors = {
        'TSTM': 'lightgreen',
        'MRGL': 'green',
        'SLGT': 'yellow',
        'ENH': 'orange',
        'MDT': 'red',
        'HIGH': 'magenta'
    }
    return colors.get(outlook_type, 'blue')  # Default to white color for unknown types


### GUI Functions ###

# Start the GUI
def start_gui():
    # Initialize a window
    log.info('GUI - Initializing window')
    window = ctk.CTk()
    window.geometry('900x400')
    window.title('Severe Weather Outlook Display')

    # Configure Layout
    window.grid_columnconfigure(5, weight=1)
    window.grid_rowconfigure(7, weight=1)

    # Fonts
    Title_Font = ctk.CTkFont(family='Montserrat', size=40, weight='bold')
    Description_Font = ctk.CTkFont(family='karla', size=18)

    # Title Label
    Title_Label = ctk.CTkLabel(window, text='Severe Weather Outlook Display', font=Title_Font)
    Title_Label.grid(columnspan=7)

    # Welcome Label
    Welcome_Label = ctk.CTkLabel(window, text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.', font=Description_Font)
    Welcome_Label.grid(columnspan=7)

    def D1_C_and_R():
        log.info('GUI - running the close_and_run_program function')
        window.withdraw()
        run_d1_cat()

    def D2_C_and_R():
        log.info('GUI - running the close_and_run_program function')
        window.withdraw()
        run_d2_cat()

    def Test_C_and_R():
        log.info('GUI - running the close_and_run_program function')
        window.withdraw()
        run_test_cat()
    
    def close_program():
        log.info('GUI - Now Closing Program')
        window.withdraw() 
        sys.exit(0)

    window.protocol("WM_DELETE_WINDOW", close_program)

    # Day 1 Categorial Button
    D1_Cat_Button = ctk.CTkButton(window, text='Day 1 Categorial', width=150, font=Description_Font, command=D1_C_and_R)
    D1_Cat_Button.grid(row=5, column=0, columnspan=1, padx=25, sticky='ew')

    # Day 2 Categorial Button
    D2_Cat_Button = ctk.CTkButton(window, text='Day 2 Categorial', width=150, font=Description_Font, command=D2_C_and_R)
    D2_Cat_Button.grid(row=5, column=1, columnspan=1, padx=25, sticky='ew')

    # Test Categorial Button
    Test_Button = ctk.CTkButton(window, text='Test Categorial', width=150, font=Description_Font, command=Test_C_and_R)
    Test_Button.grid(row=5, column=2, columnspan=1, padx=25, sticky='ew')

    # Close Button
    Close_Button=ctk.CTkButton(window, text='Close', font=Description_Font, width=50, command=close_program)
    Close_Button.grid(row=0, column=5, sticky='e')

    log.info('GUI - Created widgets')

    # Run the Window
    log.info('GUI - Running window')
    window.mainloop()


### Function to Run the Program ###
def run_d1_cat():
    log.info('Running Day 1 Categorial Function')
    show_popup('program is Running', 'Program is now running and may take some time to run. Click "ok" or Close to continue')
    outlook_data = fetch_d1_cat_outlook()
    display_cat_outlook(current_directory, outlook_data)

def run_test_cat():
    log.info('Running Test Categorial')
    show_popup('program is running', 'Program is now running and may take some time to run. Click "ok" or Close to continue')
    outlook_data = fetch_test_cat_outlook()
    display_cat_outlook(current_directory, outlook_data)

def run_d2_cat():
    log.info('Running Test Categorial')
    show_popup('program is running', 'Program is now running and may take some time to run. Click "ok" or Close to continue')
    outlook_data = fetch_d2_cat_outlook()
    display_cat_outlook(current_directory, outlook_data)

start_gui()