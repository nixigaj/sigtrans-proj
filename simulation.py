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
    channel_id = 15
    fc = 4400  # Set carrier frequency (adjust based on your group assignment)
    Tb = 0.04  # Set symbol duration
    fs = 44100  # Sampling frequency

    #####################################################

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

    # Convert string to bit sequence or string bit sequence to numeric bit
    # sequence
    if string_data:
        bs = wcs.encode_string(data)
    else:
        bs = np.array([bit for bit in map(int, data)])

    # Encode baseband signal
    xb = wcs.encode_baseband_signal(bs, Tb, fs)

    #####################################################

    # Carrier signal wc
    xc = np.sin(2 * np.pi * fc * np.arange(len(xb)) / fs)

    xm = xb * xc  # Modulated signal

    # Normalize the signal to be within the range of [-1, 1] for audio playback
    # xm = xm / np.max(np.abs(xm))

    #####################################################

    # Filter specifications
    f_low = 4300  # Lower passband frequency
    f_high = 4500  # Upper passband frequency
    R_p = 1  # Passband ripple in dB
    R_s = 40  # Stopband attenuation in dB

    # Create the bandpass filter
    sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)

    # Apply the bandpass filter to the modulated signal
    filtered_signal = sosfilt(sos, xm)

    #####################################################
    # Channel simulation
    yr = wcs.simulate_channel(filtered_signal, fs, channel_id)

    # Step 2: Filtering (Bandpass filter)
    sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)
    filtered_signal = sosfilt(sos, yr.flatten())

    # Step 3: IQ Demodulation (complex demodulation)
    I = filtered_signal * np.cos(2 * np.pi * fc *
                                np.arange(len(filtered_signal)) / fs)
    Q = -1 * filtered_signal * \
        np.sin(2 * np.pi * fc * np.arange(len(filtered_signal)) / fs)

    # Create the lowpass filter
    fl_high = 250  # Cutoff frequency for the lowpass filter
    Rl_p = 1  # Passband ripple in dB
    Rl_s = 40  # Stopband attenuation in dB
    sos_low = create_lowpass_filter(fs, fl_high, Rl_p, Rl_s)

    # Apply the lowpass filter to I and Q separately
    I_filtered = sosfilt(sos_low, I)
    Q_filtered = sosfilt(sos_low, Q)

    # Now I_filtered and Q_filtered are the lowpass filtered I and Q components
    # Combine them back to get the filtered baseband signal
    yb_filtered = I_filtered + 1j * Q_filtered

    # Step 6: Decode the baseband signal
    bit_sequence = wcs.decode_baseband_signal(np.abs(yb_filtered), np.angle(yb_filtered), Tb, fs)

    # Step 7: Decode the bit sequence into a string
    data_rx = wcs.decode_string(bit_sequence)
    print('Received: ' + data_rx)



if __name__ == "__main__":
    main()
