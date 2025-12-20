"""
Content Collection Service
AI Language Tutor App - Session 129

Provides:
- Create and manage content collections
- Add/remove content from collections
- Organize collections (color, icon, description)
- Retrieve collections with content items
- Multi-user isolation

Collections allow users to group related content together for better organization.
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.database import (
    ContentCollection,
    ContentCollectionItem,
    ProcessedContent,
)

logger = logging.getLogger(__name__)


class ContentCollectionService:
    """Service for managing content collections"""

    def __init__(self, db: Session):
        """
        Initialize the service with a database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def _generate_collection_id(self, user_id: int, name: str) -> str:
        """
        Generate unique collection ID from user ID and name

        Args:
            user_id: User ID
            name: Collection name

        Returns:
            Unique collection ID (12 characters)
        """
        timestamp = datetime.now().isoformat()
        unique_string = f"collection_{user_id}_{name}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def create_collection(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> ContentCollection:
        """
        Create a new content collection

        Args:
            user_id: User ID who owns the collection
            name: Collection name
            description: Optional collection description
            color: Optional color code for UI (e.g., "#3B82F6")
            icon: Optional icon identifier for UI (e.g., "book", "video")

        Returns:
            Created ContentCollection object

        Raises:
            ValueError: If name is empty or too long
        """
        # Validate input
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")
        if len(name) > 200:
            raise ValueError("Collection name too long (max 200 characters)")

        # Generate collection ID
        collection_id = self._generate_collection_id(user_id, name)

        # Create collection
        collection = ContentCollection(
            user_id=user_id,
            collection_id=collection_id,
            name=name.strip(),
            description=description.strip() if description else None,
            color=color,
            icon=icon,
        )

        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)

        logger.info(
            f"Created collection '{name}' (ID: {collection_id}) for user {user_id}"
        )
        return collection

    def get_user_collections(
        self, user_id: int, include_items: bool = False
    ) -> List[ContentCollection]:
        """
        Get all collections for a user

        Args:
            user_id: User ID
            include_items: Whether to include collection items (default: False)

        Returns:
            List of ContentCollection objects
        """
        query = self.db.query(ContentCollection).filter(
            ContentCollection.user_id == user_id
        )

        # Order by created_at descending (newest first)
        query = query.order_by(desc(ContentCollection.created_at))

        collections = query.all()

        logger.info(f"Retrieved {len(collections)} collections for user {user_id}")
        return collections

    def get_collection(
        self, collection_id: str, user_id: int, include_content: bool = True
    ) -> Optional[ContentCollection]:
        """
        Get a specific collection by ID

        Args:
            collection_id: Collection ID
            user_id: User ID (for ownership verification)
            include_content: Whether to include full content objects (default: True)

        Returns:
            ContentCollection object or None if not found

        Raises:
            PermissionError: If user doesn't own the collection
        """
        collection = (
            self.db.query(ContentCollection)
            .filter(ContentCollection.collection_id == collection_id)
            .first()
        )

        if not collection:
            logger.warning(f"Collection {collection_id} not found")
            return None

        # Verify ownership
        if collection.user_id != user_id:
            raise PermissionError(
                f"User {user_id} does not own collection {collection_id}"
            )

        logger.info(f"Retrieved collection {collection_id} for user {user_id}")
        return collection

    def update_collection(
        self,
        collection_id: str,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> ContentCollection:
        """
        Update collection metadata

        Args:
            collection_id: Collection ID
            user_id: User ID (for ownership verification)
            name: New name (optional)
            description: New description (optional)
            color: New color (optional)
            icon: New icon (optional)

        Returns:
            Updated ContentCollection object

        Raises:
            ValueError: If collection not found or name invalid
            PermissionError: If user doesn't own the collection
        """
        collection = self.get_collection(collection_id, user_id, include_content=False)

        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        # Update fields if provided
        if name is not None:
            if not name or not name.strip():
                raise ValueError("Collection name cannot be empty")
            if len(name) > 200:
                raise ValueError("Collection name too long (max 200 characters)")
            collection.name = name.strip()

        if description is not None:
            collection.description = description.strip() if description else None

        if color is not None:
            collection.color = color

        if icon is not None:
            collection.icon = icon

        # Update timestamp
        collection.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(collection)

        logger.info(f"Updated collection {collection_id} for user {user_id}")
        return collection

    def delete_collection(self, collection_id: str, user_id: int) -> bool:
        """
        Delete a collection (items remain, only collection deleted)

        Args:
            collection_id: Collection ID
            user_id: User ID (for ownership verification)

        Returns:
            True if deleted, False if not found

        Raises:
            PermissionError: If user doesn't own the collection
        """
        collection = self.get_collection(collection_id, user_id, include_content=False)

        if not collection:
            return False

        self.db.delete(collection)
        self.db.commit()

        logger.info(f"Deleted collection {collection_id} for user {user_id}")
        return True

    def add_content_to_collection(
        self, collection_id: str, content_id: str, user_id: int, position: int = 0
    ) -> bool:
        """
        Add content to a collection

        Args:
            collection_id: Collection ID
            content_id: Content ID to add
            user_id: User ID (for ownership verification)
            position: Position in collection (default: 0)

        Returns:
            True if added, False if already exists

        Raises:
            ValueError: If collection or content not found
            PermissionError: If user doesn't own the collection or content
        """
        # Verify collection ownership
        collection = self.get_collection(collection_id, user_id, include_content=False)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

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

        # Check if already in collection
        existing = (
            self.db.query(ContentCollectionItem)
            .filter(
                and_(
                    ContentCollectionItem.collection_id == collection_id,
                    ContentCollectionItem.content_id == content_id,
                )
            )
            .first()
        )

        if existing:
            logger.info(
                f"Content {content_id} already in collection {collection_id}, skipping"
            )
            return False

        # Add to collection
        item = ContentCollectionItem(
            collection_id=collection_id, content_id=content_id, position=position
        )

        self.db.add(item)
        self.db.commit()

        logger.info(f"Added content {content_id} to collection {collection_id}")
        return True

    def remove_content_from_collection(
        self, collection_id: str, content_id: str, user_id: int
    ) -> bool:
        """
        Remove content from a collection

        Args:
            collection_id: Collection ID
            content_id: Content ID to remove
            user_id: User ID (for ownership verification)

        Returns:
            True if removed, False if not in collection

        Raises:
            PermissionError: If user doesn't own the collection
        """
        # Verify collection ownership
        collection = self.get_collection(collection_id, user_id, include_content=False)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        # Find and delete item
        item = (
            self.db.query(ContentCollectionItem)
            .filter(
                and_(
                    ContentCollectionItem.collection_id == collection_id,
                    ContentCollectionItem.content_id == content_id,
                )
            )
            .first()
        )

        if not item:
            logger.info(
                f"Content {content_id} not in collection {collection_id}, nothing to remove"
            )
            return False

        self.db.delete(item)
        self.db.commit()

        logger.info(f"Removed content {content_id} from collection {collection_id}")
        return True

    def get_collections_for_content(
        self, content_id: str, user_id: int
    ) -> List[ContentCollection]:
        """
        Get all collections containing a specific content item

        Args:
            content_id: Content ID
            user_id: User ID (for ownership verification)

        Returns:
            List of ContentCollection objects
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
            logger.warning(
                f"Content {content_id} not found or not owned by user {user_id}"
            )
            return []

        # Get all collection items for this content
        items = (
            self.db.query(ContentCollectionItem)
            .filter(ContentCollectionItem.content_id == content_id)
            .all()
        )

        # Get collection objects
        collection_ids = [item.collection_id for item in items]
        collections = (
            self.db.query(ContentCollection)
            .filter(
                and_(
                    ContentCollection.collection_id.in_(collection_ids),
                    ContentCollection.user_id == user_id,
                )
            )
            .all()
        )

        logger.info(
            f"Found {len(collections)} collections containing content {content_id}"
        )
        return collections

    def get_collection_item_count(self, collection_id: str, user_id: int) -> int:
        """
        Get the number of items in a collection

        Args:
            collection_id: Collection ID
            user_id: User ID (for ownership verification)

        Returns:
            Number of items in collection

        Raises:
            PermissionError: If user doesn't own the collection
        """
        # Verify collection ownership
        collection = self.get_collection(collection_id, user_id, include_content=False)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")

        count = (
            self.db.query(func.count(ContentCollectionItem.id))
            .filter(ContentCollectionItem.collection_id == collection_id)
            .scalar()
        )

        return count or 0
