"""TAB_Scanning.py is responsible for the movement of the Zaber and
the data processing of the laser measurements, including the flow velocity profile
"""

from Frequency_Func import *
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel,QVBoxLayout,QGraphicsView
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor

import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode

import DAQ_Reader_Global # Import for use of stop_daq() function

    ###################################################################
    ###################################################################
    #Graphic Widget
class ColorGrid(QWidget):
    def __init__(self, g_W, g_H, cell_size):
        super().__init__()
        self.g_W = g_W
        self.g_H = g_H
        self.cell_size = cell_size

        # Matrix to export CSV data
        self.CSV_Moments_M0_Matrix=np.zeros((self.g_W,self.g_H))
        self.CSV_Moments_M1_Matrix=np.zeros((self.g_W,self.g_H))
        self.CSV_Moments_Matrix=np.zeros((self.g_W,self.g_H))

        # Create PlotItem and add it to the GraphicsLayout
        self.graphicsView = pg.GraphicsView()
        self.graphicsView.setBackgroundBrush(QColor('white'))
        self.graphicsLayout = pg.GraphicsLayout()
        self.graphicsView.setCentralItem(self.graphicsLayout)

        # Create PlotItem and add it to the GraphicsLayout
        self.plotItem = self.graphicsLayout.addPlot()
        self.plotItem.showGrid(x=True, y=True)
        self.plotItem.setRange(xRange=(0, self.g_W), yRange=(0, self.g_H), padding=0)
        
        # Create the ImageItem and add it to the PlotItem
        self.imageItem = pg.ImageItem()
        self.plotItem.addItem(self.imageItem)
        self.plotItem.getViewBox().setBackgroundColor('w')
        self.gridArray = np.ones((self.g_H, self.g_W, 3), dtype=np.uint8)*255

        # Configure the design
        layout = QVBoxLayout(self)
        layout.addWidget(self.graphicsView)

        self.timer_Calib_Scan = QTimer(self)
        self.timer_Calib_Scan.setInterval(1000)  # Intervalo en milisegundos
        self.timer_Calib_Scan.timeout.connect(self.updatePixel)
        # Variables for traversing pixels
        self.current_row = 0
        self.current_col = 0


    def updatePixel(self):

        # Change the colour of the current pixel
        self.gridArray[self.current_row, self.current_col] = [255, 0, 0]  # Red
        # Updating the image
        self.imageItem.setImage(self.gridArray, autoLevels=False)
        # Move to the next pixel
        self.current_col += 1
        if self.current_col >= self.g_W: # If end of row has been reached
            self.current_col = 0  # Reset column to beginning
            self.current_row += 1 # Go to next row
            if self.current_row >= self.g_H: # If last row has been reached
                self.current_row = 0  # Reset row


    def changeCellColor(self, row, col, color):
        self.gridArray[row, col] = color
        self.imageItem.setImage(self.gridArray, autoLevels=False)

    def Start_Grid_Scan(self):
        self.timer_Calib_Scan.start()

    def Stop_Grid_Scan(self):
        self.timer_Calib_Scan.stop()

    def update_white(self):
        self.gridArray = np.zeros((self.g_H, self.g_W, 3), dtype=np.uint8)*255
        self.imageItem.setImage(self.gridArray, autoLevels=False)

    ### Export CSV functions
    def updateCSV(self, row, col, Moment, M0, M1):
        self.CSV_Moments_Matrix[row, col] = Moment
        self.CSV_Moments_M0_Matrix[row, col] = M0
        self.CSV_Moments_M1_Matrix[row, col] = M1


    def exportar_Matrix_CSV(self):
        df = pd.DataFrame(self.CSV_Moments_Matrix)
        df.to_csv('Scanning_Moments_CSV.csv', index=True)
        df = pd.DataFrame(self.CSV_Moments_M0_Matrix)
        df.to_csv('Scanning_Moments_M0_CSV.csv', index=True)
        df = pd.DataFrame(self.CSV_Moments_M1_Matrix)
        df.to_csv('Scanning_Moments_M1_CSV.csv', index=True)

    ###################################################################
    ###################################################################

