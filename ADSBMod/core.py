import numpy as np
from scipy import signal, fft
import matplotlib.pyplot as plt
from .utils import npbin_to_dec, get_subarray_indices, nl, TC_MSG_TYPE, CALLSIGN_CHAR, ACFT_ID_CATEGORY
from datetime import datetime
import time

PREAMBLE = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
MAX_FRAME_LEN = 240
MIN_FRAME_LEN = 112
FACTOR = 3.5
VERBOSE = False
ACCEPTED_DF = [17, 18]
MAX_ACCEPTED_ERROR = 5
LATref = 46.071389  # Initially ref position is receiver position
LONref = 14.481111
nz = 15  # Number of latitude zones


class Aircrafts:

    def __init__(self):
        self.aircrafts = []

    def add_frame(self, Frame):
        if Frame.icao not in self.get_icaos():
            self.aircrafts.append(Aircraft(Frame))
        else:
            self.aircrafts[self.get_ac_index_by_icao(
                Frame.icao)].add_frame(Frame)

    def get_ac_index_by_icao(self, icao):
        ac_index = 9999  # Just an out of bounds number
        for index, aircraft in enumerate(self.aircrafts):
            if aircraft.icao == icao:
                ac_index = index
        return ac_index

    def get_icaos(self):
        return [aircraft.icao for aircraft in self.aircrafts]

    def get_current_acs(self):
        ret = []
        for aircraft in self.aircrafts:
            dt = time.time() - aircraft.last_update_time
            print(dt)
            if dt <= 30:
                ac = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "icao": aircraft.icao,
                    "altitude": aircraft.altitude,
                    "latitude": aircraft.latitude,
                    "longitude": aircraft.longitude,
                    "callsign": aircraft.callsign,
                    "speed": 0}
                ret.append(ac)
        return ret


class Aircraft:
    def __init__(self, MyFrame):
        self.frames = []
        self.icao = MyFrame.icao
        self.callsign = ""
        self.wake_category = ""
        self.baroALT = False
        self.altitude = 0
        self.latitude = LATref
        self.longitude = LONref
        self.LATref = LATref
        self.LONref = LONref
        self.last_update_time = 0
        self.add_frame(MyFrame)

    def set_callsign(self, callsign):
        self.callsign = callsign

    def add_frame(self, MyFrame):
        self.frames.append(MyFrame)
        self.last_update_time = time.time()
        if isinstance(MyFrame.msg, ACFT_ID_msg):
            # These are the same during capture, so setting only once would \
            # suffice, but updating constantly in case of errors in reading
            self.set_callsign(MyFrame.msg.callsign)
            self.wake_category = MyFrame.msg.wake_category
        if isinstance(MyFrame.msg, ACFT_POS_msg):
            self.baroALT = MyFrame.msg.baroALT
            self.altitude = MyFrame.msg.altitude
            self.update_latlon(MyFrame)

    def update_latlon(self, Frame):
        # Latitude part
        dLat = 360/(4*nz - Frame.msg.msg_is_odd)  # Lat zones odd or even
        LATcpr = Frame.msg.lat_encoded/2**17
        j = np.fix(self.LATref/dLat) + \
            np.fix((self.LATref % dLat)/dLat-(LATcpr+0.5))
        self.latitude = dLat*(j+LATcpr)
        self.LATref = self.latitude
        # Longitude part
        dLon = 360/max(nl(self.latitude) - Frame.msg.msg_is_odd, 1)
        LONcpr = Frame.msg.lon_encoded/2**17
        m = np.fix(self.LONref/dLon) + \
            np.fix((self.LONref % dLon)/dLon-(LONcpr+0.5))
        self.longitude = dLon*(m+LONcpr)
        self.LONref = self.longitude
        # Sprint('Coordinates = ', self.latitude, ' , ', self.longitude)


