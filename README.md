# How to Share a Secret?



# Implementation of multi-secret sharing algorithms

Imagine a situation where you want to secure vulnerable data and give access to it only to a specified group of people, e.g. board of directors of a company. The vulnerable secret can be codes to open a safe or to fire the ballistic missiles.

*Now imagine that the level of authority in group is varied. The president can open the safe, while at least 2 vice-presidents must gather together to open it.*

Now imagine you have 17 safes or 56 missiles. You can have 56 secret codes and split them 56 times to give each member a share. Now the directors have to remeber 56 different passwords.

**Here multi-secret sharing comes in handy. It allows the creator of the scheme to assign 'access structures' which can gain access to whole secret, or just a chosen part of it. Using multi-secret sharing all participants only have to remember one password.**

In this repo, different multi-secret sharing schemes will be implemented and compared.

# 1. "Multi-Use Multi-Secret Sharing Scheme for General Access Structure" - Roy, Adhikari
--- python prototype
--- C++ implementation with GUI
