"""
Scenario Integration Service

Connects scenario completion to:
- Progress tracking (scenario_progress_history)
- Spaced repetition (vocabulary_items)
- Learning sessions
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.config import get_primary_db_session
from app.models.database import (
    LearningSession,
    ScenarioProgressHistory,
    VocabularyItem,
)
from app.services.scenario_models import ScenarioProgress

logger = logging.getLogger(__name__)


class ScenarioIntegrationService:
    """Service for integrating scenario completion with progress tracking and spaced repetition"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize with optional database session"""
        self.db = db_session or get_primary_db_session()
    
    async def save_scenario_progress(
        self,
        progress: ScenarioProgress,
        user_id: int,
        scenario_id: str,
        total_phases: int
    ) -> ScenarioProgressHistory:
        """
        Save completed scenario progress to database
        
        Args:
            progress: ScenarioProgress object with completion data
            user_id: User ID who completed the scenario
            scenario_id: ID of the completed scenario
            total_phases: Total number of phases in scenario
            
        Returns:
            ScenarioProgressHistory record
        """
        try:
            # Calculate duration
            duration_minutes = int((datetime.now() - progress.start_time).total_seconds() / 60)
            
            # Create history record
            history = ScenarioProgressHistory(
                user_id=user_id,
                scenario_id=scenario_id,
                progress_id=progress.progress_id,
                started_at=progress.start_time,
                completed_at=datetime.now(),
                duration_minutes=duration_minutes,
                phases_completed=progress.current_phase + 1,
                total_phases=total_phases,
                vocabulary_mastered=progress.vocabulary_mastered,
                objectives_completed=progress.objectives_completed,
                success_rate=progress.success_rate,
                completion_score=progress.success_rate * 100
            )
            
            self.db.add(history)
            self.db.commit()
            self.db.refresh(history)
            
            logger.info(
                f"Saved scenario progress: user={user_id}, scenario={scenario_id}, "
                f"duration={duration_minutes}min, vocab={len(progress.vocabulary_mastered)}"
            )
            
            return history
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save scenario progress: {e}")
            raise
    
    async def create_sr_items_from_scenario(
        self,
        vocabulary: List[str],
        scenario_id: str,
        user_id: int,
        language: str
    ) -> List[VocabularyItem]:
        """
        Create spaced repetition items for vocabulary from completed scenario
        
        Args:
            vocabulary: List of vocabulary words mastered
            scenario_id: ID of the scenario
            user_id: User ID
            language: Language code
            
        Returns:
            List of created VocabularyItem records
        """
        created_items = []
        
        try:
            for word in vocabulary:
                # Check if item already exists
                existing = self.db.query(VocabularyItem).filter(
                    VocabularyItem.user_id == user_id,
                    VocabularyItem.language == language,
                    VocabularyItem.word == word
                ).first()
                
                if existing:
                    # Update existing item - mark that it was reviewed in scenario
                    existing.times_studied += 1
                    existing.source_type = "scenario"  # Update source if it was manual
                    if not existing.source_document_id:
                        existing.source_document_id = scenario_id
                    logger.debug(f"Updated existing vocab item: {word}")
                    created_items.append(existing)
                else:
                    # Create new spaced repetition item
                    item = VocabularyItem(
                        user_id=user_id,
                        language=language,
                        word=word,
                        source_type="scenario",
                        source_document_id=scenario_id,
                        difficulty_level=1,
                        mastery_level=0.3,  # Initial mastery from scenario
                        times_studied=1,
                        times_correct=1,
                        next_review_date=datetime.now(),  # Available for immediate review
                        repetition_interval_days=1,
                        ease_factor=2.5
                    )
                    
                    self.db.add(item)
                    created_items.append(item)
                    logger.debug(f"Created new vocab item: {word}")
            
            self.db.commit()
            
            logger.info(
                f"Created/updated {len(created_items)} SR items from scenario {scenario_id} "
                f"for user {user_id}"
            )
            
            return created_items
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create SR items from scenario: {e}")
            raise
    
    async def record_learning_session(
        self,
        user_id: int,
        scenario_id: str,
        language: str,
        started_at: datetime,
        ended_at: datetime,
        vocabulary_count: int,
        objectives_count: int,
        success_rate: float
    ) -> LearningSession:
        """
        Record a learning session for the completed scenario
        
        Args:
            user_id: User ID
            scenario_id: ID of the scenario
            language: Language code
            started_at: Session start time
            ended_at: Session end time
            vocabulary_count: Number of vocabulary items learned
            objectives_count: Number of objectives completed
            success_rate: Success rate (0-1)
            
        Returns:
            LearningSession record
        """
        try:
            duration_seconds = int((ended_at - started_at).total_seconds())
            
            session = LearningSession(
                user_id=user_id,
                session_type="scenario",
                source_id=scenario_id,
                language=language,
                started_at=started_at,
                ended_at=ended_at,
                duration_seconds=duration_seconds,
                items_studied=vocabulary_count + objectives_count,
                items_correct=int((vocabulary_count + objectives_count) * success_rate),
                items_incorrect=int((vocabulary_count + objectives_count) * (1 - success_rate)),
                accuracy_rate=success_rate,
                session_metadata={
                    "scenario_id": scenario_id,
                    "vocabulary_learned": vocabulary_count,
                    "objectives_completed": objectives_count
                }
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(
                f"Recorded learning session: user={user_id}, scenario={scenario_id}, "
                f"duration={duration_seconds}s, accuracy={success_rate:.2%}"
            )
            
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to record learning session: {e}")
            raise
    
    async def integrate_scenario_completion(
        self,
        progress: ScenarioProgress,
        user_id: int,
        scenario_id: str,
        total_phases: int,
        language: str
    ) -> Dict[str, Any]:
        """
        Complete integration of scenario completion across all systems
        
        This is the main method that orchestrates all integration steps:
        1. Save progress history
        2. Create SR items for vocabulary
        3. Record learning session
        
        Args:
            progress: ScenarioProgress object
            user_id: User ID
            scenario_id: Scenario ID
            total_phases: Total phases in scenario
            language: Language code
            
        Returns:
            Dictionary with integration results
        """
        try:
            # 1. Save progress history
            history = await self.save_scenario_progress(
                progress, user_id, scenario_id, total_phases
            )
            
            # 2. Create SR items for vocabulary
            sr_items = await self.create_sr_items_from_scenario(
                progress.vocabulary_mastered,
                scenario_id,
                user_id,
                language
            )
            
            # 3. Record learning session
            session = await self.record_learning_session(
                user_id=user_id,
                scenario_id=scenario_id,
                language=language,
                started_at=progress.start_time,
                ended_at=datetime.now(),
                vocabulary_count=len(progress.vocabulary_mastered),
                objectives_count=len(progress.objectives_completed),
                success_rate=progress.success_rate
            )
            
            return {
                "progress_history_id": history.id,
                "sr_items_created": len(sr_items),
                "learning_session_id": session.id,
                "integration_complete": True
            }
            
        except Exception as e:
            logger.error(f"Scenario integration failed: {e}")
            raise


# Module-level convenience function
async def integrate_completed_scenario(
    progress: ScenarioProgress,
    user_id: int,
    scenario_id: str,
    total_phases: int,
    language: str
) -> Dict[str, Any]:
    """
    Convenience function to integrate scenario completion
    
    Creates a service instance and performs full integration
    """
    service = ScenarioIntegrationService()
    return await service.integrate_scenario_completion(
        progress, user_id, scenario_id, total_phases, language
    )
