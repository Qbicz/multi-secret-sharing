from nose.tools import assert_equal
from multisecret.primality import is_probable_prime, is_prime

# large prime
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

def test_is_probable_prime():
    assert_equal(is_probable_prime(2), True)
    assert_equal(is_probable_prime(3), True)
    assert_equal(is_probable_prime(39), False)
    assert_equal(is_probable_prime(41), True)
    assert_equal(is_probable_prime(p256), True)
    
def test_is_prime():
    assert_equal(is_prime(2), True)
    assert_equal(is_prime(3), True)
    assert_equal(is_prime(39), False)
    assert_equal(is_prime(41), True)
    # don't test large primes with this slow (but accurate) method
    