from machine import Pin, PWM, ADC
import math
import time

#random bullshit
NOTES = [
    262,  # C4
    277,  # C#4
    294,  # D4
    311,  # D#4
    330,  # E4
    349,  # F4
    370,  # F#4
    392,  # G4
    415,  # G#4
    440,  # A4
    466,  # A#4
    494,  # B4
    523,  # C5
]

# keyboard pins
key_pins = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(13)]

btn_octave = Pin(13, Pin.IN, Pin.PULL_UP)

# ADC
adc_vibrato = ADC(26)
adc_attack  = ADC(27)
adc_release = ADC(28)

# Audio
audio = PWM(Pin(16))
audio.freq(440)
audio.duty_u16(0)

octave = 0
vibrato_phase = 0.0
current_duty = 0.0

MAX_DUTY = 20000

while True:
    if btn_octave.value() == 0:
        octave ^= 1
        time.sleep_ms(200)

    vib_raw     = adc_vibrato.read_u16()
    attack_raw  = adc_attack.read_u16()
    release_raw = adc_release.read_u16()
#idk how ts work
    if vib_raw < 6553:
        vib_depth = 0.0
    else:
        vib_depth = (vib_raw - 6553) / (65535 - 6553) * 0.04

    if attack_raw < 6553:
        attack_ms = 10
    else:
        attack_ms = 10 + (attack_raw - 6553) / (65535 - 6553) * 2000

    if release_raw < 6553:
        release_ms = 10
    else:
        release_ms = 10 + (release_raw - 6553) / (65535 - 6553) * 2000

    attack_step  = MAX_DUTY / attack_ms
    release_step = MAX_DUTY / release_ms

    # keyboard
    note_freq = 0
    for i, pin in enumerate(key_pins):
        if pin.value() == 0:
            note_freq = NOTES[i]
            break

    if note_freq:
        freq = note_freq * (2 if octave else 1)

        # Vibrato
        vibrato_phase += 0.3
        if vib_depth > 0:
            freq = int(freq + math.sin(vibrato_phase) * freq * vib_depth)

        audio.freq(freq)

        # Attack
        current_duty = min(current_duty + attack_step, MAX_DUTY)
        audio.duty_u16(int(current_duty))

    else:
        # Release
        if current_duty > 0:
            current_duty = max(current_duty - release_step, 0)
            audio.duty_u16(int(current_duty))
        else:
            audio.duty_u16(0)
            vibrato_phase = 0.0

#absolute cinema l_o-o_l 