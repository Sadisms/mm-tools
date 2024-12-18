from setuptools import setup, find_packages


def requires(filename: str):
    return open(filename).read().splitlines()


if __name__ == '__main__':
    setup(
        name='mm-tools',
        packages=find_packages(),
        install_requires=requires("requirements.txt"),
    )
