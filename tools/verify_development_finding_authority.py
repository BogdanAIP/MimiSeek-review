#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,subprocess,urllib.request,urllib.error
from pathlib import Path

REPO='BogdanAIP/MimiSeek-review'; PR=21
LEDGER='data/development-finding-adjudications.jsonl'; PATTERNS='data/development-failure-patterns.jsonl'
SOURCES='data/development-occurrence-sources.jsonl'
MANIFEST_ID=5558483395; MANIFEST_UPDATED='2026-09-06T10:00:17Z'
MANIFEST_SHA='89d402bfc7af9087440dfd33a9d68158f9fefbed6d58b8b386803be728c564ea'
MARK='DEVELOPMENT_FINDING_ADJUDICATION_MANIFEST_V2\n'
REVIEW=re.compile(r'^review_comment:([1-9][0-9]*)$'); PRC=re.compile(r'^pr_comment:([1-9][0-9]*)$')
class E(RuntimeError): pass

def h(s): return hashlib.sha256(s.encode()).hexdigest()
def show(root,p):
    try: b=subprocess.run(['git','-C',str(root),'show',f'HEAD:{p}'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    except Exception as x: raise E(f'missing exact-HEAD file: {p}') from x
    try:return b.decode()
    except UnicodeDecodeError as x: raise E(f'non-UTF8 exact-HEAD file: {p}') from x
def jsonl(root,p):
    out=[]
    for n,line in enumerate(show(root,p).splitlines(),1):
        if line.strip():
            try:v=json.loads(line)
            except json.JSONDecodeError as x: raise E(f'{p}:{n}: invalid JSON') from x
            if not isinstance(v,dict): raise E(f'{p}:{n}: row must be object')
            out.append(v)
    if not out: raise E(f'{p}: empty')
    return out

def fetcher():
    api=os.getenv('GITHUB_API_URL','https://api.github.com').rstrip('/'); token=os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if os.getenv('GITHUB_REPOSITORY',REPO)!=REPO or not token: raise E('live authority verification requires MimiSeek GH token')
    def get(path):
        req=urllib.request.Request(api+path,headers={'Accept':'application/vnd.github+json','Authorization':f'Bearer {token}','X-GitHub-Api-Version':'2022-11-28'})
        try:
            with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
        except Exception as x: raise E(f'GitHub evidence resolution failed: {path}') from x
    return get

def manifest(get):
    p=get(f'/repos/{REPO}/issues/comments/{MANIFEST_ID}'); body=p.get('body')
    if p.get('id')!=MANIFEST_ID or not str(p.get('issue_url','')).endswith(f'/repos/{REPO}/issues/{PR}'): raise E('manifest PR identity differs')
    if (p.get('user') or {}).get('login')!='BogdanAIP' or p.get('updated_at')!=MANIFEST_UPDATED: raise E('manifest actor/update identity differs')
    if not isinstance(body,str) or h(body)!=MANIFEST_SHA or not body.startswith(MARK): raise E('manifest body binding differs')
    try:m=json.loads(body[len(MARK):])
    except json.JSONDecodeError as x: raise E('manifest JSON invalid') from x
    if m.get('schema_version')!='DEVELOPMENT_FINDING_ADJUDICATION_MANIFEST_V2' or m.get('repository')!=REPO or m.get('adjudication_pr')!=PR or m.get('adjudicator_role')!='development_workflow': raise E('manifest semantics differ')
    rows=m.get('records');
    if not isinstance(rows,list) or not rows: raise E('manifest records missing')
    return rows

def key(r): return (r.get('repository'),r.get('pr'),r.get('head_sha'),r.get('evidence_locator'))
def bind_ledger(ledger, records):
    fields=('repository','pr','head_sha','evidence_locator','disposition','claim','basis')
    byid={r.get('adjudication_id'):r for r in records}
    if len(byid)!=len(records) or len(ledger)!=len(records): raise E('ledger/manifest cardinality differs')
    bound={}
    for row in ledger:
        aid=row.get('adjudication_id'); r=byid.get(aid)
        if r is None: raise E(f'{aid}: absent from external manifest')
        for f in fields:
            if row.get(f)!=r.get(f): raise E(f'{aid}: ledger/manifest {f} mismatch')
        k=key(row)
        if k in bound: raise E('duplicate adjudication target')
        bound[k]=r
    return bound

def source_review(r,get):
    m=REVIEW.fullmatch(str(r.get('evidence_locator','')))
    if r.get('source_type')!='REVIEW_COMMENT' or not m: raise E(f"{r.get('adjudication_id')}: source type/locator differs")
    p=get(f'/repos/{REPO}/pulls/comments/{m.group(1)}'); body=p.get('body')
    if p.get('id')!=int(m.group(1)) or not str(p.get('pull_request_url','')).endswith(f"/repos/{REPO}/pulls/{r.get('pr')}"): raise E('source review repo/PR differs')
    if p.get('original_commit_id')!=r.get('head_sha'): raise E('source review original commit differs')
    if (p.get('user') or {}).get('login')!=r.get('source_author_login') or p.get('updated_at')!=r.get('source_updated_at'): raise E('source review actor/update differs')
    if not isinstance(body,str) or h(body)!=r.get('source_body_sha256'): raise E('source review body digest differs')

def sources(rows):
    out={}
    for r in rows:
        exact={'pattern_id','occurrence_id','source_kind'}
        if set(r)!=exact or r.get('source_kind') not in {'REVIEW_FINDING','PROCESS_INCIDENT'}: raise E('occurrence source row invalid')
        k=(r.get('pattern_id'),r.get('occurrence_id'))
        if k in out: raise E('duplicate occurrence source row')
        out[k]=r.get('source_kind')
    return out

def occurrence_authority(patterns, src, adjudications, get):
    seen=set()
    for p in patterns:
        pid=p.get('pattern_id'); origin=p.get('origin') or {}
        for o in p.get('occurrences') or []:
            oid=o.get('occurrence_id'); k=(pid,oid); seen.add(k); kind=src.get(k)
            if kind is None: raise E(f'{pid}/{oid}: missing explicit source_kind')
            loc=o.get('evidence_locator'); pr=o.get('pr'); head=o.get('head_sha')
            if o.get('relation')=='ORIGIN' and kind!=origin.get('source_kind'): raise E(f'{pid}/{oid}: source_kind differs from origin')
            if kind=='REVIEW_FINDING':
                if not REVIEW.fullmatch(str(loc)): raise E(f'{pid}/{oid}: REVIEW_FINDING requires review_comment')
                a=adjudications.get((REPO,pr,head,loc))
                if a is None or a.get('disposition')!='CONFIRMED': raise E(f'{pid}/{oid}: lacks externally bound CONFIRMED adjudication')
            else:
                m=PRC.fullmatch(str(loc))
                if not m: raise E(f'{pid}/{oid}: PROCESS_INCIDENT requires pr_comment')
                q=get(f'/repos/{REPO}/issues/comments/{m.group(1)}'); body=q.get('body')
                if q.get('id')!=int(m.group(1)) or not str(q.get('issue_url','')).endswith(f'/repos/{REPO}/issues/{pr}'): raise E('process incident PR differs')
                if (q.get('user') or {}).get('login')!='BogdanAIP' or not isinstance(body,str) or 'PROCESS_INCIDENT' not in body or head not in body: raise E('process incident class/head binding differs')
    if seen!=set(src): raise E('occurrence source registry has extra/missing rows')

def verify(root,get):
    ledger=jsonl(root,LEDGER); pats=jsonl(root,PATTERNS); src=sources(jsonl(root,SOURCES)); recs=manifest(get)
    adj=bind_ledger(ledger,recs)
    for r in recs: source_review(r,get)
    occurrence_authority(pats,src,adj,get)

def main():
    root=Path(__file__).resolve().parents[1]
    try: verify(root,fetcher())
    except (E,OSError,json.JSONDecodeError) as x:
        print(f'development finding authority verification failed: {x}'); return 1
    print(f'development finding authority verified: manifest_comment={MANIFEST_ID}'); return 0
if __name__=='__main__': raise SystemExit(main())
