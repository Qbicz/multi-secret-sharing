from nose.tools import assert_equal
from nose.tools import assert_raises
from multisecret.byteHelper import *
from multisecret.Dealer import Dealer

# large prime
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

def test_bitlen():
    pass
    
def test_int_to_bytes():
    pass
    
def test_bytes_to_int():
    pass
    
def test_take_first_bits():

    dealer = Dealer(7, 2, [5,6], [[(1,2)],[(1)]] )
    
    input = (0xDEADBEEF).to_bytes(8, byteorder='big') # len in bytes
    
    # test correct exception raised
    with assert_raises(ValueError):
        dealer.take_first_bits(input, 65) # len in bits
    
    #first_bits = dealer.take_first_bits(input, 24)
    #assert_equal(first_bits, bytes(0xDEA))
    