class Scan_functions:
    def __init__(self, main_window):
        self.main_window = main_window
        
        # #Init
        # self.Pos_Y1_Scan = float(self.main_window.ui.load_pages.lineEdit_y1_scan.text())
        # self.Pos_Y2_Scan = float(self.main_window.ui.load_pages.lineEdit_y2_scan.text())
        # self.speed = float(self.main_window.ui.load_pages.lineEdit_speed_ums.text()) * 1000 * 1.6381 / 1.9843
        # self.time_timer_scan=0
        # self.cell_size = int(self.main_window.ui.load_pages.lineEdit_Pixel_size.text()) 
        
        # self.counter_Data_per_Pixel=0 # Used for keeping track of current pixel
        # self.current_col=0
        # self.current_row=0
        # self.New_Color= [255,255,255]
        # self.scanning_Finish=False
        # #Counter for the N. of average samples: 
        # self.Counter_DAQ_samples=0
        # self.PSD_Avg_Moment=0

        # Button connections
        self.main_window.ui.load_pages.Calib_Reset_Scan_but.clicked.connect(self.reset_refresh_scan)
        self.main_window.ui.load_pages.Stop_Y_but.clicked.connect(self.Stop_z1)
        self.main_window.ui.load_pages.Stop_x_but.clicked.connect(self.Stop_z2) # Button for stopping X
        self.main_window.ui.load_pages.continuous_scanX_but.clicked.connect(self.Scan_Continuos_X)
        self.main_window.ui.load_pages.continuous_scanY_but.clicked.connect(self.Scan_Continuos_Y)

    def reset_refresh_scan(self):
        '''Resets the grid for a new scan. Without this, a second grid will appear.
        
        CONDITIONS: grid must already be present, so a measurement must have already been performed.
        It gives an error otherwise, as it cannot adjust/delete what does not exist yet.
        '''
        # Check if color_grid_widget exists or not
        if not hasattr(self.main_window,'color_grid_widget'): # was self.main_window
            print("INFO: No grid to reset")
            return
        
        # The color_grid_widget is dynamically added, so pylint gives an error on the follow lines.
        # This error is disabled for the specific lines using the disable comments.
        self.main_window.color_grid_widget.update_white()
        self.main_window.color_grid_widget.Stop_Grid_Scan()
        self.main_window.ui.load_pages.Layout_table_Scan.removeWidget(self.main_window.color_grid_widget)
        print("INFO: Flow Velocity Profile grid reset for new scan")

    # Stop Zaber in Y orientation
    def Stop_z1(self):
        self.main_window.Pixel_Interval.stop()
        self.main_window.Pixel_Interval_X.stop()
        self.main_window.Adquisit_Timer.stop()
        with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
            connection.generic_command(1, CommandCode.STOP, 1)

    # Stop Zaber in X orientation
    def Stop_z2(self):
        self.main_window.Pixel_Interval.stop()
        self.main_window.Pixel_Interval_X.stop()
        self.main_window.Adquisit_Timer.stop()
        with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
            connection.generic_command(3, CommandCode.STOP, 1)
            
    def move_to_position(self, Zab,position):
        with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            device_list[Zab].move_absolute(position, Units.LENGTH_MICROMETRES)

    def get_current_position(self, Zab):
        with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            act_pos=device_list[Zab].get_position(Units.LENGTH_MICROMETRES)
            return act_pos

    # X-direction-scanning
    def start_continuous_movement_x(self):
        """Performs continous movement of Zaber NOTE: in X direction.
        Calculates time it takes to travel along entire distance and stops
        the saber when this time, and thus distance, have passed.
        """
        self.main_window.distance = abs(self.main_window.Pos_X2_Scan - self.main_window.Pos_X1_Scan)
        self.main_window.time_to_travel = (self.main_window.distance / float(self.main_window.ui.load_pages.lineEdit_speed_ums.text()))*1000 # Milliseconds
        self.main_window.cell_size = int(self.main_window.ui.load_pages.lineEdit_Pixel_size.text()) 
        self.main_window.time_timer_scan=((self.main_window.time_to_travel/(self.main_window.distance/self.main_window.cell_size)))

        try:
            with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
                connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int((((self.main_window.speed/1.55)/10)*1.6384/0.047625)))#/0.047625)) #speed in um/s
        except:
            self.start_continuous_movement_x() # What is the purpose of this? Why does the y direction function not have it?

        self.main_window.Pixel_Interval_X.setInterval(self.main_window.time_timer_scan)
        self.main_window.Pixel_Interval_X.start()
        self.main_window.Adquisit_Timer.start()
        
    # X-direction-scanning
    # #Initial_Move
    def check_position_and_start_X(self, Zab, reference_Zab):
        """Starts continuous movement along X if Zaber is in reference position
        Otherwise, give command to move to reference position.
        Args:
            Zab (_type_): _description_
            reference_Zab (_type_): _description_
        """
        if abs(self.get_current_position(Zab) - reference_Zab) < 10:
            self.start_continuous_movement_x()
        else:
            QTimer.singleShot(500, self.main_window.check_position_and_start_X(Zab,reference_Zab))

    # Y-direction-scanning
    def start_continuous_movement_y(self):
        """Performs continous movement of Zaber NOTE: in Y direction.
        Calculates time it takes to travel along entire distance and stops
        the saber when this time, and thus distance, have passed.
        """
        self.main_window.distance = abs(self.main_window.Pos_Y2_Scan - self.main_window.Pos_Y1_Scan)
        self.main_window.time_to_travel = (self.main_window.distance / float(self.main_window.ui.load_pages.lineEdit_speed_ums.text()))*1000 # Milliseconds
        self.main_window.cell_size = int(self.main_window.ui.load_pages.lineEdit_Pixel_size.text())
        self.main_window.time_timer_scan=((self.main_window.time_to_travel/(self.main_window.distance/self.main_window.cell_size)))

        with Connection.open_serial_port(self.main_window.Zaber_COM) as connection:
            connection.generic_command(1, CommandCode.MOVE_AT_CONSTANT_SPEED, int(self.main_window.speed))

        self.main_window.Pixel_Interval.setInterval(self.main_window.time_timer_scan)
        self.main_window.Pixel_Interval.start()
        self.main_window.Adquisit_Timer.start()
        
    # Y-direction-scanning
    #Initial_Move
    def check_position_and_start(self, Zab, reference_Zab):
        if abs(self.get_current_position(Zab) - reference_Zab) < 10:
            self.start_continuous_movement_y()
        else:
            QTimer.singleShot(500, self.main_window.check_position_and_start(Zab,reference_Zab))

        #Color pixel adjustment
    def interpolation_Color(self, oldcolor):
        """Adjusts the displayed color of flow velocity profile display 
        -(dark green, bright green etc.)
        The range of measurement value inputs (min_x, max_x) are converted to 
        the same ratio but from 0 to 255. This can then be used for colors
        
        NOTE: take care in defining these values, if all measured values are 
        lower than min_x, for example, you won't see any colors in the results.

        Args:
            oldcolor (integer): the average momentum measured by the laser

        Returns:
            newcolor (integer): the color value within a range of 0 to 255, 
            with the lowest input resulting in 255, and max input in 0.
        """
        min_x = 15000
        max_x = 37000
        min_y = 255
        max_y = 0
        newcolor = ((oldcolor - min_x) * (max_y - min_y) / (max_x - min_x)) + min_y
        return newcolor

    def Scan_Continuos_X(self):
        # Reset grid so there won't be 2 grids if there's already a grid with previous measurements
        if hasattr(self.main_window,'color_grid_widget'):
            self.reset_refresh_scan()
        
        #Update GUI Information
        self.main_window.speed = float(self.main_window.ui.load_pages.lineEdit_speed_ums.text())# / ((1.6381 / 1.9843))
        self.main_window.Pos_Y1_Scan = float(self.main_window.ui.load_pages.lineEdit_y1_scan.text())
        self.main_window.Pos_Y2_Scan = float(self.main_window.ui.load_pages.lineEdit_y2_scan.text())
        self.main_window.Pos_X1_Scan = float(self.main_window.ui.load_pages.lineEdit_x1_scan.text())
        self.main_window.Pos_X2_Scan = float(self.main_window.ui.load_pages.lineEdit_x2_scan.text())
        self.main_window.cell_size = int(self.main_window.ui.load_pages.lineEdit_Pixel_size.text())
        
        #Update everything
        self.main_window.g_W=int((self.main_window.Pos_X2_Scan-self.main_window.Pos_X1_Scan)/self.main_window.cell_size)
        self.main_window.g_H=int((self.main_window.Pos_Y2_Scan-self.main_window.Pos_Y1_Scan)/self.main_window.cell_size)
        
        #Create Graph
        self.main_window.color_grid_widget = ColorGrid(self.main_window.g_H,self.main_window.g_W,self.main_window.cell_size)
        self.main_window.ui.load_pages.Layout_table_Scan.addWidget(self.main_window.color_grid_widget)
        
        # Variables_Initialization
        self.main_window.counter_Data_per_Pixel=0
        self.main_window.counter_Step_Zaber_X=0
        self.main_window.current_col=0
        self.main_window.current_row=0
        self.main_window.New_Color= [255,255,255]

        # Average dev flow rate
        self.main_window.Moment_Dev=pd.DataFrame()
        self.main_window.Samples_to_AVG=0
        self.main_window.Samples_To_AVG_Flag=True
        # Move first to (X1,Y1)
        self.move_to_position(0,self.main_window.Pos_Y1_Scan)
        self.move_to_position(2,self.main_window.Pos_X1_Scan)
        self.check_position_and_start_X(2,self.main_window.Pos_X1_Scan)

    def Scan_Continuos_Y(self):
        # Reset grid so there won't be 2 grids if there's already a grid with previous measurements
        if hasattr(self,'color_grid_widget'):
            self.reset_refresh_scan()
            
        #Update GUI Information
        self.main_window.speed = float(self.main_window.ui.load_pages.lineEdit_speed_ums.text()) / ((1.6381 / 1.9843))
        self.main_window.Pos_Y1_Scan = float(self.main_window.ui.load_pages.lineEdit_y1_scan.text())
        self.main_window.Pos_Y2_Scan = float(self.main_window.ui.load_pages.lineEdit_y2_scan.text())
        self.main_window.Pos_X1_Scan = float(self.main_window.ui.load_pages.lineEdit_x1_scan.text())
        self.main_window.Pos_X2_Scan = float(self.main_window.ui.load_pages.lineEdit_x2_scan.text())
        self.main_window.cell_size = int(self.main_window.ui.load_pages.lineEdit_Pixel_size.text())
        #Update everything
        self.main_window.g_W=int((self.main_window.Pos_X2_Scan-self.main_window.Pos_X1_Scan)/self.main_window.cell_size)
        self.main_window.g_H=int((self.main_window.Pos_Y2_Scan-self.main_window.Pos_Y1_Scan)/self.main_window.cell_size)
        #Create Graph
        self.main_window.color_grid_widget = ColorGrid(self.main_window.g_H,self.main_window.g_W,self.main_window.cell_size)
        self.main_window.ui.load_pages.Layout_table_Scan.addWidget(self.main_window.color_grid_widget)
        # Variables_Initialization
        self.main_window.counter_Data_per_Pixel=0 # used for determining current pixel
        self.main_window.counter_Step_Zaber_X=0
        self.main_window.current_col=0
        self.main_window.current_row=0
        self.main_window.New_Color= [255,255,255] # [R,G,B] => WHITE
        # Move first to (X1,Y1)
        self.move_to_position(2,self.main_window.Pos_X1_Scan)
        self.move_to_position(0,self.main_window.Pos_Y1_Scan)
        self.check_position_and_start(0,self.main_window.Pos_Y1_Scan)

    def Change_Pixel_DAQ_X(self):
        #Stop condition:
        #Reach end of a line
        if self.main_window.counter_Data_per_Pixel >= (self.main_window.g_W):
            self.main_window.counter_Data_per_Pixel=0
            self.Stop_z2() # Stop the movement
            actual_pos=(self.main_window.Pos_Y1_Scan+(((self.main_window.Pos_Y2_Scan-self.main_window.Pos_Y1_Scan)/self.main_window.g_H)*self.main_window.counter_Step_Zaber_X))
            #Save Avg spectrum for each row
            self.main_window.Data_Spectrum_Array.to_csv('Scanning_Avg_Spectrum'+str(actual_pos)+'.csv', index=True)
            self.main_window.Data_Spectrum_Array=pd.DataFrame()
        
            # Reset positions
            self.main_window.counter_Step_Zaber_X+=1
            new_x_pos=(self.main_window.Pos_Y1_Scan
                        +(((self.main_window.Pos_Y2_Scan-self.main_window.Pos_Y1_Scan)/self.main_window.g_H)
                        *self.main_window.counter_Step_Zaber_X))
            
            if new_x_pos>=self.main_window.Pos_Y2_Scan: # Why is new x position compared with y position?
                
                # Stop DAQ if it is already running, causes crash otherwise
                if hasattr (DAQ_Reader_Global.daq_instance, 'threadDAQ'): #CHECK THIS
                    DAQ_Reader_Global.Stop_DAQ() # CHECK THIS
                
                self.main_window.Adquisit_Timer.stop()
                self.main_window.color_grid_widget.exportar_Matrix_CSV()
                self.main_window.Moment_Dev.to_csv('Scanning_Moments_Dev.csv', index=True)
                print('------  Scan finished --------')
                print('NOTE: Do not forget to save .csv files to other directory before starting next scan')
            else:
                self.move_to_position(0,new_x_pos)
                self.move_to_position(2,self.main_window.Pos_X1_Scan)
                self.check_position_and_start_X(2,self.main_window.Pos_X1_Scan)

        # End of line not reached:
        else:
            #Deviation estimation, vectorized by row by pixel
            
            factor_PSD = 2 / (self.main_window.number_of_samples * self.main_window.Laser_Frequency)
            self.main_window.Pixel_by_Row = self.main_window.Freq_Data.pow(2).mul(factor_PSD)
            M0_Pixel=self.main_window.Pixel_by_Row.sum(axis=0)
            M0_Pixel = M0_Pixel.replace(0, 1)
            M1_Pixel=self.main_window.Pixel_by_Row.mul(self.main_window.dataFreq, axis=0)
            M1_Pixel=M1_Pixel.sum(axis=0)
            M_dev=M1_Pixel/M0_Pixel
            #Set N of data to average fix length
            if self.main_window.Samples_To_AVG_Flag==True:
                self.main_window.Samples_To_AVG=len(M1_Pixel)
                self.main_window.Samples_To_AVG_Flag=False
            M_dev = pd.Series(np.resize(M_dev.to_numpy(), self.main_window.Samples_To_AVG))
            self.main_window.Moment_Dev=pd.concat([self.main_window.Moment_Dev, M_dev], axis=1)
            
            
            self.main_window.dataAmp_Avg=(self.main_window.Freq_Data.mean(axis=1))
            
            #Save Avg Spectrum
            self.main_window.Data_Spectrum_Array=pd.concat([self.main_window.Data_Spectrum_Array, self.main_window.dataAmp_Avg], axis=1)
            print('N Avg Samples')
            print(self.main_window.Counter_DAQ_samples)
            
            if self.main_window.dataAmp_Avg.empty:
                self.main_window.dataAmp_Avg=self.main_window.dataFreq*0
                self.main_window.Freq_Data=self.main_window.dataFreq*0

            # Make PSD discrete, as original equation is time domain and
            # contains integral to infinity:
            self.main_window.PSD_Avg_Moment=(self.main_window.dataAmp_Avg*self.main_window.dataAmp_Avg)*(2/(self.main_window.number_of_samples*self.main_window.Laser_Frequency))
            
            # Solve M0: simple sum of PSD.
            #self.PSD_Avg_Moment = self.PSD_Avg_Moment[:n // 2]
            M0 = np.sum(self.main_window.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])
            
            # Solve division by 0.
            if M0==0:
                M0=1
     
            # Solve M1: multiplication of the frequency and the PSD.
            M1 = np.sum(self.main_window.dataFreq * self.main_window.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])# / M0
            print('AVG Moment')
            print(M1/M0)

            # Save calculated moment to variable for flow velocity profile view.
            colorcolor=int(M1/M0)

            # Reset count data average and vector.
            self.main_window.Counter_DAQ_samples=0
            self.main_window.Freq_Data=pd.DataFrame()

            # Determine color given to flow velocity profile pixel.
            # Format is [R,G,B] so the pixel will be varying intensity of green.
            # colorcolor => integer value of average momentum.
            self.main_window.New_Color=[0, self.interpolation_Color(colorcolor), 0]

            # Apply new color to pixel in flow velocity profile view
            # and save measured momentum to CSV file            
            self.main_window.color_grid_widget.changeCellColor(self.main_window.counter_Data_per_Pixel,self.main_window.counter_Step_Zaber_X, self.main_window.New_Color)
            self.main_window.color_grid_widget.updateCSV(self.main_window.counter_Step_Zaber_X-1,self.main_window.counter_Data_per_Pixel-1,(M1/M0),M0,M1)
           
            # Add one to data taken for this pixel
            self.main_window.counter_Data_per_Pixel+=1
            
            # Change current_column to next pixel (next column)
            self.main_window.current_col= self.main_window.counter_Data_per_Pixel

            # Why increment with one if the max width has been exceeded?
            if self.main_window.counter_Data_per_Pixel >= self.main_window.g_W: 
                self.main_window.counter_Data_per_Pixel += 1

