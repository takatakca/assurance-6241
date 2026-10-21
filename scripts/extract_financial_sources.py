from pathlib import Path
import csv,json,hashlib,re
from datetime import datetime,timedelta
from collections import defaultdict
import openpyxl
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
ARC=ROOT/'6241 Léger/10_Archive_avocat_2026-10-05'
OUT=ROOT/'scripts/.build-livrables'
OUT.mkdir(exist_ok=True,parents=True)
data={'sources':[],'ledger':[],'workbooks':[],'pdfs':[]}
def source(p):
    rec={'path':str(p.relative_to(ROOT)).replace('\\','/'),'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    data['sources'].append(rec)
    return rec['path']
p=ARC/'GRAND-LIVRE-ORIGINAL-feuille-1.csv'
src=source(p)
account=name=None
for i,row in enumerate(csv.reader(p.open(encoding='utf-8-sig')),1):
    row += ['']*(11-len(row))
    if re.fullmatch(r'\d{4}',row[0]): account,name=row[0],row[2]
    if re.fullmatch(r'J\d+',row[6]) and row[3]:
        try: date=(datetime(1899,12,30)+timedelta(days=float(row[3]))).date().isoformat()
        except: date=row[3]
        data['ledger'].append({'row':i,'account':account,'accountName':name,'date':date,'description':row[4],'sourceNo':row[5],'journal':row[6],'debit':float(row[7] or 0),'credit':float(row[8] or 0),'source':src})
paths=list((ARC/'comptabilite-ventes2024').glob('*.xlsx'))+list((ARC/'joey-rapport7-avril2025').glob('*.xlsx'))+list((ARC/'photos-assurance-2024').glob('*.xlsx'))
paths+=list((ROOT/'6241 Léger/04_Pieces_jointes/takatak.ca@gmail.com').glob('*Janv*.xlsx'))
for p in paths:
    src=source(p)
    wb=openpyxl.load_workbook(p,data_only=True,read_only=True)
    wf=openpyxl.load_workbook(p,data_only=False,read_only=False)
    sheets=[]
    for s in wb:
        rows=[]
        for row in s:
            populated=[{'cell':c.coordinate,'value':c.value.isoformat() if isinstance(c.value,datetime) else c.value,'formula':wf[s.title][c.coordinate].value if wf[s.title][c.coordinate].data_type=='f' else None} for c in row if c.value is not None]
            if populated: rows.append(populated)
        sheets.append({'name':s.title,'rows':rows})
    data['workbooks'].append({'source':src,'sheets':sheets})
    print(p.name,[(s['name'],len(s['rows'])) for s in sheets])
pdfs=list((ARC/'sources').glob('*.pdf'))+list((ARC/'photos-assurance-2024').glob('*.pdf'))+list((ARC/'pieces-facturation-oct2025').glob('*.pdf'))
for p in pdfs:
    if p.name.startswith('Registraire'):continue
    src=source(p)
    try:
        pages=[{'page':i+1,'text':page.extract_text() or ''} for i,page in enumerate(PdfReader(p).pages)]
        data['pdfs'].append({'source':src,'pages':pages})
    except Exception as e: data['pdfs'].append({'source':src,'error':str(e)})
(OUT/'finance-source-extract.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
accounts=defaultdict(lambda:{'debits':0,'credits':0,'count':0})
for r in data['ledger']:
    a=accounts[r['account']];a['debits']+=r['debit'];a['credits']+=r['credit'];a['count']+=1
print('ACCOUNTS',dict(accounts))
