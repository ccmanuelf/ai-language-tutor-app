"""
Language Configuration API - Fixed Database Pattern

This module provides RESTful API endpoints for managing language configurations,
voice models, and admin language settings in the AI Language Tutor App.

Task 3.1.3 - Language Configuration Panel
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import logging
from pathlib import Path

from app.database.config import get_db_session_context
from app.services.admin_auth import require_permission
from app.models.database import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/languages", tags=["Language Configuration"])


# Pydantic Models for API
class VoiceModelResponse(BaseModel):
    """Voice model information response"""

    id: int
    model_name: str
    language_code: str
    file_path: str
    config_path: str
    quality_level: str
    sample_rate: int
    file_size_mb: float
    is_active: bool
    is_default: bool
    created_at: datetime
    metadata: Dict[str, Any] = {}


class LanguageConfigResponse(BaseModel):
    """Language configuration response"""

    language_code: str
    language_name: str
    native_name: Optional[str]
    is_enabled_globally: bool
    default_voice_model: Optional[str]
    speech_recognition_enabled: bool
    text_to_speech_enabled: bool
    pronunciation_analysis_enabled: bool
    conversation_mode_enabled: bool
    tutor_mode_enabled: bool
    scenario_mode_enabled: bool
    realtime_analysis_enabled: bool
    difficulty_levels: List[str]
    voice_settings: Dict[str, Any]
    available_voice_models: List[VoiceModelResponse]


class LanguageConfigUpdate(BaseModel):
    """Language configuration update request"""

    is_enabled_globally: Optional[bool] = None
    default_voice_model: Optional[str] = None
    speech_recognition_enabled: Optional[bool] = None
    text_to_speech_enabled: Optional[bool] = None
    pronunciation_analysis_enabled: Optional[bool] = None
    conversation_mode_enabled: Optional[bool] = None
    tutor_mode_enabled: Optional[bool] = None
    scenario_mode_enabled: Optional[bool] = None
    realtime_analysis_enabled: Optional[bool] = None
    difficulty_levels: Optional[List[str]] = None
    voice_settings: Optional[Dict[str, Any]] = None


class VoiceModelUpdate(BaseModel):
    """Voice model update request"""

    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    quality_level: Optional[str] = None


class FeatureToggleResponse(BaseModel):
    """Feature toggle response"""

    id: int
    feature_name: str
    is_enabled: bool
    description: Optional[str]
    category: str
    requires_restart: bool
    min_role: str
    configuration: Dict[str, Any]


class FeatureToggleUpdate(BaseModel):
    """Feature toggle update request"""

    is_enabled: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None


# API Endpoints


@router.get("/", response_model=List[LanguageConfigResponse])
async def get_all_language_configurations(
    current_admin: User = Depends(require_permission("manage_languages")),
):
    """Get all language configurations with voice models"""
    try:
        with get_db_session_context() as session:
            # Get all languages with their configurations
            query = text("""
                SELECT
                    l.code as language_code,
                    l.name as language_name,
                    l.native_name,
                    COALESCE(alc.is_enabled_globally, 1) as is_enabled_globally,
                    alc.default_voice_model,
                    COALESCE(alc.speech_recognition_enabled, 1) as speech_recognition_enabled,
                    COALESCE(alc.text_to_speech_enabled, 1) as text_to_speech_enabled,
                    COALESCE(alc.pronunciation_analysis_enabled, 1) as pronunciation_analysis_enabled,
                    COALESCE(alc.conversation_mode_enabled, 1) as conversation_mode_enabled,
                    COALESCE(alc.tutor_mode_enabled, 1) as tutor_mode_enabled,
                    COALESCE(alc.scenario_mode_enabled, 1) as scenario_mode_enabled,
                    COALESCE(alc.realtime_analysis_enabled, 1) as realtime_analysis_enabled,
                    COALESCE(alc.difficulty_levels, '["beginner", "intermediate", "advanced"]') as difficulty_levels,
                    COALESCE(alc.voice_settings, '{}') as voice_settings
                FROM languages l
                LEFT JOIN admin_language_config alc ON l.code = alc.language_code
                WHERE l.is_active = 1
                ORDER BY l.name
            """)

            result = session.execute(query)
            languages = result.fetchall()

            # Get voice models for each language
            voice_models_query = text("""
                SELECT * FROM voice_models
                WHERE language_code = ? AND is_active = 1
                ORDER BY is_default DESC, quality_level, model_name
            """)

            language_configs = []
            for lang in languages:
                # Get voice models for this language
                voice_result = session.execute(
                    voice_models_query, (lang.language_code,)
                )
                voice_models = []

                for vm in voice_result.fetchall():
                    metadata = {}
                    try:
                        metadata = json.loads(vm.metadata) if vm.metadata else {}
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass

                    voice_models.append(
                        VoiceModelResponse(
                            id=vm.id,
                            model_name=vm.model_name,
                            language_code=vm.language_code,
                            file_path=vm.file_path,
                            config_path=vm.config_path or "",
                            quality_level=vm.quality_level,
                            sample_rate=vm.sample_rate,
                            file_size_mb=vm.file_size_mb,
                            is_active=bool(vm.is_active),
                            is_default=bool(vm.is_default),
                            created_at=vm.created_at,
                            metadata=metadata,
                        )
                    )

                # Parse JSON fields
                difficulty_levels = json.loads(lang.difficulty_levels)
                voice_settings = json.loads(lang.voice_settings)

                language_configs.append(
                    LanguageConfigResponse(
                        language_code=lang.language_code,
                        language_name=lang.language_name,
                        native_name=lang.native_name,
                        is_enabled_globally=bool(lang.is_enabled_globally),
                        default_voice_model=lang.default_voice_model,
                        speech_recognition_enabled=bool(
                            lang.speech_recognition_enabled
                        ),
                        text_to_speech_enabled=bool(lang.text_to_speech_enabled),
                        pronunciation_analysis_enabled=bool(
                            lang.pronunciation_analysis_enabled
                        ),
                        conversation_mode_enabled=bool(lang.conversation_mode_enabled),
                        tutor_mode_enabled=bool(lang.tutor_mode_enabled),
                        scenario_mode_enabled=bool(lang.scenario_mode_enabled),
                        realtime_analysis_enabled=bool(lang.realtime_analysis_enabled),
                        difficulty_levels=difficulty_levels,
                        voice_settings=voice_settings,
                        available_voice_models=voice_models,
                    )
                )

            return language_configs

    except Exception as e:
        logger.error(f"Failed to get language configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve language configurations: {str(e)}",
        )


@router.get("/feature-toggles/", response_model=List[FeatureToggleResponse])
async def get_feature_toggles(
    category: Optional[str] = None,
    current_admin: User = Depends(require_permission("manage_features")),
):
    """Get all feature toggles, optionally filtered by category"""
    try:
        with get_db_session_context() as session:
            if category:
                query = text("""
                    SELECT * FROM admin_feature_toggles
                    WHERE category = ?
                    ORDER BY category, feature_name
                """)
                result = session.execute(query, (category,))
            else:
                query = text("""
                    SELECT * FROM admin_feature_toggles
                    ORDER BY category, feature_name
                """)
                result = session.execute(query)

            feature_toggles = []
            for ft in result.fetchall():
                configuration = {}
                try:
                    configuration = (
                        json.loads(ft.configuration) if ft.configuration else {}
                    )
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass

                feature_toggles.append(
                    FeatureToggleResponse(
                        id=ft.id,
                        feature_name=ft.feature_name,
                        is_enabled=bool(ft.is_enabled),
                        description=ft.description,
                        category=ft.category,
                        requires_restart=bool(ft.requires_restart),
                        min_role=ft.min_role,
                        configuration=configuration,
                    )
                )

            return feature_toggles

    except Exception as e:
        logger.error(f"Failed to get feature toggles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feature toggles: {str(e)}",
        )


@router.put("/{language_code}", response_model=LanguageConfigResponse)
async def update_language_configuration(
    language_code: str,
    update_data: LanguageConfigUpdate,
    current_admin: User = Depends(require_permission("manage_languages")),
):
    """Update language configuration"""
    try:
        with get_db_session_context() as session:
            # Check if language exists
            lang_check = session.execute(
                text("SELECT code FROM languages WHERE code = ? AND is_active = 1"),
                (language_code,),
            )
            if not lang_check.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Language '{language_code}' not found",
                )

            # Check if config exists, create if not
            config_check = session.execute(
                text(
                    "SELECT language_code FROM admin_language_config WHERE language_code = ?"
                ),
                (language_code,),
            )

            update_fields = []
            update_values = []

            if update_data.is_enabled_globally is not None:
                update_fields.append("is_enabled_globally = ?")
                update_values.append(update_data.is_enabled_globally)

            if update_data.speech_recognition_enabled is not None:
                update_fields.append("speech_recognition_enabled = ?")
                update_values.append(update_data.speech_recognition_enabled)

            if update_data.text_to_speech_enabled is not None:
                update_fields.append("text_to_speech_enabled = ?")
                update_values.append(update_data.text_to_speech_enabled)

            # Add other update fields...

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")

                if config_check.fetchone():
                    # Update existing config
                    query = f"""
                        UPDATE admin_language_config
                        SET {", ".join(update_fields)}
                        WHERE language_code = ?
                    """
                    update_values.append(language_code)
                else:
                    # Insert new config
                    query = f"""
                        INSERT INTO admin_language_config
                        (language_code, {", ".join(field.split(" = ")[0] for field in update_fields)})
                        VALUES (?, {", ".join(["?" for _ in update_fields])})
                    """
                    update_values.insert(0, language_code)

                session.execute(text(query), update_values)
                session.commit()

            # Return updated configuration (simplified)
            return LanguageConfigResponse(
                language_code=language_code,
                language_name="Updated",
                native_name="Updated",
                is_enabled_globally=update_data.is_enabled_globally or True,
                default_voice_model=None,
                speech_recognition_enabled=update_data.speech_recognition_enabled
                or True,
                text_to_speech_enabled=update_data.text_to_speech_enabled or True,
                pronunciation_analysis_enabled=True,
                conversation_mode_enabled=True,
                tutor_mode_enabled=True,
                scenario_mode_enabled=True,
                realtime_analysis_enabled=True,
                difficulty_levels=["beginner", "intermediate", "advanced"],
                voice_settings={},
                available_voice_models=[],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update language configuration for {language_code}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update language configuration: {str(e)}",
        )


@router.post("/sync-voice-models")
async def sync_voice_models(
    current_admin: User = Depends(require_permission("manage_languages")),
):
    """Synchronize voice models with filesystem"""
    try:
        voices_dir = Path("app/data/piper_voices")
        if not voices_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Piper voices directory not found",
            )

        with get_db_session_context() as session:
            # Get existing models
            existing_models = {}
            result = session.execute(
                text("SELECT model_name, file_path FROM voice_models")
            )
            for row in result.fetchall():
                existing_models[row.model_name] = row.file_path

            # Language mapping
            language_mapping = {
                "en_US": "en",
                "es_AR": "es",
                "es_ES": "es",
                "es_MX": "es",
                "fr_FR": "fr",
                "de_DE": "de",
                "it_IT": "it",
                "pt_BR": "pt",
                "zh_CN": "zh",
            }

            new_models = []

            for onnx_file in voices_dir.glob("*.onnx"):
                if onnx_file.stat().st_size < 1000:  # Skip corrupt files
                    continue

                model_name = onnx_file.stem

                if model_name not in existing_models:
                    # Add new model
                    config_file = onnx_file.with_suffix(".onnx.json")
                    lang_prefix = model_name.split("-")[0]
                    language_code = language_mapping.get(lang_prefix, "en")

                    quality_level = "medium"
                    if "high" in model_name:
                        quality_level = "high"
                    elif "low" in model_name:
                        quality_level = "low"

                    file_size_mb = round(onnx_file.stat().st_size / (1024 * 1024), 2)

                    session.execute(
                        text("""
                        INSERT INTO voice_models
                        (model_name, language_code, file_path, config_path, quality_level,
                         sample_rate, file_size_mb, is_active, is_default, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """),
                        (
                            model_name,
                            language_code,
                            str(onnx_file),
                            str(config_file) if config_file.exists() else "",
                            quality_level,
                            22050,
                            file_size_mb,
                            True,
                            False,
                            "{}",
                        ),
                    )

                    new_models.append(model_name)

            session.commit()

            return {
                "message": "Voice models synchronized successfully",
                "new_models": len(new_models),
                "new_model_names": new_models,
                "total_models": len(existing_models) + len(new_models),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync voice models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synchronize voice models: {str(e)}",
        )
