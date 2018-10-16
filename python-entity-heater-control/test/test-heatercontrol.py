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
	spacecollapse_op1('kil_kvv32_heatercontrol_status','status', g_state)
	spacecollapse_op1('kil_kvv32_heatercontrol_mode','mode', g_mode)
	spacecollapse_op1('kil_kvv32_heatercontrol_position','position', g_current_position)
	spacecollapse_op1('kil_kvv32_heatercontrol_inertia','inertia', r_inertia)
	spacecollapse_op1('kil_kvv32_heatercontrol_uptime','uptime', r_uptime)
	spacecollapse_op1('kil_kvv32_heatercontrol_target','target', y)
	spacecollapse_op1('kil_kvv32_heatercontrol_steps','steps', steps)
	spacecollapse_op1('kil_kvv32_heatercontrol_energy','energy', energy)
	spacecollapse_op1('kil_kvv32_heatercontrol_timeout_indoor','timeout_indoor', timeout_temperature_indoor)
	spacecollapse_op1('kil_kvv32_heatercontrol_timeout_outdoor','timeout_outdoor', timeout_temperature_outdoor)
	spacecollapse_op1('kil_kvv32_heatercontrol_timeout_water_in','timeout_water_in', timeout_temperature_water_in)
	spacecollapse_op1('kil_kvv32_heatercontrol_timeout_water_out','timeout_water_out', timeout_temperature_water_out)
	spacecollapse_op1('kil_kvv32_heatercontrol_timeout_smoke','timeout_smoke', timeout_temperature_smoke)
	return
#=====================================================
