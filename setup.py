from setuptools import setup

setup(
    name='buddhas-hand',
    version='0.1.0',
    description='A Python module for integrating with databases and caching systems.',
    author='Noraa Stoke',
    author_email='noraa.july.stoke@gmail.com',
    url='https://github.com/noraa-july-stoke/buddhas-hand',
    packages=['buddhas_hand'],
    install_requires=[
        'tortoise-orm==0.16.15',
        'aioredis==2.0.0',
        # other dependencies as required
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
