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
        {
            id = id_arg;
        }

        friend std::ostream& operator<< (std::ostream& output, const Participant& P)
        {
            output << "Participant id: " << P.id << endl;
            return output;
        }
    };

    class AccessGroup
    {
    public:
        vector<byte> polynomialCoefficients;
        vector<Participant> participants;

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
    Roy::Participant P1(7);
    Roy::Participant P2(13);
    cout << P2;

    vector<Roy::Participant> participants =
    {   P1, P2};
    Roy::AccessGroup A1;
    A1.participants = participants;
    cout << A1;

    return 0;
}
