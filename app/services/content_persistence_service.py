"""
Content Persistence Service
AI Language Tutor App - Session 128

Provides:
- Save processed content to database (YouTube, documents, etc.)
- Retrieve content by ID, user, type, language
- Search and filter content
- Manage learning materials
- Content organization (tags, categories)

This service bridges the in-memory ContentProcessor with the database,
ensuring all content persists across restarts.
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.models.database import (
    ContentFavorite,
    ContentTag,
    LearningMaterialDB,
    ProcessedContent,
)
from app.services.content_processor import (
    ContentMetadata,
    LearningMaterial,
    LearningMaterialType,
)
from app.services.content_processor import (
    ProcessedContent as ProcessedContentDataclass,
)

logger = logging.getLogger(__name__)


class ContentPersistenceService:
    """Service for persisting and retrieving content from the database"""

    def __init__(self, db: Session):
        """
        Initialize the service with a database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def _generate_content_id(self, source: str, user_id: int) -> str:
        """Generate unique content ID from source and user"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{source}_{user_id}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def _generate_material_id(self, content_id: str, material_type: str) -> str:
        """Generate unique material ID"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{content_id}_{material_type}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def save_content(
        self,
        user_id: int,
        metadata: ContentMetadata,
        raw_content: str,
        processed_content: str,
        processing_stats: Optional[Dict] = None,
    ) -> ProcessedContent:
        """
        Save processed content to database

        Args:
            user_id: User ID who owns this content
            metadata: Content metadata (title, type, source, etc.)
            raw_content: Original extracted content
            processed_content: Cleaned/processed content
            processing_stats: Processing statistics and metadata

        Returns:
            Created ProcessedContent database object
        """
        try:
            # Check if content already exists
            existing = (
                self.db.query(ProcessedContent)
                .filter(
                    and_(
                        ProcessedContent.user_id == user_id,
                        ProcessedContent.source_url == metadata.source_url,
                    )
                )
                .first()
            )

            if existing:
                logger.info(
                    f"Content already exists for URL: {metadata.source_url}, updating..."
                )
                # Update existing content
                existing.title = metadata.title
                existing.raw_content = raw_content
                existing.processed_content = processed_content
                existing.duration = metadata.duration
                existing.word_count = metadata.word_count
                existing.difficulty_level = metadata.difficulty_level
                existing.topics = metadata.topics
                existing.author = metadata.author
                existing.file_size = metadata.file_size
                existing.processing_stats = processing_stats or {}
                existing.updated_at = datetime.now()

                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated content: {existing.content_id}")
                return existing

            # Create new content
            content_id = metadata.content_id
            if not content_id:
                content_id = self._generate_content_id(
                    metadata.source_url or metadata.title, user_id
                )

            db_content = ProcessedContent(
                content_id=content_id,
                user_id=user_id,
                title=metadata.title,
                content_type=metadata.content_type.value
                if hasattr(metadata.content_type, "value")
                else str(metadata.content_type),
                source_url=metadata.source_url,
                language=metadata.language,
                raw_content=raw_content,
                processed_content=processed_content,
                duration=metadata.duration,
                word_count=metadata.word_count,
                difficulty_level=metadata.difficulty_level,
                topics=metadata.topics,
                author=metadata.author,
                file_size=metadata.file_size,
                processing_stats=processing_stats or {},
            )

            self.db.add(db_content)
            self.db.commit()
            self.db.refresh(db_content)

            logger.info(f"Saved content: {db_content.content_id} for user {user_id}")
            return db_content

        except Exception as e:
            logger.error(f"Error saving content: {e}")
            self.db.rollback()
            raise

    def save_learning_material(
        self,
        user_id: int,
        content_id: str,
        material: LearningMaterial,
    ) -> LearningMaterialDB:
        """
        Save learning material to database

        Args:
            user_id: User ID who owns this material
            content_id: Content ID this material belongs to
            material: Learning material data

        Returns:
            Created LearningMaterialDB database object
        """
        try:
            material_id = material.material_id
            if not material_id:
                material_id = self._generate_material_id(
                    content_id,
                    material.material_type.value
                    if hasattr(material.material_type, "value")
                    else str(material.material_type),
                )

            db_material = LearningMaterialDB(
                material_id=material_id,
                content_id=content_id,
                user_id=user_id,
                material_type=material.material_type.value
                if hasattr(material.material_type, "value")
                else str(material.material_type),
                title=material.title,
                difficulty_level=material.difficulty_level,
                estimated_time=material.estimated_time,
                tags=material.tags,
                content=material.content,
            )

            self.db.add(db_material)
            self.db.commit()
            self.db.refresh(db_material)

            logger.info(f"Saved learning material: {db_material.material_id}")
            return db_material

        except Exception as e:
            logger.error(f"Error saving learning material: {e}")
            self.db.rollback()
            raise

    def save_processed_content_with_materials(
        self,
        user_id: int,
        processed_content_dataclass: ProcessedContentDataclass,
    ) -> ProcessedContent:
        """
        Save complete processed content with all learning materials

        Args:
            user_id: User ID who owns this content
            processed_content_dataclass: Complete ProcessedContent dataclass from ContentProcessor

        Returns:
            Created ProcessedContent database object with materials
        """
        try:
            # Save main content
            db_content = self.save_content(
                user_id=user_id,
                metadata=processed_content_dataclass.metadata,
                raw_content=processed_content_dataclass.raw_content,
                processed_content=processed_content_dataclass.processed_content,
                processing_stats=processed_content_dataclass.processing_stats,
            )

            # Save all learning materials
            for material in processed_content_dataclass.learning_materials:
                self.save_learning_material(
                    user_id=user_id,
                    content_id=db_content.content_id,
                    material=material,
                )

            logger.info(
                f"Saved content {db_content.content_id} with {len(processed_content_dataclass.learning_materials)} materials"
            )
            return db_content

        except Exception as e:
            logger.error(f"Error saving complete content: {e}")
            self.db.rollback()
            raise

    def get_content_by_id(
        self, content_id: str, user_id: Optional[int] = None
    ) -> Optional[ProcessedContent]:
        """
        Get content by ID

        Args:
            content_id: Content ID to retrieve
            user_id: Optional user ID for access control

        Returns:
            ProcessedContent or None if not found
        """
        query = self.db.query(ProcessedContent).filter(
            ProcessedContent.content_id == content_id
        )

        if user_id is not None:
            query = query.filter(ProcessedContent.user_id == user_id)

        return query.first()

    def get_user_content(
        self,
        user_id: int,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ProcessedContent]:
        """
        Get all content for a user with optional filters

        Args:
            user_id: User ID
            content_type: Optional content type filter
            language: Optional language filter
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of ProcessedContent objects
        """
        query = self.db.query(ProcessedContent).filter(
            ProcessedContent.user_id == user_id
        )

        if content_type:
            query = query.filter(ProcessedContent.content_type == content_type)

        if language:
            query = query.filter(ProcessedContent.language == language)

        return (
            query.order_by(desc(ProcessedContent.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def search_content(
        self,
        user_id: int,
        search_query: Optional[str] = None,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        topics: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        limit: int = 50,
    ) -> List[ProcessedContent]:
        """
        Search content with multiple filters

        Args:
            user_id: User ID
            search_query: Text search in title/content
            content_type: Filter by content type
            language: Filter by language
            topics: Filter by topics (any match)
            difficulty: Filter by difficulty level
            limit: Maximum number of results

        Returns:
            List of matching ProcessedContent objects
        """
        query = self.db.query(ProcessedContent).filter(
            ProcessedContent.user_id == user_id
        )

        # Text search in title
        if search_query:
            query = query.filter(ProcessedContent.title.ilike(f"%{search_query}%"))

        # Filter by content type
        if content_type:
            query = query.filter(ProcessedContent.content_type == content_type)

        # Filter by language
        if language:
            query = query.filter(ProcessedContent.language == language)

        # Filter by difficulty
        if difficulty:
            query = query.filter(ProcessedContent.difficulty_level == difficulty)

        # Filter by topics (any topic matches)
        if topics:
            # SQLite JSON search - check if any topic is in the topics JSON array
            topic_filters = [
                ProcessedContent.topics.contains(topic) for topic in topics
            ]
            query = query.filter(or_(*topic_filters))

        return query.order_by(desc(ProcessedContent.created_at)).limit(limit).all()

    def get_learning_materials(
        self,
        content_id: str,
        user_id: Optional[int] = None,
        material_type: Optional[str] = None,
    ) -> List[LearningMaterialDB]:
        """
        Get learning materials for content

        Args:
            content_id: Content ID
            user_id: Optional user ID for access control
            material_type: Optional material type filter

        Returns:
            List of LearningMaterialDB objects
        """
        query = self.db.query(LearningMaterialDB).filter(
            LearningMaterialDB.content_id == content_id
        )

        if user_id is not None:
            query = query.filter(LearningMaterialDB.user_id == user_id)

        if material_type:
            query = query.filter(LearningMaterialDB.material_type == material_type)

        return query.all()

    def delete_content(self, content_id: str, user_id: int) -> bool:
        """
        Delete content and all associated learning materials

        Args:
            content_id: Content ID to delete
            user_id: User ID for access control

        Returns:
            True if deleted, False if not found
        """
        try:
            content = (
                self.db.query(ProcessedContent)
                .filter(
                    and_(
                        ProcessedContent.content_id == content_id,
                        ProcessedContent.user_id == user_id,
                    )
                )
                .first()
            )

            if not content:
                return False

            # Delete associated learning materials (cascade should handle this)
            self.db.query(LearningMaterialDB).filter(
                LearningMaterialDB.content_id == content_id
            ).delete()

            # Delete content
            self.db.delete(content)
            self.db.commit()

            logger.info(f"Deleted content: {content_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting content: {e}")
            self.db.rollback()
            raise

    def get_content_statistics(self, user_id: int) -> Dict:
        """
        Get content statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        total_content = (
            self.db.query(func.count(ProcessedContent.id))
            .filter(ProcessedContent.user_id == user_id)
            .scalar()
        )

        by_type = (
            self.db.query(
                ProcessedContent.content_type, func.count(ProcessedContent.id)
            )
            .filter(ProcessedContent.user_id == user_id)
            .group_by(ProcessedContent.content_type)
            .all()
        )

        by_language = (
            self.db.query(ProcessedContent.language, func.count(ProcessedContent.id))
            .filter(ProcessedContent.user_id == user_id)
            .group_by(ProcessedContent.language)
            .all()
        )

        total_materials = (
            self.db.query(func.count(LearningMaterialDB.id))
            .filter(LearningMaterialDB.user_id == user_id)
            .scalar()
        )

        return {
            "total_content": total_content or 0,
            "by_type": {type_: count for type_, count in by_type},
            "by_language": {lang: count for lang, count in by_language},
            "total_materials": total_materials or 0,
        }

    # ===== Tag Management Methods (Session 129) =====

    def add_tag(self, content_id: str, user_id: int, tag: str) -> bool:
        """
        Add a tag to content

        Args:
            content_id: Content ID
            user_id: User ID
            tag: Tag string

        Returns:
            True if added, False if already exists

        Raises:
            ValueError: If content not found or tag invalid
        """
        # Validate tag
        if not tag or not tag.strip():
            raise ValueError("Tag cannot be empty")

        tag = tag.strip().lower()  # Normalize tag

        # Verify content exists and user owns it
        content = (
            self.db.query(ProcessedContent)
            .filter(
                and_(
                    ProcessedContent.content_id == content_id,
                    ProcessedContent.user_id == user_id,
                )
            )
            .first()
        )

        if not content:
            raise ValueError(f"Content {content_id} not found or not owned by user")

        # Check if tag already exists
        existing = (
            self.db.query(ContentTag)
            .filter(
                and_(
                    ContentTag.content_id == content_id,
                    ContentTag.user_id == user_id,
                    ContentTag.tag == tag,
                )
            )
            .first()
        )

        if existing:
            logger.info(f"Tag '{tag}' already exists on content {content_id}")
            return False

        # Add tag
        content_tag = ContentTag(user_id=user_id, content_id=content_id, tag=tag)

        self.db.add(content_tag)
        self.db.commit()

        logger.info(f"Added tag '{tag}' to content {content_id}")
        return True

    def remove_tag(self, content_id: str, user_id: int, tag: str) -> bool:
        """
        Remove a tag from content

        Args:
            content_id: Content ID
            user_id: User ID
            tag: Tag string

        Returns:
            True if removed, False if not found
        """
        tag = tag.strip().lower()  # Normalize tag

        content_tag = (
            self.db.query(ContentTag)
            .filter(
                and_(
                    ContentTag.content_id == content_id,
                    ContentTag.user_id == user_id,
                    ContentTag.tag == tag,
                )
            )
            .first()
        )

        if not content_tag:
            logger.info(f"Tag '{tag}' not found on content {content_id}")
            return False

        self.db.delete(content_tag)
        self.db.commit()

        logger.info(f"Removed tag '{tag}' from content {content_id}")
        return True

    def get_content_tags(self, content_id: str, user_id: int) -> List[str]:
        """
        Get all tags for content

        Args:
            content_id: Content ID
            user_id: User ID

        Returns:
            List of tag strings
        """
        tags = (
            self.db.query(ContentTag.tag)
            .filter(
                and_(
                    ContentTag.content_id == content_id,
                    ContentTag.user_id == user_id,
                )
            )
            .all()
        )

        return [tag[0] for tag in tags]

    def get_all_user_tags(self, user_id: int) -> List[Dict]:
        """
        Get all tags for user with counts

        Args:
            user_id: User ID

        Returns:
            List of dictionaries with tag and count
        """
        tags = (
            self.db.query(ContentTag.tag, func.count(ContentTag.id).label("count"))
            .filter(ContentTag.user_id == user_id)
            .group_by(ContentTag.tag)
            .order_by(desc("count"))
            .all()
        )

        return [{"tag": tag, "count": count} for tag, count in tags]

    def search_by_tag(self, user_id: int, tag: str) -> List[ProcessedContent]:
        """
        Search content by tag

        Args:
            user_id: User ID
            tag: Tag to search for

        Returns:
            List of ProcessedContent objects
        """
        tag = tag.strip().lower()

        # Get content IDs with this tag
        content_ids = (
            self.db.query(ContentTag.content_id)
            .filter(and_(ContentTag.user_id == user_id, ContentTag.tag == tag))
            .all()
        )

        content_id_list = [cid[0] for cid in content_ids]

        if not content_id_list:
            return []

        # Get content objects
        content_list = (
            self.db.query(ProcessedContent)
            .filter(ProcessedContent.content_id.in_(content_id_list))
            .order_by(desc(ProcessedContent.created_at))
            .all()
        )

        logger.info(f"Found {len(content_list)} content items with tag '{tag}'")
        return content_list

    # ===== Favorite Management Methods (Session 129) =====

    def add_favorite(self, content_id: str, user_id: int) -> bool:
        """
        Mark content as favorite

        Args:
            content_id: Content ID
            user_id: User ID

        Returns:
            True if added, False if already favorited

        Raises:
            ValueError: If content not found
        """
        # Verify content exists and user owns it
        content = (
            self.db.query(ProcessedContent)
            .filter(
                and_(
                    ProcessedContent.content_id == content_id,
                    ProcessedContent.user_id == user_id,
                )
            )
            .first()
        )

        if not content:
            raise ValueError(f"Content {content_id} not found or not owned by user")

        # Check if already favorited
        existing = (
            self.db.query(ContentFavorite)
            .filter(
                and_(
                    ContentFavorite.content_id == content_id,
                    ContentFavorite.user_id == user_id,
                )
            )
            .first()
        )

        if existing:
            logger.info(f"Content {content_id} already favorited")
            return False

        # Add favorite
        favorite = ContentFavorite(user_id=user_id, content_id=content_id)

        self.db.add(favorite)
        self.db.commit()

        logger.info(f"Added content {content_id} to favorites")
        return True

    def remove_favorite(self, content_id: str, user_id: int) -> bool:
        """
        Remove content from favorites

        Args:
            content_id: Content ID
            user_id: User ID

        Returns:
            True if removed, False if not favorited
        """
        favorite = (
            self.db.query(ContentFavorite)
            .filter(
                and_(
                    ContentFavorite.content_id == content_id,
                    ContentFavorite.user_id == user_id,
                )
            )
            .first()
        )

        if not favorite:
            logger.info(f"Content {content_id} not in favorites")
            return False

        self.db.delete(favorite)
        self.db.commit()

        logger.info(f"Removed content {content_id} from favorites")
        return True

    def get_favorites(self, user_id: int) -> List[ProcessedContent]:
        """
        Get all favorited content for user

        Args:
            user_id: User ID

        Returns:
            List of ProcessedContent objects
        """
        # Get favorited content IDs
        content_ids = (
            self.db.query(ContentFavorite.content_id)
            .filter(ContentFavorite.user_id == user_id)
            .all()
        )

        content_id_list = [cid[0] for cid in content_ids]

        if not content_id_list:
            return []

        # Get content objects
        favorites = (
            self.db.query(ProcessedContent)
            .filter(ProcessedContent.content_id.in_(content_id_list))
            .order_by(desc(ProcessedContent.created_at))
            .all()
        )

        logger.info(f"Retrieved {len(favorites)} favorited content items")
        return favorites

    def is_favorite(self, content_id: str, user_id: int) -> bool:
        """
        Check if content is favorited

        Args:
            content_id: Content ID
            user_id: User ID

        Returns:
            True if favorited, False otherwise
        """
        favorite = (
            self.db.query(ContentFavorite)
            .filter(
                and_(
                    ContentFavorite.content_id == content_id,
                    ContentFavorite.user_id == user_id,
                )
            )
            .first()
        )

        return favorite is not None
