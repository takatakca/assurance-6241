from pathlib import Path
import json,hashlib,re

root=Path(__file__).resolve().parents[1]
folder=root/'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Ooeuf'
raw=folder/'99_Travail_et_collecte'
raw.mkdir(exist_ok=True)
for p in folder.glob('*-dom.txt'):
    backup=raw/p.name
    if not backup.exists(): backup.write_bytes(p.read_bytes())
    text=backup.read_text(encoding='utf-8')
    start=text.find('- main:')
    if start>=0:text=text[start:]
    end=text.find('- complementary ')
    if end>=0:text=text[:end]
    # Remove operational navigation/payment URLs from the public working copy.
    # Native email and PDF sources remain byte-for-byte unchanged.
    text=re.sub(r'^\s*- /url: (?!mailto:|tel:).*$','',text,flags=re.M)
    text='EXTRACTION DE L’INTERFACE GMAIL — compte ooeuf.ca@gmail.com — collecte du 24 octobre 2026.\nCopie de lecture : liens techniques/navigation retirés; capture de travail conservée localement. Ce fichier n’est pas un EML natif.\n\n'+text
    p.write_text(text,encoding='utf-8')
files=[]
details={
 '2025-07-01-Relocalisation-Jean-Talon.eml':('Courriel natif','1 juillet 2025, 15 h 17; Ooeuf vers Maude Robidoux'),
 'Invoice_1020_from_AKA_Moving.pdf':('Pièce jointe native PDF','11 juin 2025, 9 h 39; message msg-f:1834640111589325967'),
 '2025-08-20_Invoice_1026_from_AKA_Moving.pdf':('Pièce jointe native PDF','20 août 2025, 9 h 24'),
 '2025-08-27_0933_Invoice_1026_from_AKA_Moving.pdf':('Pièce jointe native PDF','27 août 2025, 9 h 33; message msg-f:1841615699350891713'),
 'Quadro_Holding_Lettre_UberEats_FR_Clean.pdf':('Pièce jointe native PDF','Échange du 16 juillet 2025 avec Benson Noisy; date imprimée 24 avril 2024'),
}
for name,(nature,source) in details.items():
 p=folder/name
 files.append(dict(fichier=name,nature=nature,source=source,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),octets=p.stat().st_size,controle_visuel_pages=list(range(1,4)) if 'Uber' in name else [1] if name.endswith('.pdf') else []))
data=dict(collecte='2026-10-24',compte='ooeuf.ca@gmail.com',methode='Interface Gmail connectée et téléchargement des pièces par les commandes de l’interface',sources=files,limites=['Recherches larges non exhaustives au-delà de la page observée.','PDF du message AKA du 27 août à 9 h 30 non téléchargé; PDF de 9 h 33 acquis.','Les extractions DOM publiques retirent les liens techniques. Les fichiers natifs ci-dessus ne sont pas modifiés.'],transmission=False)
(folder/'PROVENANCE-OOEUF-24.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources_natives':len(files),'extractions':len(list(folder.glob('*-dom.txt')))},ensure_ascii=False))
