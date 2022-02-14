from pathlib import Path
from typing import List

from setuptools import find_packages, setup

REQUIREMENTS_DIR = Path(__file__).parent / 'requirements'


def get_requirements(filename: str) -> List[str]:
    with open(REQUIREMENTS_DIR / filename) as file:
        return [ln.strip() for ln in file.readlines()]


essential_packages = get_requirements('essential.txt')
api_srvice_packages = get_requirements('docker/api.txt')
dashboard_srvice_packages = get_requirements('docker/dashboard.txt')
standalone_srvice_packages = get_requirements('docker/standalone.txt')
worker_srvice_packages = get_requirements('docker/worker.txt')

test_packages = get_requirements('test.txt')
train_packages = get_requirements('train.txt')

setup(
    name='zreader',
    version='0.1.0',
    license='Apache License 2.0',
    author='Alexander Shulga',
    author_email='alexandershulga.sh@gmail.com',
    python_requires='>=3.8',
    packages=find_packages(
        where='src',
        include=['zreader'],
    ),
    package_dir={'': 'src'},
    install_requires=[essential_packages],
    extras_require={
        'api': api_srvice_packages,
        'dashboard': dashboard_srvice_packages,
        'standalone': standalone_srvice_packages,
        'worker': worker_srvice_packages,
        "test": test_packages,
        "train": train_packages,
    },
    entry_points={
        'console_scripts': [
            'zreader = zreader.app.cli.zreadercli:cli',
        ],
    },
)
