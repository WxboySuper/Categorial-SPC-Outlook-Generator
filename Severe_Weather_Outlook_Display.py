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

# Import specific functions from modules
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from tkinter import TclError

from CTkMessagebox import CTkMessagebox

matplotlib.use('TkAgg')


# Variables
log_directory = 'C:\\log'
current_directory = os.path.dirname(os.path.abspath(__file__))

# Create a Tkinter root window
root = tk.Tk()
root.withdraw()

# Setup Function
def setup():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log.basicConfig(
        level = log.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='C:\\log\\cod.log',
        filemode='w'
    )

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
        log.error(f'Invalid Date. Day = {day}. Error on Line 68')
        popup('warning', 'Invalid Day', "An error has occured where the day wasn't read correctly.")
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
        log.error(f'Invalid Date. Day = {day}. Error on line 84')
        popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly.")
    response = requests.get(url) # Requests the data from the GeoJSON URL
    response.raise_for_status()
    outlook_data = response.json()
    return outlook_data # Returns the data from the Outlook

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
    header_img = OffsetImage(header_img, zoom=0.4)
    ab = AnnotationBbox(header_img, (0.3, 1.1), xycoords='axes fraction', frameon=False)
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
        if 'LABEL' in feature['properties'] and 'geometry' in feature and 'coordinates' in feature ['geometry']: 
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

    if not check_outlook_availability(outlook_data):
        no_outlook_available()
        start_gui()

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
        popup('warning', 'Invalid Outlook Type', 'There was an error when trying to get colors')

# Displaying Popups
def popup(type, title, message):
    log.info(f'Showing a {type} popup titled {title} with the following message: {message}')
    if type == 'info':
        messagebox.showinfo(title, message)
    elif type == 'error':
        messagebox.showerror(title, message)
    elif type == 'warning':
        messagebox.showwarning(title, message)
    elif type == 'question':
        messagebox.askquestion(title, message)
    else:
        messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup')

# Start the GUI
def start_gui():
    # Initialize a window
    log.info('GUI - Initializing window')
    window = ctk.CTk()
    window.geometry('1500x600')
    window.title('Severe Weather Outlook Display')

    # Configure Layout
    window.grid_columnconfigure(3, weight=1)
    window.grid_rowconfigure(7, weight=1)

    # Fonts
    Title_Font = ctk.CTkFont(family='Montserrat', size=50, weight='bold')
    Description_Font = ctk.CTkFont(family='karla', size=21)

    # Frames
    sidebar_frame = ctk.CTkFrame(window, fg_color='grey')
    sidebar_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsw')

    main_frame = ctk.CTkFrame(window, fg_color='darkblue')
    main_frame.grid(row=0, column=1, padx=10, pady=10)

    def buttons(day):
        if day == 1:
            # Day 1 Categorial Button
            D1_Cat_Button = ctk.CTkButton(main_frame, text='Day 1 Categorial', width=300, font=Description_Font, command=lambda: button_run('cat', 1))
            D1_Cat_Button.grid(row=2, column=0, columnspan=1, padx=45, pady=50, sticky='ew')

            # Day 1 Tornado Button
            D1_Tor_Button = ctk.CTkButton(main_frame, text='Day 1 Tornado', width = 300, font=Description_Font, command=lambda: button_run('tor', 1))
            D1_Tor_Button.grid(row=3, column=0, columnspan=1, padx=45, pady=50, sticky='ew')
        elif day == 2:
            # Day 2 Categorial Button
            D2_Cat_Button = ctk.CTkButton(main_frame, text='Day 2 Categorial', width=300, font=Description_Font, command=lambda: button_run('cat', 2))
            D2_Cat_Button.grid(row=2, column=1, columnspan=1, padx=25, pady=50, sticky='ew')

            # Day 2 Tornado Button
            D2_Tor_Button = ctk.CTkButton(main_frame, text='Day 2 Tornado', width = 300, font=Description_Font, command=lambda: button_run('tor', 2))
            D2_Tor_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=50, sticky='ew')
        elif day == 3:
            # Day 3 Categorial Button
            D3_Cat_Button = ctk.CTkButton(main_frame, text='Day 3 Categorial', width=300, font=Description_Font, command=lambda: button_run('cat', 3))
            D3_Cat_Button.grid(row=2, column=2, columnspan=1, padx=25, pady=50, sticky='ew')
        elif day == 'test':
            # Test Categorial Button
            Test_Button = ctk.CTkButton(main_frame, text='(Test) March 31st, 2023', width=300, font=Description_Font, command=lambda: button_run('cat', 'test'))
            Test_Button.grid(row=2, column=3, columnspan=1, padx=25, pady=50, sticky='ew')
        
            # Test Tornado Button
            Test_Tor_Button = ctk.CTkButton(main_frame, text='(Test) March 17th, 2021', width = 300, font=Description_Font, command=lambda: button_run('tor', 'test'))
            Test_Tor_Button.grid(row=3, column=3, columnspan=1, padx=25, pady=50, sticky='ew')
        else:
            log.error(f'Invalid Button. Day = {day}. Error on line 436')
            popup('error', 'Invalid Button', "An error has occured where the button isn't programmed correctly.")
        
    def frame_change(day):
        for widget in main_frame.winfo_children():
            widget.destroy()
        
        buttons(day)

    def button_run(type, day):
        log.info(f'GUI - {type} {day} button has been pressed. Running Day {day} {type} outlook')
        window.withdraw()
        run(type, day)
    
    def close_program():
        log.info('GUI - Now Closing Program')
        window.withdraw() 
        sys.exit(0)

    window.protocol("WM_DELETE_WINDOW", close_program)

    ## Mainscreen Setup ##
    # Title Label
    Title_Label = ctk.CTkLabel(main_frame, text='Severe Weather Outlook Display', font=Title_Font)
    Title_Label.grid(columnspan=7, row=0)

    # Welcome Label
    Welcome_Label = ctk.CTkLabel(main_frame, text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.', font=Description_Font)
    Welcome_Label.grid(columnspan=7, row=1)

    ## Sidebar Buttons ##
    # Day 1 Button
    D1_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 1', width=200, height=50, font=Description_Font, command=lambda: frame_change(1))
    D1_Side_Button.grid(row=0, column=0, columnspan=1, padx=5, pady=10)

    # Day 2 Button
    D2_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 2', width=200, height=50, font=Description_Font, command=lambda: frame_change(2))
    D2_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

    # Day 3 Button
    D3_Side_Button = ctk.CTkButton(sidebar_frame, text='Day 3', width=200, height=50, font=Description_Font, command=lambda: frame_change(3))
    D3_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

    # Day Test Button
    Test_Side_Button = ctk.CTkButton(sidebar_frame, text='Day Test', width=200, height=50, font=Description_Font, command=lambda: frame_change('test'))
    Test_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

    log.info('GUI - Created widgets')

    # Run the Window
    log.info('GUI - Running window')
    window.mainloop()

### Function to Run the Program ###
def run(type, day):
    log.info(f'Running the Program under day {day}')
    popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be paitent. Click "Ok" or Close the Window to Continue')
    if type == 'cat':
        outlook_data = fetch_cat_outlooks(day)
        display_cat_outlook(day, outlook_data)
    elif type == 'tor':
        outlook_data = fetch_tor_outlooks(day)
        display_tor_outlook(day, outlook_data)
    else:
        log.error(f'Invalid Outlook Type. Outlook Type = {type}')
        popup('error', 'Invalid Outlook Type', "An error has occured where the outlook type wasn't read correctly.")

setup()
start_gui()