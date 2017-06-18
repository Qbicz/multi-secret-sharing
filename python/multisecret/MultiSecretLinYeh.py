# Prototype of "Dynamic Multi Secret Sharing Scheme" by Lin & Yeh
# Filip Kubicz 2016-2017

import multisecret.MultiSecretCommon as common
from multisecret.primality import is_probable_prime
from multisecret.byteHelper import inverse_modulo_p
import os
import math
import copy


class Dealer:

    def __init__(self, p, n_participants, s_secrets, access_structures):
        """ A dealer class, in Lin-Yeh publication called system authority (SA).
            Responsible for sharing secrets and publication of data required
            for secret reconstruction.
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
                if len(group[0]) < 2:
                    raise ValueError(
                        'Less than 2 participants in one of the access groups!')
            self.access_structures = access_structures
        self.random_id = []
        self.hash_len = math.floor(math.log2(self.p)) + 1
        self.hash_aes_nonce = os.urandom(16)
        self.d = []

        print('hash_len:', self.hash_len)
        print(
            'Dealer created for Lin-Yeh sharing of %d secrets among %d participants' % (
            self.k, self.n))

    def access_group_polynomial_coeffs(self):
        """ for the qth qualified set of access group,
            the dealer chooses d0, d1, d2... dm in Zp modulo field
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

    def get_d_polynomial_coeffs(self, secret, group):
        return self.d[secret][group]

    def user_polynomial_value_B(self, i_secret, q_group, participant):
        assert (participant in self.access_structures[i_secret][q_group])

        print('user_polynomial_value_B for secret %d, group A %d '.format(
            i_secret, q_group))
        participant_id = self.random_id[participant - 1]
        print('B value for user %d with ID %d'.format(participant,
                                                      participant_id))

        coeffs = self.get_d_polynomial_coeffs(i_secret, q_group)
        secret_value = self.s_secrets[i_secret]

        # returns int
        return common.shamir_polynomial_compute(participant_id, coeffs,
                                                secret_value, self.p)

    def compute_all_pseudo_shares(self):
        """ In Lin-Yeh algorithm, pseudo shares are created as follows:
            U = hash(master_share_x) XOR master_share_x
        """
        self.pseudo_shares = copy.deepcopy(self.access_structures)
        print(self.access_structures)

        for i, gamma in enumerate(self.access_structures):
            for q, A in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    print('[i=%d][q=%d], participant=%r' % (i, q, Pb))
                    # it's important to call with Pb - Participant number, not b - index
                    # e.g when A = (2,3) we should call function with 2 and 3, not 0 and 1
                    # but we store in in a list under indexes [i][q][0], [i][q][1]
                    self.pseudo_shares[i][q][b] = self.pseudo_share_participant(
                        i, q, Pb)
                    print('[i={}][q={}][b={}][Pb={}], pseudo_share={!r}'.format(
                        i, q, b, Pb, self.pseudo_shares[i][q][b]))

    def pseudo_share_participant(self, i_secret, q_group, participant):
        """ pseudo share generation for a single participant
            U = hash(master_share_x) XOR master_share_x
        """
        print('Pseudo share computation for secret s%r, access group A%r,'
              'participant P%r' % (i_secret, q_group, participant))

        # convert master share to bytes
        if isinstance(self.master_shares_x[participant - 1], bytes):
            bytes_x = self.master_shares_x[participant - 1]
            int_x = int.from_bytes(self.master_shares_x[participant - 1], byteorder='big')
        else:
            bytes_x = bytes([self.master_shares_x[participant - 1]])
            int_x = self.master_shares_x[participant - 1]

        # hash the master share
        hash_of_master_share = common.hash(bytes_x, self.hash_len, self.hash_aes_nonce)
        hash_of_master_share = common.modulo_p(self.p, hash_of_master_share)

        hash_of_master_share_int = int.from_bytes(hash_of_master_share, byteorder='big')

        print('XOR\n {} \n{}'.format(hash_of_master_share.hex(), bytes_x.hex()))
        # XOR hashed value with master share
        int_pseudo_share = hash_of_master_share_int ^ int_x
        pseudo_share = bytes([int_pseudo_share])
        print(pseudo_share.hex())

        # print('Pseudo share for secret s%d, access group A%d, participant P%d:\nU = ' % (i_secret, q_group, participant), share.hex())
        assert isinstance(pseudo_share, bytes)
        return pseudo_share

    def public_user_share_M(self, i_secret, q_group, participant, B_value):
        """ In Lin-Yeh algorithm, public share M is created as follows:
            M = B - U
        """
        # assert(participant in self.access_structures[i_secret][q_group])

        U_value = int.from_bytes(
            self.pseudo_shares[i_secret][q_group][participant], byteorder='big')
        M_public_share = (B_value - U_value) % self.p
        print('participant %d, U = %d, public M = %d' % (
        participant, U_value, M_public_share))
        return M_public_share

    def compute_all_public_shares_M(self):
        """ experimental, use nested lists instead of np.array """

        # duplicate the structure of access_structure
        self.public_shares_M = copy.deepcopy(self.access_structures)
        self.B_values = copy.deepcopy(self.access_structures)

        for i, _ in enumerate(self.access_structures):
            for q, _ in enumerate(self.access_structures[i]):
                for b, Pb in enumerate(self.access_structures[i][q]):
                    print(
                        'compute_all_public_shares_M, i=%d, q=%d, b=%d, user P%d' % (
                        i, q, b, Pb))

                    B_value = self.user_polynomial_value_B(i, q, Pb)
                    print('B_P%d = %d' % (Pb, B_value))
                    M = self.public_user_share_M(i, q, b, B_value)

                    # for testing store B in a nested list
                    self.B_values[i][q][b] = B_value

                    # STORE in a nested list
                    self.public_shares_M[i][q][b] = M

    def get_M_public_user_share(self, i_secret, q_group, participant):

        return self.public_shares_M[i_secret][q_group][participant]

    def split_secrets(self):
        """ Split secret in one step """

        self.random_id = common.provide_id(self.n, self.hash_len, self.p)
        self.master_shares_x = common.list_of_random_in_modulo_p(self.n, self.hash_len,
                                                 self.p)
        self.access_group_polynomial_coeffs()
        self.compute_all_pseudo_shares()
        self.compute_all_public_shares_M()

        return self.pseudo_shares


