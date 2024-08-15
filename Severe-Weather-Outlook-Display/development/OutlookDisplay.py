# Outlook Display
# Created by WeatherboySuper
# Created with WeatherTrackUS

# Imports
import os, requests, matplotlib, matplotlib.pyplot as plt, matplotlib.patches as mpatches, geopandas as gpd, tkinter as tk, ttkbootstrap as ttk, customtkinter as ctk, contextily as ctx, sys, logging as log, pystray, feedparser, time, threading

import OutlookMonitoring
import OutlookProcessing

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

monitor = OutlookMonitoring.monitor()
fetch = OutlookMonitoring.fetch()

display = OutlookProcessing.display()

class GUI:
    _instance = None

    def __init__(self):
        self.current_directory = os.path.dirname(os.path.abspath(__file__))

        self.tornado_icon_path = os.path.join(self.current_directory, '../files/icons/Tornado.png')
        self.tornado_icon = ctk.CTkImage(dark_image=Image.open(self.tornado_icon_path), 
                                         light_image=Image.open(self.tornado_icon_path), 
                                         size=(50,40))
        self.home_icon_path = os.path.join(self.current_directory, '../files/icons/Home.png')
        self.home_icon = ctk.CTkImage(dark_image=Image.open(self.home_icon_path), 
                                      light_image=Image.open(self.home_icon_path), 
                                      size=(50,40))
        self.lightning_icon_path = os.path.join(self.current_directory, '../files/icons/Lightning.png')
        self.lightning_icon = ctk.CTkImage(dark_image=Image.open(self.lightning_icon_path), 
                                           light_image=Image.open(self.lightning_icon_path), 
                                           size=(50,40))
        self.logo_icon_path = os.path.join(self.current_directory, '../files/icons/My_project.png')
        self.logo_icon = ctk.CTkImage(dark_image=Image.open(self.logo_icon_path), 
                                      light_image=Image.open(self.logo_icon_path), 
                                      size=(120,120))

        self.risk_level_mapping_cat = {
            'TSTM': 1, # Thunderstorm
            'MRGL': 2, # Marginal
            'SLGT': 3, # Slight
            'ENH': 4,   # Enhanced
            'MDT': 5,   # Moderate
            'HIGH': 6   # High
        }

        self.risk_level_mapping_tor = {
            '0.02': 1,
            '0.05': 2,
            '0.10': 3,
            '0.15': 4,
            '0.30': 5,
            '0.45': 6,
            '0.60': 7
        }

        self.risk_level_mapping_prob = {
            '0.05': 1,
            '0.15': 2,
            '0.30': 3,
            '0.45': 4,
            '0.60': 5,
        }

        self.risk_level_mapping_d48 = {
            '0.15': 1,
            '0.30': 2
        }

        if not GUI._instance:
            GUI._instance = self
            #self.create_window()
        else:
            self = GUI._instance

    '''def create_window(self):
        # Initialize a window
        log.info('GUI - Initializing window')
        self.window = ctk.CTkToplevel()
        self.window.geometry('1700x900+50+50')
        self.window.title('Severe Weather Outlook Display')

        # Configure Layout
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(2, weight=1)

        # Fonts
        self.Title_Font = ctk.CTkFont(family='Montserrat', size=50, weight='bold')
        self.Description_Font = ctk.CTkFont(family='karla', size=21)

        # Frames
        self.sidebar_frame = ctk.CTkFrame(self.window, height=550, fg_color='#103157')
        self.sidebar_frame.grid(row=0, column=0, sticky='ns')

        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, columnspan=2, sticky='nsew')'''

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

    def run_gui(self):
        log.info('Starting GUI')

        # Initialize a window
        log.info('GUI - Initializing window')
        self.window = ctk.CTkToplevel()
        self.window.geometry('1700x900+50+50')
        self.window.title('Severe Weather Outlook Display')

        # Configure Layout
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(2, weight=1)

        # Fonts
        self.Title_Font = ctk.CTkFont(family='Montserrat', size=50, weight='bold')
        self.Description_Font = ctk.CTkFont(family='karla', size=21)

        # Frames
        self.sidebar_frame = ctk.CTkFrame(self.window, height=550, fg_color='#103157')
        self.sidebar_frame.grid(row=0, column=0, sticky='ns')

        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, columnspan=2, sticky='nsew')

        self.side_bar()
        self.frames('home')

        self.window.mainloop()

    def frame_change(self, day):

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.frames(day)

    def button_run(self, outlook_type, day):
        log.info(f'GUI - {type} {day} button has been pressed. Running Day {day} {type} outlook')
        self.window.withdraw()
        run.run_program(outlook_type, day, self.window)

    def show_from_system_tray(self,icon, item):
        icon.stop()
        self.window.deiconify()

    def hide_to_system_tray(self):
        global icon
        self.window.withdraw()
        image = Image.open('../files/icons/My_project.png')
        menu = (pystray.MenuItem("Show", self.show_from_system_tray), pystray.MenuItem("Exit", self.close_program))
        icon = pystray.Icon("name", image, "My System Tray Icon", menu)
        icon.run()

    def close_program(self):
        global question # Declare question as a global variable
        log.info('GUI - Now Closing Program')
        self.popup('question', 'Close Program?', 'Are you sure you want to close the program? You will not receive notifications for new outlooks when the program is closed. Use "Hide" instead to hide the program and still receive new outlook notifications!')
        if self.question == 'yes':
            if 'icon' in globals() and icon is not None:
                icon.stop() 
            self.window.withdraw() 
            os._exit(0)
        else:
            return

    def side_bar(self):
        ## Sidebar Buttons ##
        # Logo
        logo_Button = ctk.CTkButton(self.sidebar_frame, text='', width=200, height=250, corner_radius=10, fg_color='transparent', 
                                    state='disabled', image=self.logo_icon, compound='top')
        logo_Button.grid(row=0, column=0, columnspan=1, padx=5, pady=10)
        
        # Home Button
        Home_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Home', width=200, corner_radius=10, fg_color='transparent',
                                        font=('karla', 26), command=lambda: self.frame_change('home'),
                                        hover_color='#2191aa', image=self.home_icon, compound='top')
        Home_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

        # Day 1 Button
        D1_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 1',width=200, corner_radius=12, fg_color='transparent',
                                    font=('karla', 26), command=lambda: self.frame_change(1),
                                    hover_color='#2191aa', image=self.tornado_icon)
        D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

        # Day 2 Button
        D2_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 2',width=200, corner_radius=12, fg_color='transparent',
                                    font=('karla', 26), command=lambda: self.frame_change(2),
                                    hover_color='#2191aa', image=self.tornado_icon)
        D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

        # Day 3 Button
        D3_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 3',width=200, corner_radius=12, fg_color='transparent', 
                                    font=('karla', 26), command=lambda: self.frame_change(3),
                                    hover_color='#2191aa', image=self.lightning_icon)
        D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)

        # Day 4-8 Button
        D48_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 4-8',width=200, corner_radius=12, fg_color='transparent', 
                                        font=self.Description_Font, command=lambda: self.frame_change('d4-8'),
                                        hover_color='#2191aa', image=self.lightning_icon)
        D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)

    def determine_highest_risk_level_cat(self, outlook_data):
        highest_risk_level = 0
        for feature in outlook_data['features']:
            risk_level_label = feature['properties'].get('LABEL')
            if risk_level_label:
                risk_level = self.risk_level_mapping_cat.get(risk_level_label)
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

    def determine_highest_risk_level_tor(self, outlook_data):
        highest_tor_risk_level = 0
        for feature in outlook_data['features']:
            tor_risk_level_label = feature['properties'].get('LABEL')
            if tor_risk_level_label:
                risk_level = self.risk_level_mapping_tor.get(tor_risk_level_label)
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
    
    def determine_highest_risk_level_wind(self, outlook_data):
        highest_wind_risk_level = 0
        for feature in outlook_data['features']:
            wind_risk_level_label = feature['properties'].get('LABEL')
            if wind_risk_level_label:
                risk_level = self.risk_level_mapping_prob.get(wind_risk_level_label)
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
    
    def determine_highest_risk_level_hail(self, outlook_data):
        highest_hail_risk_level = 0
        for feature in outlook_data['features']:
            hail_risk_level_label = feature['properties'].get('LABEL')
            if hail_risk_level_label:
                risk_level = self.risk_level_mapping_prob.get(hail_risk_level_label)
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
    
    def determine_highest_risk_level_prob(self, outlook_data):
        highest_prob_risk_level = 0
        for feature in outlook_data['features']:
            prob_risk_level_label = feature['properties'].get('LABEL')
            if prob_risk_level_label:
                risk_level = self.risk_level_mapping_prob.get(prob_risk_level_label)
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
    
    def determine_highest_risk_level_d48(self, outlook_data):
        highest_d48_risk_level = 0
        for feature in outlook_data['features']:
            d48_risk_level_label = feature['properties'].get('LABEL')
            if d48_risk_level_label:
                risk_level = self.risk_level_mapping_d48.get(d48_risk_level_label)
                if risk_level is not None and (highest_d48_risk_level is None or risk_level > highest_d48_risk_level):
                    highest_d48_risk_level = risk_level
        if highest_d48_risk_level == 0:
            highest_d48_risk_level = 'None'
        elif highest_d48_risk_level == 1:
            highest_d48_risk_level = '15%'
        elif highest_d48_risk_level == 2:
            highest_d48_risk_level = '30%'
        return highest_d48_risk_level

    def frames(self, day):
        if day == 'home':
            self.side_bar()
            
            # Home Button
            Home_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Home', width=200, corner_radius=10, fg_color='transparent',
                                     font=('karla', 26), command=lambda: self.frame_change('home'),
                                     state='disabled', image=self.home_icon, compound='top')
            Home_Side_Button.grid(row=1, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(self.main_frame, text='Close', width=200, font=self.Description_Font, command=self.close_program)
            Close_Button.place(x=1285, y=15)

            # Hide Button
            Hide_Button = ctk.CTkButton(self.main_frame, text='Hide', width=200, font=self.Description_Font, command=self.hide_to_system_tray)
            Hide_Button.place(x=1075, y=15)

            # Title Label
            Title_Label = ctk.CTkLabel(self.main_frame, text='Severe Weather Outlook Display', 
                                       font=('Montserrat', 72, 'bold'), width=1200)
            Title_Label.place(x=150, y=350)

            # Welcome Label
            Welcome_Label = ctk.CTkLabel(self.main_frame, text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.', 
                                        font=('karla', 25))
            Welcome_Label.place(x=200, y=450)
        elif day == 1:
            outlook_data_cat_day_1 = fetch.cat(1)
            highest_risk_level_cat_day_1 = self.determine_highest_risk_level_cat(outlook_data_cat_day_1)
            
            outlook_data_tor_day_1 = fetch.tor(1)
            highest_risk_level_tor_day_1 = self.determine_highest_risk_level_tor(outlook_data_tor_day_1)

            outlook_data_wind_day_1 = fetch.wind(1)
            highest_risk_level_wind_day_1 = self.determine_highest_risk_level_wind(outlook_data_wind_day_1)

            outlook_data_hail_day_1 = fetch.hail(1)
            highest_risk_level_hail_day_1 = self.determine_highest_risk_level_hail(outlook_data_hail_day_1)

            self.side_bar()
            
            # Day 1 Button
            D1_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 1',width=200, corner_radius=12, fg_color='transparent',
                                   font=('karla', 26), command=lambda: self.frame_change(1),
                                   state='disabled', image=self.tornado_icon)
            D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

            # Close Button
            Close_Button = ctk.CTkButton(self.main_frame, text='Close', width=200, font=self.Description_Font, command=self.close_program)
            Close_Button.grid(row=1, column=3, padx=20, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(self.main_frame, text='Hide', width=200, font=self.Description_Font, command=self.hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 1 Heading Label
            D1_Label = ctk.CTkLabel(self.main_frame, text='Day 1 Outlooks', font=self.Title_Font)
            D1_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 1 Categorical Button
            D1_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 1 Categorical', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('cat', 1))
            D1_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Categorial Risk Label
            highest_risk_label_cat_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_1}', font=('karla', 25))
            highest_risk_label_cat_day_1.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 1 Tornado Button
            D1_Tor_Button = ctk.CTkButton(self.main_frame, text='Day 1 Tornado', width = 150, height=50, font=('karla', 28), command=lambda: self.button_run('tor', 1))
            D1_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Tornado Risk Label
            highest_risk_label_tor_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_1}', font=('karla', 25))
            highest_risk_label_tor_day_1.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 1 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(self.main_frame, text='Day 1 Wind', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('wind', 1))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_1}', font=('karla', 25))
            highest_risk_label_wind_day_1.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 1 Hail Outlook
            D1_Hail_Button = ctk.CTkButton(self.main_frame, text='Day 1 Hail', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('hail', 1))
            D1_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Hail Risk Label
            highest_risk_label_hail_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_1}', font=('karla', 25))
            highest_risk_label_hail_day_1.grid(row=6, column=2, columnspan=1, sticky='nsew')
        elif day == 2:
            outlook_data_cat_day_2 = fetch.cat(2)
            highest_risk_level_cat_day_2 = self.determine_highest_risk_level_cat(outlook_data_cat_day_2)
            
            outlook_data_tor_day_2 = fetch.tor(2)
            highest_risk_level_tor_day_2 = self.determine_highest_risk_level_tor(outlook_data_tor_day_2)

            outlook_data_wind_day_2 = fetch.wind(2)
            highest_risk_level_wind_day_2 = self.determine_highest_risk_level_wind(outlook_data_wind_day_2)

            outlook_data_hail_day_2 = fetch.hail(2)
            highest_risk_level_hail_day_2 = self.determine_highest_risk_level_hail(outlook_data_hail_day_2)

            self.side_bar()
            
            # Day 2 Button
            D2_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 2',width=200, corner_radius=12, fg_color='transparent',
                                   font=('karla', 26), command=lambda: self.frame_change(2),
                                   state='disabled', image=self.tornado_icon)
            D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(self.main_frame, text='Close', width=200, font=self.Description_Font, command=self.close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(self.main_frame, text='Hide', width=200, font=self.Description_Font, command=self.hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 2 Heading Label
            D2_Label = ctk.CTkLabel(self.main_frame, text='Day 2 Outlooks', font=self.Title_Font)
            D2_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 2 Categorical Button
            D2_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 2 Categorical', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('cat', 2))
            D2_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Categorial Risk Label
            highest_risk_label_cat_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_2}', font=('karla', 25))
            highest_risk_label_cat_day_2.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 2 Tornado Button
            D2_Tor_Button = ctk.CTkButton(self.main_frame, text='Day 2 Tornado', width = 150, height=50, font=('karla', 28), command=lambda: self.button_run('tor', 2))
            D2_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Tornado Risk Label
            highest_risk_label_tor_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_2}', font=('karla', 25))
            highest_risk_label_tor_day_2.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 2 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(self.main_frame, text='Day 2 Wind', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('wind', 2))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Wind Risk Label
            highest_risk_label_wind_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_2}', font=('karla', 25))
            highest_risk_label_wind_day_2.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 2 Hail Outlook
            D2_Hail_Button = ctk.CTkButton(self.main_frame, text='Day 2 Hail', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('hail', 2))
            D2_Hail_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Hail Risk Label
            highest_risk_label_hail_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_hail_day_2}', font=('karla', 25))
            highest_risk_label_hail_day_2.grid(row=6, column=2, columnspan=1, sticky='nsew')
        elif day == 3:
            outlook_data_cat_day_3 = fetch.cat(3)
            highest_risk_level_cat_day_3 = self.determine_highest_risk_level_cat(outlook_data_cat_day_3)

            outlook_data_prob_day_3 = fetch.prob(3)
            highest_risk_level_prob_day_3 = self.determine_highest_risk_level_prob(outlook_data_prob_day_3)
            
            self.side_bar()

            #Day 3 Button
            D3_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 3',width=200, corner_radius=12, fg_color='transparent', 
                                   font=('karla', 26), command=lambda: self.frame_change(3),
                                   state='disabled', image=self.lightning_icon)
            D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(self.main_frame, text='Close', width=200, font=self.Description_Font, command=self.close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(self.main_frame, text='Hide', width=200, font=self.Description_Font, command=self.hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 3 Heading Label
            D3_Label = ctk.CTkLabel(self.main_frame, text='Day 3 Outlooks', font=self.Title_Font)
            D3_Label.grid(row=2, column=1, columnspan=2, padx=435, pady=50, sticky='nsew')

            # Day 3 Categorical Button
            D3_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 3 Categorical', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('cat', 3))
            D3_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Categorial Risk Label
            highest_risk_label_cat_day_3 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_3}', font=('karla', 25))
            highest_risk_label_cat_day_3.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 3 Probabilistic Outlook
            D3_Prob_Button = ctk.CTkButton(self.main_frame, text='Day 3 Probabilistic', width=150, height=50, font=('karla', 28), command=lambda: self.button_run('prob', 3))
            D3_Prob_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Probabilistic Risk Label
            highest_risk_label_prob_day_3 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_prob_day_3}', font=('karla', 25))
            highest_risk_label_prob_day_3.grid(row=4, column=2, columnspan=1, sticky='nsew')
        elif day == 'd4-8':
            outlook_data_d48_day_4 = fetch.d48(4)
            highest_risk_level_d48_day_4 = self.determine_highest_risk_level_d48(outlook_data_d48_day_4)
            
            outlook_data_d48_day_5 = fetch.d48(5)
            highest_risk_level_d48_day_5 = self.determine_highest_risk_level_d48(outlook_data_d48_day_5)

            outlook_data_d48_day_6 = fetch.d48(6)
            highest_risk_level_d48_day_6 = self.determine_highest_risk_level_d48(outlook_data_d48_day_6)

            outlook_data_d48_day_7 = fetch.d48(7)
            highest_risk_level_d48_day_7 = self.determine_highest_risk_level_d48(outlook_data_d48_day_7)

            outlook_data_d48_day_8 = fetch.d48(8)
            highest_risk_level_d48_day_8 = self.determine_highest_risk_level_d48(outlook_data_d48_day_8)

            self.side_bar()
            
            # Day 4-8 Button
            D48_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 4-8', width=200, corner_radius=12, fg_color='transparent', 
                                    font=self.Description_Font, command=lambda: self.frame_change('d4-8'),
                                    state='disabled', image=self.lightning_icon)
            D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)
            
            # Close Button
            Close_Button = ctk.CTkButton(self.main_frame, text='Close', width=200, font=self.Description_Font, command=self.close_program)
            Close_Button.grid(row=1, column=3, padx=15, pady=15, sticky='e')

            # Hide_Button
            Hide_Button = ctk.CTkButton(self.main_frame, text='Hide', width=200, font=self.Description_Font, command=self.hide_to_system_tray)
            Hide_Button.grid(row=1, column=2, padx=25, pady=15, sticky='e')

            # Day 4-8 Heading Label
            D48_Label = ctk.CTkLabel(self.main_frame, text='Day 4-8 Outlooks', font=self.Title_Font)
            D48_Label.grid(row=2, column=1, columnspan=2, padx=400, pady=50, sticky='nsew')

            # Day 4 Button
            D4_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 4 Outlook', font=('karla', 28), height=50, command=lambda: self.button_run('d4-8', 4))
            D4_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 4 Probabilistic Risk Label
            highest_risk_label_d48_day_4 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_4}', font=('karla', 25))
            highest_risk_label_d48_day_4.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 5 Button
            D5_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 5 Outlook', font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 5))
            D5_Cat_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 5 Probabilistic Risk Label
            highest_risk_label_d48_day_5 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_5}', font=('karla', 25))
            highest_risk_label_d48_day_5.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 6 Button
            D6_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 6 Outlook', font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 6))
            D6_Cat_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 6 Probabilistic Risk Label
            highest_risk_label_d48_day_6 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_6}', font=('karla', 25))
            highest_risk_label_d48_day_6.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 7 Button
            D7_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 7 Outlook', font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 7))
            D7_Cat_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 7 Probabilistic Risk Label
            highest_risk_label_d48_day_7 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_7}', font=('karla', 25))
            highest_risk_label_d48_day_7.grid(row=6, column=2, columnspan=1, sticky='nsew')

            # Day 8 Button
            D8_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 8 Outlook', font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 8))
            D8_Cat_Button.grid(row=7, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 8 Probabilistic Risk Label
            highest_risk_label_d48_day_8 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_8}', font=('karla', 25))
            highest_risk_label_d48_day_8.grid(row=7, column=2, columnspan=1, sticky='nsew')
        else:
            log.error(f'Invalid Button. Day = {day}. Error on line 1305')
            self.popup('error', 'Invalid Button', "An error has occured where the button isn't programmed correctly. The program will now quit.")
            sys.exit(0)
