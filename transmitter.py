import sys
import numpy as np
import wcslib as wcs
import sounddevice as sd
from scipy.signal import sosfilt

from bandpass import create_bandpass_filter

# Example pseudocode
fc = 4400  # Set carrier frequency (adjust based on your group assignment)
Tb = 0.04  # Set symbol duration
fs = 48000  # Sampling frequency

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

xm = xb * xc # Modulated signal

# Normalize the signal to be within the range of [-1, 1] for audio playback
#xm = xm / np.max(np.abs(xm))

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

# Play the modulated signal using sounddevice
sd.play(filtered_signal, fs)

# Wait until sound is finished playing
sd.wait()
