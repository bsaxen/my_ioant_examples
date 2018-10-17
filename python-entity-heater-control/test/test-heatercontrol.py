# =============================================
# File: test-heatercontrol.py
# Author: Benny Saxen
# Date: 2018-10-16
# Description: IOANT heater control algorithm
# 90 degrees <=> 1152/4 steps = 288
# =============================================

import logging
import hashlib
import math
import urllib
import urllib2
import time
import datetime

r_inertia = 0
#===================================================
def read_data (row):
#===================================================
	global temperature_indoor
	global temperature_outdoor
	global temperature_water_in
	global temperature_water_out
	global temperature_smoke

	try:
		with open("test.work",'r') as f:
			content = f.readlines()
			line = content[row]
			print line
			line2 = line.split(' ')
			temperature_indoor = float(line2[0])
			temperature_outdoor = float(line2[1])
			temperature_water_in = float(line2[2])
			temperature_water_out = float(line2[3])
			temperature_smoke = float(line2[4])
		f.close()
		
	except:
		print("ERRROR Reading test file")
	
#===================================================
def spacecollapse_op1 ( label, typ, value ):
#===================================================
	return
	url = 'http://spacecollapse.simuino.com/scServer.php'
	data = {}
	data['op'] = 1
	data['label'] = label
	data['type'] = typ
	data['value'] = value

	values = urllib.urlencode(data)
	req = url + '?' + values
	try: response = urllib2.urlopen(req)
	except urllib2.URLError as e:
		print e.reason
	the_page = response.read()

#===================================================
def spacecollapse_op2 ( label, param ):
#===================================================
	return
	url = 'http://spacecollapse.simuino.com/scServer.php'
	data = {}
	data['op'] = 2
	data['label'] = label
	data['param'] = param

	values = urllib.urlencode(data)
	req = url + '?' + values
	try: response = urllib2.urlopen(req)
	except urllib2.URLError as e:
		print e.reason
	the_page = response.read()

#=====================================================
def write_position(pos):
    try:
        f = open("position.work",'w')
        s = str(pos)
        f.write(s)
        f.close()
    except:
        print "ERROR write to position file"
    return
#=====================================================
def read_position():
    try:
        f = open("position.work",'r')
        pos = int(f.read())
        f.close()
    except:
        print("WARNING Reading position file")
        f = open("position.work",'w')
        s = str(0)
        f.write(s)
        f.close()
        pos = 0
    return pos
