# Tests for Omega 1 Multi Secret Sharing Scheme by Herranz, Ruiz & Saez
# Filip Kubicz 2017

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from multisecret.MultiSecretHerranzRuizSaez import Dealer
import multisecret.MultiSecretCommon as common

""" Declare basic params used to initialize Dealer in test cases """
# large prime from NIST P-256 elliptic curve
p256 = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1
# multi secret sharing parameters
s_secrets = [7, 313, 671]  # s_i
n_participants = 3
# access structure: to which secret what group has access
# Gamma(s_i) = [A1, A2, ... Al], Aq = (P1, P2, Pm), q=1,2...l
# gamma1 is a group of users authorized to reconstruct s1
gamma1 = [(1, 3)]
gamma2 = [(1, 2), (2, 3)]  # A1, A2 implicitly
gamma3 = [(1, 2, 3)]  # to secret s3 only all 3 users together can gain access
access_structures = [gamma1, gamma2, gamma3]


def test_init():
    """ check exception handling if params are faulty """

    # test for proper exception: p not prime
    with assert_raises(ValueError):
        dealer = Dealer(24, n_participants, s_secrets, access_structures)

    # test for proper exception: too little participants
    with assert_raises(ValueError):
        dealer = Dealer(p256, 1, s_secrets, access_structures)

def test_cipher_generate_user_keys():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.cipher_generate_user_keys()

    assert_equal(len(dealer.cipher_keys[-1]), Dealer.AES_KEY_LEN)
    assert_equal(len(dealer.cipher_keys), n_participants)

def test_cipher_encrypt():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.cipher_generate_user_keys()

    # Encrypt number
    input = 299
    key = dealer.cipher_keys[0]
    ciphertext = dealer.cipher_encrypt(input, key)
    assert_equal(len(ciphertext), Dealer.AES_BLOCK_SIZE)
    assert_equal(0,1)

def test_cipher_decrypt():
    pass

def test_access_group_polynomial_coeffs():
    """ test: access_group_polynomial_coeffs """

    A1 = (1, 3)
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [A1]
    gamma2 = [(1, 2), (2, 3)]  # A1, A2 implicitly
    gamma3 = [
        (1, 2, 3)]  # to secret s3 only all 3 users together can gain access
    access_structures = [gamma1, gamma2, gamma3]

    # Create a Dealer
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # compute d coeffs
    dealer.access_group_polynomial_coeffs()

    # dealer.print_list_of_hex(dealer.d[1][1], 'd-1-1')
    # test output
    assert_equal(len(dealer.d), 3)
    assert_equal(len(dealer.d[0]), 1)
    assert_equal(len(dealer.d[1][1]), 1)
    assert_equal(len(dealer.d[2][0]), 2)

    # Test index out of range
    with assert_raises(IndexError):
        print('Test', common.print_list_of_hex(dealer.d[2][1], 'd-2-1'))

