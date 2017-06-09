"""
Interface with SciPy filter functions.

Data passed into this module is pure Python. Data is converted into usable form
to pass into respective functions and returned as pure Python.
"""

import numpy
import scipy.signal as sig
from utils.qtshim import logging

log = logging.getLogger(__name__)


def create_filter(fps, low, high, order, pass_type=None):
    """
    :param fps: Frequency of samples.
    :param low: Low-end cutoff for highpass filter.
    :param high: High-end cutoff for lowpass filter.
    :param order: Order index of filter - higher order is sharper frequency response falloff.
    :param pass_type: {"lowpass", "highpass", "bandpass", "bandstop"}

    :return b, a: Polynomial arrays of the filter - to be plugged into sig.lfilter(b, a, x).
    """
    if pass_type == "lowpass":
        critical = high
    elif pass_type == "highpass":
        critical = low
    elif pass_type == "bandpass":
        critical = [low, high]

    nyq = 0.5 * float(fps)
    low = float(low) / nyq
    high = float(high) / nyq

    b, a = sig.butter(order, critical, btype=pass_type, analog=True, output='ba')

    b = b.tolist()
    a = a.tolist()

    return b, a


def filter_list(b, a, data):
    """
    :param b: Numerator polynomial list of the filter.
    :param a: Denominator polynomial list of the filter.
    :param data: Python list of data to be filtered.

    :return y: Python list of filtered data - converted from Numpy array.
    """
    b = numpy.asarray(b)
    a = numpy.asarray(a)
    data = numpy.asarray(data)

    y = sig.filtfilt(b, a, data, padtype=None)
    y = y.tolist()

    return y
