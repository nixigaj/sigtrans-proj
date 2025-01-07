import numpy as np
import sounddevice as sd
from scipy.signal import sosfilt
from lowpass import create_lowpass_filter
from bandpass import create_bandpass_filter
import wcslib as wcs

# Parameters
Tb = 0.04   # Symbol duration
fs = 48000 # Sampling frequency
duration = 20 # Recording duration
f_low = 4300  # Lower passband frequency
f_high = 4500  # Upper passband frequency
R_p = 1  # Passband ripple
R_s = 40  # Stopband attenuation
fc = 4400  # Carrier frequency

# Step 1: Record the signal
print("Recording...")
recorded_signal = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
sd.wait()
print("Recording completed.")

# Step 2: Bandpass filtering
sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)
filtered_signal = sosfilt(sos, recorded_signal.flatten())

# Step 3: IQ Demodulation
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

# Step 7: Decode the bit sequence into a bytes
data_rx = wcs.decode_string(bit_sequence)

print('Received: ' + data_rx)
