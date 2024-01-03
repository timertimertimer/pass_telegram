import gnupg
import os
from pathlib import Path
from string import digits, ascii_letters, punctuation
from random import sample
from utils import logger

password_store = Path(__file__).parent / 'my-passwords'
gpg = gnupg.GPG()
gpg.encoding = 'utf-8'


def is_not_hidden(path: Path):
    return not path.name.startswith(".")


def ls(user_path: str | Path = None) -> list:
    return sorted([path.name for path in (password_store / (user_path or '')).iterdir() if is_not_hidden(path)],
                  key=lambda x: x.endswith('.gpg'))


def decrypt(user_path: str | Path) -> str:
    user_path = str(user_path)
    return str(gpg.decrypt_file(
        user_path if str(password_store) in user_path else str(password_store / (user_path + '.gpg')),
        passphrase=os.getenv('PASSPHRASE')
    ))


def insert(user_path: str | Path, password: str) -> bool:
    path = password_store / user_path
    with open(str(path) + '.txt', 'w', encoding='utf-8') as file:
        file.write(password)

    with open(password_store / (str(user_path) + '.txt'), 'rb') as file:
        status = gpg.encrypt_file(
            file,
            recipients=['arkashaparovozov69@gmail.com'],
            output=str(path) + '.gpg',
            passphrase=os.getenv('PASSPHRASE')
        )
        logger.info(f"ok: {status.ok}")
        logger.info(f"status: {status.status}")
        logger.info(f"stderr: {status.stderr}")

    Path(str(path) + '.txt').unlink()
    return status.ok


def generate_random_password(length: int = 25, no_symbols: bool = False) -> str | None:
    alph = digits + ascii_letters if no_symbols else digits + ascii_letters + punctuation
    return ''.join(sample(alph, length))


if __name__ == '__main__':
    print(ls('Crypto'))
