import gnupg
import os
from pathlib import Path
from string import digits, ascii_letters, punctuation
from random import sample

import data
from utils import logger

password_store = Path(__file__).parent / 'my-passwords'
gpg = gnupg.GPG()
gpg.encoding = 'utf-8'


def is_not_hidden(path: Path):
    return not path.name.startswith(".")


def ls(user_path: str | Path = None) -> list:
    current_folder_structure = []
    for path in (password_store / (user_path or '')).iterdir():
        name = path.name
        if is_not_hidden(path):
            if not path.name.endswith('.gpg'):
                name += '/'
            else:
                name = name[:-4]
            current_folder_structure.append(name)
    return sorted(current_folder_structure, key=lambda x: not x.endswith('/'))


def decrypt(user_path: str | Path) -> str:
    user_path = str(user_path)
    if not user_path.endswith('.gpg'):
        user_path += '.gpg'
    return str(gpg.decrypt_file(
        user_path if Path(user_path).is_relative_to(password_store) else password_store / user_path,
        passphrase=os.getenv('PASSPHRASE')  # TODO: redis
    ))


def insert(user_path: str | Path, password: str) -> bool:
    user_path = user_path if user_path.is_relative_to(password_store) else password_store / user_path
    user_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f'Created sub directories: {str(user_path.parent.relative_to(password_store))}')
    new_path = Path(str(user_path) + '.txt')
    with new_path.open(mode='w', encoding='utf-8') as file:
        file.write(password)
    logger.info(f'Saved password in {new_path.relative_to(password_store)}')

    with new_path.open(mode='rb') as file:
        status = gpg.encrypt_file(
            file,
            recipients=['arkashaparovozov69@gmail.com'],
            output=str(user_path) + '.gpg',
            passphrase=os.getenv('PASSPHRASE')
        )
        if status.ok:
            logger.success(f'Encrypted password in {new_path.relative_to(password_store)}')
        else:
            logger.error(status.stderr)

    new_path.unlink()
    logger.info(f'Cleaned temp {new_path.relative_to(password_store)}')
    return status.ok


def generate_random_password(length: int = 25, no_symbols: bool = False) -> str | None:
    alph = digits + ascii_letters if no_symbols else digits + ascii_letters + punctuation
    return ''.join(sample(alph, length))


def mv(old_path: str | Path, new_path: str | Path) -> (bool, Path, Path):
    old_path = Path(old_path)
    new_path = Path(new_path)
    old_path = old_path if old_path.is_relative_to(password_store) else password_store / old_path
    new_path = new_path if new_path.is_relative_to(password_store) else password_store / new_path
    if not str(new_path).endswith('.gpg'):
        new_path = Path(str(new_path) + '.gpg')
    try:
        Path(old_path).replace(new_path)
    except OSError as e:
        logger.error(e)
        return False, old_path, new_path
    logger.success(
        f'Moved from {str(old_path.relative_to(password_store))} to {str(new_path.relative_to(password_store))}'
    )
    return True, old_path, new_path


def delete(user_path: str | Path) -> str:
    password = decrypt(user_path)
    user_path = user_path if user_path.is_relative_to(password_store) else password_store / user_path
    Path(str(user_path) + '.gpg').unlink()
    logger.success(f'Deleted {str(user_path.relative_to(data.password_store))}\n{password}')
    if user_path.parent != data.password_store:
        directory = user_path.parent
        try:
            Path(directory).rmdir()
            logger.info(f'Cleaned empty directory {str(directory.relative_to(data.password_store))}')
        except OSError as e:
            if 'The directory is not empty' in str(e):
                logger.info(f'The directory {str(directory.relative_to(data.password_store))} is not empty')
            else:
                logger.error(e)
    return password


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    insert('Crypto/test/test', '123')
    print(delete('Crypto/test/test'))
