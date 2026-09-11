"""Consolidate tested residuals without deleting repeated model membership."""
import json
from analysis_data import tsv,jsonlines,write_tsv,load_annotations

def main():
    out=[]
    for file,keep in [
      ('old-long-screen-residuals.tsv',lambda r:True),
      ('old-long-nominal-residuals.tsv',lambda r:True),
      ('palula-short-a-pairs.tsv',lambda r:r['status']!='consistent'),
      ('palula-umlaut-i-nouns.tsv',lambda r:r['status']!='consistent'),
      ('palula-i-decl-extension.tsv',lambda r:r['status']!='consistent'),
      ('vowel-raising-reviewed.tsv',lambda r:r['status']=='other-quality'),
      ('kalkoti-palula-combined.tsv',lambda r:r['status'] in ['residual','Low-interaction','conflicting']),
      ('kundal-primary-paradigms.tsv',lambda r:r['table']=='12'),
      ('dras-suffix-accent-review.tsv',lambda r:r['suffix'] in ['-eh','-eɦ','-eh/-eɦ'] and r['final_vowel_accented']=='0'),
    ]:
        for i,r in enumerate(tsv(file),2):
            if not keep(r):continue
            out.append(dict(ledger_id='R'+str(len(out)+1).zfill(3),source_table=file,source_row=i,
              family_id=r.get('family_id',r.get('family_ids','')),record_id=r.get('record_id',r.get('record_ids',r.get('plural_id',''))),
              language=r.get('language','Kalk/Phal' if file.startswith('kalkoti') else 'Kund' if file.startswith('kundal') else 'Sh:Dras' if file.startswith('dras') else 'Phal'),
              status=r.get('status',r.get('observed_pattern',r.get('suffix_accent_status','residual'))),
              explanation=r.get('analysis',r.get('explanation',r.get('explanations',r.get('adjudication',r.get('manual_lexical_note',''))))),
              unresolved=r.get('unresolved',''),full_evidence=r))
    for pattern in ['adjective_residuals*.jsonl','property_residuals*.jsonl']:
        for r,loc in jsonlines(pattern):
            out.append(dict(ledger_id='R'+str(len(out)+1).zfill(3),source_table=loc,source_row='',family_id=r.get('family_id',''),
              record_id=r.get('record_id',r.get('record_ids',[])),language=r.get('language','see record'),status=r.get('status','manually-reviewed-location-residual'),
              explanation=r.get('analysis',r.get('basis','')),unresolved=r.get('unresolved',''),full_evidence=r))
    write_tsv('exception-ledger.tsv',out)
    editorial=[]
    for pattern in ['record_decisions*.jsonl','formation_decisions*.jsonl','source_observations*.jsonl']:
        for r,loc in jsonlines(pattern):editorial.append(dict(locator=loc,kind=pattern,record_ids=r.get('record_ids',[r.get('record_id')]),family_id=r.get('family_id',r.get('research_family_id',r.get('research_family',''))),decision=r))
    write_tsv('editorial-and-source-decisions.tsv',editorial)
    write_tsv('all-family-open-issues.tsv',({'family_id':fid,'formation':r['formation'],'analysis':r['analysis'],'open_issue':r.get('unresolved',''),'status':r['status']} for fid,r in load_annotations().items() if r.get('unresolved')))
    print(len(out),'model residual appearances;',len(editorial),'editorial/source decisions')
if __name__=='__main__':main()
