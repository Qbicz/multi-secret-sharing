# Functions common for implemented multi-secret sharing algorithms
# Filip Kubicz 2016-2017

# import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
# import AES-CTR
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
from math import log2, floor
from multisecret.primality import is_probable_prime
from multisecret.byteHelper import inverse_modulo_p
import copy # to have deepcopy, independent copy of a list


# common functions, extracted from class Dealer


def user_count_from_access_structure(access_structure):
    max_user_count = 0
    for secret in access_structure:
        for group in secret:
            if max(group) > max_user_count:
                max_user_count = max(group)
    print('only returns maximal user number, not a total number of users.\n'
          'But the user over this number is irrelevant.\n'
          'TODO: reconstruct for subsets of shares - will solve the problem')
    return max_user_count


def modulo_p(prime, number):
    """ works for:
    - int type
    - bytes type
    """
    return_bytes = False

    # if input is bytes, convert it to int, but return bytes object
    if (isinstance(number, bytes)):
        return_bytes = True
        number = int.from_bytes(number, byteorder='big')

    if (number >= prime):
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


def list_of_random_in_modulo_p(listlen, hashlen, prime):
    """helper function returning list of random numbers less than p prime"""
    randoms = []
    bytelen_of_randoms_generated = hashlen  # TODO: write bytelenOfInt() method in byteHelper

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
