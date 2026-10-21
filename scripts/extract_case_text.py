from pathlib import Path
import json, hashlib, subprocess, re, sys
from pypdf import PdfReader
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
CASE=ROOT/'6241 Léger'
OUT=CASE/'09_Index_et_tracabilite'/'Texte_et_OCR'
TMP=CASE/'99_Travail_et_collecte'/'ocr-images'
OUT.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
POP=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
seen={}; records=[]; jobs=[]
for f in sorted(CASE.rglob('*')):
    if not f.is_file() or any(p in f.parts for p in ['Texte_et_OCR','ocr-images']): continue
    if f.suffix.lower() not in ['.pdf','.png','.jpg','.jpeg','.webp']: continue
    h=hashlib.sha256(f.read_bytes()).hexdigest()
    if h in seen:
        seen[h]['copies'].append(f.relative_to(CASE).as_posix()); continue
    rec={'id':'DOC-'+h[:12].upper(),'sha256':h,'source':f.relative_to(CASE).as_posix(),'copies':[], 'pages':[], 'errors':[]}
    seen[h]=rec; records.append(rec)
    try:
        if f.suffix.lower()=='.pdf':
            reader=PdfReader(f)
            for i,p in enumerate(reader.pages,1):
                text=p.extract_text() or ''
                row={'page':i,'characters':len(text.strip()),'method':'Texte PDF natif','text_file':None}
                stem=f'{rec["id"]}-p{i:03}'
                if text.strip():
                    dest=OUT/(stem+'.txt'); dest.write_text(text,encoding='utf-8');row['text_file']=dest.name
                rec['pages'].append(row)
                if len(re.sub(r'\s','',text)) < 100:
                    prefix=TMP/stem
                    proc=subprocess.run([str(POP),'-f',str(i),'-l',str(i),'-singlefile','-scale-to','2600','-png',str(f),str(prefix)],capture_output=True)
                    png=prefix.with_suffix('.png')
                    if proc.returncode==0 and png.exists():
                        jobs.append({'id':rec['id'],'page':i,'image':str(png),'output':str(OUT/(stem+'-ocr.txt'))})
                        row['ocr_requested']=True
                    else: rec['errors'].append(f'Rendu page {i}: '+proc.stderr.decode(errors='replace')[:250])
        else:
            stem=rec['id']+'-p001'; dest=TMP/(stem+'.png')
            with Image.open(f) as img:
                img=ImageOps.exif_transpose(img).convert('RGB'); img.thumbnail((2600,2600)); img.save(dest)
            rec['pages'].append({'page':1,'characters':0,'method':'Image','text_file':None,'ocr_requested':True})
            jobs.append({'id':rec['id'],'page':1,'image':str(dest),'output':str(OUT/(stem+'-ocr.txt'))})
    except Exception as e: rec['errors'].append(str(e))
    if len(records)%20==0: print(f'{len(records)} documents distincts préparés',flush=True)
(OUT/'manifest-extraction.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'ocr-jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8-sig')
print(json.dumps({'unique_documents':len(records),'copies':sum(len(x['copies']) for x in records),'pages':sum(len(x['pages']) for x in records),'ocr_jobs':len(jobs),'errors':sum(len(x['errors']) for x in records)},ensure_ascii=False),flush=True)

