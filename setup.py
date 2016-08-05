from setuptools import setup, find_packages


setup(
    name='mp3organizer',
    version='1.0',
    packages=find_packages(),
    install_requires=['logbook', 'lxml', 'PyQt5', 'mutagen', 'pytest']
)
