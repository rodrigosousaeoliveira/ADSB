from rtlsdr import RtlSdr
from ADSBMod import Capture, npbin_to_dec, TC_MSG_TYPE, Aircrafts
from datetime import datetime
import requests
import json
import time
import threading
import numpy as np

acs = Aircrafts()

def send_updates():
    UPDATE_EVERY = 5
    while True:
        time.sleep(UPDATE_EVERY)
        send = acs.get_current_acs()
        print("Sending Updates...")
        print(send)
        response = requests.post(
            'http://localhost:3001/api/senddata',
            json=send,  # O requests converte automaticamente para JSON
            headers={'Content-Type': 'application/json'},
            timeout=10  # Timeout de 10 segundos
)
            
def process_signals():
    # SDR CONFIG
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6 # Hz
    sdr.center_freq = 1090e6   # Hz
    sdr.freq_correction = 60  # PPM
    print("Valid gains: \n", sdr.valid_gains_db)
    sdr.gain = 49.6
    print("Gain: \n", sdr.get_gain())
    plotcount = 0
    plotevery = 0
    while True:
        # SDR READ SAMPLES
        capture_time = datetime.now()
        timestamp = capture_time.strftime("%Y%m%d_%H%M%S")
        t0 = time.time()
        x = sdr.read_samples(1.5e4)[2000:]
        time.sleep(0.01)
        t1 = time.time()
        #sdr.close()
         
        # THRESHOLD
        
        recording = Capture(x, sdr.sample_rate)
        #recording.bandpass()
        recording.sync(2e6)
        recording.threshold_cap(0.38)
        recording.detect_preambles()
        recording.get_frames(acs)   
        t2 = time.time()
        # if plotevery == 100:
        #     plotevery = 0
        #     print('Plotting')
        #     recording.plot('random')
        for frame in recording.frames:
            if plotcount <= 1:
                recording.plot('adsbframe')
                plotcount += 1
            print("\n############ FRAME ############")
            print(bin(npbin_to_dec(frame.data)))
            print("ERROR COUNT: ", frame.errors)
            print("|  DF  | Downlink format:      ", frame.df)
            print("|  CA  | Capability:           ", frame.ca)
            print("| ICAO | Transponder ICAO Addr:", frame.icao)
            print("|  ME  | *Message Type:        ", frame.msgtype,
                  " ", TC_MSG_TYPE[frame.msgtype])
            print(frame.msg)
            name = str(sdr.sample_rate) + '_' + timestamp + '.npy'
            #np.save(name, x)
        del recording
        t3 = time.time()
        plotevery +=1
        # print("Total Time:      ", t3-t0)
        # print("Capture Time:    ", t1-t0, " = ", (t1-t0)/(t3-t0), "%")
        # print("Processing Time: ", t2-t1, " = ", (t2-t1)/(t3-t0), "%")
        # print("Printing Time:   ", t2-t1, " = ", (t3-t2)/(t3-t0), "%")
# Criar e iniciar as threads
thread1 = threading.Thread(target=process_signals, daemon=True)
thread2 = threading.Thread(target=send_updates, daemon=True)

thread1.start()
thread2.start()

print("✅ Ambas threads iniciadas!")

#Manter o programa principal rodando
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Programa encerrado pelo usuário")