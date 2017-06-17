# Prototype of "Dynamic Multi Secret Sharing Scheme" by Lin & Yeh
# Filip Kubicz 2016-2017

from multisecret.primality import is_probable_prime
from multisecret.byteHelper import inverse_modulo_p
import os
import math

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

        print('hash_len:', self.hash_len)
        print(
            'Dealer created for Roy-Adhikari sharing of %d secrets among %d participants' % (
            self.k, self.n))


