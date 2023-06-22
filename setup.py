from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='mm-tools',
        packages=find_packages(),
        install_requires=[
            'aiosqlite',
        ]
    )