from setuptools import setup, find_packages

with open('README.md', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name='awsipenum',
    version='0.1.0',
    description='List your AWS public IPs',
    author='Steve Melo',
    author_email='momelod@gmail.com',
    url='https://github.com/momelod/awsipenum',
    install_requires=['boto3'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'awsipenum=awsipenum.cli:main',
        ]
    }
)
