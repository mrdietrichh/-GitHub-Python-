import unittest
import math
from rat import RatNum, RatPoly

class TestRatNum(unittest.TestCase):
    def test_init(self):
        r = RatNum(3, 4)
        self.assertEqual(r._num, 3)
        self.assertEqual(r._den, 4)
        self.assertFalse(r._is_nan)
        r2 = RatNum(6, 8)
        self.assertEqual(r2._num, 3)
        self.assertEqual(r2._den, 4)
        r3 = RatNum(0, 5)
        self.assertEqual(r3._num, 0)
        self.assertEqual(r3._den, 1)
        r4 = RatNum(1, 0)
        self.assertTrue(r4._is_nan)

    def test_is_nan(self):
        self.assertTrue(RatNum(1, 0).is_nan())
        self.assertFalse(RatNum(1, 2).is_nan())

    def test_is_negative_positive(self):
        self.assertTrue(RatNum(-1, 2).is_negative())
        self.assertFalse(RatNum(-1, 2).is_positive())
        self.assertTrue(RatNum(1, 3).is_positive())
        self.assertFalse(RatNum(1, 3).is_negative())
        self.assertFalse(RatNum(0, 1).is_negative())
        self.assertFalse(RatNum(0, 1).is_positive())
        self.assertFalse(RatNum(1, 0).is_negative())
        self.assertFalse(RatNum(1, 0).is_positive())

    def test_compare_to(self):
        r1 = RatNum(1, 2)
        r2 = RatNum(1, 3)
        self.assertEqual(r1.compare_to(r2), 1)
        self.assertEqual(r2.compare_to(r1), -1)
        self.assertEqual(r1.compare_to(r1), 0)
        nan = RatNum(1, 0)
        self.assertEqual(nan.compare_to(nan), 0)
        self.assertEqual(nan.compare_to(r1), 1)
        self.assertEqual(r1.compare_to(nan), -1)

    def test_float_value(self):
        self.assertAlmostEqual(RatNum(1, 2).float_value(), 0.5)
        self.assertTrue(math.isnan(RatNum(1, 0).float_value()))

    def test_int_value(self):
        self.assertEqual(RatNum(7, 3).int_value(), 2)
        self.assertEqual(RatNum(-7, 3).int_value(), -3)
        with self.assertRaises(ValueError):
            RatNum(1, 0).int_value()

    def test_neg(self):
        r = RatNum(2, 3)
        self.assertEqual((-r)._num, -2)
        self.assertEqual((-r)._den, 3)
        nan = RatNum(1, 0)
        self.assertTrue((-nan).is_nan())

    def test_add(self):
        r1 = RatNum(1, 2)
        r2 = RatNum(1, 3)
        res = r1 + r2
        self.assertEqual(res._num, 5)
        self.assertEqual(res._den, 6)
        nan = RatNum(1, 0)
        self.assertTrue((r1 + nan).is_nan())
        self.assertTrue((nan + r1).is_nan())
        self.assertTrue((nan + nan).is_nan())

    def test_sub(self):
        r1 = RatNum(1, 2)
        r2 = RatNum(1, 3)
        res = r1 - r2
        self.assertEqual(res._num, 1)
        self.assertEqual(res._den, 6)
        nan = RatNum(1, 0)
        self.assertTrue((r1 - nan).is_nan())

    def test_mul(self):
        r1 = RatNum(2, 3)
        r2 = RatNum(3, 4)
        res = r1 * r2
        self.assertEqual(res._num, 1)
        self.assertEqual(res._den, 2)
        nan = RatNum(1, 0)
        self.assertTrue((r1 * nan).is_nan())

    def test_truediv(self):
        r1 = RatNum(2, 3)
        r2 = RatNum(3, 4)
        res = r1 / r2
        self.assertEqual(res._num, 8)
        self.assertEqual(res._den, 9)
        zero = RatNum(0, 1)
        self.assertTrue((r1 / zero).is_nan())
        nan = RatNum(1, 0)
        self.assertTrue((r1 / nan).is_nan())

    def test_str(self):
        self.assertEqual(str(RatNum(3, 4)), "3/4")
        self.assertEqual(str(RatNum(5, 1)), "5")
        self.assertEqual(str(RatNum(0, 1)), "0")
        self.assertEqual(str(RatNum(1, 0)), "NaN")
        self.assertEqual(str(RatNum(-2, 3)), "-2/3")

    def test_hash(self):
        self.assertEqual(hash(RatNum(1, 2)), hash((1, 2)))
        self.assertEqual(hash(RatNum(2, 4)), hash((1, 2)))
        nan = RatNum(1, 0)
        self.assertEqual(hash(nan), 0)

    def test_eq(self):
        self.assertEqual(RatNum(1, 2), RatNum(2, 4))
        self.assertNotEqual(RatNum(1, 2), RatNum(1, 3))
        nan1 = RatNum(1, 0)
        nan2 = RatNum(0, 0)
        self.assertEqual(nan1, nan2)
        self.assertNotEqual(nan1, RatNum(1, 2))