gui = GUI()
class RUN:
    def __init__(self):
        self.instance = 0
        self.log_directory = 'C:\\log'

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

    def run_program(self, outlook_type, day, window):
        log.info(f'Running outlook {outlook_type} for day {day}')

        outlook_data = getattr(fetch, outlook_type)(day)
        
        if fetch.check_outlook_availability(outlook_data):
            if self.instance == 0:
                self.popup('info', 'Program is Running', 'The Severe Weather Outlook Display is now running. The program may take some time to load so be patient. Click "Ok" or Close the Window to Continue')
                self.instance = 1
            
            window.withdraw()
            getattr(display, outlook_type)(day, gui.run_gui, outlook_data)
        else:
            self.popup('warning', 'No Outlook Available', f'There is no {outlook_type} outlook available for day {day}.')
            gui.run_gui()

        if outlook_type not in ['cat', 'tor', 'wind', 'hail', 'd4-8', 'prob']:
            log.error(f'Invalid Outlook Type. Outlook Type = {outlook_type}')
            self.popup('error', 'Invalid Outlook Type', "An error has occurred where the outlook type wasn't read correctly. The program will now quit.")
            sys.exit(0)
    
    def startup(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
    
        log.basicConfig(
            level = log.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='C:\\log\\cod.log',
            filemode='w'
        )

        rss_feed_thread = threading.Thread(target=monitor.rss)
        rss_feed_thread.daemon = True
        rss_feed_thread.start()

gui = GUI()
run = RUN()