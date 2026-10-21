from pathlib import Path
from email import policy
from email.parser import BytesParser
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'HARMONY MOVERS/03_Courriels/Originaux_ooeuf_2026-10-20'
records=[]
for source in sorted(BASE.glob('*.eml')):
    raw=source.read_bytes()
    message=BytesParser(policy=policy.default).parsebytes(raw)
    entry={'file':source.name,'sha256':hashlib.sha256(raw).hexdigest(),'headers':{k:str(message.get(k,'')) for k in ['Subject','From','To','Cc','Date','Message-ID']},'attachments':[]}
    body=message.get_body(preferencelist=('plain','html'))
    if body:
        suffix='.html' if body.get_content_type()=='text/html' else '.txt'
        target=source.with_suffix(suffix)
        content=body.get_content()
        target.write_text(content,encoding='utf-8')
        entry['body_file']=target.name
    for part in message.iter_attachments():
        filename=part.get_filename()
        if not filename:continue
        safe=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',Path(filename).name)
        data=part.get_payload(decode=True)
        if not data:continue
        dest=BASE/'Pieces_jointes'/safe;dest.parent.mkdir(exist_ok=True)
        if dest.exists() and dest.read_bytes()!=data:
            dest=dest.with_name(dest.stem+'_'+hashlib.sha256(data).hexdigest()[:8]+dest.suffix)
        dest.write_bytes(data)
        entry['attachments'].append({'original_filename':filename,'file':dest.relative_to(BASE).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    records.append(entry)
(BASE/'manifest-originaux.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))