#=====================================================
def write_history(message):
    try:
        f = open("history.work",'a')
	f.write(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")+" ")
        f.write(message)
        f.write('\n')
        f.close()
    except:
        print "ERROR write to history file"
    return
#=====================================================
def write_log(message):
    try:
        f = open("log.work",'a')
        f.write(message)
        f.write('\n')
        f.close()
    except:
        print "ERROR write to log file"
    return
#=====================================================
def write_ML(pos,temp):
    try:
	message = str(pos) + " " + str(temp)
        f = open("ML.work",'a')
        f.write(message)
        f.write('\n')
        f.close()
    except:
        print "ERROR write to ML file"
    return

#=====================================================
def init_history():
    try:
        f = open("history.work",'w')
        f.write("===== History =====")
        f.write('\n')
        f.close()
    except:
        print "ERROR init history file"
    return
#=====================================================
def init_log():
    try:
        f = open("log.work",'w')
        f.write("===== Log =====")
        f.write('\n')
        f.close()
    except:
        print "ERROR init log file"
    return
#=====================================================
def publishStepperMsg(steps, direction):
	global g_stepperpos
	msg = "ORDER steps to move: "+str(steps) + " dir:" + str(direction)
	write_history(msg)
	print msg
	
	if steps > 500: # same limit as stepper device
		print "Too many steps "+str(steps)
        return
#=====================================================
def init_log():
    try:
        f = open("log.work",'w')
        f.write("===== Log =====")
        f.write('\n')
        f.close()
    except:
        print "ERROR init log file"
    return
    write_position(g_stepperpos)
#=====================================================
def heater_model():
	global g_minsteps,g_maxsteps,g_defsteps
	global g_minsmoke
	global g_mintemp,g_maxtemp
	global g_minheat,g_maxheat
	global g_x_0,g_y_0
	global g_relax
	global r_inertia
	global g_current_position
	global r_uptime
	global g_state
	global g_mode
	global g_inertia
	global g_uptime
	global temperature_indoor
	global temperature_outdoor
	global temperature_water_in
	global temperature_water_out
	global temperature_smoke
	global timeout_temperature_indoor
	global timeout_temperature_outdoor
	global timeout_temperature_water_in
	global timeout_temperature_water_out
	global timeout_temperature_smoke
	global STATE_INIT
	global STATE_OFF
	global STATE_WARMING
	global STATE_ON
	global MODE_OFFLINE
	global MODE_ONLINE
	init_log()
	CLOCKWISE = 0
	COUNTERCLOCKWISE = 1

	coeff1 = (g_maxheat - g_y_0)/(g_mintemp - g_x_0)
	mconst1 = g_y_0 - coeff1*g_x_0
	coeff2 = (g_y_0 - g_minheat)/(g_x_0 - g_maxtemp)
	mconst2 = g_minheat - coeff2*g_maxtemp

	y = 999
	energy = 999
	steps = 999
	all_data_is_new = 0
	old_data = 0

	# If necessary data not available: do nothing
	ndi = 0
	if temperature_outdoor == 999:
		message = "No data - temperature_outdoor"
		write_log(message)
		#write_history(message)
		ndi = ndi + 1

	if temperature_water_out == 999:
		message = "No data - temperature_water_out"
		write_log(message)
		#write_history(message)
		ndi = ndi + 1

	if temperature_water_in == 999:
		message = "No data - temperature_water_in"
		write_log(message)
		#write_history(message)
		ndi = ndi + 1

	if temperature_smoke == 999:
		message = "No data - temperature_smoke"
		write_log(message)
		#write_history(message)
		ndi = ndi + 1

		print ndi

	if ndi == 0:
		all_data_is_available = 1
	else:
		all_data_is_available = 0

	old_data = 0

	timeout_temperature_indoor -= 1
	timeout_temperature_outdoor -= 1
	timeout_temperature_water_in -= 1
	timeout_temperature_water_out -= 1
	timeout_temperature_smoke -= 1

	if timeout_temperature_indoor < 1:
		message = "Old data - temperature_indoor " + str(timeout_temperature_indoor)
		write_log(message)
		write_history(message)
		old_data= 1
	if timeout_temperature_outdoor < 1:
		message = "Old data - temperature_outdoor " + str(timeout_temperature_outdoor)
		write_log(message)
		write_history(message)
		old_data= 1
	if timeout_temperature_water_in < 1:
		message = "Old data - temperature_water_in " + str(timeout_temperature_water_in)
		write_log(message)
		write_history(message)
		old_data= 1

	if timeout_temperature_water_out < 1:
		message = "Old data - temperature_water_out " + str(timeout_temperature_water_out)
		write_log(message)
		write_history(message)
		old_data= 1
	if timeout_temperature_smoke < 1:
		message = "Old data - temperature_smoke " + str(timeout_temperature_smoke)
		write_log(message)
		write_history(message)
		old_data= 1


	write_log("===== Heater Model =====")
	if g_mode == MODE_OFFLINE:
		if all_data_is_available == 1:
			g_mode = MODE_ONLINE
			r_inertia = g_inertia
	if g_mode == MODE_ONLINE:
		old_data = 0
		if old_data == 1:
			g_mode = MODE_OFFLINE
		if g_state == STATE_OFF:
			r_uptime -= 1
			if r_uptime < 0:
				r_uptime = 0
			if temperature_smoke > g_minsmoke:
				g_state = STATE_WARMING
		if g_state == STATE_WARMING:
			r_uptime += 1
			if r_uptime == g_uptime:
				g_state = STATE_ON
			if temperature_smoke < g_minsmoke:
				g_state = STATE_OFF
				r_uptime = 0
		if g_state == STATE_ON:
			action = 0
			if r_inertia > 0:
				r_inertia -= 1
				action += 1
			if temperature_smoke < g_minsmoke:
				action += 2
				g_state = STATE_OFF
				r_uptime = 0
			if temperature_indoor > 20:
				action += 4
			if temperature_water_in > temperature_water_out:
				action += 8

			temp = temperature_outdoor

			if temp > g_maxtemp:
				temp = g_maxtemp
			if temp < g_mintemp:
				temp = g_mintemp

			if temp < g_x_0:
				y = coeff1*temp + mconst1
			else:
				y = coeff2*temp + mconst2

			steps = (int)(y - temperature_water_out)*g_relax

			energy = temperature_water_out - temperature_water_in

			if steps > 0:
				direction = COUNTERCLOCKWISE
				if g_current_position + steps > 288:
					steps = 0
			if steps < 0:
				direction = CLOCKWISE
				if g_current_position + steps < 0:
					steps = 0

			if steps > g_maxsteps:
				steps = g_maxsteps
			if steps < g_minsteps:
				steps = 0

			go = 1
			print "action " + str(action)
			c = action & 0x0001
			print "c1 " + str(c)
			if c == 1:
				go = 0

			c = action & 0x0004
			print "c4 " + str(c)
			if c == 1:
				go = 0

			if steps == 0:
				go = 0

			if go == 1 :
				#publishStepperMsg(steps, direction)
				print "Move Stepper " + str(steps) + " " + str(direction)
				r_inertia = g_inertia
				if direction == COUNTERCLOCKWISE:
					g_current_position += steps
				if direction == CLOCKWISE:
					g_current_position -= steps
#========================================================================
	status = str(r_uptime) + " state " + str(g_state) + " target=" + str(y) + "("+str(temperature_water_out)+")" + " Energy " + str(energy) + " countdown " + str(r_inertia) + " steps " + str(steps)
	status = status + "Pos=" + str(g_current_position) + " indoor " + str(timeout_temperature_indoor) + " outdoor " + str(timeout_temperature_outdoor)
	status = status + " mode " + str(g_mode)
	print status
	write_log(status)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_status','status', g_state)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_mode','mode', g_mode)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_position','position', g_current_position)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_inertia','inertia', r_inertia)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_uptime','uptime', r_uptime)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_target','target', y)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_steps','steps', steps)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_energy','energy', energy)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_timeout_indoor','timeout_indoor', timeout_temperature_indoor)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_timeout_outdoor','timeout_outdoor', timeout_temperature_outdoor)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_timeout_water_in','timeout_water_in', timeout_temperature_water_in)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_timeout_water_out','timeout_water_out', timeout_temperature_water_out)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_timeout_smoke','timeout_smoke', timeout_temperature_smoke)
	return

