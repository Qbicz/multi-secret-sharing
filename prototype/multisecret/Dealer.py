# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from os import urandom
from math import log2, floor, ceil
# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
#import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from multisecret.primality import is_probable_prime

import numpy as np
from sys import byteorder

class Dealer:

    def __init__(self, p, n_participants, s_secrets, access_structures):
        """ Create a Dealer object with random AES-CTR nonce for collision-resistant hashing. [?]
        Dealer stores access structures, participants and secrets in array beginning at 0
        """
        
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
        """ works for:
        - int type
        - bytes type
        """
        return_bytes = False
    
        # if input is bytes, convert it to int, but return bytes object
        if(isinstance(number, bytes)):
            return_bytes = True
            number = int.from_bytes(number, byteorder='big')
        
        #print(number)
        #print(log2(number))
        
        # compare int objects
        assert(isinstance(number, int))
        if(number > self.p):
            number = number % self.p
        
        if(return_bytes):
            bit_len = floor(log2(number))+1
            byte_len = floor(bit_len/8)+1
            #print('bit_len, byte_len', bit_len, byte_len)
            modulo_number = number.to_bytes(byte_len, byteorder='big')
        else:
            modulo_number = number
        
        return modulo_number
    
    
    def hash(self, message):
        """A collision resistant hash function h with variable output length:
        # option 1: use SHA-3 Keccak (variable length digest)
        # option 2: use BLAKE2 : variable length digest (available at "cryptography" library - but to bytes, not bits resolution)
        # option 3 (chosen): use the first [log2(p)]+1 bits of AES-CTR(SHA256(m))"""

        # SHA256 of message
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(message)
        hashed_message = digest.finalize()

        # AES-CTR of the hash
        aes_key = hashed_message
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(self.aes_nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        input = b'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
        #print(input.hex())
        ciphertext = encryptor.update(input) + encryptor.finalize()

        # take demanded numer of bits
        varlen_hash = self.take_first_bits(ciphertext, self.hash_len)
        print(varlen_hash.hex())
        
        return varlen_hash
        
        
    def list_of_random_in_modulo_p(self, listlen):
        """helper function returning list of random numbers less than p prime"""
        randoms = []
        bytelen_of_randoms_generated = 32 # TODO: write bytelenOfInt() method in byteHelper
        
        for i in range(listlen):
            while True:
                randoms.append(urandom(bytelen_of_randoms_generated))
                if(int.from_bytes(randoms[i], byteorder='big') < self.p):
                    break
            
        return randoms # TODO: yield generator for bigger problem sizes

        
    def print_list_of_hex(self, list_to_print, description):
        """helper to print list of bytes objects with string description"""
        for i in range(len(list_to_print)):
            print('%s%d = %s' % (description, i, list_to_print[i].hex()))

            
    def provide_id(self):
        """for each participant provide ID in p modulo field"""
        self.random_id = self.list_of_random_in_modulo_p(self.n)
        self.print_list_of_hex(self.random_id, 'Participant ID ')
        
        return self.random_id
    
    
    def take_first_bits(self, input, bitlen):
        #print('Length of input', len(input))
    
        if bitlen > 8*len(input):
            raise ValueError('input shorter than %d bits' % bitlen)
        elif bitlen == 8*len(input):
            return input
        else:
            # take all bytes needed
            if bitlen % 8 == 0:
                bytelen = int(bitlen/8)
            else:
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
        """ for the qth qualified set of access group,
            the dealer chooses d0, d1, d2... dm in Zp modulo field
            to construct the polynomial
            f_q(x) = si + d1*x + d2*x^2 + ... + dm*x^(m-1)
            
            note: d0 corresponds to x^1, d1 corresponds to x^2
        """
        self.d = []
        
        for gindex, gamma in enumerate(self.access_structures):
            print('gamma%d for secret s%d:' % (gindex,gindex))
            coeffs_for_A = []
            self.d.append([])
            
            for index, A in enumerate(gamma):
                #self.d[index].append(self.list_of_random_in_modulo_p(len(A)))
                coeffs_for_A = self.list_of_random_in_modulo_p(len(A))
            
                print('A%d: %r' % (index,A))
                self.print_list_of_hex(coeffs_for_A, 'polynomial coeff d')
                # TODO: dla kazdej grupy powinno byc inaczej, osobno
                
                self.d[gindex].append(coeffs_for_A)
              
        return self.d
            
    
    def get_d_polynomial_coeffs(self, secret, group):
        
        return self.d[secret][group]


    def f_polynomial_compute(self, x, *, secret, group):
        """ compute f_q(x) for q-th access group in access structure """    
        
        print('f_polynomial_compute for secret %d, group A %d ' % (secret, group))
        poly_value = 0;
        coeffs = self.get_d_polynomial_coeffs(secret, group)
        
        #print('x=', x.hex())
        if isinstance(x, bytes):
            x = int.from_bytes(x, byteorder='big')
        
        for degree, coeff in enumerate(coeffs):
            coeff = int.from_bytes(coeff, byteorder='big')
            
            #print('d%d, coeff=%d' % (degree+1, coeff))
            poly_value += coeff * x**(degree+1)
        
        poly_value += self.s_secrets[secret]
        #print('secret =', self.s_secrets[secret])
        print('poly_value', poly_value)    
        
        return poly_value
    
    
    def user_polynomial_value_B(self, i_secret, q_group, participant):
        
        assert(participant in self.access_structures[i_secret][q_group])
        
        participant_id = self.random_id[participant-1]
        print('B value for user', participant)
        
        # returns int
        return self.f_polynomial_compute(participant_id, secret=i_secret, group=q_group)
                
    
    def pseudo_share_array_size_iqb(self):
        """ Return sizes i, q, b needed for holding pseudo shares and shares
        
        """
        max_i_list = []
        max_q_list = []
        max_b_list = []
        # keep pseudo shares in a 3D array
        for i, gamma in enumerate(self.access_structures):
            max_i_list.append(i)
            for q, A in enumerate(gamma):
                max_q_list.append(q)
                max_b_list.append(max(A))
                #for b, Pb in enumerate(A):
                #    max_b_list.append(b)
        
        max_i = max(max_i_list)
        max_q = max(max_q_list)
        max_b = max(max_b_list)
        
        print('sizes: i, q, b', max_i, max_q, max_b)
        return (max_i+1, max_q+1, max_b+1)


    def compute_all_pseudo_shares(self):
        """ compute all pseudo shares U """
        
        # use desired type 'object' to allow holding bytes/strings in a numpy array
        self.pseudo_shares = np.zeros(self.pseudo_share_array_size_iqb(), dtype=object)
        
        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(gamma):
                for b in A:
                    print('compute_all_pseudo_shares, i=%d, q=%d, b=%d' % (i,q,b))
                    U = self.pseudo_share_participant(i, q, b)
                    
                    # STORE in a 3D array
                    self.pseudo_shares[i][q][b] = U
                    #print(self.pseudo_shares)
            
        print(self.pseudo_shares)


    def pseudo_share_participant(self, i_secret, q_group, participant):
        """ pseudo share generation for a single participant
            U = h(x || i_U || q_v)
        """
    
        print('Pseudo share computation for secret s%d, access group A%d, participant P%d' % (i_secret, q_group, participant))

        # l = length of longest access group for this secret
        lengths = []
        gamma = self.access_structures[i_secret]
        for A in gamma:
            lengths.append(len(A)-1)
        l = max(lengths)
        #print('l = ', l)
        
        # u = bit length of number of secrets k
        u = floor(log2(self.k)) + 1
        #print('u = ', u)
        
        # v = bit length of l
        v = floor(log2(l)) + 1
        #print('v = ', v)
        
        # concatenate x, i and q binary
        bytes_x = self.x[participant-1]
        bytes_i = bytes([i_secret])
        bytes_q = bytes([q_group])

        # TODO: after retrieving secret, check if bytes objects have proper lengths u,v
        
        message = b''.join([bytes_x, bytes_i, bytes_q]) # python 3.x
        # hash the concatenated bytes
        print('[x,i,q]: ', message.hex())
        hash_of_message = self.hash(message)
        #print('hash of [x,i,q]', hash_of_message.hex())
        share = self.modulo_p(hash_of_message)
        print('Pseudo share for secret s%d, access group A%d, participant P%d:\nU = ' % (i_secret, q_group, participant), share.hex())
        
        return share


    def public_user_share_M(self, i_secret, q_group, participant, B_value):
        
        assert(participant in self.access_structures[i_secret][q_group])
        
        U_value = int.from_bytes(self.pseudo_shares[i_secret][q_group][participant], byteorder='big')
        M_public_share = B_value - U_value
        print('participant %d, public M = %d' % (participant, M_public_share))
        
        return M_public_share
    
    
    def compute_all_public_shares_M(self):
        
        # use desired type 'object' to allow holding bytes/strings in a numpy array
        self.public_shares_M = np.zeros(self.pseudo_share_array_size_iqb(), dtype=object)
        
        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(gamma):
                for b in A:
                    print('compute_all_public_shares_M, i=%d, q=%d, b=%d' % (i,q,b))
                    
                    B_value = self.user_polynomial_value_B(i, q, b)
                    M = self.public_user_share_M(i, q, b, B_value)
                    
                    # STORE in a 3D array
                    self.public_shares_M[i][q][b] = M
        
    
    def get_M_public_user_share(self, i_secret, q_group, participant):
        pass
        
        
    
