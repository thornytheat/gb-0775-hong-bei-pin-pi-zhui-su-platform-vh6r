from collections import Counter
from fractions import Fraction


def propagate(parts, portion, intake):
    return {key:str(Fraction(value)*portion/intake) for key,value in parts.items()}


def pack(supply, trace, budgets):
    allocations, returns, packages, jobs={}, {}, {}, {}
    drawn=Counter()
    for work,row in trace['jobs'].items():
        plan=budgets[work]
        allowed=not row['codes']
        if allowed:
            for feed in row['lots']:
                if feed['source_kind']=='return':
                    drawn[feed['source']]+=Fraction(feed['g'])
        intake=Fraction(row['input_g'])
        remaining=Fraction(plan['remaining_g']) if allowed else Fraction()
        totals=Counter()
        for output in plan['outputs']:
            amount=Fraction(output['g'])
            record={**output,'status':'certified' if allowed else 'pending',
                    'origin_g':propagate(row['composition_g'],amount,intake) if allowed else {}}
            allocations[record['id']]=record
            if allowed:
                totals[output['kind']]+=amount
                if output['kind']=='pack':
                    packages[output['id']]=record
        jobs[work]=dict(pack_g=str(totals['pack']),loss_g=str(totals['loss']),return_g=str(totals['return']),
                        hold_g=str(remaining),hold_origin_g=propagate(row['composition_g'],remaining,intake) if allowed else {},
                        pending_g='0' if allowed else row['input_g'],budget=plan)
    for key, pool in supply['return_lots'].items():
        entry=allocations[key]
        used=drawn[key]
        allowed=entry['status']=='certified'
        left=Fraction(entry['g'])-used if allowed else None
        returns[key]={**entry,'drawn_g':str(used),'available_g':str(left) if left is not None else None,
                      'request_g':supply['pools']['return'][key]['requested_g'],
                      'remaining_origin_g':propagate(entry['origin_g'],left,Fraction(entry['g'])) if left else {}}
    return dict(jobs=jobs,outputs=allocations,returns=returns,packages=packages)
