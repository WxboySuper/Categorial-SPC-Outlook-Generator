# Outlook Processing
# Created by WeatherboySuper
# Created with WeatherTrackUS
import OutlookMonitoring

import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import tkinter as tk
import contextily as ctx
import sys
import logging as log

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

matplotlib.use('TkAgg')

# Create root
root = tk.Tk()
root.withdraw()

monitor = OutlookMonitoring.monitor()
fetch = OutlookMonitoring.fetch()


class plot:
    """
    Represents a class for plotting severe weather outlook data.

    This class provides methods for setting up a plot, adding overlays and shapefiles, and creating an output directory.

    Attributes:
        question (str): The question to be asked.
        output_directory (str): The directory where the output will be saved.
        current_directory (str): The current working directory.
        fig (matplotlib.figure.Figure): The figure object.
        ax (matplotlib.axes.Axes): The axes object.

    Methods:
        __init__(): Initializes the plot object with default values.
        popup(type, title, message): Displays a popup message box of the specified type with the given title and message.
        create_output_directory(): Creates an output directory in the current directory.
        setup_plot(): Sets up the plot by configuring the figure and axes.
        add_overlays(outlook_type): Adds overlays and shapefiles to the plot based on the provided outlook type.
    """

    def __init__(self):
        """
        Initializes the `plot` object with default values for the `question`, `output_directory`, and `current_directory` attributes.
        Sets up the figure and axes for plotting with a size of (10,8).
        """
        self.question = None
        self.output_directory = None
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        self.fig, self.ax = plt.subplots(figsize=(10,8))

    def popup(self, type, title, message):
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
        :return: The `popup` method returns the value of `self.question` when the `type` parameter is
        set to 'question'.
        """
        log.info(f'Showing a {type} popup titled {title} with the following message: {message}')
        if type == 'info':
            messagebox.showinfo(title, message)
        elif type == 'error':
            messagebox.showerror(title, message)
        elif type == 'warning':
            messagebox.showwarning(title, message)
        elif type == 'question':
            self.question = messagebox.askquestion(title, message)
            return self.question
        else:
            messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup. The program will now quit.')
            sys.exit(0)

    def create_output_directory(self):
        """
        Creates an output directory in the current directory named 'output' if it does not already exist.
        
        Returns:
            str: The path of the newly created output directory.
        """
        self.output_directory = os.path.join(self.current_directory, 'output')
        os.makedirs(self.output_directory, exist_ok = True)
        return self.output_directory
    
    def setup_plot(self):
        """
        Sets up the plot by configuring the figure and axes for plotting.

        This function sets the face color of the figure to black and adjusts the aspect ratio of the axes to 'auto'. 
        It also sets the x-axis and y-axis limits to (-125, -66) and (20, 60) respectively. 
        The function then removes the x-axis and y-axis ticks and tick labels, hides the top, right, bottom, and left spines, 
        and sets the title of the plot to an empty string. 
        Finally, it adds a basemap to the axes using the specified zoom level, coordinate reference system, and source URL.

        Returns:
            tuple: A tuple containing the figure and axes objects.
        """
        self.fig.set_facecolor('black')
        self.ax.set_aspect('auto', adjustable='box')

        self.ax.set_xlim(-125, -66)
        self.ax.set_ylim(20, 60)

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)

        self.ax.set_title('')

        ctx.add_basemap(self.ax, zoom=6, crs='EPSG:4326', source='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=63fe7729-f786-444d-8787-817db15f3368') # type: ignore

        return self.fig, self.ax
    
    def add_overlays(self, outlook_type):
        """
        Adds overlays and shapefiles to the plot.

        This function adds state outlines, interstate lines, and a header image to the plot based on the provided outlook type.

        Parameters:
            outlook_type (str): The type of outlook to display. Can be 'cat', 'tor', 'wind', 'hail', 'd4-8', or 'prob'.

        Returns:
            None
        """
        log.info('Adding all Overlays and Shapefiles')

        # State Outlines
        states_shapefile = os.path.join(self.current_directory, '../files/mapping/s_11au16.shp') 
        states = gpd.read_file(states_shapefile)  
        states.plot(ax=self.ax, edgecolor='black', lw=0.75, alpha=0.75) # Remove facecolor (Added right below), and changed edgecolor to 'white' to contrast with the black 
        self.ax.set_facecolor("black") # Background of the CONUS Shapefile will be Black

        # Interstate Lines
        highways_shapefile = os.path.join(self.current_directory, '../files/mapping/USA_Freeway_System.shp')
        highways_gdf = gpd.read_file(highways_shapefile)
        highways_gdf.plot(ax=self.ax, color='red', linewidth=0.6, alpha=0.75)

        # Header Image
        if outlook_type =='cat':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_cat_header.png'))
        elif outlook_type =='tor':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_tor_header.png'))
        elif outlook_type =='wind':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_wind_header.png'))
        elif outlook_type =='hail':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_hail_header.png'))
        elif outlook_type =='d4-8':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_d48_header.png'))
        elif outlook_type =='prob':
            header_img = plt.imread(os.path.join(self.current_directory, '../files/overlays/wtus_prob_header.png'))
        else:
            log.error(f"There was an error getting the {outlook_type} header. Error on line 276.")
            self.popup('error', 'Header Error', 'An error has occured getting the header image. The program will now quit.')
        
        header_img = OffsetImage(header_img, zoom=0.4)
        ab = AnnotationBbox(header_img, (0.3, 0.95), xycoords='axes fraction', frameon=False)
        self.ax.add_artist(ab)

    def color(self, outlook_type, outlook_label):
        """
        Returns the color associated with a given outlook type and label.

        Parameters:
            outlook_type (str): The type of outlook. Can be 'cat', 'tor', 'wind', 'hail', 'd4-8', or 'prob'.
            outlook_label (str): The label of the outlook.

        Returns:
            str: The color associated with the outlook type and label. Returns 'blue' if the label is not found.
        """
        log.info(f'Getting {outlook_type} for {type} outlook')
        if outlook_type == 'cat':
            colors = {
            'TSTM': 'lightgreen',
            'MRGL': 'green',
            'SLGT': 'yellow',
            'ENH': 'orange',
            'MDT': 'red',
            'HIGH': 'magenta'
            }
            return colors.get(outlook_label, 'blue') # Returns the Color, Blue if not found
        elif outlook_type == 'tor':
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
            return colors.get(outlook_label, 'blue') # Returns the color, Blue if not found
        elif ('wind', 'hail', 'prob') in outlook_type:
            colors = {
                '0.05': 'saddlebrown',
                '0.15': 'gold',
                '0.30': 'red',
                '0.45': 'fuchsia',
                '0.60': 'blueviolet',
                'sig': 'black'
            }
            return colors.get(outlook_label, 'blue') # Returns the color, Blue if not found
        elif outlook_type == 'd4-8':
            colors = {
                '0.15': 'gold',
                '0.30': 'sandybrown'
            }
            return colors.get(outlook_label, 'blue') # Returns the color, blue if not found
        else:
            log.error(f"There was an error accessing colors. Error on line 751")
            self.popup('warning', 'Invalid Outlook Type', 'There was an error when trying to get colors. The program will now quit.')
            sys.exit(0)

    def plot_outlook_polygons(self, outlook_type, outlook_data):
        """
        Plots outlook polygons on a map based on the provided outlook type and data.

        Args:
            outlook_type (str): The type of outlook to plot (e.g. 'cat', 'tor', 'wind', etc.).
            outlook_data (dict): The data containing the outlook polygons to plot.

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
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('cat', outlook_label)))
        elif outlook_type == 'tor':
            for feature in outlook_data['features']:
                outlook_label = feature['properties']['LABEL']
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for polygon in outlook_polygon: # Find the properties of each polygon
                        x, y = zip(*polygon[0])
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('tor', outlook_label), edgecolor='black', hatch='x'))
                        else:
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('tor', outlook_label)))
                elif feature['geometry']['type'] == 'MultiPolygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for multipolygon in outlook_polygon: # Find the properties of each polygon
                        for polygon in multipolygon:
                            x, y = zip(*polygon[0])
                            if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('tor', outlook_label), edgecolor='black', hatch='x'))
                            else:
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('tor', outlook_label)))
        elif outlook_type == 'wind':
            for feature in outlook_data['features']:
                outlook_label = feature['properties']['LABEL']
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for polygon in outlook_polygon: # Find the properties of each polygon
                        x, y = zip(*polygon[0])
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('wind', outlook_label), edgecolor='black', hatch='x'))
                        else:
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('wind', outlook_label)))
                elif feature['geometry']['type'] == 'MultiPolygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for multipolygon in outlook_polygon: # Find the properties of each polygon
                        for polygon in multipolygon:
                            x, y = zip(*polygon[0])
                            if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('wind', outlook_label), edgecolor='black', hatch='x'))
                            else:
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('wind', outlook_label)))
        elif outlook_type == 'hail':
            for feature in outlook_data['features']:
                outlook_label = feature['properties']['LABEL']
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for polygon in outlook_polygon: # Find the properties of each polygon
                        x, y = zip(*polygon[0])
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('hail', outlook_label), edgecolor='black', hatch='x'))
                        else:
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('hail', outlook_label)))
                elif feature['geometry']['type'] == 'MultiPolygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for multipolygon in outlook_polygon: # Find the properties of each polygon
                        for polygon in multipolygon:
                            x, y = zip(*polygon[0])
                            if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('hail', outlook_label), edgecolor='black', hatch='x'))
                            else:
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('hail', outlook_label)))
        elif outlook_type == 'd4-8':
            for feature in outlook_data['features']:
                outlook_label = feature['properties']['LABEL']
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                for polygon in outlook_polygon: # Find the properties of each polygon
                    x, y = zip(*polygon[0])
                    self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('d4-8', outlook_label)))
        elif outlook_type == 'prob':
            for feature in outlook_data['features']:
                outlook_label = feature['properties']['LABEL']
                outlook_polygon = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for polygon in outlook_polygon: # Find the properties of each polygon
                        x, y = zip(*polygon[0])
                        if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('prob', outlook_label), edgecolor='black', hatch='x'))
                        else:
                            self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('prob', outlook_label)))
                elif feature['geometry']['type'] == 'MultiPolygon':
                    outlook_polygon = [outlook_polygon]  # Convert single polygon to a list for consistency
                    for multipolygon in outlook_polygon: # Find the properties of each polygon
                        for polygon in multipolygon:
                            x, y = zip(*polygon[0])
                            if outlook_label == 'SIGN':  # Add hatching for 'SIGN' outlook type
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.2, ec='k', lw=1, fc=self.color('prob', outlook_label), edgecolor='black', hatch='x'))
                            else:
                                self.ax.add_patch(mpatches.Polygon(polygon[0], alpha=0.5, ec='k', lw=1, fc=self.color('prob', outlook_label)))
        else:
            log.error(f"There was an error plotting the {type} outlook. Error on line 405.")
            self.popup('error', 'Plotting Error', 'An error has occured plotting the outlook. The program will now quit.')
            sys.exit(0)

