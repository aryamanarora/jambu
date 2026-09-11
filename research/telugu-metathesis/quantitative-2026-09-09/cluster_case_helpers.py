"""Compact authoring interface; all inputs and outcomes are manually specified."""
def case(add,tokens,id,concept,recon,c1,v1,c2,v2,shape,pos,support,direction,history,exceptions,evidence,*,quantity='short',structure='singleton',boundary='Exact formative correspondence discussed in derivation; not inferred from output.',eligibility='core',confidence='medium',family=None,refs=''):
    outcomes={};groups={}
    for lang,code,words,note in evidence:
        groups.setdefault(lang,[]).append((code,words,note))
    for lang,rows in groups.items():
        codes={r[0] for r in rows}
        top='M' if {'D','R'}<=codes else 'A' if 'A' in codes else 'O' if 'O' in codes else 'B' if 'B' in codes else next(iter(codes))
        outcomes[lang]=(top,'|'.join(r[1] for r in rows),' '.join(r[2] for r in rows))
    add(id,concept,recon,c1,v1,c2,v2,shape,pos,support,direction,history,exceptions,outcomes,
        quantity=quantity,c2_structure=structure,boundary=boundary,eligibility=eligibility,confidence=confidence,family=family,
        references='DEDR '+id[1:]+'; current comparative cluster panel'+('; '+refs if refs else ''),
        input_confidence='Comparative order and exact formation confidence distinguished in support and exception notes')
    for lang,rows in groups.items():
        if len({r[0] for r in rows})>1:
            combined={}
            for code,words,note in rows:combined.setdefault(code,[]).append(words)
            tokens(id,lang,**{code:'|'.join(words) for code,words in combined.items()})
