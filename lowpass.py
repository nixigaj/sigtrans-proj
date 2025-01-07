from scipy.signal import cheby1, sosfreqz
import numpy as np
import matplotlib.pyplot as plt

# Function to create the Chebyshev Type I lowpass filter


def create_lowpass_filter(fs, f_cutoff, R_p, R_s):
    """
    Create a Chebyshev Type I lowpass filter.

    Parameters:
    fs (int): Sampling frequency in Hz.
    f_cutoff (float): Cutoff frequency in Hz.
    R_p (float): Passband ripple in dB.
    R_s (float): Stopband attenuation in dB.

    Returns:
    sos (ndarray): Second-order sections of the filter.
    """
    # Normalize frequency by Nyquist frequency
    nyquist = fs / 2
    Wn = f_cutoff / nyquist  # Cutoff frequency (normalized)

    # Design the Chebyshev Type I lowpass filter using second-order sections (sos)
    sos = cheby1(N=6, rp=R_p, Wn=Wn, btype='lowpass', output='sos')
    return sos

