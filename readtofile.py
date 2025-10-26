from rtlsdr import RtlSdr
from adsbMod import Capture, Aircrafts, npbin_to_dec, TC_MSG_TYPE
from datetime import datetime

# SDR CONFIG
sdr = RtlSdr()
sdr.sample_rate = 2.4e6 # Hz
sdr.center_freq = 1090e6   # Hz
sdr.freq_correction = 60  # PPM
print(sdr.valid_gains_db)
sdr.gain = 49.6
print(sdr.gain)

acs = Aircrafts()

while True:
    # SDR READ SAMPLES
    capture_time = datetime.now()
    timestamp = capture_time.strftime("%Y%m%d_%H%M%S")
    x = sdr.read_samples(3e4)[3000:]
    #sdr.close()
    #time.sleep(1)
    # THRESHOLD
    
    recording = Capture(x, sdr.sample_rate)
    recording.sync(2e6)
    recording.threshold_cap(0.4)
    recording.detect_preambles()
    recording.get_frames(acs)
    
    #print("Threshold = ", recording.threshold)
    # plt.plot(recording.data)
    # plt.hlines([recording.threshold, -recording.threshold], 0, 
    #             recording.data.size, colors = 'k', linestyles = 'dashed')
    # plt.grid()
    # plt.show()
    
    for frame in recording.frames:
        print("\n############ FRAME ############")
        print(bin(npbin_to_dec(frame.data)))
        print("ERROR COUNT: ", frame.errors)
        print("|  DF  | Downlink format:      ", frame.df)
        print("|  CA  | Capability:           ", frame.ca)
        print("| ICAO | Transponder ICAO Addr:", frame.icao)
        print("|  ME  | *Message Type:        ", frame.msgtype,
              " ", TC_MSG_TYPE[frame.msgtype])
        print(frame.msg)
            
            # with open('captures.csv', 'a', newline='') as f:
            #     writer = csv.writer(f)
            #     writer.writerow(np.append(frame.data.flatten(), timestamp))
                
            # if npbin_to_dec(frame.df) == 17 or npbin_to_dec(frame.df) == 18:
            #     print("\n\n\n\n\n\n\n\n\n\n\n\n FOUND A GOOD FRAME \n\n\n\n\n\n\n\n\n\n\n\n")
            #     name = str(sdr.sample_rate) + '_' + timestamp + '.npy'
            #     np.save(name, x)
    del recording

