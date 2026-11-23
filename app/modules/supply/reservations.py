from collections import defaultdict
from fractions import Fraction


def reserve(demands, origins, coupons):
    grouped=defaultdict(list)
    for row in demands:
        grouped[row['source_kind'],row['source']].append(row)
    accepted, rejected, pools=[],[],{'origin':{},'return':{}}
    for kind,bins in (('origin',origins),('return',coupons)):
        for name, source in bins.items():
            requests=grouped[kind,name]
            requested=sum((Fraction(row['g']) for row in requests),Fraction())
            capacity=Fraction(source['g'])
            status='OVERDRAW_ORIGIN' if kind=='origin' else 'OVERDRAW_RETURN'
            fits=requested<=capacity
            pools[kind][name]=dict(capacity_g=str(capacity),requested_g=str(requested),
                                   reserved_g=str(requested if fits else 0),blocked=not fits,
                                   source_line=source['line'],tickets=[row['id'] for row in requests])
            if fits:
                accepted.extend(requests)
            else:
                rejected.extend({**row,'code':status,'capacity_g':str(capacity),'requested_g':str(requested)} for row in requests)
    return accepted,rejected,pools
