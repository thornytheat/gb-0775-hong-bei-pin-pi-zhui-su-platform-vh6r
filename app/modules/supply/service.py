from collections import Counter

from app.errors import RoastError

from .reservations import reserve


def check_supply(intake):
    for warning in intake['rejected']:
        if warning['sheet'] in ('jobs','origins') and warning['code']!='COPIED_TICKET':
            raise RoastError('BAD_REGISTER',f'{warning["sheet"]} 第 {warning["line"]} 行定义有误')
    tables=intake['tables']
    jobs,origins=tables['jobs'],tables['origins']
    rejected, outputs, candidates=[],{},[]
    for key,row in tables['outputs'].items():
        if row['work'] not in jobs:
            rejected.append({**row,'code':'NO_WORK'})
        else:
            outputs[key]=row
    coupons={key:row for key,row in outputs.items() if row['kind']=='return'}
    for row in tables['inputs'].values():
        if row['work'] not in jobs:
            rejected.append({**row,'code':'NO_WORK'})
        elif row['source_kind']=='origin' and row['source'] not in origins:
            rejected.append({**row,'code':'NO_ORIGIN'})
        elif row['source_kind']=='return' and row['source'] not in coupons:
            rejected.append({**row,'code':'NO_RETURN'})
        else:
            candidates.append(row)
    accepted,overdraw,pools=reserve(candidates,origins,coupons)
    rejected.extend(overdraw)
    input_bad, output_bad = {},{}
    for row in intake['rejected']+rejected:
        if row['code']=='COPIED_TICKET' or row.get('work') not in jobs:
            continue
        if row['sheet'] in ('inputs','outputs'):
            index=input_bad if row['sheet']=='inputs' else output_bad
            index.setdefault(row['work'],[]).append(row)
    return dict(jobs=jobs,origins=origins,inputs=accepted,outputs=outputs,return_lots=coupons,
                pools=pools,by_input_issue=input_bad,by_output_issue=output_bad,rejected=rejected,
                reasons=dict(Counter(row['code'] for row in rejected)))
