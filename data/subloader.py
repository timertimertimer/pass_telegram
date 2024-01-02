import gnupg
import os
import random
from pathlib import Path
from string import digits, ascii_letters, punctuation
from random import sample

password_store = Path(__file__).parent.resolve() / 'my-passwords'
gpg = gnupg.GPG()
gpg.encoding = 'utf-8'


class DisplayablePath(object):
    display_filename_prefix_middle = '╠══'
    display_filename_prefix_last = '╚══'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '║   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return '<i>' + self.path.name + '</i>'
        return self.path.name.split('.gpg')[0]

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


# With a criteria (skip hidden files)
def is_not_hidden(path):
    return not path.name.startswith(".")


def ls(user_path: str = None) -> list:
    paths = DisplayablePath.make_tree(
        password_store / (user_path or ''),
        criteria=is_not_hidden
    )
    return [path.displayable() for path in paths]


def decrypt(user_path: str) -> list[str]:
    return str(gpg.decrypt_file(
        str(password_store / (user_path + '.gpg')),
        passphrase=os.getenv('PASSPHRASE')
    )).split('\n')


def insert(user_path: str, password: str):
    path = (password_store / user_path).as_posix()
    open(path + '.txt', 'w', encoding='utf-8').write(password)

    with open(password_store / (user_path + '.txt'), 'rb') as file:
        status = gpg.encrypt_file(
            file,
            recipients=['timerkhan2002@gmail.com'],
            output=path + '.gpg',
            passphrase=os.getenv('PASSPHRASE')
        )
        print("ok: ", status.ok)
        print("status: ", status.status)
        print("stderr: ", status.stderr)

    Path(path + '.txt').unlink()
    return password


def generate(user_path: str, length: int = 25, no_symbols: bool = False):
    alph = digits + ascii_letters if no_symbols else digits + ascii_letters + punctuation
    return insert(user_path, ''.join(sample(alph, length)))


if __name__ == '__main__':
    print(ls())