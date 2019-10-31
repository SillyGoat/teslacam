' Setup script '
import contextlib
import os
import setuptools
import shutil
import subprocess

def cleanup():
    ' cleanup routine '
    package_path = os.path.dirname(os.path.realpath(__file__))
    shutil.rmtree(os.path.join(package_path, 'build'), ignore_errors=True)
    shutil.rmtree(os.path.join(package_path, 'dist'), ignore_errors=True)
    shutil.rmtree(
        os.path.join(
            package_path,
            f'{os.path.basename(package_path)}.egg-info'
        ),
        ignore_errors=True
    )

class Upload(setuptools.Command):
    ' Upload distribution '
    description = 'upload local distribution'
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        ' upload routine '
        cmd = [
            'py',
            '-m', 'twine',
            'upload', 'dist/*',
        ]
        subprocess.check_call(cmd)

@contextlib.contextmanager
def setup():
    ' Setup routine '
    with open('README.md', 'r') as readme_file:
        long_description = readme_file.read()

    try:
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
            cmdclass={
                'upload': Upload,
            },
        )
        yield
    finally:
        cleanup()

def main():
    ' main entry point '
    with setup():
        pass

main()