class Capture:
    def __init__(self, data, sample_rate):
        if VERBOSE:
            print("> Started processing reading")
        self.data = data
        self.sample_rate = sample_rate
        self.data_threshold = np.empty((0, 0))
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

        xrespl = signal.resample_poly(self.data, 18, 3)
        xtimerespl = np.linspace(0, 1e6*duration, num=xrespl.size)

        synctime = np.linspace(
            0, 1e6*duration, num=int(self.data.size*sample_rate_out/self.sample_rate))
        timescale = xtimerespl.size/synctime.size

        synced = []

        for index, time in enumerate(synctime):
            synced.append(xrespl[int(index*timescale)])

        normalizedSynced = (synced)/(np.max(np.abs(synced)))

        self.sample_rate = sample_rate_out
        self.data = normalizedSynced

        return np.array(normalizedSynced), synctime

    def threshold_cap(self, threshold=0):
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
            self.preambles = get_subarray_indices(
                self.data_threshold, PREAMBLE)
            if VERBOSE:
                print("> Found ", self.preambles.size, " preambles")
        return self.preambles

    def get_frames(self, Aircrafts):
        if VERBOSE:
            print("> Capturing frames based on preambles")
        for preamble in self.preambles:
            ThisFrame = Frame(self.data_threshold, preamble)
            if ThisFrame.df in ACCEPTED_DF and \
                    ThisFrame.errors <= MAX_ACCEPTED_ERROR:
                self.frames.append(ThisFrame)
                Aircrafts.add_frame(ThisFrame)
                
    def bandpass(self):
        """
        Aplica um filtro passa-faixa Butterworth no array self.data
        entre 25 kHz e 75 kHz.
        
        Returns:
            numpy.array: Dados filtrados
        """
        # Parâmetros do sinal
        fs = self.sample_rate  # Frequência de amostragem: 2 MHz
        lowcut = 25000  # Frequência inferior: 25 kHz
        highcut = 75000  # Frequência superior: 75 kHz
        
        # Projeto do filtro Butterworth
        nyquist = fs / 2  # Frequência de Nyquist
        low = lowcut / nyquist  # Frequência normalizada inferior
        high = highcut / nyquist  # Frequência normalizada superior
        
        # Verifica se as frequências estão dentro do range válido
        if low >= 1.0 or high >= 1.0:
            raise ValueError("Frequências de corte devem ser menores que a frequência de Nyquist")
        
        # Ordem do filtro (pode ser ajustada conforme necessário)
        order = 4
        
        # Projeto do filtro passa-faixa Butterworth
        b, a = signal.butter(order, [low, high], btype='band')
        
        # Aplica o filtro (filtfilt elimina o deslocamento de fase)
        dados_filtrados = signal.filtfilt(b, a, self.data)
        self.data = dados_filtrados
        
        return dados_filtrados

    def plot(self, text = ''):
        n = self.data.size
        data_fft = fft.fft(self.data)
        freq_fft = fft.fftfreq(n, 1/self.sample_rate)
        now_str = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        fig, axs = plt.subplots(2)
        fig.set_figheight(15)
        fig.set_figwidth(15)
        fig.suptitle(now_str+text)
        axs[0].plot(abs(self.data), marker='.')
        axs[0].hlines(self.threshold, 0, n, color='r')
        axs[0].grid()
        axs[1].plot(freq_fft, np.abs(data_fft))
        axs[1].set_xlim([0,1e6])
        axs[1].grid()
        fig.savefig('plots/'+now_str+text+'.png')
        plt.close(fig)


