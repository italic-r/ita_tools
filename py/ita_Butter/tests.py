"""
Tests for ita_Butter.

Test interaction with scipy and UI.
"""

import unittest
import matplotlib.pyplot as plt
import numpy
import scipy.signal as sig
import scipy_interface


class TestScipy(unittest.TestCase):

    def test_array_create(self):
        """Test lfilter example."""
        t = numpy.linspace(-1, 1, 201)
        x = (
            numpy.sin(2 * numpy.pi * 0.75 * t * (1 - t) + 2.1) +
            0.1 * numpy.sin(2 * numpy.pi * 1.25 * t + 1) +
            0.18 * numpy.cos(2 * numpy.pi * 3.85 * t)
        )
        xn_array = x + numpy.random.randn(len(t)) * 0.08
        xn_list = xn_array.tolist()

        self.assertIsInstance(xn_array, numpy.ndarray)
        self.assertIsInstance(xn_list, list)

        return t, x, xn_array

    def test_lfilter_example(self):
        """Test lfilter example."""
        t, x, xn = self.test_array_create()
        b, a = sig.butter(3, 0.05)

        zi = sig.lfilter_zi(b, a)
        z, _ = sig.lfilter(b, a, xn, zi=zi*xn[0])
        z2, _ = sig.lfilter(b, a, z, zi=zi*z[0])
        y = sig.filtfilt(b, a, xn)

        return t, x, xn, b, a, zi, z, z2, y

    def test_matplotlib_example(self):
        """Test lfilter example."""
        t, x, xn, b, a, zi, z, z2, y = self.test_lfilter_example()

        plt.figure
        plt.plot(t, xn, 'b', alpha=0.25)
        plt.plot(t, z, 'r--')
        plt.plot(t, z2, 'r')
        plt.plot(t, y, 'k')
        # plt.plot(t, z, 'r--', t, z2, 'r', t, y, 'k')
        plt.legend(('noisy signal', 'lfilter, once', 'lfilter, twice', 'filtfilt'), loc='best')
        plt.grid(True)
        plt.show()

    def test_polynomial(self):
        fps = float(120)
        low = float(2)
        high = float(60)
        order = 2

        b, a = scipy_interface.create_filter(fps, low, high, order, pass_type="lowpass")

        self.assertIsInstance(a, list)
        self.assertIsInstance(b, list)

        return b, a

    def test_filter(self):
        b, a = self.test_polynomial()
        x = numpy.linspace(-1, 1, 241)

        y = scipy_interface.filter_list(b, a, x)

        self.assertIsInstance(y, list)


if __name__ == '__main__':
    unittest.main()
