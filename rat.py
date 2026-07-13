import math
from functools import total_ordering

@total_ordering
class RatNum:
    def __init__(self, num=0, den=1):
        if den == 0:
            self._num = 0
            self._den = 1
            self._is_nan = True
        else:
            if den < 0:
                num, den = -num, -den
            g = RatNum.gcd(abs(num), den)
            self._num = num // g
            self._den = den // g
            self._is_nan = False

    @staticmethod
    def gcd(a, b):
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a

    def is_nan(self):
        return self._is_nan

    def is_negative(self):
        if self._is_nan:
            return False
        return self._num < 0

    def is_positive(self):
        if self._is_nan:
            return False
        return self._num > 0

    def compare_to(self, other):
        if not isinstance(other, RatNum):
            raise TypeError("Comparison requires RatNum")
        if self._is_nan and other._is_nan:
            return 0
        if self._is_nan:
            return 1
        if other._is_nan:
            return -1
        left = self._num * other._den
        right = other._num * self._den
        if left < right:
            return -1
        elif left > right:
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self.compare_to(other) < 0

    def __eq__(self, other):
        if not isinstance(other, RatNum):
            return False
        if self._is_nan and other._is_nan:
            return True
        if self._is_nan or other._is_nan:
            return False
        return self._num == other._num and self._den == other._den

    def float_value(self):
        if self._is_nan:
            return math.nan
        return self._num / self._den

    def int_value(self):
        if self._is_nan:
            raise ValueError("Cannot convert NaN to int")
        return self._num // self._den

    def __neg__(self):
        if self._is_nan:
            return RatNum(1, 0)
        return RatNum(-self._num, self._den)

    def __add__(self, other):
        if not isinstance(other, RatNum):
            return NotImplemented
        if self._is_nan or other._is_nan:
            return RatNum(1, 0)
        return RatNum(self._num * other._den + other._num * self._den,
                      self._den * other._den)

    def __sub__(self, other):
        if not isinstance(other, RatNum):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other):
        if not isinstance(other, RatNum):
            return NotImplemented
        if self._is_nan or other._is_nan:
            return RatNum(1, 0)
        return RatNum(self._num * other._num, self._den * other._den)

    def __truediv__(self, other):
        if not isinstance(other, RatNum):
            return NotImplemented
        if self._is_nan or other._is_nan or other._num == 0:
            return RatNum(1, 0)
        return RatNum(self._num * other._den, self._den * other._num)

    def __str__(self):
        if self._is_nan:
            return "NaN"
        if self._den == 1:
            return str(self._num)
        return f"{self._num}/{self._den}"

    def __hash__(self):
        if self._is_nan:
            return 0
        return hash((self._num, self._den))

    def __repr__(self):
        return f"RatNum({self._num}, {self._den})" if not self._is_nan else "RatNum(NaN)"


