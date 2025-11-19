"""
Comprehensive tests for app/database/chromadb_config.py

Target: TRUE 100% coverage (statement + branch)
Current: 48.23% coverage (115 statements, 59 missed, 26 branches)
Missing: Lines 58-61, 80-86, 134-158, 179-203, 226-247, 260-268, 288-302, 313-315, 321-328, 332-338, 349, 354, 359, 370

Test Strategy:
1. Test ChromaDBManager initialization and lazy properties
2. Test collection management (get_or_create, initialize)
3. Test document embedding operations
4. Test conversation embedding operations
5. Test search functionality with various filters
6. Test user learning patterns retrieval
7. Test GDPR compliance (delete_user_data)
8. Test collection statistics and reset operations
9. Test all convenience functions
10. Test error handling paths
"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.database.chromadb_config import (
    ChromaDBManager,
    chroma_manager,
    get_chromadb_client,
    search_conversations,
)


class TestChromaDBManagerInitialization:
    """Test ChromaDBManager initialization"""

    def test_manager_initialization_default_directory(self):
        """Test manager initializes with default directory"""
        manager = ChromaDBManager()
        assert manager.persist_directory == "./data/chromadb"
        assert manager._client is None
        assert manager._embedding_model is None
        assert manager._collections == {}

    def test_manager_initialization_custom_directory(self):
        """Test manager initializes with custom directory"""
        custom_dir = "/tmp/test_chromadb"
        manager = ChromaDBManager(persist_directory=custom_dir)
        assert manager.persist_directory == custom_dir
        assert manager._client is None
        assert manager._embedding_model is None
        assert manager._collections == {}

    def test_directory_creation(self, tmp_path):
        """Test that persist directory is created if it doesn't exist"""
        test_dir = tmp_path / "new_chroma_dir"
        assert not test_dir.exists()

        manager = ChromaDBManager(persist_directory=str(test_dir))

        assert test_dir.exists()
        assert test_dir.is_dir()


