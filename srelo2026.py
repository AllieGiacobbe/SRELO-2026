# ===============================================================
# Micro:bit 1A (R)
# ===============================================================

right_level = -1        # -1 acts as a null value to prevent error in initialization at level 0

# Transmission
radio.set_group(1)
radio.set_transmit_power(7)
radio.set_frequency_band(70)

# Pace function
# Machine learning detects the user's speed level and broadcasts this information to Micro:bit 2
def updatePace(level: number):
    global right_level
    right_level = level
    radio.send_number(level)

# Function calls and Machine Learning
def on_level_0():
    updatePace(0)
ml.on_start(ml.event.still, on_level_0)

def on_level_1():
    updatePace(1)
ml.on_start(ml.event.level1, on_level_1)

def on_level_2():
    updatePace(2)
ml.on_start(ml.event.level2, on_level_2)

def on_level_3():
    updatePace(3)
ml.on_start(ml.event.level3, on_level_3)

def on_level_4():
    updatePace(4)
ml.on_start(ml.event.level4, on_level_4)

def on_level_5():
    updatePace(5)
ml.on_start(ml.event.level5, on_level_5)

def on_level_6():
    updatePace(6)
ml.on_start(ml.event.level6, on_level_6)

def on_level_7():
    updatePace(7)
ml.on_start(ml.event.level7, on_level_7)

def on_level_8():
    updatePace(8)
ml.on_start(ml.event.level8, on_level_8)

def on_level_9():
    updatePace(9)
ml.on_start(ml.event.level9, on_level_9)

def on_level_10():
    updatePace(10)
ml.on_start(ml.event.level10, on_level_10)


# ===============================================================
# Micro:bit 1B (L)
# Mirrors Micro:bit 1A program with added offset to distinguish the left ankle.
# ===============================================================

left_level = -1

# Transmission
radio.set_group(1)
radio.set_transmit_power(7)
radio.set_frequency_band(70)

# Pace Function
def updatePace(level: number):
    global left_level
    left_level = level
    radio.send_number(level + 100)      # Offset so Micro:bit 2 differentiates left ankle input

# Function Calls and ML
def on_level_0():
    updatePace(0)
ml.on_start(ml.event.still, on_level_0)

def on_level_1():
    updatePace(1)
ml.on_start(ml.event.level1, on_level_1)

def on_level_2():
    updatePace(2)
ml.on_start(ml.event.level2, on_level_2)

def on_level_3():
    updatePace(3)
ml.on_start(ml.event.level3, on_level_3)

def on_level_4():
    updatePace(4)
ml.on_start(ml.event.level4, on_level_4)

def on_level_5():
    updatePace(5)
ml.on_start(ml.event.level5, on_level_5)

def on_level_6():
    updatePace(6)
ml.on_start(ml.event.level6, on_level_6)

def on_level_7():
    updatePace(7)
ml.on_start(ml.event.level7, on_level_7)

def on_level_8():
    updatePace(8)
ml.on_start(ml.event.level8, on_level_8)

def on_level_9():
    updatePace(9)
ml.on_start(ml.event.level9, on_level_9)

def on_level_10():
    updatePace(10)
ml.on_start(ml.event.level10, on_level_10)


# ===============================================================
# MICRO:BIT 2
# ===============================================================

# Transmission
radio.set_group(1)
radio.set_transmit_power(7)
radio.set_frequency_band(70)

# Core RAS Variables
right_level = -1        # -1 indicates no gait level has been received yet.
left_level = -1
target_cadence = 0
cadence_int = 0         # Time between each tick

ras_active = False  # When the user first turns the device on, metronome is off
ras_override = False    # User has the option to turn metronome on/off in the later function on_button_pressed_b

# Variables for SI Calculation
MS = 2000
last_right_update = 0
last_left_update = 0

SI_TRIGGER = 15     # SI > 15% indicates clinical gait asymmetry (Robinson et al., 1987).
current_si = -1     # Null value to prevent malfunction upon code initialization

# Arrays for Output Management
speed_mapping = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]   # Velocities increasing at 10% (for SI calculation) (Bella et al., 2017)
cadence_mapping = [0, 17, 26, 34, 43, 51, 60, 69, 77, 86, 94]   # Cadences calculated using the cadence formula (Paker et al., 2015)

# DATA COLLECTION FOR FIG 2 -------------------------------
# true_test_level = 0
# ---------------------------------------------------------

