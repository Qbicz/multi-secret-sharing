# Prototype of Multi-secret sharing scheme by Roy & Adhikari
# Filip Kubicz 2016

from multisecret.Dealer import Dealer

def main():
    # large prime from NIST P-256 elliptic curve 
    p256 = 2**256 - 2**224 + 2**192 + 2**96 - 1

    # multi secret sharing parameters
    s_secrets = [7, 313, 671] # s_i
    n_participants = 3
    # access structure: to which secret what group has access
    # Gamma(s_i) = [A1, A2, ... Al], Aq = (P1, P2, Pm), q=1,2...l
    A1 = (1,3)
    # gamma1 is a group of users authorized to reconstruct s1
    gamma1 = [A1]
    gamma2 = [(1,2), (2,3)] # A1, A2 implicitly
    gamma3 = [(1,2,3)] # to secret s3 only all 3 users together can gain access
    access_structures = [gamma1, gamma2, gamma3]
    # TODO: in GUI choosing access structures on a matrix

    # Create a Dealer
    
    """ TODO: test with 4099 prime """
    dealer = Dealer(p256, n_participants, s_secrets, access_structures)

    # test hash function - it should be repeatable for the same Dealer object
    dealer.hash(b'BYTESEQUENCE') # careful, b'' syntax gives ASCII bytes string
    dealer.hash(b'BYTESEQUENCE')

    dealer.provide_id() # a list of IDs stored internally
    dealer.choose_distinct_x()

    dealer.access_group_polynomial_coeffs()

    # indexes begin at 0
    #user_num = 1
    #secret_num = 2
    #group_num = 2
    #share133 = dealer.pseudo_share_participant(user_num, secret_num, group_num)
    #print('Pseudo share length = ', len(share133))
    
    dealer.compute_all_pseudo_shares()

    #dealer.print_list_of_hex(dealer.d, 'd polynomial coeffs') # d coeffs are indexed from 1
    
    
    # TODO: talk with professor about research meaning of the schemes

if __name__ == "__main__":
    main()
