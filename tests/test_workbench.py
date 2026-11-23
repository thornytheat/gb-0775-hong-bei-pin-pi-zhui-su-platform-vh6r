def test_seven_pages(client):
    sections={'balance':'重量勾稽卷联','weighins':'秤单收讫联','supply':'来源额度联','lineage':'拼批血缘卷联',
              'packing':'返料占用与余额','runs':'在柜卷联','proof':'包装批次追溯联'}
    for view,text in sections.items():
        response=client.get('/ledger/'+view)
        assert response.status_code==200 and text in response.get_data(as_text=True)


def test_cycle_evidence_on_web(client):
    page=client.get('/ledger/lineage?work=BA-09').get_data(as_text=True)
    assert 'BA-09 → BA-10 → BA-09' in page


def test_rejected_file_has_no_archive(client,files):
    files['jobs']='work,label,measured,unit\n'
    response=client.post('/api/runs',json={'files':files})
    assert (response.status_code,response.json['code'])==(422,'HEADER_ONLY')
    assert client.get('/api/runs').json['runs']==[]
