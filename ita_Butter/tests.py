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
        t = numpy.linspace(1, 45, 44)
        x = [
            6.10073773779645,
            6.083901597959422,
            6.772113729079406,
            6.69155928387719,
            5.843792396558136,
            7.7600117770232195,
            5.5412599302608205,
            3.2762736016638847,
            5.139264666004937,
            4.904853857811264,
            2.6942623221540942,
            2.4209988926847212,
            4.709816486018015,
            3.8871745483887086,
            1.9704382685500903,
            0.5735523122411439,
            1.9868888622241925,
            -0.12216856465709647,
            2.072497093710182,
            -0.05054674399822545,
            -0.4217189815610065,
            -0.7959994546758562,
            0.5847009212041216,
            0.208866334410712,
            1.3798892891393733,
            1.0087164580062176,
            -0.903095903962637,
            0.38668886260055624,
            -1.030400979158727,
            -1.3735988710224327,
            -2.757013888539267,
            -3.0769011279372567,
            -1.5865082764644143,
            -1.8768666822355655,
            -2.150130666858135,
            -7.012036493552377,
            -5.787785222699686,
            -6.95854869976713,
            -2.992713470883843,
            -5.3361830190212896,
            -5.4742396209005015,
            -3.3983352920633285,
            -2.6790412050488612,
            -5.4469136434984256
        ]
        xn_array = numpy.asarray(x)
        xn_list = x

        # print(xn_array)
        # print(xn_list)

        self.assertIsInstance(xn_array, numpy.ndarray)
        self.assertIsInstance(xn_list, list)

        return t, x, xn_array

    def test_lfilter_example(self):
        """Test lfilter example."""
        t, x, xn = self.test_array_create()
        b, a = sig.butter(2, 0.05)

        # zi = sig.lfilter_zi(b, a)
        # z, _ = sig.lfilter(b, a, xn, zi=zi*xn[0])
        # z2, _ = sig.lfilter(b, a, z, zi=zi*z[0])
        y = sig.filtfilt(b, a, xn)

        # print(t)
        print(y)

        # x, b, a, zi, z, z2
        return t, xn, y

    def test_matplotlib_example(self):
        """Test lfilter example."""
        t, xn, y = self.test_lfilter_example()

        plt.figure
        plt.plot(t, xn, 'b', alpha=0.25)
        # plt.plot(t, z, 'r--')
        # plt.plot(t, z2, 'r')
        plt.plot(t, y, 'k')
        plt.legend(('noisy signal', 'filtfilt'), loc='best')
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
