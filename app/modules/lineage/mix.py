from collections import defaultdict
from fractions import Fraction


def blend(feeds, donors, genealogy):
    composition, evidence=defaultdict(Fraction),[]
    for feed in feeds:
        amount=Fraction(feed['g'])
        if feed['source_kind']=='origin':
            split={feed['source']:amount}
            sources=[]
        else:
            donor=donors[feed['source']]
            parent=genealogy[donor['work']]
            share=amount/Fraction(parent['input_g'])
            split={key:Fraction(value)*share for key,value in parent['composition_g'].items()}
            sources=[{'work':donor['work'],'line':donor['line'],'coupon':donor['id']}]
        for key,part in split.items():
            composition[key]+=part
        evidence.append(dict(ticket=feed['id'],line=feed['line'],source=feed['source'],source_kind=feed['source_kind'],
                             g=feed['g'],origin_g={key:str(val) for key,val in sorted(split.items())},from_coupon=sources))
    return {key:str(val) for key,val in sorted(composition.items())},evidence
