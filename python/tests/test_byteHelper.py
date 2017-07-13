from nose.tools import assert_equal
from nose.tools import assert_raises

import multisecret.byteHelper as bytehelper
from multisecret.MultiSecretRoyAdhikari import Dealer

# large prime
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

def test_bitlen():
    pass


def test_bytelen():
    number = 255
    length = bytehelper.bytelen(number)
    assert_equal(length, 1)

    number = 258
    length = bytehelper.bytelen(number)
    assert_equal(length, 2)

    number = 0xFEEDBEEF
    length = bytehelper.bytelen(number)
    assert_equal(length, 4)

def test_int_to_bytes():
    pass
    
def test_bytes_to_int():
    pass
    
def test_take_first_bits_exceptions():

    dealer = Dealer(7, 2, [5,6], [[(1,2)],[(1,3)]] )
    
    input = (0xDEADBEEF).to_bytes(8, byteorder='big') # len in bytes
    
    # test correct exception raised
    with assert_raises(ValueError):
        bytehelper.take_first_bits(input, 65) # len in bits


def test_take_first_bits():
    dealer = Dealer(7, 2, [5, 6], [[(1, 2)], [(1, 3)]])

    input = bytes([0xDE, 0xAD, 0xBE, 0xEF])  # len in bytes
    print('test input: ', input.hex())

    first_bits = bytehelper.take_first_bits(input, 12)
    print('test first bits: ', first_bits.hex())
    assert_equal(first_bits, bytes([0xDE, 0xA0]))

    modulo_bits = bytehelper.take_first_bits(input, 16)
    assert_equal(modulo_bits, bytes([0xDE, 0xAD]))


def test_inverse_modulo_p():
    
    assert_equal(7, bytehelper.inverse_modulo_p(5, 17))
    assert_equal(5, bytehelper.inverse_modulo_p(7, 17))
    assert_equal(9, bytehelper.inverse_modulo_p(3, 26))
    assert_equal(829540, bytehelper.inverse_modulo_p(1009, 1000007))

