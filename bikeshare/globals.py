## doing this here to prevent circular imports, since we have to put the data from typer's callback(s) somewhere
GLOBALS={'station_availability_high': 0.8, 
         'station_availability_low': 0.3, 
         'station_availability_color': {'high': 'bright_green', 'low': 'bright_red', 'medium': 'bright_yellow'}}