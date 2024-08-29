import logging
import paramiko


async def get_file(file_name, message):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('185.13.44.216', username='mazazyrik', password='Alekodancer1')
    logging.info('ssh connected')
    sftp = ssh.open_sftp()
    remote_file_path = f'/home/mazazyrik/dev/speechai_web/web/uploaded_files/{file_name}'
    local_file_path = f'/home/mazazyrik/dev/speechai/speech/uploaded_files/{file_name}'
    logging.info('sftp connected')
    try:
        sftp.get(remote_file_path, local_file_path)
    except FileNotFoundError:
        logging.error('File not found on server')
        await message.answer('Файл не найден!')

    logging.info('file downloaded')
    sftp.remove(remote_file_path)
    logging.info('file removed')
    sftp.close()
    ssh.close()
