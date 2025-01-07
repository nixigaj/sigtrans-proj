import numpy as np
from scipy.signal import sosfreqz
import matplotlib.pyplot as plt
from bandpass import create_bandpass_filter
from lowpass import create_lowpass_filter

# Properties
fs = 48000  # Sampling frequency
f_low, f_high = 4300, 4500  # Passband frequencies
f_stop_low, f_stop_high = 4250, 4550  # Stopband frequencies
R_p = 1     # Passband ripple
R_s = 40    # Stopband attenuation

# Create the bandpass filter
sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)

# Compute the frequency response of the bandpass filter
worN = 10000 # Increases the graphical resolution
frequencies, h = sosfreqz(sos, worN=worN, fs=fs)

# Plot range for bandpass
freq_range_mask_bp = (frequencies >= 4100) & (frequencies <= 4700)

# Lowpass filter specifications
fl_cutoff = 250  # Cutoff frequency
fls = 48000  # Sampling frequency
lR_p = 1  # Passband ripple
lR_s = 40  # Stopband attenuation

# Normalize frequency
nyquist = fs / 2
Wn = fl_cutoff / nyquist

# Create the lowpass filter
sos_lowpass = create_lowpass_filter(fls, fl_cutoff, lR_p, lR_s)

# Compute the frequency response of the lowpass filter
frequencies_lowpass, h_lowpass = sosfreqz(sos_lowpass, worN=worN, fs=fls)

# Plot range for lowpass
freq_range_mask_lp = (frequencies_lowpass >= 0) & (frequencies_lowpass <= 400)

# Create the merged plot
plt.figure(figsize=(12, 6))

# Plot the frequency responses
plt.subplot(1, 2, 1)
plt.plot(frequencies[freq_range_mask_bp], 20 * np.log10(
    np.abs(h[freq_range_mask_bp])), label='Bandpass Filter Frequency Response')
plt.axvline(f_low, color='green', linestyle='--', label="Passband Lower Edge")
plt.axvline(f_high, color='green', linestyle='--', label="Passband Upper Edge")
plt.axvline(f_stop_low, color='red', linestyle='--',
            label="Stopband Lower Edge")
plt.axvline(f_stop_high, color='red', linestyle='--',
            label="Stopband Upper Edge")
plt.title('Chebyshev Type I Bandpass Filter Frequency Response (4000–4800 Hz)')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.legend()
plt.grid()

plt.subplot(1, 2, 2)
plt.plot(frequencies_lowpass[freq_range_mask_lp], 20 * np.log10(np.abs(
    h_lowpass[freq_range_mask_lp])), label='Lowpass Filter Frequency Response')
plt.axvline(fl_cutoff, color='green', linestyle='--', label="Cutoff Frequency")
plt.axvline(fl_cutoff+50, color='red', linestyle='--', label="Stopband Edge")
plt.title('Chebyshev Type I Lowpass Filter Frequency Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
