from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from normalize import normalize_fa
import os 
from dotenv import load_dotenv

load_dotenv()

es_host = os.getenv("ES_URL")
embed_model_name = os.getenv("EMBED_MODEL_NAME")
es_index_name = os.getenv("ES_INDEX_NAME")

model = SentenceTransformer(embed_model_name)
es = Elasticsearch(es_host)

INDEX = es_index_name

def show(res):
    for h in res["hits"]["hits"]:
        s = h["_source"]
        line = (f'{h["_id"]}   {h["_score"]:.3f}  {s["brand_en"]} {s["model"]}  '
                f'{s["price_toman"]:,}  stock={s["stock"]}')
        d = h.get("_debug")
        if d:
            line += f'  | keyword={d["bm25"]:.3f} vector={d["vector"]:.3f} ({d["source"]})'
        print(line)
    print("---")

def build_filters(max_price=None, in_stock=True, beginner_only=False):
    f = []
    if max_price is not None:
        f.append({"range": {"price_toman": {"lte": max_price}}})
    if in_stock:
        f.append({"range": {"stock": {"gte": 1}}})
    if beginner_only:
        f.append({"term": {"beginner_friendly": True}})
    return f

def hybrid_search(text, max_price=None, in_stock=True, beginner_only=False,
                  size=3, bm25_boost=1.0, knn_boost=1.0, debug=False):
    q = normalize_fa(text)
    qv = model.encode(q, normalize_embeddings=True).tolist()
    filters = build_filters(max_price, in_stock, beginner_only)

    bm25_query = {"bool": {
        "must": [{"match": {"search_text": {"query": q, "boost": bm25_boost}}}],
        "filter": filters,
    }}
    knn_clause = {"field": "embedding", "query_vector": qv,
                  "k": size, "num_candidates": 50,
                  "filter": {"bool": {"filter": filters}},
                  "boost": knn_boost}

    res = es.search(index=INDEX, size=size, query=bm25_query, knn=knn_clause)

    if debug:
        # Re-run each half alone, with the same settings, to see its own score
        bm = {h["_id"]: h["_score"]
              for h in es.search(index=INDEX, size=50, query=bm25_query)["hits"]["hits"]}
        kn = {h["_id"]: h["_score"]
              for h in es.search(index=INDEX, size=size, knn=knn_clause)["hits"]["hits"]}
        for h in res["hits"]["hits"]:
            b = bm.get(h["_id"], 0.0)
            k = kn.get(h["_id"], 0.0)
            h["_debug"] = {
                "bm25": b, "vector": k,
                "source": "both" if b and k else "keyword" if b else "vector",
            }
    return res

if __name__ == "__main__":
    show(hybrid_search("موتور ارزان و مناسب تازه‌کار برای رفت و آمد شهری",
                       max_price=150000000, beginner_only=True))
    # show(hybrid_search("Duke 390", in_stock=True))
    # show(hybrid_search("Duke 390", beginner_only=True))

