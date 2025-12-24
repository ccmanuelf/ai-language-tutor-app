"""
ChromaDB Configuration for AI Language Tutor App

This module handles ChromaDB setup for vector storage used in:
- Document embeddings for content-driven conversations
- Conversation history embeddings for context retrieval
- Language learning content vectors for semantic search
- User-specific learning pattern analysis
"""

import logging
import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Manages ChromaDB operations for the AI Language Tutor App"""

    def __init__(self, persist_directory: str = "./data/chromadb"):
        """
        Initialize ChromaDB manager

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self._client: Optional[PersistentClient] = None
        self._embedding_model = None
        self._collections = {}

        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)

    @property
    def client(self) -> PersistentClient:
        """Get or create ChromaDB client"""
        if self._client is None:
            self._client = PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
        return self._client

    @property
    def embedding_model(self) -> SentenceTransformer:
        """Get or create sentence transformer model for embeddings"""
        if self._embedding_model is None:
            # Using a multilingual model that supports Chinese, French, German, Japanese
            self._embedding_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        return self._embedding_model

    def get_or_create_collection(
        self, name: str, metadata: Optional[Dict] = None
    ) -> Collection:
        """
        Get existing collection or create new one

        Args:
            name: Collection name
            metadata: Optional metadata for the collection

        Returns:
            ChromaDB Collection instance
        """
        if name in self._collections:
            return self._collections[name]

        try:
            collection = self.client.get_collection(name=name)
            logger.info(f"Retrieved existing collection: {name}")
        except ValueError:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=name, metadata=metadata or {}
            )
            logger.info(f"Created new collection: {name}")

        self._collections[name] = collection
        return collection

    def initialize_collections(self):
        """Initialize all required collections for the app"""
        collections = {
            "documents": {
                "metadata": {
                    "description": "Uploaded document embeddings for content-driven learning"
                }
            },
            "conversations": {
                "metadata": {
                    "description": "Conversation history embeddings for context retrieval"
                }
            },
            "learning_content": {
                "metadata": {
                    "description": "Language learning content vectors for semantic search"
                }
            },
            "user_patterns": {
                "metadata": {
                    "description": "User learning pattern analysis and recommendations"
                }
            },
            "vocabulary": {
                "metadata": {
                    "description": "Vocabulary words and phrases with multilingual embeddings"
                }
            },
        }

        for collection_name, config in collections.items():
            self.get_or_create_collection(collection_name, config["metadata"])
            logger.info(f"Initialized collection: {collection_name}")

    def add_document_embedding(
        self, user_id: str, document_id: str, content: str, metadata: Dict[str, Any]
    ) -> str:
        """
        Add document embedding to the documents collection

        Args:
            user_id: User ID who uploaded the document
            document_id: Unique document identifier
            content: Document text content
            metadata: Additional metadata (language, type, etc.)

        Returns:
            Embedding ID
        """
        collection = self.get_or_create_collection("documents")

        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()

        # Create unique ID
        embedding_id = f"{user_id}_{document_id}_{uuid4().hex[:8]}"

        # Add to collection
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[
                {
                    "user_id": user_id,
                    "document_id": document_id,
                    "timestamp": metadata.get("timestamp"),
                    "language": metadata.get("language", "unknown"),
                    "content_type": metadata.get("content_type", "text"),
                    **metadata,
                }
            ],
            ids=[embedding_id],
        )

        logger.info(f"Added document embedding: {embedding_id}")
        return embedding_id

    def add_conversation_embedding(
        self, user_id: str, conversation_id: str, content: str, metadata: Dict[str, Any]
    ) -> str:
        """
        Add conversation embedding for context retrieval

        Args:
            user_id: User ID
            conversation_id: Unique conversation identifier
            content: Conversation text content
            metadata: Additional metadata

        Returns:
            Embedding ID
        """
        collection = self.get_or_create_collection("conversations")

        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()

        # Create unique ID
        embedding_id = f"{user_id}_{conversation_id}_{uuid4().hex[:8]}"

        # Add to collection
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": metadata.get("timestamp"),
                    "language": metadata.get("language", "unknown"),
                    "turn_type": metadata.get("turn_type", "unknown"),  # user/assistant
                    **metadata,
                }
            ],
            ids=[embedding_id],
        )

        logger.info(f"Added conversation embedding: {embedding_id}")
        return embedding_id

    def search_similar_content(
        self,
        query: str,
        collection_name: str,
        user_id: str,
        language: Optional[str] = None,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Search for similar content using semantic similarity

        Args:
            query: Search query text
            collection_name: Name of collection to search
            user_id: Optional filter by user ID
            language: Optional filter by language
            n_results: Number of results to return

        Returns:
            Search results with documents, metadata, and distances
        """
        collection = self.get_or_create_collection(collection_name)

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Build where clause for filtering
        where_clause = {}
        if user_id:
            where_clause["user_id"] = user_id
        if language:
            where_clause["language"] = language

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"],
        )

        logger.info(
            f"Search in {collection_name}: {len(results['documents'][0])} results found"
        )
        return results

    def get_user_learning_patterns(
        self, user_id: str, language: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve user learning patterns for personalized recommendations

        Args:
            user_id: User ID
            language: Target language

        Returns:
            List of learning pattern data
        """
        results = self.search_similar_content(
            query="learning progress patterns",
            collection_name="user_patterns",
            user_id=user_id,
            language=language,
            n_results=10,
        )

        return [
            {"content": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def delete_user_data(self, user_id: str):
        """
        Delete all data for a specific user (GDPR compliance)

        Args:
            user_id: User ID to delete data for
        """
        collections_to_clean = ["documents", "conversations", "user_patterns"]

        for collection_name in collections_to_clean:
            try:
                collection = self.get_or_create_collection(collection_name)

                # Query all items for this user
                user_items = collection.get(where={"user_id": user_id})

                if user_items["ids"]:
                    collection.delete(ids=user_items["ids"])
                    logger.info(
                        f"Deleted {len(user_items['ids'])} items from {collection_name} for user {user_id}"
                    )

            except Exception as e:
                logger.error(f"Error deleting user data from {collection_name}: {e}")

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections"""
        stats = {}

        for collection_name in [
            "documents",
            "conversations",
            "learning_content",
            "user_patterns",
            "vocabulary",
        ]:
            try:
                collection = self.get_or_create_collection(collection_name)
                count = collection.count()
                stats[collection_name] = count
            except Exception as e:
                logger.error(f"Error getting stats for {collection_name}: {e}")
                stats[collection_name] = 0

        return stats

    def reset_collection(self, collection_name: str):
        """Reset a specific collection (remove all data)"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            # Remove from cache
            if collection_name in self._collections:
                del self._collections[collection_name]
        except ValueError:
            logger.info(f"Collection {collection_name} does not exist")

    def reset_all_collections(self):
        """Reset all collections (complete reset)"""
        collections = [
            "documents",
            "conversations",
            "learning_content",
            "user_patterns",
            "vocabulary",
        ]
        for collection_name in collections:
            self.reset_collection(collection_name)

        # Clear cache
        self._collections.clear()
        logger.info("All collections reset")


# Global ChromaDB manager instance
chroma_manager = ChromaDBManager()

# Convenience functions


def initialize_chromadb():
    """Initialize ChromaDB with all required collections"""
    chroma_manager.initialize_collections()


def get_chromadb_client():
    """Get ChromaDB client"""
    return chroma_manager.client


def search_documents(
    query: str, user_id: str, language: Optional[str] = None, n_results: int = 5
):
    """Search user documents"""
    return chroma_manager.search_similar_content(
        query=query,
        collection_name="documents",
        user_id=user_id,
        language=language,
        n_results=n_results,
    )


def search_conversations(
    query: str, user_id: str, language: Optional[str] = None, n_results: int = 5
):
    """Search conversation history"""
    return chroma_manager.search_similar_content(
        query=query,
        collection_name="conversations",
        user_id=user_id,
        language=language,
        n_results=n_results,
    )
