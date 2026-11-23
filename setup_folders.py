import os

directories = [
    "app/agents", "app/rag", "app/literature", "app/documents",
    "app/mcp", "app/database", "app/schemas", "app/utils",
    "frontend", "data/papers", "data/processed", "data/cache",
    "tests", "notebooks"
]

files = [
    "app/main.py",
    "app/agents/research_agent.py", "app/agents/evidence_agent.py", "app/agents/validation_agent.py", "app/agents/synthesis_agent.py", "app/agents/gap_agent.py",
    "app/rag/embeddings.py", "app/rag/chunking.py", "app/rag/retriever.py", "app/rag/vector_store.py", "app/rag/pipeline.py",
    "app/literature/pubmed.py", "app/literature/semantic_scholar.py", "app/literature/metadata.py",
    "app/documents/pdf_loader.py", "app/documents/parser.py", "app/documents/processor.py",
    "app/mcp/literature_server.py", "app/mcp/file_server.py", "app/mcp/database_server.py",
    "app/database/models.py", "app/database/database.py", "app/database/crud.py",
    "app/schemas/research.py", "app/schemas/paper.py", "app/schemas/evidence.py",
    "app/utils/logging.py", "app/utils/config.py",
    ".env", ".gitignore", "Dockerfile", "docker-compose.yml", "README.md"
]

# Create directories
for d in directories:
    os.makedirs(d, exist_ok=True)

# Create empty files
for f in files:
    with open(f, 'a') as file:
        pass

print("Project structure created successfully!")