# ASYMMMETRY DETECTION with Symmetry Index (Robinson et al., 1987)
# SI = 2 * |Vr - Vl| / (Vr + Vl) * 100
# Returns SI as an integer percentage, or -1 (null value) if insufficient data are available.
def compute_symmetry_index():
    global current_si
    now = input.running_time()

    if right_level == -1 or left_level == -1:       # Function returns if no level is recorded (original null value is kept)
        return -1
    if (now - last_right_update) > MS or (now - last_left_update) > MS: # Function returns if it hasn't been updated within 2000 ms
        return -1

    r = speed_mapping[right_level]
    l = speed_mapping[left_level]

    current_si = abs(abs(r - l) / (.5 * (r + l))) * 100     # Robinson's formula for Symmetry Index
    return int(current_si)

# Gait Regularity Verification
def verify_gait_regularity():
    global ras_active, current_si

    if ras_override:
        return

    si = compute_symmetry_index()
    if si < 0:
        return

    current_si = si

    if si > SI_TRIGGER:     # Symmetry Index > 15% triggers Rhythmic Auditory Stimulation
        ras_active = True
    else:
        ras_active = False


# Radio Data Management
def on_received_number(receivedLVL):
    global right_level, left_level
    global target_cadence, cadence_int, ras_active
    global last_right_update, last_left_update

    # DATA COLLECTION FOR FIG 2 -------------------------------
    # serial.write_line("" + true_test_level + "," + (receivedLVL - 100 if receivedLVL >= 100 else receivedLVL))
    # ---------------------------------------------------------

    computed_level = 0

    if receivedLVL >= 100:
        # strips offset from Micro:bit 1B (left ankle)
        left_level = receivedLVL - 100
        last_left_update = input.running_time()
    else:
        # Micro:bit 1A (right ankle)
        right_level = receivedLVL
        last_right_update = input.running_time()

    # DATA COLLECTION FOR FIG 3 -------------------------------
    # serial.write_line("" + input.running_time() + "," + computed_level + target_cadence)
    # ---------------------------------------------------------

    # DATA COLLECTION FOR FIG 4 -------------------------------
    # serial.write_line("" + input.running_time() + "," + (1 if receivedLVL >= 100 else 0) + "," + computed_level)
    # ---------------------------------------------------------
    
    # Asymmetry check, skipped if user locks RAS
    if ras_override == False:
        verify_gait_regularity()

    if right_level != -1 and left_level != -1:
        computed_level = int((right_level + left_level) / 2)    # Averages levels received from Micro:bits 1A and 1B
    elif right_level != -1:
        computed_level = right_level
    elif left_level != -1:
        computed_level = left_level
    else:
        # if no data is received from either ankle
        return

    # Levels clamped to valid index range
    computed_level = max(0, min(computed_level, 10))
    target_cadence = cadence_mapping[computed_level]

    if target_cadence > 0:
        cadence_int = int(60000 / target_cadence)   # Time interval (ms) between each tick
    else:
        cadence_int = 0

radio.on_received_number(on_received_number)

# METRONOMIC CADENCE OUTPUT

# DATA COLLECTION FOR FIG 5 -------------------------------
# last_beep_time = 0
# ---------------------------------------------------------

def play_ras_loop():
    global target_cadence, cadence_int, ras_active

    while True:
        if ras_active and target_cadence > 0:
            start_tick = input.running_time()

            # DATA COLLECTION FOR FIG 5 ------------------------------------
            # if last_beep_time > 0:
                # actual_interval = start_tick - last_beep_time
                # serial.write_line("" + actual_interval)
            # last_beep_time = start_tick
            # --------------------------------------------------------------

            music.play_tone (1047, 40)          # C6/standard metronome pitch, 40ms
            basic.show_icon(IconNames.HEART, 0)         # Visual indication metronome is running
            elapsed = input.running_time() - start_tick
            remainder = cadence_int - elapsed
            if remainder > 0:
                basic.pause(remainder)
            basic.clear_screen()
        else:
            basic.pause(50)

control.in_background(play_ras_loop)

# Manual initiation of RAS
# Button A
def on_button_pressed_a():
    global ras_active, ras_override

    # If RAS is active, it is turned off, and if RAS is inactive, it is turned on
    ras_active = not ras_active
    ras_override = not ras_active

    if ras_active:
        basic.show_string("V", 400)     # Visual indication RAS is active
    else:
        basic.show_string("X", 400)     # Visual indication RAS is inactive

input.on_button_pressed(Button.A, on_button_pressed_a)

# Data Visualization
# Button B
def on_button_pressed_b():
    basic.show_string("BPM: ")
    basic.show_number(target_cadence)
    basic.pause(300)
    basic.show_string("SI: ")
    if current_si >= 0:
        basic.show_number(current_si)   # Displays as integer %
    else:
        basic.show_string("--")     # Indication if not enough information
    basic.clear_screen()

input.on_button_pressed(Button.B, on_button_pressed_b)