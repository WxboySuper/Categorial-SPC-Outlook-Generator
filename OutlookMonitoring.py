
# * Outlook Monitoring
# * Created by WeatherboySuper
# * Created with WeatherTrackUS

# Imports
import os, requests, matplotlib, matplotlib.pyplot as plt, matplotlib.patches as mpatches, geopandas as gpd, tkinter as tk, ttkbootstrap as ttk, customtkinter as ctk, contextily as ctx, sys, logging as log, pystray, feedparser, time, threading

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from tkinter import TclError
from PIL import Image, ImageTk
from customtkinter import CTkImage
from plyer import notification

matplotlib.use('TkAgg')

# Create root
root = tk.Tk()
root.withdraw()


class monitor:
    def __init__(self):
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        self.instance = 0
        self.rss_url = 'https://www.spc.noaa.gov/products/spcacrss.xml'
        self.check_interval = 60
        self.refresh_interval = 15 # Refresh the list every 15 seconds
        self.notified_titles = [] # List to store notified titles
        self.first_message_title = None # Title of the first message encountered
    
    def rss(self):
        self.last_refresh_time = time.time()
        
        while True:
            self.current_time = time.time()
            if self.current_time - self.last_refresh_time >= self.refresh_interval:
                # Refresh the list every refresh_interval seconds
                self.last_refresh_time = self.current_time
            
            feed = feedparser.parse(self.rss_url)
            if feed.entries:
                for entry in feed.entries:
                    if entry.title not in self.notified_titles:
                        truncated_title = entry.title [:256]
                        log.info(f'RSS - New RSS Notification. {entry.title}')
                        notification.notify( # type: ignore
                            title='New RSS Feed Update',
                            message=(f'{truncated_title}. Check it out in the App!'),
                            timeout=10
                        )
                        self.notified_titles.append(entry.title)
            log.info(f'RSS - {self.notified_titles}')
            time.sleep(self.check_interval)
            log.info('RSS - Interval Passed')
    
class fetch:
    def __init__(self):
        pass

    def popup(self, type, title, message):
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

    def cat(self, day):
        log.info('Fetching a Categorical Outlook')
        if day == 1:
            url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson'
        elif day == 2:
            url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_cat.nolyr.geojson'
        elif day == 3:
            url = 'https://www.spc.noaa.gov/products/outlook/day3otlk_cat.nolyr.geojson'
        elif day == 'test':
            url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210526_1630_cat.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 199')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def tor(self, day):
        log.info('Fetching a Tornado Outlook')
        if day == 1:
            url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_torn.nolyr.geojson'
        elif day == 2:
            url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_torn.nolyr.geojson'
        elif day == 'test':
            url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210317_1630_torn.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 131')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def wind(self, day):
        log.info('Fetching a Wind Outlook')
        if day == 1:
            url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_wind.nolyr.geojson'
        elif day == 2:
            url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_wind.nolyr.geojson'
        elif day == 'test':
            url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210325_1630_wind.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 148')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def hail(self, day):
        log.info('Fetching a Hail Outlook')
        if day == 1:
            url = 'https://www.spc.noaa.gov/products/outlook/day1otlk_hail.nolyr.geojson'
        elif day == 2:
            url = 'https://www.spc.noaa.gov/products/outlook/day2otlk_hail.nolyr.geojson'
        elif day == 'test':
            url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210526_1630_hail.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 165')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def d48(self, day):
        log.info('Fetching a 48 Hour Outlook')
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
        elif day == 'test':
            url = 'https://www.spc.noaa.gov/products/outlook/archive/2021/day1otlk_20210526_1630_48hr.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 181')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def prob(self, day):
        log.info('Fetching a Probability Outlook')
        if day == 3:
            url = 'https://www.spc.noaa.gov/products/outlook/day3otlk_prob.lyr.geojson'
        else:
            log.error(f'Invalid Date. Day = {day}. Error on line 197')
            self.popup('error', 'Invalid Day', "An error has occured where the day wasn't read correctly. The program will now quit.")
            sys.exit(0)
        response = requests.get(url)
        response.raise_for_status()
        self.outlook_data = response.json()
        return self.outlook_data
    
    def no_outlook_available(self, gui_callback):
        log.info('No outlook available')
        self.popup('error', 'No Outlook Available', 'There is no outlook available for the selected day. The outlook will not be displayed.')
        gui_callback()

    def check_outlook_availability(self, outlook_data, gui_callback):
        for feature in outlook_data['features']:
            if 'coordinates' in feature['geometry']:
                log.info('There is an outlook')
            else:
                self.no_outlook_available(gui_callback)