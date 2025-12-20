"""
Content Processing API Endpoints
AI Language Tutor App - Task 2.1 Implementation

Provides:
- Content upload and processing endpoints
- YouTube video processing
- Document upload and parsing
- Learning material generation
- Content library management
- Real-time processing status
"""

import shutil
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, HttpUrl

from app.core.security import get_current_user
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser as User
from app.services.content_persistence_service import ContentPersistenceService
from app.services.content_processor import (
    LearningMaterialType,
    ProcessingStatus,
    content_processor,
)

router = APIRouter()


# Request/Response Models
class ContentTypeEnum(str, Enum):
    """API-friendly content type enum"""

    youtube_video = "youtube_video"
    pdf_document = "pdf_document"
    word_document = "word_document"
    text_file = "text_file"
    web_article = "web_article"


class MaterialTypeEnum(str, Enum):
    """API-friendly material type enum"""

    summary = "summary"
    flashcards = "flashcards"
    quiz = "quiz"
    notes = "notes"
    mind_map = "mind_map"
    key_concepts = "key_concepts"
    practice_questions = "practice_questions"


class ProcessContentRequest(BaseModel):
    """Request model for processing content from URL"""

    url: HttpUrl
    material_types: Optional[List[MaterialTypeEnum]] = [
        "summary",
        "flashcards",
        "key_concepts",
    ]
    language: str = "en"
    title: Optional[str] = None


class ProcessingStatusResponse(BaseModel):
    """Response model for processing status"""

    content_id: str
    status: str
    current_step: str
    progress_percentage: int
    time_elapsed: float
    estimated_remaining: float
    details: str
    error_message: Optional[str] = None
    created_at: datetime


class ContentLibraryItem(BaseModel):
    """Response model for content library items"""

    content_id: str
    title: str
    content_type: str
    topics: List[str]
    difficulty_level: str
    created_at: datetime
    material_count: int
    word_count: int
    estimated_study_time: int


class LearningMaterialResponse(BaseModel):
    """Response model for learning materials"""

    material_id: str
    content_id: str
    material_type: str
    title: str
    content: Dict[str, Any]
    difficulty_level: str
    estimated_time: int
    tags: List[str]
    created_at: datetime


class ProcessedContentResponse(BaseModel):
    """Response model for complete processed content"""

    metadata: Dict[str, Any]
    content_preview: str  # First 500 chars
    learning_materials: List[LearningMaterialResponse]
    processing_stats: Dict[str, Any]


@router.post("/process/url", response_model=Dict[str, str])
async def process_content_from_url(
    request: ProcessContentRequest, current_user: User = Depends(get_current_user)
):
    """
    Process content from URL (YouTube, web articles, etc.)

    Returns content_id for tracking processing progress
    """
    try:
        # Convert material types to internal enum
        material_types = [
            LearningMaterialType(mt.value) for mt in request.material_types
        ]

        # Start content processing
        content_id = await content_processor.process_content(
            source=str(request.url),
            material_types=material_types,
            language=request.language,
        )

        return {
            "content_id": content_id,
            "message": "Content processing started",
            "status_url": f"/api/content/status/{content_id}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to process content: {str(e)}"
        )


