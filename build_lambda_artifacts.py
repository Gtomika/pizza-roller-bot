import shutil
import os
import subprocess
import sys


def build_lambda_zip(src_folder_name):
    shutil.make_archive(f'artifacts/{src_folder_name}', 'zip', f'src/{src_folder_name}')


python_layer_required_path = 'python/lib/python3.12/site-packages'


def install_layer_dependencies():
    install_folder = f'installed_dependencies/{python_layer_required_path}'
    os.makedirs(install_folder, exist_ok=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-lambda.txt",
                    "--target", install_folder], check=True)


def build_layer_zip():
    shutil.make_archive('artifacts/lambda_layer', 'zip', 'installed_dependencies')


if __name__ == '__main__':
    shutil.rmtree('artifacts', ignore_errors=True)
    shutil.rmtree('installed_dependencies', ignore_errors=True)
    os.mkdir('artifacts')

    install_layer_dependencies()
    build_layer_zip()
    build_lambda_zip('discord_interaction_lambda')
    build_lambda_zip('scheduled_lambda')

