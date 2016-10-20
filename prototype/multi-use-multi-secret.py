# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

def is_prime(n):
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    f = 5
    while f <= r:
        print ('\t',f)
        if n%f == 0: return False
        if n%(f+2) == 0: return False
        f +=6
    return True

#def choose_prime(p_size):
    
    
import os # for OS random number generation

k_secrets = 3
s_secrets = [7, 313, 671] # s_i
n_participants = 2
access_structures = [(1,),(2,),(1,2)]

p_size = 2 # bytes

print(access_structures)

# 1. Dealer Phase
## I. Initialization stage
p = int.from_bytes(os.urandom(p_size), byteorder="big")
print(p)
while p <= n_participants or not is_prime(p): # p must be prime, greater than any of secrets and greater than n
    p = int.from_bytes(os.urandom(p_size), byteorder="big")
    print(p)

