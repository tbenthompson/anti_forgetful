from setuptools import setup

version = open('VERSION').read()

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md').read()

setup(
    packages = ['anti_forgetful'],

    install_requires = ['boto3'],
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'rememberlaunch = anti_forgetful.launch:main',
            'awsterminate = anti_forgetful.terminate:main'
        ]
    },

    name = 'anti_forgetful',
    version = version,
    description = '',
    long_description = description,

    url = 'https://github.com/tbenthompson/anti_forgetful',
    author = 'T. Ben Thompson',
    author_email = 't.ben.thompson@gmail.com',
    license = 'MIT',
    platforms = ['any']
)
