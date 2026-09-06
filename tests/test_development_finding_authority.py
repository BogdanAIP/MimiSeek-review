from __future__ import annotations
import importlib.util,hashlib,json
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'tools'/'verify_development_finding_authority.py'
s=importlib.util.spec_from_file_location('a',P); a=importlib.util.module_from_spec(s); s.loader.exec_module(a)
class T(unittest.TestCase):
 def rec(self):
  body='finding'; return {'adjudication_id':'DFA-1','repository':a.REPO,'pr':21,'head_sha':'a'*40,'evidence_locator':'review_comment:1','disposition':'CONFIRMED','claim':'c','basis':'b','source_type':'REVIEW_COMMENT','source_author_login':'bot','source_updated_at':'2026-01-01T00:00:00Z','source_body_sha256':hashlib.sha256(body.encode()).hexdigest()},body
 def test_ledger_claim_bound(self):
  r,_=self.rec(); l={k:r[k] for k in ('adjudication_id','repository','pr','head_sha','evidence_locator','disposition','claim','basis')}; l['claim']='negated'
  with self.assertRaises(a.E): a.bind_ledger([l],[r])
 def test_source_body_head_pr_bound(self):
  r,b=self.rec(); p={'id':1,'pull_request_url':f'https://api.github.com/repos/{a.REPO}/pulls/21','original_commit_id':'a'*40,'user':{'login':'bot'},'updated_at':r['source_updated_at'],'body':b}; a.source_review(r,lambda _:p)
  for f,v in [('original_commit_id','b'*40),('updated_at','2026-01-01T00:00:01Z'),('body','edited')]:
   q=dict(p); q[f]=v
   with self.assertRaises(a.E): a.source_review(r,lambda _:q)
 def test_occurrence_requires_explicit_kind_and_confirmation(self):
  p=[{'pattern_id':'DFP-1','origin':{'source_kind':'REVIEW_FINDING'},'occurrences':[{'occurrence_id':'O1','relation':'ORIGIN','pr':21,'head_sha':'a'*40,'evidence_locator':'review_comment:1'}]}]
  with self.assertRaises(a.E): a.occurrence_authority(p,{}, {},lambda _: {})
  src={('DFP-1','O1'):'REVIEW_FINDING'}
  with self.assertRaises(a.E): a.occurrence_authority(p,src,{},lambda _: {})
  adj={(a.REPO,21,'a'*40,'review_comment:1'):{'disposition':'CONFIRMED'}}; a.occurrence_authority(p,src,adj,lambda _: {})
 def test_ambiguous_transport_rejected(self):
  p=[{'pattern_id':'D','origin':{'source_kind':'REVIEW_FINDING'},'occurrences':[{'occurrence_id':'O','relation':'ORIGIN','pr':21,'head_sha':'a'*40,'evidence_locator':'issue_comment:9'}]}]
  with self.assertRaises(a.E): a.occurrence_authority(p,{('D','O'):'REVIEW_FINDING'}, {},lambda _: {})
if __name__=='__main__': unittest.main()
