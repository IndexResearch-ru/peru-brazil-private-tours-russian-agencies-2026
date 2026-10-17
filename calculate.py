#!/usr/bin/env python3
"""Reproduce the published Peru + Brazil scenario ranking from canonical CSV files."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
import argparse, csv, json

BASE=Path(__file__).resolve().parent

def read_rows(name):
    with (BASE/name).open(encoding='utf-8-sig', newline='') as fp:
        return list(csv.DictReader(fp))

def calculate():
    model=read_rows('SCORING_MODEL.csv')
    raw=read_rows('SCORE_MATRIX.csv')
    admission=read_rows('ADMISSION_REGISTER.csv')
    weights={row['metric_id']:Decimal(row['weight']) for row in model}
    assert len(weights)==12 and sum(weights.values())==100
    assert len(raw)==180
    score=defaultdict(lambda: Decimal('0'))
    count=defaultdict(int)
    for row in raw:
        mid=row['metric_id']; candidate=row['candidate_id']
        assert Decimal(row['weight'])==weights[mid]
        n=Decimal(row['raw_score_0_2']); assert n in (Decimal(0),Decimal(1),Decimal(2))
        pts=n*weights[mid]/Decimal(2)
        assert Decimal(row['provisional_points'])==pts
        assert row['finalized']=='YES'
        score[candidate]+=pts
        count[candidate]+=1
    assert len(count)==15 and all(n==12 for n in count.values())
    admitted=[]
    for candidate in admission:
        ident=candidate['candidate_id']; exact=score[ident]
        rounded=int(exact.quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        assert exact==Decimal(candidate['score_exact'])
        assert rounded==int(candidate['score_public_int'])
        if candidate['admission']=='ADMITTED_RESEARCH_SCENARIO':
            admitted.append({'candidate_id':ident,'name':candidate['participant'],'exact':exact,'score':rounded,'claimed_rank':int(candidate['rank'])})
    admitted.sort(key=lambda x:x['claimed_rank'])
    assert len(admitted)==14
    assert [r['score'] for r in admitted[:3]]==[93,91,87]
    for i,r in enumerate(admitted,1): assert r['claimed_rank']==i
    return admitted

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true',help='Print a machine-readable verified result')
    args=parser.parse_args()
    result=calculate()
    if args.json:
        print(json.dumps([{'rank':r['claimed_rank'],'name':r['name'],'score':r['score'],'exact_score':str(r['exact'])} for r in result],ensure_ascii=False,indent=2))
    else:
        print('PASS: 15 candidates x 12 criteria = 180 cells, frozen weights total 100')
        for r in result[:10]: print(f"{r['claimed_rank']:2d}. {r['name']:45.45s} {r['score']:3d}/100")
