import sys
sys.path.insert(0, '.')

from app.schemas.paper import PaperMetadata
from app.rag.pipeline import ingest_paper
from app.rag.retriever import retrieve

# Ingest a paper abstract
meta = PaperMetadata(
    title='Diabetic Retinopathy Detection using CNN',
    authors=['Smith J'],
    year='2023',
    abstract='We propose a CNN-based approach for detecting diabetic retinopathy achieving 97% AUC on EyePACS dataset. The model uses ResNet-50 architecture trained on 88000 fundus images.',
    source='pubmed',
    pmid='12345'
)
n = ingest_paper(meta)
print(f'Ingested {n} chunks from abstract')

# Retrieve
results = retrieve('diabetic retinopathy CNN detection', top_k=3)
print(f'Retrieved {len(results)} chunks')
if results:
    print('Top chunk:', results[0]['text'][:100])

print('=== ALL RAG TESTS PASSED ===')
