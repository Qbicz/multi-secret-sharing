# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

def is_prime(n):
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    f = 5
    while f <= r:
        print ('\t',f)
        if n%f == 0: return False
        if n%(f+2) == 0: return False
        f +=6
    return True

#def choose_prime(p_size):

def take_first_bits(input, bitlen):
    if bitlen > 8*len(input):
        raise ValueError('input shorter than %d bits' % bitlen)
    elif bitlen == 8*len(input):
        return input
    else:
        # take all bytes needed
        bytelen = (floor(bitlen/8)) + 1
        input_bytelen = input[:bytelen]
        
        # now extract bits from the last byte
        last_byte = input_bytelen[-1]
        mask = ~(0xff >> (8-(8*bytelen - bitlen)))
        output = bytearray(input_bytelen[:bytelen-1])
        output.append(mask & last_byte)
        return output
    
    
import os # for OS random number generation
from math import log2, floor
# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
#import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

k_secrets = 3
s_secrets = [7, 313, 671] # s_i
n_participants = 2
access_structures = [(1,),(2,),(1,2)]

p_size = 2 # bytes

print(access_structures)

# 1. Dealer Phase
## I. Initialization stage
p = int.from_bytes(os.urandom(p_size), byteorder="big")
print(p)
while p <= n_participants or p <= max(s_secrets) or not is_prime(p): # p must be prime, greater than any of secrets and greater than n
    p = int.from_bytes(os.urandom(p_size), byteorder="big")
    print(p)
    
print('[log2(p)]+1 = ', floor(log2(p))+1)

### A collision resistant hash function with variable output length:
# option 1: use SHA-3 Keccak (variable length digest)
# option 2: use BLAKE2 : variable length digest (available at "cryptography" library)
# option 3: use the first [log2(p)]+1 bits of AES-CTR(SHA256(m))

# SHA256 of message
message = b'deadbeef'
digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
digest.update(message)
hashed_message = digest.finalize()

print('Hash of len', len(hashed_message))
print(hashed_message.hex())

# AES-CTR of the hash
aes_key = os.urandom(32)
aes_nonce = os.urandom(16)
cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_nonce), backend=default_backend())
encryptor = cipher.encryptor()
ciphertext = encryptor.update(hashed_message) + encryptor.finalize()

print('Ciphertext of len', len(ciphertext))
print(ciphertext.hex())

# take demanded numer of bits
var_hash = take_first_bits(ciphertext, 26)
print('First bits:')
print(var_hash.hex())