class TestRatPoly(unittest.TestCase):
    def test_init(self):
        p = RatPoly({0: RatNum(1, 1), 2: RatNum(3, 1)})
        self.assertEqual(p._coeffs, {0: RatNum(1), 2: RatNum(3)})
        self.assertFalse(p._nan)
        p2 = RatPoly([RatNum(1), RatNum(0), RatNum(3)])
        self.assertEqual(p2._coeffs, {0: RatNum(1), 2: RatNum(3)})
        p3 = RatPoly({0: RatNum(0)})
        self.assertEqual(p3._coeffs, {})
        p4 = RatPoly({1: RatNum(1, 0)})
        self.assertTrue(p4._nan)

    def test_degree(self):
        p = RatPoly({0: RatNum(1), 2: RatNum(3)})
        self.assertEqual(p.degree(), 2)
        p2 = RatPoly({})
        self.assertEqual(p2.degree(), -1)
        p3 = RatPoly({1: RatNum(1, 0)})
        self.assertEqual(p3.degree(), -1)

    def test_get_coeff(self):
        p = RatPoly({0: RatNum(1), 2: RatNum(3)})
        self.assertEqual(p.get_coeff(0), RatNum(1))
        self.assertEqual(p.get_coeff(1), RatNum(0))
        self.assertEqual(p.get_coeff(2), RatNum(3))
        p_nan = RatPoly({1: RatNum(1, 0)})
        self.assertTrue(p_nan.get_coeff(1).is_nan())
        self.assertTrue(p_nan.get_coeff(0).is_nan())

    def test_is_nan(self):
        p = RatPoly()
        self.assertFalse(p.is_nan())
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue(p_nan.is_nan())

    def test_scale_coeff(self):
        p = RatPoly({1: RatNum(2), 2: RatNum(3)})
        p.scale_coeff(1, RatNum(1, 2))
        self.assertEqual(p.get_coeff(1), RatNum(1))
        p.scale_coeff(1, RatNum(0))
        self.assertEqual(p.get_coeff(1), RatNum(0))
        self.assertNotIn(1, p._coeffs)
        p.scale_coeff(2, RatNum(1, 0))
        self.assertTrue(p.is_nan())
        self.assertEqual(p.get_coeff(2), RatNum(1, 0))

    def test_neg(self):
        p = RatPoly({1: RatNum(2), 0: RatNum(-1)})
        neg = -p
        self.assertEqual(neg.get_coeff(1), RatNum(-2))
        self.assertEqual(neg.get_coeff(0), RatNum(1))
        self.assertFalse(neg.is_nan())
        p_nan = RatPoly({1: RatNum(1, 0)})
        self.assertTrue((-p_nan).is_nan())

    def test_add(self):
        p1 = RatPoly({0: RatNum(1), 1: RatNum(2)})
        p2 = RatPoly({0: RatNum(3), 1: RatNum(4), 2: RatNum(5)})
        res = p1 + p2
        self.assertEqual(res.get_coeff(0), RatNum(4))
        self.assertEqual(res.get_coeff(1), RatNum(6))
        self.assertEqual(res.get_coeff(2), RatNum(5))
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue((p1 + p_nan).is_nan())
        self.assertTrue((p_nan + p2).is_nan())

    def test_sub(self):
        p1 = RatPoly({0: RatNum(5), 1: RatNum(2)})
        p2 = RatPoly({0: RatNum(3), 1: RatNum(1)})
        res = p1 - p2
        self.assertEqual(res.get_coeff(0), RatNum(2))
        self.assertEqual(res.get_coeff(1), RatNum(1))

    def test_mul(self):
        p1 = RatPoly({0: RatNum(1), 1: RatNum(1)})   
        p2 = RatPoly({0: RatNum(1), 1: RatNum(-1)})  
        res = p1 * p2
        # (x+1)*(1-x) = 1 - x^2
        self.assertEqual(res.get_coeff(0), RatNum(1))   
        self.assertEqual(res.get_coeff(1), RatNum(0))   
        self.assertEqual(res.get_coeff(2), RatNum(-1))  

    def test_truediv(self):
        p = RatPoly({0: RatNum(2), 1: RatNum(4)})
        res = p / RatNum(2)
        self.assertEqual(res.get_coeff(0), RatNum(1))
        self.assertEqual(res.get_coeff(1), RatNum(2))
        res2 = p / RatNum(0)
        self.assertTrue(res2.is_nan())
        res3 = p / RatNum(1, 0)
        self.assertTrue(res3.is_nan())
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue((p_nan / RatNum(2)).is_nan())

    def test_eval(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2), 2: RatNum(3)})
        self.assertEqual(p.eval(RatNum(2)), RatNum(17))
        self.assertEqual(p.eval(RatNum(0)), RatNum(1))
        self.assertTrue(p.eval(RatNum(1, 0)).is_nan())
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue(p_nan.eval(RatNum(2)).is_nan())

    def test_differentiate(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2), 2: RatNum(3), 3: RatNum(4)})
        dp = p.differentiate()
        self.assertEqual(dp.get_coeff(0), RatNum(2))
        self.assertEqual(dp.get_coeff(1), RatNum(6))
        self.assertEqual(dp.get_coeff(2), RatNum(12))
        self.assertEqual(dp.get_coeff(3), RatNum(0))
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue(p_nan.differentiate().is_nan())

    def test_anti_differentiate(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2)})
        ap = p.anti_differentiate()
        self.assertEqual(ap.get_coeff(1), RatNum(1))
        self.assertEqual(ap.get_coeff(2), RatNum(1))
        self.assertEqual(ap.get_coeff(0), RatNum(0))
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue(p_nan.anti_differentiate().is_nan())

    def test_integrate(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2)})
        self.assertEqual(p.integrate(RatNum(0), RatNum(1)), RatNum(2))
        self.assertEqual(p.integrate(RatNum(1), RatNum(2)), RatNum(4))
        self.assertTrue(p.integrate(RatNum(0), RatNum(1, 0)).is_nan())
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertTrue(p_nan.integrate(RatNum(0), RatNum(1)).is_nan())

    def test_value_of(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2)})
        self.assertEqual(p.value_of(RatNum(3)), RatNum(7))
        self.assertTrue(p.value_of(RatNum(1, 0)).is_nan())

    def test_str(self):
        p = RatPoly({0: RatNum(1), 1: RatNum(2), 2: RatNum(3)})
        self.assertEqual(str(p), "3*x^2 + 2*x + 1")
        p2 = RatPoly({1: RatNum(1), 2: RatNum(-1)})
        self.assertEqual(str(p2), "-x^2 + x")        # без явной единицы
        p3 = RatPoly({0: RatNum(5)})
        self.assertEqual(str(p3), "5")
        p4 = RatPoly({})
        self.assertEqual(str(p4), "0")
        p5 = RatPoly({2: RatNum(1), 1: RatNum(-1), 0: RatNum(0)})
        self.assertEqual(str(p5), "x^2 - x")         
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertEqual(str(p_nan), "NaN")

    def test_hash(self):
        p1 = RatPoly({0: RatNum(1), 1: RatNum(2)})
        p2 = RatPoly({0: RatNum(1), 1: RatNum(2)})
        self.assertEqual(hash(p1), hash(p2))
        p3 = RatPoly({1: RatNum(2), 0: RatNum(1)})
        self.assertEqual(hash(p1), hash(p3))
        p_nan = RatPoly({0: RatNum(1, 0)})
        self.assertEqual(hash(p_nan), hash(p_nan))

    def test_eq(self):
        p1 = RatPoly({0: RatNum(1), 1: RatNum(2)})
        p2 = RatPoly({1: RatNum(2), 0: RatNum(1)})
        self.assertEqual(p1, p2)
        p3 = RatPoly({0: RatNum(1)})
        self.assertNotEqual(p1, p3)
        nan1 = RatPoly({0: RatNum(1, 0)})
        nan2 = RatPoly({1: RatNum(1, 0)})
        self.assertEqual(nan1, nan2)
        self.assertNotEqual(nan1, p1)


if __name__ == '__main__':
    unittest.main()
