def test_bom(dirty):  # TRAP-02
    assert dirty['weighins']['tables']['inputs']['IN-01']['raw']['ticket']=='IN-01'


def test_segment(dirty):  # TRAP-04
    assert dirty['weighins']['files']['inputs']==dict(segments=2,blanks=0,records=18,accepted=14,isolated=4)


def test_bad_width(dirty):  # TRAP-05
    issue=next(row for row in dirty['weighins']['rejected'] if row['code']=='BAD_WIDTH')
    assert (issue['work'],issue['line'],issue['raw'][-1])==('BA-08',18,'多余')


def test_sentinel(dirty):  # TRAP-07
    row=next(row for row in dirty['weighins']['rejected'] if row['code']=='NO_VALUE')
    assert row['id']=='IN-15' and row['raw']['quantity']=='N/A'


def test_unit_normalized_duplicate(dirty):  # TRAP-15
    accepted=dirty['weighins']['tables']['outputs']['PK-A']
    repeat=next(row for row in dirty['weighins']['rejected'] if row['code']=='COPIED_TICKET')
    assert (accepted['raw']['unit'],repeat['raw']['unit'],repeat['kept_line'])==('kg','g',2)
    assert accepted['g']==repeat['g']=='600'


def test_conflict_removed(dirty):  # TRAP-14
    conflict=[row for row in dirty['weighins']['rejected'] if row['code']=='TICKET_CONFLICT']
    assert [(row['id'],row['g']) for row in conflict]==[('IN-17','70'),('IN-17','60')]
    assert 'IN-17' not in dirty['weighins']['tables']['inputs']


def test_invalid_header(client,files):
    files['outputs']='bad,header\n'
    response=client.post('/api/lots/weighins',json={'files':files})
    assert (response.status_code,response.json['code'])==(422,'BAD_HEADER')
