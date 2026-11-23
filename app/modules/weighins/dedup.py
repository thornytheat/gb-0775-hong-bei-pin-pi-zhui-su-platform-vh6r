from collections import defaultdict


def collapse(records):
    groups=defaultdict(list)
    for record in records:
        groups[record['id']].append(record)
    kept, rejected=[],[]
    for key in sorted(groups):
        items=groups[key]
        keys={tuple((name,value) for name,value in sorted(row.items()) if name not in {'line','raw','sheet'})
              for row in items}
        if len(keys)>1:
            rejected.extend({**item,'code':'TICKET_CONFLICT'} for item in items)
        else:
            winner,*copies=items
            kept.append(winner)
            rejected.extend({**row,'code':'COPIED_TICKET','kept_line':winner['line']} for row in copies)
    return kept,rejected
