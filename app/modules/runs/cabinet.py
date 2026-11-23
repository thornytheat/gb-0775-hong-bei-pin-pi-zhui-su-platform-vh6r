import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.errors import RoastError

from .fingerprint import encode

KEY = re.compile(r'[a-f0-9]{64}\Z')


class Cabinet:
    def __init__(self, directory):
        self.path=Path(directory)
        self.path.mkdir(parents=True,exist_ok=True)

    def write(self, document):
        final=self.path / f'{document["manifest"]["id"]}.json'
        part = None
        try:
            with NamedTemporaryFile(mode='w',encoding='utf-8',dir=self.path,prefix='.pending-',delete=False) as stream:
                part=Path(stream.name)
                stream.write(encode(document))
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(part,final)
                return True
            except FileExistsError:
                return False
        finally:
            if part is not None:
                part.unlink(missing_ok=True)

    def read(self, key):
        try:
            if not KEY.fullmatch(key):
                raise FileNotFoundError()
            return json.loads((self.path / f'{key}.json').read_text(encoding='utf-8'))
        except FileNotFoundError as exc:
            raise RoastError('NO_RUN','称签归档不存在',404) from exc
        except (json.JSONDecodeError,UnicodeError) as exc:
            raise RoastError('DAMAGED_RUN','归档原件不可读',409) from exc

    def recent(self):
        entries=[]
        for file in self.path.glob('*.json'):
            if KEY.fullmatch(file.stem):
                entries.append((file.stat().st_mtime_ns,file.stem))
        return [self.read(key)['manifest'] for _,key in sorted(entries,reverse=True)[:30]]