class TestLazyProperties:
    """Test lazy initialization of client and embedding_model properties"""

    @patch("app.database.chromadb_config.PersistentClient")
    def test_client_property_lazy_initialization(
        self, mock_persistent_client, tmp_path
    ):
        """Test client property creates client on first access (covers lines 58-61)"""
        test_dir = tmp_path / "chromadb_test"
        manager = ChromaDBManager(persist_directory=str(test_dir))

        # Initially None
        assert manager._client is None

        # Access property - should create client
        client = manager.client

        # Verify client was created
        mock_persistent_client.assert_called_once()
        assert manager._client is not None

        # Second access should return same client (no new call)
        client2 = manager.client
        assert client == client2
        assert mock_persistent_client.call_count == 1

    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_embedding_model_property_lazy_initialization(
        self, mock_sentence_transformer, tmp_path
    ):
        """Test embedding_model property creates model on first access (covers lines 64-67)"""
        test_dir = tmp_path / "chromadb_test"
        manager = ChromaDBManager(persist_directory=str(test_dir))

        # Initially None
        assert manager._embedding_model is None

        # Access property - should create model
        model = manager.embedding_model

        # Verify model was created with multilingual model
        mock_sentence_transformer.assert_called_once_with(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
        assert manager._embedding_model is not None

        # Second access should return same model (no new call)
        model2 = manager.embedding_model
        assert model == model2
        assert mock_sentence_transformer.call_count == 1


class TestCollectionManagement:
    """Test collection creation and retrieval"""

    @patch("app.database.chromadb_config.PersistentClient")
    def test_get_or_create_collection_from_cache(self, mock_client_class, tmp_path):
        """Test getting collection from cache (lines 75-77)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Pre-populate cache
        mock_collection = Mock()
        manager._collections["test_collection"] = mock_collection

        # Get collection
        result = manager.get_or_create_collection("test_collection")

        # Should return cached collection without calling client
        assert result == mock_collection
        # Client should not be accessed since we returned from cache
        assert not manager._client

    @patch("app.database.chromadb_config.PersistentClient")
    def test_get_or_create_collection_exists(self, mock_client_class, tmp_path):
        """Test getting existing collection from ChromaDB (lines 79-81)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_collection = Mock()
        mock_client = Mock()
        mock_client.get_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        # Get collection
        result = manager.get_or_create_collection("existing_collection")

        # Should call get_collection
        mock_client.get_collection.assert_called_once_with(name="existing_collection")
        assert result == mock_collection
        assert manager._collections["existing_collection"] == mock_collection

    @patch("app.database.chromadb_config.PersistentClient")
    def test_get_or_create_collection_new(self, mock_client_class, tmp_path):
        """Test creating new collection when it doesn't exist (lines 82-87)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_collection = Mock()
        mock_client = Mock()
        # Simulate collection doesn't exist
        mock_client.get_collection.side_effect = ValueError("Collection not found")
        mock_client.create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        metadata = {"description": "Test collection"}
        result = manager.get_or_create_collection("new_collection", metadata=metadata)

        # Should try get_collection first, then create
        mock_client.get_collection.assert_called_once_with(name="new_collection")
        mock_client.create_collection.assert_called_once_with(
            name="new_collection", metadata=metadata
        )
        assert result == mock_collection
        assert manager._collections["new_collection"] == mock_collection

    @patch("app.database.chromadb_config.PersistentClient")
    def test_get_or_create_collection_new_no_metadata(
        self, mock_client_class, tmp_path
    ):
        """Test creating new collection without metadata"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_collection = Mock()
        mock_client = Mock()
        mock_client.get_collection.side_effect = ValueError("Collection not found")
        mock_client.create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        result = manager.get_or_create_collection("new_collection")

        # Should create with empty metadata
        mock_client.create_collection.assert_called_once_with(
            name="new_collection", metadata={}
        )

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_initialize_collections(self, mock_get_or_create, tmp_path):
        """Test initialize_collections creates all required collections (lines 92-112)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        manager.initialize_collections()

        # Should create 5 collections
        assert mock_get_or_create.call_count == 5

        # Verify each collection is created with correct metadata
        expected_calls = [
            call(
                "documents",
                {
                    "description": "Uploaded document embeddings for content-driven learning"
                },
            ),
            call(
                "conversations",
                {
                    "description": "Conversation history embeddings for context retrieval"
                },
            ),
            call(
                "learning_content",
                {
                    "description": "Language learning content vectors for semantic search"
                },
            ),
            call(
                "user_patterns",
                {"description": "User learning pattern analysis and recommendations"},
            ),
            call(
                "vocabulary",
                {
                    "description": "Vocabulary words and phrases with multilingual embeddings"
                },
            ),
        ]
        mock_get_or_create.assert_has_calls(expected_calls, any_order=False)


class TestDocumentEmbeddings:
    """Test document embedding operations"""

    @patch("app.database.chromadb_config.uuid4")
    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_add_document_embedding(
        self, mock_transformer_class, mock_get_collection, mock_uuid, tmp_path
    ):
        """Test adding document embedding (lines 134-158)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock embedding model
        mock_model = Mock()
        mock_embedding = [0.1, 0.2, 0.3]
        mock_model.encode.return_value = Mock(tolist=Mock(return_value=mock_embedding))
        mock_transformer_class.return_value = mock_model

        # Mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock uuid
        mock_uuid.return_value = Mock(hex="abcd1234")

        # Add document
        user_id = "user123"
        document_id = "doc456"
        content = "This is test content"
        metadata = {
            "timestamp": "2024-01-01",
            "language": "en",
            "content_type": "pdf",
            "extra_field": "extra_value",
        }

        result = manager.add_document_embedding(user_id, document_id, content, metadata)

        # Verify embedding was generated
        mock_model.encode.assert_called_once_with(content)

        # Verify collection was accessed
        mock_get_collection.assert_called_once_with("documents")

        # Verify add was called with correct parameters
        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args[1]

        assert call_kwargs["embeddings"] == [mock_embedding]
        assert call_kwargs["documents"] == [content]
        assert call_kwargs["ids"] == ["user123_doc456_abcd1234"]

        # Verify metadata includes all fields
        assert len(call_kwargs["metadatas"]) == 1
        metadata_dict = call_kwargs["metadatas"][0]
        assert metadata_dict["user_id"] == user_id
        assert metadata_dict["document_id"] == document_id
        assert metadata_dict["timestamp"] == "2024-01-01"
        assert metadata_dict["language"] == "en"
        assert metadata_dict["content_type"] == "pdf"
        assert metadata_dict["extra_field"] == "extra_value"

        # Verify return value
        assert result == "user123_doc456_abcd1234"

    @patch("app.database.chromadb_config.uuid4")
    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_add_document_embedding_minimal_metadata(
        self, mock_transformer_class, mock_get_collection, mock_uuid, tmp_path
    ):
        """Test adding document with minimal metadata (default values)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_model = Mock()
        mock_embedding = [0.1, 0.2]
        mock_model.encode.return_value = Mock(tolist=Mock(return_value=mock_embedding))
        mock_transformer_class.return_value = mock_model

        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        mock_uuid.return_value = Mock(hex="xyz789")

        # Minimal metadata
        metadata = {}

        result = manager.add_document_embedding("u1", "d1", "content", metadata)

        # Verify defaults are applied
        call_kwargs = mock_collection.add.call_args[1]
        metadata_dict = call_kwargs["metadatas"][0]
        assert metadata_dict["language"] == "unknown"
        assert metadata_dict["content_type"] == "text"
        assert metadata_dict["timestamp"] is None


class TestConversationEmbeddings:
    """Test conversation embedding operations"""

    @patch("app.database.chromadb_config.uuid4")
    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_add_conversation_embedding(
        self, mock_transformer_class, mock_get_collection, mock_uuid, tmp_path
    ):
        """Test adding conversation embedding (lines 179-203)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock embedding model
        mock_model = Mock()
        mock_embedding = [0.4, 0.5, 0.6]
        mock_model.encode.return_value = Mock(tolist=Mock(return_value=mock_embedding))
        mock_transformer_class.return_value = mock_model

        # Mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock uuid
        mock_uuid.return_value = Mock(hex="conv1234")

        # Add conversation
        user_id = "user789"
        conversation_id = "conv456"
        content = "User: Hello. Assistant: Hi!"
        metadata = {
            "timestamp": "2024-01-02",
            "language": "fr",
            "turn_type": "assistant",
            "session_id": "session123",
        }

        result = manager.add_conversation_embedding(
            user_id, conversation_id, content, metadata
        )

        # Verify embedding was generated
        mock_model.encode.assert_called_once_with(content)

        # Verify collection was accessed
        mock_get_collection.assert_called_once_with("conversations")

        # Verify add was called with correct parameters
        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args[1]

        assert call_kwargs["embeddings"] == [mock_embedding]
        assert call_kwargs["documents"] == [content]
        assert call_kwargs["ids"] == ["user789_conv456_conv1234"]

        # Verify metadata
        metadata_dict = call_kwargs["metadatas"][0]
        assert metadata_dict["user_id"] == user_id
        assert metadata_dict["conversation_id"] == conversation_id
        assert metadata_dict["timestamp"] == "2024-01-02"
        assert metadata_dict["language"] == "fr"
        assert metadata_dict["turn_type"] == "assistant"
        assert metadata_dict["session_id"] == "session123"

        # Verify return value
        assert result == "user789_conv456_conv1234"

    @patch("app.database.chromadb_config.uuid4")
    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_add_conversation_embedding_minimal_metadata(
        self, mock_transformer_class, mock_get_collection, mock_uuid, tmp_path
    ):
        """Test adding conversation with minimal metadata (default values)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_model = Mock()
        mock_embedding = [0.7, 0.8]
        mock_model.encode.return_value = Mock(tolist=Mock(return_value=mock_embedding))
        mock_transformer_class.return_value = mock_model

        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        mock_uuid.return_value = Mock(hex="abc999")

        # Minimal metadata
        metadata = {}

        result = manager.add_conversation_embedding("u2", "c2", "content", metadata)

        # Verify defaults are applied
        call_kwargs = mock_collection.add.call_args[1]
        metadata_dict = call_kwargs["metadatas"][0]
        assert metadata_dict["language"] == "unknown"
        assert metadata_dict["turn_type"] == "unknown"
        assert metadata_dict["timestamp"] is None


class TestSearchFunctionality:
    """Test semantic search operations"""

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_search_similar_content_no_filters(
        self, mock_transformer_class, mock_get_collection, tmp_path
    ):
        """Test search without user_id or language filters (lines 226-247)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock embedding model
        mock_model = Mock()
        mock_query_embedding = [0.9, 0.8, 0.7]
        mock_model.encode.return_value = Mock(
            tolist=Mock(return_value=mock_query_embedding)
        )
        mock_transformer_class.return_value = mock_model

        # Mock collection
        mock_collection = Mock()
        mock_search_results = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"key": "val1"}, {"key": "val2"}]],
            "distances": [[0.1, 0.2]],
        }
        mock_collection.query.return_value = mock_search_results
        mock_get_collection.return_value = mock_collection

        # Search without filters
        results = manager.search_similar_content(
            query="test query",
            collection_name="documents",
            user_id=None,
            language=None,
            n_results=5,
        )

        # Verify embedding was generated
        mock_model.encode.assert_called_once_with("test query")

        # Verify collection query was called correctly
        mock_collection.query.assert_called_once_with(
            query_embeddings=[mock_query_embedding],
            n_results=5,
            where=None,  # No filters
            include=["documents", "metadatas", "distances"],
        )

        assert results == mock_search_results

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_search_similar_content_with_user_filter(
        self, mock_transformer_class, mock_get_collection, tmp_path
    ):
        """Test search with user_id filter (lines 226-247)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_model = Mock()
        mock_query_embedding = [0.1, 0.2]
        mock_model.encode.return_value = Mock(
            tolist=Mock(return_value=mock_query_embedding)
        )
        mock_transformer_class.return_value = mock_model

        mock_collection = Mock()
        mock_search_results = {
            "documents": [["result"]],
            "metadatas": [[{}]],
            "distances": [[0.1]],
        }
        mock_collection.query.return_value = mock_search_results
        mock_get_collection.return_value = mock_collection

        # Search with user_id filter only
        results = manager.search_similar_content(
            query="query",
            collection_name="conversations",
            user_id="user123",
            language=None,
            n_results=3,
        )

        # Verify where clause includes user_id
        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs["where"] == {"user_id": "user123"}

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_search_similar_content_with_language_filter(
        self, mock_transformer_class, mock_get_collection, tmp_path
    ):
        """Test search with language filter (lines 226-247)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_model = Mock()
        mock_query_embedding = [0.3, 0.4]
        mock_model.encode.return_value = Mock(
            tolist=Mock(return_value=mock_query_embedding)
        )
        mock_transformer_class.return_value = mock_model

        mock_collection = Mock()
        mock_search_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_collection.query.return_value = mock_search_results
        mock_get_collection.return_value = mock_collection

        # Search with language filter only
        results = manager.search_similar_content(
            query="query",
            collection_name="learning_content",
            user_id=None,
            language="fr",
            n_results=10,
        )

        # Verify where clause includes language
        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs["where"] == {"language": "fr"}

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    @patch("app.database.chromadb_config.SentenceTransformer")
    def test_search_similar_content_with_both_filters(
        self, mock_transformer_class, mock_get_collection, tmp_path
    ):
        """Test search with both user_id and language filters (lines 226-247)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_model = Mock()
        mock_query_embedding = [0.5, 0.6]
        mock_model.encode.return_value = Mock(
            tolist=Mock(return_value=mock_query_embedding)
        )
        mock_transformer_class.return_value = mock_model

        mock_collection = Mock()
        mock_search_results = {
            "documents": [["a", "b"]],
            "metadatas": [[{}, {}]],
            "distances": [[0.1, 0.2]],
        }
        mock_collection.query.return_value = mock_search_results
        mock_get_collection.return_value = mock_collection

        # Search with both filters
        results = manager.search_similar_content(
            query="query",
            collection_name="vocabulary",
            user_id="user456",
            language="zh",
            n_results=7,
        )

        # Verify where clause includes both filters
        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs["where"] == {"user_id": "user456", "language": "zh"}


class TestUserLearningPatterns:
    """Test user learning patterns retrieval"""

    @patch("app.database.chromadb_config.ChromaDBManager.search_similar_content")
    def test_get_user_learning_patterns(self, mock_search, tmp_path):
        """Test get_user_learning_patterns method (lines 260-268)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock search results
        mock_search.return_value = {
            "documents": [["pattern1", "pattern2", "pattern3"]],
            "metadatas": [
                [
                    {"type": "vocab", "score": 0.9},
                    {"type": "grammar", "score": 0.8},
                    {"type": "reading", "score": 0.7},
                ]
            ],
            "distances": [[0.1, 0.2, 0.3]],
        }

        # Get patterns
        results = manager.get_user_learning_patterns("user999", "es")

        # Verify search was called correctly
        mock_search.assert_called_once_with(
            query="learning progress patterns",
            collection_name="user_patterns",
            user_id="user999",
            language="es",
            n_results=10,
        )

        # Verify results are formatted correctly
        assert len(results) == 3
        assert results[0] == {
            "content": "pattern1",
            "metadata": {"type": "vocab", "score": 0.9},
            "distance": 0.1,
        }
        assert results[1] == {
            "content": "pattern2",
            "metadata": {"type": "grammar", "score": 0.8},
            "distance": 0.2,
        }
        assert results[2] == {
            "content": "pattern3",
            "metadata": {"type": "reading", "score": 0.7},
            "distance": 0.3,
        }


