# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from Dealer import Dealer

# large prime from NIST P-256 elliptic curve 
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

# multi secret sharing parameters
s_secrets = [7, 313, 671] # s_i
n_participants = 3
# access structure: to which secret what group has access
# Gamma(s_i) = [A1, A2, ... Al], Aq = (P1, P2, Pm), q=1,2...l
access_structure = [(1,2),(2,3),(1,2,3)]

dealer = Dealer(p256, n_participants, s_secrets, access_structure)
# test hash function - it should be repeatable for the same Dealer object
dealer.hash(b'BYTESEQUENCE') # careful, b'' syntax gives ASCII bytes string
dealer.hash(b'BYTESEQUENCE')

dealer.provide_id() # a list of IDs stored internally
dealer.choose_distinct_x()

dealer.access_group_polynomial_coeffs()

user_num = 1
secret_num = 3
group_num = 3
share133 = dealer.pseudo_share(user_num, secret_num, group_num)
print('Pseudo share for user 1, secret 3, group 3 =', share133.hex())
print('Pseudo share length = ', len(share133))
