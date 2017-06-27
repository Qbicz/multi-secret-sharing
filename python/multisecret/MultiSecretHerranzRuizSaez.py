# Prototype of Omega 1 Multi Secret Sharing Scheme by Herranz, Ruiz & Saez
# Filip Kubicz 2017

import multisecret.MultiSecretCommon as common
from multisecret.primality import is_probable_prime
import multisecret.byteHelper as bytehelper
import os
import math
import copy
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class Dealer:

    # Length of AES keys in bytes. AES-256 has a key of 256 bits or 32 bytes
    AES_KEY_LEN = 32
    # All AES variants use 128 bit blocks and IV in CBC mode must have the same size as a block
    AES_BLOCK_SIZE = 16

    def __init__(self, p, n_participants, s_secrets, access_structures):
        """ In Omega 1 scheme symmetric encryption in used to protect
            secret shares. In this implementation AES CBC cipher is used,
            but it can be configured otherwise.
        """

        # check sanity of p
        if is_probable_prime(p) and p > n_participants and p > max(s_secrets):
            self.p = p
        else:
            raise ValueError('Wrong p selected!')

        if n_participants < 2:
            raise ValueError('There must be at least 2 participants!')
        else:
            self.n = n_participants
        self.k = len(s_secrets)  # number of secrets
        self.s_secrets = s_secrets
        if isinstance(access_structures[0], list):
            for group in access_structures:
                assert(len(group) == 1) # only one access group per secret (threshold scheme)
                if len(group[0]) < 2:
                    raise ValueError(
                        'Less than 2 participants in one of the access groups!')
            self.access_structures = access_structures
        self.random_id = []
        self.d = []

        # Setup for symmetric encryption scheme.
        # The initialization vector iv must be available to combiner.
        self.cipher_keys = []
        self.iv = os.urandom(Dealer.AES_BLOCK_SIZE)

        print('hash_len:', self.hash_len)
        print('Dealer created for Herranz-Ruiz-Saez sharing of %d secrets'
              ' among %d participants' % (self.k, self.n))

    def cipher_generate_keys(self):
        """ Generate a key K for each secret. The key will be used to
            encrypt all secrets. Key is later split among users. """
        for secret in range(self.k):
            key = os.urandom(Dealer.AES_KEY_LEN)
            self.cipher_keys.append(key)

    def cipher_encrypt(self, input, key):
        """ Symmetric encryption of input using key. If input is not bytes
            converts the input to needed format. """
        if(isinstance(input, int)):
            input = input.to_bytes(bytehelper.bytelen(input), byteorder='big')
        elif(isinstance(input, str)):
            input = input.encode('utf-8')

        print(input)
        assert(isinstance(input, (bytes, bytearray)))

        # Perform padding if the input is not a multiple of a block
        padder = padding.PKCS7(Dealer.AES_BLOCK_SIZE*8).padder()
        padded_input = padder.update(input) + padder.finalize()
        print(padded_input, len(padded_input))

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_input) + encryptor.finalize()
        print('Encrypted\t{}\n'
              'Key\t\t{}\n'
              'IV\t\t{}\n'
              'Ciphertext:\t{}'.format(padded_input, key, self.iv, ciphertext))
        return ciphertext

    def cipher_decrypt(self, ciphertext, key):
        assert(isinstance(ciphertext, (bytes, bytearray)))

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # remove padding
        unpadder = padding.PKCS7(Dealer.AES_BLOCK_SIZE*8).unpadder()
        plaintext = unpadder.update(plaintext_padded) + unpadder.finalize()
        return plaintext

    def cipher_encrypt_all_secrets(self):
        assert(self.k == len(self.s_secrets))

        self.public_encrypted_secrets = []
        for j, secret in enumerate(self.s_secrets):
            # compute c_j = Enc(s_j, K_j)
            encrypted_secret = self.cipher_encrypt(secret, self.cipher_keys[j])
            self.public_encrypted_secrets.append(encrypted_secret)

        return self.public_encrypted_secrets

    def compute_all_key_shares(self):

        self.key_shares = copy.deepcopy(self.access_structures)
        print(self.access_structures)

        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):

                    secret_value = int.from_bytes(self.cipher_keys[i],
                                                  byteorder='big')
                    self.key_shares[i][q][b] = \
                        common.shamir_polynomial_compute(self.random_id[b],
                                                     self.d[i][q],
                                                     secret_value,
                                                     self.p)
        return self.key_shares

    def split_secret_keys(self):
        """ High-level interface function.
            Use Shamir's scheme to share the keys used
            to encrypt secrets. """
        self.cipher_generate_keys()
        assert(self.cipher_keys)

        # Shamir polynomial for each access group
        self.access_group_polynomial_coeffs()
        assert(self.d)

        # ID for each participant
        self.random_id = common.provide_id(self.n, self.hash_len, self.p)

        self.compute_all_key_shares()
        #self.get_user_key_share(1)

    def get_user_key_share(self, user):
        assert(self.key_shares)
        user_shares = []

        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):

                user_shares.append(self.key_shares[i][q][user])

        return user_shares

    def access_group_polynomial_coeffs(self):
        """ In Herraz-Ruiz-Saez scheme, there's only one access group for
            each secret (threshold scheme).

            The dealer chooses d0, d1, d2... dm in Zp modulo field
            to construct the polynomial
            f_q(x) = si + d1*x + d2*x^2 + ... + dm*x^(m-1)

            note: d0 corresponds to x^1, d1 corresponds to x^2
        """
        for gindex, gamma in enumerate(self.access_structures):
            print('gamma%d for secret s%d:' % (gindex, gindex))
            coeffs_for_A = []
            self.d.append([])

            for index, A in enumerate(gamma):
                coeffs_for_A = common.list_of_random_in_modulo_p(len(A) - 1,
                                                                 self.hash_len,
                                                                 self.p)
                print('A%d: %r' % (index, A))
                common.print_list_of_hex(coeffs_for_A, 'polynomial coeff d')

                self.d[gindex].append(coeffs_for_A)
        return self.d

    def get_id_int(self, participant):
        """ returns ID as an integer, with indexing from 1 """
        return int.from_bytes(self.random_id[participant-1], byteorder='big')

    def get_d_polynomial_coeffs(self, secret, group):
        return self.d[secret][group]

                 i, q, b, Pb, self.pseudo_shares[i][q][b]))

    def split_secrets(self):
        """ Split secret in one step with Lin-Yeh algorithm """

        self.random_id = common.provide_id(self.n, self.hash_len, self.p)
        self.master_shares_x = common.list_of_random_in_modulo_p(self.n,
                                                                 self.hash_len,
                                                                 self.p)
        self.access_group_polynomial_coeffs()
        self.compute_all_pseudo_shares()
        self.compute_all_public_shares_M()

        return self.pseudo_shares

    def combine_secret(self, i_secret, q_group, obtained_pseudo_shares):
        """
        combine a single secret in Lin-Yeh algorithm
        """
        if isinstance(obtained_pseudo_shares[0], bytes):
            obtained_shares_int = []
            for obtained_share in obtained_pseudo_shares:
                obtained_shares_int.append(
                    int.from_bytes(obtained_share, byteorder='big'))
            obtained_pseudo_shares = obtained_shares_int

        print('Obtained pseudo shares:', obtained_pseudo_shares)

        print('Access group:', self.access_structures[i_secret])
        assert (q_group <= len(self.access_structures[i_secret]))

        combine_sum = 0

        for b, Pb in enumerate(self.access_structures[i_secret][q_group]):

            print('\tb =', b)
            part_sum_B = (obtained_pseudo_shares[b]
                          + self.public_shares_M[i_secret][q_group][b]) % self.p
            print('\tB = U+M, B = %d, M=%d'
                  % (part_sum_B, self.public_shares_M[i_secret][q_group][b]))

            combine_product = 1
            for r, Pr in enumerate(self.access_structures[i_secret][q_group]):
                if r != b:
                    print('\t\tr =', r)
                    print('\t\tID_(b=%d) : %d, ID_(r=%d) : %d'
                          % (Pb, self.get_id_int(Pb), Pr, self.get_id_int(Pr)))
                    denominator = (self.get_id_int(Pr) - self.get_id_int(
                        Pb)) % self.p
                    den_inverse = bytehelper.inverse_modulo_p(denominator,
                                                              self.p)
                    print('\t\tdenominator = %d\n its inverse = %d'
                          % (denominator, den_inverse))
                    part_product = ((self.get_id_int(
                        Pr)) % self.p * den_inverse) % self.p

                    combine_product *= part_product
                    print('\t\tpart_product', part_product)
                    print('\t\tcombine_product', combine_product)

            combine_sum += (part_sum_B * combine_product) % self.p
            print('\tcomb prod=%d, part_sum_B=%d, combined_sum=%d'
                  % (combine_product, part_sum_B, combine_sum))

        print("Combined sum, s%d = %d" % (i_secret, combine_sum % self.p))

        return common.modulo_p(self.p, combine_sum)

