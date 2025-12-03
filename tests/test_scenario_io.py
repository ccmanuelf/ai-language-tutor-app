"""
Comprehensive tests for scenario_io.py

Tests for ScenarioIO class covering all file I/O operations for scenarios.
Target: TRUE 100% coverage (47/47 statements, 16/16 branches)
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from app.services.scenario_io import ScenarioIO
from app.services.scenario_models import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioPhase,
)


class TestScenarioIOSaveSuccess:
    """Test successful save operations"""

    @pytest.mark.asyncio
    async def test_save_scenarios_creates_directory(self):
        """Test that save creates data/scenarios directory"""
        scenarios = {}

        with (
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("builtins.open", mock_open()) as mock_file,
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            # Verify directory creation
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @pytest.mark.asyncio
    async def test_save_scenarios_writes_json_file(self):
        """Test that save writes to scenarios.json"""
        scenarios = {}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()) as mock_file,
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            # Verify file opened for writing with UTF-8
            mock_file.assert_called_once()
            call_args = mock_file.call_args[0]
            call_kwargs = mock_file.call_args[1]
            assert "scenarios.json" in str(call_args[0])
            assert call_kwargs["encoding"] == "utf-8"

    @pytest.mark.asyncio
    async def test_save_scenarios_serializes_minimal_scenario(self):
        """Test serialization of scenario with minimal attributes"""
        # Create minimal scenario
        phase = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test phase",
            expected_duration_minutes=5,
            key_vocabulary=["hello"],
            essential_phrases=["How are you?"],
            learning_objectives=["Greet"],
            cultural_notes="Notes",
            success_criteria=["Done"],
        )

        scenario = ConversationScenario(
            scenario_id="test_001",
            name="Test Scenario",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="A test scenario",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Hotel lobby",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=["hello", "goodbye"],
            cultural_context={"country": "France"},
        )

        scenarios = {"test_001": scenario}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            # Verify json.dump was called
            assert mock_dump.call_count == 1
            dumped_data = mock_dump.call_args[0][0]

            # Verify scenario structure
            assert "test_001" in dumped_data
            scenario_dict = dumped_data["test_001"]
            assert scenario_dict["scenario_id"] == "test_001"
            assert scenario_dict["name"] == "Test Scenario"
            assert scenario_dict["category"] == "travel"
            assert scenario_dict["difficulty"] == "beginner"
            assert scenario_dict["user_role"] == "tourist"
            assert scenario_dict["ai_role"] == "service_provider"

    @pytest.mark.asyncio
    async def test_save_scenarios_serializes_phases(self):
        """Test that phases are correctly serialized"""
        phase = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test phase",
            expected_duration_minutes=5,
            key_vocabulary=["vocab1", "vocab2"],
            essential_phrases=["phrase1"],
            learning_objectives=["obj1"],
            cultural_notes="Cultural info",
            success_criteria=["criteria1"],
        )

        scenario = ConversationScenario(
            scenario_id="test_001",
            name="Test",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.LOCAL,
            setting="Test",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=[],
            cultural_context={},
        )

        scenarios = {"test_001": scenario}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            dumped_data = mock_dump.call_args[0][0]
            phases_data = dumped_data["test_001"]["phases"]

            assert len(phases_data) == 1
            phase_dict = phases_data[0]
            assert phase_dict["phase_id"] == "phase1"
            assert phase_dict["name"] == "Phase 1"
            assert phase_dict["description"] == "Test phase"
            assert phase_dict["expected_duration_minutes"] == 5
            assert phase_dict["key_vocabulary"] == ["vocab1", "vocab2"]
            assert phase_dict["essential_phrases"] == ["phrase1"]
            assert phase_dict["learning_objectives"] == ["obj1"]
            assert phase_dict["cultural_notes"] == "Cultural info"
            assert phase_dict["success_criteria"] == ["criteria1"]

    @pytest.mark.asyncio
    async def test_save_scenarios_handles_optional_attributes(self):
        """Test that optional scenario attributes are handled with getattr"""
        phase = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=[],
            essential_phrases=[],
            learning_objectives=[],
            cultural_notes=None,
            success_criteria=[],
        )

        scenario = ConversationScenario(
            scenario_id="test_001",
            name="Test",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Test",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=[],
            cultural_context={},
        )

        # Add optional attributes
        scenario.prerequisites = ["prereq1"]
        scenario.learning_outcomes = ["outcome1"]
        scenario.vocabulary_focus = ["vocab1"]
        scenario.cultural_context = "Context info"
        scenario.is_active = False
        scenario.created_at = datetime(2024, 1, 1, 12, 0, 0)
        scenario.updated_at = datetime(2024, 1, 2, 14, 30, 0)

        scenarios = {"test_001": scenario}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            dumped_data = mock_dump.call_args[0][0]
            scenario_dict = dumped_data["test_001"]

            # Verify optional attributes
            assert scenario_dict["prerequisites"] == ["prereq1"]
            assert scenario_dict["learning_outcomes"] == ["outcome1"]
            assert scenario_dict["vocabulary_focus"] == ["vocab1"]
            assert scenario_dict["cultural_context"] == "Context info"
            assert scenario_dict["is_active"] is False
            assert scenario_dict["created_at"] == "2024-01-01T12:00:00"
            assert scenario_dict["updated_at"] == "2024-01-02T14:30:00"

    @pytest.mark.asyncio
    async def test_save_scenarios_defaults_optional_attributes(self):
        """Test that missing optional attributes get defaults"""
        phase = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=[],
            essential_phrases=[],
            learning_objectives=[],
            cultural_notes=None,
            success_criteria=[],
        )

        scenario = ConversationScenario(
            scenario_id="test_001",
            name="Test",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test",
            user_role=ConversationRole.FRIEND,
            ai_role=ConversationRole.FRIEND,
            setting="Test",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=[],
            cultural_context={},
        )

        # Don't set optional attributes - they should get defaults
        scenarios = {"test_001": scenario}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            dumped_data = mock_dump.call_args[0][0]
            scenario_dict = dumped_data["test_001"]

            # Verify defaults
            assert scenario_dict["prerequisites"] == []
            assert scenario_dict["learning_outcomes"] == []
            assert scenario_dict["vocabulary_focus"] == []
            assert scenario_dict["cultural_context"] == {}
            assert scenario_dict["is_active"] is True
            # Timestamps should be generated
            assert "created_at" in scenario_dict
            assert "updated_at" in scenario_dict

    @pytest.mark.asyncio
    async def test_save_scenarios_handles_none_created_at(self):
        """Test that None created_at gets current datetime"""
        phase = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=[],
            essential_phrases=[],
            learning_objectives=[],
            cultural_notes=None,
            success_criteria=[],
        )

        scenario = ConversationScenario(
            scenario_id="test_001",
            name="Test",
            category=ScenarioCategory.BUSINESS,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test",
            user_role=ConversationRole.COLLEAGUE,
            ai_role=ConversationRole.COLLEAGUE,
            setting="Test",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=[],
            cultural_context={},
        )

        # Set created_at to None explicitly
        scenario.created_at = None
        scenario.updated_at = None

        scenarios = {"test_001": scenario}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            dumped_data = mock_dump.call_args[0][0]
            scenario_dict = dumped_data["test_001"]

            # Verify timestamps were generated
            assert "created_at" in scenario_dict
            assert "updated_at" in scenario_dict
            # Should be valid ISO format
            datetime.fromisoformat(scenario_dict["created_at"])
            datetime.fromisoformat(scenario_dict["updated_at"])

    @pytest.mark.asyncio
    async def test_save_scenarios_json_formatting(self):
        """Test that JSON is formatted with proper settings"""
        scenarios = {}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            # Verify json.dump parameters
            call_kwargs = mock_dump.call_args[1]
            assert call_kwargs["indent"] == 2
            assert call_kwargs["ensure_ascii"] is False

    @pytest.mark.asyncio
    async def test_save_scenarios_multiple_scenarios(self):
        """Test saving multiple scenarios"""
        phase1 = ScenarioPhase(
            phase_id="phase1",
            name="Phase 1",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=[],
            essential_phrases=[],
            learning_objectives=[],
            cultural_notes=None,
            success_criteria=[],
        )

        scenario1 = ConversationScenario(
            scenario_id="test_001",
            name="Scenario 1",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test 1",
            user_role=ConversationRole.STUDENT,
            ai_role=ConversationRole.TEACHER,
            setting="Hotel",
            duration_minutes=15,
            phases=[phase1],
            vocabulary_focus=[],
            cultural_context={},
        )

        scenario2 = ConversationScenario(
            scenario_id="test_002",
            name="Scenario 2",
            category=ScenarioCategory.BUSINESS,
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            description="Test 2",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Office",
            duration_minutes=30,
            phases=[phase1],
            vocabulary_focus=[],
            cultural_context={},
        )

        scenarios = {"test_001": scenario1, "test_002": scenario2}

        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", mock_open()),
            patch("json.dump") as mock_dump,
        ):
            await ScenarioIO.save_scenarios_to_file(scenarios)

            dumped_data = mock_dump.call_args[0][0]

            assert len(dumped_data) == 2
            assert "test_001" in dumped_data
            assert "test_002" in dumped_data


class TestScenarioIOSaveErrors:
    """Test error handling in save operations"""

    @pytest.mark.asyncio
    async def test_save_scenarios_handles_exception(self):
        """Test that exceptions during save are caught and logged"""
        scenarios = {}

        with (
            patch("pathlib.Path.mkdir", side_effect=Exception("Disk error")),
            patch("app.services.scenario_io.logger") as mock_logger,
        ):
            # Should not raise, just log
            await ScenarioIO.save_scenarios_to_file(scenarios)

            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_msg = mock_logger.error.call_args[0][0]
            assert "Error saving scenarios" in error_msg
            assert "Disk error" in error_msg


class TestScenarioIOLoadSuccess:
    """Test successful load operations"""

    @pytest.mark.asyncio
    async def test_load_scenarios_file_not_exists(self):
        """Test that load returns empty dict when file doesn't exist"""
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("app.services.scenario_io.logger") as mock_logger,
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            assert result == {}
            # Verify info log
            mock_logger.info.assert_called_once()
            assert "No saved scenarios file found" in mock_logger.info.call_args[0][0]

    @pytest.mark.asyncio
    async def test_load_scenarios_reads_file(self):
        """Test that load reads from scenarios.json"""
        json_data = json.dumps({})

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json_data)) as mock_file,
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            # Verify file was opened for reading with UTF-8
            mock_file.assert_called_once()
            call_args = mock_file.call_args[0]
            call_kwargs = mock_file.call_args[1]
            assert "scenarios.json" in str(call_args[0])
            assert call_kwargs["encoding"] == "utf-8"

    @pytest.mark.asyncio
    async def test_load_scenarios_deserializes_scenario(self):
        """Test deserialization of complete scenario"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Test Scenario",
                "category": "travel",
                "difficulty": "beginner",
                "description": "A test",
                "user_role": "tourist",
                "ai_role": "local",
                "setting": "Hotel",
                "duration_minutes": 15,
                "phases": [
                    {
                        "phase_id": "phase1",
                        "name": "Phase 1",
                        "description": "Test phase",
                        "expected_duration_minutes": 5,
                        "key_vocabulary": ["hello"],
                        "essential_phrases": ["How are you?"],
                        "learning_objectives": ["Greet"],
                        "cultural_notes": "Notes",
                        "success_criteria": ["Done"],
                    }
                ],
                "prerequisites": ["prereq1"],
                "learning_outcomes": ["outcome1"],
                "vocabulary_focus": ["vocab1"],
                "cultural_context": "Context",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T14:00:00",
            }
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            assert len(result) == 1
            assert "test_001" in result

            scenario = result["test_001"]
            assert scenario.scenario_id == "test_001"
            assert scenario.name == "Test Scenario"
            assert scenario.category == ScenarioCategory.TRAVEL
            assert scenario.difficulty == ScenarioDifficulty.BEGINNER
            assert scenario.description == "A test"
            assert scenario.user_role == ConversationRole.TOURIST
            assert scenario.ai_role == ConversationRole.LOCAL
            assert scenario.setting == "Hotel"
            assert scenario.duration_minutes == 15

    @pytest.mark.asyncio
    async def test_load_scenarios_deserializes_phases(self):
        """Test that phases are correctly deserialized"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Test",
                "category": "travel",
                "difficulty": "beginner",
                "description": "Test",
                "user_role": "customer",
                "ai_role": "service_provider",
                "setting": "Test",
                "duration_minutes": 15,
                "phases": [
                    {
                        "phase_id": "phase1",
                        "name": "Phase 1",
                        "description": "Test phase",
                        "expected_duration_minutes": 5,
                        "key_vocabulary": ["vocab1", "vocab2"],
                        "essential_phrases": ["phrase1"],
                        "learning_objectives": ["obj1"],
                        "cultural_notes": "Cultural",
                        "success_criteria": ["criteria1"],
                    }
                ],
            }
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            scenario = result["test_001"]
            assert len(scenario.phases) == 1

            phase = scenario.phases[0]
            assert phase.phase_id == "phase1"
            assert phase.name == "Phase 1"
            assert phase.description == "Test phase"
            assert phase.expected_duration_minutes == 5
            assert phase.key_vocabulary == ["vocab1", "vocab2"]
            assert phase.essential_phrases == ["phrase1"]
            assert phase.learning_objectives == ["obj1"]
            assert phase.cultural_notes == "Cultural"
            assert phase.success_criteria == ["criteria1"]

    @pytest.mark.asyncio
    async def test_load_scenarios_handles_missing_phase_fields(self):
        """Test that missing phase fields get defaults"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Test",
                "category": "travel",
                "difficulty": "beginner",
                "description": "Test",
                "user_role": "friend",
                "ai_role": "friend",
                "setting": "Test",
                "duration_minutes": 15,
                "phases": [
                    {
                        "phase_id": "phase1",
                        "name": "Phase 1",
                        "description": "Test phase",
                        "expected_duration_minutes": 5,
                        # Missing optional fields
                    }
                ],
            }
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            phase = result["test_001"].phases[0]
            assert phase.key_vocabulary == []
            assert phase.essential_phrases == []
            assert phase.learning_objectives == []
            assert phase.cultural_notes is None
            assert phase.success_criteria == []

    @pytest.mark.asyncio
    async def test_load_scenarios_sets_optional_attributes(self):
        """Test that optional scenario attributes are set"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Test",
                "category": "travel",
                "difficulty": "beginner",
                "description": "Test",
                "user_role": "student",
                "ai_role": "teacher",
                "setting": "Test",
                "duration_minutes": 15,
                "phases": [],
                "prerequisites": ["prereq1"],
                "learning_outcomes": ["outcome1"],
                "vocabulary_focus": ["vocab1"],
                "cultural_context": "Context",
                "is_active": False,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T14:00:00",
            }
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            scenario = result["test_001"]
            assert scenario.is_active is False
            assert scenario.created_at == datetime(2024, 1, 1, 12, 0, 0)
            assert scenario.updated_at == datetime(2024, 1, 2, 14, 0, 0)

    @pytest.mark.asyncio
    async def test_load_scenarios_defaults_missing_attributes(self):
        """Test that missing optional attributes get defaults"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Test",
                "category": "travel",
                "difficulty": "beginner",
                "description": "Test",
                "user_role": "colleague",
                "ai_role": "colleague",
                "setting": "Test",
                "duration_minutes": 15,
                "phases": [],
                # Missing optional fields
            }
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            scenario = result["test_001"]
            assert scenario.prerequisites == []
            assert scenario.learning_outcomes == []
            assert scenario.vocabulary_focus == []
            assert scenario.cultural_context is None

    @pytest.mark.asyncio
    async def test_load_scenarios_multiple_scenarios(self):
        """Test loading multiple scenarios"""
        json_data = {
            "test_001": {
                "scenario_id": "test_001",
                "name": "Scenario 1",
                "category": "travel",
                "difficulty": "beginner",
                "description": "Test 1",
                "user_role": "tourist",
                "ai_role": "local",
                "setting": "Hotel",
                "duration_minutes": 15,
                "phases": [],
            },
            "test_002": {
                "scenario_id": "test_002",
                "name": "Scenario 2",
                "category": "business",
                "difficulty": "intermediate",
                "description": "Test 2",
                "user_role": "student",
                "ai_role": "teacher",
                "setting": "Office",
                "duration_minutes": 30,
                "phases": [],
            },
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(json_data))),
            patch("app.services.scenario_io.logger") as mock_logger,
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            assert len(result) == 2
            assert "test_001" in result
            assert "test_002" in result

            # Verify success log
            mock_logger.info.assert_called_once()
            assert "Loaded 2 scenarios" in mock_logger.info.call_args[0][0]


class TestScenarioIOLoadErrors:
    """Test error handling in load operations"""

    @pytest.mark.asyncio
    async def test_load_scenarios_handles_exception(self):
        """Test that exceptions during load are caught and logged"""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=Exception("Read error")),
            patch("app.services.scenario_io.logger") as mock_logger,
        ):
            result = await ScenarioIO.load_scenarios_from_file()

            # Should return empty dict
            assert result == {}

            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_msg = mock_logger.error.call_args[0][0]
            assert "Error loading scenarios" in error_msg
            assert "Read error" in error_msg