#=====================================================
def setup(configuration):
    # Configuration
	global g_minsteps,g_maxsteps,g_defsteps
	global g_minsmoke
	global g_mintemp,g_maxtemp
	global g_minheat,g_maxheat
	global g_x_0,g_y_0
	global g_uptime
	global g_relax
	global r_inertia
	global g_current_position
	global r_uptime
	global g_state
	global g_mode
	global g_inertia
	global STATE_INIT
	global STATE_OFF
	global STATE_WARMING
	global STATE_ON
	global MODE_OFFLINE
	global MODE_ONLINE

	STATE_INIT = 0
	STATE_OFF = 1
	STATE_WARMING = 2
	STATE_ON = 3
	MODE_OFFLINE = 1
	MODE_ONLINE = 2
	g_minsteps = 5
	g_maxsteps = 30
	g_defsteps = 10
	g_minsmoke = 27
	g_mintemp = -7
	g_maxtemp = 10
	g_minheat = 20
	g_maxheat = 40
	g_x_0 = 0
	g_y_0 = 35
	g_relax = 3.0
	g_current_position = read_position()
	global temperature_indoor
	global temperature_outdoor
	global temperature_water_in
	global temperature_water_out
	global temperature_smoke
	temperature_indoor    = 999
	temperature_outdoor   = 999
	temperature_water_in  = 999
	temperature_water_out = 999
	temperature_smoke     = 999
	global timeout_temperature_indoor
	global timeout_temperature_outdoor
	global timeout_temperature_water_in
	global timeout_temperature_water_out
	global timeout_temperature_smoke
	timeout_temperature_indoor = 60
	timeout_temperature_outdoor = 60
	timeout_temperature_water_in = 60
	timeout_temperature_water_out = 60
	timeout_temperature_smoke = 60

	g_minsteps = 6
	g_maxsteps = 40
	g_defsteps = 30
	g_minsmoke = 25
	g_mintemp = -7
	g_maxtemp = 15
	g_minheat = 20
	g_maxheat = 40
	g_x_0 = 0
	g_y_0 = 36
	g_uptime = 3600
	g_inertia = 480
	g_relax = 1.5

	g_state = STATE_OFF
	g_mode = MODE_OFFLINE
	r_inertia = g_inertia
	r_uptime = g_uptime

	spacecollapse_op1('test_kil_kvv32_heatercontrol_status','status', g_state)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_position','position', g_current_position)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_inertia','inertia', r_inertia)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_uptime','uptime', r_uptime)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_target','target', 0)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_steps','steps', 0)
	spacecollapse_op1('test_kil_kvv32_heatercontrol_energy','energy', 0)

	init_log()
	init_history()

#=====================================================
global r_inertia

# Open the file with read only permit
f = open('test.work','r')
line = f.readline()
while line:
	if r_inertia > 0:
		r_inertia -= 1
	print line
	print(line)
	line = f.readline()
	#decode line
	line2 = line.split(' ')
	temperature_indoor = float(line2[0])
	temperature_outdoor = float(line2[1])
	temperature_water_in = float(line2[2])
	temperature_water_out = float(line2[3])
	temperature_smoke = float(line2[4])
	heater_model()
	time.sleep(5)
f.close()

#=====================================================
# End of file
#=====================================================
