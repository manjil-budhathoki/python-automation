import uvicorn
from fastapi import FastAPI
from views import router as stock_router

app = FastAPI(title="Nepal Stock Scraper API Hub")

# Include all the routes from views.py
app.include_router(stock_router)

@app.get("/")
async def root():
    return {"message": "API is running. Visit /docs for the interface."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)