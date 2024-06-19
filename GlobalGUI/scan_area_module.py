import time
""" Module responsible for determining the center reference position and image processing
"""
def edge_scan(main_window, direction, start_coordinates):
    """performs a scan in a direction and returns the Zaber (X,Y) coordinates
    of first encountered edge.

    Args:
        direction (string): 'x', '-x', 'y' , '-y'
        start_coordinates (_type_): (X,Y) tuple

    Returns:
        tuple: tuple containing (X,Y)
    """
    main_window.speed_override  = float(400)
    main_window.time_timer_scan_override =0 # not sure if this override is required
    main_window.cell_size_override  = int(200)
    main_window.override_user_settings = True
    
    counter = 0
    timeout_value_ms = 50000
    
    if direction == 'x':
        # Go in positive X direction
        # Start: start coordinate
        # End: maximum range of Zaber setup
        # Set override settings
        print(f"Starting algorithm edge scan with starting position {start_coordinates[0]}, {start_coordinates[1]}")
        main_window.Pos_X1_Scan_override = float(start_coordinates[0]) # x part of X,Y tuple
        main_window.Pos_X2_Scan_override = float(49800) # end of Zaber with small margin
        main_window.Pos_Y1_Scan_override = float(start_coordinates[1]) # y of X,Y tuple
        main_window.Pos_Y2_Scan_override = float(start_coordinates[1]+(2*main_window.cell_size_override)) #WARNING: needs 2 rows (2 x cell size), crashes otherwise.
        
        # Start scan
        main_window.scan_functions_instance.Scan_Continuos_X()

        print("EDGE SCAN: comparing measurements to threshold")
        while main_window.moment_average <= main_window.detect_edge_threshold and counter < timeout_value_ms:
            print(f"current average: {main_window.moment_average}")
            time.sleep(0.001) # wait 1 ms, maybe change to us
            counter+= 1

        # Stop Zabers
        main_window.scan_functions_instance.Stop_z2()
        main_window.scan_functions_instance.Stop_z1()
        # ALSO STOP DAQ
        
        # Check if while loop was passed due to threshold or due to timeout of counter
        # position might have a small delay, but should work.
        if main_window.moment_average > main_window.detect_edge_threshold:
            print(f"EDGE SCAN: edge found within {counter} ms. Saving position.")
            x = main_window.scan_functions_instance.get_current_position(2) # Get current position of X Zaber
            y = main_window.scan_functions_instance.get_current_position(1) # Get current position of Y Zaber
            edge_coordinates = (x,y)
        else:
            print(f"EDGE SCAN: timeout of {counter} ms expired, no edge found.")
            edge_coordinates = (0,0) # NO EDGE FOUND



    return edge_coordinates
