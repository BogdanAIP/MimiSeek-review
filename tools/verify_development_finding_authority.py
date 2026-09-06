#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,subprocess,urllib.request
from pathlib import Path
REPO='BogdanAIP/MimiSeek-review'; PR=21
LEDGER='data/development-finding-adjudications.jsonl'; PATTERNS='data/development-failure-patterns.jsonl'; SOURCES='data/development-occurrence-sources.jsonl'
FINDING=(5558483395,'2026-09-06T10:00:17Z','89d402bfc7af9087440dfd33a9d68158f9fefbed6d58b8b386803be728c564ea','DEVELOPMENT_FINDING_ADJUDICATION_MANIFEST_V2\n')
SUPPLEMENT=(5558687674,'2026-09-06T10:42:38Z','07fb1ebabc7792083d5088ab7001621aadd1892998909d54b209857e7412aa11','DEVELOPMENT_FINDING_ADJUDICATION_SUPPLEMENT_V1\n')
PROCESS=(5559836346,'2026-09-06T14:20:19Z','2b164e3e9c46c69b6c4349569260a385d3893ba356e14352befd9e72559f1659','DEVELOPMENT_PROCESS_INCIDENT_BINDING_MANIFEST_V2\n')
REVIEW=re.compile(r'^review_comment:([1-9][0-9]*)$'); PRC=re.compile(r'^pr_comment:([1-9][0-9]*)$'); SHA=re.compile(r'^[0-9a-f]{40}$')
class E(RuntimeError): pass
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def show(root,p):
 try:b=subprocess.run(['git','-C',str(root),'show',f'HEAD:{p}'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 except Exception as x: raise E(f'missing exact-HEAD file: {p}') from x
 try:return b.decode()
 except UnicodeDecodeError as x: raise E(f'non-UTF8 exact-HEAD file: {p}') from x
def jsonl(root,p):
 out=[]
 for n,line in enumerate(show(root,p).splitlines(),1):
  if not line.strip(): continue
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
  q=urllib.request.Request(api+path,headers={'Accept':'application/vnd.github+json','Authorization':f'Bearer {token}','X-GitHub-Api-Version':'2022-11-28'})
  try:
   with urllib.request.urlopen(q,timeout=20) as r:return json.load(r)
  except Exception as x: raise E(f'GitHub evidence resolution failed: {path}') from x
 return get
def bound_comment(get,spec):
 cid,updated,digest,mark=spec; p=get(f'/repos/{REPO}/issues/comments/{cid}'); body=p.get('body')
 if p.get('id')!=cid or not str(p.get('issue_url','')).endswith(f'/repos/{REPO}/issues/{PR}'): raise E(f'comment {cid}: PR identity differs')
 if (p.get('user') or {}).get('login')!='BogdanAIP' or p.get('updated_at')!=updated: raise E(f'comment {cid}: actor/update differs')
 if not isinstance(body,str) or h(body)!=digest or not body.startswith(mark): raise E(f'comment {cid}: body binding differs')
 return body
def one_line_manifest(get,spec,schema,extra):
 body=bound_comment(get,spec); lines=body.splitlines()
 if len(lines)<2: raise E(f'{schema}: payload missing')
 try:m=json.loads(lines[1])
 except json.JSONDecodeError as x: raise E(f'{schema}: JSON invalid') from x
 if not isinstance(m,dict) or m.get('schema_version')!=schema or m.get('repository')!=REPO: raise E(f'{schema}: semantics differ')
 for k,v in extra.items():
  if m.get(k)!=v: raise E(f'{schema}: {k} differs')
 rows=m.get('records')
 if not isinstance(rows,list) or not rows: raise E(f'{schema}: records missing')
 return rows
def finding_manifest(get):
 body=bound_comment(get,FINDING)
 try:m=json.loads(body[len(FINDING[3]):])
 except json.JSONDecodeError as x: raise E('finding manifest JSON invalid') from x
 if not isinstance(m,dict) or m.get('schema_version')!='DEVELOPMENT_FINDING_ADJUDICATION_MANIFEST_V2' or m.get('repository')!=REPO or m.get('adjudication_pr')!=PR or m.get('adjudicator_role')!='development_workflow': raise E('finding manifest semantics differ')
 rows=m.get('records')
 if not isinstance(rows,list) or not rows: raise E('finding manifest records missing')
 return rows
def supplement_manifest(get): return one_line_manifest(get,SUPPLEMENT,'DEVELOPMENT_FINDING_ADJUDICATION_SUPPLEMENT_V1',{'adjudication_pr':PR,'adjudicator_role':'development_workflow'})
def process_manifest(get): return one_line_manifest(get,PROCESS,'DEVELOPMENT_PROCESS_INCIDENT_BINDING_MANIFEST_V2',{'authority_pr':PR})
def key(r): return (r.get('repository'),r.get('pr'),r.get('head_sha'),r.get('evidence_locator'))
def bind_ledger(ledger,records):
 fields=('repository','pr','head_sha','evidence_locator','disposition','claim','basis'); byid={r.get('adjudication_id'):r for r in records}
 if len(byid)!=len(records) or len(ledger)!=len(records): raise E('ledger/manifest cardinality differs')
 out={}
 for row in ledger:
  if row.get('schema_version')!='DEVELOPMENT_FINDING_ADJUDICATION_V1': raise E('ledger schema identity differs')
  aid=row.get('adjudication_id'); r=byid.get(aid)
  if r is None: raise E(f'{aid}: absent from external manifest')
  for f in fields:
   if row.get(f)!=r.get(f): raise E(f'{aid}: ledger/manifest {f} mismatch')
  k=key(row)
  if k in out: raise E('duplicate adjudication target')
  out[k]=r
 return out
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
  if set(r)!={'pattern_id','occurrence_id','source_kind'} or r.get('source_kind') not in {'REVIEW_FINDING','PROCESS_INCIDENT'}: raise E('occurrence source row invalid')
  k=(r.get('pattern_id'),r.get('occurrence_id'))
  if not all(isinstance(x,str) and x for x in k) or k in out: raise E('occurrence source identity invalid or duplicate')
  out[k]=r.get('source_kind')
 return out
def bind_process_incidents(records,get):
 out={}; rf={'source_comment_id','source_pr','source_author_login','source_updated_at','source_body_sha256','pattern_id','failure_class','occurrences'}; of={'occurrence_id','head_sha','relation','prevention_failure_reason'}
 for n,r in enumerate(records,1):
  label=f'process manifest record {n}'
  if not isinstance(r,dict) or set(r)!=rf: raise E(f'{label}: shape differs')
  cid=r.get('source_comment_id'); source_pr=r.get('source_pr')
  if not isinstance(cid,int) or isinstance(cid,bool) or cid<1 or not isinstance(source_pr,int) or isinstance(source_pr,bool) or source_pr<1: raise E(f'{label}: source identity invalid')
  p=get(f'/repos/{REPO}/issues/comments/{cid}'); parent=get(f'/repos/{REPO}/pulls/{source_pr}'); body=p.get('body')
  if p.get('id')!=cid or not str(p.get('issue_url','')).endswith(f'/repos/{REPO}/issues/{source_pr}'): raise E(f'{label}: source comment identity differs')
  if not isinstance(parent,dict) or parent.get('number')!=source_pr: raise E(f'{label}: source PR identity differs')
  if (p.get('user') or {}).get('login')!=r.get('source_author_login') or p.get('updated_at')!=r.get('source_updated_at'): raise E(f'{label}: source actor/update differs')
  if not isinstance(body,str) or h(body)!=r.get('source_body_sha256'): raise E(f'{label}: source body digest differs')
  pid=r.get('pattern_id'); fc=r.get('failure_class'); occs=r.get('occurrences')
  if not isinstance(pid,str) or not pid or not isinstance(fc,str) or not fc or fc not in body or not isinstance(occs,list) or not occs: raise E(f'{label}: claim binding invalid')
  for o in occs:
   if not isinstance(o,dict) or set(o)!=of or not isinstance(o.get('occurrence_id'),str) or not SHA.fullmatch(str(o.get('head_sha',''))) or o.get('head_sha') not in body: raise E(f'{label}: occurrence binding invalid')
   k=(pid,o.get('occurrence_id'))
   if k in out: raise E('duplicate process-incident occurrence binding')
   out[k]={'source_comment_id':cid,'failure_class':fc,'pr':source_pr,**o}
 return out
def occurrence_authority(patterns,src,adjudications,process_bindings):
 seen=set(); seen_process=set()
 for p in patterns:
  pid=p.get('pattern_id'); fc=p.get('failure_class'); origin=p.get('origin') or {}
  for o in p.get('occurrences') or []:
   oid=o.get('occurrence_id'); k=(pid,oid); seen.add(k); kind=src.get(k); loc=o.get('evidence_locator'); pr=o.get('pr'); head=o.get('head_sha')
   if kind is None: raise E(f'{pid}/{oid}: missing explicit source_kind')
   if o.get('relation')=='ORIGIN' and kind!=origin.get('source_kind'): raise E(f'{pid}/{oid}: source_kind differs from origin')
   if kind=='REVIEW_FINDING':
    if not REVIEW.fullmatch(str(loc)): raise E(f'{pid}/{oid}: REVIEW_FINDING requires review_comment')
    a=adjudications.get((REPO,pr,head,loc))
    if a is None or a.get('disposition')!='CONFIRMED': raise E(f'{pid}/{oid}: lacks externally bound CONFIRMED adjudication')
   else:
    m=PRC.fullmatch(str(loc)); b=process_bindings.get(k)
    if not m or b is None: raise E(f'{pid}/{oid}: lacks exact process-incident binding')
    if b.get('source_comment_id')!=int(m.group(1)) or b.get('failure_class')!=fc: raise E(f'{pid}/{oid}: process-incident claim differs')
    for f in ('pr','head_sha','relation','prevention_failure_reason'):
     if b.get(f)!=o.get(f): raise E(f'{pid}/{oid}: process-incident {f} differs')
    seen_process.add(k)
 if seen!=set(src): raise E('occurrence source registry has extra/missing rows')
 if seen_process!=set(process_bindings): raise E('process-incident manifest has extra/missing occurrence bindings')
def verify(root,get):
 ledger=jsonl(root,LEDGER); pats=jsonl(root,PATTERNS); src=sources(jsonl(root,SOURCES)); recs=finding_manifest(get)+supplement_manifest(get); adj=bind_ledger(ledger,recs)
 for r in recs: source_review(r,get)
 occurrence_authority(pats,src,adj,bind_process_incidents(process_manifest(get),get))
def main():
 root=Path(__file__).resolve().parents[1]
 try: verify(root,fetcher())
 except (E,OSError,json.JSONDecodeError) as x: print(f'development finding authority verification failed: {x}'); return 1
 print(f'development finding authority verified: finding_manifest_comment={FINDING[0]} finding_supplement_comment={SUPPLEMENT[0]} process_manifest_comment={PROCESS[0]}'); return 0
if __name__=='__main__': raise SystemExit(main())
