# Functions common for implemented multi-secret sharing algorithms
# Filip Kubicz 2016-2017

from os import urandom
from math import log2, floor

# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
# import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import multisecret.byteHelper as bytehelper


# --- common functions, extracted from class Dealer ---
def user_count_from_access_structure(access_structure):
    """ Returns maximal user number found in access structure,
        which does not have to be equal to a total number of users.
        The users over this returned number are irrelevant during reconstruction.
        TODO: reconstruct for subsets of shares to solve the problem
    """
    max_user_count = 0
    for secret in access_structure:
        for group in secret:
            if max(group) > max_user_count:
                max_user_count = max(group)
    return max_user_count


def hash(message, hash_len, aes_nonce):
    """A collision resistant hash function h with variable output length:
    - option 1: use SHA-3 Keccak (variable length digest)
    - option 2: use BLAKE2 : variable length digest (available
        at "cryptography" library - but to bytes, not bits resolution)
    - option 3 (chosen, implemented her): use the first [log2(p)]+1 bits
                of AES-CTR(SHA256(m))"""

    # SHA256 of message
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(message)
    hashed_message = digest.finalize()

    # AES-CTR of the hash
    aes_key = hashed_message
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    input = b'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
    #print(input.hex())
    ciphertext = encryptor.update(input) + encryptor.finalize()

    # take demanded numer of bits
    varlen_hash = bytehelper.take_first_bits(ciphertext, hash_len)
    #print('Hash is ', varlen_hash.hex())
    return varlen_hash


def modulo_p(prime, number):
    """ modulo which works for:
    - int type
    - bytes type
    """
    return_bytes = False

    # if input is bytes, convert it to int, but return bytes object
    if (isinstance(number, bytes)):
        return_bytes = True
        number = int.from_bytes(number, byteorder='big')

    if (number >= prime or number < 0):
        number = number % prime

    if (return_bytes):
        if number == 0:
            byte_len = 1
        else:
            bit_len = floor(log2(number)) + 1
            byte_len = bit_len // 8 + 1
        # print('bit_len, byte_len', bit_len, byte_len)
        modulo_number = number.to_bytes(byte_len, byteorder='big')
    else:
        modulo_number = number

    return modulo_number


def list_of_random_in_modulo_p(listlen, bytelen, prime):
    """helper function returning list of random numbers less than p prime"""
    randoms = []
    bytelen_of_randoms_generated = bytelen  # TODO: write bytelenOfInt() method in byteHelper

    for i in range(listlen):
        generated = urandom(bytelen_of_randoms_generated)
        randoms.append(modulo_p(prime, generated))

    return randoms  # TODO: yield generator for bigger problem sizes


def print_list_of_hex(list_to_print, description):
    """helper to print list of bytes objects with string description"""
    for i in range(len(list_to_print)):
        print('%s%d = %s' % (description, i, list_to_print[i].hex()))


def provide_id(participants_num, hash_len, prime):
    """for each participant provide ID in p modulo field"""
    random_id = list_of_random_in_modulo_p(participants_num,
                                                  hash_len,
                                                  prime)
    print_list_of_hex(random_id, 'Participant ID ')
    return random_id


def shamir_polynomial_compute(argument, coeffs, secret_value, prime):
    """ compute f_q(x) for q-th access group in access structure """

    poly_value = 0
    if isinstance(argument, bytes):
        argument = int.from_bytes(argument, byteorder='big')

    for degree, coeff in enumerate(coeffs):
        if isinstance(coeff, bytes):
            coeff = int.from_bytes(coeff, byteorder='big')

        print('+ %d * %d^%d' % (coeff, argument, degree + 1))
        poly_value += coeff * argument ** (degree + 1)

    poly_value += secret_value
    print('+ secret ({})'.format(secret_value))
    poly_value = modulo_p(prime, poly_value)
    # print('poly_value', poly_value)
    return poly_value
