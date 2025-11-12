"""
Comprehensive tests for Content Processor module
AI Language Tutor App - YouLearn functionality testing

Tests cover:
- Enum and dataclass definitions
- Content type detection
- YouTube video processing
- PDF/DOCX/text file extraction
- AI-powered content analysis
- Learning material generation
- Content library management
- Search functionality
"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.services.content_processor import (
    ContentMetadata,
    ContentProcessor,
    ContentType,
    LearningMaterial,
    LearningMaterialType,
    ProcessedContent,
    ProcessingProgress,
    ProcessingStatus,
    content_processor,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def processor():
    """Create a fresh ContentProcessor instance for testing"""
    return ContentProcessor()


@pytest.fixture
def sample_youtube_url():
    """Sample YouTube URL"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_youtube_short_url():
    """Sample YouTube short URL"""
    return "https://youtu.be/dQw4w9WgXcQ"


@pytest.fixture
def sample_content_metadata():
    """Sample content metadata"""
    return ContentMetadata(
        content_id="test123",
        title="Test Content",
        content_type=ContentType.YOUTUBE_VIDEO,
        source_url="https://example.com",
        language="en",
        duration=10.5,
        word_count=1000,
        difficulty_level="intermediate",
        topics=["Python", "Testing"],
        author="Test Author",
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_learning_material():
    """Sample learning material"""
    return LearningMaterial(
        material_id="mat123",
        content_id="test123",
        material_type=LearningMaterialType.SUMMARY,
        title="Test Summary",
        content={"main_points": ["point1", "point2"]},
        difficulty_level="intermediate",
        estimated_time=5,
        tags=["test"],
    )


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Create a temporary PDF-like file for testing"""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%test content")
    return pdf_file


@pytest.fixture
def temp_text_file(tmp_path):
    """Create a temporary text file for testing"""
    text_file = tmp_path / "test.txt"
    text_file.write_text("Test Title\nThis is test content for processing.")
    return text_file


# ============================================================================
# Test Enums and DataClasses
# ============================================================================


class TestEnumsAndDataClasses:
    """Test enum and dataclass definitions"""

    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.YOUTUBE_VIDEO.value == "youtube_video"
        assert ContentType.PDF_DOCUMENT.value == "pdf_document"
        assert ContentType.WORD_DOCUMENT.value == "word_document"
        assert ContentType.TEXT_FILE.value == "text_file"
        assert ContentType.WEB_ARTICLE.value == "web_article"
        assert ContentType.AUDIO_FILE.value == "audio_file"
        assert ContentType.IMAGE_FILE.value == "image_file"
        assert ContentType.UNKNOWN.value == "unknown"

    def test_processing_status_enum(self):
        """Test ProcessingStatus enum values"""
        assert ProcessingStatus.QUEUED.value == "queued"
        assert ProcessingStatus.EXTRACTING.value == "extracting"
        assert ProcessingStatus.ANALYZING.value == "analyzing"
        assert ProcessingStatus.GENERATING.value == "generating"
        assert ProcessingStatus.ORGANIZING.value == "organizing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"

    def test_learning_material_type_enum(self):
        """Test LearningMaterialType enum values"""
        assert LearningMaterialType.SUMMARY.value == "summary"
        assert LearningMaterialType.FLASHCARDS.value == "flashcards"
        assert LearningMaterialType.QUIZ.value == "quiz"
        assert LearningMaterialType.NOTES.value == "notes"
        assert LearningMaterialType.MIND_MAP.value == "mind_map"
        assert LearningMaterialType.KEY_CONCEPTS.value == "key_concepts"
        assert LearningMaterialType.PRACTICE_QUESTIONS.value == "practice_questions"

    def test_processing_progress_creation(self):
        """Test ProcessingProgress dataclass creation"""
        progress = ProcessingProgress(
            content_id="test123",
            status=ProcessingStatus.QUEUED,
            current_step="Starting",
            progress_percentage=0,
            time_elapsed=0.0,
            estimated_remaining=0.0,
            details="Processing started",
        )

        assert progress.content_id == "test123"
        assert progress.status == ProcessingStatus.QUEUED
        assert progress.current_step == "Starting"
        assert progress.progress_percentage == 0
        assert progress.created_at is not None  # Auto-populated
        assert progress.error_message is None

    def test_content_metadata_creation(self, sample_content_metadata):
        """Test ContentMetadata dataclass creation"""
        assert sample_content_metadata.content_id == "test123"
        assert sample_content_metadata.title == "Test Content"
        assert sample_content_metadata.content_type == ContentType.YOUTUBE_VIDEO
        assert sample_content_metadata.language == "en"
        assert sample_content_metadata.word_count == 1000
        assert len(sample_content_metadata.topics) == 2

    def test_content_metadata_type_conversion(self):
        """Test ContentMetadata converts string to ContentType enum"""
        metadata = ContentMetadata(
            content_id="test",
            title="Test",
            content_type="youtube_video",  # String instead of enum
            source_url=None,
            language="en",
            duration=None,
            word_count=100,
            difficulty_level="beginner",
            topics=[],
            author=None,
            created_at=datetime.now(),
        )

        assert metadata.content_type == ContentType.YOUTUBE_VIDEO
        assert isinstance(metadata.content_type, ContentType)

    def test_learning_material_creation(self, sample_learning_material):
        """Test LearningMaterial dataclass creation"""
        assert sample_learning_material.material_id == "mat123"
        assert sample_learning_material.content_id == "test123"
        assert sample_learning_material.material_type == LearningMaterialType.SUMMARY
        assert sample_learning_material.estimated_time == 5
        assert sample_learning_material.created_at is not None

    def test_learning_material_type_conversion(self):
        """Test LearningMaterial converts string to enum"""
        material = LearningMaterial(
            material_id="test",
            content_id="content123",
            material_type="summary",  # String instead of enum
            title="Test",
            content={},
            difficulty_level="beginner",
            estimated_time=5,
            tags=[],
        )

        assert material.material_type == LearningMaterialType.SUMMARY
        assert isinstance(material.material_type, LearningMaterialType)

    def test_processed_content_creation(
        self, sample_content_metadata, sample_learning_material
    ):
        """Test ProcessedContent dataclass creation"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="Raw content here",
            processed_content="Processed content",
            learning_materials=[sample_learning_material],
            processing_stats={"time": 1.5, "materials": 1},
        )

        assert processed.metadata.content_id == "test123"
        assert processed.raw_content == "Raw content here"
        assert len(processed.learning_materials) == 1
        assert processed.processing_stats["time"] == 1.5


# ============================================================================
# Test ContentProcessor Initialization
# ============================================================================


class TestContentProcessorInit:
    """Test ContentProcessor initialization"""

    def test_init_basic_attributes(self, processor):
        """Test processor initialization creates expected attributes"""
        assert processor.settings is not None
        assert isinstance(processor.processing_progress, dict)
        assert isinstance(processor.content_library, dict)
        assert isinstance(processor.temp_dir, Path)
        assert processor.temp_dir.exists()

    def test_init_configuration(self, processor):
        """Test processor configuration values"""
        assert processor.max_content_length == 50000
        assert len(processor.supported_languages) >= 9
        assert "en" in processor.supported_languages
        assert "zh" in processor.supported_languages
        assert processor.processing_timeout == 120

    def test_init_temp_directory_creation(self, processor):
        """Test temp directory is created"""
        assert processor.temp_dir.exists()
        assert processor.temp_dir.is_dir()

    def test_global_instance_exists(self):
        """Test global content_processor instance exists"""
        assert content_processor is not None
        assert isinstance(content_processor, ContentProcessor)


