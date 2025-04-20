import faiss
import os
import pickle
import numpy as np
from .embedding import get_embedding

VECTOR_STORE_ROOT = 'vector_store'

def get_agent_index_path(agent_id):
    return os.path.join(VECTOR_STORE_ROOT, f'agent_{agent_id}')

def load_or_create_index(agent_id, dim=384):
    path = get_agent_index_path(agent_id)
    index_file = os.path.join(path, 'index.pkl')
    if os.path.exists(index_file):
        with open(index_file, 'rb') as f:
            index, metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []
    return index, metadata

def save_index(agent_id, index, metadata):
    path = get_agent_index_path(agent_id)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'index.pkl'), 'wb') as f:
        pickle.dump((index, metadata), f)

def add_chunks_to_agent_index(agent_id, chunks):
    index, metadata = load_or_create_index(agent_id)
    vectors = []
    for chunk in chunks:
        try:
            vec = get_embedding(chunk.content)
            vectors.append(vec)
            metadata.append({
                'chunk_id': chunk.id,
                'content': chunk.content,
                'kb_id': chunk.kb_id,
            })
        except Exception as e:
            print(f"Embedding failed for chunk {chunk.id}: {e}")

    if vectors:
        index.add(np.array(vectors).astype('float32'))
        save_index(agent_id, index, metadata)

def search_agent_chunks(agent_id, query, top_k=5):
    query_vec = get_embedding(query).astype('float32')
    index, metadata = load_or_create_index(agent_id)
    if index.ntotal == 0:
        return []

    D, I = index.search(np.array([query_vec]), top_k)
    results = []
    for i in I[0]:
        if i < len(metadata):
            results.append(metadata[i])
    return results
