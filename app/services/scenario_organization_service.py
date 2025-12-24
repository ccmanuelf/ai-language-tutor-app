"""
Scenario Organization Service

This service provides comprehensive functionality for organizing, discovering,
and managing scenarios through:
- Collections and learning paths
- Tagging system (user + AI generated)
- Bookmarks and favorites
- Ratings and reviews
- Discovery and search
- Analytics aggregation

Integrates with ScenarioBuilderService and ScenarioManager for unified
scenario management across the platform.
"""

from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.database import (
    Scenario,
    ScenarioAnalytics,
    ScenarioBookmark,
    ScenarioCollection,
    ScenarioCollectionItem,
    ScenarioPhase,
    ScenarioRating,
    ScenarioTag,
)


class ScenarioOrganizationService:
    """
    Service for scenario organization, discovery, and engagement.

    Provides methods for:
    - Collections management (playlists, learning paths)
    - Tagging (user tags, AI tags)
    - Bookmarks (favorites, folders)
    - Ratings and reviews
    - Discovery (search, trending, top-rated)
    - Analytics (aggregation, scoring)
    """

    def __init__(self, db: Session):
        """
        Initialize the scenario organization service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    # ========================================================================
    # COLLECTIONS MANAGEMENT (7 methods)
    # ========================================================================

    async def create_collection(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
        is_learning_path: bool = False,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
    ) -> ScenarioCollection:
        """
        Create a new scenario collection or learning path.

        Args:
            user_id: ID of the user creating the collection
            name: Collection name
            description: Optional description
            is_public: Whether the collection is publicly visible
            is_learning_path: If true, scenarios have ordered progression
            category: Optional category filter
            difficulty_level: Optional difficulty filter

        Returns:
            Created ScenarioCollection instance

        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not name or len(name) < 3:
            raise ValueError("Collection name must be at least 3 characters")
        if len(name) > 255:
            raise ValueError("Collection name must be less than 255 characters")

        # Generate unique collection_id
        collection_id = f"collection_{uuid4().hex[:12]}"

        # Create collection
        collection = ScenarioCollection(
            collection_id=collection_id,
            name=name,
            description=description,
            created_by=user_id,
            is_public=is_public,
            is_learning_path=is_learning_path,
            category=category,
            difficulty_level=difficulty_level,
            item_count=0,
            subscriber_count=0,
        )

        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)

        return collection

    async def add_scenario_to_collection(
        self,
        collection_id: str,
        scenario_id: str,
        user_id: int,
        notes: Optional[str] = None,
    ) -> ScenarioCollectionItem:
        """
        Add a scenario to a collection.

        Args:
            collection_id: Collection identifier (string)
            scenario_id: Scenario identifier (string, e.g., 'restaurant_ordering')
            user_id: User ID (must own the collection)
            notes: Optional notes about why scenario is included

        Returns:
            Created ScenarioCollectionItem

        Raises:
            ValueError: If collection not found or user doesn't own it
            ValueError: If scenario already in collection
        """
        # Get collection
        collection = (
            self.db.query(ScenarioCollection)
            .filter(ScenarioCollection.collection_id == collection_id)
            .first()
        )

        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        if collection.created_by != user_id:
            raise ValueError("You don't own this collection")

        # Check if scenario exists
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Check if already in collection
        existing = (
            self.db.query(ScenarioCollectionItem)
            .filter(
                and_(
                    ScenarioCollectionItem.collection_id == collection.id,
                    ScenarioCollectionItem.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if existing:
            raise ValueError("Scenario already in this collection")

        # Calculate position (append to end)
        max_position = (
            self.db.query(func.max(ScenarioCollectionItem.position))
            .filter(ScenarioCollectionItem.collection_id == collection.id)
            .scalar()
        )
        position = (max_position or 0) + 1

        # Create collection item
        item = ScenarioCollectionItem(
            collection_id=collection.id,
            scenario_id=scenario.id,
            position=position,
            notes=notes,
        )

        self.db.add(item)

        # Update collection metadata
        collection.item_count += 1
        collection.estimated_total_duration = (
            collection.estimated_total_duration or 0
        ) + scenario.estimated_duration

        self.db.commit()
        self.db.refresh(item)

        return item

    async def remove_scenario_from_collection(
        self, collection_id: str, scenario_id: str, user_id: int
    ) -> bool:
        """
        Remove a scenario from a collection.

        Args:
            collection_id: Collection identifier (string)
            scenario_id: Scenario identifier (string)
            user_id: User ID (must own collection)

        Returns:
            True if removed successfully

        Raises:
            ValueError: If collection not found or user doesn't own it
        """
        # Get collection
        collection = (
            self.db.query(ScenarioCollection)
            .filter(ScenarioCollection.collection_id == collection_id)
            .first()
        )

        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        if collection.created_by != user_id:
            raise ValueError("You don't own this collection")

        # Get scenario first to obtain its integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Find and delete item
        item = (
            self.db.query(ScenarioCollectionItem)
            .filter(
                and_(
                    ScenarioCollectionItem.collection_id == collection.id,
                    ScenarioCollectionItem.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if not item:
            raise ValueError("Scenario not in this collection")

        self.db.delete(item)

        # Update collection metadata
        collection.item_count = max(0, collection.item_count - 1)
        if scenario:
            collection.estimated_total_duration = max(
                0,
                (collection.estimated_total_duration or 0)
                - scenario.estimated_duration,
            )

        # Reorder remaining items
        remaining_items = (
            self.db.query(ScenarioCollectionItem)
            .filter(ScenarioCollectionItem.collection_id == collection.id)
            .order_by(ScenarioCollectionItem.position)
            .all()
        )

        for idx, remaining_item in enumerate(remaining_items, start=1):
            remaining_item.position = idx

        self.db.commit()
        return True

    async def reorder_collection(
        self, collection_id: str, scenario_order: List[str], user_id: int
    ) -> bool:
        """
        Reorder scenarios in a collection (for learning paths).

        Args:
            collection_id: Collection identifier
            scenario_order: List of scenario IDs (strings) in desired order
            user_id: User ID (must own collection)

        Returns:
            True if reordered successfully

        Raises:
            ValueError: If validation fails
        """
        # Get collection
        collection = (
            self.db.query(ScenarioCollection)
            .filter(ScenarioCollection.collection_id == collection_id)
            .first()
        )

        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        if collection.created_by != user_id:
            raise ValueError("You don't own this collection")

        # Convert string scenario_ids to integer IDs
        scenario_id_map = {}
        for scenario_id_str in scenario_order:
            scenario = (
                self.db.query(Scenario)
                .filter(Scenario.scenario_id == scenario_id_str)
                .first()
            )
            if scenario:
                scenario_id_map[scenario_id_str] = scenario.id

        # Get all items in collection
        items = (
            self.db.query(ScenarioCollectionItem)
            .filter(ScenarioCollectionItem.collection_id == collection.id)
            .all()
        )

        # Create scenario_id (integer) to item mapping
        item_map = {item.scenario_id: item for item in items}

        # Convert order to integer IDs for validation
        integer_order = [
            scenario_id_map[s] for s in scenario_order if s in scenario_id_map
        ]

        # Validate that all scenario IDs in order exist in collection
        if set(integer_order) != set(item_map.keys()):
            raise ValueError("Scenario order doesn't match collection contents")

        # Update positions
        for position, scenario_id_int in enumerate(integer_order, start=1):
            item_map[scenario_id_int].position = position

        self.db.commit()
        return True

    async def get_collection(
        self, collection_id: str, user_id: Optional[int] = None
    ) -> Optional[ScenarioCollection]:
        """
        Get collection by ID with all items.

        Args:
            collection_id: Collection identifier
            user_id: Optional user ID for ownership check

        Returns:
            ScenarioCollection with items, or None if not found/not accessible
        """
        query = (
            self.db.query(ScenarioCollection)
            .options(joinedload(ScenarioCollection.items))
            .filter(ScenarioCollection.collection_id == collection_id)
        )

        collection = query.first()

        if not collection:
            return None

        # Check access permissions
        if not collection.is_public and user_id != collection.created_by:
            return None

        return collection

    async def get_user_collections(
        self, user_id: int, include_public: bool = False
    ) -> List[ScenarioCollection]:
        """
        Get all collections created by a user.

        Args:
            user_id: User ID
            include_public: If True, also include public collections

        Returns:
            List of ScenarioCollection instances
        """
        query = self.db.query(ScenarioCollection)

        if include_public:
            query = query.filter(
                or_(
                    ScenarioCollection.created_by == user_id,
                    ScenarioCollection.is_public == True,
                )
            )
        else:
            query = query.filter(ScenarioCollection.created_by == user_id)

        collections = query.order_by(desc(ScenarioCollection.created_at)).all()
        return collections

    async def delete_collection(self, collection_id: str, user_id: int) -> bool:
        """
        Delete a collection.

        Args:
            collection_id: Collection identifier
            user_id: User ID (must own collection)

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If collection not found or user doesn't own it
        """
        collection = (
            self.db.query(ScenarioCollection)
            .filter(ScenarioCollection.collection_id == collection_id)
            .first()
        )

        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        if collection.created_by != user_id:
            raise ValueError("You don't own this collection")

        self.db.delete(collection)
        self.db.commit()
        return True

    # ========================================================================
    # TAGGING SYSTEM (4 methods)
    # ========================================================================

    async def add_user_tag(
        self, scenario_id: str, tag: str, user_id: int
    ) -> ScenarioTag:
        """
        Add a user-generated tag to a scenario.

        Args:
            scenario_id: Scenario database ID
            tag: Tag text (will be lowercased)
            user_id: User ID

        Returns:
            Created or existing ScenarioTag

        Raises:
            ValueError: If scenario not found or tag invalid
        """
        # Validate scenario exists
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Validate tag
        tag = tag.strip().lower()
        if not tag or len(tag) < 2:
            raise ValueError("Tag must be at least 2 characters")
        if len(tag) > 50:
            raise ValueError("Tag must be less than 50 characters")

        # Check if tag already exists
        existing = (
            self.db.query(ScenarioTag)
            .filter(
                and_(
                    ScenarioTag.scenario_id == scenario.id,
                    ScenarioTag.tag == tag,
                    ScenarioTag.tag_type == "user",
                )
            )
            .first()
        )

        if existing:
            # Increment usage count
            existing.usage_count += 1
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new tag
        scenario_tag = ScenarioTag(
            scenario_id=scenario.id,
            tag=tag,
            tag_type="user",
            created_by=user_id,
            usage_count=1,
        )

        self.db.add(scenario_tag)
        self.db.commit()
        self.db.refresh(scenario_tag)

        # Update analytics
        await self._update_scenario_tag_count(scenario_id)

        return scenario_tag

    async def add_ai_tags(self, scenario_id: str, tags: List[str]) -> List[ScenarioTag]:
        """
        Add AI-generated tags to a scenario.

        Args:
            scenario_id: Scenario database ID
            tags: List of AI-generated tags

        Returns:
            List of created ScenarioTag instances

        Raises:
            ValueError: If scenario not found
        """
        # Validate scenario exists
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        created_tags = []

        for tag in tags:
            tag = tag.strip().lower()
            if not tag or len(tag) < 2 or len(tag) > 50:
                continue

            # Check if AI tag already exists
            existing = (
                self.db.query(ScenarioTag)
                .filter(
                    and_(
                        ScenarioTag.scenario_id == scenario.id,
                        ScenarioTag.tag == tag,
                        ScenarioTag.tag_type == "ai",
                    )
                )
                .first()
            )

            if not existing:
                scenario_tag = ScenarioTag(
                    scenario_id=scenario.id,
                    tag=tag,
                    tag_type="ai",
                    created_by=None,  # NULL for AI tags
                    usage_count=1,
                )
                self.db.add(scenario_tag)
                created_tags.append(scenario_tag)

        if created_tags:
            self.db.commit()
            for tag in created_tags:
                self.db.refresh(tag)

            # Update analytics
            await self._update_scenario_tag_count(scenario_id)

        return created_tags

    async def get_scenario_tags(
        self, scenario_id: str, tag_type: Optional[str] = None
    ) -> List[ScenarioTag]:
        """
        Get all tags for a scenario.

        Args:
            scenario_id: Scenario database ID (string)
            tag_type: Optional filter for 'user' or 'ai' tags

        Returns:
            List of ScenarioTag instances
        """
        # Get scenario to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            return []

        query = self.db.query(ScenarioTag).filter(
            ScenarioTag.scenario_id == scenario.id
        )

        if tag_type:
            query = query.filter(ScenarioTag.tag_type == tag_type)

        tags = query.order_by(desc(ScenarioTag.usage_count)).all()
        return tags

    async def search_by_tag(self, tag: str, limit: int = 20) -> List[Scenario]:
        """
        Find scenarios by tag.

        Args:
            tag: Tag to search for
            limit: Maximum number of results

        Returns:
            List of Scenario instances
        """
        tag = tag.strip().lower()

        # Find all scenario IDs with this tag
        scenario_ids = (
            self.db.query(ScenarioTag.scenario_id)
            .filter(ScenarioTag.tag == tag)
            .distinct()
            .limit(limit)
            .all()
        )

        scenario_ids = [sid[0] for sid in scenario_ids]

        if not scenario_ids:
            return []

        # Get scenarios
        scenarios = self.db.query(Scenario).filter(Scenario.id.in_(scenario_ids)).all()

        return scenarios

    # ========================================================================
    # BOOKMARKS & FAVORITES (5 methods)
    # ========================================================================

    async def add_bookmark(
        self,
        user_id: int,
        scenario_id: str,
        folder: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> ScenarioBookmark:
        """
        Bookmark a scenario.

        Args:
            user_id: User ID
            scenario_id: Scenario database ID
            folder: Optional folder name for organization
            notes: Optional personal notes

        Returns:
            Created or updated ScenarioBookmark

        Raises:
            ValueError: If scenario not found
        """
        # Validate scenario exists
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Check if bookmark already exists
        existing = (
            self.db.query(ScenarioBookmark)
            .filter(
                and_(
                    ScenarioBookmark.user_id == user_id,
                    ScenarioBookmark.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if existing:
            # Update existing bookmark
            if folder is not None:
                existing.folder = folder
            if notes is not None:
                existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new bookmark
        bookmark = ScenarioBookmark(
            user_id=user_id,
            scenario_id=scenario.id,
            folder=folder,
            notes=notes,
            is_favorite=True,
        )

        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)

        # Update analytics
        await self._update_scenario_bookmark_count(scenario_id)

        return bookmark

    async def remove_bookmark(self, user_id: int, scenario_id: str) -> bool:
        """
        Remove a bookmark.

        Args:
            user_id: User ID
            scenario_id: Scenario identifier (string)

        Returns:
            True if removed successfully
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        bookmark = (
            self.db.query(ScenarioBookmark)
            .filter(
                and_(
                    ScenarioBookmark.user_id == user_id,
                    ScenarioBookmark.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if bookmark:
            self.db.delete(bookmark)
            self.db.commit()

            # Update analytics
            await self._update_scenario_bookmark_count(scenario_id)
            return True

        return False

    async def get_user_bookmarks(
        self, user_id: int, folder: Optional[str] = None
    ) -> List[ScenarioBookmark]:
        """
        Get all bookmarks for a user.

        Args:
            user_id: User ID
            folder: Optional folder filter

        Returns:
            List of ScenarioBookmark instances with scenarios loaded
        """
        query = (
            self.db.query(ScenarioBookmark)
            .options(joinedload(ScenarioBookmark.scenario))
            .filter(ScenarioBookmark.user_id == user_id)
        )

        if folder is not None:
            query = query.filter(ScenarioBookmark.folder == folder)

        bookmarks = query.order_by(desc(ScenarioBookmark.created_at)).all()
        return bookmarks

    async def get_user_folders(self, user_id: int) -> List[str]:
        """
        Get all unique folder names for a user's bookmarks.

        Args:
            user_id: User ID

        Returns:
            List of folder names (excluding None)
        """
        folders = (
            self.db.query(ScenarioBookmark.folder)
            .filter(
                and_(
                    ScenarioBookmark.user_id == user_id,
                    ScenarioBookmark.folder.isnot(None),
                )
            )
            .distinct()
            .all()
        )

        return [folder[0] for folder in folders if folder[0]]

    async def is_bookmarked(self, user_id: int, scenario_id: str) -> bool:
        """
        Check if a scenario is bookmarked by a user.

        Args:
            user_id: User ID
            scenario_id: Scenario database ID (string)

        Returns:
            True if bookmarked
        """
        # Get scenario to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            return False

        bookmark = (
            self.db.query(ScenarioBookmark)
            .filter(
                and_(
                    ScenarioBookmark.user_id == user_id,
                    ScenarioBookmark.scenario_id == scenario.id,
                )
            )
            .first()
        )

        return bookmark is not None

    # ========================================================================
    # RATINGS & REVIEWS (7 methods)
    # ========================================================================

    async def add_rating(
        self,
        user_id: int,
        scenario_id: str,
        rating: int,
        review: Optional[str] = None,
        difficulty_rating: Optional[int] = None,
        usefulness_rating: Optional[int] = None,
        cultural_accuracy_rating: Optional[int] = None,
        is_public: bool = True,
    ) -> ScenarioRating:
        """
        Add or update a rating/review for a scenario.

        Args:
            user_id: User ID
            scenario_id: Scenario database ID
            rating: Overall rating (1-5)
            review: Optional text review
            difficulty_rating: Optional difficulty rating (1-5)
            usefulness_rating: Optional usefulness rating (1-5)
            cultural_accuracy_rating: Optional cultural accuracy rating (1-5)
            is_public: Whether review is publicly visible

        Returns:
            Created or updated ScenarioRating

        Raises:
            ValueError: If validation fails
        """
        # Validate scenario exists
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Validate rating
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # Validate optional ratings
        for optional_rating in [
            difficulty_rating,
            usefulness_rating,
            cultural_accuracy_rating,
        ]:
            if optional_rating is not None and (
                optional_rating < 1 or optional_rating > 5
            ):
                raise ValueError("All ratings must be between 1 and 5")

        # Check if rating already exists
        existing = (
            self.db.query(ScenarioRating)
            .filter(
                and_(
                    ScenarioRating.user_id == user_id,
                    ScenarioRating.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if existing:
            # Update existing rating
            existing.rating = rating
            if review is not None:
                existing.review = review
            if difficulty_rating is not None:
                existing.difficulty_rating = difficulty_rating
            if usefulness_rating is not None:
                existing.usefulness_rating = usefulness_rating
            if cultural_accuracy_rating is not None:
                existing.cultural_accuracy_rating = cultural_accuracy_rating
            existing.is_public = is_public
            existing.updated_at = datetime.now(UTC)

            self.db.commit()
            self.db.refresh(existing)

            # Update analytics
            await self._update_scenario_rating_stats(scenario_id)

            return existing

        # Create new rating
        scenario_rating = ScenarioRating(
            user_id=user_id,
            scenario_id=scenario.id,
            rating=rating,
            review=review,
            difficulty_rating=difficulty_rating,
            usefulness_rating=usefulness_rating,
            cultural_accuracy_rating=cultural_accuracy_rating,
            is_public=is_public,
            helpful_count=0,
        )

        self.db.add(scenario_rating)
        self.db.commit()
        self.db.refresh(scenario_rating)

        # Update analytics
        await self._update_scenario_rating_stats(scenario_id)

        return scenario_rating

    async def get_scenario_ratings(
        self, scenario_id: str, public_only: bool = True, limit: int = 50
    ) -> List[ScenarioRating]:
        """
        Get all ratings/reviews for a scenario.

        Args:
            scenario_id: Scenario database ID (string)
            public_only: If True, only return public reviews
            limit: Maximum number of reviews

        Returns:
            List of ScenarioRating instances
        """
        # Get scenario to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            return []

        query = self.db.query(ScenarioRating).filter(
            ScenarioRating.scenario_id == scenario.id
        )

        if public_only:
            query = query.filter(ScenarioRating.is_public == True)

        ratings = (
            query.order_by(desc(ScenarioRating.helpful_count))
            .order_by(desc(ScenarioRating.created_at))
            .limit(limit)
            .all()
        )

        return ratings

    async def get_user_rating(
        self, user_id: int, scenario_id: str
    ) -> Optional[ScenarioRating]:
        """
        Get a user's rating for a specific scenario.

        Args:
            user_id: User ID
            scenario_id: Scenario database ID (string)

        Returns:
            ScenarioRating or None if not found
        """
        # Get scenario to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            return None

        rating = (
            self.db.query(ScenarioRating)
            .filter(
                and_(
                    ScenarioRating.user_id == user_id,
                    ScenarioRating.scenario_id == scenario.id,
                )
            )
            .first()
        )

        return rating

    async def delete_rating(self, user_id: int, scenario_id: str) -> bool:
        """
        Delete a user's rating.

        Args:
            user_id: User ID
            scenario_id: Scenario identifier (string)

        Returns:
            True if deleted successfully
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        rating = (
            self.db.query(ScenarioRating)
            .filter(
                and_(
                    ScenarioRating.user_id == user_id,
                    ScenarioRating.scenario_id == scenario.id,
                )
            )
            .first()
        )

        if rating:
            self.db.delete(rating)
            self.db.commit()

            # Update analytics
            await self._update_scenario_rating_stats(scenario_id)
            return True

        return False

    async def mark_review_helpful(self, rating_id: int, user_id: int) -> bool:
        """
        Mark a review as helpful.

        Args:
            rating_id: ScenarioRating ID
            user_id: User ID marking it helpful

        Returns:
            True if marked successfully

        Note: This is a simplified version. In production, you'd want a
        separate table to track which users found which reviews helpful.
        """
        rating = (
            self.db.query(ScenarioRating).filter(ScenarioRating.id == rating_id).first()
        )

        if rating:
            rating.helpful_count += 1
            self.db.commit()
            return True

        return False

    async def get_scenario_rating_summary(self, scenario_id: str) -> Dict:
        """
        Get rating summary statistics for a scenario.

        Args:
            scenario_id: Scenario identifier (string)

        Returns:
            Dictionary with rating statistics:
            - average_rating: Average overall rating
            - rating_count: Total number of ratings
            - rating_distribution: Count of each star rating (1-5)
            - average_difficulty: Average difficulty rating
            - average_usefulness: Average usefulness rating
            - average_cultural_accuracy: Average cultural accuracy rating
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            return {
                "average_rating": 0.0,
                "rating_count": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "average_difficulty": 0.0,
                "average_usefulness": 0.0,
                "average_cultural_accuracy": 0.0,
                "total_ratings": 0,
            }

        ratings = (
            self.db.query(ScenarioRating)
            .filter(ScenarioRating.scenario_id == scenario.id)
            .all()
        )

        if not ratings:
            return {
                "average_rating": 0.0,
                "rating_count": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "average_difficulty": 0.0,
                "average_usefulness": 0.0,
                "average_cultural_accuracy": 0.0,
            }

        # Calculate statistics
        rating_values = [r.rating for r in ratings]
        difficulty_values = [
            r.difficulty_rating for r in ratings if r.difficulty_rating is not None
        ]
        usefulness_values = [
            r.usefulness_rating for r in ratings if r.usefulness_rating is not None
        ]
        cultural_values = [
            r.cultural_accuracy_rating
            for r in ratings
            if r.cultural_accuracy_rating is not None
        ]

        # Rating distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating_val in rating_values:
            distribution[rating_val] += 1

        return {
            "average_rating": sum(rating_values) / len(rating_values),
            "rating_count": len(ratings),
            "rating_distribution": distribution,
            "average_difficulty": (
                sum(difficulty_values) / len(difficulty_values)
                if difficulty_values
                else 0.0
            ),
            "average_usefulness": (
                sum(usefulness_values) / len(usefulness_values)
                if usefulness_values
                else 0.0
            ),
            "average_cultural_accuracy": (
                sum(cultural_values) / len(cultural_values) if cultural_values else 0.0
            ),
        }

    async def get_top_rated_scenarios(
        self, category: Optional[str] = None, limit: int = 20, min_ratings: int = 5
    ) -> List[Tuple[Scenario, float]]:
        """
        Get top-rated scenarios.

        Args:
            category: Optional category filter
            limit: Maximum number of results
            min_ratings: Minimum number of ratings required

        Returns:
            List of (Scenario, average_rating) tuples
        """
        # Get analytics with minimum rating count
        query = (
            self.db.query(ScenarioAnalytics, Scenario)
            .join(Scenario, ScenarioAnalytics.scenario_id == Scenario.id)
            .filter(ScenarioAnalytics.rating_count >= min_ratings)
        )

        if category:
            query = query.filter(Scenario.category == category)

        results = (
            query.order_by(desc(ScenarioAnalytics.average_rating)).limit(limit).all()
        )

        return [(scenario, analytics.average_rating) for analytics, scenario in results]

    # ========================================================================
    # DISCOVERY & SEARCH (5 methods)
    # ========================================================================

    async def search_scenarios(
        self,
        query: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 20,
    ) -> List[Scenario]:
        """
        Search scenarios by text query and filters.

        Args:
            query: Search text (searches title, description, tags)
            category: Optional category filter
            difficulty: Optional difficulty filter
            min_rating: Optional minimum rating filter
            limit: Maximum number of results

        Returns:
            List of Scenario instances
        """
        search_query = self.db.query(Scenario).filter(
            or_(
                Scenario.is_system_scenario == True,
                Scenario.is_public == True,
            )
        )

        # Text search
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    Scenario.title.like(search_pattern),
                    Scenario.description.like(search_pattern),
                )
            )

        # Category filter
        if category:
            search_query = search_query.filter(Scenario.category == category)

        # Difficulty filter
        if difficulty:
            search_query = search_query.filter(Scenario.difficulty == difficulty)

        # Rating filter
        if min_rating is not None:
            search_query = search_query.join(
                ScenarioAnalytics,
                Scenario.id == ScenarioAnalytics.scenario_id,
                isouter=True,
            ).filter(
                or_(
                    ScenarioAnalytics.average_rating >= min_rating,
                    ScenarioAnalytics.average_rating.is_(None),
                )
            )

        scenarios = search_query.limit(limit).all()
        return scenarios

    async def get_trending_scenarios(
        self, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[Scenario, float]]:
        """
        Get trending scenarios based on recent activity.

        Args:
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of (Scenario, trending_score) tuples
        """
        query = (
            self.db.query(ScenarioAnalytics, Scenario)
            .join(Scenario, ScenarioAnalytics.scenario_id == Scenario.id)
            .filter(ScenarioAnalytics.trending_score.isnot(None))
        )

        if category:
            query = query.filter(Scenario.category == category)

        results = (
            query.order_by(desc(ScenarioAnalytics.trending_score)).limit(limit).all()
        )

        return [(scenario, analytics.trending_score) for analytics, scenario in results]

    async def get_popular_scenarios(
        self, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[Scenario, int]]:
        """
        Get most popular scenarios by completion count.

        Args:
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of (Scenario, completion_count) tuples
        """
        query = self.db.query(ScenarioAnalytics, Scenario).join(
            Scenario, ScenarioAnalytics.scenario_id == Scenario.id
        )

        if category:
            query = query.filter(Scenario.category == category)

        results = (
            query.order_by(desc(ScenarioAnalytics.total_completions)).limit(limit).all()
        )

        return [
            (scenario, analytics.total_completions) for analytics, scenario in results
        ]

    async def get_recommended_scenarios(
        self, user_id: int, limit: int = 10
    ) -> List[Scenario]:
        """
        Get personalized scenario recommendations for a user.

        Simple recommendation algorithm based on:
        - User's completed scenarios (categories, difficulty)
        - Popular scenarios in those categories
        - Scenarios the user hasn't completed yet

        Args:
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of Scenario instances

        Note: This is a basic implementation. In production, you'd want
        a more sophisticated recommendation engine.
        """
        # For now, return popular scenarios the user hasn't bookmarked
        bookmarked_ids = (
            self.db.query(ScenarioBookmark.scenario_id)
            .filter(ScenarioBookmark.user_id == user_id)
            .all()
        )
        bookmarked_ids = [bid[0] for bid in bookmarked_ids]

        query = (
            self.db.query(Scenario)
            .join(ScenarioAnalytics, Scenario.id == ScenarioAnalytics.scenario_id)
            .filter(
                or_(
                    Scenario.is_system_scenario == True,
                    Scenario.is_public == True,
                )
            )
        )

        if bookmarked_ids:
            query = query.filter(~Scenario.id.in_(bookmarked_ids))

        scenarios = (
            query.order_by(desc(ScenarioAnalytics.popularity_score)).limit(limit).all()
        )

        return scenarios

    async def get_discovery_hub(
        self, user_id: Optional[int] = None, category: Optional[str] = None
    ) -> Dict:
        """
        Get complete discovery hub data with multiple sections.

        Args:
            user_id: Optional user ID for personalization
            category: Optional category filter

        Returns:
            Dictionary with discovery sections:
            - trending: Trending scenarios
            - top_rated: Top-rated scenarios
            - popular: Most completed scenarios
            - recommended: Personalized recommendations (if user_id provided)
            - recent_collections: Recent public collections
        """
        hub_data = {
            "trending": await self.get_trending_scenarios(category=category, limit=10),
            "top_rated": await self.get_top_rated_scenarios(
                category=category, limit=10
            ),
            "popular": await self.get_popular_scenarios(category=category, limit=10),
        }

        if user_id:
            hub_data["recommended"] = await self.get_recommended_scenarios(
                user_id=user_id, limit=10
            )

        # Get recent public collections
        recent_collections = (
            self.db.query(ScenarioCollection)
            .filter(ScenarioCollection.is_public == True)
            .order_by(desc(ScenarioCollection.created_at))
            .limit(5)
            .all()
        )
        hub_data["recent_collections"] = recent_collections

        return hub_data

    # ========================================================================
    # ANALYTICS (3 methods)
    # ========================================================================

    async def update_analytics(self, scenario_id: str) -> ScenarioAnalytics:
        """
        Update all analytics for a scenario.

        This is the main analytics update method that recalculates:
        - Usage metrics (completions, starts, unique users)
        - Rating metrics (average, distribution)
        - Engagement metrics (bookmarks, collections, tags)
        - Trending and popularity scores

        Args:
            scenario_id: Scenario identifier (string)

        Returns:
            Updated ScenarioAnalytics instance
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Get or create analytics record
        analytics = (
            self.db.query(ScenarioAnalytics)
            .filter(ScenarioAnalytics.scenario_id == scenario.id)
            .first()
        )

        if not analytics:
            analytics = ScenarioAnalytics(scenario_id=scenario.id)
            self.db.add(analytics)

        # Update rating metrics
        rating_summary = await self.get_scenario_rating_summary(scenario_id)
        analytics.average_rating = rating_summary["average_rating"]
        analytics.rating_count = rating_summary["rating_count"]
        analytics.rating_distribution = rating_summary["rating_distribution"]

        # Update engagement metrics
        analytics.bookmark_count = (
            self.db.query(func.count(ScenarioBookmark.id))
            .filter(ScenarioBookmark.scenario_id == scenario.id)
            .scalar()
        )

        analytics.collection_count = (
            self.db.query(func.count(ScenarioCollectionItem.id))
            .filter(ScenarioCollectionItem.scenario_id == scenario.id)
            .scalar()
        )

        analytics.tag_count = (
            self.db.query(func.count(ScenarioTag.id))
            .filter(ScenarioTag.scenario_id == scenario.id)
            .scalar()
        )

        # Calculate trending score (weighted recent activity)
        # Formula: (7_day_completions * 3) + (30_day_completions * 1) + (rating * 10)
        trending_score = (
            ((analytics.last_7_days_completions or 0) * 3)
            + ((analytics.last_30_days_completions or 0) * 1)
            + ((analytics.average_rating or 0) * 10)
        )
        analytics.trending_score = trending_score

        # Calculate popularity score
        # Formula: completions + (bookmarks * 2) + (rating_count * 1.5) + (collections * 3)
        popularity_score = (
            (analytics.total_completions or 0)
            + ((analytics.bookmark_count or 0) * 2)
            + ((analytics.rating_count or 0) * 1.5)
            + ((analytics.collection_count or 0) * 3)
        )
        analytics.popularity_score = popularity_score

        analytics.last_updated = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(analytics)

        return analytics

    async def record_scenario_start(self, scenario_id: str, user_id: int) -> None:
        """
        Record that a user started a scenario.

        Args:
            scenario_id: Scenario identifier (string)
            user_id: User ID
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        analytics = (
            self.db.query(ScenarioAnalytics)
            .filter(ScenarioAnalytics.scenario_id == scenario.id)
            .first()
        )

        if not analytics:
            analytics = ScenarioAnalytics(scenario_id=scenario.id)
            self.db.add(analytics)

        analytics.total_starts = (analytics.total_starts or 0) + 1
        self.db.commit()

        # Update completion rate
        if (analytics.total_starts or 0) > 0:
            analytics.completion_rate = (
                (analytics.total_completions or 0) / (analytics.total_starts or 0)
            ) * 100
            self.db.commit()

    async def record_scenario_completion(self, scenario_id: str, user_id: int) -> None:
        """
        Record that a user completed a scenario.

        Args:
            scenario_id: Scenario identifier (string)
            user_id: User ID
        """
        # Get scenario first to obtain integer ID
        scenario = (
            self.db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
        )
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        analytics = (
            self.db.query(ScenarioAnalytics)
            .filter(ScenarioAnalytics.scenario_id == scenario.id)
            .first()
        )

        if not analytics:
            analytics = ScenarioAnalytics(scenario_id=scenario.id)
            self.db.add(analytics)

        analytics.total_completions = (analytics.total_completions or 0) + 1
        analytics.last_7_days_completions = (analytics.last_7_days_completions or 0) + 1
        analytics.last_30_days_completions = (
            analytics.last_30_days_completions or 0
        ) + 1

        # Update completion rate
        if (analytics.total_starts or 0) > 0:
            analytics.completion_rate = (
                (analytics.total_completions or 0) / (analytics.total_starts or 0)
            ) * 100

        self.db.commit()

        # Trigger full analytics update
        await self.update_analytics(scenario_id)

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _update_scenario_rating_stats(self, scenario_id: str) -> None:
        """Update rating statistics in analytics table."""
        await self.update_analytics(scenario_id)

    async def _update_scenario_bookmark_count(self, scenario_id: str) -> None:
        """Update bookmark count in analytics table."""
        await self.update_analytics(scenario_id)

    async def _update_scenario_tag_count(self, scenario_id: str) -> None:
        """Update tag count in analytics table."""
        await self.update_analytics(scenario_id)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_scenario_org_service: Optional[ScenarioOrganizationService] = None


def get_scenario_organization_service(
    db: Optional[Session] = None,
) -> ScenarioOrganizationService:
    """
    Get or create the singleton ScenarioOrganizationService instance.

    Args:
        db: Optional database session. If not provided, uses primary session.

    Returns:
        ScenarioOrganizationService instance
    """
    global _scenario_org_service

    if db is not None:
        return ScenarioOrganizationService(db)

    if _scenario_org_service is None:
        from app.models.database import get_db_session

        db_session = next(get_db_session())
        _scenario_org_service = ScenarioOrganizationService(db_session)

    return _scenario_org_service