class display:
    """
    Represents a class for displaying severe weather outlook data.

    This class provides methods for displaying different types of outlook data, including categorical, tornado, wind, hail, and probability outlooks.

    Attributes:
        ax (matplotlib.axes.Axes): The axes object.
        fig (matplotlib.figure.Figure): The figure object.
        plotting (plot): An instance of the plot class for handling plotting tasks.

    Methods:
        cat(day, start_gui_callback, outlook_data): Displays a categorical outlook for a given day.
        tor(day, start_gui_callback, outlook_data): Displays a tornado outlook for a given day.
        wind(day, start_gui_callback, outlook_data): Displays a wind outlook for a given day.
        hail(day, start_gui_callback, outlook_data): Displays a hail outlook for a given day.
        d48(day, start_gui_callback, outlook_data): Displays a 48-hour outlook for a given day.
        prob(day, start_gui_callback, outlook_data): Displays a probability outlook for a given day.
        close_figure(): Closes the current figure.
    """

    def __init__(self):
        """
        Initializes the display object with default values for the ax, fig, and plotting attributes.
        
        Parameters:
        None
        
        Returns:
        None
        """
        self.ax = None
        self.fig = None
        self.plotting = plot()

    def cat(self, day, start_gui_callback, outlook_data):
        """
        Displays a categorial outlook for a given day.

        Parameters:
            day (int): The day for which the outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Categorial Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('cat')

        self.plotting.plot_outlook_polygons('cat', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}cat_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.
            
            Parameters:
                None
            
            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')

    def tor(self, day, start_gui_callback, outlook_data):
        """
        Displays a Tornado Outlook for a given day.

        Parameters:
            day (int): The day for which the outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Tornado Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('tor')

        self.plotting.plot_outlook_polygons('tor', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}_tor_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.
            
            Parameters:
                None
            
            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')

    def wind(self, day, start_gui_callback, outlook_data):
        """
        Displays a Wind Outlook for a given day.

        Parameters:
            day (int): The day for which the outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Wind Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('wind')

        self.plotting.plot_outlook_polygons('wind', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}_wind_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.
            
            Parameters:
                None
            
            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')

    def hail(self, day, start_gui_callback, outlook_data):
        """
        Displays the hail outlook for a given day.

        Parameters:
            day (int): The day for which the hail outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the hail outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Hail Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('hail')

        self.plotting.plot_outlook_polygons('hail', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}_hail_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.
            
            Parameters:
                None
            
            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')
    
    def d48(self, day, start_gui_callback, outlook_data):
        """
        Displays a Day 4-8 Outlook for a given day.

        Parameters:
            day (int): The day for which the outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Day 4-8 Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('d4-8')

        self.plotting.plot_outlook_polygons('d4-8', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}_d4-8_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.

            Parameters:
                None

            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')
    
    def prob(self, day, start_gui_callback, outlook_data):
        """
        Displays a probabilistic outlook for a given day.

        Parameters:
            day (int): The day for which the outlook is to be displayed.
            start_gui_callback (function): A callback function to start the GUI.
            outlook_data (dict): The data for the outlook to be displayed.

        Returns:
            None
        """
        log.info('Displaying Probabilistic Outlook')
        self.fig, self.ax = self.plotting.setup_plot()

        # Clear the figure and axes before displaying a new outlook
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.plotting.add_overlays('prob')

        self.plotting.plot_outlook_polygons('prob', outlook_data)

        output_directory = self.plotting.create_output_directory()
        output_filename = f'spc_day_{day}_prob_outlook.png'
        output_path = os.path.join(output_directory, output_filename)

        for widget in root.winfo_children():
            widget.destroy()

        # Create a canvas and add it to the root window
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a custom toolbar with a close button
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()

        def close_figure():
            """
            Closes the current figure and withdraws the root window, then calls the start_gui_callback function.

            Parameters:
                None

            Returns:
                None
            """
            plt.close(self.fig)
            root.withdraw()
            start_gui_callback()

        close_button = tk.Button(toolbar, text='Close', command=close_figure)
        close_button.pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", close_figure)

        # Show the Tkinter root window with the canvas and toolbar
        root.deiconify()
        root.mainloop()

        log.info('Showing the plot')
        plt.savefig(output_path, dpi=96, bbox_inches='tight')