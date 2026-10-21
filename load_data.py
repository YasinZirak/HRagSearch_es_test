import os 
from data  import BIKES
from normalize import build_search_text
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch,helpers
from dotenv import load_dotenv

load_dotenv()

es_host = os.getenv("ES_URL")
embed_model_name = os.getenv("EMBED_MODEL_NAME")
es_index_name = os.getenv("ES_INDEX_NAME")

model = SentenceTransformer(embed_model_name)
es = Elasticsearch(es_host)

texts = [build_search_text(bike) for bike in BIKES]
embeddings = model.encode(texts , normalize_embeddings= True , batch_size= 8)

INDEX =  es_index_name

actions = []
for bike , vec in  zip(BIKES, embeddings):
    doc = {
        **bike,
        "search_text": build_search_text(bike),
        "embedding": vec.tolist()
          }
    actions.append({"_index": INDEX, "_id": bike["id"], "_source": doc})
helpers.bulk(es,actions)
es.indices.refresh(index=INDEX)

print("documents in index", es.count(index = INDEX)["count"])