# ============================================================================
# Test Helper Methods
# ============================================================================


class TestHelperMethods:
    """Test helper methods"""

    def test_generate_content_id(self, processor):
        """Test content ID generation"""
        content_id1 = processor._generate_content_id("https://example.com/video")
        content_id2 = processor._generate_content_id("https://example.com/video")

        # IDs should be valid hex strings
        assert len(content_id1) == 12
        assert all(c in "0123456789abcdef" for c in content_id1)

        # Different calls should generate different IDs (due to timestamp)
        assert content_id1 != content_id2

    def test_generate_content_id_consistent_format(self, processor):
        """Test content ID has consistent format"""
        content_id = processor._generate_content_id("test_source")

        assert isinstance(content_id, str)
        assert len(content_id) == 12
        # MD5 hash should be hex
        int(content_id, 16)  # Should not raise ValueError

    def test_update_progress_new_content(self, processor):
        """Test updating progress for new content"""
        processor._update_progress(
            "test123",
            ProcessingStatus.QUEUED,
            "Starting",
            0,
            "Test progress",
        )

        assert "test123" in processor.processing_progress
        progress = processor.processing_progress["test123"]
        assert progress.status == ProcessingStatus.QUEUED
        assert progress.current_step == "Starting"
        assert progress.progress_percentage == 0
        assert progress.details == "Test progress"

    def test_update_progress_existing_content(self, processor):
        """Test updating progress for existing content"""
        # Create initial progress
        processor._update_progress(
            "test123", ProcessingStatus.QUEUED, "Starting", 0, "Initial"
        )

        # Update progress
        processor._update_progress(
            "test123", ProcessingStatus.EXTRACTING, "Extracting", 20, "Updated"
        )

        progress = processor.processing_progress["test123"]
        assert progress.status == ProcessingStatus.EXTRACTING
        assert progress.current_step == "Extracting"
        assert progress.progress_percentage == 20
        assert progress.details == "Updated"

    def test_update_progress_with_error(self, processor):
        """Test updating progress with error message"""
        processor._update_progress(
            "test123",
            ProcessingStatus.FAILED,
            "Failed",
            0,
            "Error occurred",
            "Test error message",
        )

        progress = processor.processing_progress["test123"]
        assert progress.status == ProcessingStatus.FAILED
        assert progress.error_message == "Test error message"

    def test_update_progress_time_estimation(self, processor):
        """Test progress time estimation calculation"""
        # Create progress at 50%
        processor._update_progress(
            "test123", ProcessingStatus.EXTRACTING, "Extracting", 50, "Halfway"
        )

        progress = processor.processing_progress["test123"]
        # At 50%, estimated remaining should be approximately equal to time elapsed
        assert progress.estimated_remaining >= 0

    @pytest.mark.asyncio
    async def test_get_processing_progress_exists(self, processor):
        """Test getting progress for existing content"""
        processor._update_progress(
            "test123", ProcessingStatus.QUEUED, "Starting", 0, "Test"
        )

        progress = await processor.get_processing_progress("test123")
        assert progress is not None
        assert progress.content_id == "test123"

    @pytest.mark.asyncio
    async def test_get_processing_progress_not_exists(self, processor):
        """Test getting progress for non-existent content"""
        progress = await processor.get_processing_progress("nonexistent")
        assert progress is None


# ============================================================================
# Test Content Type Detection
# ============================================================================


