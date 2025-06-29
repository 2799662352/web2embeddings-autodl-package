#!/usr/bin/env python3

# =================================================================================
# IMPORTANT LICENSE NOTE:
# The default model 'jinaai/jina-embeddings-v3' is licensed under CC BY-NC 4.0.
# This means it is free for research and non-commercial use.
# For commercial use, you must contact Jina AI for a proper license.
# =================================================================================

import os
import json
import argparse
import time
import threading
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Enhanced visualization imports
from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn, 
    TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import psutil
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Initialize rich console
console = Console()


class SystemMonitor:
    """Real-time system and GPU monitoring for enhanced visualization."""
    
    def __init__(self):
        self.monitoring = False
        self.stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_gb': 0.0,
            'memory_total_gb': 0.0,
            'gpu_stats': []
        }
        
    def start_monitoring(self):
        """Start background monitoring thread."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # CPU and Memory stats
                self.stats['cpu_percent'] = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.stats['memory_percent'] = memory.percent
                self.stats['memory_used_gb'] = memory.used / (1024**3)
                self.stats['memory_total_gb'] = memory.total / (1024**3)
                
                # GPU stats
                if GPU_AVAILABLE:
                    try:
                        gpus = GPUtil.getGPUs()
                        self.stats['gpu_stats'] = []
                        for gpu in gpus:
                            self.stats['gpu_stats'].append({
                                'id': gpu.id,
                                'name': gpu.name,
                                'load': gpu.load * 100,
                                'memory_used': gpu.memoryUsed,
                                'memory_total': gpu.memoryTotal,
                                'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                                'temperature': gpu.temperature
                            })
                    except Exception:
                        pass
                        
            except Exception:
                pass
            time.sleep(2)
    
    def get_stats_table(self) -> Table:
        """Generate a rich table with current system stats."""
        table = Table(title="🖥️ System Monitor", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Usage", justify="right")
        
        # CPU and Memory
        table.add_row(
            "CPU", 
            "🟢 Active",
            f"{self.stats['cpu_percent']:.1f}%"
        )
        table.add_row(
            "Memory", 
            "🟢 Available",
            f"{self.stats['memory_used_gb']:.1f}GB / {self.stats['memory_total_gb']:.1f}GB ({self.stats['memory_percent']:.1f}%)"
        )
        
        # GPU stats
        if self.stats['gpu_stats']:
            for gpu in self.stats['gpu_stats']:
                table.add_row(
                    f"GPU {gpu['id']}", 
                    f"🚀 {gpu['name'][:20]}{'...' if len(gpu['name']) > 20 else ''}",
                    f"Load: {gpu['load']:.1f}% | VRAM: {gpu['memory_used']}MB/{gpu['memory_total']}MB ({gpu['memory_percent']:.1f}%) | {gpu['temperature']}°C"
                )
        else:
            table.add_row("GPU", "❌ Not Available", "N/A")
            
        return table


class ChunkVectorizer:
    """Generate embeddings from text chunks and store them in a ChromaDB vector database."""
    
    def __init__(
        self,
        input_file: str,
        db_directory: str,
        model_name: str,
        task: str,
        truncate_dim: Optional[int],
        max_length: int,
        device: str,
        batch_size: int = 32
    ):
        """Initialize the vectorizer with input path and model parameters.
        
        Args:
            input_file: Path to the input JSONL file containing text chunks
            db_directory: Directory where ChromaDB will store the vector database
            model_name: The name of the sentence-transformer model to use
            task: The task for which the embeddings are generated
            truncate_dim: The dimension to truncate embeddings to (Matryoshka)
            max_length: The maximum sequence length for the model
            device: The device to run the model on (e.g., 'cuda', 'cpu')
            batch_size: Batch size for embedding generation
        """
        self.input_file = input_file
        self.db_directory = db_directory
        self.task = task
        self.truncate_dim = truncate_dim
        self.max_length = max_length
        self.device = device
        self.batch_size = batch_size
        self.start_time = time.time()
        
        # Initialize system monitor
        self.monitor = SystemMonitor()
        self.monitor.start_monitoring()
        
        # Create beautiful header
        self._print_header()
        
        # Setup collection
        self._setup_collection(model_name)
        
        # Load model with progress
        self._load_model(model_name)
        
    def _print_header(self):
        """Print a beautiful header for the vectorization process."""
        header_text = Text()
        header_text.append("🚀 Jina Embeddings V3 Vectorizer\n", style="bold blue")
        header_text.append("Enhanced with Real-time Monitoring & Visualization\n", style="italic cyan")
        header_text.append(f"Input: {self.input_file}\n", style="white")
        header_text.append(f"Device Strategy: {self.device or 'Auto-detect'}\n", style="white")
        header_text.append(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        console.print(Panel(header_text, title="🎯 Vectorization Mission", border_style="blue"))
        console.print()
        
    def _setup_collection(self, model_name: str):
        """Setup ChromaDB collection with progress indication."""
        with console.status("[bold green]Setting up ChromaDB collection...", spinner="dots"):
            collection_base_name = os.path.basename(self.input_file).replace('.jsonl', '')
            
            # Create collection name and limit to 63 characters (database limitation)
            model_short_name = model_name.split('/')[-1] if '/' in model_name else model_name
            collection_name = f"{collection_base_name}_{model_short_name}"
            
            # Truncate if longer than 63 chars
            if len(collection_name) > 63:
                collection_name = collection_name[:63]
            
            self.collection_name = collection_name
            
            # Initialize the ChromaDB client
            self.client = chromadb.PersistentClient(path=self.db_directory)
            
            # Delete the collection if it exists
            try:
                self.client.delete_collection(name=self.collection_name)
                console.print(f"🗑️ Deleted existing collection: {self.collection_name}", style="yellow")
            except Exception:
                pass
            
            # Create a new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Log collection info
            collections_file = "artifacts/vector_stores/collections.txt"
            os.makedirs(os.path.dirname(collections_file), exist_ok=True)
            with open(collections_file, 'a+', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{self.collection_name} ({timestamp}) - Model: {model_name}, Task: {self.task}\n")
            
        console.print(f"✅ ChromaDB collection ready: [bold cyan]{self.collection_name}[/bold cyan]")
        
    def _load_model(self, model_name: str):
        """Load the embedding model with enhanced progress visualization."""
        console.print()
        console.print(Panel.fit(f"📦 Loading Model: {model_name}", style="green"))
        
        with console.status(f"[bold green]Loading {model_name}...", spinner="aesthetic") as status:
            # Determine device
            if self.device is None:
                import torch
                if torch.cuda.is_available():
                    self.device = 'cuda'
                    status.update(f"[bold green]🚀 CUDA detected! Loading on GPU...")
                else:
                    self.device = 'cpu'
                    status.update(f"[bold yellow]Loading on CPU...")
            
            # Load model
            self.model = SentenceTransformer(
                model_name, trust_remote_code=True, device=self.device
            )
        
        # Model info table
        model_table = Table(title="🤖 Model Information", show_header=True, header_style="bold green")
        model_table.add_column("Property", style="cyan", no_wrap=True)
        model_table.add_column("Value", style="white")
        
        model_table.add_row("Model Name", model_name)
        model_table.add_row("Device", str(self.model.device))
        model_table.add_row("Max Sequence Length", str(self.model.max_seq_length))
        model_table.add_row("Embedding Dimension", str(self.model.get_sentence_embedding_dimension()))
        model_table.add_row("Task", self.task)
        if self.truncate_dim:
            model_table.add_row("Truncate Dimension", str(self.truncate_dim))
        model_table.add_row("Max Length", str(self.max_length))
        model_table.add_row("Batch Size", str(self.batch_size))
        
        console.print(model_table)
        console.print()
        
    def load_chunks(self) -> List[Dict[str, Any]]:
        """Load chunks from the input JSONL file with progress."""
        chunks = []
        
        console.print(Panel.fit(f"📄 Loading Data: {self.input_file}", style="blue"))
        
        with console.status("[bold blue]Reading JSONL file...", spinner="dots12"):
            with open(self.input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunk = json.loads(line)
                        chunks.append(chunk)
        
        # Data statistics
        data_table = Table(title="📊 Data Statistics", show_header=True, header_style="bold blue")
        data_table.add_column("Metric", style="cyan")
        data_table.add_column("Value", style="white")
        
        data_table.add_row("Total Chunks", str(len(chunks)))
        if chunks:
            avg_length = sum(len(chunk.get('text', '')) for chunk in chunks) / len(chunks)
            data_table.add_row("Average Text Length", f"{avg_length:.0f} characters")
            max_length = max(len(chunk.get('text', '')) for chunk in chunks)
            data_table.add_row("Max Text Length", f"{max_length} characters")
        
        console.print(data_table)
        console.print()
        
        return chunks
    
    def process_and_store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Process chunks with enhanced visualization and monitoring."""
        if not chunks:
            console.print("❌ No chunks to process!", style="bold red")
            return
        
        chunk_ids = [chunk['id'] for chunk in chunks]
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [{'source': chunk['source']} for chunk in chunks]
        
        total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size
        total_tokens = 0  # Initialize token counter
        
        console.print(Panel.fit(f"⚙️ Processing {len(chunks)} chunks in {total_batches} batches", style="yellow"))
        
        # Create layout for live updating
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=8)
        )
        
        # Embedding progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:
            
            embedding_task = progress.add_task(
                "[green]🧠 Generating Embeddings",
                total=len(texts)
            )
            
            # Custom encode with progress callback
            batch_embeddings = []
            processed_count = 0
            
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i+self.batch_size]
                
                # Tokenize to get token count for this batch
                encoding = self.model.tokenizer(batch_texts, padding=False, truncation=False)
                batch_tokens = sum(len(e) for e in encoding['input_ids'])
                total_tokens += batch_tokens
                
                # Generate embeddings for this batch
                batch_result = self.model.encode(
                    batch_texts,
                    task=self.task,
                    prompt_name=self.task,
                    truncate_dim=self.truncate_dim,
                    max_length=self.max_length,
                    show_progress_bar=False
                )
                
                batch_embeddings.extend(batch_result)
                processed_count += len(batch_texts)
                progress.update(embedding_task, completed=processed_count)
        
        console.print("✅ Embedding generation complete!")
        console.print()
        
        # ChromaDB storage progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            
            storage_task = progress.add_task(
                "[blue]💾 Storing in ChromaDB",
                total=total_batches
            )
            
            for i in range(0, len(chunks), self.batch_size):
                batch_ids = chunk_ids[i:i+self.batch_size]
                batch_emb = batch_embeddings[i:i+self.batch_size]
                batch_docs = texts[i:i+self.batch_size]
                batch_meta = metadatas[i:i+self.batch_size]
                
                # Convert numpy to list if needed
                if hasattr(batch_emb, 'tolist'):
                    batch_emb = [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in batch_emb]
                
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_emb,
                    documents=batch_docs,
                    metadatas=batch_meta
                )
                
                progress.advance(storage_task)
        
        console.print("✅ Storage complete!")
        console.print()
        
        # Final statistics
        self._print_completion_stats(len(chunks), total_tokens)
    
    def _print_completion_stats(self, total_chunks: int, total_tokens: int):
        """Print completion statistics and system status."""
        total_time = time.time() - self.start_time
        
        # Performance stats
        stats_table = Table(title="🎉 Completion Statistics", show_header=True, header_style="bold green")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Chunks Processed", str(total_chunks))
        stats_table.add_row("Total Tokens Processed", f"{total_tokens:,}")
        stats_table.add_row("Total Time", f"{total_time:.2f} seconds")
        stats_table.add_row("Processing Speed (Chunks)", f"{total_chunks/total_time:.2f} chunks/sec")
        stats_table.add_row("Processing Speed (Tokens)", f"{total_tokens / total_time:,.0f} tokens/sec")
        stats_table.add_row("Database Location", os.path.abspath(self.db_directory))
        stats_table.add_row("Collection Name", self.collection_name)
        stats_table.add_row("Documents in Collection", str(self.collection.count()))
        
        console.print(stats_table)
        console.print()
        
        # System monitor final status
        console.print(self.monitor.get_stats_table())
        
        # Success message
        success_text = Text()
        success_text.append("🎯 Vectorization Mission Complete! 🎯\n", style="bold green")
        success_text.append("Your data is now ready for semantic search and RAG applications.", style="italic cyan")
        
        console.print(Panel(success_text, title="✅ Success", border_style="green"))
    
    def run(self) -> None:
        """Run the full vectorization process with enhanced visualization."""
        try:
            chunks = self.load_chunks()
            if chunks:
                self.process_and_store_chunks(chunks)
            else:
                console.print("❌ No chunks found in the input file. Nothing to process.", style="bold red")
        except Exception as e:
            console.print(f"❌ Error during processing: {str(e)}", style="bold red")
            raise
        finally:
            self.monitor.stop_monitoring()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🚀 Enhanced Jina-v3 Vectorizer with Real-time Monitoring",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", "-i", required=True, help="Input JSONL file containing text chunks")
    parser.add_argument("--db", "-d", default="artifacts/vector_stores/chroma_db",
                        help="Directory for ChromaDB vector database")
    parser.add_argument("--model", "-m", default="jinaai/jina-embeddings-v3",
                        help="Name of the sentence-transformer model to use")
    parser.add_argument("--task", "-t", default="retrieval.passage",
                        choices=['retrieval.query', 'retrieval.passage', 'separation', 'classification', 'text-matching'],
                        help="The task for which to generate embeddings")
    parser.add_argument("--truncate-dim", "-td", type=int, default=None,
                        help="The dimension to truncate embeddings to (Matryoshka). Default is None (no truncation, uses full 1024 dim).")
    parser.add_argument("--max-length", "-ml", type=int, default=8192,
                        help="The maximum sequence length for the model")
    parser.add_argument("--batch-size", "-b", type=int, default=32,
                        help="Batch size for embedding generation")
    parser.add_argument("--device", "-dev", type=str, default=None,
                        help="Device to use for computation, e.g., 'cuda', 'cpu'. Auto-detects if None.")
    
    args = parser.parse_args()
    
    vectorizer = ChunkVectorizer(
        input_file=args.input,
        db_directory=args.db,
        model_name=args.model,
        task=args.task,
        truncate_dim=args.truncate_dim,
        max_length=args.max_length,
        device=args.device,
        batch_size=args.batch_size
    )
    vectorizer.run()