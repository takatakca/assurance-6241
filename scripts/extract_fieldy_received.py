from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
source = Path('C:/Users/fansh/Downloads/Fieldy – Interrogatoire préalable Quadro Holding vs Harmony Movers – 5 octobre 2026 – transcription verbatim.pdf')
dest = root / 'HARMONY MOVERS/11_Fieldy'
pdf = dest / '2026-10-05-Fieldy-interrogatoire-Quadro-Harmony.pdf'
raw = source.read_bytes()
if not raw.startswith(b'%PDF-'):
    raise ValueError('Le fichier téléchargé ne commence pas par une signature PDF')
if pdf.exists() and pdf.read_bytes() != raw:
    raise ValueError('Une version différente existe; ne pas écraser')
shutil.copy2(source, pdf)
reader = PdfReader(pdf)
pages = [{'page':i+1,'text':page.extract_text() or ''} for i,page in enumerate(reader.pages)]
(dest/'texte-natif-pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
(dest/'texte-natif-integral.txt').write_text('\n\n'.join(f'=== PAGE {p["page"]} ===\n{p["text"]}' for p in pages), encoding='utf-8')
report = {'source_filename':source.name,'source_path':str(source),'pdf_path':pdf.relative_to(root).as_posix(),'share_url':'https://acrobat.adobe.com/id/urn:aaid:sc:VA6C2:c4dc68eb-22e2-4295-bcb2-ca96aa69398f','email_message_id':'1a15fd5a4ddf7dfb','acquired_utc':datetime.now(timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'pages':len(pages),'nonempty_pages':sum(bool(p['text'].strip()) for p in pages),'characters':sum(len(p['text']) for p in pages),'extraction':'Texte natif extrait avec pypdf; aucune OCR ni correction de la transcription','audio_verified':False,'speaker_attribution_verified':False}
(dest/'acquisition-pdf.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
