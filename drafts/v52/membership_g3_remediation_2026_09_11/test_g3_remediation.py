"""Current delivery suite; recovered 42 checks are historical evidence only."""
import unittest
from test_certificate import CertificateTests
from test_delivery_g2 import RelatedG2Tests
from test_delivery_pipeline import *
from test_delivery_integration import *

if __name__ == '__main__':
    unittest.main(verbosity=2)
