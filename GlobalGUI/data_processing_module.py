import pandas as pd

class Data_processing:
    def __init__ (self, main_window):
        main_window = main_window
        self.moments = None
        
    def read_moments(self):
        # read_csv with pandas of scanning_moments_csv.csv
        # save it to pandas series in such a way that it can easily be manipulated
        self.moments = pd.read_csv("Scanning_Moments_CSV.csv")
        print(self.moments.head(1))
        print(self.moments.tail(1))
        
        
        
Data_processing_instance = Data_processing(None)
Data_processing_instance.read_moments()