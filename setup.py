from setuptools import setup, find_packages
setup(
    name='sdmo_parser',
    sdk_version='2.1.4',
    version='0.1.0',
    author='khismatullin_Vladimir',
    author_email='hismatullin.v@gmail.com',
    description='',
    license='PRIVATE',
    packages = find_packages('src'),
    package_dir={ '' : 'src' },
    zip_safe=False,
    install_requires=[
    ],
    entry_points = """
        [console_scripts]
        sdmo_parser = Application:main
        """
)
