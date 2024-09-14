from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
import requests
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UrlInput(BaseModel):
    urls: List[HttpUrl]

def scrape_url(url: str):
    jina_url = f'https://r.jina.ai/{url}'
    headers = {
        'Authorization': 'Bearer jina_55e19b66cd2d469b938fbd32daa029d1p4pTsRaHxnVEpg9sIViyLBzHe4DQ',
        'X-Return-Format': 'markdown'
    }
    
    try:
        response = requests.get(jina_url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return None

@app.post("/scrape_urls")
async def scrape_urls(url_input: UrlInput):
    logger.info(f"Received request to scrape URLs: {url_input.urls}")
    
    if len(url_input.urls) > 6:
        logger.warning(f"Received request with too many URLs: {len(url_input.urls)}")
        raise HTTPException(status_code=400, detail="Maximum 6 URLs allowed")

    results = []
    for url in url_input.urls:
        logger.info(f"Scraping URL: {url}")
        content = scrape_url(str(url))
        if content:
            results.append({
                "url": str(url),
                "content": content
            })
            logger.info(f"Successfully scraped: {url}")
        else:
            logger.error(f"Failed to scrape: {url}")
            results.append({
                "url": str(url),
                "error": "Failed to scrape URL"
            })

    logger.info(f"Scraping completed. Returning results for {len(results)} URLs")
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")