"""
Interface with SciPy filter functions.

Data passed into this module is pure Python. Data is converted into usable form
to pass into respective functions and returned as pure Python.
"""


from utils.qtshim import logging
log = logging.getLogger(__name__)

try:
    import numpy
except ImportError:
    log.error("Numpy not available. Did you install Numpy properly?")
try:
    import scipy.signal as sig
except ImportError:
    log.error("Scipy not available. Did you install Scipy properly?")



def create_filter(low, high, order, pass_type=None):
    # type: (float, float, int, str) -> Tuple(List[float], List[float])
    """
    :param low: Low-end cutoff for highpass filter.
    :param high: High-end cutoff for lowpass filter.
    :param order: Order index of filter - higher order is sharper frequency response falloff.
    :param pass_type: {"lowpass", "highpass", "bandpass", "bandstop"}

    :return b, a: Polynomial arrays of the filter - to be plugged into sig.lfilter(b, a, x).
    :return type: Numpy arrays
    """
    if pass_type == "lowpass":
        critical = high
    elif pass_type == "highpass":
        critical = low
    elif pass_type == "bandpass":
        critical = [low, high]

    b, a = sig.butter(order, critical, btype=pass_type, analog=False, output='ba')

    return b, a


def filter_list(b, a, data):
    # type: (List[float], List[float], List[float]) -> List[float]
    """
    :param b: Numerator polynomial Numpy array of the filter.
    :param a: Denominator polynomial Numpy array of the filter.
    :param data: Python list of data to be filtered.

    :return y: Python list of filtered data - converted from Numpy array.
    """
    data = numpy.asarray(data)

    y = sig.filtfilt(
        b, a, data,
        # method="pad",
        # padlen=4,
        # padtype=None,
        # method="gust",
        # irlen=None,
    )
    y = y.tolist()

    return y
