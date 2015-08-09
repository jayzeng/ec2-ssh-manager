import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('ec2/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

description = 'AWS EC2 SSH manager. You no longer need to memoize host name or ip, ssh with auto-completion.'


setup(
        name='ec2-ssh-manager',
        author='Jay Zeng',
        author_email='jayzeng[at]jay-zeng.com',
        version=version,
        license='LICENSE.txt',
        url='https://github.com/jayzeng/ec2-ssh-manager',
        packages=find_packages(),
        description=description,
        long_description=open('README.rst').read(),
        install_requires=[
            'boto >= 2.38.0',
            'prompt-toolkit >= 0.46',
            'netaddr >= 0.7.15',
            ],
        entry_points='''
            [console_scripts]
            ec2-ssh-manager=ec2.ssh:cli
        ''',
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Unix',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: AWS',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        )
