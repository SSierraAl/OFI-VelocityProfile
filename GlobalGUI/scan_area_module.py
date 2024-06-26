import time
""" Module responsible for determining the center reference position and image processing
"""
def edge_scan(main_window, direction, start_coordinates):
    """performs a scan in a direction and returns the Zaber (X,Y) coordinates
    of first encountered edge.

    Args:
        direction (string): 'x', '-x', 'y' , '-y'
        start_coordinates (_type_): (X,Y) tuple
    """

    main_window.time_timer_scan_override =0 # not sure if this override is required
    main_window.cell_size_override  = int(200)
    main_window.override_user_settings = True
    main_window.edge_scan_mode = True
    
    if direction == 'x':
        # Go in positive X direction
        # Start: start coordinate
        # End: maximum range of Zaber setup
        # Set override settings
        main_window.speed_override  = float(400)
        print(f"Starting algorithm edge scan with starting position {start_coordinates[0]}, {start_coordinates[1]}")
        main_window.Pos_X1_Scan_override = float(start_coordinates[0]) # x part of X,Y tuple
        main_window.Pos_X2_Scan_override = float(49800) # end of Zaber with small margin
        #main_window.Pos_X2_Scan_override = float(49800) # end of Zaber with small margin
        main_window.Pos_Y1_Scan_override = float(start_coordinates[1]) # y of X,Y tuple
        main_window.Pos_Y2_Scan_override = float(start_coordinates[1]+(2*main_window.cell_size_override)) #WARNING: needs 2 rows (2 x cell size), crashes otherwise.
    
        # Start scan
        main_window.scan_functions_instance.Scan_Continuous(axis = 'x')
    
    elif direction == '-x':
        # Go in negative X direction
        # Start: start coordinate
        # End: maximum range of Zaber setup
        # Set override settings
        main_window.speed_override  = float(-400)
        print(f"Starting algorithm edge scan with starting position {start_coordinates[0]}, {start_coordinates[1]}")
        main_window.Pos_X1_Scan_override = float(start_coordinates[0]) # x part of X,Y tuple
        main_window.Pos_X2_Scan_override = float(1000) # end of Zaber with small margin
        main_window.Pos_Y1_Scan_override = float(start_coordinates[1]) # y of X,Y tuple
        main_window.Pos_Y2_Scan_override = float(start_coordinates[1]+(2*main_window.cell_size_override)) #WARNING: needs 2 rows (2 x cell size), crashes otherwise.
        
        # Start scan
        main_window.scan_functions_instance.Scan_Continuous(axis = 'x')
        
    elif direction == 'y':
        # Go in positive X direction
        # Start: start coordinate
        # End: maximum range of Zaber setup
        # Set override settings
        main_window.speed_override  = float(400)
        print(f"Starting algorithm edge scan with starting position {start_coordinates[0]}, {start_coordinates[1]}")
        main_window.Pos_X1_Scan_override = float(start_coordinates[0]) # x part of X,Y tuple
        main_window.Pos_X2_Scan_override = float(start_coordinates[0]+(2*main_window.cell_size_override)) #WARNING: needs 2 rows (2 x cell size), crashes otherwise.
        main_window.Pos_Y1_Scan_override = float(start_coordinates[1]) # y of X,Y tuple
        main_window.Pos_Y2_Scan_override = float(49800) # end of Zaber with small margin
    
        # Start scan
        main_window.scan_functions_instance.Scan_Continuous(axis = 'y')
        
def scan_all_edges(main_window, start_coordinates, count):
    if count == 0:
        edge_scan(main_window, 'x', start_coordinates)
    elif count == 1:
        edge_scan(main_window, '-x', start_coordinates)
    if count == 2:
        edge_scan(main_window, 'y', start_coordinates)
    elif count == 3:
        edge_scan(main_window, '-y', start_coordinates)
    