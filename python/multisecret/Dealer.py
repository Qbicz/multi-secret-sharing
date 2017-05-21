# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016-2017

from os import urandom
from math import log2, floor
# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
#import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from multisecret.primality import is_probable_prime

from multisecret.byteHelper import inverse_modulo_p

import copy # to have deepcopy, independent copy of a list


class Dealer:

    def __init__(self, p, n_participants, s_secrets, access_structures):
        """ Create a Dealer object with random AES-CTR nonce for collision-resistant hashing. [?]
        Dealer stores access structures, participants and secrets in 0-indexed arrays
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
            for group in access_structures:
                if len(group[0]) < 2:
                    raise ValueError('Less than 2 participants in one of the access groups!')
            self.access_structures = access_structures
        self.random_id = []
        self.hash_len = floor(log2(self.p))+1
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
        
        if(number >= self.p):
            number = number % self.p
        
        if(return_bytes):
            if number == 0:
                byte_len = 1
            else:
                bit_len = floor(log2(number))+1
                byte_len = bit_len // 8 +1
            #print('bit_len, byte_len', bit_len, byte_len)
            modulo_number = number.to_bytes(byte_len, byteorder='big')
        else:
            modulo_number = number
        
        return modulo_number
    
    
    def hash(self, message):
        """A collision resistant hash function h with variable output length:
        # option 1: use SHA-3 Keccak (variable length digest)
        # option 2: use BLAKE2 : variable length digest (available
            at "cryptography" library - but to bytes, not bits resolution)
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
        #print('Hash is ', varlen_hash.hex())
        
        return varlen_hash
        
        
    def list_of_random_in_modulo_p(self, listlen):
        """helper function returning list of random numbers less than p prime"""
        randoms = []
        bytelen_of_randoms_generated = self.hash_len # TODO: write bytelenOfInt() method in byteHelper
        
        for i in range(listlen):
            
            generated = urandom(bytelen_of_randoms_generated)
            randoms.append(self.modulo_p(generated))
            
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
    
    
    def get_id_int(self, participant):
        """ returns ID as an integer, with indexing from 1 """
        return int.from_bytes(self.random_id[participant-1], byteorder='big')
    
    
    def take_first_bits(self, input, bitlen):
        #print('Length of input', len(input))
    
        #print('take first bits from', input)
        if bitlen > 8*len(input):
            raise ValueError('input shorter than %d bits' % bitlen)
        elif bitlen == 8*len(input):
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
            mask = ~(0xff >> (8-(8*bytelen - bitlen)))
            output = bytes(input_bytelen[:bytelen-1])
            output += bytes([mask & last_byte])
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
                coeffs_for_A = self.list_of_random_in_modulo_p(len(A) - 1)
            
                print('A%d: %r' % (index,A))
                self.print_list_of_hex(coeffs_for_A, 'polynomial coeff d')
                
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
            if isinstance(coeff, bytes):
                coeff = int.from_bytes(coeff, byteorder='big')
            
            print('+ %d * %d^%d' % (coeff, x, degree+1))
            poly_value += coeff * x**(degree+1)
        
        poly_value += self.s_secrets[secret]
        print('+ secret (%d)' % self.s_secrets[secret])
        poly_value = self.modulo_p(poly_value)
        #print('poly_value', poly_value)    
        
        return poly_value
    
    
    def user_polynomial_value_B(self, i_secret, q_group, participant):
        
        assert(participant in self.access_structures[i_secret][q_group])
        print('polynomial value for user', participant)
        
        participant_id = self.random_id[participant-1]
        print('B value for user', participant)
        
        # returns int
        return self.f_polynomial_compute(participant_id, secret=i_secret, group=q_group)
                

    def compute_all_pseudo_shares_lists(self):
        """ experimental: use nested lists, don't use numpy arrays
            - this way we don't have empty (0) elements in pseudo_shares structure """
        self.pseudo_shares = copy.deepcopy(self.access_structures)
        print(self.access_structures)
        
        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    print('[i=%d][q=%d], participant=%r' % (i, q, Pb ))
                    # it's important to call with Pb - Participant number, not b - index
                    # e.g when A = (2,3) we should call function with 2 and 3, not 0 and 1
                    # but we store in in a list under indexes [i][q][0], [i][q][1]
                    self.pseudo_shares[i][q][b] = self.pseudo_share_participant(i, q, Pb)
                    print('[i=%d][q=%d][b=%d][Pb=%d], pseudo_share=%r' % (i, q, b, Pb, self.pseudo_shares[i][q][b] ))
        
        

    def pseudo_share_participant(self, i_secret, q_group, participant):
        """ pseudo share generation for a single participant
            U = h(x || i_U || q_v)
        """
    
        print('Pseudo share computation for secret s%r, access group A%r, participant P%r' % (i_secret, q_group, participant))

        # l = length of longest access group for this secret
        lengths = []
        gamma = self.access_structures[i_secret]
        for A in gamma:
            lengths.append(len(A)-1)
        l = max(lengths)
        
        # u = bit length of number of secrets k
        u = floor(log2(self.k)) + 1
        
        # v = bit length of l
        v = floor(log2(l)) + 1
        
        # concatenate x, i and q binary
        if isinstance(self.x[participant-1], bytes):
            bytes_x = self.x[participant-1]
        else:
            bytes_x = bytes([ self.x[participant-1] ])
        bytes_i = bytes([i_secret])
        bytes_q = bytes([q_group])

        # TODO: after retrieving secret, check if bytes objects have proper lengths u,v
        
        message = b''.join([bytes_x, bytes_i, bytes_q]) # python 3.x
        # hash the concatenated bytes
        hash_of_message = self.hash(message)
        share = self.modulo_p(hash_of_message)
        #print('Pseudo share for secret s%d, access group A%d, participant P%d:\nU = ' % (i_secret, q_group, participant), share.hex())
        
        return share


    def public_user_share_M(self, i_secret, q_group, participant, B_value):
        
        #assert(participant in self.access_structures[i_secret][q_group])
        
        U_value = int.from_bytes(self.pseudo_shares[i_secret][q_group][participant], byteorder='big')
        M_public_share = (B_value - U_value) % self.p
        print('participant %d, U = %d, public M = %d' % (participant, U_value, M_public_share))
        
        return M_public_share
                    
                    
    def compute_all_public_shares_M_lists(self):
        """ experimental, use nested lists instead of np.array """
        
        # duplicate the structure of access_structure
        self.public_shares_M = copy.deepcopy(self.access_structures)
        self.B_values = copy.deepcopy(self.access_structures)
        
        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    print('compute_all_public_shares_M, i=%d, q=%d, b=%d, user P%d' % (i,q,b,Pb))
                    
                    B_value = self.user_polynomial_value_B(i, q, Pb)
                    print('B_P%d = %d' % (Pb, B_value))
                    M = self.public_user_share_M(i, q, b, B_value)
                    
                    # for testing store B in a nested list
                    self.B_values[i][q][b] = B_value
                    
                    # STORE in a nested list
                    self.public_shares_M[i][q][b] = M
                    
        
    
    def get_M_public_user_share(self, i_secret, q_group, participant):
        
        return self.public_shares_M[i_secret][q_group][participant]
    
    
    def get_pseudo_shares_for_participant(self, participant):
        """ Scan for pseudo shares specific to a chosen participant.
            Returns a dictionary {(secret number,group) : pseudo_share}
        """
        my_pseudo_shares = {}
        
        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    # if we found participant in the access structure,
                    # copy his pseudo share to a dictionary with tuple key (secret, group)
                    if Pb == participant:
                        my_pseudo_shares[(i,q)] = self.pseudo_shares[i][q][b]
                        print('Pb == participant ==', Pb)
                        print('my_pseudo_shares[(i=%d,q=%d)]'
                              '= self.pseudo_shares[%d][%d][b=%d]' % (i,q,i,q,b))
        
        return my_pseudo_shares
        
        
    def set_pseudo_shares_from_participant(self, participant, my_pseudo_shares):
        """ Take my_pseudo_shares dictionary from a specific user and put shares
            into right places in the dealer's pseudo_shares nested list.
            (Reverse of get_pseudo_shares_for_participant() )
        """
        
        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    if Pb == participant:
                        self.pseudo_shares[i][q][b] = my_pseudo_shares['({}, {})'.format(i,q)]
        
    
    def split_secrets(self):
        """ Split secret in one step """
        
        self.provide_id() # a list of IDs stored internally
        self.choose_distinct_x()

        self.access_group_polynomial_coeffs()
        self.compute_all_pseudo_shares_lists()
        self.compute_all_public_shares_M_lists()
        
        return self.pseudo_shares
    
    
    def combine_secret(self, i_secret, q_group, obtained_pseudo_shares):
        """
        combine a single secret using Lagrange interpolation
        """
        
        if isinstance(obtained_pseudo_shares[0], bytes):
            obtained_shares_int = []
            for obtained_share in obtained_pseudo_shares:
                obtained_shares_int.append(int.from_bytes(obtained_share, byteorder='big'))
            obtained_pseudo_shares = obtained_shares_int
        
        print('Obtained pseudo shares:', obtained_pseudo_shares)
        
        print('Access group:',self.access_structures[i_secret])
        assert(q_group <= len( self.access_structures[i_secret]))
        
        combine_sum = 0
        
        for b, Pb in enumerate(self.access_structures[i_secret][q_group]):
            
            print('\tb =', b)
            part_sum_B = (obtained_pseudo_shares[b] \
                     + self.public_shares_M[i_secret][q_group][b]) % self.p
            print('\tB = U+M, B = %d, M=%d'
                  % (part_sum_B, self.public_shares_M[i_secret][q_group][b] ))
                     
            combine_product = 1
            for r, Pr in enumerate(self.access_structures[i_secret][q_group]):
                if r != b:
                    print('\t\tr =', r)
                    print('\t\tID_(b=%d) : %d, ID_(r=%d) : %d'
                          % (Pb, self.get_id_int(Pb), Pr, self.get_id_int(Pr) ))
                    denominator = (self.get_id_int(Pr) - self.get_id_int(Pb)) % self.p
                    den_inverse = inverse_modulo_p(denominator, self.p)
                    print('\t\tdenominator = %d\n its inverse = %d'
                          % (denominator, den_inverse))
                    part_product = ((self.get_id_int(Pr)) % self.p * den_inverse ) % self.p

                    combine_product *= part_product
                    print('\t\tpart_product', part_product)
                    print('\t\tcombine_product', combine_product)
            
            combine_sum += (part_sum_B * combine_product) % self.p
            print('\tcomb prod=%d, part_sum_B=%d, combined_sum=%d'
                  % (combine_product, part_sum_B, combine_sum))
            
        print("Combined sum, s%d = %d" % (i_secret, combine_sum % self.p))
        
        # obtained shares U should be passed by argument
        return self.modulo_p(combine_sum)
    