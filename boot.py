# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal
# this is a special version for EMF
#pyb.usb_mode('CDC+MSC') # act as a serial and a storage device
#pyb.usb_mode('CDC+HID') # act as a serial device and a mouse

import pyb
import os
import micropython
import json

micropython.alloc_emergency_exception_buf(100)

m = "bootstrap.py"
if "main.py" in os.listdir():
    m = "main.py"
elif "apps" in os.listdir():
	apps = os.listdir("apps")
	if ("home" in apps) and ("main.py" in os.listdir("apps/home")):
		m = "apps/home/main.py"
	elif ("app_library" in apps) and ("main.py" in os.listdir("apps/app_library")):
		m = "apps/app_library/main.py"

# must set USB mode before calling pyb.main()
try:
    with open('main.json', 'r') as f:
        main_dict = json.loads(f.read())
        u = main_dict.get('usb_mode')
        if u:
            pyb.usb_mode(u)
except OSError:
    pass
pyb.main(m)
