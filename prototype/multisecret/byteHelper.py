""" Helper functions for robust conversion
    - int->bytes
    - bytes->int
"""
from math import log2, floor

def bitlen(number):
    """ return length of integer in bits """
    assert(isinstance(number, int))
    
def inverse_modulo_p(a, p):
    """ multiplicative inverse of a in finite field mod p """
    
    if a < 0:
        a += p
    
    y1 = 1
    y2 = 0
    
    while a != 1:
        print (a)
        q = p // a
        # use of integer division // speeded algorithm up by huge factor
        
        # save temporary values
        tmp_a = a
        tmp_y2 = y2
        # compute all these simultaneously
        a = p - (q*a)
        P = tmp_a
        y2 = y1
        y1 = tmp_y2 - (q*y1)
        
    return y1 % p
        

def int_to_bytes(int_number):
    pass


def bytes_to_int(byte_number):
    pass
    
""" use multipledispatch """ 
 
def take_first_bits():
    pass