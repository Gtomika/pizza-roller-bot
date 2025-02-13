import shutil
import os
import subprocess
import sys


# if dependencies are not changes, it's useful to set this as false.
skip_layer_building = bool(int(os.getenv('SKIP_LAYER_BUILDING')))


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
    if not os.path.exists('artifacts'):
        os.mkdir('artifacts')

    if not skip_layer_building:
        print('Building lambda layer...')
        if os.path.exists('installed_dependencies'):
            shutil.rmtree('installed_dependencies', ignore_errors=True)
        if os.path.exists('artifacts/lambda_layer.zip'):
            os.remove('artifacts/lambda_layer.zip')
        install_layer_dependencies()
        build_layer_zip()
        print('Lambda layer ZIP is created.')
    else:
        print('Layer building is skipped.')

    if os.path.exists('artifacts/discord_interaction_lambda.zip'):
        os.remove('artifacts/discord_interaction_lambda.zip')
    build_lambda_zip('discord_interaction_lambda')
    print('Discord interaction lambda ZIP is created.')

    if os.path.exists('artifacts/scheduled_lambda.zip'):
        os.remove('artifacts/scheduled_lambda.zip')
    build_lambda_zip('scheduled_lambda')
    print('Scheduled lambda ZIP is created.')

