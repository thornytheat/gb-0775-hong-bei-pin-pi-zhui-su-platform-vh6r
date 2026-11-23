from app.config import FILE_LIMIT,SAMPLES
from app.errors import RoastError
from app.modules.weighins.schema import SCHEMA


def receive(payload):
    if isinstance(payload,dict) and set(payload)=={'sample'}:
        key=payload['sample']
        if key not in ('dirty','clean'):
            raise RoastError('NO_SAMPLE','该样例未登记',404)
        return {name:(SAMPLES/key/f'{name}.csv').read_bytes().decode() for name in SCHEMA}
    files=payload.get('files') if isinstance(payload,dict) else None
    if not isinstance(files,dict) or set(payload)!={'files'} or set(files)!=set(SCHEMA) or any(not isinstance(text,str) for text in files.values()):
        raise RoastError('BAD_INPUT','请提交整套称签 CSV')
    try:
        if any(len(text.encode())>FILE_LIMIT for text in files.values()):
            raise RoastError('TOO_LARGE','单张原件超过 300 KB',413)
    except UnicodeEncodeError as exc:
        raise RoastError('BAD_INPUT','原件含非法字符') from exc
    return files
