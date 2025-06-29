#!/usr/bin/env python3
"""
🚀 Minimal ChromaDB FastMCP Server 🚀

A minimal viable MCP server for connecting to and querying a pre-existing
ChromaDB vector database. This version is optimized for performance by caching
the collection object on startup.

SPECIAL FEATURE - ARTIST ANALYSIS WORKFLOW:
When provided with specific artist names, the server automatically performs:
1. Detailed artist style and tag analysis
2. Similar artist discovery based on core characteristics
3. Generation of ready-to-use artist combination strings
4. Comprehensive explanations for each recommendation

This enables rapid discovery and composition of artist combinations for 
creative projects while maintaining thematic coherence and quality standards.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, List
import uuid
from datetime import datetime

# --- Dependency Imports ---
try:
    from mcp.server.fastmcp import FastMCP
    import chromadb
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError as e:
    print("="*80, file=sys.stderr)
    print(f"ERROR: A required library is not installed: {e}", file=sys.stderr)
    print("Please run: `pip install fastmcp-server chromadb sentence-transformers torch`", file=sys.stderr)
    print("="*80, file=sys.stderr)
    sys.exit(1)

# --- Server Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MinimalChromaServer")
mcp = FastMCP("Minimal ChromaDB Query Server")

# --- Global Variables ---
client: chromadb.PersistentClient
collection: chromadb.Collection
memory_collection: chromadb.Collection
model: SentenceTransformer

@mcp.tool()
def list_collections(dummy: str = "") -> Dict[str, Any]:
    """
    Lists all available collections in the ChromaDB database.
    (This function includes a dummy parameter to satisfy MCP requirements for no-argument tools.)
    """
    try:
        collections = client.list_collections()
        return {
            "success": True, 
            "collections": [{"name": c.name, "id": str(c.id)} for c in collections]
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to list collections: {e}"}

@mcp.tool()
def query(query_text: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Queries the pre-configured collection for text similar to the query_text.
    The collection is set on server startup.
    
    SPECIAL WORKFLOW FOR ARTIST QUERIES:
    When query_text contains a specific artist name (e.g., "asanagi", "inunekomaskman"), 
    the system should automatically:
    
    1. First perform detailed artist analysis including:
       - Artist's core creative themes and style
       - Most frequently used tags and their meanings
       - Quality level and popularity metrics
       - Signature techniques and visual characteristics
    
    2. Based on the analysis, search for similar artists who share:
       - Similar core tags (mind break, guro, bondage, etc.)
       - Comparable art quality and style
       - Compatible thematic elements
    
    3. Generate a ready-to-copy artist string in the format:
       `(artist:original_artist:1.0), ((artist:similar1, artist:similar2)), (artist:similar3, artist:similar4)`
    
    4. Provide detailed explanations for each recommended artist including:
       - Why they are similar to the original artist
       - Their key tags and specialties
       - Art quality and popularity level
       - Specific strengths that complement the original artist
    
    The goal is to create comprehensive artist combinations that maintain the core aesthetic 
    while expanding creative possibilities.
    """
    try:
        query_embedding = model.encode(query_text).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def search_memory(query_text: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Searches only the user's memory collection for text similar to the query_text.
    
    ARTIST WORKFLOW SUPPORT:
    When searching for artist-related memories, this tool can help recall:
    - Previously analyzed artist profiles and style characteristics
    - Successful artist combinations and their results
    - User preferences for specific artistic themes or tags
    - Historical artist recommendations and their effectiveness
    
    This supports the main query workflow by providing context from past 
    artist analysis sessions and user feedback.
    """
    try:
        query_embedding = model.encode(query_text).tolist()
        
        results = memory_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def remember(memory_text: str) -> Dict[str, Any]:
    """
    Stores a piece of text (a memory) in the ChromaDB collection.
    A unique ID will be generated for the memory.
    """
    try:
        memory_id = f"memory_{uuid.uuid4()}"
        
        logger.info(f"Encoding memory: '{memory_text[:50]}...'")
        embedding = model.encode(memory_text).tolist()
        
        logger.info(f"Adding memory with ID: {memory_id} to collection '{memory_collection.name}'")
        memory_collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[memory_text],
            metadatas=[{
                "source": "user_memory",
                "timestamp_utc": datetime.utcnow().isoformat()
            }]
        )
        
        return {"success": True, "message": "Memory stored successfully.", "memory_id": memory_id}
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the Minimal ChromaDB FastMCP Server')
    parser.add_argument('--chromadb-path', '-d', type=str, required=True,
                        help='Path to the ChromaDB database')
    parser.add_argument('--collection-name', '-c', type=str, required=True,
                        help='Name of the ChromaDB collection to query')
    parser.add_argument('--memory-collection-name', type=str, 
                        default="user_memories",
                        help='Name of the collection to store user memories (default: user_memories)')
    parser.add_argument('--model-name', '-m', type=str, 
                        default="jinaai/jina-embeddings-v3",
                        help='Sentence transformer model name (default: jinaai/jina-embeddings-v3)')
    parser.add_argument('--device', type=str, 
                        default="auto",
                        help='Device to run model on: cuda, cpu, or auto (default: auto)')
    
    args = parser.parse_args()
    
    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else "cpu"
    
    logger.info("🚀 Starting Minimal ChromaDB FastMCP Server...")
    logger.info(f"Database path: {args.chromadb_path}")
    logger.info(f"Main Collection: {args.collection_name}")
    logger.info(f"Memory Collection: {args.memory_collection_name}")
    logger.info(f"Model: {args.model_name}")
    logger.info(f"Device: {device}")
    
    try:
        if not os.path.exists(args.chromadb_path):
            raise FileNotFoundError(f"Database path does not exist: {args.chromadb_path}")
        
        client = chromadb.PersistentClient(path=args.chromadb_path)
        
        logger.info(f"Loading model '{args.model_name}' on device '{device}'...")
        model = SentenceTransformer(
            args.model_name, 
            device=device,
            trust_remote_code=True
        )
        
        logger.info(f"Accessing collection '{args.collection_name}'...")
        collection = client.get_collection(name=args.collection_name)
        
        logger.info(f"Accessing or creating memory collection '{args.memory_collection_name}'...")
        memory_collection = client.get_or_create_collection(name=args.memory_collection_name)
        
        logger.info("✅ Server ready. Listening for MCP requests via stdio...")
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"❌ Server initialization failed: {e}")
        sys.exit(1)