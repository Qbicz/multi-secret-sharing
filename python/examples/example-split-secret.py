#!/usr/bin/env python3

from multisecret.Dealer import Dealer
from multisecret.byteHelper import inverse_modulo_p

if __name__ == "__main__":
    
    """ This example shows how to use high level secret splitting functionality """
    
    prime = 15487469

    # multi secret sharing parameters
    secrets = [15002900, 313, 501]
    n_participants = 3
    access_structures = [[[1,2,3]], [[1,2,3]], [[1,2,3]]]
    
    dealer = Dealer(prime, n_participants, secrets, access_structures)
    pseudo_shares = dealer.split_secrets()
    
    # Combine first secret for its first access group
    secret_num = 0
    group_num = 0
    combined = dealer.combine_secret(secret_num, group_num, pseudo_shares[0][0])
    
    assert combined == secrets[0]
    print('Combined secret: ', combined)
    
