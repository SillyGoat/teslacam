' Setup script '
import setuptools

def setup():
    ' Setup routine '
    with open('README.md', 'r') as readme_file:
        long_description = readme_file.read()

    setuptools.setup(
        name='teslacam',
        version='1.0.0',
        author='SillyGoat',
        author_email='fake.me.now.and.forever@gmail.com',
        description='Consolidate and format Tesla vehicle camera video data',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/SillyGoat/teslacam',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        python_requires='>=3.8',
    )

setup()
