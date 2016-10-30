# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from os import urandom
from math import log2, floor
# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
#import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from primality import is_probable_prime

class Dealer:

    def __init__(self, p, n_participants, s_secrets, access_structure):
        
        # check sanity of p
        if is_probable_prime(p) and p > n_participants and p > max(s_secrets):
            self.p = p
        else:
            raise ValueError('Wrong p selected!')
        
        if n_participants < 2:
            raise ValueError('There must be at least 2 participants!')
        else:
            self.n = n_participants
        self.k = len(s_secrets) # number of secrets
        self.s_secrets = s_secrets # TODO: hide the secrets
        self.access_structure = access_structure
        self.random_id = [b'ZERO'] # fill the 0th element to begin from 1 when appending
        self.hash_len = floor(log2(p))+1
        self.aes_nonce = urandom(16)
        
        print('hash_len:', self.hash_len)
        print('Dealer created for Roy-Adhikari sharing of %d secrets among %d participants' % (self.k, self.n))
    
    
    def hash(self, message, num_first_bits):
        """A collision resistant hash function with variable output length:
        # option 1: use SHA-3 Keccak (variable length digest)
        # option 2: use BLAKE2 : variable length digest (available at "cryptography" library - but to bytes, not bits resolution)
        # option 3 (chosen): use the first [log2(p)]+1 bits of AES-CTR(SHA256(m))"""

        # SHA256 of message
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(message)
        hashed_message = digest.finalize()

        print('Hash of len', len(hashed_message))
        print(hashed_message.hex())

        # AES-CTR of the hash
        aes_key = hashed_message
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(self.aes_nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        input = b'wwwwwwwwwwwwwwww'
        print(input.hex())
        ciphertext = encryptor.update(input) + encryptor.finalize()

        print('Ciphertext of len', len(ciphertext))
        print(ciphertext.hex())

        # take demanded numer of bits
        var_hash = self.take_first_bits(ciphertext, num_first_bits)
        print('First %d bits:' % num_first_bits)
        print(var_hash.hex())
        
        
    def provide_id(self):
        """for each participant provide ID in p modulo field"""
        for i in range(1, self.n+1):
            while True:
                self.random_id.append(urandom(32))
                if(int.from_bytes(self.random_id[i], byteorder='big') < self.p):
                    break
            print('Participant ID %d, %s' % (i, self.random_id[i].hex()))
        
        return self.random_id
          
          
    def is_prime(self, n):
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
    
    
    def take_first_bits(self, input, bitlen):
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
    
    def choose_distinct_x(self):
        """ dealer chooses distinct x_j and sends it secretly to each participant, j=1,2...n
        """
        self.x = [b'ZERO']
        
        for j in range(1, self.n+1):
            while True:
                self.x.append(urandom(32))
                if(int.from_bytes(self.x[j], byteorder='big') < self.p):
                    break
            print('x%d = %s' % (j, self.x[j].hex()))
            
        return self.x # TODO: use yield to construct a generator
    
    
    