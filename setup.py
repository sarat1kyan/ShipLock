"""
ShipLock Setup Configuration
Production-grade CLI tool for secure Docker distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = [
        'rich>=13.0.0',
        'click>=8.0.0',
        'pyyaml>=6.0',
        'cryptography>=41.0.0',
        'docker>=6.0.0',
        'netifaces>=0.11.0',
    ]

# Development requirements
dev_requirements = [
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
    'black>=23.0.0',
    'flake8>=6.0.0',
    'mypy>=1.5.0',
    'pre-commit>=3.3.0',
]

setup(
    name='shiplock',
    version='1.0.0',
    description='Secure Docker Product Distribution CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/shiplock',
    license='Commercial',
    
    packages=find_packages(exclude=['tests', 'docs']),
    
    install_requires=requirements,
    
    extras_require={
        'dev': dev_requirements,
    },
    
    entry_points={
        'console_scripts': [
            'shiplock=shiplock_cli:cli',
        ],
    },
    
    python_requires='>=3.8',
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Security',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
    ],
    
    keywords='docker distribution security licensing packaging',
    
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/shiplock/issues',
        'Source': 'https://github.com/yourusername/shiplock',
        'Documentation': 'https://shiplock.readthedocs.io',
    },
    
    include_package_data=True,
    
    zip_safe=False,
)