@router.post("/process/upload", response_model=Dict[str, str])
async def process_uploaded_file(
    file: UploadFile = File(...),
    material_types: List[MaterialTypeEnum] = Form(
        ["summary", "flashcards", "key_concepts"]
    ),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user),
):
    """
    Process uploaded file (PDF, DOCX, TXT, etc.)

    Returns content_id for tracking processing progress
    """
    try:
        # Validate file type
        allowed_extensions = {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"}
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}",
            )

        # Save uploaded file temporarily
        temp_dir = Path(tempfile.gettempdir()) / "ai_tutor_uploads"
        temp_dir.mkdir(exist_ok=True)

        temp_file_path = (
            temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        )

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert material types to internal enum
        material_types_enum = [LearningMaterialType(mt.value) for mt in material_types]

        # Start content processing
        content_id = await content_processor.process_content(
            source=file.filename,
            file_path=temp_file_path,
            material_types=material_types_enum,
            language=language,
        )

        return {
            "content_id": content_id,
            "message": f"File '{file.filename}' processing started",
            "status_url": f"/api/content/status/{content_id}",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")


@router.get("/status/{content_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    content_id: str, current_user: User = Depends(get_current_user)
):
    """Get real-time processing status for content"""
    try:
        progress = await content_processor.get_processing_progress(content_id)

        if not progress:
            raise HTTPException(
                status_code=404, detail=f"Content ID {content_id} not found"
            )

        return ProcessingStatusResponse(
            content_id=progress.content_id,
            status=progress.status.value,
            current_step=progress.current_step,
            progress_percentage=progress.progress_percentage,
            time_elapsed=progress.time_elapsed,
            estimated_remaining=progress.estimated_remaining,
            details=progress.details,
            error_message=progress.error_message,
            created_at=progress.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/content/{content_id}", response_model=ProcessedContentResponse)
async def get_processed_content(
    content_id: str, current_user: User = Depends(get_current_user)
):
    """Get processed content and learning materials"""
    try:
        processed = await content_processor.get_processed_content(content_id)

        if not processed:
            raise HTTPException(
                status_code=404, detail=f"Content ID {content_id} not found"
            )

        # Convert learning materials to response format
        materials = [
            LearningMaterialResponse(
                material_id=material.material_id,
                content_id=material.content_id,
                material_type=material.material_type.value,
                title=material.title,
                content=material.content,
                difficulty_level=material.difficulty_level,
                estimated_time=material.estimated_time,
                tags=material.tags,
                created_at=material.created_at,
            )
            for material in processed.learning_materials
        ]

        # Convert metadata to dict
        metadata_dict = {
            "content_id": processed.metadata.content_id,
            "title": processed.metadata.title,
            "content_type": processed.metadata.content_type.value,
            "source_url": processed.metadata.source_url,
            "language": processed.metadata.language,
            "duration": processed.metadata.duration,
            "word_count": processed.metadata.word_count,
            "difficulty_level": processed.metadata.difficulty_level,
            "topics": processed.metadata.topics,
            "author": processed.metadata.author,
            "created_at": processed.metadata.created_at,
            "file_size": processed.metadata.file_size,
        }

        return ProcessedContentResponse(
            metadata=metadata_dict,
            content_preview=processed.processed_content[:500],
            learning_materials=materials,
            processing_stats=processed.processing_stats,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")


@router.get("/library", response_model=List[ContentLibraryItem])
def _apply_content_type_filter(
    library: List[Dict[str, Any]], content_type: Optional[ContentTypeEnum]
) -> List[Dict[str, Any]]:
    """Apply content type filter to library"""
    if content_type:
        return [item for item in library if item["content_type"] == content_type.value]
    return library


def _apply_difficulty_filter(
    library: List[Dict[str, Any]], difficulty: Optional[str]
) -> List[Dict[str, Any]]:
    """Apply difficulty filter to library"""
    if difficulty:
        return [item for item in library if item["difficulty_level"] == difficulty]
    return library


def _apply_language_filter(
    library: List[Dict[str, Any]], language: Optional[str]
) -> List[Dict[str, Any]]:
    """Apply language filter to library"""
    if language:
        return [item for item in library if item.get("language") == language]
    return library


def _apply_pagination(
    library: List[Dict[str, Any]], offset: int, limit: int
) -> List[Dict[str, Any]]:
    """Apply pagination to library"""
    return library[offset : offset + limit]


def _convert_to_response_items(
    library: List[Dict[str, Any]],
) -> List[ContentLibraryItem]:
    """Convert library items to response format"""
    return [
        ContentLibraryItem(
            content_id=item["content_id"],
            title=item["title"],
            content_type=item["content_type"],
            topics=item["topics"],
            difficulty_level=item["difficulty_level"],
            created_at=datetime.fromisoformat(item["created_at"]),
            material_count=item["material_count"],
            word_count=item["word_count"],
            estimated_study_time=item["estimated_study_time"],
        )
        for item in library
    ]


async def get_content_library(
    limit: int = 50,
    offset: int = 0,
    content_type: Optional[ContentTypeEnum] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get user's content library with filtering and pagination"""
    try:
        library = await content_processor.get_content_library()

        library = _apply_content_type_filter(library, content_type)
        library = _apply_difficulty_filter(library, difficulty)
        library = _apply_language_filter(library, language)
        library = _apply_pagination(library, offset, limit)

        return _convert_to_response_items(library)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get library: {str(e)}")


@router.get("/search")
async def search_content(
    query: str,
    content_type: Optional[ContentTypeEnum] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    """Search content library"""
    try:
        # Prepare filters
        filters = {}
        if content_type:
            filters["content_type"] = content_type.value
        if difficulty:
            filters["difficulty_level"] = difficulty
        if language:
            filters["language"] = language

        # Perform search
        results = await content_processor.search_content(query, filters)

        # Apply limit
        results = results[:limit]

        return {"query": query, "total_results": len(results), "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/material/{material_id}")
async def get_learning_material(
    material_id: str, current_user: User = Depends(get_current_user)
):
    """Get specific learning material by ID"""
    try:
        # Find material in content library
        for content_id, processed in content_processor.content_library.items():
            for material in processed.learning_materials:
                if material.material_id == material_id:
                    return LearningMaterialResponse(
                        material_id=material.material_id,
                        content_id=material.content_id,
                        material_type=material.material_type.value,
                        title=material.title,
                        content=material.content,
                        difficulty_level=material.difficulty_level,
                        estimated_time=material.estimated_time,
                        tags=material.tags,
                        created_at=material.created_at,
                    )

        raise HTTPException(
            status_code=404, detail=f"Material ID {material_id} not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material: {str(e)}")


@router.delete("/content/{content_id}")
async def delete_content(
    content_id: str, current_user: User = Depends(get_current_user)
):
    """Delete processed content and its materials"""
    try:
        if content_id not in content_processor.content_library:
            raise HTTPException(
                status_code=404, detail=f"Content ID {content_id} not found"
            )

        # Remove from library
        del content_processor.content_library[content_id]

        # Remove processing progress if exists
        if content_id in content_processor.processing_progress:
            del content_processor.processing_progress[content_id]

        return {"message": f"Content {content_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete content: {str(e)}"
        )


@router.get("/stats")
async def get_content_stats(current_user: User = Depends(get_current_user)):
    """Get content library statistics"""
    try:
        library = await content_processor.get_content_library()

        # Calculate statistics
        total_content = len(library)
        total_materials = sum(item["material_count"] for item in library)
        total_study_time = sum(item["estimated_study_time"] for item in library)

        # Count by content type
        content_types = {}
        for item in library:
            content_type = item["content_type"]
            content_types[content_type] = content_types.get(content_type, 0) + 1

        # Count by difficulty
        difficulties = {}
        for item in library:
            difficulty = item["difficulty_level"]
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1

        return {
            "total_content": total_content,
            "total_materials": total_materials,
            "total_study_time_minutes": total_study_time,
            "content_by_type": content_types,
            "content_by_difficulty": difficulties,
            "average_materials_per_content": total_materials / total_content
            if total_content > 0
            else 0,
            "average_study_time_per_content": total_study_time / total_content
            if total_content > 0
            else 0,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ===== Tag Management Endpoints (Session 129) =====


class AddTagRequest(BaseModel):
    """Request model for adding a tag"""

    tag: str = Field(..., min_length=1, max_length=100, description="Tag name")


class TagResponse(BaseModel):
    """Response model for tag"""

    tag: str
    count: int


@router.post("/{content_id}/tags", status_code=201)
def add_tag_to_content(
    content_id: str,
    request: AddTagRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Add a tag to content

    Args:
        content_id: Content ID
        request: Tag to add
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message with all tags

    Raises:
        HTTPException: If content not found or error occurs
    """
    try:
        service = ContentPersistenceService(db)

        added = service.add_tag(
            content_id=content_id, user_id=current_user.id, tag=request.tag
        )

        tags = service.get_content_tags(content_id=content_id, user_id=current_user.id)

        return {
            "success": True,
            "message": "Tag added" if added else "Tag already exists",
            "tags": tags,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding tag: {e}")


@router.delete("/{content_id}/tags/{tag}", status_code=204)
def remove_tag_from_content(
    content_id: str,
    tag: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Remove a tag from content

    Args:
        content_id: Content ID
        tag: Tag to remove
        current_user: Authenticated user
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If tag not found
    """
    try:
        service = ContentPersistenceService(db)

        removed = service.remove_tag(
            content_id=content_id, user_id=current_user.id, tag=tag
        )

        if not removed:
            raise HTTPException(status_code=404, detail="Tag not found")

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing tag: {e}")


@router.get("/tags", response_model=List[TagResponse])
def get_all_user_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get all tags for user with counts

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of tags with counts

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentPersistenceService(db)

        tags = service.get_all_user_tags(user_id=current_user.id)

        return tags

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tags: {e}")


@router.get("/tags/{tag}/content")
def get_content_by_tag(
    tag: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get all content with a specific tag

    Args:
        tag: Tag to search for
        current_user: Authenticated user
        db: Database session

    Returns:
        List of content items

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentPersistenceService(db)

        content_list = service.search_by_tag(user_id=current_user.id, tag=tag)

        return {
            "total": len(content_list),
            "content": [c.to_dict() for c in content_list],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching by tag: {e}")


# ===== Favorite Management Endpoints (Session 129) =====


@router.post("/{content_id}/favorite", status_code=201)
def add_content_to_favorites(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Mark content as favorite

    Args:
        content_id: Content ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If content not found
    """
    try:
        service = ContentPersistenceService(db)

        added = service.add_favorite(content_id=content_id, user_id=current_user.id)

        return {
            "success": True,
            "message": "Added to favorites" if added else "Already favorited",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to favorites: {e}")


@router.delete("/{content_id}/favorite", status_code=204)
def remove_content_from_favorites(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Remove content from favorites

    Args:
        content_id: Content ID
        current_user: Authenticated user
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If not favorited
    """
    try:
        service = ContentPersistenceService(db)

        removed = service.remove_favorite(
            content_id=content_id, user_id=current_user.id
        )

        if not removed:
            raise HTTPException(status_code=404, detail="Content not in favorites")

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing from favorites: {e}"
        )


@router.get("/favorites")
def get_favorited_content(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get all favorited content for user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of favorited content

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentPersistenceService(db)

        favorites = service.get_favorites(user_id=current_user.id)

        return {"total": len(favorites), "content": [c.to_dict() for c in favorites]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving favorites: {e}")


# Health check for content processing service
@router.get("/health")
async def content_service_health():
    """Health check for content processing service"""
    try:
        # Check if processor is responsive
        stats = {
            "status": "healthy",
            "service": "content-processor",
            "active_processing": len(
                [
                    p
                    for p in content_processor.processing_progress.values()
                    if p.status
                    in [
                        ProcessingStatus.QUEUED,
                        ProcessingStatus.EXTRACTING,
                        ProcessingStatus.ANALYZING,
                        ProcessingStatus.GENERATING,
                    ]
                ]
            ),
            "total_content": len(content_processor.content_library),
            "temp_dir_exists": content_processor.temp_dir.exists(),
            "timestamp": datetime.now().isoformat(),
        }

        return stats

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "content-processor",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
