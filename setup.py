from setuptools import setup, find_packages

setup(
    install_requires=[
        'boto3 >= 1.24.89',
        'botocore >= 1.27.89'
    ],
    name='awsipenum',
    version='0.1',
    description='List your AWS public IPs',
    author='Steve Melo',
    author_email='momelod@gmail.com',
    url='https://github.com/momelod/awsipenum',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'awsipenum = awsipenum:main'
        ]
    }
)
