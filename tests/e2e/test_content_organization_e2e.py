"""
End-to-End Tests for Content Organization
AI Language Tutor App - Session 129

Tests:
- Collection creation and management
- Tag management and search
- Favorites system
- Study tracking and mastery
- Advanced search with filters
- Multi-user isolation for all features
"""

import uuid
from datetime import datetime

import pytest

from app.database.config import get_primary_db_session
from app.models.database import ProcessedContent
from app.models.simple_user import SimpleUser, UserRole
from app.services.content_collection_service import ContentCollectionService
from app.services.content_persistence_service import ContentPersistenceService
from app.services.content_processor import ContentMetadata, ContentType
from app.services.content_study_tracking_service import ContentStudyTrackingService


class TestContentOrganizationE2E:
    """E2E tests for content organization features"""

    def _unique_id(self, prefix="test"):
        """Generate unique ID for test data"""
        return f"{prefix}_{str(uuid.uuid4())[:8]}"

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.content_service = ContentPersistenceService(self.db)
        self.collection_service = ContentCollectionService(self.db)
        self.study_service = ContentStudyTrackingService(self.db)

        # Create test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = SimpleUser(
            user_id=f"org_test_user_{unique_id}",
            username="Organization Test User",
            email=f"org_test_{unique_id}@example.com",
            password_hash="test_hash",
            role=UserRole.CHILD,
        )
        self.db.add(test_user)
        self.db.commit()
        self.db.refresh(test_user)
        self.user_id = test_user.id

        # Create test content
        self.content_items = []
        for i in range(5):
            metadata = ContentMetadata(
                content_id=self._unique_id(f"content_{i}"),
                title=f"Test Content {i}",
                content_type=ContentType.YOUTUBE_VIDEO,
                source_url=f"https://youtube.com/watch?v=test{i}",
                language="es",
                duration=10.0,
                word_count=1000,
                difficulty_level="beginner" if i < 3 else "intermediate",
                topics=["grammar"] if i < 2 else ["vocabulary"],
                author="Test Author",
                created_at=datetime.now(),
            )

            content = self.content_service.save_content(
                user_id=self.user_id,
                metadata=metadata,
                raw_content=f"Raw content {i}",
                processed_content=f"Processed content {i}",
            )
            self.content_items.append(content)

        yield

        # Cleanup
        self.db.close()

    def test_create_collection_and_manage_content(self):
        """
        Test E2E-1: Create collection, add/remove content, delete collection

        Scenario:
        1. Create collection "Spanish Grammar"
        2. Add 3 content items to collection
        3. Retrieve collection and verify 3 items
        4. Remove 1 item
        5. Retrieve collection and verify 2 items
        6. Delete collection
        7. Verify content items still exist
        """
        # Step 1: Create collection
        collection = self.collection_service.create_collection(
            user_id=self.user_id,
            name="Spanish Grammar",
            description="Collection of grammar resources",
            color="#3B82F6",
            icon="book",
        )

        assert collection is not None
        assert collection.name == "Spanish Grammar"
        assert collection.user_id == self.user_id
        assert collection.color == "#3B82F6"
        assert collection.icon == "book"

        # Step 2: Add 3 content items
        for i in range(3):
            added = self.collection_service.add_content_to_collection(
                collection_id=collection.collection_id,
                content_id=self.content_items[i].content_id,
                user_id=self.user_id,
            )
            assert added is True

        # Step 3: Retrieve collection and verify 3 items
        retrieved = self.collection_service.get_collection(
            collection_id=collection.collection_id,
            user_id=self.user_id,
            include_content=True,
        )

        assert retrieved is not None
        assert len(retrieved.items) == 3

        # Step 4: Remove 1 item
        removed = self.collection_service.remove_content_from_collection(
            collection_id=collection.collection_id,
            content_id=self.content_items[0].content_id,
            user_id=self.user_id,
        )
        assert removed is True

        # Step 5: Verify 2 items remain
        retrieved = self.collection_service.get_collection(
            collection_id=collection.collection_id,
            user_id=self.user_id,
            include_content=True,
        )
        assert len(retrieved.items) == 2

        # Step 6: Delete collection
        deleted = self.collection_service.delete_collection(
            collection_id=collection.collection_id, user_id=self.user_id
        )
        assert deleted is True

        # Step 7: Verify content still exists
        for item in self.content_items[:3]:
            content = self.content_service.get_content_by_id(
                content_id=item.content_id, user_id=self.user_id
            )
            assert content is not None

    def test_tag_content_and_search_by_tags(self):
        """
        Test E2E-2: Tag content and search by tag

        Scenario:
        1. Create 5 content items
        2. Tag items 0-2 with "grammar"
        3. Tag items 1-3 with "vocabulary"
        4. Search by tag "grammar" → expect 3 results
        5. Search by tag "vocabulary" → expect 3 results
        6. Get all user tags → expect {"grammar": 3, "vocabulary": 3}
        7. Remove tag from item 1
        8. Search by tag "grammar" → expect 2 results
        """
        # Step 2: Tag items 0-2 with "grammar"
        for i in range(3):
            added = self.content_service.add_tag(
                content_id=self.content_items[i].content_id,
                user_id=self.user_id,
                tag="grammar",
            )
            assert added is True

        # Step 3: Tag items 1-3 with "vocabulary"
        for i in range(1, 4):
            added = self.content_service.add_tag(
                content_id=self.content_items[i].content_id,
                user_id=self.user_id,
                tag="vocabulary",
            )
            assert added is True

        # Step 4: Search by "grammar"
        grammar_content = self.content_service.search_by_tag(
            user_id=self.user_id, tag="grammar"
        )
        assert len(grammar_content) == 3

        # Step 5: Search by "vocabulary"
        vocab_content = self.content_service.search_by_tag(
            user_id=self.user_id, tag="vocabulary"
        )
        assert len(vocab_content) == 3

        # Step 6: Get all user tags
        all_tags = self.content_service.get_all_user_tags(user_id=self.user_id)
        assert len(all_tags) == 2
        tag_dict = {tag["tag"]: tag["count"] for tag in all_tags}
        assert tag_dict["grammar"] == 3
        assert tag_dict["vocabulary"] == 3

        # Step 7: Remove tag from item 1
        removed = self.content_service.remove_tag(
            content_id=self.content_items[1].content_id,
            user_id=self.user_id,
            tag="grammar",
        )
        assert removed is True

        # Step 8: Search by "grammar" → expect 2 results
        grammar_content = self.content_service.search_by_tag(
            user_id=self.user_id, tag="grammar"
        )
        assert len(grammar_content) == 2

    def test_favorite_content_and_retrieve(self):
        """
        Test E2E-3: Mark content as favorite and retrieve favorites

        Scenario:
        1. Create 5 content items
        2. Mark items 0, 2, 4 as favorites
        3. Retrieve favorites → expect 3 items
        4. Un-favorite item 2
        5. Retrieve favorites → expect 2 items
        6. Verify favorites persist across requests
        """
        # Step 2: Mark items 0, 2, 4 as favorites
        for i in [0, 2, 4]:
            added = self.content_service.add_favorite(
                content_id=self.content_items[i].content_id, user_id=self.user_id
            )
            assert added is True

        # Step 3: Retrieve favorites
        favorites = self.content_service.get_favorites(user_id=self.user_id)
        assert len(favorites) == 3

        # Verify correct items
        fav_ids = {f.content_id for f in favorites}
        assert self.content_items[0].content_id in fav_ids
        assert self.content_items[2].content_id in fav_ids
        assert self.content_items[4].content_id in fav_ids

        # Step 4: Un-favorite item 2
        removed = self.content_service.remove_favorite(
            content_id=self.content_items[2].content_id, user_id=self.user_id
        )
        assert removed is True

        # Step 5: Retrieve favorites → expect 2 items
        favorites = self.content_service.get_favorites(user_id=self.user_id)
        assert len(favorites) == 2

        # Step 6: Verify is_favorite check
        assert (
            self.content_service.is_favorite(
                content_id=self.content_items[0].content_id, user_id=self.user_id
            )
            is True
        )
        assert (
            self.content_service.is_favorite(
                content_id=self.content_items[2].content_id, user_id=self.user_id
            )
            is False
        )

    def test_study_session_and_mastery_tracking(self):
        """
        Test E2E-4: Study content and track mastery progression

        Scenario:
        1. Start study session for content
        2. Update session with 5/10 flashcards correct
        3. Complete session (5 min duration)
        4. Check mastery status → level="learning", 50% mastered
        5. Start 2nd session
        6. Complete with 9/10 correct
        7. Check mastery status → level="reviewing", 90% mastered
        8. Start 3rd, 4th, 5th sessions (all high scores)
        9. Check mastery status → level="mastered"
        """
        content = self.content_items[0]

        # Session 1
        # Step 1: Start study session
        session1_id = self.study_service.start_study_session(
            user_id=self.user_id, content_id=content.content_id
        )
        assert session1_id > 0

        # Step 2: Update session
        updated = self.study_service.update_study_session(
            session_id=session1_id,
            user_id=self.user_id,
            materials_studied={"flashcards": [1, 2, 3, 4, 5]},
            items_correct=5,
            items_total=10,
            completion_percentage=50.0,
        )
        assert updated is True

        # Step 3: Complete session
        mastery1 = self.study_service.complete_study_session(
            session_id=session1_id,
            user_id=self.user_id,
            duration_seconds=300,  # 5 minutes
            final_stats={"items_correct": 5, "items_total": 10},
        )

        # Step 4: Check mastery
        assert mastery1.mastery_level == "learning"
        assert mastery1.total_sessions == 1
        assert mastery1.items_mastered == 5
        assert mastery1.items_total == 10

        # Session 2
        # Step 5: Start 2nd session
        session2_id = self.study_service.start_study_session(
            user_id=self.user_id, content_id=content.content_id
        )

        # Step 6: Complete with high score
        mastery2 = self.study_service.complete_study_session(
            session_id=session2_id,
            user_id=self.user_id,
            duration_seconds=600,
            final_stats={"items_correct": 9, "items_total": 10},
        )

        # Step 7: Check mastery (should still be learning, need 3+ sessions for reviewing)
        assert mastery2.mastery_level == "learning"  # Only 2 sessions
        assert mastery2.total_sessions == 2

        # Sessions 3, 4, 5
        # Step 8: Complete more sessions
        for i in range(3):
            session_id = self.study_service.start_study_session(
                user_id=self.user_id, content_id=content.content_id
            )
            mastery = self.study_service.complete_study_session(
                session_id=session_id,
                user_id=self.user_id,
                duration_seconds=600,
                final_stats={"items_correct": 9, "items_total": 10},
            )

        # Step 9: Check final mastery level
        final_mastery = self.study_service.get_mastery_status(
            content_id=content.content_id, user_id=self.user_id
        )
        assert final_mastery.mastery_level == "mastered"  # 5 sessions, >80% mastered
        assert final_mastery.total_sessions == 5

    def test_multi_user_isolation(self):
        """
        Test E2E-5: Verify multi-user data isolation

        Scenario:
        1. User 1 creates collections, tags, favorites
        2. User 2 creates same
        3. Verify User 1 cannot see User 2's data
        4. Verify User 2 cannot access User 1's collections
        """
        # Create second user
        unique_id = str(uuid.uuid4())[:8]
        user2 = SimpleUser(
            user_id=f"org_test_user2_{unique_id}",
            username="Organization Test User 2",
            email=f"org_test2_{unique_id}@example.com",
            password_hash="test_hash",
            role=UserRole.CHILD,
        )
        self.db.add(user2)
        self.db.commit()
        self.db.refresh(user2)
        user2_id = user2.id

        # Create content for user 2
        metadata2 = ContentMetadata(
            content_id=self._unique_id("user2_content"),
            title="User 2 Content",
            content_type=ContentType.YOUTUBE_VIDEO,
            source_url="https://youtube.com/watch?v=user2",
            language="fr",
            duration=5.0,
            word_count=500,
            difficulty_level="beginner",
            topics=["basics"],
            author="User 2",
            created_at=datetime.now(),
        )

        content2 = self.content_service.save_content(
            user_id=user2_id,
            metadata=metadata2,
            raw_content="User 2 raw",
            processed_content="User 2 processed",
        )

        # User 1: Create collection
        coll1 = self.collection_service.create_collection(
            user_id=self.user_id, name="User 1 Collection"
        )

        # User 2: Create collection
        coll2 = self.collection_service.create_collection(
            user_id=user2_id, name="User 2 Collection"
        )

        # Verify User 1 sees only their collection
        user1_collections = self.collection_service.get_user_collections(
            user_id=self.user_id
        )
        assert len(user1_collections) == 1
        assert user1_collections[0].name == "User 1 Collection"

        # Verify User 2 sees only their collection
        user2_collections = self.collection_service.get_user_collections(
            user_id=user2_id
        )
        assert len(user2_collections) == 1
        assert user2_collections[0].name == "User 2 Collection"

        # Verify User 2 cannot access User 1's collection
        with pytest.raises(PermissionError):
            self.collection_service.get_collection(
                collection_id=coll1.collection_id, user_id=user2_id
            )

        # User 1: Add tag
        self.content_service.add_tag(
            content_id=self.content_items[0].content_id,
            user_id=self.user_id,
            tag="user1tag",
        )

        # User 2: Add tag
        self.content_service.add_tag(
            content_id=content2.content_id, user_id=user2_id, tag="user2tag"
        )

        # Verify tag isolation
        user1_tags = self.content_service.get_all_user_tags(user_id=self.user_id)
        user2_tags = self.content_service.get_all_user_tags(user_id=user2_id)

        user1_tag_names = {tag["tag"] for tag in user1_tags}
        user2_tag_names = {tag["tag"] for tag in user2_tags}

        assert "user1tag" in user1_tag_names
        assert "user2tag" not in user1_tag_names
        assert "user2tag" in user2_tag_names
        assert "user1tag" not in user2_tag_names
