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

    def __init__(self, p, n_participants, s_secrets, access_structures):
        
        # check sanity of p
        if is_probable_prime(p) and p > n_participants and p > max(s_secrets):
            self.p = p
        else:
            raise ValueError('Wrong p selected!') # do I want to catch it?
        
        if n_participants < 2:
            raise ValueError('There must be at least 2 participants!')
        else:
            self.n = n_participants
        self.k = len(s_secrets) # number of secrets
        self.s_secrets = s_secrets # TODO: hide the secrets
        if isinstance(access_structures[0], list):
            self.access_structures = access_structures
        self.random_id = []
        self.hash_len = floor(log2(p))+1
        self.aes_nonce = urandom(16)
        
        print('hash_len:', self.hash_len)
        print('Dealer created for Roy-Adhikari sharing of %d secrets among %d participants' % (self.k, self.n))
    
    
    def modulo_p(self, number):
    
        if(int.from_bytes(number, byteorder='big') > self.p):
            number_int = int.from_bytes(number, byteorder='big') % self.p
            number = bytes([number_int])
        
        return number
    
    
    def hash(self, message):
        """A collision resistant hash function h with variable output length:
        # option 1: use SHA-3 Keccak (variable length digest)
        # option 2: use BLAKE2 : variable length digest (available at "cryptography" library - but to bytes, not bits resolution)
        # option 3 (chosen): use the first [log2(p)]+1 bits of AES-CTR(SHA256(m))"""

        # SHA256 of message
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(message)
        hashed_message = digest.finalize()
        #print(hashed_message.hex())

        # AES-CTR of the hash
        aes_key = hashed_message
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(self.aes_nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        input = b'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
        #print(input.hex())
        ciphertext = encryptor.update(input) + encryptor.finalize()

        #print('Ciphertext of len', len(ciphertext))
        #print(ciphertext.hex())

        # take demanded numer of bits
        varlen_hash = self.take_first_bits(ciphertext, self.hash_len)
        print('First %d bits of hash:' % self.hash_len)
        print(varlen_hash.hex())
        
        return varlen_hash
        
        
    def list_of_random_in_modulo_p(self, listlen):
        """helper function returning list of random numbers less than p prime"""
        randoms = [b'DUMMY0th'] # fill the 0th element to begin from 1 when appending
        for i in range(1, listlen+1):
            while True:
                randoms.append(urandom(32))
                if(int.from_bytes(randoms[i], byteorder='big') < self.p):
                    break
            
        return randoms # TODO: yield generator for bigger problem sizes

        
    def print_list_of_hex(self, list_to_print, description):
        """helper to print list of bytes objects with string description"""
        for i in range(1, len(list_to_print)):
            print('%s%d = %s' % (description, i, list_to_print[i].hex()))

            
    def provide_id(self):
        """for each participant provide ID in p modulo field"""
        self.random_id = self.list_of_random_in_modulo_p(self.n)
        self.print_list_of_hex(self.random_id, 'Participant ID ')
        
        return self.random_id
          
          
    def is_prime(self, n):
        """ slow, deterministic prime check, superceded by Rabin-Miller """
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
        self.x = self.list_of_random_in_modulo_p(self.n)
        
        self.print_list_of_hex(self.x, 'x')
            
        return self.x # TODO: use yield to construct a generator
    
    
    def access_group_polynomial_coeffs(self):
        """ for the qth qualified set of access group, the dealer chooses d1, d2... dm in Zp modulo field to construct the polynomial f_q(x) = si + d1*x + d2*x^2 + ... + dm*x^(m-1)
        """
        
        for gindex, gamma in enumerate(self.access_structures, start=1):
            print('gamma%d for secret s%d:' % (gindex,gindex))
            for index, A in enumerate(gamma, start=1):
                self.d = self.list_of_random_in_modulo_p(len(A))
            
                print('A%d: %r' % (index,A))
                self.print_list_of_hex(self.d, 'polynomial coeff d')

            
    def f_polynomial_compute(self, q):
        """ compute f_q(x) for q-th access group in access structure """
    
        pass
        
 
    def pseudo_share(self, )

    
    def pseudo_share_participant(self, participant, i_secret, q_group):
        """ pseudo share generation for a single partipant
            U = h(x || i_U || q_v)
        """
    
        print('Pseudo share computation for secret s%d, access group A%d, participant P%d' % (i_secret, q_group, participant))

        # l = length of longest access group for this secret
        lengths = []
        gamma = self.access_structures[i_secret]
        for A in gamma:
            lengths.append(len(A)-1)
        l = max(lengths)
        print('l = ', l)
        
        # u = bit length of number of secrets k
        u = floor(log2(self.k)) + 1
        print('u = ', u)
        
        # v = bit length of l
        v = floor(log2(l)) + 1
        print('v = ', v)
        
        # concatenate x, i and q binary
        bytes_x = self.x[participant]
        bytes_i = bytes([i_secret])
        bytes_q = bytes([q_group])
        
        # TODO: check if bytes objects have proper lengths u,v
        
        message = b''.join([bytes_x, bytes_i, bytes_q]) # python 3.x
        print(message.hex())
        # hash the concatenated bytes
        share = self.hash(message)
        
        return self.modulo_p(share)
        
        # TODO: check why v, u = 2 while q,i size = 1 

