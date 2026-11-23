from collections import Counter

from .dedup import collapse
from .normalize import normalize
from .reader import load_sheet
from .schema import SCHEMA


def weigh(sources):
    tables, counts, issues = {}, {}, []
    for name in SCHEMA:
        rows, bad, stats=load_sheet(name,sources[name])
        valid=[]
        for row in rows:
            parsed=normalize(name,row)
            if 'code' in parsed:
                bad.append(parsed)
            else:
                valid.append(parsed)
        kept, collision=collapse(valid)
        bad.extend(collision)
        tables[name]={row['id']:row for row in kept}
        issues.extend(sorted(bad,key=lambda row:row['line']))
        counts[name]={**stats,'accepted':len(kept),'isolated':len(bad)}
    return dict(tables=tables,files=counts,rejected=issues,reasons=dict(Counter(row['code'] for row in issues)))
