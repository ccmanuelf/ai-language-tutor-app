#!/usr/bin/env python3
"""
Reset Budget Data Script

This script clears API usage data to reset the monthly budget.
Use this for development/testing purposes to reset accumulated costs.

Usage:
    python scripts/reset_budget.py [--all | --current-month]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import func

from app.database.config import get_primary_db_session
from app.models.database import APIUsage


def reset_current_month():
    """Reset API usage for current month only"""
    db = get_primary_db_session()
    try:
        month_start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # Get current stats
        count = db.query(APIUsage).filter(APIUsage.created_at >= month_start).count()
        total_cost = (
            db.query(func.sum(APIUsage.estimated_cost))
            .filter(APIUsage.created_at >= month_start)
            .scalar()
            or 0.0
        )

        print(f"\nCurrent Month Usage:")
        print(f"  Records: {count}")
        print(f"  Total Cost: ${total_cost:.2f}")

        if count == 0:
            print("\nNo records to delete for current month.")
            return

        # Confirm deletion
        response = input(f"\nDelete {count} records? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return

        # Delete current month records
        deleted = db.query(APIUsage).filter(APIUsage.created_at >= month_start).delete()
        db.commit()

        print(f"\n✅ Deleted {deleted} API usage records for current month")
        print(f"   Budget reset to $0.00 / $30.00")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error resetting budget: {e}")
    finally:
        db.close()


def reset_all():
    """Reset all API usage data (development/testing only)"""
    db = get_primary_db_session()
    try:
        # Get current stats
        count = db.query(APIUsage).count()
        total_cost = db.query(func.sum(APIUsage.estimated_cost)).scalar() or 0.0

        print(f"\nAll-Time Usage:")
        print(f"  Records: {count}")
        print(f"  Total Cost: ${total_cost:.2f}")

        if count == 0:
            print("\nNo records to delete.")
            return

        # Confirm deletion
        print("\n⚠️  WARNING: This will delete ALL API usage data!")
        response = input(f"\nDelete ALL {count} records? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return

        # Delete all records
        deleted = db.query(APIUsage).delete()
        db.commit()

        print(f"\n✅ Deleted {deleted} API usage records")
        print(f"   Budget reset to $0.00 / $30.00")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error resetting budget: {e}")
    finally:
        db.close()


def show_status():
    """Show current budget status"""
    db = get_primary_db_session()
    try:
        month_start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # Current month stats
        month_count = (
            db.query(APIUsage).filter(APIUsage.created_at >= month_start).count()
        )
        month_cost = (
            db.query(func.sum(APIUsage.estimated_cost))
            .filter(APIUsage.created_at >= month_start)
            .scalar()
            or 0.0
        )

        # All-time stats
        all_count = db.query(APIUsage).count()
        all_cost = db.query(func.sum(APIUsage.estimated_cost)).scalar() or 0.0

        print(f"\n📊 Budget Status:")
        print(f"\nCurrent Month (December 2025):")
        print(f"  Records: {month_count}")
        print(f"  Total Cost: ${month_cost:.2f}")
        print(f"  Budget: $30.00")
        print(f"  Usage: {(month_cost / 30.0 * 100):.1f}%")

        print(f"\nAll-Time:")
        print(f"  Records: {all_count}")
        print(f"  Total Cost: ${all_cost:.2f}")

    except Exception as e:
        print(f"\n❌ Error getting status: {e}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Reset API usage budget data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reset_budget.py --status          # Show current status
  python scripts/reset_budget.py --current-month   # Reset current month
  python scripts/reset_budget.py --all             # Reset all data
        """,
    )

    parser.add_argument(
        "--current-month",
        action="store_true",
        help="Reset current month API usage data",
    )
    parser.add_argument(
        "--all", action="store_true", help="Reset ALL API usage data (use with caution)"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show current budget status"
    )

    args = parser.parse_args()

    if args.status or (not args.current_month and not args.all):
        show_status()
    elif args.all:
        reset_all()
    elif args.current_month:
        reset_current_month()


if __name__ == "__main__":
    main()