class TestContentTypeDetection:
    """Test content type detection"""

    def test_detect_youtube_standard_url(self, processor):
        """Test YouTube detection from standard URL"""
        content_type = processor._detect_content_type(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert content_type == ContentType.YOUTUBE_VIDEO

    def test_detect_youtube_short_url(self, processor):
        """Test YouTube detection from short URL"""
        content_type = processor._detect_content_type("https://youtu.be/dQw4w9WgXcQ")
        assert content_type == ContentType.YOUTUBE_VIDEO

    def test_detect_youtube_mobile_url(self, processor):
        """Test YouTube detection from mobile URL"""
        content_type = processor._detect_content_type(
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert content_type == ContentType.YOUTUBE_VIDEO

    def test_detect_pdf_from_file_path(self, processor, temp_pdf_file):
        """Test PDF detection from file path"""
        content_type = processor._detect_content_type("source", file_path=temp_pdf_file)
        assert content_type == ContentType.PDF_DOCUMENT

    def test_detect_docx_from_file_path(self, processor, tmp_path):
        """Test DOCX detection from file path"""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        content_type = processor._detect_content_type("source", file_path=docx_file)
        assert content_type == ContentType.WORD_DOCUMENT

    def test_detect_text_from_file_path(self, processor, temp_text_file):
        """Test text file detection from file path"""
        content_type = processor._detect_content_type(
            "source", file_path=temp_text_file
        )
        assert content_type == ContentType.TEXT_FILE

    def test_detect_web_article(self, processor):
        """Test web article detection"""
        content_type = processor._detect_content_type("https://example.com/article")
        assert content_type == ContentType.WEB_ARTICLE

    def test_detect_unknown(self, processor):
        """Test unknown content type"""
        content_type = processor._detect_content_type("just some text")
        assert content_type == ContentType.UNKNOWN


# ============================================================================
# Test YouTube ID Extraction
# ============================================================================


class TestYouTubeIDExtraction:
    """Test YouTube video ID extraction"""

    def test_extract_youtube_id_standard_url(self, processor):
        """Test extracting ID from standard YouTube URL"""
        video_id = processor._extract_youtube_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_youtube_id_short_url(self, processor):
        """Test extracting ID from short URL (youtu.be)"""
        video_id = processor._extract_youtube_id("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_youtube_id_embed_url(self, processor):
        """Test extracting ID from embed URL"""
        video_id = processor._extract_youtube_id(
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_youtube_id_mobile_url(self, processor):
        """Test extracting ID from mobile URL"""
        video_id = processor._extract_youtube_id(
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_youtube_id_with_extra_params(self, processor):
        """Test extracting ID with additional URL parameters"""
        video_id = processor._extract_youtube_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest&index=1"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_youtube_id_invalid_url(self, processor):
        """Test extracting ID from invalid URL"""
        video_id = processor._extract_youtube_id("https://example.com/not-youtube")
        assert video_id is None

    def test_extract_youtube_id_malformed_url(self, processor):
        """Test extracting ID from malformed URL"""
        video_id = processor._extract_youtube_id("not a url at all")
        assert video_id is None

    def test_extract_youtube_id_exception_handling(self, processor):
        """Test exception handling in YouTube ID extraction

        This tests lines 281-283 in content_processor.py where exceptions
        during URL parsing are caught and logged.
        """
        from unittest.mock import patch

        # Mock urlparse to raise an exception
        with patch(
            "app.services.content_processor.urlparse",
            side_effect=Exception("Parse error"),
        ):
            video_id = processor._extract_youtube_id(
                "https://www.youtube.com/watch?v=test"
            )

            # Should return None when exception occurs
            assert video_id is None


# Will continue with more test classes in next part...


# ============================================================================
# Test YouTube Content Extraction
# ============================================================================


class TestYouTubeContentExtraction:
    """Test YouTube content extraction with mocked yt-dlp and transcript API"""

    @pytest.mark.asyncio
    async def test_extract_youtube_content_success(self, processor):
        """Test successful YouTube content extraction"""
        mock_info = {
            "title": "Test Video Title",
            "description": "Test video description",
            "duration": 600,  # 10 minutes in seconds
            "uploader": "Test Channel",
        }

        mock_transcript_data = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "This is a test", "start": 2.0, "duration": 3.0},
        ]

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            # Mock yt-dlp
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = mock_info
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            # Mock transcript API
            with patch(
                "app.services.content_processor.YouTubeTranscriptApi"
            ) as mock_api_class:
                mock_transcript = Mock()
                mock_transcript.fetch.return_value = mock_transcript_data

                mock_transcript_list = Mock()
                mock_transcript_list.find_transcript.return_value = mock_transcript

                mock_api_instance = Mock()
                mock_api_instance.list.return_value = mock_transcript_list
                mock_api_class.return_value = mock_api_instance

                # Mock TextFormatter
                with patch(
                    "app.services.content_processor.TextFormatter"
                ) as mock_formatter:
                    mock_formatter.return_value.format_transcript.return_value = (
                        "Hello world This is a test"
                    )

                    result = await processor._extract_youtube_content(
                        "https://www.youtube.com/watch?v=test123"
                    )

                    assert result["title"] == "Test Video Title"
                    assert result["duration"] == 10.0  # 600 seconds / 60
                    assert result["author"] == "Test Channel"
                    assert "Hello world" in result["content"]
                    assert result["language"] == "en"
                    assert result["word_count"] > 0

    @pytest.mark.asyncio
    async def test_extract_youtube_content_no_transcript(self, processor):
        """Test YouTube extraction when transcript unavailable"""
        mock_info = {
            "title": "Test Video",
            "description": "Fallback description text",
            "duration": 300,
            "uploader": "Test",
        }

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = mock_info
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            # Mock transcript API to raise exception
            with patch(
                "app.services.content_processor.YouTubeTranscriptApi"
            ) as mock_api_class:
                mock_api_instance = Mock()
                mock_api_instance.list.side_effect = Exception("No transcript")
                mock_api_class.return_value = mock_api_instance

                result = await processor._extract_youtube_content(
                    "https://www.youtube.com/watch?v=test123"
                )

                # Should fallback to description
                assert result["content"] == "Fallback description text"
                assert result["title"] == "Test Video"

    @pytest.mark.asyncio
    async def test_extract_youtube_content_invalid_url(self, processor):
        """Test YouTube extraction with invalid URL"""
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            await processor._extract_youtube_content("https://example.com/not-youtube")

    @pytest.mark.asyncio
    async def test_extract_youtube_content_ydl_error(self, processor):
        """Test YouTube extraction when yt-dlp fails"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.side_effect = Exception("Download error")
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with pytest.raises(ValueError, match="Could not process YouTube video"):
                await processor._extract_youtube_content(
                    "https://www.youtube.com/watch?v=test123"
                )


# ============================================================================
# Test Document Content Extraction
# ============================================================================


class TestDocumentContentExtraction:
    """Test PDF, DOCX, and text file content extraction"""

    @pytest.mark.asyncio
    async def test_extract_pdf_content_success(self, processor, tmp_path):
        """Test successful PDF content extraction"""
        pdf_file = tmp_path / "test.pdf"

        # Mock pypdf.PdfReader
        with patch("app.services.content_processor.pypdf.PdfReader") as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content\n"

            mock_pdf = Mock()
            mock_pdf.pages = [mock_page, mock_page]
            mock_pdf.metadata = {"/Title": "Test PDF", "/Author": "Test Author"}

            mock_reader.return_value = mock_pdf

            # Create dummy file
            pdf_file.write_bytes(b"PDF content")

            result = await processor._extract_pdf_content(pdf_file)

            assert result["title"] == "Test PDF"
            assert result["author"] == "Test Author"
            assert "Test PDF content" in result["content"]
            assert result["word_count"] > 0
            assert result["page_count"] == 2

    @pytest.mark.asyncio
    async def test_extract_pdf_content_no_metadata(self, processor, tmp_path):
        """Test PDF extraction without metadata"""
        pdf_file = tmp_path / "test.pdf"

        with patch("app.services.content_processor.pypdf.PdfReader") as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Content here\n"

            mock_pdf = Mock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = None  # No metadata

            mock_reader.return_value = mock_pdf

            pdf_file.write_bytes(b"PDF")

            result = await processor._extract_pdf_content(pdf_file)

            # Should use filename as title
            assert result["title"] == "test"
            assert result["author"] == "Unknown"

    @pytest.mark.asyncio
    async def test_extract_pdf_content_error(self, processor, tmp_path):
        """Test PDF extraction error handling"""
        pdf_file = tmp_path / "bad.pdf"
        pdf_file.write_bytes(b"Invalid")

        with patch(
            "app.services.content_processor.pypdf.PdfReader",
            side_effect=Exception("PDF error"),
        ):
            with pytest.raises(ValueError, match="Could not process PDF file"):
                await processor._extract_pdf_content(pdf_file)

    @pytest.mark.asyncio
    async def test_extract_docx_content_success(self, processor, tmp_path):
        """Test successful DOCX content extraction"""
        docx_file = tmp_path / "test.docx"

        # Mock python-docx Document
        with patch("app.services.content_processor.Document") as mock_doc_class:
            mock_para1 = Mock()
            mock_para1.text = "First paragraph"
            mock_para2 = Mock()
            mock_para2.text = "Second paragraph"

            mock_doc = Mock()
            mock_doc.paragraphs = [mock_para1, mock_para2]

            mock_doc_class.return_value = mock_doc

            docx_file.write_bytes(b"DOCX content")

            result = await processor._extract_docx_content(docx_file)

            assert "First paragraph" in result["title"]
            assert "First paragraph\nSecond paragraph" == result["content"]
            assert result["word_count"] == 4

    @pytest.mark.asyncio
    async def test_extract_docx_content_long_title(self, processor, tmp_path):
        """Test DOCX with very long first paragraph (title truncation)"""
        docx_file = tmp_path / "test.docx"

        with patch("app.services.content_processor.Document") as mock_doc_class:
            mock_para = Mock()
            mock_para.text = "A" * 100  # 100 characters

            mock_doc = Mock()
            mock_doc.paragraphs = [mock_para]

            mock_doc_class.return_value = mock_doc

            docx_file.write_bytes(b"DOCX")

            result = await processor._extract_docx_content(docx_file)

            # Title should be truncated to 50 chars + "..."
            assert len(result["title"]) == 53
            assert result["title"].endswith("...")

    @pytest.mark.asyncio
    async def test_extract_docx_content_error(self, processor, tmp_path):
        """Test DOCX extraction error handling"""
        docx_file = tmp_path / "bad.docx"
        docx_file.write_bytes(b"Invalid")

        with patch(
            "app.services.content_processor.Document",
            side_effect=Exception("DOCX error"),
        ):
            with pytest.raises(ValueError, match="Could not process Word document"):
                await processor._extract_docx_content(docx_file)

    @pytest.mark.asyncio
    async def test_extract_text_content_success(self, processor, tmp_path):
        """Test successful text file extraction"""
        text_file = tmp_path / "test.txt"
        text_file.write_text("Title Line\nThis is the content\nMore content here")

        result = await processor._extract_text_content(text_file)

        assert result["title"] == "Title Line"
        assert "This is the content" in result["content"]
        assert result["word_count"] == 9
        assert result["line_count"] == 3

    @pytest.mark.asyncio
    async def test_extract_text_content_empty_file(self, processor, tmp_path):
        """Test text extraction from empty file"""
        text_file = tmp_path / "empty.txt"
        text_file.write_text("")

        result = await processor._extract_text_content(text_file)

        # Should use filename as title
        assert result["title"] == "empty"
        assert result["content"] == ""
        assert result["word_count"] == 0

    @pytest.mark.asyncio
    async def test_extract_text_content_error(self, processor, tmp_path):
        """Test text extraction error handling"""
        text_file = tmp_path / "test.txt"

        # File doesn't exist
        with pytest.raises(ValueError, match="Could not process text file"):
            await processor._extract_text_content(text_file)


# ============================================================================
# Test Web Content Extraction
# ============================================================================


class TestWebContentExtraction:
    """Test web article content extraction"""

    @pytest.mark.asyncio
    async def test_extract_web_content_placeholder(self, processor):
        """Test web content extraction (currently returns placeholder)"""
        url = "https://example.com/article"

        # Create proper async context manager mock
        mock_response = Mock()
        mock_response.text = AsyncMock(return_value="<html>Content</html>")

        # Create async context manager for session.get()
        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_get_cm)

        # Mock ClientSession context manager
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await processor._extract_web_content(url)

            assert "Web Article" in result["title"]
            assert "example.com" in result["title"]
            # Currently returns placeholder
            assert "not yet implemented" in result["content"]

    @pytest.mark.asyncio
    async def test_extract_web_content_error(self, processor):
        """Test web content extraction error handling"""
        url = "https://example.com/article"

        # Mock aiohttp to raise exception
        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__ = AsyncMock(side_effect=Exception("Network error"))
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_get_cm)

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(ValueError, match="Could not process web article"):
                await processor._extract_web_content(url)


# Continue in next part...


# ============================================================================
# Test AI Content Analysis
# ============================================================================


class TestAIContentAnalysis:
    """Test AI-powered content analysis"""

    @pytest.mark.asyncio
    async def test_analyze_content_success(self, processor):
        """Test successful content analysis with AI"""
        content = (
            "This is a comprehensive guide about Python programming for beginners."
        )
        metadata = {"title": "Python Guide", "word_count": 100}

        # Mock AI response
        mock_analysis = {
            "topics": ["Python", "Programming", "Beginners"],
            "difficulty_level": "beginner",
            "key_concepts": ["Variables", "Functions", "Classes"],
            "estimated_study_time": 30,
            "language": "en",
            "content_classification": "educational",
        }

        mock_response = Mock()
        mock_response.content = json.dumps(mock_analysis)

        # Mock Ollama service
        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(return_value=mock_response)

        with patch.object(processor, "settings", Mock()):
            # Patch ai_router to return mock Ollama service
            with patch("app.services.content_processor.ai_router") as mock_router:
                mock_router.providers = {"ollama": mock_ollama}

                result = await processor._analyze_content(content, metadata)

                assert result["topics"] == ["Python", "Programming", "Beginners"]
                assert result["difficulty_level"] == "beginner"
                assert len(result["key_concepts"]) == 3
                assert result["detected_language"] == "en"

    @pytest.mark.asyncio
    async def test_analyze_content_ollama_unavailable(self, processor):
        """Test content analysis when Ollama is unavailable (fallback to router)"""
        content = "Test content"
        metadata = {"title": "Test"}

        mock_analysis = {
            "topics": ["General"],
            "difficulty_level": "intermediate",
            "key_concepts": [],
            "estimated_study_time": 20,
            "language": "en",
            "content_classification": "general",
        }

        mock_response = Mock()
        mock_response.content = json.dumps(mock_analysis)

        # Mock Ollama as unavailable
        mock_ollama = Mock()
        mock_ollama.is_available = False

        # Mock generate_ai_response fallback
        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            with patch(
                "app.services.content_processor.generate_ai_response",
                return_value=mock_response,
            ):
                result = await processor._analyze_content(content, metadata)

                assert "topics" in result
                assert "difficulty_level" in result

    @pytest.mark.asyncio
    async def test_analyze_content_error_fallback(self, processor):
        """Test content analysis with error returns default analysis"""
        content = "Test content with 200 words " * 200
        metadata = {"title": "Test"}

        # Mock Ollama to raise exception
        mock_ollama = Mock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(side_effect=Exception("AI Error"))

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            result = await processor._analyze_content(content, metadata)

            # Should return default analysis
            assert result["topics"] == ["General"]
            assert result["difficulty_level"] == "intermediate"
            assert result["detected_language"] == "en"
            assert result["estimated_study_time"] > 0

    @pytest.mark.asyncio
    async def test_analyze_content_invalid_json(self, processor):
        """Test content analysis with invalid JSON response"""
        content = "Test content"
        metadata = {"title": "Test"}

        mock_response = Mock()
        mock_response.content = "Not valid JSON"

        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(return_value=mock_response)

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            result = await processor._analyze_content(content, metadata)

            # Should return default analysis on JSON parse error
            assert result["topics"] == ["General"]
            assert result["difficulty_level"] == "intermediate"


# ============================================================================
# Test Learning Material Generation
# ============================================================================


class TestLearningMaterialGeneration:
    """Test learning material generation"""

    def test_estimate_material_time_summary(self, processor):
        """Test time estimation for summary"""
        time = processor._estimate_material_time(
            LearningMaterialType.SUMMARY, {"text": "summary"}
        )
        assert time == 5

    def test_estimate_material_time_flashcards(self, processor):
        """Test time estimation for flashcards"""
        content = {"flashcards": [{"front": "Q1", "back": "A1"}] * 10}
        time = processor._estimate_material_time(
            LearningMaterialType.FLASHCARDS, content
        )
        assert time == 5  # 10 cards * 0.5 min

    def test_estimate_material_time_quiz(self, processor):
        """Test time estimation for quiz"""
        content = {"questions": [{"q": "Q1"}] * 5}
        time = processor._estimate_material_time(LearningMaterialType.QUIZ, content)
        assert time == 7  # 5 questions * 1.5 min, rounded

    def test_estimate_material_time_key_concepts(self, processor):
        """Test time estimation for key concepts"""
        content = {"concepts": [{"term": "C1"}] * 8}
        time = processor._estimate_material_time(
            LearningMaterialType.KEY_CONCEPTS, content
        )
        assert time == 16  # 8 concepts * 2 min

    def test_estimate_material_time_notes(self, processor):
        """Test time estimation for notes"""
        time = processor._estimate_material_time(LearningMaterialType.NOTES, {})
        assert time == 10

    @pytest.mark.asyncio
    async def test_generate_single_material_summary(
        self, processor, sample_content_metadata
    ):
        """Test generating summary material"""
        content = "This is test content for learning."

        mock_summary = {
            "main_points": ["Point 1", "Point 2"],
            "key_takeaways": ["Takeaway 1"],
            "summary_text": "Summary here",
        }

        mock_response = Mock()
        mock_response.content = json.dumps(mock_summary)

        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(return_value=mock_response)

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            material = await processor._generate_single_material(
                content, sample_content_metadata, LearningMaterialType.SUMMARY
            )

            assert material is not None
            assert material.material_type == LearningMaterialType.SUMMARY
            assert "main_points" in material.content
            assert material.estimated_time == 5

    @pytest.mark.asyncio
    async def test_generate_single_material_flashcards(
        self, processor, sample_content_metadata
    ):
        """Test generating flashcards"""
        content = "Test content"

        mock_flashcards = {
            "flashcards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2", "back": "A2"},
            ]
        }

        mock_response = Mock()
        mock_response.content = json.dumps(mock_flashcards)

        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(return_value=mock_response)

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            material = await processor._generate_single_material(
                content, sample_content_metadata, LearningMaterialType.FLASHCARDS
            )

            assert material is not None
            assert material.material_type == LearningMaterialType.FLASHCARDS
            assert len(material.content["flashcards"]) == 2

    @pytest.mark.asyncio
    async def test_generate_single_material_unsupported_type(
        self, processor, sample_content_metadata
    ):
        """Test generating unsupported material type"""
        content = "Test"

        # Mind map and practice questions don't have prompts defined
        material = await processor._generate_single_material(
            content, sample_content_metadata, LearningMaterialType.MIND_MAP
        )

        assert material is None

    @pytest.mark.asyncio
    async def test_generate_single_material_error(
        self, processor, sample_content_metadata
    ):
        """Test material generation error handling"""
        content = "Test"

        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(side_effect=Exception("AI Error"))

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            material = await processor._generate_single_material(
                content, sample_content_metadata, LearningMaterialType.SUMMARY
            )

            assert material is None

    @pytest.mark.asyncio
    async def test_generate_learning_materials(
        self, processor, sample_content_metadata
    ):
        """Test generating multiple learning materials"""
        content = "Test content"

        mock_response = Mock()
        mock_response.content = json.dumps({"main_points": []})

        mock_ollama = AsyncMock()
        mock_ollama.is_available = True
        mock_ollama.generate_response = AsyncMock(return_value=mock_response)

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            materials = await processor._generate_learning_materials(
                content,
                sample_content_metadata,
                [LearningMaterialType.SUMMARY, LearningMaterialType.NOTES],
            )

            assert len(materials) <= 2  # May be less if generation fails


# ============================================================================
# Test Search and Library Management
# ============================================================================


class TestSearchAndLibrary:
    """Test search and library management"""

    @pytest.mark.asyncio
    async def test_get_processed_content_exists(
        self, processor, sample_content_metadata, sample_learning_material
    ):
        """Test getting processed content that exists"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="Raw",
            processed_content="Processed",
            learning_materials=[sample_learning_material],
            processing_stats={},
        )

        processor.content_library["test123"] = processed

        result = await processor.get_processed_content("test123")
        assert result is not None
        assert result.metadata.content_id == "test123"

    @pytest.mark.asyncio
    async def test_get_processed_content_not_exists(self, processor):
        """Test getting non-existent content"""
        result = await processor.get_processed_content("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_content_library(
        self, processor, sample_content_metadata, sample_learning_material
    ):
        """Test getting full content library"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="Raw",
            processed_content="Processed",
            learning_materials=[sample_learning_material],
            processing_stats={},
        )

        processor.content_library["test123"] = processed

        library = await processor.get_content_library()

        assert len(library) == 1
        assert library[0]["content_id"] == "test123"
        assert library[0]["title"] == "Test Content"
        assert library[0]["material_count"] == 1

    def test_matches_query_title_match(self, processor, sample_content_metadata):
        """Test query matching in title"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="content",
            processed_content="content",
            learning_materials=[],
            processing_stats={},
        )

        assert processor._matches_query("test", processed) is True
        assert processor._matches_query("nomatch", processed) is False

    def test_matches_query_topic_match(self, processor, sample_content_metadata):
        """Test query matching in topics"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="content",
            processed_content="content",
            learning_materials=[],
            processing_stats={},
        )

        assert processor._matches_query("python", processed) is True
        assert processor._matches_query("testing", processed) is True

    def test_matches_query_content_match(self, processor, sample_content_metadata):
        """Test query matching in content"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="content",
            processed_content="This contains search term",
            learning_materials=[],
            processing_stats={},
        )

        assert processor._matches_query("search", processed) is True

    def test_passes_filters_no_filters(self, processor, sample_content_metadata):
        """Test filtering with no filters (all pass)"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="",
            learning_materials=[],
            processing_stats={},
        )

        assert processor._passes_filters(processed, None) is True
        assert processor._passes_filters(processed, {}) is True

    def test_passes_filters_content_type(self, processor, sample_content_metadata):
        """Test filtering by content type"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="",
            learning_materials=[],
            processing_stats={},
        )

        assert (
            processor._passes_filters(processed, {"content_type": "youtube_video"})
            is True
        )
        assert (
            processor._passes_filters(processed, {"content_type": "pdf_document"})
            is False
        )

    def test_passes_filters_difficulty(self, processor, sample_content_metadata):
        """Test filtering by difficulty level"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="",
            learning_materials=[],
            processing_stats={},
        )

        assert (
            processor._passes_filters(processed, {"difficulty_level": "intermediate"})
            is True
        )
        assert (
            processor._passes_filters(processed, {"difficulty_level": "advanced"})
            is False
        )

    def test_passes_filters_language(self, processor, sample_content_metadata):
        """Test filtering by language"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="",
            learning_materials=[],
            processing_stats={},
        )

        assert processor._passes_filters(processed, {"language": "en"}) is True
        assert processor._passes_filters(processed, {"language": "es"}) is False

    def test_calculate_relevance(self, processor, sample_content_metadata):
        """Test relevance score calculation"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="This contains python and testing keywords",
            learning_materials=[],
            processing_stats={},
        )

        # Title match (highest score)
        score_title = processor._calculate_relevance("test", processed)
        assert score_title >= 1.0

        # Topic match
        score_topic = processor._calculate_relevance("python", processed)
        assert score_topic >= 0.5

        # Content match (lower score)
        score_content = processor._calculate_relevance("keywords", processed)
        assert score_content >= 0.2

    def test_get_content_snippet_query_found(self, processor):
        """Test getting content snippet with query found"""
        content = "This is the beginning. Here is the search term in the middle. And this is the end."

        snippet = processor._get_content_snippet("search", content, max_length=50)

        assert "search term" in snippet.lower()
        assert len(snippet) <= 60  # max_length + ellipsis

    def test_get_content_snippet_query_not_found(self, processor):
        """Test getting snippet when query not found"""
        content = "This is the content without the query term."

        snippet = processor._get_content_snippet("nomatch", content, max_length=20)

        # Should return beginning of content
        assert snippet.startswith("This is")
        assert "..." in snippet

    @pytest.mark.asyncio
    async def test_search_content_basic(
        self, processor, sample_content_metadata, sample_learning_material
    ):
        """Test basic content search"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="Test content",
            learning_materials=[],
            processing_stats={},
        )

        processor.content_library["test123"] = processed

        results = await processor.search_content("test")

        assert len(results) == 1
        assert results[0]["content_id"] == "test123"
        assert "relevance_score" in results[0]
        assert "snippet" in results[0]

    @pytest.mark.asyncio
    async def test_search_content_no_match(self, processor, sample_content_metadata):
        """Test search with query that doesn't match any content

        This tests line 1057 in content_processor.py where content that
        doesn't match the query is skipped.
        """
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="Test content about Python programming",
            learning_materials=[],
            processing_stats={},
        )

        processor.content_library["test123"] = processed

        # Search for something that doesn't match
        results = await processor.search_content("javascript")

        # Should return empty list since query doesn't match
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_content_with_filters(
        self, processor, sample_content_metadata
    ):
        """Test content search with filters"""
        processed = ProcessedContent(
            metadata=sample_content_metadata,
            raw_content="",
            processed_content="Test content",
            learning_materials=[],
            processing_stats={},
        )

        processor.content_library["test123"] = processed

        # Should match
        results = await processor.search_content(
            "test", filters={"content_type": "youtube_video"}
        )
        assert len(results) == 1

        # Should not match
        results = await processor.search_content(
            "test", filters={"content_type": "pdf_document"}
        )
        assert len(results) == 0


