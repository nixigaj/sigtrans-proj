import numpy as np
from scipy.signal import cheby1, sosfilt, sosfreqz
import matplotlib.pyplot as plt
from bandpass import create_bandpass_filter


# Sampling frequency and filter specifications
fs = 48000        # Sampling frequency in Hz
f_low, f_high = 4300, 4500  # Passband frequencies in Hz
f_stop_low, f_stop_high = 4250, 4550  # Stopband frequencies in Hz
R_p = 1           # Passband ripple in dB
R_s = 40          # Stopband attenuation in dB

# Create the bandpass filter
sos = create_bandpass_filter(fs, f_low, f_high, R_p, R_s)

# Number of frequency points for higher resolution
worN = 10000  # Increase for more resolution

# Compute the frequency response of the bandpass filter
frequencies, h = sosfreqz(sos, worN=worN, fs=fs)

# Mask frequencies to focus on the 4000–4800 Hz range for the bandpass filter
freq_range_mask_bp = (frequencies >= 4100) & (frequencies <= 4700)

# Lowpass filter specifications
fl_cutoff = 250  # Cutoff frequency in Hz (just above the baseband bandwidth)
fls = 48000  # Sampling frequency in Hz
lR_p = 1  # Passband ripple in dB
lR_s = 40  # Stopband attenuation in dB

# Normalize frequency
nyquist = fs / 2
Wn = fl_cutoff / nyquist

# Design Chebyshev Type I lowpass filter
sos_lowpass = cheby1(N=6, rp=lR_p, Wn=Wn, btype='lowpass', output='sos')

# Compute the frequency response of the lowpass filter
frequencies_lowpass, h_lowpass = sosfreqz(sos_lowpass, worN=worN, fs=fls)

# Mask frequencies to focus on the 0–500 Hz range for clarity
freq_range_mask_lp = (frequencies_lowpass >= 0) & (frequencies_lowpass <= 400)

# Create the merged plot
plt.figure(figsize=(12, 6))

# Plot the frequency response of the bandpass filter
plt.subplot(1, 2, 1)  # First subplot (left side)
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

# Plot the frequency response of the lowpass filter
plt.subplot(1, 2, 2)  # Second subplot (right side)
plt.plot(frequencies_lowpass[freq_range_mask_lp], 20 * np.log10(np.abs(
    h_lowpass[freq_range_mask_lp])), label='Lowpass Filter Frequency Response')
plt.axvline(fl_cutoff, color='green', linestyle='--', label="Cutoff Frequency")
plt.axvline(fl_cutoff+50, color='red', linestyle='--', label="Stopband Edge")
plt.title('Chebyshev Type I Lowpass Filter Frequency Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.legend()
plt.grid()

# Show the plot with both filters in one figure
plt.tight_layout()
plt.show()
