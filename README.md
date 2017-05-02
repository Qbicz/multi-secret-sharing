# How to Share a Secret?

![Traditional way of sharing a secret](https://raw.githubusercontent.com/Qbicz/multi-secret-sharing/master/docs/Sharing-Secrets.jpg)

**multi-secret-sharing** is a tool for splitting secret data into parts.
The parts, or secret shares can be later distributed to several people or backed up on separate disks and online storage facilities.

If you want to secure a huge file, it might be better to encrypt it using block cipher, e.g. AES and only split the password with secret sharing.

**WARNING. This project is under development and is not suitable for vulnerable tasks. If you want to encrypt your disk or some important data, better use a tested program, such as [VeraCrypt](https://sourceforge.net/projects/veracrypt/).**

# Download
You can find binary executables in [releases section](https://github.com/Qbicz/multi-secret-sharing/releases).


# Run example
To run a Python 3.5 prototype, please install [cryptography](https://pypi.python.org/pypi/cryptography) module.
```bash
pip3 install cryptography
```
Run an example
```bash
cd multi-secret-sharing/python
python3 example-split-secret.py
```

# Run GUI
To run GUI application, install PyQt5 and jsonpickle:
```bash
pip3 install PyQt5
pip3 install jsonpickle
```
Run GUI application:
```
python3 ui_controller.py
```

# Run tests
To run tests, you need nosetests unit testing library for Python3:
```bash
sudo apt install python3-nose
```
Run tests:
```bash
nosetests3
```

# Implementation of multi-secret sharing algorithms

Imagine a situation where you want to secure vulnerable data and give access to it only to a specified group of people, e.g. board of directors of a company. The vulnerable secret can be codes to open a safe or to fire the ballistic missiles.

*Now imagine that the level of authority in group is varied. The president can open the safe, while at least 2 vice-presidents must gather together to open it.*

Now imagine you have 17 safes or 56 missiles. You can have 56 secret codes and split them 56 times to give each member a share. Now the directors have to remeber 56 different passwords.

**Here multi-secret sharing comes in handy. It allows the creator of the scheme to assign 'access structures' which can gain access to whole secret, or just a chosen part of it. Using multi-secret sharing all participants only have to remember one password.**

In this repo, different multi-secret sharing schemes will be implemented and compared.

- Algorithm 1 based on "Multi-Use Multi-Secret Sharing Scheme for General Access Structure" by Roy & Adhikari


# Continuous Integration with Jenkins
TBD.
https://www.blazemeter.com/blog/how-start-working-github-plugin-jenkins