# ============================================================================
# Test Content Processing Workflow
# ============================================================================


class TestContentProcessingWorkflow:
    """Test main content processing workflow"""

    @pytest.mark.asyncio
    async def test_process_content_returns_content_id(self, processor):
        """Test process_content returns content ID immediately"""
        captured_coro = []

        def capture_create_task(coro):
            captured_coro.append(coro)
            return Mock()

        with patch(
            "app.services.content_processor.asyncio.create_task",
            side_effect=capture_create_task,
        ):
            content_id = await processor.process_content(
                "https://www.youtube.com/watch?v=test", material_types=[]
            )

            assert content_id is not None
            assert len(content_id) == 12
            assert content_id in processor.processing_progress

            # Close coroutine to prevent RuntimeWarning
            if captured_coro:
                captured_coro[0].close()

    @pytest.mark.asyncio
    async def test_process_content_initializes_progress(self, processor):
        """Test process_content initializes progress tracking"""
        captured_coro = []

        def capture_create_task(coro):
            captured_coro.append(coro)
            return Mock()

        with patch(
            "app.services.content_processor.asyncio.create_task",
            side_effect=capture_create_task,
        ):
            content_id = await processor.process_content("test_source")

            progress = processor.processing_progress[content_id]
            assert progress.status == ProcessingStatus.QUEUED
            assert progress.progress_percentage == 0

            # Close coroutine to prevent RuntimeWarning
            if captured_coro:
                captured_coro[0].close()

    @pytest.mark.asyncio
    async def test_process_content_default_material_types(self, processor):
        """Test process_content uses default material types"""
        # Capture the coroutine to close it properly and avoid warning
        captured_coro = []

        def capture_create_task(coro):
            captured_coro.append(coro)
            return Mock()

        with patch(
            "app.services.content_processor.asyncio.create_task",
            side_effect=capture_create_task,
        ):
            content_id = await processor.process_content("test_source")

            # Verify create_task was called
            assert len(captured_coro) == 1
            assert content_id is not None

            # Close the coroutine to prevent RuntimeWarning
            captured_coro[0].close()


