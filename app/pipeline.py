from app.modules.balance.service import verify_mass
from app.modules.lineage.service import trace
from app.modules.packing.budget import budgets
from app.modules.packing.settle import pack
from app.modules.supply.service import check_supply
from app.modules.weighins.service import weigh

PHASES=('weighins','supply','lineage','packing','balance')


def compute(contents, until='balance'):
    result={'weighins':weigh(contents)}
    if until=='weighins':
        return result
    supply=result['supply']=check_supply(result['weighins'])
    if until=='supply':
        return result
    bounds=budgets(supply)
    origins=result['lineage']=trace(supply,bounds)
    if until=='lineage':
        return result
    result['packing']=pack(supply,origins,bounds)
    if until!='packing':
        result['balance']=verify_mass(result['weighins'],origins,result['packing'])
    return result
