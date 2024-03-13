import warnings

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from search import Search

TEMPLATES_DIRECTORY = './templates'

templates = Jinja2Templates(TEMPLATES_DIRECTORY)
app = FastAPI()
vector = Search()
warnings.filterwarnings('ignore')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request, q: str = ''):
    result = []
    if q:
        result = vector.search(q)
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result, 'q': q})


if __name__ == '__main__':
    uvicorn.run(app)