class TestGDPRCompliance:
    """Test GDPR data deletion"""

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_delete_user_data_with_items(self, mock_get_collection, tmp_path):
        """Test deleting user data when items exist (lines 288-302)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock collections
        mock_doc_collection = Mock()
        mock_doc_collection.get.return_value = {"ids": ["id1", "id2", "id3"]}

        mock_conv_collection = Mock()
        mock_conv_collection.get.return_value = {"ids": ["id4", "id5"]}

        mock_pattern_collection = Mock()
        mock_pattern_collection.get.return_value = {"ids": ["id6"]}

        def get_collection_side_effect(name):
            if name == "documents":
                return mock_doc_collection
            elif name == "conversations":
                return mock_conv_collection
            elif name == "user_patterns":
                return mock_pattern_collection
            return Mock()

        mock_get_collection.side_effect = get_collection_side_effect

        # Delete user data
        manager.delete_user_data("user_to_delete")

        # Verify all collections were queried
        mock_doc_collection.get.assert_called_once_with(
            where={"user_id": "user_to_delete"}
        )
        mock_conv_collection.get.assert_called_once_with(
            where={"user_id": "user_to_delete"}
        )
        mock_pattern_collection.get.assert_called_once_with(
            where={"user_id": "user_to_delete"}
        )

        # Verify deletions
        mock_doc_collection.delete.assert_called_once_with(ids=["id1", "id2", "id3"])
        mock_conv_collection.delete.assert_called_once_with(ids=["id4", "id5"])
        mock_pattern_collection.delete.assert_called_once_with(ids=["id6"])

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_delete_user_data_no_items(self, mock_get_collection, tmp_path):
        """Test deleting user data when no items exist"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock collections with no items
        mock_collection = Mock()
        mock_collection.get.return_value = {"ids": []}  # Empty list
        mock_get_collection.return_value = mock_collection

        # Delete user data
        manager.delete_user_data("user_no_data")

        # Verify get was called but delete was not (no items to delete)
        assert mock_collection.get.call_count == 3
        mock_collection.delete.assert_not_called()

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_delete_user_data_with_error(self, mock_get_collection, tmp_path):
        """Test delete_user_data handles errors gracefully"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # First collection succeeds, second raises error, third succeeds
        mock_collection1 = Mock()
        mock_collection1.get.return_value = {"ids": ["id1"]}

        mock_collection2 = Mock()
        mock_collection2.get.side_effect = Exception("Database error")

        mock_collection3 = Mock()
        mock_collection3.get.return_value = {"ids": ["id3"]}

        call_count = [0]

        def get_collection_side_effect(name):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_collection1
            elif call_count[0] == 2:
                return mock_collection2
            else:
                return mock_collection3

        mock_get_collection.side_effect = get_collection_side_effect

        # Should not raise exception despite error
        manager.delete_user_data("user123")

        # Verify first and third collections were processed
        mock_collection1.delete.assert_called_once_with(ids=["id1"])
        mock_collection3.delete.assert_called_once_with(ids=["id3"])


class TestCollectionStatistics:
    """Test collection statistics and management"""

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_get_collection_stats(self, mock_get_collection, tmp_path):
        """Test get_collection_stats method (lines 313-328)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Mock different counts for each collection
        def collection_factory(count):
            mock_coll = Mock()
            mock_coll.count.return_value = count
            return mock_coll

        collections = {
            "documents": collection_factory(100),
            "conversations": collection_factory(250),
            "learning_content": collection_factory(50),
            "user_patterns": collection_factory(30),
            "vocabulary": collection_factory(500),
        }

        mock_get_collection.side_effect = lambda name: collections[name]

        # Get stats
        stats = manager.get_collection_stats()

        # Verify all collections were queried
        assert mock_get_collection.call_count == 5

        # Verify stats
        assert stats == {
            "documents": 100,
            "conversations": 250,
            "learning_content": 50,
            "user_patterns": 30,
            "vocabulary": 500,
        }

    @patch("app.database.chromadb_config.ChromaDBManager.get_or_create_collection")
    def test_get_collection_stats_with_error(self, mock_get_collection, tmp_path):
        """Test get_collection_stats handles errors gracefully"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        call_count = [0]

        def get_collection_side_effect(name):
            call_count[0] += 1
            mock_coll = Mock()
            if call_count[0] == 2:  # Second call raises error
                mock_coll.count.side_effect = Exception("Count failed")
            else:
                mock_coll.count.return_value = 10
            return mock_coll

        mock_get_collection.side_effect = get_collection_side_effect

        # Get stats
        stats = manager.get_collection_stats()

        # Verify error collection has 0 count
        assert stats["conversations"] == 0
        # Other collections should have 10
        assert stats["documents"] == 10
        assert stats["learning_content"] == 10

    @patch("app.database.chromadb_config.PersistentClient")
    def test_reset_collection_exists(self, mock_client_class, tmp_path):
        """Test reset_collection when collection exists (lines 332-338)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Pre-populate cache
        manager._collections["test_collection"] = Mock()

        # Reset collection
        manager.reset_collection("test_collection")

        # Verify delete was called
        mock_client.delete_collection.assert_called_once_with(name="test_collection")

        # Verify collection removed from cache
        assert "test_collection" not in manager._collections

    @patch("app.database.chromadb_config.PersistentClient")
    def test_reset_collection_not_exists(self, mock_client_class, tmp_path):
        """Test reset_collection when collection doesn't exist"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_client = Mock()
        mock_client.delete_collection.side_effect = ValueError("Collection not found")
        mock_client_class.return_value = mock_client

        # Reset non-existent collection - should not raise exception
        manager.reset_collection("nonexistent")

        # Verify delete was attempted
        mock_client.delete_collection.assert_called_once_with(name="nonexistent")

    @patch("app.database.chromadb_config.PersistentClient")
    def test_reset_collection_not_in_cache(self, mock_client_class, tmp_path):
        """Test reset_collection when collection exists but not in cache (covers line 325->exit)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Cache is empty (collection not in cache)
        assert "test_collection" not in manager._collections

        # Reset collection that exists in DB but not in cache
        manager.reset_collection("test_collection")

        # Verify delete was called
        mock_client.delete_collection.assert_called_once_with(name="test_collection")

        # Verify cache check doesn't fail (the else/exit branch of line 325)
        assert "test_collection" not in manager._collections

    @patch("app.database.chromadb_config.ChromaDBManager.reset_collection")
    def test_reset_all_collections(self, mock_reset, tmp_path):
        """Test reset_all_collections (lines 344-354)"""
        manager = ChromaDBManager(persist_directory=str(tmp_path / "chromadb"))

        # Pre-populate cache
        manager._collections = {
            "documents": Mock(),
            "conversations": Mock(),
            "other": Mock(),
        }

        # Reset all
        manager.reset_all_collections()

        # Verify reset_collection called for each collection
        assert mock_reset.call_count == 5
        expected_calls = [
            call("documents"),
            call("conversations"),
            call("learning_content"),
            call("user_patterns"),
            call("vocabulary"),
        ]
        mock_reset.assert_has_calls(expected_calls, any_order=False)

        # Verify cache is cleared
        assert manager._collections == {}


