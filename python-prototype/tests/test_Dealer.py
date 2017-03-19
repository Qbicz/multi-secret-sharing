# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from multisecret.Dealer import Dealer
from numpy import array, array_equal

# TODO: test if hash is the same for the same Dealer object and different among separate objects with random AES-CTR nonce

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


def test_init():
    """ check exception handling if params are faulty """
    
    # test for proper exception: p not prime
    with assert_raises(ValueError):
        dealer = Dealer(24, n_participants, s_secrets, access_structures)
    
    # test for proper exception: too little participants
    with assert_raises(ValueError):
        dealer = Dealer(p256, 1, s_secrets, access_structures)


def test_hash():
    """ set up Dealer object and check hash repeatability """
    
    # Create a Dealer
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # test hash function - it should be repeatable for the same Dealer object
    hash1 = dealer.hash(b'BYTESEQUENCE')
    hash2 = dealer.hash(b'BYTESEQUENCE')
    assert_equal(hash1, hash2)
    
def test_hash_different():
    """ different instances of Dealer should have different hash results as the have separate random AES nonces"""
    
    # Create a Dealer
    dealer1 = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer2 = Dealer(p256, n_participants, s_secrets, access_structures)
    
    # test hash function - it should be repeatable for the same Dealer object
    hash1 = dealer1.hash(b'BYTESEQUENCE')
    hash2 = dealer2.hash(b'BYTESEQUENCE')
    assert_not_equal(hash1, hash2)


def test_modulo_p():
    p = 1009
    dealer = Dealer(p, n_participants, s_secrets, access_structures)
    
    assert_equal(dealer.modulo_p(2011), 1002)
    

def test_list_of_random_in_modulo_p():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    
    n = 5
    randomList = dealer.list_of_random_in_modulo_p(n)
    dealer.print_list_of_hex(randomList, 'test randomList')
    # check the length of the list
    assert_equal(len(randomList), n)
    # check the type of object in the list
    assert_equal(isinstance(randomList[0], bytes), True)
    
    #dealer_short = Dealer(1009, 2, [13], [[(1,2), ()]])
    #randomListShort = dealer_short.list_of_random_in_modulo_p(n)
    #dealer_short.print_list_of_hex(randomListShort, 'test randomListShort')
    #assert_equal(len(randomListShort[0]), 1)


def test_provide_id():
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    
    id_list = dealer.provide_id()
    # check the length of the list
    assert_equal(len(id_list), n_participants)
    # check the type of object in the list
    assert_equal(isinstance(id_list[0], bytes), True)
    

def test_take_first_bits():

    dealer = Dealer(7, 2, [5,6], [[(1,2)],[(1)]] )
    
    input = bytes([0xDE, 0xAD, 0xBE, 0xEF]) # len in bytes
    print('test input: ', input.hex())
    
    # test correct exception raised
    with assert_raises(ValueError):
        dealer.take_first_bits(input, 65) # len in bits
    
    first_bits = dealer.take_first_bits(input, 12)
    print('test first bits: ', first_bits.hex())
    assert_equal(first_bits, bytes([0xDE, 0xA0]))
    
    modulo_bits = dealer.take_first_bits(input, 16)
    assert_equal(modulo_bits, bytes([0xDE, 0xAD]))
    
    
def test_access_group_polynomial_coeffs():
    
    A1 = (1,3)
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [A1]
    gamma2 = [(1,2), (2,3)] # A1, A2 implicitly
    gamma3 = [(1,2,3)] # to secret s3 only all 3 users together can gain access
    access_structures = [gamma1, gamma2, gamma3]

    # Create a Dealer
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    
    # compute d coeffs
    dealer.access_group_polynomial_coeffs()
    
    #dealer.print_list_of_hex(dealer.d[1][1], 'd-1-1')
    # test output
    assert_equal(len(dealer.d), 3)
    assert_equal(len(dealer.d[0]), 1)
    assert_equal(len(dealer.d[1][1]), 2)
    assert_equal(len(dealer.d[2][0]), 3)
    
    # Test index out of range
    with assert_raises(IndexError):
        print('Test', dealer.print_list_of_hex(dealer.d[2][1], 'd-2-1'))
    
    
def test_get_d_polynomial_coeffs():
    
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.access_group_polynomial_coeffs()
    
    coeff1 = dealer.get_d_polynomial_coeffs(secret=0, group=0)[1]
    coeff2 = dealer.d[0][0][1]
    
    assert_equal(coeff1, coeff2)
    

def test_f_polynomial_compute():
    
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)
    dealer.access_group_polynomial_coeffs()
    # override coeffs
    dealer.d[0][0] = [bytes([0x05]), bytes([0x07])]
    
    value = dealer.f_polynomial_compute(bytes([0x01]), secret=0, group=0)
    assert_equal(value, 12+s_secrets[0])
    
    value = dealer.f_polynomial_compute(bytes([0x02]), secret=0, group=0)
    assert_equal(value, 38+s_secrets[0])
    

def test_combine_secret_2_participants():
    pass

def test_combine_secret_3_participants():
    """ Acceptance test """
    
    s1 = 4
    p = 7
    # access group
    A = (1,2,3)
    # user IDs
    IDs = [1,2,3]
    # polynomial coeffs
    d1 = 2
    d2 = 1
    
    dealer = Dealer(p, len(A), [s1], [[A]])
    assert_equal(dealer.n, 3)
    
    # set IDs, don't generate random
    byte_IDs = []
    for ID in IDs:
        byte_IDs.append( bytes([ID]) )
    print(byte_IDs)
    dealer.random_id = byte_IDs
    
    # set polynomial coeffs
    dealer.d = [[]]
    dealer.d[0].append([d1, d2])
    assert_equal([2,1], dealer.get_d_polynomial_coeffs(0, 0))
    
    # set x-shares for pseudo share generation only
    dealer.x = [3,4,5]
    
    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()
    
    print(dealer.B_values)
    assert_equal(True, array_equal([[[0,0,5,5]]], dealer.B_values))
    
    obtained_pseudo_shares = dealer.pseudo_shares[0][0][1:] # skip 0th element (user P0, we have P1, P2, P3)
    print(obtained_pseudo_shares)
    combined_secret = dealer.combine_secret(0, 0, obtained_pseudo_shares)
    
    assert_equal(combined_secret, s1)
    
