from setuptools import setup

version = open('VERSION').read()

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
)
