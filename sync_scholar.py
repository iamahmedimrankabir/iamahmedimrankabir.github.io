"""Fetch Scholar author metrics and all listed papers through SerpApi.
No external dependencies. Fails safely without overwriting last good data.
"""
import json, os, pathlib, urllib.parse, urllib.request, datetime, time

AUTHOR_ID = '1OWW__EAAAAJ'
DEST = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'scholar.json'
KEY = os.environ.get('SERPAPI_KEY')
if not KEY:
    raise SystemExit('SERPAPI_KEY secret is missing. Existing data is preserved.')

def request(params):
    params = {'engine':'google_scholar_author','author_id':AUTHOR_ID,'api_key':KEY,**params}
    url = 'https://serpapi.com/search.json?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AcademicPortfolioSync/1.0'}),timeout=45) as response:
        data = json.load(response)
    if data.get('error'):
        raise RuntimeError('Scholar provider error: '+str(data['error']))
    return data

first = request({'num':100,'start':0})
counts = first.get('cited_by', {}).get('table', [])
metrics = {}
for item in counts:
    name = str(item.get('citations',{}).get('all',''))
    # SerpApi table normally contains row identifiers: citations, h_index, i10_index.
    key = item.get('name') or item.get('key') or item.get('title') or ''
    if not key and isinstance(item.get('citations'),dict):
        key = item.get('citations',{}).get('name','')
    if key:
        metrics[str(key).lower().replace('-','_').replace(' ','_')] = item.get('citations',{}).get('all')
# SerpApi author response also commonly returns these metrics in cited_by.table as
# [{"citations": {"all": 123}}, {"h_index": {"all": 10}}, ...].
for row in counts:
    for key in ('citations','h_index','i10_index'):
        if key in row and isinstance(row[key],dict) and 'all' in row[key]:
            metrics[key] = row[key]['all']

def number(v):
    if isinstance(v,dict): v=v.get('all')
    try: return int(str(v).replace(',',''))
    except (ValueError,TypeError): return None

articles=[]
for start in range(0,2000,100):
    page = first if start==0 else request({'num':100,'start':start})
    batch=page.get('articles',[])
    if not isinstance(batch,list):raise RuntimeError('Unexpected Scholar articles payload')
    for a in batch:
        cited=a.get('cited_by') or {}
        articles.append({'title':a.get('title',''),'year':a.get('year'),
          'authors':a.get('authors',''),'publication':a.get('publication',''),
          'link':a.get('link') or ('https://scholar.google.com/citations?view_op=view_citation&hl=en&user='+AUTHOR_ID+'&citation_for_view='+urllib.parse.quote(str(a.get('citation_id','')))),
          'cited_by':number(cited.get('value'))})
    if len(batch)<100:break
    time.sleep(1)
else:raise RuntimeError('Pagination limit reached; refusing incomplete update')
if not articles:raise RuntimeError('No publications returned; preserving previous data')
# Reject missing metric values instead of silently publishing incorrect zeroes.
values={k:number(metrics.get(k)) for k in ('citations','h_index','i10_index')}
if any(v is None for v in values.values()):
    raise RuntimeError('Incomplete metrics from Scholar provider: '+str(metrics))
output={'last_updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),**values,'publications':articles}
tmp=DEST.with_suffix('.tmp')
tmp.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tmp.replace(DEST)
print('Updated',len(articles),'Scholar publications; metrics:',values)
