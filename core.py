import numpy as np
from scipy import signal

PREAMBLE = [1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0]
MAX_FRAME_LEN = 240
MIN_FRAME_LEN = 112
FACTOR = 3.5
VERBOSE = False

class Frame:
    def __init__(self, reading ,start_pos):
        self.start_pos = start_pos
        self.ppm_data = reading[start_pos:start_pos+MAX_FRAME_LEN]
        self.crop_frame()
        self.data, self.errors = self.ppm_to_bits()
        self.df =        self.data[9:14]       # DOWNLINK FORMAT
        self.ca =        self.data[14:17]      # CAPABILITY
        self.icao =      self.data[17:41]      # ICAO IDENTIFIER
        self.msgtype =   self.data[41:49]      # MESSAGE TYPE
        self.df =        self.data[9:14]       # DOWNLINK FORMAT
        self.ca =        self.data[14:17]      # CAPABILITY
        self.icao =      self.data[17:41]      # ICAO IDENTIFIER
        self.msgtype =   self.data[41:49]      # MESSAGE TYPE
        if VERBOSE:
            print(">> Isolated frame at starting position ", start_pos)
            print(">> Frame length: ", self.data.size)
            print(">> Error count : ", self.errors)
        
    def crop_frame(self):
        last1 = np.where(self.ppm_data>0)[0][-1]
        if last1 > MIN_FRAME_LEN:
            self.ppm_data = self.ppm_data[:last1+1]
        else:
            self.ppm_data = self.ppm_data[:MIN_FRAME_LEN]
        
    def ppm_to_bits(self):
        frame = np.zeros((int(self.ppm_data.size/2)))
        _errors = 0
        for i in range(frame.size):
            symbol = self.ppm_data[2*i:2*i+2]
            if (symbol == [1,0]).all():
                frame[i] = 1
            elif (symbol == [0,1]).all():
                pass
            else:
                if(i>=len(PREAMBLE)):
                    _errors += 1
        return frame, _errors
            
class Capture:
    def __init__(self, data, sample_rate):
        if VERBOSE:
            print("> Started processing reading")
        self.data = data
        self.sample_rate = sample_rate
        self.data_threshold = np.empty((0,0))
        self.preambles = []
        self.frames = []
        self.rms = np.sqrt(np.mean(abs(self.data)**2))
        self.threshold = self.rms * FACTOR
        
    def sync(self, sample_rate_out):
        if VERBOSE:
            print("> Syncing reading")
        """
        Syncs reading at rate_in to rate_out
        
        Args:
            reading (numpy array): array of complex or float. The signal
            rate_in (int): Sample rate at which reading was captured
            rate_out(int): Sample rate to resample reading
            
        Returns:
            synced: reading sampled at rate_out, normalized
        """
        
        duration = self.data.size/self.sample_rate
        
        xrespl = signal.resample_poly(self.data, 18,3)
        xtimerespl = np.linspace(0,1e6*duration,num=xrespl.size)
        
        synctime = np.linspace(0,1e6*duration, num = int(self.data.size*sample_rate_out/self.sample_rate))
        timescale = xtimerespl.size/synctime.size
        
        synced = []
        
        for index, time in enumerate(synctime):
            synced.append(xrespl[int(index*timescale)])
        
        normalizedSynced = (synced)/(np.max(np.abs(synced)))
        
        self.sample_rate = sample_rate_out
        self.data = normalizedSynced
        
        return np.array(normalizedSynced), synctime
    
    def threshold_cap(self, threshold = 0):
        if threshold == 0:
            threshold = self.threshold
        else:
            self.threshold = threshold
        if VERBOSE:
            print("> Reading threshold of: ", threshold)
        self.data_threshold = abs(self.data) > threshold
        return abs(self.data) > threshold
    
    def detect_preambles(self):
        if self.data_threshold.size == 0:
            print("Data not thresholded")
        else:
            self.preambles = get_subarray_indices(self.data_threshold, PREAMBLE)
            if VERBOSE:
                print("> Found ", self.preambles.size, " preambles")
        return self.preambles
    
    def get_frames(self):
        if VERBOSE:
            print("> Capturing frames based on preambles")
        for preamble in self.preambles:
            self.frames.append(Frame(self.data_threshold, preamble))
        for frame in self.frames:
            frame.crop_frame()
    
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
    print(str(matches.size) + " occurances found")
    
    return matches