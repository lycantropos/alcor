from setuptools import (setup,
                        find_packages)

setup(name='alcor',
      packages=find_packages(),
      version='0.0.0',
      description='Library for astronomical researches.',
      author='Georgy Skorobogatov, '
             'Azat Ibrakov',
      author_email='skorobogatov@phystech.edu, '
                   'azatibrakov@gmail.com',
      url='https://github.com/lycantropos/alcor',
      download_url='https://github.com/lycantropos/alcor/archive/master.tar.gz',
      keywords=['astronomy'],
      install_requires=[
          'cassandra-driver>=3.9.0',  # working with Cassandra
          'PyYAML>=3.12.0',  # settings loading
      ])
