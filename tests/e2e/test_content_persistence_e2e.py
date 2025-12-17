"""
End-to-End Tests for Content Persistence
AI Language Tutor App - Session 128

Tests:
- Content creation and retrieval
- Learning materials association
- Content search and filtering
- Content organization (topics, difficulty)
- Content deletion (with cascading materials)
- Multi-user content isolation
- Content statistics
"""

import uuid
from datetime import datetime

import pytest

from app.database.config import get_primary_db_session
from app.models.database import LearningMaterialDB, ProcessedContent
from app.models.simple_user import SimpleUser, UserRole
from app.services.content_persistence_service import ContentPersistenceService
from app.services.content_processor import (
    ContentMetadata,
    ContentType,
    LearningMaterial,
    LearningMaterialType,
)
from app.services.content_processor import (
    ProcessedContent as ProcessedContentDataclass,
)


class TestContentPersistenceE2E:
    """E2E tests for content persistence functionality"""

    def _unique_id(self, prefix="test"):
        """Generate unique ID for test data"""
        return f"{prefix}_{str(uuid.uuid4())[:8]}"

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.service = ContentPersistenceService(self.db)

        # Create test user directly in database
        unique_id = str(uuid.uuid4())[:8]
        test_user = SimpleUser(
            user_id=f"content_test_user_{unique_id}",
            username="Content Test User",
            email=f"content_test_{unique_id}@example.com",
            password_hash="test_hash",
            role=UserRole.CHILD,
        )
        self.db.add(test_user)
        self.db.commit()
        self.db.refresh(test_user)
        self.user_id = test_user.id

        yield

        # Cleanup
        self.db.close()

    def test_save_and_retrieve_youtube_content(self):
        """Test saving and retrieving YouTube content"""
        # Create content metadata
        content_id = self._unique_id("yt_test")
        metadata = ContentMetadata(
            content_id=content_id,
            title="Learn Spanish Basics",
            content_type=ContentType.YOUTUBE_VIDEO,
            source_url="https://youtube.com/watch?v=test123",
            language="es",
            duration=15.5,  # 15.5 minutes
            word_count=2500,
            difficulty_level="beginner",
            topics=["grammar", "vocabulary", "pronunciation"],
            author="Spanish Teacher",
            created_at=datetime.now(),
        )

        raw_content = "Este es el contenido original del video..."
        processed_content = "This is the processed video content..."
        processing_stats = {
            "extraction_time": 2.5,
            "processing_time": 1.2,
            "success": True,
        }

        # Save content
        saved_content = self.service.save_content(
            user_id=self.user_id,
            metadata=metadata,
            raw_content=raw_content,
            processed_content=processed_content,
            processing_stats=processing_stats,
        )

        assert saved_content is not None
        assert saved_content.content_id == content_id
        assert saved_content.user_id == self.user_id
        assert saved_content.title == "Learn Spanish Basics"
        assert saved_content.content_type == "youtube_video"
        assert saved_content.language == "es"
        assert saved_content.word_count == 2500
        assert saved_content.difficulty_level == "beginner"
        assert len(saved_content.topics) == 3
        assert "grammar" in saved_content.topics

        # Retrieve content
        retrieved = self.service.get_content_by_id(content_id, self.user_id)
        assert retrieved is not None
        assert retrieved.content_id == content_id
        assert retrieved.title == "Learn Spanish Basics"

        print("✅ YouTube content save/retrieve test passed")

    def test_save_learning_materials(self):
        """Test saving learning materials associated with content"""
        # First create content
        content_id = self._unique_id("content_with_materials")
        metadata = ContentMetadata(
            content_id=content_id,
            title="French Vocabulary Lesson",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/french_vocab.pdf",
            language="fr",
            duration=None,
            word_count=1500,
            difficulty_level="intermediate",
            topics=["vocabulary"],
            author="French Teacher",
            created_at=datetime.now(),
        )

        saved_content = self.service.save_content(
            user_id=self.user_id,
            metadata=metadata,
            raw_content="Raw French content...",
            processed_content="Processed French content...",
        )

        # Create learning material
        material_id = self._unique_id("material")
        material = LearningMaterial(
            material_id=material_id,
            content_id=saved_content.content_id,
            material_type=LearningMaterialType.FLASHCARDS,
            title="French Vocabulary Flashcards",
            content={
                "cards": [
                    {"front": "Bonjour", "back": "Hello"},
                    {"front": "Merci", "back": "Thank you"},
                    {"front": "Au revoir", "back": "Goodbye"},
                ]
            },
            difficulty_level="intermediate",
            estimated_time=10,
            tags=["vocabulary", "basics"],
        )

        # Save material
        saved_material = self.service.save_learning_material(
            user_id=self.user_id,
            content_id=saved_content.content_id,
            material=material,
        )

        assert saved_material is not None
        assert saved_material.material_id == material_id
        assert saved_material.content_id == saved_content.content_id
        assert saved_material.material_type == "flashcards"
        assert len(saved_material.content["cards"]) == 3

        # Retrieve materials
        materials = self.service.get_learning_materials(
            saved_content.content_id, self.user_id
        )
        assert len(materials) == 1
        assert materials[0].material_id == material_id

        print("✅ Learning materials test passed")

    def test_save_complete_content_with_materials(self):
        """Test saving complete ProcessedContent with all materials"""
        # Create complete processed content dataclass
        content_id = self._unique_id("complete_content")
        metadata = ContentMetadata(
            content_id=content_id,
            title="German Grammar Guide",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/german_grammar.pdf",
            language="de",
            duration=None,
            word_count=3000,
            difficulty_level="advanced",
            topics=["grammar", "syntax"],
            author="German Expert",
            created_at=datetime.now(),
        )

        materials = [
            LearningMaterial(
                material_id=self._unique_id("mat_summary"),
                content_id=content_id,
                material_type=LearningMaterialType.SUMMARY,
                title="Grammar Summary",
                content={"summary": "Key grammar points..."},
                difficulty_level="advanced",
                estimated_time=5,
                tags=["summary"],
            ),
            LearningMaterial(
                material_id=self._unique_id("mat_quiz"),
                content_id=content_id,
                material_type=LearningMaterialType.QUIZ,
                title="Grammar Quiz",
                content={
                    "questions": [
                        {
                            "question": "What is the dative case used for?",
                            "options": ["A", "B", "C", "D"],
                            "answer": "A",
                        }
                    ]
                },
                difficulty_level="advanced",
                estimated_time=15,
                tags=["quiz", "practice"],
            ),
        ]

        processed_content = ProcessedContentDataclass(
            metadata=metadata,
            raw_content="Raw German grammar content...",
            processed_content="Processed German grammar content...",
            learning_materials=materials,
            processing_stats={"success": True},
        )

        # Save complete content
        saved = self.service.save_processed_content_with_materials(
            user_id=self.user_id,
            processed_content_dataclass=processed_content,
        )

        assert saved is not None
        assert saved.content_id == content_id

        # Verify all materials were saved
        all_materials = self.service.get_learning_materials(
            saved.content_id, self.user_id
        )
        assert len(all_materials) == 2

        material_types = [m.material_type for m in all_materials]
        assert "summary" in material_types
        assert "quiz" in material_types

        print("✅ Complete content with materials test passed")

    def test_search_content_by_filters(self):
        """Test searching content with multiple filters"""
        # Create multiple content items
        for i in range(5):
            content_id = self._unique_id(f"search_test_{i}")
            metadata = ContentMetadata(
                content_id=content_id,
                title=f"Spanish Lesson {i}",
                content_type=ContentType.YOUTUBE_VIDEO,
                source_url=f"https://youtube.com/watch?v=test{i}",
                language="es",
                duration=10.0,
                word_count=1000,
                difficulty_level="beginner" if i < 3 else "intermediate",
                topics=["grammar"] if i % 2 == 0 else ["vocabulary"],
                author="Test Author",
                created_at=datetime.now(),
            )

            self.service.save_content(
                user_id=self.user_id,
                metadata=metadata,
                raw_content=f"Content {i}",
                processed_content=f"Processed {i}",
            )

        # Search by language
        spanish_content = self.service.get_user_content(
            user_id=self.user_id,
            language="es",
        )
        assert len(spanish_content) == 5

        # Search by content type
        videos = self.service.get_user_content(
            user_id=self.user_id,
            content_type="youtube_video",
        )
        assert len(videos) == 5

        # Search by difficulty
        beginner = self.service.search_content(
            user_id=self.user_id,
            difficulty="beginner",
        )
        assert len(beginner) == 3

        # Search by topics
        grammar_content = self.service.search_content(
            user_id=self.user_id,
            topics=["grammar"],
        )
        assert len(grammar_content) >= 2  # At least items 0, 2, 4

        # Search by title text
        lesson_2 = self.service.search_content(
            user_id=self.user_id,
            search_query="Lesson 2",
        )
        assert len(lesson_2) >= 1
        assert any("Lesson 2" in c.title for c in lesson_2)

        print("✅ Content search test passed")

    def test_multi_user_content_isolation(self):
        """Test that users can only access their own content"""
        # Create second user
        unique_id_2 = str(uuid.uuid4())[:8]
        test_user_2 = SimpleUser(
            user_id=f"content_test_user_2_{unique_id_2}",
            username="Content Test User 2",
            email=f"content_test_2_{unique_id_2}@example.com",
            password_hash="test_hash",
            role=UserRole.CHILD,
        )
        self.db.add(test_user_2)
        self.db.commit()
        self.db.refresh(test_user_2)
        user_2_id = test_user_2.id

        # Create content for user 1
        content_id_1 = self._unique_id("user1_content")
        metadata_1 = ContentMetadata(
            content_id=content_id_1,
            title="User 1 Content",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/user1.pdf",
            language="en",
            duration=None,
            word_count=1000,
            difficulty_level="beginner",
            topics=["test"],
            author="User 1",
            created_at=datetime.now(),
        )

        self.service.save_content(
            user_id=self.user_id,
            metadata=metadata_1,
            raw_content="User 1 raw",
            processed_content="User 1 processed",
        )

        # Create content for user 2
        content_id_2 = self._unique_id("user2_content")
        metadata_2 = ContentMetadata(
            content_id=content_id_2,
            title="User 2 Content",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/user2.pdf",
            language="en",
            duration=None,
            word_count=1000,
            difficulty_level="beginner",
            topics=["test"],
            author="User 2",
            created_at=datetime.now(),
        )

        self.service.save_content(
            user_id=user_2_id,
            metadata=metadata_2,
            raw_content="User 2 raw",
            processed_content="User 2 processed",
        )

        # User 1 should only see their content
        user1_content = self.service.get_user_content(user_id=self.user_id)
        assert all(c.user_id == self.user_id for c in user1_content)
        assert not any(c.content_id == content_id_2 for c in user1_content)

        # User 2 should only see their content
        user2_content = self.service.get_user_content(user_id=user_2_id)
        assert all(c.user_id == user_2_id for c in user2_content)
        assert not any(c.content_id == content_id_1 for c in user2_content)

        # User 1 cannot access user 2's content by ID
        no_access = self.service.get_content_by_id(content_id_2, self.user_id)
        assert no_access is None

        print("✅ Multi-user content isolation test passed")

    def test_delete_content_with_cascade(self):
        """Test deleting content cascades to learning materials"""
        # Create content with materials
        content_id = self._unique_id("delete_test_content")
        metadata = ContentMetadata(
            content_id=content_id,
            title="Content to Delete",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/delete_test.pdf",
            language="en",
            duration=None,
            word_count=1000,
            difficulty_level="beginner",
            topics=["test"],
            author="Test",
            created_at=datetime.now(),
        )

        saved_content = self.service.save_content(
            user_id=self.user_id,
            metadata=metadata,
            raw_content="Raw content",
            processed_content="Processed content",
        )

        # Add learning material
        material = LearningMaterial(
            material_id=self._unique_id("delete_test_material"),
            content_id=saved_content.content_id,
            material_type=LearningMaterialType.SUMMARY,
            title="Summary to Delete",
            content={"summary": "Test summary"},
            difficulty_level="beginner",
            estimated_time=5,
            tags=["test"],
        )

        self.service.save_learning_material(
            user_id=self.user_id,
            content_id=saved_content.content_id,
            material=material,
        )

        # Verify content and material exist
        assert self.service.get_content_by_id(content_id, self.user_id) is not None
        materials_before = self.service.get_learning_materials(content_id, self.user_id)
        assert len(materials_before) == 1

        # Delete content
        deleted = self.service.delete_content(content_id, self.user_id)
        assert deleted is True

        # Verify content and materials are gone
        assert self.service.get_content_by_id(content_id, self.user_id) is None
        materials_after = self.service.get_learning_materials(content_id, self.user_id)
        assert len(materials_after) == 0

        print("✅ Content deletion with cascade test passed")

    def test_content_update(self):
        """Test updating existing content"""
        # Create initial content
        content_id = self._unique_id("update_test")
        metadata = ContentMetadata(
            content_id=content_id,
            title="Original Title",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/update_test.pdf",
            language="en",
            duration=None,
            word_count=1000,
            difficulty_level="beginner",
            topics=["original"],
            author="Original Author",
            created_at=datetime.now(),
        )

        original = self.service.save_content(
            user_id=self.user_id,
            metadata=metadata,
            raw_content="Original raw content",
            processed_content="Original processed content",
        )

        original_id = original.id
        original_created_at = original.created_at

        # Update content (same source_url triggers update)
        updated_metadata = ContentMetadata(
            content_id=content_id,
            title="Updated Title",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/update_test.pdf",  # Same URL
            language="en",
            duration=None,
            word_count=1500,  # Changed
            difficulty_level="intermediate",  # Changed
            topics=["updated"],  # Changed
            author="Updated Author",  # Changed
            created_at=datetime.now(),
        )

        updated = self.service.save_content(
            user_id=self.user_id,
            metadata=updated_metadata,
            raw_content="Updated raw content",
            processed_content="Updated processed content",
        )

        # Verify it's the same record (same ID) but updated
        assert updated.id == original_id
        assert updated.content_id == content_id
        assert updated.title == "Updated Title"
        assert updated.word_count == 1500
        assert updated.difficulty_level == "intermediate"
        assert "updated" in updated.topics
        assert updated.author == "Updated Author"
        assert updated.created_at == original_created_at  # Created time unchanged
        assert updated.updated_at is not None  # Updated time set

        print("✅ Content update test passed")

    def test_content_statistics(self):
        """Test retrieving content statistics"""
        # Create various content
        content_data = [
            ("es", "youtube_video"),
            ("es", "youtube_video"),
            ("fr", "pdf_document"),
            ("de", "pdf_document"),
            ("es", "youtube_video"),
        ]

        for i, (lang, ctype) in enumerate(content_data):
            content_id = self._unique_id(f"stats_test_{i}")
            metadata = ContentMetadata(
                content_id=content_id,
                title=f"Stats Test {i}",
                content_type=ContentType(ctype),
                source_url=f"https://example.com/stats_{i}",
                language=lang,
                duration=10.0 if ctype == "youtube_video" else None,
                word_count=1000,
                difficulty_level="beginner",
                topics=["test"],
                author="Stats Test",
                created_at=datetime.now(),
            )

            saved = self.service.save_content(
                user_id=self.user_id,
                metadata=metadata,
                raw_content=f"Raw {i}",
                processed_content=f"Processed {i}",
            )

            # Add one material per content
            material = LearningMaterial(
                material_id=self._unique_id(f"stats_mat_{i}"),
                content_id=saved.content_id,
                material_type=LearningMaterialType.SUMMARY,
                title=f"Summary {i}",
                content={"summary": f"Summary {i}"},
                difficulty_level="beginner",
                estimated_time=5,
                tags=["test"],
            )
            self.service.save_learning_material(
                user_id=self.user_id,
                content_id=saved.content_id,
                material=material,
            )

        # Get statistics
        stats = self.service.get_content_statistics(self.user_id)

        assert stats["total_content"] >= 5
        assert stats["by_language"]["es"] >= 3
        assert stats["by_language"]["fr"] >= 1
        assert stats["by_language"]["de"] >= 1
        assert stats["by_type"]["youtube_video"] >= 3
        assert stats["by_type"]["pdf_document"] >= 2
        assert stats["total_materials"] >= 5

        print("✅ Content statistics test passed")

    def test_get_learning_materials_by_type(self):
        """Test filtering learning materials by type"""
        # Create content
        content_id = self._unique_id("materials_filter_test")
        metadata = ContentMetadata(
            content_id=content_id,
            title="Materials Filter Test",
            content_type=ContentType.PDF_DOCUMENT,
            source_url="https://example.com/materials_filter.pdf",
            language="en",
            duration=None,
            word_count=1000,
            difficulty_level="beginner",
            topics=["test"],
            author="Test",
            created_at=datetime.now(),
        )

        saved_content = self.service.save_content(
            user_id=self.user_id,
            metadata=metadata,
            raw_content="Raw",
            processed_content="Processed",
        )

        # Create multiple material types
        material_types = [
            LearningMaterialType.SUMMARY,
            LearningMaterialType.FLASHCARDS,
            LearningMaterialType.QUIZ,
            LearningMaterialType.NOTES,
        ]

        for i, mat_type in enumerate(material_types):
            material = LearningMaterial(
                material_id=self._unique_id(f"filter_mat_{i}"),
                content_id=saved_content.content_id,
                material_type=mat_type,
                title=f"{mat_type.value} Material",
                content={"data": f"Material {i}"},
                difficulty_level="beginner",
                estimated_time=5,
                tags=["test"],
            )
            self.service.save_learning_material(
                user_id=self.user_id,
                content_id=saved_content.content_id,
                material=material,
            )

        # Get all materials
        all_materials = self.service.get_learning_materials(content_id, self.user_id)
        assert len(all_materials) == 4

        # Filter by specific type
        summaries = self.service.get_learning_materials(
            content_id, self.user_id, material_type="summary"
        )
        assert len(summaries) == 1
        assert summaries[0].material_type == "summary"

        flashcards = self.service.get_learning_materials(
            content_id, self.user_id, material_type="flashcards"
        )
        assert len(flashcards) == 1
        assert flashcards[0].material_type == "flashcards"

        print("✅ Learning materials filter test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
