import gnupg, os
from pathlib import Path

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
    
def ls(user_path: str=None, data_path: str='data') -> list:
    paths = DisplayablePath.make_tree(
        data_path / Path('my-passwords') / (user_path or ''),
        criteria=is_not_hidden
    )
    return [path.displayable() for path in paths]

def decrypt(user_path: str, data_path: str='data') -> str:
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'

    password_store = Path().cwd() / data_path / 'my-passwords'
    
    return str(gpg.decrypt_file(str(password_store / (user_path + '.gpg')), passphrase=os.getenv('PASSPHRASE'))).split('\n')