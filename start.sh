source venv/bin/activate
create_ap wlan0 end0 ADSBlive --no-virt &
python server.py &
python readtofile.py &