def Set_Scanning_Tab(self, scan_functionality):
    """Creates the scanning tab in the widget
    """
    #Initialization
    self.Pos_Y1_Scan = float(self.ui.load_pages.lineEdit_y1_scan.text())
    self.Pos_Y2_Scan = float(self.ui.load_pages.lineEdit_y2_scan.text())
    self.speed = float(self.ui.load_pages.lineEdit_speed_ums.text()) * 1000 * 1.6381 / 1.9843
    self.time_timer_scan=0
    self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text())
    self.counter_Data_per_Pixel=0 # Used for keeping track of current pixel
    self.current_col=0
    self.current_row=0
    self.New_Color= [255,255,255]
    self.scanning_Finish=False
    #Counter for the N. of average samples: 
    self.Counter_DAQ_samples=0
    self.PSD_Avg_Moment=0


    #Graphic_Data_Update
    def Change_Pixel_DAQ():
        #Stop condition
        #The final Y position is reach
        if self.counter_Data_per_Pixel >= (self.g_H):
            self.counter_Data_per_Pixel=0
            scan_functionality.Stop_z1() #Stop the movement
            #Reset the position
            self.counter_Step_Zaber_X+=1
            #Move to te next X position
            new_x_pos=(self.Pos_X1_Scan+(((self.Pos_X2_Scan-self.Pos_X1_Scan)/self.g_W)*self.counter_Step_Zaber_X))
            if new_x_pos>=self.Pos_X2_Scan:
                # Stop DAQ if it is running, causes crash otherwise
                if hasattr (DAQ_Reader_Global.daq_instance, 'threadDAQ'):
                    DAQ_Reader_Global.Stop_DAQ()
                    
                print('------  Scan finished --------')
                print('NOTE: Do not forget to save .csv files to other directory before starting next scan')
                self.Adquisit_Timer.stop()
            else:
                scan_functionality.move_to_position(2,new_x_pos)
                scan_functionality.move_to_position(0,self.Pos_Y1_Scan)
                scan_functionality.check_position_and_start(0,self.Pos_Y1_Scan)
        else:
            #AVG FFT
            self.dataAmp_Avg=(self.Freq_Data.mean(axis=1))
            print('N Avg Samples')
            print(self.Counter_DAQ_samples)
            #PSD estimation
            self.PSD_Avg_Moment=(self.dataAmp_Avg*self.dataAmp_Avg)*(2/(self.number_of_samples*self.Laser_Frequency))
            #Experimental
            M0 = np.sum(self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])
            M1 = np.sum(self.dataFreq * self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0]) / M0
            print('AVG Moment')
            colorcolor=int(M1/M0)
            print(colorcolor)
            newcolor=scan_functionality.interpolation_Color(colorcolor)

            print('end AVG Moment')
            #Restart counter and variable
            self.Counter_DAQ_samples=0
            self.Freq_Data=pd.DataFrame()
            self.New_Color=[0, newcolor, 0]


            self.color_grid_widget.changeCellColor(self.counter_Step_Zaber_X, self.counter_Data_per_Pixel, self.New_Color)
            self.counter_Data_per_Pixel+=1
            self.current_col= self.counter_Data_per_Pixel

            if self.counter_Data_per_Pixel >= self.g_H:
                self.counter_Data_per_Pixel += 1

    


    # X-direction-scanning
    #Graphic_Data_Update
    # def Change_Pixel_DAQ_X():
        
    #     #Stop condition:
    #     #Reach end of a line
    #     if self.counter_Data_per_Pixel >= (self.g_W):
    #         self.counter_Data_per_Pixel=0
    #         scan_functionality.Stop_z2() # Stop the movement
    #         actual_pos=(self.Pos_Y1_Scan+(((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.g_H)*self.counter_Step_Zaber_X))
    #         #Save Avg spectrum for each row
    #         self.Data_Spectrum_Array.to_csv('Scanning_Avg_Spectrum'+str(actual_pos)+'.csv', index=True)
    #         self.Data_Spectrum_Array=pd.DataFrame()
        
    #         # Reset positions
    #         self.counter_Step_Zaber_X+=1
    #         new_x_pos=(self.Pos_Y1_Scan
    #                     +(((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.g_H)
    #                     *self.counter_Step_Zaber_X))
            
    #         if new_x_pos>=self.Pos_Y2_Scan: # Why is new x position compared with y position?
                
    #             # Stop DAQ if it is already running, causes crash otherwise
    #             if hasattr (DAQ_Reader_Global.daq_instance, 'threadDAQ'):
    #                 DAQ_Reader_Global.Stop_DAQ()
                
    #             self.Adquisit_Timer.stop()
    #             self.color_grid_widget.exportar_Matrix_CSV()
    #             self.Moment_Dev.to_csv('Scanning_Moments_Dev.csv', index=True)
    #             print('------  Scan finished --------')
    #             print('NOTE: Do not forget to save .csv files to other directory before starting next scan')
    #         else:
    #             scan_functionality.move_to_position(0,new_x_pos)
    #             scan_functionality.move_to_position(2,self.Pos_X1_Scan)
    #             scan_functionality.check_position_and_start_X(2,self.Pos_X1_Scan)

    #     # End of line not reached:
    #     else:
    #         #Deviation estimation, vectorized by row by pixel
            
    #         factor_PSD = 2 / (self.number_of_samples * self.Laser_Frequency)
    #         self.Pixel_by_Row = self.Freq_Data.pow(2).mul(factor_PSD)
    #         M0_Pixel=self.Pixel_by_Row.sum(axis=0)
    #         M0_Pixel = M0_Pixel.replace(0, 1)
    #         M1_Pixel=self.Pixel_by_Row.mul(self.dataFreq, axis=0)
    #         M1_Pixel=M1_Pixel.sum(axis=0)
    #         M_dev=M1_Pixel/M0_Pixel
    #         #Set N of data to average fix length
    #         if self.Samples_To_AVG_Flag==True:
    #             self.Samples_To_AVG=len(M1_Pixel)
    #             self.Samples_To_AVG_Flag=False
    #         M_dev = pd.Series(np.resize(M_dev.to_numpy(), self.Samples_To_AVG))
    #         self.Moment_Dev=pd.concat([self.Moment_Dev, M_dev], axis=1)
            
            
    #         self.dataAmp_Avg=(self.Freq_Data.mean(axis=1))
            
    #         #Save Avg Spectrum
    #         self.Data_Spectrum_Array=pd.concat([self.Data_Spectrum_Array, self.dataAmp_Avg], axis=1)
    #         print('N Avg Samples')
    #         print(self.Counter_DAQ_samples)
            
    #         if self.dataAmp_Avg.empty:
    #             self.dataAmp_Avg=self.dataFreq*0
    #             self.Freq_Data=self.dataFreq*0

    #         # Make PSD discrete, as original equation is time domain and
    #         # contains integral to infinity:
    #         self.PSD_Avg_Moment=(self.dataAmp_Avg*self.dataAmp_Avg)*(2/(self.number_of_samples*self.Laser_Frequency))
            
    #         # Solve M0: simple sum of PSD.
    #         #self.PSD_Avg_Moment = self.PSD_Avg_Moment[:n // 2]
    #         M0 = np.sum(self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])
            
    #         # Solve division by 0.
    #         if M0==0:
    #             M0=1
     
    #         # Solve M1: multiplication of the frequency and the PSD.
    #         M1 = np.sum(self.dataFreq * self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])# / M0
    #         print('AVG Moment')
    #         print(M1/M0)

    #         # Save calculated moment to variable for flow velocity profile view.
    #         colorcolor=int(M1/M0)

    #         # Reset count data average and vector.
    #         self.Counter_DAQ_samples=0
    #         self.Freq_Data=pd.DataFrame()

    #         # Determine color given to flow velocity profile pixel.
    #         # Format is [R,G,B] so the pixel will be varying intensity of green.
    #         # colorcolor => integer value of average momentum.
    #         self.New_Color=[0, scan_functionality.interpolation_Color(colorcolor), 0]

    #         # Apply new color to pixel in flow velocity profile view
    #         # and save measured momentum to CSV file            
    #         self.color_grid_widget.changeCellColor(self.counter_Data_per_Pixel,self.counter_Step_Zaber_X, self.New_Color)
    #         self.color_grid_widget.updateCSV(self.counter_Step_Zaber_X-1,self.counter_Data_per_Pixel-1,(M1/M0),M0,M1)
           
    #         # Add one to data taken for this pixel
    #         self.counter_Data_per_Pixel+=1
            
    #         # Change current_column to next pixel (next column)
    #         self.current_col= self.counter_Data_per_Pixel

    #         # Why increment with one if the max width has been exceeded?
    #         if self.counter_Data_per_Pixel >= self.g_W: 
    #             self.counter_Data_per_Pixel += 1


    def Capture_Data_Avg():
        
        ######### Update Laser data FFT and Voltage
        self.DAQ_Data=self.threadDAQ.DAQ_Data
        self.data_DAQ2=butter_bandpass_filter(self.DAQ_Data, self.low_freq_filter, self.high_freq_filter,self.order_filter, self.Laser_Frequency)
        self.dataAmp, self.dataFreq, _=FFT_calc(self.data_DAQ2, self.Laser_Frequency)
        amp=pd.Series((self.dataAmp))
        #Add a new column
        self.Freq_Data=pd.concat([self.Freq_Data, amp], axis=1)
        self.Counter_DAQ_samples=self.Counter_DAQ_samples+1

    ###################################################################
    ###################################################################
    #CALIBRATION
    def Start_Vel_Calib():

        #Parameters ###########################
        self.Directory=(self.ui.load_pages.lineEdit_Directory.text())
        self.FileName=(self.ui.load_pages.lineEdit_Name_Files.text())
        self.Amp_Peak_Search=float(self.ui.load_pages.Vel_Threshold_Peak.text())

        zab_start=int(self.ui.load_pages.Vel_Manual_X1.text())
        zab_stop=int(self.ui.load_pages.Vel_Manual_X2.text())
        zab_steps=int(self.ui.load_pages.Vel_Steps_Calib.text())
        self.Data_To_Check=int(self.ui.load_pages.lineEdit_Avg_FFT.text())
        self.Zaber_Steps=np.linspace(start=zab_start, stop=zab_stop, num=zab_steps)
        self.ActualStep=0
        self.Zaber_Pos=0
        self.Vel_Move_Start=False
        self.Freq_Data=pd.DataFrame()
        self.Counter_DAQ_samples=0
        #List with max peaks
        self.Vel_Calib_Peaks_List=[]
        self.Vel_Routine.start()


    def Vel_Routine():
        #Pipeline
        if self.ActualStep<len(self.Zaber_Steps):
            #Move Zaber
            if self.Vel_Move_Start==False:
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    new_position=self.Zaber_Steps[self.ActualStep]
                    #zaber_pos=new_position/10000
                    device_list[2].move_absolute(new_position, Units.LENGTH_MICROMETRES)
                    print("---------- Zaber Pos: ---------- " + str(self.Zaber_Steps[self.ActualStep])+" ----------")
                    self.Vel_Move_Start=True
                    #Clear
                    self.Freq_Data=pd.DataFrame()
                    self.Counter_DAQ_samples=0
                    self.Adquisit_Timer.start()
            #Adquisition
            else:
                # Once the samples are acquired
                if self.Counter_DAQ_samples>self.Data_To_Check:
                    self.Adquisit_Timer.stop()
                    self.Vel_Calib_Peaks_List.append(max(self.Freq_Data.mean(axis=1)))
                    #Move to next Position
                    self.ActualStep=self.ActualStep+1
                    print("--- Next Step ---")
                    self.Vel_Move_Start=False
        else:
            self.Vel_Routine.stop()
            print(self.Vel_Calib_Peaks_List)
            #Find Frontiers
            New_Limits=[]
            for i, valor in enumerate(self.Vel_Calib_Peaks_List):
                if valor >= self.Amp_Peak_Search:
                    New_Limits.append(i)
            inicio_grupo = 0
            fin_grupo = 0
            if len(New_Limits) > 2:

                max_longitud = 0
                for i in range(len(New_Limits) - 1):
                    longitud_actual = New_Limits[i+1] - New_Limits[i]
                    if longitud_actual > max_longitud:
                        max_longitud = longitud_actual
                        inicio_grupo = New_Limits[i]
                        fin_grupo = New_Limits[i+1]
            New_Limits=[inicio_grupo, fin_grupo]
            print(New_Limits)
            self.ui.load_pages.Vel_Limit_X2.setText(str(round(self.Zaber_Steps[fin_grupo],1)))
            self.ui.load_pages.Vel_Limit_X1.setText(str(round(self.Zaber_Steps[inicio_grupo],1)))

            print("---------- Calibration finished ---------- ")



    def Get_Report():
        plot_grouped_error_bars('Scanning_Moments_Dev.csv', int((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.cell_size))

    ###################################################################
    ###################################################################
    self.Data_Spectrum_Array=pd.DataFrame()
    
    #Buttons and timmer connections #########################
    self.Pixel_Interval_X = QTimer()
    self.Pixel_Interval_X.timeout.connect(scan_functionality.Change_Pixel_DAQ_X)

    self.Pixel_Interval = QTimer()
    self.Pixel_Interval.timeout.connect(Change_Pixel_DAQ)

    # Continuous Sweep Routine
    # Configure timer that determines sampling frequency
    # NOTE: This timer determines how often the program requests the sampling data
    # from the DAQ. After every interval, all the samples of the past interval are
    # requested, and then the average is taken from that.
    # NOTE: interval used to be 1ms, but had to be changed to 10 due to laptop
    # performance. With a faster laptop, it can be returned to 1.
    # NOTE: to compensate for this interval change, reduce the measurement speed
    # by the same factor (so, 1/10th for example) if you want to keep the same samples / pixel.
    # At the moment it has around 300 samples per pixel of 200 um, so this 
    # can be reduced without issue.
    self.Adquisit_Timer = QTimer()
    self.Adquisit_Timer.setInterval(10) # ISSUE here, works with 5 but unstable.
    self.Adquisit_Timer.timeout.connect(Capture_Data_Avg)

    #For Calibration Routine
    # Configure timer that determines sampling frequency
    self.Vel_Routine= QTimer()
    self.Vel_Routine.setInterval(1)
    self.Vel_Routine.timeout.connect(Vel_Routine)

    # Link buttons to functions #
    self.ui.load_pages.Stop_x_but.clicked.connect(scan_functionality.get_current_position)


    # self.ui.load_pages.Stop_Y_but.clicked.connect(Stop_z1)
    # self.ui.load_pages.Stop_x_but.clicked.connect(Stop_z2) # Button for stopping X
    self.ui.load_pages.Vel_Start_Calib.clicked.connect(Start_Vel_Calib)
    self.ui.load_pages.Vel_Report.clicked.connect(Get_Report)
    ###################################################################
    ###################################################################

