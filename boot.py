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
            if 'HID' in u:
                import binascii
                hid_scls = main_dict.get('usb_hid_subclass', pyb.hid_mouse[0])
                hid_proto = main_dict.get('usb_hid_protocol', pyb.hid_mouse[1])
                hid_max_len = main_dict.get('usb_hid_max_packet_len', pyb.hid_mouse[2])
                hid_poll = main_dict.get('usb_hid_polling_interval', pyb.hid_mouse[3])
                hid_desc_hex = main_dict.get('usb_hid_report_descriptor', pyb.hid_mouse[4])
                hid_desc = binascii.unhexlify(hid_desc_hex)
                pyb.usb_mode(u, hid=(hid_scls, hid_proto, hid_max_len, hid_poll, hid_desc))
            else:
                pyb.usb_mode(u)
except OSError:
    pass
pyb.main(m)
