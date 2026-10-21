from typing import Optional
from fastapi import FastAPI, Query
from search import hybrid_search
from fastapi.responses import FileResponse


app = FastAPI(title="Motorcycle search")

@app.get("/" , include_in_schema= False)
def home():
    return FileResponse("index.html")

@app.get("/search")
def saerch(
            q:str = Query(...,min_length=1, description="Search text" ),
            max_price: Optional[int] =  None,
            in_stock:bool = True,
            beginner_only:bool = False,
            size:int = Query(3, ge=1, le=20),
            debug: bool = False,
          ):
    res = hybrid_search(q, max_price=max_price, in_stock=in_stock,
                        beginner_only=beginner_only, size=size, debug=debug)
    results = []
    for h in res["hits"]["hits"]:
        item = {k: v for k, v in h["_source"].items() if k != "embedding"}
        results.append({"id": h["_id"], "score": h["_score"],
                        "debug": h.get("_debug"), **item})
    return {"results": results}


    