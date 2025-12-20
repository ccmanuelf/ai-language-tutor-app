"""
Content Collections API Endpoints
AI Language Tutor App - Session 129

Provides:
- Create and manage content collections
- Add/remove content from collections
- Organize collections (color, icon, description)
- Retrieve collections with content items
- Multi-user isolation
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser as User
from app.services.content_collection_service import ContentCollectionService

router = APIRouter()


# Request/Response Models


class CreateCollectionRequest(BaseModel):
    """Request model for creating a collection"""

    name: str = Field(..., min_length=1, max_length=200, description="Collection name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Collection description"
    )
    color: Optional[str] = Field(
        None, max_length=20, description="Color code (e.g., #3B82F6)"
    )
    icon: Optional[str] = Field(
        None, max_length=50, description="Icon identifier (e.g., book, video)"
    )


class UpdateCollectionRequest(BaseModel):
    """Request model for updating a collection"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)


class AddContentRequest(BaseModel):
    """Request model for adding content to collection"""

    content_id: str = Field(..., description="Content ID to add")
    position: int = Field(0, ge=0, description="Position in collection")


class CollectionItemResponse(BaseModel):
    """Response model for collection item"""

    id: int
    collection_id: str
    content_id: str
    added_at: str
    position: int


class CollectionResponse(BaseModel):
    """Response model for collection"""

    id: int
    collection_id: str
    user_id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    created_at: str
    updated_at: str
    item_count: int
    items: Optional[List[CollectionItemResponse]] = None


class CollectionListResponse(BaseModel):
    """Response model for list of collections"""

    total: int
    collections: List[CollectionResponse]


# API Endpoints


@router.post("/collections", response_model=CollectionResponse, status_code=201)
def create_collection(
    request: CreateCollectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Create a new content collection

    Args:
        request: Collection creation request
        current_user: Authenticated user
        db: Database session

    Returns:
        Created collection

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        service = ContentCollectionService(db)

        collection = service.create_collection(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
        )

        return collection.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {e}")


@router.get("/collections", response_model=CollectionListResponse)
def get_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get all collections for the current user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of collections with item counts

    Raises:
        HTTPException: If retrieval error occurs
    """
    try:
        service = ContentCollectionService(db)

        collections = service.get_user_collections(
            user_id=current_user.id, include_items=False
        )

        collection_dicts = [col.to_dict() for col in collections]

        return {"total": len(collection_dicts), "collections": collection_dicts}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving collections: {e}"
        )


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get a specific collection with its content items

    Args:
        collection_id: Collection ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Collection with content items

    Raises:
        HTTPException: If collection not found or access denied
    """
    try:
        service = ContentCollectionService(db)

        collection = service.get_collection(
            collection_id=collection_id, user_id=current_user.id, include_content=True
        )

        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        return collection.to_dict(include_items=True)

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving collection: {e}")


@router.put("/collections/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: str,
    request: UpdateCollectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Update collection metadata

    Args:
        collection_id: Collection ID
        request: Update request with new values
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated collection

    Raises:
        HTTPException: If collection not found or access denied
    """
    try:
        service = ContentCollectionService(db)

        collection = service.update_collection(
            collection_id=collection_id,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
        )

        return collection.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating collection: {e}")


@router.delete("/collections/{collection_id}", status_code=204)
def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Delete a collection (content items remain, only collection deleted)

    Args:
        collection_id: Collection ID
        current_user: Authenticated user
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If collection not found or access denied
    """
    try:
        service = ContentCollectionService(db)

        deleted = service.delete_collection(
            collection_id=collection_id, user_id=current_user.id
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Collection not found")

        return None

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {e}")


@router.post("/collections/{collection_id}/items", status_code=201)
def add_content_to_collection(
    collection_id: str,
    request: AddContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Add content to a collection

    Args:
        collection_id: Collection ID
        request: Request with content_id and position
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If collection/content not found or access denied
    """
    try:
        service = ContentCollectionService(db)

        added = service.add_content_to_collection(
            collection_id=collection_id,
            content_id=request.content_id,
            user_id=current_user.id,
            position=request.position,
        )

        if not added:
            return {"success": True, "message": "Content already in collection"}

        return {"success": True, "message": "Content added to collection"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error adding content to collection: {e}"
        )


@router.delete("/collections/{collection_id}/items/{content_id}", status_code=204)
def remove_content_from_collection(
    collection_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Remove content from a collection

    Args:
        collection_id: Collection ID
        content_id: Content ID to remove
        current_user: Authenticated user
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If collection not found or access denied
    """
    try:
        service = ContentCollectionService(db)

        removed = service.remove_content_from_collection(
            collection_id=collection_id,
            content_id=content_id,
            user_id=current_user.id,
        )

        if not removed:
            raise HTTPException(status_code=404, detail="Content not in collection")

        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing content from collection: {e}"
        )


@router.get("/content/{content_id}/collections", response_model=CollectionListResponse)
def get_collections_for_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get all collections containing a specific content item

    Args:
        content_id: Content ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of collections

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentCollectionService(db)

        collections = service.get_collections_for_content(
            content_id=content_id, user_id=current_user.id
        )

        collection_dicts = [col.to_dict() for col in collections]

        return {"total": len(collection_dicts), "collections": collection_dicts}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving collections for content: {e}"
        )
