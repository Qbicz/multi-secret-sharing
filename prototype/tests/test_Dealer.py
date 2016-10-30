# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from nose.tools import *
from multi_secret.Dealer import Dealer

# TODO: test if hash is the same for the same Dealer object and different among separate objects with random AES-CTR nonce

def test_hash():
    #assert_equal(lexicon.scan("north"), [('direction', 'north')])
    #result = lexicon.scan("north south east")
    #assert_equal(result, [('direction', 'north'),
    #                      ('direction', 'south'),
    #                      ('direction', 'east')])
    