# main.py

from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from models.filters import QueryFilters
from services.duckdb_service import query_parquet_data
from fastapi.responses import JSONResponse
from services.meta_routes import router as meta_router
from services.page_routes import router as page_router
from pydantic import BaseModel
from typing import List

from typing import Optional
app = FastAPI()


app.include_router(meta_router)
app.include_router(page_router)


# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WidgetLayout(BaseModel):
    id: str
    x: int
    y: int
    w: int
    h: int
    locked: bool

class LayoutRequest(BaseModel):
    layout: List[WidgetLayout]
    
@app.post("/save-layout")
async def save_layout(layout_data: LayoutRequest, page_id: int = Query(...)):
    # You can save this to a file or DB
    print(f"Saving layout for page_id={page_id}:")
    print(layout_data)
    return {"status": "success"}

@app.get("/")
async def root():
    return {"message": "Equipment Monitoring System Backend Running"}

@app.post("/query")
async def query_data(filters: Optional[QueryFilters]):
    try:
        df = query_parquet_data(filters)

        # Rename timestamp column to 't_sampling_time' for frontend consistency
        if 'bucket_time' in df.columns:
            df.rename(columns={"bucket_time": "t_sampling_time"}, inplace=True)

        # Convert timestamps to ISO strings
        if "t_sampling_time" in df.columns:
            df["t_sampling_time"] = df["t_sampling_time"].astype(str)

        return JSONResponse(content=df.to_dict(orient="records"))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
# {
#   "year": 2025,
#   "month": null,
#   "equipment": "bsc",
#   "day": null,
#   "dcu": 2,
#   "start_time": "2025-03-02T00:00:00",
#   "end_time": "2025-03-02T23:59:59Z",
#   "metrics": [
#     "n_soc"
#   ],
#   "window_period": "1 hour",
#   "where_args": [
#     "n_bank=1"
#   ]
# }