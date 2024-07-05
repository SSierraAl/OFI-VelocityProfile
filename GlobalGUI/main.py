# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
from gui.uis.windows.main_window.functions_main_window import *
import sys
import os

# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from qt_core import *
# IMPORT SETTINGS
# ///////////////////////////////////////////////////////////////
from gui.core.json_settings import Settings
# IMPORT PY ONE DARK WINDOWS
# ///////////////////////////////////////////////////////////////
# MAIN WINDOW
from gui.uis.windows.main_window import *
# IMPORT PY ONE DARK WIDGETS
# ///////////////////////////////////////////////////////////////
from gui.widgets import *
# ADJUST QT FONT DPI FOR HIGHT SCALE AN 4K MONITOR
# ///////////////////////////////////////////////////////////////
os.environ["QT_FONT_DPI"] = "96"
# IF IS 4K MONITOR ENABLE 'os.environ["QT_SCALE_FACTOR"] = "2"'

from random import randint

from TAB_ZaberFunctions import *
from TAB_Home_Read import *
from DAQ_Reader_Global import *
from TAB_Scanning import *
from TAB_Server import *

import pyqtgraph as pg
import sys
from PySide6.QtCore import QTimer
import keyboard

import subprocess as sp
from queue import Queue
# Shared data structure server and app
shared_queue = Queue()
# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    """ Class for setting up window GUI interface
    """
    def __init__(self):
        super().__init__()

        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        settings = Settings()
        self.settings = settings.items

        # SETUP MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.hide_grips = True # Show/Hide resize grips
        SetupMainWindow.setup_gui(self)

        # ZABER TAB
        # ///////////////////////////////////////////////////////////////
        InitializeZaber(self)

        # SET DAQ ACQUISIITON
        # ///////////////////////////////////////////////////////////////
        Set_DAQ_Functions(self)


        # SET HOME TAB
        # ///////////////////////////////////////////////////////////////
        InsertHomeGraphs(self)

        # SET SCANNING TAB
        # ///////////////////////////////////////////////////////////////
        self.scan_functions_instance = Scan_functions(self)
        Set_Scanning_Tab(self, self.scan_functions_instance) #TODO: the scan_functions_instance of self can be used within the set_scanning_tab now, without having to pass it as an argument.

        # SET SERVER TAB
        # ///////////////////////////////////////////////////////////////
        self.Server_Instance = Server_Init_Bokeh(self, shared_queue)


        # ///////////////////////////////////////////////////////////////
        # SHOW MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.show()
    


    # LEFT MENU BTN IS CLICKED
    # Run function when btn is clicked
    # Check funtion by object name / btn_id
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self)

        # Remove Selection If Clicked By "btn_close_left_column"
        if btn.objectName() != "btn_settings":
            self.ui.left_menu.deselect_all_tab()
        # LEFT MENU
        # ///////////////////////////////////////////////////////////////
        
        # HOME BTN
        if btn.objectName() == "btn_home": #display home page
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            MainFunctions.set_page(self, self.ui.load_pages.page_1)


        # CALIBRATION BTN
        if btn.objectName() == "btn_search":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            MainFunctions.set_page(self, self.ui.load_pages.page_calib)

        # SERVER CONECTION
        # ///////////////////////////////////////////////////////////////
        if btn.objectName() == "btn_server":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            MainFunctions.set_page(self, self.ui.load_pages.page_2)


        # ZABER CONECTION BTN
        # ///////////////////////////////////////////////////////////////
        if btn.objectName() == "btn_zaber":
            # Select Menu
            self.ui.left_menu.select_only_one(btn.objectName())
            MainFunctions.set_page(self, self.ui.load_pages.page_3)



    # LEFT MENU BTN IS RELEASED
    # Run function when btn is released
    # Check funtion by object name / btn_id
    # ///////////////////////////////////////////////////////////////
    def btn_released(self):
        # GET BT CLICKED
        btn = SetupMainWindow.setup_btns(self)
        # DEBUG
        print(f"Button {btn.objectName()}, released!")

    # RESIZE EVENT
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        SetupMainWindow.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()


    # BOKEH SERVER
    # ///////////////////////////////////////////////////////////////
    def closeEvent(self, event):
        #Override function to stop the thread at the same time that the app is closed
        Server_Init_Bokeh.stop_thread(self.Server_Instance)
        event.accept()


# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # APPLICATION
    # ///////////////////////////////////////////////////////////////
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()

    # EXEC APP
    # ///////////////////////////////////////////////////////////////
    sys.exit(app.exec_())