class TestConvenienceFunctions:
    """Test global convenience functions"""

    def test_initialize_chromadb(self):
        """Test initialize_chromadb convenience function (line 361)"""
        from app.database import chromadb_config

        with patch("app.database.chromadb_config.chroma_manager") as mock_manager:
            chromadb_config.initialize_chromadb()
            mock_manager.initialize_collections.assert_called_once()

    @patch("app.database.chromadb_config.chroma_manager")
    def test_get_chromadb_client(self, mock_manager):
        """Test get_chromadb_client convenience function (line 366)"""
        mock_client = Mock()
        mock_manager.client = mock_client

        result = get_chromadb_client()

        assert result == mock_client

    def test_search_documents(self):
        """Test search_documents convenience function (line 370)"""
        from app.database import chromadb_config

        with patch("app.database.chromadb_config.chroma_manager") as mock_manager:
            mock_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            mock_manager.search_similar_content.return_value = mock_results

            result = chromadb_config.search_documents(
                query="test query", user_id="user123", language="en", n_results=3
            )

            mock_manager.search_similar_content.assert_called_once_with(
                query="test query",
                collection_name="documents",
                user_id="user123",
                language="en",
                n_results=3,
            )
            assert result == mock_results

    def test_search_documents_no_language(self):
        """Test search_documents without language parameter"""
        from app.database import chromadb_config

        with patch("app.database.chromadb_config.chroma_manager") as mock_manager:
            mock_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            mock_manager.search_similar_content.return_value = mock_results

            result = chromadb_config.search_documents(
                query="query", user_id="u1", n_results=5
            )

            # language should default to None
            call_kwargs = mock_manager.search_similar_content.call_args[1]
            assert call_kwargs["language"] is None

    @patch("app.database.chromadb_config.chroma_manager")
    def test_search_conversations(self, mock_manager):
        """Test search_conversations convenience function (line 381)"""
        mock_results = {
            "documents": [["conv"]],
            "metadatas": [[{}]],
            "distances": [[0.1]],
        }
        mock_manager.search_similar_content.return_value = mock_results

        result = search_conversations(
            query="conversation query", user_id="user456", language="fr", n_results=10
        )

        mock_manager.search_similar_content.assert_called_once_with(
            query="conversation query",
            collection_name="conversations",
            user_id="user456",
            language="fr",
            n_results=10,
        )
        assert result == mock_results

    @patch("app.database.chromadb_config.chroma_manager")
    def test_search_conversations_no_language(self, mock_manager):
        """Test search_conversations without language parameter"""
        mock_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_manager.search_similar_content.return_value = mock_results

        result = search_conversations(query="query", user_id="u2", n_results=2)

        # language should default to None
        call_kwargs = mock_manager.search_similar_content.call_args[1]
        assert call_kwargs["language"] is None


class TestGlobalInstance:
    """Test global chroma_manager instance"""

    def test_global_instance_exists(self):
        """Test that global chroma_manager instance exists"""
        assert chroma_manager is not None
        assert isinstance(chroma_manager, ChromaDBManager)

    def test_global_instance_default_directory(self):
        """Test global instance has correct default directory"""
        assert chroma_manager.persist_directory == "./data/chromadb"
