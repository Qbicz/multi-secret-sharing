from nose.tools import assert_equal
from nose.tools import assert_raises
from prototype.primality import is_probable_prime

def test_is_probable_prime():
    assert_equal(is_probable_prime(2), True)
    assert_equal(is_probable_prime(3), True)
    assert_equal(is_probable_prime(39), False)
    assert_equal(is_probable_prime(41), True)
    