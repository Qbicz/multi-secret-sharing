from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from multisecret.MultiSecretRoyAdhikari import Dealer
import multisecret.MultiSecretCommon as common

""" Declare basic params used to initialize Dealer in test cases """
# large prime from NIST P-256 elliptic curve
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1
# multi secret sharing parameters
s_secrets = [7, 313, 671] # s_i
n_participants = 3
# access structure: to which secret what group has access
# Gamma(s_i) = [A1, A2, ... Al], Aq = (P1, P2, Pm), q=1,2...l
# gamma1 is a group of users authorized to reconstruct s1
gamma1 = [(1,3)]
gamma2 = [(1,2), (2,3)] # A1, A2 implicitly
gamma3 = [(1,2,3)] # to secret s3 only all 3 users together can gain access
access_structures = [gamma1, gamma2, gamma3]


def test_modulo_p():
    p = 1009
    dealer = Dealer(p, n_participants, s_secrets, access_structures)
    assert_equal(common.modulo_p(p, 2011), 1002)


def test_list_of_random_in_modulo_p():
    """ test: list_of_random_in_modulo_p """
    dealer = Dealer(4099, n_participants, s_secrets, access_structures)

    n = 5
    randomList = common.list_of_random_in_modulo_p(n,
                                                   dealer.hash_len,
                                                   dealer.p)
    common.print_list_of_hex(randomList, 'test randomList')
    # check the length of the list
    assert_equal(len(randomList), n)
    # check the type of object in the list
    assert_equal(isinstance(randomList[0], bytes), True)

    # dealer_short = Dealer(1009, 2, [13], [[(1,2), ()]])
    # randomListShort = dealer_short.list_of_random_in_modulo_p(n)
    # dealer_short.print_list_of_hex(randomListShort, 'test randomListShort')
    # assert_equal(len(randomListShort[0]), 1)


def test_provide_id():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    id_list = common.provide_id(n_participants, dealer.hash_len, dealer.p)
    # check the length of the list
    assert_equal(len(id_list), n_participants)
    # check the type of object in the list
    assert_equal(isinstance(id_list[0], bytes), True)


def test_shamir_polynomial_compute():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.access_group_polynomial_coeffs()
    # override coeffs
    dealer.d[0][0] = [bytes([0x05]), bytes([0x07])]

    coeffs = dealer.get_d_polynomial_coeffs(0, 0)
    secret_value = dealer.s_secrets[0]

    value = common.shamir_polynomial_compute(bytes([0x01]), coeffs,
                                             secret_value, dealer.p)
    assert_equal(value, 12 + s_secrets[0])

    value = common.shamir_polynomial_compute(bytes([0x02]), coeffs,
                                             secret_value, dealer.p)
    assert_equal(value, 38 + s_secrets[0])
