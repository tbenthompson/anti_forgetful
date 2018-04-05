from setuptools import setup

setup(
    packages = ['aws_launcher'],

    install_requires = ['boto3'],
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'awslaunch = aws_launcher.launch:main',
            'awsterminate = aws_launcher.terminate:main'
        ]
    },

    name = 'aws_launcher',
    version = '18.04.05',
    description = '',
)
