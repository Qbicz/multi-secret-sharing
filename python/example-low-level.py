#!/usr/bin/env python3

import multisecret.MultiSecretRoyAdhikari
import multisecret.MultiSecretCommon as common

def main():
    """ This example shows low-level functions for splitting
        and combining secrets with multi-secret sharing
        scheme by Roy & Adhikari. """
        
    # large prime from NIST P-256 elliptic curve 
    p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

    # multi secret sharing parameters
    s_secrets = [7, 313, 671] # s_i
    n_participants = 3
    # access structure: to which secret what group has access
    # Gamma(s_i) = [A1, A2, ... Al], Aq = (P1, P2, Pm), q=1,2...l
    A1 = [1,3]
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [A1]
    gamma2 = [[1,2], [2,3]] # A1, A2 implicitly
    gamma3 = [[1,2,3]] # to secret s3 only all 3 users together can gain access
    access_structures = [gamma1, gamma2, gamma3]
    # TODO: in GUI choosing access structures on a matrix

    # Create a Dealer
    dealer = multisecret.MultiSecretRoyAdhikari.Dealer(p256, n_participants, s_secrets, access_structures)

    dealer.random_id = common.provide_id(n_participants,
                                         dealer.hash_len,
                                         dealer.p) # a list of IDs stored internally
    dealer.master_shares_x = dealer.choose_distinct_master_shares_x()

    dealer.access_group_polynomial_coeffs()
    dealer.compute_all_pseudo_shares()
    dealer.compute_all_public_shares_M()
    
    print('obtained shares', dealer.pseudo_shares[0][0])   
    obtained_shares = []
    for share in dealer.pseudo_shares[0][0]:
        obtained_shares.append(int.from_bytes(share, byteorder='big'))
    
    print('obtained shares', obtained_shares) 
    combined_secret = dealer.combine_secret(0, 0, obtained_shares)
    print('Combined secret s1', combined_secret)



if __name__ == "__main__":
    main()
