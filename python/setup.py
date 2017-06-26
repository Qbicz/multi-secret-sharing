try:
    from setuptools import setup
    print("setuptools setup")
except ImportError:
    from distutils.core import setup
    print("distutils.core setup")
    
config = {
    'description': 'Multi secret sharing schemes - python prototype',
    'author': 'Filip Kubicz',
    'url': 'http://github.com/Qbicz/multi-secret-sharing',
    'download_url': 'where to download',
    'author_email': 'avenger.v14@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': [],
    'scripts': [],
    'name': 'multiSecret'
 }

setup(**config, install_requires=['PyQt5'])
 