# ============================================================================
# Additional Edge Case Tests for 90%+ Coverage
# ============================================================================


class TestContentTypeEdgeCases:
    """Test edge cases for content type detection"""

    def test_detect_audio_file(self, processor):
        """Test detection of audio file types"""
        assert (
            processor._detect_content_type("", file_path=Path("test.mp3"))
            == ContentType.AUDIO_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.wav"))
            == ContentType.AUDIO_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.m4a"))
            == ContentType.AUDIO_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.flac"))
            == ContentType.AUDIO_FILE
        )

    def test_detect_image_file(self, processor):
        """Test detection of image file types"""
        assert (
            processor._detect_content_type("", file_path=Path("test.jpg"))
            == ContentType.IMAGE_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.jpeg"))
            == ContentType.IMAGE_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.png"))
            == ContentType.IMAGE_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.gif"))
            == ContentType.IMAGE_FILE
        )
        assert (
            processor._detect_content_type("", file_path=Path("test.bmp"))
            == ContentType.IMAGE_FILE
        )


class TestYouTubeTranscriptFallbacks:
    """Test YouTube transcript fallback scenarios"""

    @pytest.mark.asyncio
    async def test_extract_youtube_content_generated_transcript(self, processor):
        """Test fallback to generated transcript when manual not available"""
        mock_info = {
            "id": "test123",
            "title": "Test Video",
            "description": "Test description",
            "duration": 120,
            "uploader": "Test Channel",
        }

        # Mock transcript list with only generated transcripts
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = [{"text": "Generated transcript text"}]

        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.side_effect = Exception(
            "No manual transcript"
        )
        mock_transcript_list.find_generated_transcripts.return_value = [mock_transcript]

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = mock_info
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with patch(
                "app.services.content_processor.YouTubeTranscriptApi"
            ) as mock_api_class:
                mock_api_instance = Mock()
                mock_api_instance.list.return_value = mock_transcript_list
                mock_api_class.return_value = mock_api_instance

                with patch(
                    "app.services.content_processor.TextFormatter"
                ) as mock_formatter:
                    mock_formatter.return_value.format_transcript.return_value = (
                        "Generated transcript text"
                    )

                    result = await processor._extract_youtube_content(
                        "https://youtube.com/watch?v=test123"
                    )

                    assert result["title"] == "Test Video"
                    assert "Generated transcript text" in result["content"]

    @pytest.mark.asyncio
    async def test_extract_youtube_content_no_transcript_at_all(self, processor):
        """Test fallback to description when no transcript available"""
        mock_info = {
            "id": "test123",
            "title": "Test Video",
            "description": "Test description fallback",
            "duration": 120,
            "uploader": "Test Channel",
        }

        # Mock transcript list with no transcripts available
        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.side_effect = Exception(
            "No manual transcript"
        )
        mock_transcript_list.find_generated_transcripts.return_value = []

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = mock_info
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with patch(
                "app.services.content_processor.YouTubeTranscriptApi"
            ) as mock_api_class:
                mock_api_instance = Mock()
                mock_api_instance.list.return_value = mock_transcript_list
                mock_api_class.return_value = mock_api_instance

                result = await processor._extract_youtube_content(
                    "https://youtube.com/watch?v=test123"
                )

                assert result["title"] == "Test Video"
                assert result["content"] == "Test description fallback"


