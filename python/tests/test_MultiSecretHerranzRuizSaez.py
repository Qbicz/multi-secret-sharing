# Tests for Omega 1 Multi Secret Sharing Scheme by Herranz, Ruiz & Saez
# Filip Kubicz 2017

from nose.tools import assert_equal
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
gamma1 = [[1, 3]]
gamma2 = [[1, 2]]  # A1, A2 implicitly
gamma3 = [[1, 2, 3]]  # to secret s3 only all 3 users together can gain access
access_structures = [gamma1, gamma2, gamma3]


def test_init():
    """ check exception handling if params are faulty """

    # test for proper exception: p not prime
    with assert_raises(ValueError):
        dealer = Dealer(24, n_participants, s_secrets, access_structures)

    # test for proper exception: too little participants
    with assert_raises(ValueError):
        dealer = Dealer(p256, 1, s_secrets, access_structures)

def test_assert_one_group_per_secret():
    with assert_raises(AssertionError):
        dealer = Dealer(p256, 2, s_secrets, [[(1,2,3)], [(1,2), (1,2,3)]])

def test_cipher_generate_keys():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.cipher_generate_keys()

    assert_equal(len(dealer.cipher_keys[-1]), Dealer.AES_KEY_LEN)
    assert_equal(len(dealer.cipher_keys), len(s_secrets))

def test_cipher_encrypt():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.cipher_generate_keys()

    # Encrypt number
    input = 299
    key = dealer.cipher_keys[0]
    ciphertext = dealer.cipher_encrypt(input, key)
    assert_equal(len(ciphertext), Dealer.AES_BLOCK_SIZE)

def test_cipher_decrypt():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.cipher_generate_keys()

    test_input = 'Test message'
    ciphertext = dealer.cipher_encrypt(test_input, dealer.cipher_keys[-1])
    assert_equal(len(ciphertext), Dealer.AES_BLOCK_SIZE)

    plaintext = dealer.cipher_decrypt(ciphertext, dealer.cipher_keys[-1])
    print('type of decrypted plaintext', type(plaintext))
    assert_equal(plaintext.decode('utf-8'), test_input) # decrypted data has type bytes

def test_cipher_encrypt_all_secrets():
    dealer = Dealer(p256, n_participants, [41, 12], access_structures)
    dealer.cipher_generate_keys()
    dealer.cipher_encrypt_all_secrets()

    assert_equal(len(dealer.public_shares_M), len([41, 12]))
    assert_equal(len(dealer.public_shares_M[0]), Dealer.AES_BLOCK_SIZE)

def test_split_secret_keys():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # this function invokes low-level methods
    dealer.split_secrets()

    print(dealer.key_shares)
    assert_equal(len(dealer.key_shares), len(dealer.s_secrets))

def test_get_user_key_share():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # this function invokes low-level methods
    dealer.split_secrets()
    user_share = dealer.get_user_key_share(1)

    print('All key shares', dealer.key_shares)
    print('User 0 key share', user_share)

    assert_equal(user_share[0], dealer.key_shares[0][0][0])
    # user 2 has internally index 1
    assert_equal(dealer.get_user_key_share(2)[1], dealer.key_shares[1][0][1])
    assert_equal(dealer.get_user_key_share(2)[0], dealer.key_shares[0][0][1])
    # if it not available, shout at user!


def test_access_group_polynomial_coeffs():
    """ test: access_group_polynomial_coeffs """

    A1 = (1, 3)
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [A1]
    gamma2 = [(1, 2)]  # A1, A2 implicitly
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
    assert_equal(len(dealer.d[1][0]), 1)
    assert_equal(len(dealer.d[2][0]), 2)

    # Test index out of range
    with assert_raises(IndexError):
        print('Test', common.print_list_of_hex(dealer.d[2][1], 'd-2-1'))

def test_combine_secret_2_users():
    """ Acceptance test with 2 users """
    secrets = [7, 9]
    dealer = Dealer(p256, 2, secrets, [[[1,2]], [[1,2]]])
    dealer.split_secrets()

    share1 = dealer.get_user_key_share(1)
    share2 = dealer.get_user_key_share(2)

    print('Secrets shared!')

    shares_for_secret_0 = [share1[0], share2[0]]
    print('Combine using shares: %r', shares_for_secret_0)

    secret_key_0 = dealer.combine_secret_key(0, shares_for_secret_0)

    assert_equal(secret_key_0.to_bytes(dealer.AES_KEY_LEN, byteorder='big'), dealer.cipher_keys[0])

    secret0_bytes = dealer.cipher_decrypt(dealer.public_shares_M[0], secret_key_0)
    secret0 = int.from_bytes(secret0_bytes, byteorder='big')

    assert_equal(secret0, secrets[0])

def test_combine_secret_3_users():
    """ Acceptance test with 3 users and not-full access groups """

    secrets = [7, 9]
    user_num = 4
    dealer = Dealer(17, user_num, secrets, [[[1, 4]], [[2, 3, 4]]])
    dealer.split_secrets()
    print('Secrets shared!')

    user_shares = []

    # for user in dealer.access_structures[0][0]
    for user in range(user_num): # here only users who are in access group should give their shares
        share = dealer.get_user_key_share(user)
        user_shares.append(share)

    shares_for_secret_0 = [share[0] for share in user_shares]
    #shares_for_secret_0 = [share1[0], share2[0]]it
    print('Combine using shares: %r', shares_for_secret_0)
    assert False

    secret_key_0 = dealer.combine_secret_key(0, shares_for_secret_0)

    assert_equal(secret_key_0.to_bytes(dealer.AES_KEY_LEN, byteorder='big'),
                 dealer.cipher_keys[0])

    secret0_bytes = dealer.cipher_decrypt(dealer.public_shares_M[0],
                                          secret_key_0)
    secret0 = int.from_bytes(secret0_bytes, byteorder='big')

    assert_equal(secret0, secrets[0])


