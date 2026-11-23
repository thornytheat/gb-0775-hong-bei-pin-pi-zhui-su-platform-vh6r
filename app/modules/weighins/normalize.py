from .mass import grams
from .schema import KEY_FIELD, MISSING


class RejectedTicket(ValueError):
    pass


def normalize(name, row):
    raw={key:value.strip() for key,value in row['raw'].items()}
    base={**row,'id':raw[KEY_FIELD[name]]}
    if 'work' in raw:
        base['work']=raw['work']
    try:
        if any(value.upper() in MISSING for value in raw.values()):
            raise RejectedTicket('NO_VALUE')
        unit=raw['unit']
        if name=='outputs':
            if raw['kind'] not in ('pack','loss','return'):
                raise RejectedTicket('BAD_KIND')
            gross,tare=(grams(raw[key],unit) for key in ('gross','tare'))
            if tare>gross:
                raise RejectedTicket('NEGATIVE_NET')
            return {**base,'kind':raw['kind'],'gross_g':str(gross),'tare_g':str(tare),'g':str(gross-tare)}
        if name=='inputs':
            if raw['source_kind'] not in ('origin','return'):
                raise RejectedTicket('BAD_KIND')
            net=grams(raw['quantity'],unit)
            if net<=0:
                raise RejectedTicket('BAD_MASS')
            return {**base,'source_kind':raw['source_kind'],'source':raw['source'],'g':str(net)}
        quantity=grams(raw['available' if name=='origins' else 'measured'],unit)
        if name=='jobs' and quantity<=0:
            raise RejectedTicket('BAD_MASS')
        return {**base,'g':str(quantity),'label':raw['label']}
    except RejectedTicket as error:
        return {**base,'code':str(error)}
    except ValueError:
        return {**base,'code':'BAD_MASS'}
