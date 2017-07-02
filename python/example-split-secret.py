#!/usr/bin/env python3

import multisecret.MultiSecretRoyAdhikari

if __name__ == "__main__":
    
    """ This example shows how to use high level secret splitting functionality """
    
    prime = 15487469

    # multi secret sharing parameters
    secrets = [15002900, 313, 501]
    n_participants = 3
    access_structures = [[[1,2,3]], [[1,2,3]], [[1,2,3]]]

    # initialize Roy-Adhikari secret sharing algorithm
    dealer = multisecret.MultiSecretRoyAdhikari.Dealer(prime, n_participants, secrets, access_structures)
    pseudo_shares = dealer.split_secrets()
    
    # Combine first secret for its first access group
    secret_num = 0
    group_num = 0
    combined = dealer.combine_secret(secret_num, group_num,
                                     pseudo_shares[secret_num][group_num])
    
    assert combined == secrets[secret_num]
    print('Combined secret: ', combined)
    
