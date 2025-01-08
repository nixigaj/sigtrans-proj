import sys
import numpy as np
import wcslib as wcs
import sounddevice as sd
from scipy.signal import sosfilt
from bandpass import create_bandpass_filter

# Properties
fc = 4400  # Carrier frequency
Tb = 0.02  # Symbol duration
fs = 48000  # Sampling frequency

# Detect input or set defaults
string_data = True
if len(sys.argv) == 2:
    data = str(sys.argv[1])

elif len(sys.argv) == 3 and str(sys.argv[1]) == '-b':
    string_data = False
    data = str(sys.argv[2])

else:
    data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    print(f'Transmitting "{data}"', file=sys.stderr)
# Convert string to bit sequence or string bit sequence to numeric bit sequence
if string_data:
    bs = wcs.encode_string(data + "a")
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

# Play the filtered signal
sd.play(filtered_signal, fs)
sd.wait()
