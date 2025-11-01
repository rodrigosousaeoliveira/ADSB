from rtlsdr import RtlSdr
from ADSBMod import Capture, npbin_to_dec, TC_MSG_TYPE, Aircrafts
from datetime import datetime
import requests
import json
import time
import threading

# SDR CONFIG
sdr = RtlSdr()
sdr.sample_rate = 2.4e6 # Hz
sdr.center_freq = 1090e6   # Hz
sdr.freq_correction = 60  # PPM
sdr.gain = 49.6

acs = Aircrafts()

def send_updates():
    UPDATE_EVERY = 5
    last_time = 0
    while True:
        time.sleep(0.1)
        t = time.time()
        if t-last_time>=UPDATE_EVERY:
            send = acs.get_current_acs()
            last_time = t
            print("Sending Updates...")
            print(send)
            response = requests.post(
                'http://localhost:3001/api/senddata',
                json=send,  # O requests converte automaticamente para JSON
                headers={'Content-Type': 'application/json'},
                timeout=10  # Timeout de 10 segundos
    )
            
def process_signals():
    while True:
        # SDR READ SAMPLES
        t0 = time.time()
        capture_time = datetime.now()
        timestamp = capture_time.strftime("%Y%m%d_%H%M%S")
        x = sdr.read_samples(3e4)
        #sdr.close()
        
        # THRESHOLD
        
        recording = Capture(x, sdr.sample_rate)
        recording.sync(2e6)
        recording.threshold_cap(0.4)
        recording.detect_preambles()
        recording.get_frames(acs)    
        
        # for frame in recording.frames:
        #     print("\n############ FRAME ############")
        #     print(bin(npbin_to_dec(frame.data)))
        #     print("ERROR COUNT: ", frame.errors)
        #     print("|  DF  | Downlink format:      ", frame.df)
        #     print("|  CA  | Capability:           ", frame.ca)
        #     print("| ICAO | Transponder ICAO Addr:", frame.icao)
        #     print("|  ME  | *Message Type:        ", frame.msgtype,
        #           " ", TC_MSG_TYPE[frame.msgtype])
        #     print(frame.msg)
        print("Loop time: ", time.time()-t0)
        del recording
        
# Criar e iniciar as threads
thread1 = threading.Thread(target=send_updates, daemon=True)
thread2 = threading.Thread(target=process_signals, daemon=True)

thread1.start()
thread2.start()

print("✅ Ambas threads iniciadas!")

# Manter o programa principal rodando
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Programa encerrado pelo usuário")