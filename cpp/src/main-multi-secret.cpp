#include <iostream>
#include <vector>

using std::vector;
using std::cout;
using std::endl;
typedef unsigned char byte;

namespace Roy
{
    class Participant
    {
        int id;
        vector<byte> share;
        vector<byte> pseudoShare;

    public:
        Participant(int id_arg)
            : id{id_arg} // uniform initialization C++11
        {}

        ~Participant()
        {}

        int getId() const { return id; }

        friend std::ostream& operator<< (std::ostream& output, const Participant& P)
        {
            output << "Participant id: " << P.id << endl;
            return output;
        }
    };

    class AccessGroup
    {
        vector<byte> polynomialCoefficients;
        vector<Participant> participants;

    public:
        AccessGroup(vector<Participant> vP)
            : participants {vP}
        {}

        ~AccessGroup()
        {}

        int getParticipantsCount() const { return participants.size(); }
        const vector<Participant>& getParticipants() const { return participants; }

        friend std::ostream& operator<< (std::ostream& output, const AccessGroup& A)
        {
            output << "AccessGroup\n(" << endl;
            for (auto participant : A.participants)
                output << "\t" << participant;
            output << ")" << endl;
            return output;
        }
};
}

int main(void)
{
    Roy::Participant P1(6);
    Roy::Participant P2(13);
    cout << P1 << P2;

    Roy::AccessGroup A1({P1, P2}); // fully initialize member vector using uniform initialization
    cout << A1;

    cout << "A1 group has " << A1.getParticipantsCount() << " participants.\n";

    cout << "First participant of A1 is: " << A1.getParticipants()[0];

    return 0;
}
