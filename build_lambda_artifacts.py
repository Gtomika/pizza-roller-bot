import shutil
import os


def build_lambda_zip(src_folder_name):
    shutil.make_archive(f'artifacts/{src_folder_name}', 'zip', f'src/{src_folder_name}')


if __name__ == '__main__':
    shutil.rmtree('artifacts', ignore_errors=True)
    os.mkdir('artifacts')
    build_lambda_zip('discord_interaction_lambda')
    build_lambda_zip('scheduled_lambda')

