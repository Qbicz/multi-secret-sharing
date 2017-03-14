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
    
    prime = p
    
    while a < 0:
        a += prime
    
    y1 = 1
    y2 = 0
    
    while a != 1:
        print (a)
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
        

def int_to_bytes(int_number):
    pass


def bytes_to_int(byte_number):
    pass
    
""" use multipledispatch """ 
 
def take_first_bits():
    pass