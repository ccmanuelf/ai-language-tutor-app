"""
Unit Tests for ContentPersistenceService
Session 129B - Coverage Fix

Tests error scenarios and edge cases for:
- save_content (update path, errors)
- save_learning_material (errors)
- save_processed_content_with_materials (errors)
- search_content (topics filtering)
- get_content_statistics (edge cases)
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.database.config import get_primary_db_session
from app.models.database import LearningMaterialDB, ProcessedContent
from app.services.content_persistence_service import ContentPersistenceService
from app.services.content_processor import (
    ContentMetadata,
    ContentType,
    LearningMaterial,
    LearningMaterialType,
    ProcessedContent as ProcessedContentDataclass,
)


class TestContentPersistenceService:
    """Test ContentPersistenceService error handling and edge cases"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.service = ContentPersistenceService(self.db)
        yield
        self.db.close()

    def _create_metadata(self, user_id=11001, content_id=None, source_url=None):
        """Helper to create ContentMetadata"""
        return ContentMetadata(
            content_id=content_id,
            title=f"Test Content {user_id}",
            content_type=ContentType.YOUTUBE_VIDEO,
            source_url=source_url or f"https://youtube.com/watch?v={user_id}",
            language="en",
            duration=300,
            word_count=500,
            difficulty_level="intermediate",
            topics=["grammar", "vocabulary"],
            author="Test Author",
            created_at=datetime.now(),
            file_size=1024,
        )

    @pytest.mark.asyncio
    async def test_save_content_update_existing(self):
        """Test save_content updates existing content"""
        user_id = 11001
        source_url = "https://youtube.com/watch?v=update_test"

        # Create initial content
        metadata1 = self._create_metadata(user_id=user_id, source_url=source_url)
        content1 = self.service.save_content(
            user_id=user_id,
            metadata=metadata1,
            raw_content="Original content",
            processed_content="Original processed",
            processing_stats={"version": 1},
        )

        assert content1 is not None
        original_id = content1.content_id

        # Update the same content
        metadata2 = self._create_metadata(user_id=user_id, source_url=source_url)
        metadata2.title = "Updated Title"
        content2 = self.service.save_content(
            user_id=user_id,
            metadata=metadata2,
            raw_content="Updated content",
            processed_content="Updated processed",
            processing_stats={"version": 2},
        )

        assert content2.content_id == original_id  # Same ID
        assert content2.title == "Updated Title"
        assert content2.processed_content == "Updated processed"
        assert content2.processing_stats["version"] == 2

    @pytest.mark.asyncio
    async def test_save_content_db_error(self):
        """Test save_content handles database errors"""
        metadata = self._create_metadata(user_id=12001)

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                self.service.save_content(
                    user_id=12001,
                    metadata=metadata,
                    raw_content="Test content",
                    processed_content="Test processed",
                )

    @pytest.mark.asyncio
    async def test_save_learning_material_db_error(self):
        """Test save_learning_material handles database errors"""
        # First create content
        metadata = self._create_metadata(user_id=13001)
        content = self.service.save_content(
            user_id=13001,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        material = LearningMaterial(
            material_id=None,
            content_id=content.content_id,
            material_type=LearningMaterialType.FLASHCARDS,
            title="Test Flashcard",
            content={"front": "Hello", "back": "Hola"},
            difficulty_level="beginner",
            estimated_time=5,
            tags=["greeting"],
        )

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                self.service.save_learning_material(
                    user_id=13001,
                    content_id=content.content_id,
                    material=material,
                )

    @pytest.mark.asyncio
    async def test_save_processed_content_with_materials_error(self):
        """Test save_processed_content_with_materials handles errors"""
        metadata = self._create_metadata(user_id=14001)

        material1 = LearningMaterial(
            material_id=None,
            content_id="temp_content_id",  # Will be replaced when saved
            material_type=LearningMaterialType.QUIZ,
            title="Test Quiz",
            content={"questions": []},
            difficulty_level="intermediate",
            estimated_time=10,
            tags=["quiz"],
        )

        processed_content = ProcessedContentDataclass(
            metadata=metadata,
            raw_content="Raw test",
            processed_content="Processed test",
            learning_materials=[material1],
            processing_stats={},
        )

        # Mock save_learning_material to raise an exception
        with patch.object(
            self.service,
            "save_learning_material",
            side_effect=Exception("Material save failed"),
        ):
            with pytest.raises(Exception, match="Material save failed"):
                self.service.save_processed_content_with_materials(
                    user_id=14001,
                    processed_content_dataclass=processed_content,
                )

    @pytest.mark.asyncio
    async def test_search_content_with_topics(self):
        """Test search_content with topics filter"""
        user_id = 15001

        # Create content with specific topics
        metadata1 = self._create_metadata(user_id=user_id)
        metadata1.topics = ["python", "programming", "tutorial"]
        content1 = self.service.save_content(
            user_id=user_id,
            metadata=metadata1,
            raw_content="Python content",
            processed_content="Python processed",
        )

        metadata2 = self._create_metadata(user_id=user_id)
        metadata2.source_url = "https://youtube.com/watch?v=different"
        metadata2.topics = ["javascript", "web", "development"]
        content2 = self.service.save_content(
            user_id=user_id,
            metadata=metadata2,
            raw_content="JS content",
            processed_content="JS processed",
        )

        # Search for Python topics
        results = self.service.search_content(
            user_id=user_id,
            topics=["python"],
        )

        assert len(results) >= 1
        assert any(c.content_id == content1.content_id for c in results)

    @pytest.mark.asyncio
    async def test_search_content_with_multiple_topics(self):
        """Test search_content with multiple topics (any match)"""
        user_id = 16001

        # Create content with specific topics
        metadata = self._create_metadata(user_id=user_id)
        metadata.topics = ["react", "frontend", "hooks"]
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="React content",
            processed_content="React processed",
        )

        # Search for multiple topics - should match if ANY topic matches
        results = self.service.search_content(
            user_id=user_id,
            topics=["react", "vue", "angular"],  # Only react matches
        )

        assert len(results) >= 1
        assert any(c.content_id == content.content_id for c in results)

    @pytest.mark.asyncio
    async def test_delete_content_not_found(self):
        """Test delete_content returns False when content not found"""
        result = self.service.delete_content(
            content_id="nonexistent_content_id",
            user_id=99999,
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_content_success_with_materials(self):
        """Test delete_content removes content and materials"""
        user_id = 17001

        # Create content with materials
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        material = LearningMaterial(
            material_id=None,
            content_id=content.content_id,
            material_type=LearningMaterialType.SUMMARY,
            title="Test Summary",
            content={"summary": "Brief summary"},
            difficulty_level="beginner",
            estimated_time=5,
            tags=["summary"],
        )

        self.service.save_learning_material(
            user_id=user_id,
            content_id=content.content_id,
            material=material,
        )

        # Delete content
        result = self.service.delete_content(
            content_id=content.content_id,
            user_id=user_id,
        )

        assert result is True

        # Verify content is deleted
        deleted_content = self.service.get_content_by_id(
            content_id=content.content_id,
            user_id=user_id,
        )
        assert deleted_content is None

    @pytest.mark.asyncio
    async def test_delete_content_db_error(self):
        """Test delete_content handles database errors"""
        user_id = 18001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                self.service.delete_content(
                    content_id=content.content_id,
                    user_id=user_id,
                )

    @pytest.mark.asyncio
    async def test_get_content_statistics_empty(self):
        """Test get_content_statistics with no content"""
        stats = self.service.get_content_statistics(user_id=99998)

        assert stats["total_content"] == 0
        assert stats["by_type"] == {}
        assert stats["by_language"] == {}
        assert stats["total_materials"] == 0

    @pytest.mark.asyncio
    async def test_get_content_statistics_with_data(self):
        """Test get_content_statistics with actual content"""
        user_id = 19001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Create material
        material = LearningMaterial(
            material_id=None,
            content_id=content.content_id,
            material_type=LearningMaterialType.FLASHCARDS,
            title="Test",
            content={},
            difficulty_level="beginner",
            estimated_time=5,
            tags=[],
        )

        self.service.save_learning_material(
            user_id=user_id,
            content_id=content.content_id,
            material=material,
        )

        # Get statistics
        stats = self.service.get_content_statistics(user_id=user_id)

        assert stats["total_content"] >= 1
        assert "youtube_video" in stats["by_type"]  # Database stores full enum value
        assert "en" in stats["by_language"]
        assert stats["total_materials"] >= 1

    @pytest.mark.asyncio
    async def test_save_processed_content_with_materials_rollback(self):
        """Test save_processed_content_with_materials handles rollback on failure"""
        metadata = self._create_metadata(user_id=20001)

        material = LearningMaterial(
            material_id=None,
            content_id="temp_id",
            material_type=LearningMaterialType.NOTES,
            title="Test Notes",
            content={"notes": "Test notes"},
            difficulty_level="intermediate",
            estimated_time=10,
            tags=["notes"],
        )

        processed_content = ProcessedContentDataclass(
            metadata=metadata,
            raw_content="Raw content",
            processed_content="Processed content",
            learning_materials=[material],
            processing_stats={},
        )

        # Mock db.commit to raise exception
        with patch.object(self.service.db, "commit", side_effect=Exception("Commit failed")):
            with pytest.raises(Exception, match="Commit failed"):
                self.service.save_processed_content_with_materials(
                    user_id=20001,
                    processed_content_dataclass=processed_content,
                )

    @pytest.mark.asyncio
    async def test_get_user_content_with_content_type_filter(self):
        """Test get_user_content with content_type filter"""
        user_id = 21001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Get content with content_type filter
        results = self.service.get_user_content(
            user_id=user_id,
            content_type="youtube_video",
        )

        assert len(results) >= 1
        assert all(c.content_type == "youtube_video" for c in results)

    @pytest.mark.asyncio
    async def test_get_user_content_with_language_filter(self):
        """Test get_user_content with language filter"""
        user_id = 22001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        metadata.language = "es"
        self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Get content with language filter
        results = self.service.get_user_content(
            user_id=user_id,
            language="es",
        )

        assert len(results) >= 1
        assert all(c.language == "es" for c in results)

    @pytest.mark.asyncio
    async def test_get_user_content_with_pagination(self):
        """Test get_user_content with limit and offset"""
        user_id = 23001

        # Create multiple content items
        for i in range(5):
            metadata = self._create_metadata(user_id=user_id)
            metadata.source_url = f"https://youtube.com/watch?v={user_id}_{i}"
            self.service.save_content(
                user_id=user_id,
                metadata=metadata,
                raw_content=f"Test {i}",
                processed_content=f"Test {i}",
            )

        # Get with pagination
        results_page1 = self.service.get_user_content(
            user_id=user_id,
            limit=2,
            offset=0,
        )

        results_page2 = self.service.get_user_content(
            user_id=user_id,
            limit=2,
            offset=2,
        )

        assert len(results_page1) == 2
        assert len(results_page2) == 2
        # Ensure different results
        assert results_page1[0].content_id != results_page2[0].content_id

    @pytest.mark.asyncio
    async def test_search_content_with_difficulty_filter(self):
        """Test search_content with difficulty level filter"""
        user_id = 24001

        # Create content with specific difficulty
        metadata = self._create_metadata(user_id=user_id)
        metadata.difficulty_level = "advanced"
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Advanced content",
            processed_content="Advanced processed",
        )

        # Search with difficulty filter
        results = self.service.search_content(
            user_id=user_id,
            difficulty="advanced",
        )

        assert len(results) >= 1
        assert any(c.content_id == content.content_id for c in results)

    @pytest.mark.asyncio
    async def test_get_learning_materials_with_user_filter(self):
        """Test get_learning_materials with user_id filter"""
        user_id = 25001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Create material
        material = LearningMaterial(
            material_id=None,
            content_id=content.content_id,
            material_type=LearningMaterialType.QUIZ,
            title="Test Quiz",
            content={"questions": []},
            difficulty_level="beginner",
            estimated_time=10,
            tags=["quiz"],
        )

        self.service.save_learning_material(
            user_id=user_id,
            content_id=content.content_id,
            material=material,
        )

        # Get materials with user filter
        materials = self.service.get_learning_materials(
            content_id=content.content_id,
            user_id=user_id,
        )

        assert len(materials) >= 1
        assert all(m.user_id == user_id for m in materials)

    @pytest.mark.asyncio
    async def test_get_learning_materials_with_type_filter(self):
        """Test get_learning_materials with material_type filter"""
        user_id = 26001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Create material
        material = LearningMaterial(
            material_id=None,
            content_id=content.content_id,
            material_type=LearningMaterialType.FLASHCARDS,
            title="Test Flashcards",
            content={"cards": []},
            difficulty_level="beginner",
            estimated_time=5,
            tags=["flashcards"],
        )

        self.service.save_learning_material(
            user_id=user_id,
            content_id=content.content_id,
            material=material,
        )

        # Get materials with type filter
        materials = self.service.get_learning_materials(
            content_id=content.content_id,
            material_type="flashcards",
        )

        assert len(materials) >= 1
        assert all(m.material_type == "flashcards" for m in materials)

    @pytest.mark.asyncio
    async def test_save_content_without_content_id(self):
        """Test save_content generates content_id when not provided"""
        user_id = 28001

        # Create metadata WITHOUT content_id
        metadata = ContentMetadata(
            content_id=None,  # No ID provided
            title="Test Content",
            content_type=ContentType.YOUTUBE_VIDEO,
            source_url="https://youtube.com/watch?v=test_no_id",
            language="en",
            duration=300,
            word_count=500,
            difficulty_level="intermediate",
            topics=["test"],
            author="Test Author",
            created_at=datetime.now(),
            file_size=1024,
        )

        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test content",
            processed_content="Test processed",
        )

        # Verify content_id was generated
        assert content.content_id is not None
        assert len(content.content_id) > 0

    @pytest.mark.asyncio
    async def test_save_learning_material_without_material_id(self):
        """Test save_learning_material generates material_id when not provided"""
        user_id = 29001

        # Create content first
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Create material WITHOUT material_id
        material = LearningMaterial(
            material_id=None,  # No ID provided
            content_id=content.content_id,
            material_type=LearningMaterialType.NOTES,
            title="Test Notes",
            content={"notes": "Test notes"},
            difficulty_level="beginner",
            estimated_time=5,
            tags=["notes"],
        )

        db_material = self.service.save_learning_material(
            user_id=user_id,
            content_id=content.content_id,
            material=material,
        )

        # Verify material_id was generated
        assert db_material.material_id is not None
        assert len(db_material.material_id) > 0

    @pytest.mark.asyncio
    async def test_search_content_with_text_query(self):
        """Test search_content with text search in title"""
        user_id = 30001

        # Create content with specific title
        metadata = self._create_metadata(user_id=user_id)
        metadata.title = "Python Programming Tutorial"
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Python content",
            processed_content="Python processed",
        )

        # Search with text query
        results = self.service.search_content(
            user_id=user_id,
            search_query="Python",
        )

        assert len(results) >= 1
        assert any(c.content_id == content.content_id for c in results)
        assert any("Python" in c.title for c in results)

    @pytest.mark.asyncio
    async def test_search_content_with_all_filters(self):
        """Test search_content with multiple filters combined"""
        user_id = 31001

        # Create content with all attributes
        metadata = self._create_metadata(user_id=user_id)
        metadata.title = "Advanced Spanish Grammar"
        metadata.language = "es"
        metadata.difficulty_level = "advanced"
        metadata.topics = ["grammar", "verbs", "conjugation"]
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Spanish grammar content",
            processed_content="Spanish grammar processed",
        )

        # Search with all filters
        results = self.service.search_content(
            user_id=user_id,
            search_query="Spanish",
            content_type="youtube_video",
            language="es",
            difficulty="advanced",
            topics=["grammar", "verbs"],
        )

        assert len(results) >= 1
        assert any(c.content_id == content.content_id for c in results)

    @pytest.mark.asyncio
    async def test_save_content_error_rollback(self):
        """Test save_content handles errors and rolls back"""
        user_id = 32001

        metadata = self._create_metadata(user_id=user_id)

        # Mock db.add to raise exception after being called
        original_add = self.service.db.add
        def mock_add_with_error(obj):
            original_add(obj)
            raise Exception("Database error during add")

        with patch.object(self.service.db, "add", side_effect=mock_add_with_error):
            with pytest.raises(Exception, match="Database error during add"):
                self.service.save_content(
                    user_id=user_id,
                    metadata=metadata,
                    raw_content="Test",
                    processed_content="Test",
                )

    @pytest.mark.asyncio
    async def test_search_content_with_empty_topics_list(self):
        """Test search_content with empty topics list (edge case)"""
        user_id = 33001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Search with empty topics list (should not filter)
        results = self.service.search_content(
            user_id=user_id,
            topics=[],  # Empty list
        )

        # Should still return results (no filtering applied)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_save_content_refresh_error(self):
        """Test save_content handles error after commit"""
        user_id = 34001

        metadata = self._create_metadata(user_id=user_id)

        # Mock db.refresh to raise exception
        with patch.object(self.service.db, "refresh", side_effect=Exception("Refresh error")):
            with pytest.raises(Exception, match="Refresh error"):
                self.service.save_content(
                    user_id=user_id,
                    metadata=metadata,
                    raw_content="Test",
                    processed_content="Test",
                )

    @pytest.mark.asyncio
    async def test_get_content_by_id_with_user_filter(self):
        """Test get_content_by_id with user_id filter"""
        user_id = 27001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Get content with user filter
        result = self.service.get_content_by_id(
            content_id=content.content_id,
            user_id=user_id,
        )

        assert result is not None
        assert result.content_id == content.content_id
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_content_by_id_without_user_filter(self):
        """Test get_content_by_id without user_id filter (global lookup)"""
        user_id = 35001

        # Create content
        metadata = self._create_metadata(user_id=user_id)
        content = self.service.save_content(
            user_id=user_id,
            metadata=metadata,
            raw_content="Test",
            processed_content="Test",
        )

        # Get content WITHOUT user filter (user_id=None)
        result = self.service.get_content_by_id(
            content_id=content.content_id,
            user_id=None,
        )

        assert result is not None
        assert result.content_id == content.content_id
        assert result.user_id == user_id
