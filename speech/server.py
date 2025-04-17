"""
Server module for SpeechAI bot.
Handles file operations via SSH.
"""
import logging
import os
import paramiko
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_file(file_name, message):
    """
    Download file from remote server via SSH.
    
    Args:
        file_name (str): Name of the file to download
        message: Telegram message object
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Get SSH credentials from environment
    ssh.connect(
        os.getenv('SSH_HOST'),
        username=os.getenv('SSH_USERNAME'),
        password=os.getenv('SSH_PASSWORD')
    )
    
    logging.info('ssh connected')
    sftp = ssh.open_sftp()
    
    # Get paths from environment
    remote_file_path = os.path.join(os.getenv('SSH_REMOTE_PATH'), file_name)
    local_file_path = os.path.join(os.getenv('SSH_LOCAL_PATH'), file_name)
    
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
