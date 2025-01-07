#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation template for the wireless communication system project in Signals 
and Transforms.

For plain text inputs, run:
$ python3 simulation.py "Hello World!"

For binary inputs, run:
$ python3 simulation.py -b 010010000110100100100001

2020-present -- Roland Hostettler <roland.hostettler@angstrom.uu.se>
"""

import sys
import numpy as np
#from scipy import signal
#import matplotlib.pyplot as plt
import wcslib as wcs
from scipy.signal import sosfilt
from lowpass import create_lowpass_filter
from bandpass import create_bandpass_filter

def main():

    # Parameters
    channel_id = 15 # Group number
    fc = 4400  # Carrier frequency
    Tb = 0.04  # Symbol duration
    fs = 48000  # Sampling frequency

    # Detect input or set defaults
    string_data = True
    if len(sys.argv) == 2:
        data = str(sys.argv[1])

    elif len(sys.argv) == 3 and str(sys.argv[1]) == '-b':
        string_data = False
        data = str(sys.argv[2])

    else:
        print('Transmitting "Hello World!"', file=sys.stderr)
        data = "Hello World!"

    # Convert string to bit sequence or string bit sequence to numeric bit sequence
    if string_data:
        bs = wcs.encode_string(data)
    else:
        bs = np.array([bit for bit in map(int, data)])

    # Encode baseband signal
    xb = wcs.encode_baseband_signal(bs, Tb, fs)

    # Carrier signal
    xc = np.sin(2 * np.pi * fc * np.arange(len(xb)) / fs)

    # Modulated signal
    xm = xb * xc  

    # Filter specifications
    f_low = 4300  # Lower passband frequency
    f_high = 4500  # Upper passband frequency
    R_p = 1  # Passband ripple
    R_s = 40  # Stopband attenuation

    # Create the bandpass filter
    sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)

    # Bandpass filter the modulated signal
    filtered_signal = sosfilt(sos, xm)

    # Channel simulation
    yr = wcs.simulate_channel(filtered_signal, fs, channel_id)

    # Bandpass filter the recieved signal
    sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)
    filtered_signal = sosfilt(sos, yr.flatten())

    # IQ Demodulation
    I = filtered_signal * np.cos(2 * np.pi * fc * np.arange(len(filtered_signal)) / fs)
    Q = -1 * filtered_signal * np.sin(2 * np.pi * fc * np.arange(len(filtered_signal)) / fs)

    # Create the lowpass filter
    fl_high = 250  # Cutoff frequency
    Rl_p = 1  # Passband ripple
    Rl_s = 40  # Stopband attenuation
    sos_low = create_lowpass_filter(fs, fl_high, Rl_p, Rl_s)

    # Apply the lowpass filter to I and Q separately
    I_filtered = sosfilt(sos_low, I)
    Q_filtered = sosfilt(sos_low, Q)

    # Combine I_filtered and Q_filtered back to get the filtered baseband signal
    yb_filtered = I_filtered + 1j * Q_filtered

    # Step 6: Decode the baseband signal
    bit_sequence = wcs.decode_baseband_signal(np.abs(yb_filtered), np.angle(yb_filtered), Tb, fs)

    # Step 7: Decode the bit sequence into a string
    data_rx = wcs.decode_string(bit_sequence)
    print('Received: ' + data_rx)


if __name__ == "__main__":
    main()
