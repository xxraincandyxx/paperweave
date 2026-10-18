from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading,uuid,json
from fastapi import FastAPI,UploadFile,HTTPException,Request
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from .config import ROOT,Settings
from .pipeline import run
from .render import STATIC

app=FastAPI(title='研脉 PaperWeave')
app.mount('/assets',StaticFiles(directory=STATIC),name='assets')
jobs={}
lock=threading.Lock()
executor=ThreadPoolExecutor(max_workers=1)

@app.middleware('http')
async def local_only(request:Request,call_next):
    # Bind loopback and reject foreign browser origins / DNS rebinding hosts.
    host=request.headers.get('host','').split(':')[0]
    origin=request.headers.get('origin','')
    if host not in {'127.0.0.1','localhost','testserver'}:
        return HTMLResponse('仅支持本机访问',status_code=403)
    if request.method!='GET' and origin and origin not in {'http://'+request.headers.get('host','')}:
        return HTMLResponse('不接受跨站请求',status_code=403)
    return await call_next(request)

@app.get('/')
def index():
    return FileResponse(STATIC/'index.html')

@app.get('/api/config')
def config():
    try:
        cfg=Settings.load(); cfg.validate()
        return {'ready':True,'model':cfg.model}
    except Exception as exc:
        return {'ready':False,'message':str(exc)}

@app.post('/api/jobs')
async def create_job(file:UploadFile):
    try:
        cfg=Settings.load(); cfg.validate()
    except Exception as exc:
        raise HTTPException(400,str(exc)) from None
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400,'请上传 .pdf 文件')
    with lock:
        if sum(j['state'] in {'queued','running'} for j in jobs.values())>=3:
            raise HTTPException(429,'已有三个任务排队，请稍后再试。')
        job_id=uuid.uuid4().hex
        jobs[job_id]={'id':job_id,'state':'queued','progress':0,'message':'等待上传'}
    job_dir=ROOT/'outputs'/'runs'/job_id
    job_dir.mkdir(parents=True)
    input_pdf=job_dir/'input.pdf'
    total=0
    try:
        with input_pdf.open('wb') as f:
            while chunk:=await file.read(1024*1024):
                total+=len(chunk)
                if total>80*1024*1024: raise HTTPException(413,'文件超过 80 MB')
                f.write(chunk)
        with input_pdf.open('rb') as f: header=f.read(1024)
        if b'%PDF-' not in header: raise HTTPException(400,'不是有效的 PDF 文件')
    except Exception:
        jobs[job_id].update(state='failed',message='上传失败')
        input_pdf.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    def work():
        def update(message,pct):
            with lock: jobs[job_id].update(state='running',message=message,progress=pct)
        try:
            run(input_pdf,job_dir,cfg,update)
            with lock: jobs[job_id].update(state='done',progress=100,message='离线看板已生成',url=f'/api/jobs/{job_id}/files/dashboard.html')
        except Exception as exc:
            with lock: jobs[job_id].update(state='failed',message=str(exc))
    executor.submit(work)
    return {'id':job_id}

@app.get('/api/jobs/{job_id}')
def status(job_id:str):
    with lock:
        if job_id not in jobs: raise HTTPException(404,'找不到任务；服务重启后请直接查看 outputs/runs 中保存的结果。')
        return dict(jobs[job_id])

@app.get('/api/jobs/{job_id}/files/{filename}')
def result_file(job_id:str,filename:str):
    allowed={'dashboard.html','mindmap.mmd','flowchart.mmd','analysis.json','extracted.json','extracted.md','chunk_report.json'}
    if len(job_id)!=32 or any(c not in '0123456789abcdef' for c in job_id) or filename not in allowed:
        raise HTTPException(404,'文件不存在')
    path=ROOT/'outputs'/'runs'/job_id/filename
    if not path.is_file(): raise HTTPException(404,'结果尚未生成')
    return FileResponse(path)
