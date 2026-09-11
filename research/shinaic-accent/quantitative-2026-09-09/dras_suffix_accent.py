"""Count explicit suffix accent without discarding double-marked Dras words."""
import json
from collections import Counter,defaultdict
from analysis_data import tsv,write_tsv
from phonology import clusters,VOWELS

def main():
    rr=tsv('dras-paradigm-review.tsv');out=[]
    for r in rr:
        vowels=[c for c in clusters(r['plural']) if c[0] in VOWELS]
        final=bool(vowels and '\u0301' in vowels[-1]);n=sum('\u0301' in c for c in vowels)
        status='final-plus-other-accent' if final and n>1 else 'final-accent-only' if final else 'stem-accent-only' if n else 'unmarked'
        out.append({**r,'final_vowel_accented':int(final),'acute_count':n,'suffix_accent_status':status})
    write_tsv('dras-suffix-accent-review.tsv',out)
    summary=[]
    for s in ['-eh/-eɦ','-e','-i','other']:
        xs=[r for r in out if r['suffix']==s]
        summary.append(dict(suffix=s,plural_citations=len(xs),with_final_accent=sum(r['final_vowel_accented'] for r in xs),
                            statuses=dict(Counter(r['suffix_accent_status'] for r in xs))))
    write_tsv('dras-suffix-accent-summary.tsv',summary)
    for r in summary:print(r)
if __name__=='__main__':main()
