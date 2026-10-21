from elasticsearch import Elasticsearch
import os 
from dotenv import load_dotenv

load_dotenv()

es_host = os.getenv("ES_URL")
es_index_name = os.getenv("ES_INDEX_NAME")


es = Elasticsearch(es_host)

INDEX = es_index_name

if es.indices.exists(index= INDEX) : 
    print(f"Index {INDEX} existed so deleted")
    es.indices.delete(index= INDEX)


settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
}

mappings = {
    "dynamic": "false",
    "properties": {
        "id":                {"type": "keyword"},
        "brand":             {"type": "keyword"},
        "brand_en":          {"type": "keyword"},
        "category_fa":       {"type": "keyword"},
        "cc":                {"type": "integer"},
        "price_toman":       {"type": "long"},
        "seat_height_mm":    {"type": "integer"},
        "stock":             {"type": "integer"},
        "beginner_friendly": {"type": "boolean"},
        "search_text":       {"type": "text", "analyzer": "persian"},
        "embedding": {
            "type": "dense_vector",
            "dims": 1024,
            "index": True,
            "similarity": "cosine",
        },
    },
}

print(f"created new index {INDEX}" )

es.indices.create(index=INDEX ,settings=settings ,mappings = mappings)

props  = es.indices.get_mapping(index=INDEX)[INDEX]["mappings"]["properties"]

print("created fiellds" , props)