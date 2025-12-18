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
        assert "youtube" in stats["by_type"]
        assert "en" in stats["by_language"]
        assert stats["total_materials"] >= 1
