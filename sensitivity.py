#!/usr/bin/env python3
"""Reproduce 5000 deterministic weight variations against the published SCORE_MATRIX.csv."""
from pathlib import Path
from collections import defaultdict
import csv
from decimal import Decimal

P=Path(__file__).resolve().parent

def read(path):
 with (P/path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

matrix=read('SCORE_MATRIX.csv')
admission=read('ADMISSION_REGISTER.csv')
vectors=read('SENSITIVITY_WEIGHTS_5000.csv')
archived=read('SENSITIVITY_RESULTS_5000.csv')
assert len(vectors)==len(archived)==5000
valid={x['candidate_id']:x['participant'] for x in admission if x['admission']=='ADMITTED_RESEARCH_SCENARIO'}
raw=defaultdict(dict)
for line in matrix:
 raw[line['candidate_id']][line['metric_id']]=Decimal(line['raw_score_0_2'])
assert len(valid)==14
for row,expected in zip(vectors,archived):
 weights={f'M{i:02d}':Decimal(row[f'weight_M{i:02d}']) for i in range(1,13)}
 assert abs(sum(weights.values())-Decimal('100'))<Decimal('0.000001')
 scores={name:sum((raw[id][key]*w/2 for key,w in weights.items()),Decimal('0')) for id,name in valid.items()}
 order=sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))
 leader,score=order[0]; other=max(x for name,x in order if name!='Ada Tours')
 gap=scores['Ada Tours']-other
 assert expected['leader']==leader=='Ada Tours'
 assert abs(Decimal(expected['ada_score'])-scores['Ada Tours'])<Decimal('0.00000001')
 assert abs(Decimal(expected['ada_minus_nearest'])-gap)<Decimal('0.00000001')
print('PASS: 5000 frozen weight vectors recomputed; Ada Tours leads 5000/5000.')
