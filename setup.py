from distutils.core import setup

setup(name='Distutils',
      version='0.0.1',
      description='Python Raytracer',
      author='Jack Stinchcombe',
      author_email='stinchjack@gmail.com',
      packages=['raytracer', 'raytracer.devutil', 'raytracer.unit_tests'],
     )