class TestWebContentExtractionSuccess:
    """Test successful web content extraction"""

    @pytest.mark.asyncio
    async def test_extract_web_content_success(self, processor):
        """Test successful web content extraction (placeholder implementation)"""
        # Note: Web content extraction is not yet fully implemented
        # This test verifies the placeholder functionality works
        with patch(
            "app.services.content_processor.aiohttp.ClientSession"
        ) as mock_client:
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="<html>Test HTML</html>")

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = Mock()
            mock_session.get = Mock(return_value=mock_get)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_client.return_value = mock_session

            result = await processor._extract_web_content("https://example.com/article")

            assert "example.com" in result["title"]
            assert "not yet implemented" in result["content"]


class TestMaterialGenerationEdgeCases:
    """Test edge cases in material generation"""

    @pytest.mark.asyncio
    async def test_generate_learning_materials_with_exception(self, processor):
        """Test material generation continues on exception"""
        metadata = ContentMetadata(
            content_id="test123",
            title="Test",
            content_type=ContentType.TEXT_FILE,
            source_url=None,
            duration=None,
            author=None,
            language="en",
            word_count=100,
            difficulty_level="intermediate",
            topics=["test"],
            created_at=datetime.now(),
        )

        material_types = [
            LearningMaterialType.SUMMARY,
            LearningMaterialType.FLASHCARDS,
        ]

        # Mock to succeed for first, fail for second
        with patch.object(processor, "_generate_single_material") as mock_generate:
            mock_material = LearningMaterial(
                material_id="mat1",
                content_id="test123",
                material_type=LearningMaterialType.SUMMARY,
                title="Test Summary",
                content={"summary": "Test"},
                difficulty_level="intermediate",
                estimated_time=5,
                tags=["test"],
                created_at=datetime.now(),
            )

            # First call succeeds, second raises exception
            mock_generate.side_effect = [mock_material, Exception("Generation failed")]

            result = await processor._generate_learning_materials(
                "Test content", metadata, material_types
            )

            # Should have 1 material (first one succeeded)
            assert len(result) == 1
            assert result[0].material_type == LearningMaterialType.SUMMARY

    @pytest.mark.asyncio
    async def test_generate_single_material_router_fallback(self, processor):
        """Test fallback to AI router when Ollama unavailable"""
        metadata = ContentMetadata(
            content_id="test123",
            title="Test",
            content_type=ContentType.TEXT_FILE,
            source_url=None,
            duration=None,
            author=None,
            language="en",
            word_count=100,
            difficulty_level="intermediate",
            topics=["test"],
            created_at=datetime.now(),
        )

        mock_summary = {"summary": "Test summary", "key_points": ["point1"]}

        # Mock AI router response
        mock_response = Mock()
        mock_response.content = json.dumps(mock_summary)

        # Mock Ollama as unavailable
        mock_ollama = AsyncMock()
        mock_ollama.is_available = False

        with patch("app.services.content_processor.ai_router") as mock_router:
            mock_router.providers = {"ollama": mock_ollama}

            with patch(
                "app.services.content_processor.generate_ai_response"
            ) as mock_generate:
                mock_generate.return_value = mock_response

                result = await processor._generate_single_material(
                    "Test content",
                    metadata,
                    LearningMaterialType.SUMMARY,
                )

                assert result is not None
                assert result.material_type == LearningMaterialType.SUMMARY
                mock_generate.assert_called_once()


