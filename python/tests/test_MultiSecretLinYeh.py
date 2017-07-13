# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016-2017

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises

from multisecret.MultiSecretLinYeh import Dealer
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


def test_hash_same():
    """ set up Dealer object and check hash repeatability """

    # Create a Dealer
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # test hash function - it should be repeatable for the same Dealer object
    hash1 = common.hash(b'BYTESEQUENCE', dealer.hash_len, dealer.hash_aes_nonce)
    hash2 = common.hash(b'BYTESEQUENCE', dealer.hash_len, dealer.hash_aes_nonce)
    assert_equal(hash1, hash2)


def test_hash_different():
    """ different instances of Dealer should have different
        hash results as they have separate random AES nonces"""

    # Create a Dealer
    dealer1 = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer2 = Dealer(p256, n_participants, s_secrets, access_structures)

    # test hash function - it should be different for distinct Dealers
    hash1 = common.hash(b'BYTESEQUENCE', dealer1.hash_len, dealer1.hash_aes_nonce)
    hash2 = common.hash(b'BYTESEQUENCE', dealer2.hash_len, dealer2.hash_aes_nonce)
    assert_not_equal(hash1, hash2)


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


def test_get_d_polynomial_coeffs():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.access_group_polynomial_coeffs()

    coeff1 = dealer.get_d_polynomial_coeffs(secret=2, group=0)[1]
    coeff2 = dealer.d[2][0][1]

    assert_equal(coeff1, coeff2)


def test_combine_first_secret_3_participants():
    """ Acceptance test: secret with index [0]  """

    s1 = 4
    p = 13
    # access group
    A = [1, 2, 3]
    gamma1 = [A]
    # user IDs
    IDs = [1, 2, 3]
    # polynomial coeffs
    d1 = 2
    d2 = 1

    dealer = Dealer(p, len(A), [s1, 9], [gamma1])
    assert_equal(dealer.n, 3)

    # set IDs, don't generate random
    byte_IDs = []
    for ID in IDs:
        byte_IDs.append(bytes([ID]))
    print('[test] byte IDs: ', byte_IDs)
    dealer.random_id = byte_IDs

    # set polynomial coeffs
    dealer.d = [[], []]
    dealer.d[0].append([d1, d2])
    assert_equal([2, 1], dealer.get_d_polynomial_coeffs(0, 0))

    # set x-shares for pseudo share generation only
    dealer.master_shares_x = [3, 4, 5]

    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()

    # [0,5,5] when testing with p = 7
    # print(dealer.B_values)
    # assert_equal(True, array_equal([[[0,5,5]]], dealer.B_values))

    obtained_pseudo_shares = dealer.pseudo_shares[0][0]
    print('Obtained pseudo shares:', obtained_pseudo_shares)
    combined_secret = dealer.combine_secret(0, 0, obtained_pseudo_shares)

    assert_equal(combined_secret, s1)


def test_combine_second_secret_3_participants():
    """ Acceptance test: secret with index [1] when it is the longest access group """

    secrets = [7, 9]
    p = 41
    # access groups
    A = [1, 2]
    gamma1 = [A]
    gamma2 = [[1, 2, 3]]
    # user IDs
    IDs = [1, 2, 3]
    # polynomial coeffs
    d1 = 2
    d2 = 1

    dealer = Dealer(p, 3, secrets, [gamma1, gamma2])
    assert_equal(dealer.n, 3)

    # set IDs, don't generate random
    byte_IDs = []
    for ID in IDs:
        byte_IDs.append(bytes([ID]))
    print('[test] byte IDs: ', byte_IDs)
    dealer.random_id = byte_IDs

    # set polynomial coeffs
    dealer.d = [[], []]
    dealer.d[0].append([d1, d2])
    assert_equal([2, 1], dealer.get_d_polynomial_coeffs(0, 0))
    dealer.d[1].append([d2, d1])
    assert_equal([1, 2], dealer.get_d_polynomial_coeffs(1, 0))

    # set x-shares for pseudo share generation only
    dealer.master_shares_x = [3, 4, 5]

    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()

    # [0,5,5] when testing with p = 7
    # print(dealer.B_values)
    # assert_equal(True, array_equal([[[0,5,5]]], dealer.B_values))

    CHOSEN_SECRET = 1

    obtained_pseudo_shares = dealer.pseudo_shares[CHOSEN_SECRET][0]
    print('Obtained pseudo shares:', obtained_pseudo_shares)
    combined_secret = dealer.combine_secret(CHOSEN_SECRET, 0,
                                            obtained_pseudo_shares)

    assert_equal(combined_secret, secrets[CHOSEN_SECRET])


