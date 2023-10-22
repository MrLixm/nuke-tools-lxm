import logging
import unittest

import gamut_convert

LOGGER = logging.getLogger(__name__)


class TestMatrix(unittest.TestCase):
    def setUp(self):
        # rounded at 15 decimals, retrieved from colour which is using numpy
        self.array_3x3_alpha = [
            [0.412390799265959, 0.357584339383878, 0.180480788401834],
            [0.21263900587151, 0.715168678767756, 0.072192315360734],
            [0.019330818715592, 0.119194779794626, 0.950532152249661],
        ]
        self.array_3x3_alpha_inv = [
            [3.240969941904523, -1.537383177570094, -0.498610760293003],
            [-0.96924363628088, 1.875967501507721, 0.041555057407176],
            [0.055630079696994, -0.203976958888977, 1.056971514242879],
        ]

    def tearDown(self):
        pass

    def test_identity(self):
        identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        expected = gamut_convert.Matrix3x3(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        result = gamut_convert.Matrix3x3.init_as_identity()
        self.assertEqual(expected._array, result._array)
        self.assertEqual(identity, result._array)
        # test __eq__
        self.assertEqual(expected, result)

    def test_zeros(self):
        expected_array = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        expected = gamut_convert.Matrix3x3(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        result = gamut_convert.Matrix3x3.init_with_zeros()
        self.assertEqual(expected._array, result._array)
        self.assertEqual(expected_array, result._array)
        # test __eq__
        self.assertEqual(expected, result)

        # 2x2
        expected_array = [[0.0, 0.0], [0.0, 0.0]]
        expected = gamut_convert.Matrix2x2(0.0, 0.0, 0.0, 0.0)
        result = gamut_convert.Matrix2x2.init_with_zeros()
        self.assertEqual(expected._array, result._array)
        self.assertEqual(expected_array, result._array)
        # test __eq__
        self.assertEqual(expected, result)

    def test_mult(self):
        source = gamut_convert.Matrix3x3.init_as_identity()
        target = gamut_convert.Matrix3x3.init_as_identity()
        self.assertEqual(source * target, source)

        source1 = gamut_convert.Matrix3x3.from_2dsequence(self.array_3x3_alpha)
        source2 = gamut_convert.Matrix4x4.init_as_identity()
        with self.assertRaises(TypeError):
            result = source1 * source2

        source1 = gamut_convert.Matrix3x3.from_2dsequence(self.array_3x3_alpha)
        source2 = gamut_convert.Vector3(0.3, 0.2, 0.1)
        with self.assertRaises(TypeError):
            result = source1 * source2

    def test_inverted_1(self):
        source = gamut_convert.Matrix3x3.init_as_identity()
        result = source.inverted()
        self.assertEqual(result, source)

        with self.assertRaises(ValueError):
            # not invertible
            result = gamut_convert.Matrix3x3.init_with_zeros().inverted()

    def test_inverted_2(self):
        source = gamut_convert.Matrix3x3.from_2dsequence(self.array_3x3_alpha)
        result = source.inverted().as_2Dlist()
        for row_index, row in enumerate(result):
            for col_index, col in enumerate(row):
                self.assertAlmostEqual(
                    col,
                    self.array_3x3_alpha_inv[row_index][col_index],
                    delta=0.000000000000005,
                )

    def test_inverted_3(self):
        source = gamut_convert.Matrix3x3.from_2dsequence(self.array_3x3_alpha)
        result = source.inverted()
        result = result.inverted()

        for row_index, row in enumerate(result.as_2Dlist()):
            for col_index, col in enumerate(row):
                self.assertAlmostEqual(
                    col,
                    self.array_3x3_alpha[row_index][col_index],
                    delta=0.000000000000005,
                )


class TestGamutConversion(unittest.TestCase):
    def setUp(self):
        self.sRGB_gamut = gamut_convert.Gamut(
            ((0.64, 0.33), (0.3, 0.6), (0.15, 0.06)),
            (0.3127, 0.329),
        )
        self.AP0_gamut = gamut_convert.Gamut(
            ((0.7347, 0.2653), (0.0, 1.0), (0.0001, -0.077)),
            (0.32168, 0.33767),
        )
        self.AP0_D65_gamut = gamut_convert.Gamut(
            ((0.7347, 0.2653), (0.0, 1.0), (0.0001, -0.077)),
            (0.3127, 0.329),
        )

    def tearDown(self):
        pass

    def test_conversion_identity(self):
        expected = gamut_convert.Matrix3x3.init_as_identity()
        result = gamut_convert.get_conversion_matrix(self.sRGB_gamut, self.sRGB_gamut)

        expected_array = expected.as_2Dlist()
        result_array = result.as_2Dlist()

        for row_index, row in enumerate(result_array):
            for col_index, col in enumerate(row):
                self.assertAlmostEqual(
                    col,
                    expected_array[row_index][col_index],
                    delta=0.000000000000005,
                )

    def test_conversion_1(self):
        # retrieved from colour which use numpy
        # assuming no c.a.t. is used
        expected = [
            [0.432930520128218, 0.375384359521582, 0.189378057920798],
            [0.089413137095003, 0.816533021069837, 0.103021992827329],
            [0.019161713065298, 0.118152066030387, 0.94221691428194],
        ]
        result = gamut_convert.get_conversion_matrix(self.sRGB_gamut, self.AP0_gamut)

        for row_index, row in enumerate(result.as_2Dlist()):
            for col_index, col in enumerate(row):
                self.assertAlmostEqual(
                    col,
                    expected[row_index][col_index],
                    delta=0.000000000000005,
                )


class TestVector(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_class_for_size(self):
        expected = gamut_convert.Vector2
        result = gamut_convert.BaseVector.get_class_for_size(2)
        self.assertIs(result, expected)
        expected = gamut_convert.Vector3
        result = gamut_convert.BaseVector.get_class_for_size(3)
        self.assertIs(result, expected)
        expected = gamut_convert.Vector4
        result = gamut_convert.BaseVector.get_class_for_size(4)
        self.assertIs(result, expected)
        expected = None
        result = gamut_convert.BaseVector.get_class_for_size(5)
        self.assertIs(result, expected)


if __name__ == "__main__":
    unittest.main()
