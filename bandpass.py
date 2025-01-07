from scipy.signal import cheby1

# Function to create a Chebyshev Type I bandpass filter of order 6.
# Great roll-off and infinite attenuation helps to not disturb other channels.

def create_bandpass_filter(fs, f_low, f_high, R_p, R_s):

    # Normalize frequencies by Nyquist frequency
    nyquist = fs / 2
    W_p = [f_low / nyquist, f_high / nyquist]

    # Design the filter using second-order sections for performance and stability improvements
    sos = cheby1(N=6, rp=R_p, Wn=W_p, btype='bandpass', output='sos')
    return sos