def test_combine_secret_for_shorter_group():
    """ Acceptance test: combine secret with a 2-member access group
        when there are other 3-member groups """

    secrets = [7, 13]
    p = 41
    # access group
    A = [1, 2]
    gamma1 = [A]
    gamma2 = [[1, 2, 3]]
    # user IDs
    IDs = [1, 2, 3]
    # polynomial coeffs
    d1 = 2
    d2 = 1

    dealer = Dealer(p, 3, secrets, [gamma1, gamma2])
    assert_equal(dealer.n, 3)

    # set IDs, don't generate random
    byte_IDs = []
    for ID in IDs:
        byte_IDs.append(bytes([ID]))
    print('[test] byte IDs: ', byte_IDs)
    dealer.random_id = byte_IDs

    # set polynomial coeffs
    dealer.d = [[], []]
    dealer.d[0].append([d1])
    assert_equal([2], dealer.get_d_polynomial_coeffs(0, 0))
    dealer.d[1].append([d2, d1])
    assert_equal([1, 2], dealer.get_d_polynomial_coeffs(1, 0))

    # set x-shares for pseudo share generation only
    dealer.master_shares_x = [3, 4, 5]

    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()

    # [0,5,5] when testing with p = 7
    # print(dealer.B_values)
    # assert_equal(True, array_equal([[[0,5,5]]], dealer.B_values))

    CHOSEN_SECRET = 0

    obtained_pseudo_shares = dealer.pseudo_shares[CHOSEN_SECRET][0]
    print('Obtained pseudo shares:', obtained_pseudo_shares)
    combined_secret = dealer.combine_secret(CHOSEN_SECRET, 0,
                                            obtained_pseudo_shares)

    assert_equal(combined_secret, secrets[CHOSEN_SECRET])


def test_combine_with_random_d_coefficients():
    """ Acceptance test: generate d coeffs & combine secret """

    secrets = [7, 13]
    p = 41
    # access group
    A = [1, 2]
    gamma1 = [A]
    gamma2 = [[1, 2, 3]]

    dealer = Dealer(p, 3, secrets, [gamma1, gamma2])
    assert_equal(dealer.n, 3)

    # user IDs
    IDs = [1, 2, 3]

    # set IDs, don't generate random
    byte_IDs = []
    for ID in IDs:
        byte_IDs.append(bytes([ID]))
    print('[test] byte IDs: ', byte_IDs)
    dealer.random_id = byte_IDs

    #
    # set polynomial coeffs
    #
    dealer.access_group_polynomial_coeffs()
    # assert_equal([2], dealer.get_d_polynomial_coeffs(0, 0))
    # assert_equal([1,2], dealer.get_d_polynomial_coeffs(1, 0))

    # set x-shares for pseudo share generation only
    dealer.master_shares_x = [3, 4, 5]

    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()

    # [0,5,5] when testing with p = 7
    # print(dealer.B_values)
    # assert_equal(True, array_equal([[[0,5,5]]], dealer.B_values))

    CHOSEN_SECRETS = (0, 1)

    for chosen_secret in CHOSEN_SECRETS:
        obtained_pseudo_shares = dealer.pseudo_shares[chosen_secret][0]
        print('Obtained pseudo shares:', obtained_pseudo_shares)
        combined_secret = dealer.combine_secret(chosen_secret, 0,
                                                obtained_pseudo_shares)

        assert_equal(combined_secret, secrets[chosen_secret])


def test_combine_secret_4_participants_in_3_groups():
    """ Acceptance test from the example, but with 4099 prime """
    prime = 41
    s_secrets = [7, 5, 3]  # s_i
    n_participants = 3
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [[1, 3, 4]]
    gamma2 = [[1, 2, 4], [2, 3, 4]]
    gamma3 = [
        [1, 2, 3]]  # to secret s3 only all 3 users together can gain access
    access_structures = [gamma1, gamma2, gamma3]

    dealer = Dealer(prime, n_participants, s_secrets, access_structures)

    dealer.random_id = (bytes([1]), bytes([2]), bytes([3]), bytes([4]))
    # dealer.choose_distinct_x()
    dealer.master_shares_x = [3, 4, 5, 6]

    """ TODO: use Dealer method to generate """
    # dealer.d = [[[1,3,4]],[[1,2,4],[2,3,4]],[[1,2,3]]]
    # assert_equal([1,3,4], dealer.get_d_polynomial_coeffs(0, 0))
    dealer.access_group_polynomial_coeffs()

    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()

    # assert_equal(dealer.B_values[0][0], [11, 37])

    obtained_pseudo = dealer.pseudo_shares[0][0]

    combined_secret_0 = dealer.combine_secret(0, 0, obtained_pseudo)

    assert_equal([7, 5, 3], dealer.s_secrets)

    assert_equal(combined_secret_0, s_secrets[0])


