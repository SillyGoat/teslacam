' Control project builds and publishing '

import argparse
import pathlib
import shutil
import subprocess
import sys

def _build(package_path):
    cmd_line = [
        sys.executable,
        '-m', 'build',
        '--wheel',
        str(package_path),
    ]
    # Build module requires shell=True
    subprocess.run(cmd_line, check=True, shell=True)

def _publish(package_path, repository_name):
    cmd_line = [
        sys.executable,
        '-m', 'twine',
        'upload',
        '--repository', repository_name,
        str(package_path / 'dist/*'),
    ]
    subprocess.run(cmd_line, check=True)

def _clean(package_path):
    shutil.rmtree(package_path / 'build', ignore_errors=True)
    shutil.rmtree(package_path / 'dist', ignore_errors=True)
    shutil.rmtree(package_path / f'{package_path.name}.egg-info', ignore_errors=True)

def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='Build distributables')
    parser.add_argument(
        '--publish',
        metavar='REPOSITORY_NAME',
        help='Publish distributables to specified repository'
    )
    parser.add_argument('--clean', action='store_true', help='Clean package path of distributables')
    args = parser.parse_args()

    package_path = pathlib.Path(__file__).parent
    if args.build:
        _build(package_path)

    if args.publish:
        _publish(package_path, args.publish)

    if args.clean:
        _clean(package_path)

if __name__ == '__main__':
    _main()
