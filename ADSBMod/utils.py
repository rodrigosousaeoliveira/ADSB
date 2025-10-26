import numpy as np

def npbin_to_dec(array):
    try:
        return int(''.join(str(int(x)) for x in array), 2)
    except:
        return 0

def get_subarray_indices(arr, sub):
    """
    FIND OCCURANCE OF A SEQUENCE OF BITS IN READING
    """
    
    n = len(sub)
    if n == 0:
        return np.array([0])
    if len(arr) < n:
        return np.array([])
    
    windows = np.lib.stride_tricks.sliding_window_view(arr, n)
    matches = np.where(np.all(windows == sub, axis=1))[0]   
    #print(str(matches.size) + " occurances found")
    
    return matches
def nl(lat):
    nz = 15
    nl_1 = (1 - np.cos(np.pi/(2*nz)))/(np.cos(lat * np.pi/180)**2)
    return np.fix(2*np.pi/(np.arccos(1-nl_1)))

TC_MSG_TYPE = ["None",
"Aircraft identification",
"Aircraft identification",
"Aircraft identification",
"Aircraft identification",
"Surface position",
"Surface position",
"Surface position",
"Surface position",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne position (w/Baro Altitude)",
"Airborne velocities",
"Airborne position (w/GNSS Height)",
"Airborne position (w/GNSS Height)",
"Airborne position (w/GNSS Height)",
"Reserved",
"Reserved",
"Reserved",
"Reserved",
"Reserved",
"Aircraft status",
"Target state and status information",
"None",
"Aircraft operation status"]

ACFT_ID_CATEGORY = {
    '1':	'Reserved',
    '0':    'No category information',
    '21':	'Surface emergency vehicle',
    '23':	'Surface service vehicle',
    '24':	'Ground obstruction',
    '25':	'Ground obstruction',
    '26':	'Ground obstruction',
    '27':	'Ground obstruction',
    '31':	'Glider, sailplane',
    '32':	'Lighter-than-air',
    '33':	'Parachutist, skydiver',
    '34':	'Ultralight, hang-glider, paraglider',
    '35':	'Reserved',
    '36':	'Unmanned aerial vehicle',
    '37':	'Space or transatmospheric vehicle',
    '41':	'Light (less than 7000 kg)',
    '42':	'Medium 1 (between 7000 kg and 34000 kg)',
    '43':	'Medium 2 (between 34000 kg to 136000 kg)',
    '44':	'High vortex aircraft',
    '45':	'Heavy (larger than 136000 kg)',
    '46':	'High performance (>5 g acceleration) and high speed (>400 kt)',
    '47':	'Rotorcraft'}

CALLSIGN_CHAR = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######'