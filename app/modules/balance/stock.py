from collections import Counter
from fractions import Fraction


def stock(trace, packing):
    used=Counter()
    for row in trace['jobs'].values():
        for feed in row['lots']:
            if feed['source_kind']=='origin':
                used[feed['source']]+=Fraction(feed['g'])
    distributed=Counter()
    for row in packing['outputs'].values():
        if row['status']=='certified' and row['kind'] in ('pack','loss'):
            distributed.update({key:Fraction(val) for key,val in row['origin_g'].items()})
    for rows,key in ((packing['jobs'],'hold_origin_g'),(packing['returns'],'remaining_origin_g')):
        for row in rows.values():
            distributed.update({origin:Fraction(value) for origin,value in row[key].items()})
    totals={key:sum((Fraction(row[key]) for row in packing['jobs'].values()),Fraction())
            for key in ('pack_g','loss_g','hold_g','pending_g')}
    returns=sum((Fraction(row['available_g']) for row in packing['returns'].values() if row['available_g'] is not None),Fraction())
    original=sum(used.values())
    delta=original-sum(totals[key] for key in ('pack_g','loss_g','hold_g'))-returns
    origins={key:dict(used_g=str(used[key]), distributed_g=str(distributed[key]),delta_g=str(used[key]-distributed[key]))
             for key in sorted(used.keys()|distributed.keys())}
    return dict(**{key:str(val) for key,val in totals.items()},return_stock_g=str(returns),origin_used_g=str(original),
                delta_g=str(delta),origins=origins,balanced=delta==0 and all(row['delta_g']=='0' for row in origins.values()))
