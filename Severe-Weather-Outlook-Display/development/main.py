import OutlookDisplay

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

display = OutlookDisplay.RUN()
gui = OutlookDisplay.GUI()

display.startup()
gui.run_gui()
