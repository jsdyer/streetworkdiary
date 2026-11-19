from collections import defaultdict
from datetime import date, timedelta
from source import day, query, records, save

MAIN='Cityworks_Service_Requests/FeatureServer/0'
CUSTOM='Cityworks_Service_Requests_Custom_Fields/FeatureServer/0'
TYPES=('Street Surface Maintenance','ROW Litter','Graffiti')
def window(start,end):
    dates=f"DATE_INITIATED >= DATE '{start}' AND DATE_INITIATED < DATE '{end}'"
    types=' OR '.join(f"DESCRIPTION LIKE '{t}%'" for t in TYPES)
    fields='REQUEST_ID,DESCRIPTION,COMMUNITY,DATE_INITIATED,DATE_CLOSED,STATUS,RESOLUTION,WORK_ORDER'
    base=records(MAIN,dates+' AND ('+types+')',fields)
    if not base:raise ValueError('Empty street-service week')
    ids=sorted(r['REQUEST_ID'] for r in base)
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate request ID')
    marks=defaultdict(set)
    for start_at in range(0,len(ids),65):
        batch=ids[start_at:start_at+65]
        result=records(CUSTOM,'REQUESTID IN ('+','.join(map(str,batch))+')','REQUESTID,CUSTOM_FIELD_NAME')
        for row in result:
            marks[row['REQUESTID']].add((row['CUSTOM_FIELD_NAME'] or 'Unlabelled').strip())
    rows=[]
    for r in base:
        rid=r['REQUEST_ID']
        duration=None
        if r['DATE_CLOSED'] and r['DATE_CLOSED']>=r['DATE_INITIATED']:
            duration=round((r['DATE_CLOSED']-r['DATE_INITIATED'])/86400000,2)
        rows.append([rid,r['DESCRIPTION'].strip(),(r['COMMUNITY'] or 'Unspecified').strip(),day(r['DATE_INITIATED']),r['STATUS'],duration,bool(str(r['RESOLUTION'] or '').strip()),sorted(marks[rid]),r['WORK_ORDER']=='Y'])
    return {'start':str(start),'end':str(end-timedelta(days=1)),'rows':sorted(rows)}
def main():
    last=query(MAIN,where='1=1',outFields='DATE_INITIATED',returnGeometry='false',orderByFields='DATE_INITIATED DESC',resultRecordCount=1)
    latest=date.fromisoformat(day(last['features'][0]['attributes']['DATE_INITIATED']))
    end=latest-timedelta(days=latest.weekday())
    fixed=date(2025,4,1)
    periods=[window(fixed,fixed+timedelta(days=7)),window(end-timedelta(days=7),end)]
    if periods[0]['start']==periods[1]['start']:periods=periods[:1]
    save('requests.json',count=sum(len(p['rows']) for p in periods),sourceThrough=str(latest),periods=periods)
if __name__=='__main__':main()
