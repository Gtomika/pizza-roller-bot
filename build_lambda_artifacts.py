import shutil
import os
import subprocess
import sys


def build_lambda_zip(src_folder_name):
    shutil.make_archive(f'artifacts/{src_folder_name}', 'zip', f'src/{src_folder_name}')


def build_layer_zip(layer_contents_folder):
    shutil.make_archive('artifacts/lambda_layer', 'zip', f'artifacts/{layer_contents_folder}')


def install_layer_dependencies(layer_contents_folder):
    install_folder = f'artifacts/{layer_contents_folder}'
    os.mkdir(install_folder)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-lambda.txt",
                    "--target", install_folder], check=True)


if __name__ == '__main__':
    shutil.rmtree('artifacts', ignore_errors=True)
    os.mkdir('artifacts')

    install_layer_dependencies('layer_contents')
    build_layer_zip('layer_contents')
    build_lambda_zip('discord_interaction_lambda')
    build_lambda_zip('scheduled_lambda')

