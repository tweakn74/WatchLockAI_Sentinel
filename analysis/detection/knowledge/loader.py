"""RAG Knowledge Pack loader and indexer for WatchLockAI Sentinel.

Implements local RAG index from Knowledge Pack files with fallback from embeddings to FTS.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, NamedTuple

import yaml
from loguru import logger


def _get_sentence_transformer() -> type | None:
    """Lazy import sentence-transformers to avoid import-time dependencies."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer
    except ImportError:
        logger.warning("sentence-transformers not available, falling back to SQLite FTS")
        return None


class KnowledgeHit(NamedTuple):
    """Knowledge base search result with provenance."""

    content: str
    filename: str
    section: str
    lines: str
    confidence: float


class SentinelDirective(NamedTuple):
    """Parsed sentinel directive from Knowledge Pack."""

    component: str
    provides: dict[str, Any]
    constraints: dict[str, Any]


class KnowledgeLoader:
    """RAG knowledge loader implementing Knowledge Pack indexing per specs."""

    def __init__(self, packs_dir: str = "detection/knowledge/packs", index_dir: str = "detection/knowledge/index") -> None:
        """Initialize knowledge loader.

        Args:
            packs_dir: Directory containing Knowledge Pack files.
            index_dir: Directory for index storage.
        """
        self.packs_dir = Path(packs_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.index_dir / "knowledge.db"
        self.embeddings_model: Any | None = None
        self.embeddings_initialized = False
        self.mode = "fts"  # Will be set to "embeddings" if available after lazy init

        self._init_database()
        # Embeddings are now lazy-loaded on first use to avoid CI overhead

    def _init_database(self) -> None:
        """Initialize SQLite database for knowledge storage."""
        with sqlite3.connect(self.db_path) as conn:
            # Knowledge content table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    section TEXT NOT NULL,
                    content TEXT NOT NULL,
                    lines TEXT,
                    content_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Full-text search virtual table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    content,
                    filename,
                    section,
                    content=knowledge_content,
                    content_rowid=id
                )
            """)

            # Embeddings table (if using embeddings mode)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                    id INTEGER PRIMARY KEY,
                    embedding BLOB,
                    FOREIGN KEY (id) REFERENCES knowledge_content(id)
                )
            """)

            # Directives table for parsed sentinel directives
            conn.execute("""
                CREATE TABLE IF NOT EXISTS directives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    component TEXT NOT NULL,
                    provides TEXT,
                    constraints TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Pack files tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pack_files (
                    filename TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _try_init_embeddings(self) -> None:
        """Try to initialize embeddings model (called lazily on first use)."""
        if self.embeddings_initialized:
            return
            
        self.embeddings_initialized = True
        
        SentenceTransformer = _get_sentence_transformer()
        if SentenceTransformer is None:
            logger.info("Using SQLite FTS mode (embeddings not available)")
            return

        try:
            # Use a lightweight model for local deployment
            logger.info("Loading embeddings model (lazy initialization)...")
            self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.mode = "embeddings"
            logger.info("Embeddings mode enabled with all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Failed to load embeddings model, using FTS: {e}")
            self.mode = "fts"

    def _ensure_embeddings_loaded(self) -> None:
        """Ensure embeddings are loaded if we're using embeddings mode."""
        if not self.embeddings_initialized:
            self._try_init_embeddings()

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file content.

        Args:
            file_path: Path to file.

        Returns:
            Hex string of file hash.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _parse_sentinel_directives(self, content: str, filename: str) -> list[SentinelDirective]:
        """Parse sentinel directives from file content.

        Args:
            content: File content.
            filename: Name of the file.

        Returns:
            List of parsed directives.
        """
        directives = []

        # Look for sentinel directive blocks
        directive_pattern = re.compile(
            r"# --- sentinel:directive ---\n(.*?)\n# --- end ---",
            re.DOTALL | re.MULTILINE,
        )

        for match in directive_pattern.finditer(content):
            try:
                directive_yaml = match.group(1)
                directive_data = yaml.safe_load(directive_yaml)

                if directive_data and "component" in directive_data:
                    directive = SentinelDirective(
                        component=directive_data["component"],
                        provides=directive_data.get("provides", {}),
                        constraints=directive_data.get("constraints", {}),
                    )
                    directives.append(directive)
                    logger.debug(f"Parsed directive from {filename}: {directive.component}")

            except Exception as e:
                logger.warning(f"Failed to parse directive in {filename}: {e}")

        return directives

    def _extract_sections(self, content: str, filename: str) -> list[tuple[str, str, str]]:
        """Extract sections from markdown content.

        Args:
            content: File content.
            filename: Name of the file.

        Returns:
            List of (section_name, section_content, line_range) tuples.
        """
        sections = []
        lines = content.splitlines()
        current_section = "introduction"
        current_content = []
        start_line = 1

        for line_num, line in enumerate(lines, 1):
            # Detect section headers
            if line.startswith("#"):
                # Save previous section
                if current_content:
                    section_text = "\n".join(current_content).strip()
                    if section_text:
                        line_range = f"{start_line}-{line_num-1}"
                        sections.append((current_section, section_text, line_range))

                # Start new section
                current_section = line.strip("# ").lower().replace(" ", "").replace("—", "").replace("-", "")
                current_content = []
                start_line = line_num
            else:
                current_content.append(line)

        # Add final section
        if current_content:
            section_text = "\n".join(current_content).strip()
            if section_text:
                line_range = f"{start_line}-{len(lines)}"
                sections.append((current_section, section_text, line_range))

        return sections

    def rebuild_index(self) -> dict[str, Any]:
        """Rebuild knowledge index from pack files.

        Returns:
            Dictionary with indexing statistics.
        """
        logger.info("Rebuilding knowledge index...")

        stats = {
            "files_processed": 0,
            "sections_indexed": 0,
            "directives_parsed": 0,
            "mode": self.mode,
            "errors": [],
        }

        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data
            conn.execute("DELETE FROM knowledge_content")
            conn.execute("DELETE FROM knowledge_fts")
            conn.execute("DELETE FROM knowledge_embeddings")
            conn.execute("DELETE FROM directives")
            conn.execute("DELETE FROM pack_files")

            # Process all files in packs directory
            for file_path in self.packs_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in [".md", ".yaml", ".yml", ".txt"]:
                    try:
                        self._index_file(file_path, conn, stats)
                    except Exception as e:
                        error_msg = f"Error indexing {file_path}: {e}"
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)

            conn.commit()

        logger.info(f"Index rebuilt: {stats}")
        return stats

    def _index_file(self, file_path: Path, conn: sqlite3.Connection, stats: dict[str, Any]) -> None:
        """Index a single file.

        Args:
            file_path: Path to file.
            conn: Database connection.
            stats: Statistics dictionary to update.
        """
        # Ensure embeddings are loaded if we're using embeddings mode
        self._ensure_embeddings_loaded()
        
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        file_hash = self._compute_file_hash(file_path)
        filename = file_path.name

        # Track file
        conn.execute(
            "INSERT INTO pack_files (filename, file_hash) VALUES (?, ?)",
            (filename, file_hash),
        )

        # Parse directives
        directives = self._parse_sentinel_directives(content, filename)
        for directive in directives:
            conn.execute(
                "INSERT INTO directives (filename, component, provides, constraints) VALUES (?, ?, ?, ?)",
                (filename, directive.component, json.dumps(directive.provides), json.dumps(directive.constraints)),
            )
            stats["directives_parsed"] += 1

        # Extract and index sections
        sections = self._extract_sections(content, filename)
        for section_name, section_content, line_range in sections:
            # Insert content
            cursor = conn.execute(
                "INSERT INTO knowledge_content (filename, section, content, lines, content_hash) VALUES (?, ?, ?, ?, ?)",
                (filename, section_name, section_content, line_range, hashlib.sha256(section_content.encode()).hexdigest()),
            )

            content_id = cursor.lastrowid

            # Index for FTS
            conn.execute(
                "INSERT INTO knowledge_fts (rowid, content, filename, section) VALUES (?, ?, ?, ?)",
                (content_id, section_content, filename, section_name),
            )

            # Generate embeddings if available
            if self.mode == "embeddings" and self.embeddings_model:
                try:
                    embedding = self.embeddings_model.encode([section_content])[0]
                    embedding_blob = embedding.tobytes()
                    conn.execute(
                        "INSERT INTO knowledge_embeddings (id, embedding) VALUES (?, ?)",
                        (content_id, embedding_blob),
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for {filename}#{section_name}: {e}")

            stats["sections_indexed"] += 1

        stats["files_processed"] += 1
        logger.debug(f"Indexed {filename}: {len(sections)} sections, {len(directives)} directives")

    def query_knowledge(self, query: str, limit: int = 10) -> list[KnowledgeHit]:
        """Query knowledge base with automatic fallback.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            List of knowledge hits with provenance.
        """
        # Ensure embeddings are loaded if we're using embeddings mode
        self._ensure_embeddings_loaded()
        
        if self.mode == "embeddings" and self.embeddings_model:
            try:
                return self._query_embeddings(query, limit)
            except Exception as e:
                logger.warning(f"Embeddings query failed, falling back to FTS: {e}")
                return self._query_fts(query, limit)
        else:
            return self._query_fts(query, limit)

    def _query_embeddings(self, query: str, limit: int) -> list[KnowledgeHit]:
        """Query using embeddings similarity.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            List of knowledge hits.
        """
        if not self.embeddings_model:
            msg = "Embeddings model not available"
            raise ValueError(msg)

        import numpy as np

        # Generate query embedding
        query_embedding = self.embeddings_model.encode([query])[0]

        hits = []
        with sqlite3.connect(self.db_path) as conn:
            # Get all embeddings and compute similarity
            cursor = conn.execute("""
                SELECT kc.id, kc.filename, kc.section, kc.content, kc.lines, ke.embedding
                FROM knowledge_content kc
                JOIN knowledge_embeddings ke ON kc.id = ke.id
            """)

            similarities = []
            for row in cursor:
                content_id, filename, section, content, lines, embedding_blob = row

                # Deserialize embedding
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)

                # Compute cosine similarity
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                )

                similarities.append((similarity, filename, section, content, lines))

            # Sort by similarity and take top results
            similarities.sort(reverse=True, key=lambda x: x[0])

            for similarity, filename, section, content, lines in similarities[:limit]:
                hits.append(KnowledgeHit(
                    content=content,
                    filename=filename,
                    section=section,
                    lines=lines or "",
                    confidence=float(similarity),
                ))

        return hits

    def _query_fts(self, query: str, limit: int) -> list[KnowledgeHit]:
        """Query using SQLite FTS.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            List of knowledge hits.
        """
        hits = []

        # Escape FTS query and prepare terms
        fts_query = " OR ".join(f'"{term}"' for term in query.split() if term.strip())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT kc.filename, kc.section, kc.content, kc.lines,
                       snippet(knowledge_fts, 0, '<match>', '</match>', '...', 32) as snippet,
                       rank
                FROM knowledge_fts
                JOIN knowledge_content kc ON knowledge_fts.rowid = kc.id
                WHERE knowledge_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, limit))

            for row in cursor:
                filename, section, content, lines, snippet, rank = row

                # Calculate confidence based on FTS rank (higher rank = lower confidence)
                confidence = max(0.1, 1.0 / (1.0 + abs(rank) * 0.1))

                hits.append(KnowledgeHit(
                    content=content,
                    filename=filename,
                    section=section,
                    lines=lines or "",
                    confidence=confidence,
                ))

        return hits

    def get_directive(self, component: str) -> SentinelDirective | None:
        """Get parsed directive for component.

        Args:
            component: Component name.

        Returns:
            Directive if found, None otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT component, provides, constraints FROM directives WHERE component = ? LIMIT 1",
                (component,),
            )
            row = cursor.fetchone()

            if row:
                component_name, provides_json, constraints_json = row
                return SentinelDirective(
                    component=component_name,
                    provides=json.loads(provides_json) if provides_json else {},
                    constraints=json.loads(constraints_json) if constraints_json else {},
                )

        return None

    def get_index_info(self) -> dict[str, Any]:
        """Get information about the knowledge index.

        Returns:
            Dictionary with index information.
        """
        info = {
            "mode": self.mode,
            "embeddings_available": _get_sentence_transformer() is not None,
            "packs_dir": str(self.packs_dir),
            "index_dir": str(self.index_dir),
        }

        with sqlite3.connect(self.db_path) as conn:
            # Count content
            cursor = conn.execute("SELECT COUNT(*) FROM knowledge_content")
            info["total_sections"] = cursor.fetchone()[0]

            # Count files
            cursor = conn.execute("SELECT COUNT(DISTINCT filename) FROM knowledge_content")
            info["total_files"] = cursor.fetchone()[0]

            # Count directives
            cursor = conn.execute("SELECT COUNT(*) FROM directives")
            info["total_directives"] = cursor.fetchone()[0]

            # Get file info
            cursor = conn.execute("SELECT filename, file_hash, indexed_at FROM pack_files ORDER BY indexed_at DESC")
            info["files"] = [
                {"filename": row[0], "hash": row[1], "indexed_at": row[2]}
                for row in cursor
            ]

        return info


def main() -> None:
    """CLI entry point for knowledge loader."""
    import argparse

    parser = argparse.ArgumentParser(description="WatchLockAI Sentinel Knowledge Loader")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild knowledge index")
    parser.add_argument("--packs", default="detection/knowledge/packs", help="Knowledge packs directory")
    parser.add_argument("--query", help="Query knowledge base")
    parser.add_argument("--info", action="store_true", help="Show index information")

    args = parser.parse_args()

    loader = KnowledgeLoader(args.packs)

    if args.rebuild_index:
        stats = loader.rebuild_index()
        print(f"Index rebuilt: {json.dumps(stats, indent=2)}")

    if args.query:
        hits = loader.query_knowledge(args.query)
        print(f"Query: {args.query}")
        print(f"Results: {len(hits)}")
        for i, hit in enumerate(hits, 1):
            print(f"\n{i}. {hit.filename}#{hit.section} (confidence: {hit.confidence:.3f})")
            print(f"   Lines: {hit.lines}")
            print(f"   Content: {hit.content[:200]}...")

    if args.info:
        info = loader.get_index_info()
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
