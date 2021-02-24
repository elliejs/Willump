from setuptools import setup

__version__ = '1.0.0'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Pix',
    version=__version__,
    author='Eleanor Juno Silver',
    author_email='elliejs@zork.pw',
    license='MIT',
    url='https://github.com/elliejs/Pix/',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=['Pix'],
    install_requires=[
        'aiohttp',
        'psutil'
    ],
    project_urls={
        'Source': 'https://github.com/elliejs/Pix/'
    }
)