class TestProcessContentExceptionHandling:
    """Test exception handling in process_content"""

    @pytest.mark.asyncio
    async def test_process_content_initialization_exception(self, processor):
        """Test exception during process_content initialization"""

        # Mock asyncio.create_task to raise exception
        with patch(
            "asyncio.create_task", side_effect=Exception("Task creation failed")
        ):
            with pytest.raises(Exception, match="Task creation failed"):
                await processor.process_content(
                    source="https://invalid.url",
                    material_types=[LearningMaterialType.SUMMARY],
                )


class TestAsyncProcessingWorkflow:
    """Test the full async processing workflow"""

    @pytest.mark.asyncio
    async def test_process_content_async_youtube_workflow(self, processor):
        """Test complete async workflow for YouTube content"""
        content_id = "test_content_123"
        source = "https://youtube.com/watch?v=test123"

        # Mock YouTube extraction
        mock_youtube_data = {
            "title": "Test Video",
            "content": "Test transcript content",
            "duration": 120,
            "word_count": 50,
            "author": "Test Channel",
        }

        # Mock AI analysis
        mock_analysis = {
            "difficulty_level": "intermediate",
            "topics": ["testing", "python"],
            "detected_language": "en",
        }

        # Mock learning material
        mock_material = LearningMaterial(
            material_id="mat1",
            content_id=content_id,
            material_type=LearningMaterialType.SUMMARY,
            title="Test Summary",
            content={"summary": "Test"},
            difficulty_level="intermediate",
            estimated_time=5,
            tags=["testing", "python"],
            created_at=datetime.now(),
        )

        with patch.object(
            processor,
            "_extract_youtube_content",
            new=AsyncMock(return_value=mock_youtube_data),
        ):
            with patch.object(
                processor, "_analyze_content", new=AsyncMock(return_value=mock_analysis)
            ):
                with patch.object(
                    processor,
                    "_generate_learning_materials",
                    new=AsyncMock(return_value=[mock_material]),
                ):
                    await processor._process_content_async(
                        content_id=content_id,
                        source=source,
                        file_path=None,
                        material_types=[LearningMaterialType.SUMMARY],
                        language="en",
                    )

                    # Verify content was stored
                    stored = processor.content_library.get(content_id)
                    assert stored is not None
                    assert stored.metadata.title == "Test Video"
                    assert stored.metadata.difficulty_level == "intermediate"
                    assert len(stored.learning_materials) == 1

                    # Verify progress tracking
                    progress = await processor.get_processing_progress(content_id)
                    assert progress.status == ProcessingStatus.COMPLETED
                    assert progress.progress_percentage == 100

    @pytest.mark.asyncio
    async def test_process_content_async_pdf_workflow(self, processor):
        """Test complete async workflow for PDF content"""
        content_id = "test_pdf_123"

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            file_path = Path(tmp.name)
            tmp.write(b"PDF content")

        try:
            mock_pdf_data = {
                "title": "Test PDF",
                "content": "Test PDF content",
                "word_count": 100,
                "author": "Test Author",
            }

            mock_analysis = {
                "difficulty_level": "beginner",
                "topics": ["documentation"],
                "detected_language": "en",
            }

            with patch.object(
                processor, "_extract_pdf_content", return_value=mock_pdf_data
            ):
                with patch.object(
                    processor, "_analyze_content", return_value=mock_analysis
                ):
                    with patch.object(
                        processor, "_generate_learning_materials", return_value=[]
                    ):
                        await processor._process_content_async(
                            content_id=content_id,
                            source="test.pdf",
                            file_path=file_path,
                            material_types=[],
                            language="en",
                        )

                        stored = processor.content_library.get(content_id)
                        assert stored is not None
                        assert stored.metadata.title == "Test PDF"
        finally:
            file_path.unlink()

    @pytest.mark.asyncio
    async def test_process_content_async_error_handling(self, processor):
        """Test error handling in async processing workflow"""
        content_id = "test_error_123"
        source = "https://youtube.com/watch?v=error"

        # Mock extraction to raise exception
        with patch.object(
            processor,
            "_extract_youtube_content",
            side_effect=Exception("Extraction failed"),
        ):
            await processor._process_content_async(
                content_id=content_id,
                source=source,
                file_path=None,
                material_types=[LearningMaterialType.SUMMARY],
                language="en",
            )

            # Verify error was tracked
            progress = await processor.get_processing_progress(content_id)
            assert progress.status == ProcessingStatus.FAILED
            assert "Extraction failed" in progress.error_message


