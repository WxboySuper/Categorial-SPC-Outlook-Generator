# Outlook Display
# Created by WeatherboySuper
# Created with WeatherTrackUS

# Imports
import os
import matplotlib
import customtkinter as ctk
import sys
import logging as log
import pystray
import threading

import OutlookMonitoring
import OutlookProcessing

from tkinter import messagebox
from PIL import Image

matplotlib.use('TkAgg')

monitor = OutlookMonitoring.monitor()
fetch = OutlookMonitoring.fetch()

display = OutlookProcessing.display()


class GUI:
    """
    Represents the graphical user interface (GUI) class for the severe weather outlook program.

    This class is responsible for initializing and running the GUI, setting up various attributes and icons,
    and mapping risk levels to integers.

    Attributes:
        _instance (GUI): The singleton instance of the GUI class.
        current_directory (str): The directory of the current file.
        tornado_icon (CTkImage): The tornado icon image.
        home_icon (CTkImage): The home icon image.
        lightning_icon (CTkImage): The lightning icon image.

    Methods:
        __init__(): Initializes a new instance of the GUI class.
    """

    _instance = None

    def __init__(self):
        """
        Initializes a new instance of the GUI class.

        This method initializes the GUI class and sets up various attributes and icons. It sets the current directory to the directory of the current file using `os.path.dirname(os.path.abspath(__file__))`. It then sets the paths for the icons using `os.path.join` and loads the images using `Image.open`. The images are then used to create `CTkImage` objects with the specified size.

        The method also sets up several dictionaries for mapping risk levels to integers. These dictionaries map different values to corresponding integer values.

        If the instance of the GUI class does not exist, a new instance is created and assigned to `GUI._instance`. Otherwise, the existing instance is assigned to `self`.

        Parameters:
            None

        Returns:
            None
        """
        self.current_directory = os.path.dirname(os.path.abspath(__file__))

        self.tornado_icon_path = os.path.join(self.current_directory, '../files/icons/Tornado.png')
        self.tornado_icon = ctk.CTkImage(dark_image=Image.open(self.tornado_icon_path), 
                                         light_image=Image.open(self.tornado_icon_path), 
                                         size=(50, 40))
        self.home_icon_path = os.path.join(self.current_directory, '../files/icons/Home.png')
        self.home_icon = ctk.CTkImage(dark_image=Image.open(self.home_icon_path), 
                                      light_image=Image.open(self.home_icon_path), 
                                      size=(50, 40))
        self.lightning_icon_path = os.path.join(self.current_directory, '../files/icons/Lightning.png')
        self.lightning_icon = ctk.CTkImage(dark_image=Image.open(self.lightning_icon_path), 
                                           light_image=Image.open(self.lightning_icon_path), 
                                           size=(50, 40))
        self.logo_icon_path = os.path.join(self.current_directory, '../files/icons/My_project.png')
        self.logo_icon = ctk.CTkImage(dark_image=Image.open(self.logo_icon_path), 
                                      light_image=Image.open(self.logo_icon_path), 
                                      size=(120, 120))

        self.risk_level_mapping_cat = {
            'TSTM': 1,  # Thunderstorm
            'MRGL': 2,  # Marginal
            'SLGT': 3,  # Slight
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
        else:
            self = GUI._instance

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
            return self.question  # skipcq: PYL-R1710
        else:
            messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup. The program will now quit.')
            sys.exit(0)

    def run_gui(self):
        """
        This function initializes and runs the graphical user interface (GUI) of the Severe Weather Outlook Display application.

        It sets up the main window, configures the layout, defines the fonts and frames, and starts the main event loop.

        Parameters:
            self (object): A reference to the current instance of the class.

        Returns:
            None
        """
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
        """
        This function changes the frame of the GUI based on the provided day.

        It destroys all the widgets in the main frame and then calls the frames function to recreate the frame for the specified day.

        Parameters:
            self (object): A reference to the current instance of the class.
            day (int): The day for which the frame needs to be changed.

        Returns:
            None
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.frames(day)

    def button_run(self, outlook_type, day):
        """
        This function handles the button press event for running a specific outlook type for a given day.

        It logs the event, hides the current window, and then runs the specified outlook program.

        Parameters:
            self (object): A reference to the current instance of the class.
            outlook_type (str): The type of outlook to be run.
            day (int): The day for which the outlook needs to be run.

        Returns:
            None
        """
        log.info(f'GUI - {type} {day} button has been pressed. Running Day {day} {type} outlook')
        self.window.withdraw()
        run.run_program(outlook_type, day, self.window)

    def show_from_system_tray(self, logo_icon_tray, item):
        """
        Shows the application window from the system tray.

        Parameters:
            self (object): A reference to the current instance of the class.
            icon: The system tray icon object.
            item: The item that triggered this function call.

        Returns:
            None
        """
        logo_icon_tray.stop()
        self.window.deiconify()

    def hide_to_system_tray(self):
        """
        Hides the application window to the system tray.

        Parameters:
            self (object): A reference to the current instance of the class.

        Returns:
            None
        """
        global icon
        self.window.withdraw()
        image = Image.open('../files/icons/My_project.png')
        menu = (pystray.MenuItem("Show", self.show_from_system_tray), pystray.MenuItem("Exit", self.close_program))
        icon = pystray.Icon("name", image, "My System Tray Icon", menu)
        icon.run()

    def close_program(self):
        """
        This function closes the program after prompting the user for confirmation.

        It displays a popup asking the user if they want to close the program,
        and if the user responds with 'yes', it stops the system tray icon, withdraws the main window,
        and exits the program.

        Parameters:
            self (object): A reference to the current instance of the class.

        Returns:
            None
        """
        global question  # Declare question as a global variable
        log.info('GUI - Now Closing Program')
        self.popup('question', 'Close Program?',
                   'Are you sure you want to close the program? You will not receive notifications for new outlooks when the program is closed. Use "Hide" instead to hide the program and still receive new outlook notifications!')  # skipcq: FLK-E501
        if self.question == 'yes':
            if 'icon' in globals() and icon is not None:
                icon.stop() 
            self.window.withdraw() 
            os._exit(0)
        else:
            return

    def side_bar(self):
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
            self (object): A reference to the current instance of the class.

        Returns:
            None
        """
        """ Sidebar Buttons """
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
        D1_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 1', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: self.frame_change(1),
                                       hover_color='#2191aa', image=self.tornado_icon)
        D1_Side_Button.grid(row=2, column=0, columnspan=1, padx=5, pady=10)

        # Day 2 Button
        D2_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 2', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: self.frame_change(2),
                                       hover_color='#2191aa', image=self.tornado_icon)
        D2_Side_Button.grid(row=3, column=0, columnspan=1, padx=5, pady=10)

        # Day 3 Button
        D3_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 3', width=200, corner_radius=12, fg_color='transparent',
                                       font=('karla', 26), command=lambda: self.frame_change(3),
                                       hover_color='#2191aa', image=self.lightning_icon)
        D3_Side_Button.grid(row=4, column=0, columnspan=1, padx=5, pady=10)

        # Day 4-8 Button
        D48_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 4-8', width=200, corner_radius=12, fg_color='transparent',
                                        font=self.Description_Font, command=lambda: self.frame_change('d4-8'),
                                        hover_color='#2191aa', image=self.lightning_icon)
        D48_Side_Button.grid(row=5, column=0, columnspan=1, padx=5, pady=10)

    def determine_highest_risk_level_cat(self, outlook_data):
        """
        Determines the highest risk level category for severe weather from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level category.

        Raises:
            None.
        """
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
        """
        Determines the highest risk level for tornadoes from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for tornadoes as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        Determines the highest risk level for wind from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for wind as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        Determines the highest risk level for hail from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for hail as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        Determines the highest risk level for a 4-8 day outlook from the given outlook data.

        Args:
            outlook_data (dict): The outlook data containing the features.

        Returns:
            str: The highest risk level for the 48-hour period as a string, or 'None' if no risk level is found.

        Raises:
            None.
        """
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
        """
        This function handles the creation of frames for different days of severe weather outlooks.

        It takes a 'day' parameter which determines which day's outlook to display.
        The function then creates the necessary buttons and labels for that day's outlook.

        The function does not return any values.

        Parameters:
        day (str or int): The day of the severe weather outlook to display. Can be 'home', 1, 2, 3, or 'd4-8'.

        Returns:
        None
        """
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
            Welcome_Label = ctk.CTkLabel(self.main_frame,
                                         text='Welcome to the Severe Weather Outlook Display! Press a button below to find a outlook to dispaly.',
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
            D1_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 1', width=200, corner_radius=12, fg_color='transparent',
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
            D1_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 1 Categorical', width=150, height=50,
                                          font=('karla', 28), command=lambda: self.button_run('cat', 1))
            D1_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Categorial Risk Label
            highest_risk_label_cat_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_1}', font=('karla', 25))
            highest_risk_label_cat_day_1.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 1 Tornado Button
            D1_Tor_Button = ctk.CTkButton(self.main_frame, text='Day 1 Tornado', width=150, height=50,
                                          font=('karla', 28), command=lambda: self.button_run('tor', 1))
            D1_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Tornado Risk Label
            highest_risk_label_tor_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_1}', font=('karla', 25))
            highest_risk_label_tor_day_1.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 1 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(self.main_frame, text='Day 1 Wind', width=150, height=50,
                                           font=('karla', 28), command=lambda: self.button_run('wind', 1))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 1 Wind Risk Label
            highest_risk_label_wind_day_1 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_1}', font=('karla', 25))
            highest_risk_label_wind_day_1.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 1 Hail Outlook
            D1_Hail_Button = ctk.CTkButton(self.main_frame, text='Day 1 Hail', width=150, height=50,
                                           font=('karla', 28), command=lambda: self.button_run('hail', 1))
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
            D2_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 2', width=200, corner_radius=12, fg_color='transparent',
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
            D2_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 2 Categorical', width=150, height=50,
                                          font=('karla', 28), command=lambda: self.button_run('cat', 2))
            D2_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Categorial Risk Label
            highest_risk_label_cat_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_2}', font=('karla', 25))
            highest_risk_label_cat_day_2.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 2 Tornado Button
            D2_Tor_Button = ctk.CTkButton(self.main_frame, text='Day 2 Tornado', width=150, height=50,
                                          font=('karla', 28), command=lambda: self.button_run('tor', 2))
            D2_Tor_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Tornado Risk Label
            highest_risk_label_tor_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_tor_day_2}', font=('karla', 25))
            highest_risk_label_tor_day_2.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 2 Wind Outlook
            D1_Wind_Button = ctk.CTkButton(self.main_frame, text='Day 2 Wind', width=150, height=50,
                                           font=('karla', 28), command=lambda: self.button_run('wind', 2))
            D1_Wind_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 2 Wind Risk Label
            highest_risk_label_wind_day_2 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_wind_day_2}', font=('karla', 25))
            highest_risk_label_wind_day_2.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 2 Hail Outlook
            D2_Hail_Button = ctk.CTkButton(self.main_frame, text='Day 2 Hail', width=150, height=50,
                                           font=('karla', 28), command=lambda: self.button_run('hail', 2))
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

            # Day 3 Button
            D3_Side_Button = ctk.CTkButton(self.sidebar_frame, text='Day 3', width=200, corner_radius=12, fg_color='transparent',
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
            D3_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 3 Categorical',
                                          width=150, height=50, font=('karla', 28), command=lambda: self.button_run('cat', 3))
            D3_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=30, sticky='nsew')

            # Day 3 Categorial Risk Label
            highest_risk_label_cat_day_3 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_cat_day_3}', font=('karla', 25))
            highest_risk_label_cat_day_3.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 3 Probabilistic Outlook
            D3_Prob_Button = ctk.CTkButton(self.main_frame, text='Day 3 Probabilistic',
                                           width=150, height=50, font=('karla', 28), command=lambda: self.button_run('prob', 3))
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
            D4_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 4 Outlook',
                                          font=('karla', 28), height=50, command=lambda: self.button_run('d4-8', 4))
            D4_Cat_Button.grid(row=3, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 4 Probabilistic Risk Label
            highest_risk_label_d48_day_4 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_4}', font=('karla', 25))
            highest_risk_label_d48_day_4.grid(row=3, column=2, columnspan=1, sticky='nsew')

            # Day 5 Button
            D5_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 5 Outlook',
                                          font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 5))
            D5_Cat_Button.grid(row=4, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 5 Probabilistic Risk Label
            highest_risk_label_d48_day_5 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_5}', font=('karla', 25))
            highest_risk_label_d48_day_5.grid(row=4, column=2, columnspan=1, sticky='nsew')

            # Day 6 Button
            D6_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 6 Outlook',
                                          font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 6))
            D6_Cat_Button.grid(row=5, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 6 Probabilistic Risk Label
            highest_risk_label_d48_day_6 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_6}', font=('karla', 25))
            highest_risk_label_d48_day_6.grid(row=5, column=2, columnspan=1, sticky='nsew')

            # Day 7 Button
            D7_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 7 Outlook',
                                          font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 7))
            D7_Cat_Button.grid(row=6, column=1, columnspan=1, padx=25, pady=20, sticky='nsew')

            # Day 7 Probabilistic Risk Label
            highest_risk_label_d48_day_7 = ctk.CTkLabel(self.main_frame, text=f'Highest Risk: {highest_risk_level_d48_day_7}', font=('karla', 25))
            highest_risk_label_d48_day_7.grid(row=6, column=2, columnspan=1, sticky='nsew')

            # Day 8 Button
            D8_Cat_Button = ctk.CTkButton(self.main_frame, text='Day 8 Outlook',
                                          font=('karla', 28), width=150, height=50, command=lambda: self.button_run('d4-8', 8))
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
    """
    Represents the main execution class for the severe weather outlook program.

    This class is responsible for initializing the program's state and log directory.
    It provides methods for running the program, displaying popups, and logging events.

    Attributes:
        instance (int): The instance number of the program.
        log_directory (str): The directory where log files are stored.

    Methods:
        __init__(): Initializes a new instance of the RUN class.
        popup(type, title, message): Displays a popup dialog box with the specified type, title, and message.
        run_program(outlook_type, day, window): Runs the severe weather outlook program for the specified outlook type and day.
    """

    def __init__(self):
        """
        Initializes a new instance of the RUN class.

        Sets the initial state of the instance and log directory.

        Parameters:
        None

        Returns:
        None
        """
        self.instance = 0
        self.log_directory = 'C:\\log'

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
            return self.question  # skipcq: PYL-R1710
        else:
            messagebox.showerror('Invalid Popup', 'There was an error when trying to display a popup. The program will now quit.')
            sys.exit(0)

    def run_program(self, outlook_type, day, window):
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
        log.info(f'Running outlook {outlook_type} for day {day}')

        outlook_data = getattr(fetch, outlook_type)(day)

        if fetch.check_outlook_availability(outlook_data):
            if self.instance == 0:
                self.popup('info', 'Program is Running',
                           'The Severe Weather Outlook Display is now running. The program may take some time to load so be patient. Click "Ok" or Close the Window to Continue')  # skipcq: FLK-E501
                self.instance = 1

            window.withdraw()
            getattr(display, outlook_type)(day, gui.run_gui, outlook_data)
        else:
            self.popup('warning', 'No Outlook Available', f'There is no {outlook_type} outlook available for day {day}.')
            gui.run_gui()

        if outlook_type not in ['cat', 'tor', 'wind', 'hail', 'd4-8', 'prob']:
            log.error(f'Invalid Outlook Type. Outlook Type = {outlook_type}')
            self.popup('error', 'Invalid Outlook Type',
                       "An error has occurred where the outlook type wasn't read correctly. The program will now quit.")
            sys.exit(0)

    def startup(self):
        """
        Initializes the application by setting up the log directory and starting the RSS feed monitoring thread.

        Parameters:
        None

        Returns:
        None
        """
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        log.basicConfig(
            level=log.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='C:\\log\\cod.log',
            filemode='w'
        )

        rss_feed_thread = threading.Thread(target=monitor.rss)
        rss_feed_thread.daemon = True
        rss_feed_thread.start()


gui = GUI()
run = RUN()
