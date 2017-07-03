#!/usr/bin/env python3

import timeit
import multisecret.MultiSecretRoyAdhikari as RA
import multisecret.MultiSecretLinYeh as LY
import multisecret.MultiSecretHerranzRuizSaez as HRS

TEST_HRS = 1

if __name__ == "__main__":
    
    """ Measure time performance of multi-secret sharing algorithms """

    prime = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1
    # prime = 15487469

    # multi secret sharing parameters
    secrets = [7, 9, 41, 15002900, 313, 501]
    n_participants = 8

    # Hardcoded test configurations
    if n_participants == 8:
        access_structures = [[[1,2,3,4,5,6,7,8]],
                             [[1,2,3,4,5,6,7,8]],
                             [[1,2,3,4,5,6,7,8]],
                             [[1, 2, 3, 4, 5, 6, 7, 8]],
                             [[1, 2, 3, 4, 5, 6, 7, 8]],
                             [[1, 2, 3, 4, 5, 6, 7, 8]]
                             ]
    elif n_participants == 3:
        access_structures = [[[1,2,3]], [[1,2,3]], [[1,2,3]], [[1,2,3]], [[1,2,3]], [[1,2,3]]]
    else:
        raise

    #
    # Setup
    #

    #
    # Performance test
    #
    start = timeit.default_timer()
    #---#

    dealer = HRS.Dealer(prime, n_participants, secrets, access_structures)
    pseudo_shares = dealer.split_secret_keys()

    #---#
    end = timeit.default_timer()

    if not TEST_HRS:
        secret_num = 0
        group_num = 0
        combined = dealer.combine_secret(secret_num, group_num,
                                     pseudo_shares[secret_num][group_num])

    else:
        shares_for_secret_0 = []
        for user in range(1, n_participants+1):
            shares_for_secret_0.append( dealer.get_user_key_share(user)[0] )
        secret0 = dealer.combine_secret_key(0, shares_for_secret_0)


    print('Time for {} users and {} secrets with prime {}: {} seconds:'.format(
        n_participants, len(secrets), prime, end - start))
    
    # Combine first secret for its first access group

    #assert combined == secrets[secret_num]
    #print('Combined secret: ', combined)
    
