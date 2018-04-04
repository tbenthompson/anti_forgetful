from setuptools import setup

setup(
    packages = ['aws_launcher'],

    install_requires = ['boto3'],
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'awslaunch = aws_launcher.launch:main',
            'createami = aws_launcher.create_ami:main',
            'terminate_all_instances = aws_launcher.terminate_all_instances:main'
        ]
    }
)
