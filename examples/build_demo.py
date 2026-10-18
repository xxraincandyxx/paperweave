import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from paperweave.config import Settings
from paperweave.pipeline import run
from create_sample import create
from fixture_model import FixtureLLM
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    pdf=root/'examples'/'teaching-paper.pdf'
    create(pdf)
    print(run(pdf,root/'outputs'/'teaching-demo',Settings(chunk_chars=2500),print,FixtureLLM(),fixture=True))
