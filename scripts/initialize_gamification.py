"""
Initialize Gamification System

This script loads achievement definitions into the database.
Should be run after database migration.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.config import get_primary_db_session
from app.services.achievement_service import AchievementService


async def initialize_gamification():
    """Initialize gamification system"""
    print("Initializing gamification system...")

    db = get_primary_db_session()

    try:
        # Initialize achievements
        achievement_service = AchievementService(db)
        created_count = await achievement_service.initialize_achievements()

        print(f"✓ Initialized {created_count} new achievements")

        # Get achievement stats
        all_achievements = await achievement_service.get_all_achievements()
        print(f"✓ Total achievements in database: {len(all_achievements)}")

        # Show breakdown by category
        from collections import Counter

        categories = Counter(a.category for a in all_achievements)
        print("\nAchievements by category:")
        for category, count in categories.items():
            print(f"  - {category}: {count}")

        # Show breakdown by rarity
        rarities = Counter(a.rarity for a in all_achievements)
        print("\nAchievements by rarity:")
        for rarity, count in rarities.items():
            print(f"  - {rarity}: {count}")

        print("\n✓ Gamification system initialized successfully!")

    except Exception as e:
        print(f"\n✗ Error initializing gamification: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(initialize_gamification())
