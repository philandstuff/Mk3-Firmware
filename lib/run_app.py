
def reset_and_run(path, usb_mode=None, hid_scls=None, hid_proto=None, hid_max_len=None, hid_poll=None, hid_desc=None):
	import stm
	import pyb
#	if stm.mem8[0x40002850] == 0:   # this battery backed RAM section is set to 0 when the name screen runs
	with open('main.json', 'w') as f:
		f.write('{"main":"' + path + '"')
		if usb_mode: f.write(',"usb_mode":"' + usb_mode + '"')
		if hid_scls: f.write(',"usb_hid_subclass":' + hid_scls )
		if hid_proto: f.write(',"usb_hid_protocol":' + hid_proto)
		if hid_max_len: f.write(',"usb_hid_max_packet_len":' + hid_max_len)
		if hid_poll: f.write(',"usb_hid_polling_interval":' + hid_proto)
		if hid_desc: f.write(',"usb_hid_report_descriptor":"' + hid_desc + '"')
		f.write('}')
#		stm.mem8[0x40002850] = 2    #set this address to != 0 so this if statement doesnt run next time
	pyb.hard_reset()

def run_app(path):
#	buttons.enable_menu_reset()
	try:
		mod = __import__(path)
		if "main" in dir(mod):
			mod.main()
	except Exception as e:
		import sys
		import uio
		import ugfx
		s = uio.StringIO()
		sys.print_exception(e, s)
		ugfx.clear()
		ugfx.set_default_font(ugfx.FONT_SMALL)
		w=ugfx.Container(0,0,ugfx.width(),ugfx.height())
		l=ugfx.Label(0,0,ugfx.width(),ugfx.height(),s.getvalue(),parent=w)
		w.show()
		raise(e)
	import onboard
	import stm
	stm.mem8[0x40002850] = 0x9C
	import pyb
	pyb.hard_reset()
