from setuptools import setup

setup(
    name='awsipenum',
    version='0.1',
    description='List your AWS public IPs',
    author='Steve Melo',
    author_email='momelod@gmail.com',
    url='https://github.com/momelod',
    py_modules=[
        'main',
        'ec2enum',
        'msg'
    ],
)