class Frame:
    def __init__(self, reading, start_pos):
        self.start_pos = start_pos
        self.ppm_data = reading[start_pos:start_pos+MAX_FRAME_LEN]
        self.crop_frame()
        self.data, self.errors = self.ppm_to_bits()
        self.data_hex = hex(npbin_to_dec(self.data))
        self.df = npbin_to_dec(self.data[8:13])  # DOWNLINK FORMAT
        self.ca = npbin_to_dec(self.data[13:16])  # CAPABILITY
        self.icao = hex(npbin_to_dec(self.data[16:40]))  # ICAO IDENTIFIER
        self.msgtype = npbin_to_dec(self.data[40:45])  # MESSAGE TYPE
        self.time = time.time()
        self.msg = self.message_factory()
        if VERBOSE:
            print(">> Isolated frame at starting position ", start_pos)
            print(">> Frame length: ", self.data.size)
            print(">> Error count : ", self.errors)

    def crop_frame(self):
        last1 = np.where(self.ppm_data > 0)[0][-1]
        if last1 > MIN_FRAME_LEN:
            self.ppm_data = self.ppm_data[:last1+1]
        else:
            self.ppm_data = self.ppm_data[:MIN_FRAME_LEN]

    def ppm_to_bits(self):
        frame = np.zeros((int(self.ppm_data.size/2)))
        _errors = 0
        for i in range(frame.size):
            symbol = self.ppm_data[2*i:2*i+2]
            if (symbol == [1, 0]).all():
                frame[i] = 1
            elif (symbol == [0, 1]).all():
                pass
            else:
                if (i >= len(PREAMBLE)):
                    _errors += 1
        return frame, _errors

    def message_factory(self):
        # For now just selecting ADS-B messages. If general mode S implemented \
        # remove this condition
        if self.df == 17 or self.df == 18:
            if VERBOSE:
                print(">> Found ADSB MSG")
            if self.msgtype >= 1 and self.msgtype <= 4:
                return ACFT_ID_msg(self)

            elif (self.msgtype >= 9 and self.msgtype <= 18) or  \
                    (self.msgtype >= 20 and self.msgtype <= 22):
                return ACFT_POS_msg(self)
            else:
                return 0
        else:
            return ModeS_general()


class ACFT_ID_msg:

    def __init__(self, FrameOrigin):
        self.contents = FrameOrigin.data[40:98]
        self.msgtype = FrameOrigin.msgtype
        self.acft_category = npbin_to_dec(self.contents[5:8])
        self.wake_category = self.get_wake_category()
        self.callsign = self.get_callsign()

    def __str__(self):
        ret = "|------|   Wake Category:   " + self.wake_category \
            + "\n|------|   Callsign:       " + self.callsign
        return ret

    def get_wake_category(self):
        if self.msgtype == 1:
            return ACFT_ID_CATEGORY['1']
        elif self.acft_category == 0:
            return ACFT_ID_CATEGORY['0']
        else:
            try:
                return ACFT_ID_CATEGORY[str(self.msgtype) +
                                        str(self.acft_category)]
            except:
                return 'ERROR'

    def get_callsign(self):
        c1 = npbin_to_dec(self.contents[8:14])
        c2 = npbin_to_dec(self.contents[14:20])
        c3 = npbin_to_dec(self.contents[20:26])
        c4 = npbin_to_dec(self.contents[26:32])
        c5 = npbin_to_dec(self.contents[32:38])
        c6 = npbin_to_dec(self.contents[38:44])
        c7 = npbin_to_dec(self.contents[44:50])
        c8 = npbin_to_dec(self.contents[50:56])
        callsign = CALLSIGN_CHAR[c1] + CALLSIGN_CHAR[c2] + CALLSIGN_CHAR[c3] \
            + CALLSIGN_CHAR[c4] + CALLSIGN_CHAR[c5] + CALLSIGN_CHAR[c6] \
            + CALLSIGN_CHAR[c7] + CALLSIGN_CHAR[c8]
        return callsign


class ACFT_POS_msg:

    def __init__(self, FrameOrigin):
        self.contents = FrameOrigin.data[40:98]
        self.msgtype = FrameOrigin.msgtype
        # If alt is not baro, it is GNSS
        self.baroALT = self.msgtype >= 9 and self.msgtype <= 18
        self.surveil_status = self.contents[5:7]
        self.single_ant_flg = self.contents[7:8]
        self.altitude = self.get_altitude()
        self.msg_is_odd = self.contents[21]
        self.lat_encoded = npbin_to_dec(self.contents[22:39])
        self.lon_encoded = npbin_to_dec(self.contents[39:56])

    def __str__(self):
        ret = "|------|        Altitude:   " + str(self.altitude) + ' ft'
        return ret

    def get_altitude(self):
        raw_alt = self.contents[8:20]
        altitude = 0
        if self.baroALT:
            if raw_alt[7]:
                altitude = 25 * npbin_to_dec(np.delete(raw_alt, 7)) - 1000
            else:
                altitude = 99999  # Q bit = 0 means altitude > 50175 and increment is 100ft
        else:
            altitude = npbin_to_dec(raw_alt)/0.304
        return altitude


class ModeS_general:
    def __str__(self):
        return "ModeS MSG"
    # Placeholder for modeS implementation
    pass
