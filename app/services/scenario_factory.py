"""
Scenario Factory for AI Language Tutor App

This module provides the ScenarioFactory class for creating and managing
scenario templates from configuration files or default templates.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from .scenario_models import (
    ScenarioCategory,
    UniversalScenarioTemplate,
)

logger = logging.getLogger(__name__)


class ScenarioFactory:
    """Factory for creating scenarios from templates and configurations"""

    def __init__(self, template_directory: str = "scenario_templates"):
        self.template_directory = Path(template_directory)
        self.universal_templates: Dict[str, UniversalScenarioTemplate] = {}
        self.content_cache: Dict[str, Dict[str, Any]] = {}
        self._load_universal_templates()

    def _load_universal_templates(self):
        """Load universal scenario templates from configuration files"""
        templates_path = Path(__file__).parent.parent / "config" / "scenarios"

        if not templates_path.exists():
            logger.warning(f"Scenario templates directory not found: {templates_path}")
            self._create_default_templates()
            return

        template_files = list(templates_path.glob("*.json"))
        if not template_files:
            logger.info("No template JSON files found, creating defaults")
            self._create_default_templates()
            return

        for template_file in template_files:
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template = self._create_universal_template(template_data)
                    self.universal_templates[template.template_id] = template
                    logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")

    def _create_universal_template(
        self, data: Dict[str, Any]
    ) -> UniversalScenarioTemplate:
        """Create UniversalScenarioTemplate from JSON data"""
        return UniversalScenarioTemplate(
            template_id=data["template_id"],
            name=data["name"],
            category=ScenarioCategory(data["category"]),
            tier=data["tier"],
            base_vocabulary=data["base_vocabulary"],
            essential_phrases=data["essential_phrases"],
            cultural_context=data["cultural_context"],
            learning_objectives=data["learning_objectives"],
            conversation_starters=data["conversation_starters"],
            scenario_variations=data["scenario_variations"],
            difficulty_modifiers=data["difficulty_modifiers"],
            success_metrics=data["success_metrics"],
        )

    def _create_default_templates(self):
        """Create default templates when no configuration files exist"""
        logger.info("Creating comprehensive 32-scenario template system")

        # Load Tier 1 & 2 templates from scenario_templates module
        from .scenario_templates import ScenarioTemplates

        tier1_templates = ScenarioTemplates.get_tier1_templates()
        tier2_templates = ScenarioTemplates.get_tier2_templates()

        # Load extended templates (Tiers 3-4) from extended module
        try:
            from app.services.scenario_templates_extended import (
                ExtendedScenarioTemplates,
            )

            extended_templates = ExtendedScenarioTemplates.get_all_extended_templates()
            all_templates = tier1_templates + tier2_templates + extended_templates
            logger.info(
                f"Successfully loaded {len(tier1_templates)} Tier 1 + {len(tier2_templates)} Tier 2 + {len(extended_templates)} extended scenario templates = {len(all_templates)} total"
            )
        except ImportError as e:
            logger.warning(
                f"Could not load extended templates: {e}, using Tier 1-2 only"
            )
            all_templates = tier1_templates + tier2_templates

        for template in all_templates:
            self.universal_templates[template.template_id] = template
            logger.info(f"Created template: {template.name} (Tier {template.tier})")

    def get_all_templates(self) -> List[UniversalScenarioTemplate]:
        """Get all loaded templates"""
        return list(self.universal_templates.values())

    def get_template_by_id(
        self, template_id: str
    ) -> Optional[UniversalScenarioTemplate]:
        """Get specific template by ID"""
        return self.universal_templates.get(template_id)

    def get_templates_by_tier(
        self, tier: Optional[int] = None
    ) -> List[UniversalScenarioTemplate]:
        """Get templates filtered by tier"""
        templates = list(self.universal_templates.values())
        if tier is not None:
            templates = [t for t in templates if t.tier == tier]
        return sorted(templates, key=lambda t: (t.tier, t.name))

    def get_templates_by_category(
        self, category: ScenarioCategory
    ) -> List[UniversalScenarioTemplate]:
        """Get templates by category"""
        return [t for t in self.universal_templates.values() if t.category == category]
