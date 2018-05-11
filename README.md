# How to Share a Secret?

![Traditional way of sharing a secret](https://raw.githubusercontent.com/Qbicz/multi-secret-sharing/master/docs/Sharing-Secrets.jpg)

**multi-secret-sharing** is a tool for splitting multiple secrets among multiple stakeholders.

The parts, or secret shares are saved as JSON files and can be later distributed to several people or backed up on separate disks and online storage facilities.

Implemented and ready-to-use multi secrets sharing schemes are:
- [Roy-Adhikari](https://arxiv.org/abs/1409.0089)
- [Lin-Yeh](https://pdfs.semanticscholar.org/0ebb/e71b8ba333b3a5431a489c761915de59ba00.pdf)
- [Herranz-Ruiz-Saez](http://www.sciencedirect.com/science/article/pii/S0020019013001373).

If you want to secure a huge file, it might be better to encrypt it using block cipher, e.g. AES and only split the password with secret sharing. That's what Herranz-Ruiz-Saez actually does.

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

# Building executables for release
To package application under Windows & Linux, use latest development version of PyInstaller.
```bash
pip3 install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
```

Under Linux:
```bash
pyinstaller --windowed --onefile ui_controller.py
```
If under Windows Qt5 DLL's are not found by the PyInstaller script, explicitly point PyQt5 directory, e.g.:
```bash
pyinstaller --windowed --onefile --path C:\Python35\Lib\site-packages\PyQt5\Qt\bin ui_controller.py
```


# Continuous Integration with Jenkins
TBD.
https://www.blazemeter.com/blog/how-start-working-github-plugin-jenkins



# Background and motivation

Imagine a situation where you want to secure vulnerable data and give access to it only to a specified group of people, e.g. board of directors of a company. The vulnerable secret can be codes to open a safe or to fire the ballistic missiles.

*Now imagine that the level of authority in group is varied. The president can open the safe, while at least 2 vice-presidents must gather together to open it.*

Now imagine you have 17 safes or 56 missiles. You can have 56 secret codes and split them 56 times to give each member a share. Now the directors have to generate and store 56 different passwords.

**Here multi-secret sharing comes in handy. Using multi-secret sharing all participants only have to remember one password. It allows the creator of the scheme to assign 'access structures' specifying who can gain access to whole all secrets or just a chosen subset of secrets. **

[Secret-sharing](https://en.wikipedia.org/wiki/Secret_sharing)
[Multi-secret sharing](https://en.wikipedia.org/wiki/Secret_sharing#Multi-secret_and_space_efficient_(batched)_secret_sharing)


