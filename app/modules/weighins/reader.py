import csv
from io import StringIO

from app.errors import RoastError

from .schema import SCHEMA


def load_sheet(name, text):
    reader=csv.reader(StringIO(text.removeprefix('\ufeff'),newline=''),strict=True)
    rows, bad = [], []
    stats = {'segments':1,'blanks':0,'records':0}
    try:
        header=next(reader,None)
        if header is None:
            raise RoastError('EMPTY_FILE',f'{name} 原件为空')
        if not text.strip('\ufeff \t\r\n,'):
            raise RoastError('BLANK_FILE',f'{name} 只有空行')
        if len(header)!=len(SCHEMA[name]) or set(header)!=set(SCHEMA[name]):
            raise RoastError('BAD_HEADER',f'{name} 表头定义有误')
        work_index = header.index('work') if 'work' in header else None
        for fields in reader:
            if fields==header:
                stats['segments']+=1
            elif not any(field.strip() for field in fields):
                stats['blanks']+=1
            else:
                stats['records']+=1
                if len(fields)!=len(header):
                    item=dict(sheet=name,line=reader.line_num,raw=fields,code='BAD_WIDTH')
                    if work_index is not None and work_index < len(fields):
                        item['work']=fields[work_index].strip()
                    bad.append(item)
                else:
                    rows.append(dict(sheet=name,line=reader.line_num,raw=dict(zip(header,fields))))
    except csv.Error as exc:
        raise RoastError('BAD_CSV',f'{name} 第 {reader.line_num} 行格式有误') from exc
    if not stats['records'] and name in ('origins','jobs'):
        raise RoastError('HEADER_ONLY',f'{name} 缺少登记行')
    return rows,bad,stats
