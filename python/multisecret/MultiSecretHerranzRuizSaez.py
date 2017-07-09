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

    # Length of AES keys in bytes. AES-128 has a key of 128 bits or 16 bytes
    AES_KEY_LEN = 16
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

        self.hash_len = math.floor(math.log2(self.p)) + 1

        # Setup for symmetric encryption scheme.
        # The initialization vector iv must be available to combiner.
        self.cipher_keys = []
        self.iv = os.urandom(Dealer.AES_BLOCK_SIZE)

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
        assert isinstance(ciphertext, (bytes, bytearray))

        if isinstance(key, int):
            key = int.to_bytes(key, Dealer.AES_KEY_LEN, byteorder='big')

        assert len(key) == Dealer.AES_KEY_LEN
        print('--- key ---', key)

        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # remove padding
        unpadder = padding.PKCS7(Dealer.AES_BLOCK_SIZE*8).unpadder()
        plaintext = unpadder.update(plaintext_padded) + unpadder.finalize()
        return plaintext

    def cipher_encrypt_all_secrets(self):
        assert self.k == len(self.s_secrets)

        self.public_shares_M = []
        for j, secret in enumerate(self.s_secrets):
            # compute c_j = Enc(s_j, K_j)
            encrypted_secret = self.cipher_encrypt(secret, self.cipher_keys[j])
            self.public_shares_M.append(encrypted_secret)
            #print()

        return self.public_shares_M

    def compute_all_key_shares(self):

        self.key_shares = copy.deepcopy(self.access_structures)
        print(self.access_structures)

        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):

                    print('secret_value (cipher_key)', self.cipher_keys[i])
                    secret_value = int.from_bytes(self.cipher_keys[i],
                                                  byteorder='big')
                    self.key_shares[i][q][b] = \
                        common.shamir_polynomial_compute(self.random_id[b],
                                                     self.d[i][q],
                                                     secret_value,
                                                     self.p)
                    print('Key share = {} for user {} (index {}) and secret {}'.format(
                        self.key_shares[i][q][b], Pb, b, i))

        return self.key_shares

    def split_secrets(self):
        """ High-level interface function.
            Use Shamir's scheme to share the keys used
            to encrypt secrets. """
        self.cipher_generate_keys()
        assert self.cipher_keys

        # Shamir polynomial for each access group
        self.access_group_polynomial_coeffs()
        assert self.d

        # ID for each participant
        self.random_id = common.provide_id(self.n, self.hash_len, self.p)

        self.cipher_encrypt_all_secrets()

        return self.compute_all_key_shares()
        #self.get_user_key_share(1)

    def get_user_key_share(self, user):
        assert self.key_shares
        assert user != 0
        user_shares = []

        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):

                user_shares.append(self.key_shares[i][q][user - 1])

        return user_shares

    def get_pseudo_shares_for_participant(self, participant):
        """
            Named for compatibility with other algorithms.

            Scan for pseudo shares specific to a chosen participant.
            Returns a dictionary {(secret number, access group) : pseudo_share}
        """
        my_pseudo_shares = {}

        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    # if we found participant in the access structure,
                    # copy his pseudo share to a dictionary with tuple key (secret, group)
                    if Pb == participant:
                        my_pseudo_shares[(i, q)] = self.key_shares[i][q][b]
                        print('Pb == participant ==', Pb)
                        print('my_pseudo_shares[(i=%d,q=%d)]'
                              '= self.pseudo_shares[%d][%d][b=%d]' % (
                              i, q, i, q, b))
        return my_pseudo_shares

    def set_pseudo_shares_from_participant(self, participant, my_pseudo_shares):
        """ Take my_pseudo_shares dictionary from a specific user and put shares
            into right places in the dealer's pseudo_shares nested list.
            (Reverse of get_pseudo_shares_for_participant() )
        """
        self.key_shares = copy.deepcopy(self.access_structures)

        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    if Pb == participant:
                        self.key_shares[i][q][b] = my_pseudo_shares[
                            '({}, {})'.format(i, q)]

    def get_share_from_user_for_secret(self, key_shares, secret_index):
        return key_shares[secret_index]

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


    def combine_secret_key(self, i_secret, obtained_shares):
        """
        combine a single key in Herraz-Ruiz-Saez algorithm
        """
        print('Obtained pseudo shares:', obtained_shares)
        q_group = 0

        combine_sum = 0

        for b, Pb in enumerate(self.access_structures[i_secret][q_group]):

            print('\tcurrent user {} with index {} =', Pb, b)
            part_sum = obtained_shares[b] % self.p

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

            combine_sum += (part_sum * combine_product) % self.p
            print('\tcomb prod=%d, part_sum_B=%d, combined_sum=%d'
                  % (combine_product, part_sum, combine_sum))

        print("Combined sum, s%d = %d" % (i_secret, combine_sum % self.p))

        return common.modulo_p(self.p, combine_sum)

    def combine_secret(self, i_secret, _, obtained_pseudo_shares):
        """ combine secret keys and use them to decipher secrets.
            High-level function. """

        secret_key = self.combine_secret_key(i_secret, obtained_pseudo_shares[i_secret])
        secret_key = secret_key.to_bytes(2*self.AES_KEY_LEN, byteorder='big')

        assert len(secret_key) == Dealer.AES_KEY_LEN

        secret_bytes = self.cipher_decrypt(self.public_shares_M[i_secret],
                                              secret_key)
        secret = int.from_bytes(secret_bytes, byteorder='big')
        return secret
