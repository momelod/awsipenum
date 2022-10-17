from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

install_requires = (here / 'requirements.txt').read_text(encoding='utf-8').splitlines()

setup(
    install_requires=install_requires,
    name='awsipenum',
    version='0.1',
    description='List your AWS public IPs',
    author='Steve Melo',
    author_email='momelod@gmail.com',
    url='https://github.com/momelod',
    py_modules=[
        'awsipenum',
        'ec2enum',
        'msg'
    ],
)
