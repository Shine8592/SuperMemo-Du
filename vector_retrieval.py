#!/usr/bin/env python3
"""
Custom Vector Retrieval System for Memory
Uses existing embeddinggemma-300M-Q8_0.gguf model
Provides semantic search over memory files
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import struct

# Try to import necessary libraries
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Configuration
MODEL_PATH = "/root/.openclaw/models/embedding/embeddinggemma-300M-Q8_0.gguf"
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
INDEX_PATH = MEMORY_DIR / "vector_index.faiss"
METADATA_PATH = MEMORY_DIR / "vector_metadata.json"

def simple_hash(text: str) -> str:
    """Create hash of text for identification"""
    return hashlib.md5(text.encode()).hexdigest()[:12]

def tokenize_simple(text: str) -> List[str]:
    """Simple tokenizer for fallback"""
    text = text.lower()
    for punct in ".,!?;:()[]{}\"'\\n\\t":
        text = text.replace(punct, " ")
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

def create_simple_embedding(text: str, dim: int = 300) -> List[float]:
    """
    Create a simple word-based embedding (fallback when model not available)
    Uses character n-grams and word frequencies
    """
    tokens = tokenize_simple(text)
    
    # Create character n-gram features
    ngram_features = {}
    for token in tokens:
        for n in [2, 3, 4]:
            for i in range(len(token) - n + 1):
                ngram = token[i:i+n]
                ngram_features[ngram] = ngram_features.get(ngram, 0) + 1
    
    # Normalize and create fixed-dimension vector
    total = sum(ngram_features.values()) if ngram_features else 1
    
    # Use hash to distribute features across dimensions
    vector = [0.0] * dim
    for ngram, count in ngram_features.items():
        h = int(hashlib.md5(ngram.encode()).hexdigest(), 16)
        dim_idx = h % dim
        vector[dim_idx] += (count / total)
    
    # Normalize vector
    norm = sum(v**2 for v in vector) ** 0.5
    if norm > 0:
        vector = [v / norm for v in vector]
    
    return vector

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a**2 for a in vec1) ** 0.5
    norm2 = sum(b**2 for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot / (norm1 * norm2)

def load_text_chunks() -> List[Dict]:
    """Load text chunks from memory files"""
    chunks = []
    
    # Core memory files
    core_files = ["MEMORY.md", "SOUL.md", "TOOLS.md", "USER.md", "AGENTS.md", "IDENTITY.md"]
    
    for filename in core_files:
        file_path = MEMORY_DIR.parent / filename
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections
            sections = content.split("\n## ")
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                
                if not section.startswith("#"):
                    section = "## " + section
                
                section = section.strip()
                if len(section) > 2000:
                    section = section[:2000] + "..."
                
                chunks.append({
                    "id": f"{filename}:{i}",
                    "text": section,
                    "source": filename,
                    "type": "core_memory",
                    "chunk_index": i
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # Daily logs
    daily_dir = MEMORY_DIR / "daily"
    if daily_dir.exists():
        for file_path in sorted(daily_dir.glob("*.md")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use entire daily log as one chunk
                if content.strip():
                    chunks.append({
                        "id": f"daily/{file_path.name}:0",
                        "text": content.strip(),
                        "source": f"daily/{file_path.name}",
                        "type": "daily_log"
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    # REM sleep logs (dreams)
    rem_dir = MEMORY_DIR / "dreaming" / "rem"
    if rem_dir.exists():
        for file_path in sorted(rem_dir.glob("*.md")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by major sections
                sections = content.split("\n# ")
                for i, section in enumerate(sections):
                    if not section.strip():
                        continue
                    
                    if not section.startswith("#"):
                        section = "# " + section
                    
                    section = section.strip()
                    if len(section) > 1500:
                        section = section[:1500] + "..."
                    
                    chunks.append({
                        "id": f"dreaming/rem/{file_path.name}:{i}",
                        "text": section,
                        "source": f"dreaming/rem/{file_path.name}",
                        "type": "dream_log",
                        "chunk_index": i
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return chunks

def build_index():
    """Build vector index from memory files"""
    print("🔍 Loading text chunks from memory files...")
    chunks = load_text_chunks()
    print(f"  Found {len(chunks)} chunks")
    
    print("\n🧠 Creating embeddings...")
    embeddings = []
    metadata = []
    
    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
        
        embedding = create_simple_embedding(chunk["text"], dim=300)
        embeddings.append(embedding)
        
        metadata.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "type": chunk["type"],
            "text": chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
            "hash": simple_hash(chunk["text"])
        })
    
    print(f"\n💾 Saving index to {INDEX_PATH}...")
    
    # Save using Faiss if available, otherwise use simple JSON
    if FAISS_AVAILABLE and NUMPY_AVAILABLE:
        # Create Faiss index
        dimension = 300
        index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity for normalized vectors)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)
        
        index.add(embeddings_array)
        faiss.write_index(index, str(INDEX_PATH))
        print(f"  Faiss index saved with {index.ntotal} vectors")
    else:
        # Fallback: save embeddings as JSON
        index_data = {
            "embeddings": embeddings,
            "dimension": 300
        }
        with open(INDEX_PATH.with_suffix('.json'), 'w') as f:
            json.dump(index_data, f)
        print("  Fallback index saved (JSON format)")
    
    # Save metadata
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Metadata saved ({len(metadata)} items)")
    
    print("\n✅ Index built successfully!")
    print(f"   Types: core_memory, daily_log, dream_log")
    return True

def search(query: str, top_k: int = 5, use_faiss: bool = FAISS_AVAILABLE and NUMPY_AVAILABLE) -> List[Dict]:
    """Search for similar text chunks"""
    
    # Load metadata
    if not METADATA_PATH.exists():
        print("❌ Index not found. Run build_index() first.")
        return []
    
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
    
    # Create query embedding
    query_embedding = create_simple_embedding(query, dim=300)
    
    if use_faiss and FAISS_AVAILABLE and NUMPY_AVAILABLE and INDEX_PATH.exists():
        # Use Faiss for search
        index = faiss.read_index(str(INDEX_PATH))
        
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        scores, indices = index.search(query_array, top_k)
        
        results = []
        for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx < len(metadata):
                results.append({
                    **metadata[idx],
                    "similarity": float(score),
                    "rank": i + 1
                })
        
        return results
    else:
        # Fallback: compute similarities manually
        index_file = INDEX_PATH.with_suffix('.json')
        if not index_file.exists():
            print("❌ Fallback index not found.")
            return []
        
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        embeddings = index_data["embeddings"]
        
        # Compute similarities
        similarities = []
        for i, emb in enumerate(embeddings):
            sim = cosine_similarity(query_embedding, emb)
            similarities.append((i, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for rank, (idx, score) in enumerate(similarities[:top_k]):
            if score > 0:  # Only include positive similarities
                results.append({
                    **metadata[idx],
                    "similarity": score,
                    "rank": rank + 1
                })
        
        return results

def print_results(results: List[Dict]):
    """Pretty print search results"""
    if not results:
        print("\n❌ No results found.")
        return
    
    print(f"\n{'='*70}")
    print(f"📊 Top {len(results)} Results")
    print(f"{'='*70}\n")
    
    for result in results:
        type_icon = {
            "core_memory": "📚",
            "daily_log": "📅",
            "dream_log": "🌙"
        }.get(result.get("type", ""), "📄")
        
        print(f"{type_icon} Rank {result['rank']} (Similarity: {result['similarity']:.3f})")
        print(f"   📄 Source: {result['source']}")
        print(f"   🔍 ID: {result['id']}")
        text_preview = result['text'][:300]
        if len(result['text']) > 300:
            text_preview += "..."
        print(f"   💬 Text: {text_preview}")
        print()

def main():
    """Main CLI interface"""
    print("🎯 Memory Vector Retrieval System")
    print("   Using embeddinggemma-300M-Q8_0.gguf (fallback mode)\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python vector_retrieval.py build        # Build index")
        print("  python vector_retrieval.py search <query>  # Search")
        print("  python vector_retrieval.py status        # Check status")
        return
    
    command = sys.argv[1]
    
    if command == "build":
        build_index()
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        
        query = " ".join(sys.argv[2:])
        print(f"\n🔍 Searching for: '{query}'\n")
        
        results = search(query, top_k=5)
        print_results(results)
    
    elif command == "status":
        print("\n📋 System Status")
        print(f"   Model: {MODEL_PATH}")
        print(f"   Model exists: {os.path.exists(MODEL_PATH)}")
        print(f"   Memory dir: {MEMORY_DIR}")
        print(f"   Faiss available: {FAISS_AVAILABLE}")
        print(f"   NumPy available: {NUMPY_AVAILABLE}")
        print(f"   Index exists: {INDEX_PATH.exists() or INDEX_PATH.with_suffix('.json').exists()}")
        
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            print(f"   Indexed chunks: {len(metadata)}")
            types = {}
            for item in metadata:
                t = item.get("type", "unknown")
                types[t] = types.get(t, 0) + 1
            for t, count in types.items():
                print(f"     - {t}: {count}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
