# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from Dealer import Dealer

# large prime from NIST P-256 elliptic curve 
p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

# multi secret sharing parameters
s_secrets = [7, 313, 671] # s_i
n_participants = 3
access_structure = [(1,),(2,),(1,2)]

d = Dealer(p256, n_participants, s_secrets, access_structure)
# test hash function - it should be repeatable for the same Dealer object
d.hash(b'BYTESEQUENCE', 26) # careful, b'' syntax gives ASCII bytes string
d.hash(b'BYTESEQUENCE', 26)

d.provide_id()
