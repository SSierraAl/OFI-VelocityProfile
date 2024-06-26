from zaber_motion import Units
from zaber_motion.ascii import Connection
import time

with Connection.open_serial_port("COM8") as connection:
    connection.enable_alerts()

    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]

    axis = device.get_axis(1)
    if not axis.is_homed():
      axis.home()
    
    position = 25000
    position_absolute = int(position / (0.047625)) #* 10**(-6))
    connection.generic_command(f"move abs {position_absolute}", 1, 0, True, 500)
    
    actual_status = connection.generic_command("get motion.busy", 1, 0, True, 500)
    while actual_status.status == 'BUSY':
      actual_status = connection.generic_command("get motion.busy", 1, 0, True, 500)
      
    actual_pos = connection.generic_command("get pos", 1, 0, True, 500)
    print(actual_pos.data)
    connection.generic_command("move abs 498000", 1, 0, True, 500)
    
    time.sleep(10)
    actual_status = connection.generic_command("get motion.busy", 1, 0, True, 500)
    while actual_status.status == 'BUSY':
      actual_status = connection.generic_command("get motion.busy", 1, 0, True, 500)
  
    connection.generic_command("move abs 250000", 2, 0, True, 500)
    
    actual_status = connection.generic_command("get motion.busy", 2, 0, True, 500)
    while actual_status.status == 'BUSY':
      actual_status = connection.generic_command("get motion.busy", 2, 0, True, 500)
    
    connection.generic_command("move abs 498000", 2, 0, True, 500)
    
    actual_status = connection.generic_command("get motion.busy", 2, 0, True, 500)
    while actual_status.status == 'BUSY':
      actual_status = connection.generic_command("get motion.busy", 2, 0, True, 500)
    #time.sleep(5)
    # Move to 10mm
    #axis.move_absolute(10, Units.LENGTH_MILLIMETRES)

    # Move by an additional 5mm
    #axis.move_relative(5, Units.LENGTH_MILLIMETRES)
    
