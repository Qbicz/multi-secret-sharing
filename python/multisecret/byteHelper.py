""" Helper functions for robust conversion
    - int->bytes
    - bytes->int
"""
from math import log2, floor


def bitlen(number):
    """ return length of integer number in bits """
    assert(isinstance(number, int))
    if number == 0:
        return 1
    else:
        return floor(log2(number)) + 1


def bytelen(number):
    assert (isinstance(number, int))
    if number == 0:
        return 1
    else:
        return floor(log2(number) // 8) + 1


def inverse_modulo_p(a, p):
    """ multiplicative inverse of a in finite field mod p """
    prime = p
    
    while a < 0:
        a += prime
    
    y1 = 1
    y2 = 0
    
    while a != 1:
        q = (p // a) % prime
        # use of integer division // speeded algorithm up by huge factor
        
        # save temporary values
        tmp_a = a
        tmp_y2 = y2
        # compute all these simultaneously
        a = (p - (q*a)) % prime
        p = tmp_a
        y2 = y1
        y1 = (tmp_y2 - (q*y1)) % prime
        
    return y1 % prime

""" use multipledispatch """

def take_first_bits(input, bitlen):
    # print('Length of input', len(input))

    # print('take first bits from', input)
    if bitlen > 8 * len(input):
        raise ValueError('input shorter than %d bits' % bitlen)
    elif bitlen == 8 * len(input):
        return input
    else:
        # take all bytes needed
        if bitlen % 8 == 0:
            bytelen = bitlen // 8
        else:
            bytelen = bitlen // 8 + 1
        input_bytelen = input[:bytelen]

        # now extract bits from the last byte
        last_byte = input_bytelen[-1]
        mask = ~(0xff >> (8 - (8 * bytelen - bitlen)))
        output = bytes(input_bytelen[:bytelen - 1])
        output += bytes([mask & last_byte])
        return output
