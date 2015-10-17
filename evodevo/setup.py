from setuptools import setup

setup(name='evodevo',
      version='0.1',
      description='Model of robots undergoing evolution and development',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Science/Research'],
      url='https://github.com/KodoCoder/EvoDevo-Modeling',
      author='Joshua Hawthorne-Madell',
      author_email='jhawthorne13@gmail.com',
      license='BSD 3-Clause',
      packages=['evodevo'],
      # package_dir={'evodevo', 'io'},
      include_package_date=True,
      install_requires=[
          'more_itertools',
          'numpy'],
      tests_require=['pytest'])
