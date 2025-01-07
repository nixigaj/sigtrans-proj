from scipy.signal import cheby1

# Function to create the Chebyshev Type I bandpass filter


def create_bandpass_filter(fs, f_low, f_high, R_p, R_s):
    """
    Create a Chebyshev Type I bandpass filter.

    Parameters:
    fs (int): Sampling frequency in Hz.
    f_low (float): Lower passband frequency in Hz.
    f_high (float): Upper passband frequency in Hz.
    R_p (float): Passband ripple in dB.
    R_s (float): Stopband attenuation in dB.

    Returns:
    sos (ndarray): Second-order sections of the filter.
    """
    # Normalize frequencies by Nyquist frequency
    nyquist = fs / 2
    W_p = [f_low / nyquist, f_high / nyquist]  # Passband (normalized)

    # Design the Chebyshev Type I bandpass filter using second-order sections (sos)
    sos = cheby1(N=6, rp=R_p, Wn=W_p, btype='bandpass', output='sos')
    return sos


