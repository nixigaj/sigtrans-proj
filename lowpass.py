from scipy.signal import cheby1

# Function to create a Chebyshev Type I lowpass filter of order 6.
# Great roll-off and infinite attenuation helps to not disturb other channels.

def create_lowpass_filter(fs, f_cutoff, R_p, R_s):

    # Normalize frequency by Nyquist frequency
    nyquist = fs / 2
    Wn = f_cutoff / nyquist

    # Design the filter using second-order sections for performance and stability improvements
    sos = cheby1(N=6, rp=R_p, Wn=Wn, btype='lowpass', output='sos')
    return sos

