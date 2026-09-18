"""Independent rational specification of sign-code transport.

No NumPy and no import of the implementation's transform or sign helper. Binary
floats are interpreted as their exact rational values. A negative sign must
complement the source bit, including a source zero; IEEE thresholding of -0.0
therefore deliberately fails the certificate. This specifies a control, not a
new retrieval rule.
"""
from fractions import Fraction


def exact_codes(rows):
    zero = Fraction(0)
    return tuple(tuple(Fraction(float(value)) >= zero for value in row) for row in rows)


def expected_images(codes, permutation, mask):
    # This is the signed-permutation action on bits, not thresholding the same
    # numerical transform as the implementation under test.
    return tuple(tuple((not row[source]) if mask & (1 << target) else row[source]
                       for target, source in enumerate(permutation)) for row in codes)