class TestSearchHelperMethods:
    """Test search helper methods"""

    @pytest.mark.asyncio
    async def test_build_search_result(self, processor):
        """Test _build_search_result helper"""
        # First create and store a processed content
        metadata = ContentMetadata(
            content_id="search123",
            title="Searchable Content",
            content_type=ContentType.TEXT_FILE,
            source_url=None,
            duration=None,
            author=None,
            language="en",
            word_count=100,
            difficulty_level="intermediate",
            topics=["testing", "search"],
            created_at=datetime.now(),
        )

        processed = ProcessedContent(
            metadata=metadata,
            raw_content="This is searchable content for testing",
            processed_content="This is searchable content for testing",
            learning_materials=[],
            processing_stats={"processing_time": 1.0},
        )

        processor.content_library["search123"] = processed

        # Now search for it
        results = await processor.search_content(query="searchable")

        assert len(results) > 0
        result = results[0]
        assert result["content_id"] == "search123"
        assert result["title"] == "Searchable Content"
        assert result["relevance_score"] > 0
        assert "snippet" in result


class TestProgressTrackingEdgeCases:
    """Test edge cases in progress tracking"""

    @pytest.mark.asyncio
    async def test_update_progress_first_time_no_elapsed(self, processor):
        """Test progress update when no previous progress exists"""
        content_id = "new_content"

        processor._update_progress(
            content_id=content_id,
            status=ProcessingStatus.EXTRACTING,
            step="Starting",
            percentage=0,
        )

        progress = await processor.get_processing_progress(content_id)
        assert progress is not None
        assert progress.status == ProcessingStatus.EXTRACTING
        assert progress.estimated_remaining == 0


class TestContentTypeBranches:
    """Test coverage for different content type processing branches

    This tests lines 846-853 in content_processor.py where different
    extraction methods are called based on content type.
    """

    @pytest.mark.asyncio
    async def test_process_pdf_document_branch(self, processor):
        """Test PDF document processing branch (lines 846-847)"""
        content_id = "test_pdf_branch"

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            file_path = Path(tmp.name)
            tmp.write(b"PDF content")

        try:
            # Mock all the extraction and processing methods
            mock_pdf_data = {
                "title": "Test",
                "content": "PDF content",
                "word_count": 10,
            }
            mock_analysis = {
                "difficulty_level": "beginner",
                "topics": [],
                "detected_language": "en",
            }

            with patch.object(
                processor,
                "_extract_pdf_content",
                new=AsyncMock(return_value=mock_pdf_data),
            ):
                with patch.object(
                    processor,
                    "_analyze_content",
                    new=AsyncMock(return_value=mock_analysis),
                ):
                    with patch.object(
                        processor,
                        "_generate_learning_materials",
                        new=AsyncMock(return_value=[]),
                    ):
                        await processor._process_content_async(
                            content_id=content_id,
                            source="test.pdf",
                            file_path=file_path,
                            material_types=[],
                            language="en",
                        )

            # Verify processing completed
            assert content_id in processor.content_library
        finally:
            file_path.unlink()

    @pytest.mark.asyncio
    async def test_process_word_document_branch(self, processor):
        """Test Word document processing branch (lines 848-849)"""
        content_id = "test_docx_branch"

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            file_path = Path(tmp.name)
            tmp.write(b"DOCX content")

        try:
            mock_docx_data = {
                "title": "Test",
                "content": "DOCX content",
                "word_count": 10,
            }
            mock_analysis = {
                "difficulty_level": "beginner",
                "topics": [],
                "detected_language": "en",
            }

            with patch.object(
                processor,
                "_extract_docx_content",
                new=AsyncMock(return_value=mock_docx_data),
            ):
                with patch.object(
                    processor,
                    "_analyze_content",
                    new=AsyncMock(return_value=mock_analysis),
                ):
                    with patch.object(
                        processor,
                        "_generate_learning_materials",
                        new=AsyncMock(return_value=[]),
                    ):
                        await processor._process_content_async(
                            content_id=content_id,
                            source="test.docx",
                            file_path=file_path,
                            material_types=[],
                            language="en",
                        )

            assert content_id in processor.content_library
        finally:
            file_path.unlink()

    @pytest.mark.asyncio
    async def test_process_text_file_branch(self, processor):
        """Test text file processing branch (lines 850-851)"""
        content_id = "test_txt_branch"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            file_path = Path(tmp.name)
            tmp.write(b"Text content")

        try:
            mock_text_data = {
                "title": "Test",
                "content": "Text content",
                "word_count": 10,
            }
            mock_analysis = {
                "difficulty_level": "beginner",
                "topics": [],
                "detected_language": "en",
            }

            with patch.object(
                processor,
                "_extract_text_content",
                new=AsyncMock(return_value=mock_text_data),
            ):
                with patch.object(
                    processor,
                    "_analyze_content",
                    new=AsyncMock(return_value=mock_analysis),
                ):
                    with patch.object(
                        processor,
                        "_generate_learning_materials",
                        new=AsyncMock(return_value=[]),
                    ):
                        await processor._process_content_async(
                            content_id=content_id,
                            source="test.txt",
                            file_path=file_path,
                            material_types=[],
                            language="en",
                        )

            assert content_id in processor.content_library
        finally:
            file_path.unlink()

    @pytest.mark.asyncio
    async def test_process_web_article_branch(self, processor):
        """Test web article processing branch (lines 850-851)"""
        content_id = "test_web_branch"

        mock_web_data = {
            "title": "Test",
            "content": "Web content",
            "word_count": 10,
        }
        mock_analysis = {
            "difficulty_level": "beginner",
            "topics": [],
            "detected_language": "en",
        }

        with patch.object(
            processor, "_extract_web_content", new=AsyncMock(return_value=mock_web_data)
        ):
            with patch.object(
                processor, "_analyze_content", new=AsyncMock(return_value=mock_analysis)
            ):
                with patch.object(
                    processor,
                    "_generate_learning_materials",
                    new=AsyncMock(return_value=[]),
                ):
                    await processor._process_content_async(
                        content_id=content_id,
                        source="https://example.com/article",
                        file_path=None,
                        material_types=[],
                        language="en",
                    )

        assert content_id in processor.content_library

    @pytest.mark.asyncio
    async def test_process_unsupported_content_type(self, processor):
        """Test unsupported content type raises ValueError (lines 852-853)

        The ValueError is caught by the outer exception handler in _process_content_async,
        so we verify the processing fails rather than expecting the exception to propagate.
        """
        content_id = "test_unsupported"

        # Mock _detect_content_type to return UNKNOWN type
        with patch.object(
            processor, "_detect_content_type", return_value=ContentType.UNKNOWN
        ):
            await processor._process_content_async(
                content_id=content_id,
                source="unknown_source",
                file_path=None,
                material_types=[],
                language="en",
            )

            # Verify processing failed (content not in library or marked as failed)
            progress = await processor.get_processing_progress(content_id)
            assert progress is not None
            assert progress.status == ProcessingStatus.FAILED
