from setuptools import setup, find_packages

setup(
    name='openu_scraper',
    packages=find_packages(),
    url='',
    version='1.0',
    license='LGPL',
    author='Omer',
    author_email='omerbenamram@gmail.com',
    description='a script to grab videos from open university',
    entry_points={
        'console_scripts': [
            'artistworks_downloader = main:main',
        ],
    },
    install_requires=['selenium', 'logbook', 'aiohttp', 'tqdm', 'pyvirtualdisplay', 'm3u8',
              'requests', 'retry', 'm3u8', 'capybara-py', 'beautifulsoup4', 'pytest']
)
