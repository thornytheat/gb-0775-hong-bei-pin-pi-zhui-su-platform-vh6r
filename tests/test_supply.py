from app.pipeline import compute


def test_split_reservation(dirty):
    pool=dirty['supply']['pools']['return']['RT-A']
    assert pool==dict(capacity_g='300',requested_g='300',reserved_g='300',blocked=False,source_line=4,
                      tickets=['IN-03','IN-05'])


def test_global_overdraw_no_first_claim(dirty,files):  # TRAP-19
    header,*body=files['inputs'].splitlines()
    files['inputs']='\n'.join([header,*reversed(body)])
    other=compute(files,'supply')['supply']
    assert other['pools']==dirty['supply']['pools']
    denied=[row['id'] for row in other['rejected'] if row['code']=='OVERDRAW_RETURN']
    assert denied==['IN-09','IN-10'] and other['pools']['return']['RT-D']['reserved_g']=='0'


def test_unregistered_return(dirty):
    row=next(row for row in dirty['supply']['rejected'] if row['code']=='NO_RETURN')
    assert (row['id'],row['source'],row['g'])==('IN-12','RT-404','70')


def test_raw_origin_overdraw(files):
    files['origins']=files['origins'].replace('1000,g','750,g')
    result=compute(files,'supply')['supply']
    assert result['pools']['origin']['ET-01']['reserved_g']=='0'
    assert result['reasons']['OVERDRAW_ORIGIN']==2


def test_unregistered_work(files):
    files['inputs']+='IN-20,BA-77,origin,ET-01,10,g\n'
    result=compute(files,'supply')['supply']
    assert result['reasons']['NO_WORK']==1 and result['pools']['origin']['ET-01']['requested_g']=='800'


def test_master_conflict(client,files):
    files['jobs']+='BA-01,晨配基础批,1.1,kg\n'
    response=client.post('/api/lots/supply',json={'files':files})
    assert (response.status_code,response.json['code'])==(422,'BAD_REGISTER')