class RatPoly:
    def __init__(self, coeffs=None):
        self._coeffs = {}
        self._nan = False

        if coeffs is None:
            return

        if isinstance(coeffs, dict):
            for deg, val in coeffs.items():
                if not isinstance(val, RatNum):
                    raise TypeError("Coefficients must be RatNum")
                if val.is_nan():
                    self._nan = True
                    break
                if val != RatNum(0):
                    self._coeffs[deg] = val
        elif isinstance(coeffs, list):
            for deg, val in enumerate(coeffs):
                if not isinstance(val, RatNum):
                    raise TypeError("Coefficients must be RatNum")
                if val.is_nan():
                    self._nan = True
                    break
                if val != RatNum(0):
                    self._coeffs[deg] = val
        else:
            raise TypeError("coeffs must be dict or list or None")

    def degree(self):
        if self._nan:
            return -1
        if not self._coeffs:
            return -1
        return max(self._coeffs.keys())

    def get_coeff(self, degree):
        if not isinstance(degree, int) or degree < 0:
            raise ValueError("Degree must be non-negative int")
        if self._nan:
            return RatNum(1, 0)
        return self._coeffs.get(degree, RatNum(0))

    def is_nan(self):
        return self._nan

    def scale_coeff(self, degree, scalar):
        if not isinstance(scalar, RatNum):
            raise TypeError("scalar must be RatNum")
        if degree < 0:
            raise ValueError("Degree must be non-negative")
        if scalar.is_nan():
            self._nan = True
            return
        if self._nan:
            return
        curr = self._coeffs.get(degree, RatNum(0))
        new_val = curr * scalar
        if new_val == RatNum(0):
            self._coeffs.pop(degree, None)
        else:
            self._coeffs[degree] = new_val

    def __neg__(self):
        if self._nan:
            return RatPoly({0: RatNum(1, 0)})
        new_coeffs = {deg: -coeff for deg, coeff in self._coeffs.items()}
        return RatPoly(new_coeffs)

    def __add__(self, other):
        if not isinstance(other, RatPoly):
            return NotImplemented
        if self._nan or other._nan:
            return RatPoly({0: RatNum(1, 0)})
        result = dict(self._coeffs)
        for deg, val in other._coeffs.items():
            if deg in result:
                s = result[deg] + val
                if s == RatNum(0):
                    del result[deg]
                else:
                    result[deg] = s
            else:
                result[deg] = val
        return RatPoly(result)

    def __sub__(self, other):
        if not isinstance(other, RatPoly):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other):
        if not isinstance(other, RatPoly):
            return NotImplemented
        if self._nan or other._nan:
            return RatPoly({0: RatNum(1, 0)})
        result = {}
        for d1, c1 in self._coeffs.items():
            for d2, c2 in other._coeffs.items():
                deg = d1 + d2
                prod = c1 * c2
                if deg in result:
                    s = result[deg] + prod
                    if s == RatNum(0):
                        del result[deg]
                    else:
                        result[deg] = s
                else:
                    if prod != RatNum(0):
                        result[deg] = prod
        return RatPoly(result)

    def __truediv__(self, other):
        if not isinstance(other, RatNum):
            return NotImplemented
        if self._nan or other.is_nan() or other == RatNum(0):
            return RatPoly({0: RatNum(1, 0)})
        new_coeffs = {deg: coeff / other for deg, coeff in self._coeffs.items()
                      if coeff / other != RatNum(0)}
        return RatPoly(new_coeffs)

    def eval(self, x):
        if not isinstance(x, RatNum):
            raise TypeError("x must be RatNum")
        if self._nan or x.is_nan():
            return RatNum(1, 0)
        if not self._coeffs:
            return RatNum(0)
        deg = max(self._coeffs.keys())
        result = RatNum(0)
        for d in range(deg, -1, -1):
            result = result * x + self._coeffs.get(d, RatNum(0))
        return result

    def differentiate(self):
        if self._nan:
            return RatPoly({0: RatNum(1, 0)})
        new_coeffs = {}
        for deg, coeff in self._coeffs.items():
            if deg == 0:
                continue
            new_deg = deg - 1
            new_val = coeff * RatNum(deg, 1)
            if new_val != RatNum(0):
                new_coeffs[new_deg] = new_val
        return RatPoly(new_coeffs)

    def anti_differentiate(self):
        if self._nan:
            return RatPoly({0: RatNum(1, 0)})
        new_coeffs = {}
        for deg, coeff in self._coeffs.items():
            new_deg = deg + 1
            new_val = coeff / RatNum(new_deg, 1)
            if new_val != RatNum(0):
                new_coeffs[new_deg] = new_val
        return RatPoly(new_coeffs)

    def integrate(self, a, b):
        if not (isinstance(a, RatNum) and isinstance(b, RatNum)):
            raise TypeError("Limits must be RatNum")
        if self._nan or a.is_nan() or b.is_nan():
            return RatNum(1, 0)
        antideriv = self.anti_differentiate()
        return antideriv.eval(b) - antideriv.eval(a)

    def value_of(self, x):
        return self.eval(x)

    def __str__(self):
        if self._nan:
            return "NaN"
        if not self._coeffs:
            return "0"
        terms = []
        for deg in sorted(self._coeffs.keys(), reverse=True):
            coeff = self._coeffs[deg]
            if coeff == RatNum(0):
                continue
            if deg == 0:
                term = str(coeff)
            elif deg == 1:
                if coeff == RatNum(1):
                    term = "x"
                elif coeff == RatNum(-1):
                    term = "-x"
                else:
                    term = f"{coeff}*x"
            else:
                if coeff == RatNum(1):
                    term = f"x^{deg}"
                elif coeff == RatNum(-1):
                    term = f"-x^{deg}"
                else:
                    term = f"{coeff}*x^{deg}"
            terms.append(term)
        if not terms:
            return "0"
        result = " + ".join(terms)
        result = result.replace("+ -", "- ")
        return result

    def __hash__(self):
        if self._nan:
            return hash(("NaN",))
        return hash(frozenset(self._coeffs.items()))

    def __eq__(self, other):
        if not isinstance(other, RatPoly):
            return False
        if self._nan and other._nan:
            return True
        if self._nan or other._nan:
            return False
        return self._coeffs == other._coeffs

    def __repr__(self):
        return f"RatPoly({self._coeffs})"