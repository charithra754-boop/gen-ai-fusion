#!/usr/bin/env python3
"""
Database management CLI for FPO Economics Management System.
Provides commands to setup, migrate, and manage the database.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database.setup import (
    setup_database, 
    reset_database, 
    setup_test_database, 
    reset_test_database,
    check_database_status
)
from database.migrations.migration_manager import MigrationManager
from database.config import load_database_config, get_test_database_config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cmd_setup(args):
    """Setup database command."""
    config = get_test_database_config() if args.test else load_database_config()
    setup_database(config, include_sample_data=not args.no_sample_data)
    print(f"Database setup completed: {config.database}")


def cmd_reset(args):
    """Reset database command."""
    if not args.force:
        response = input("This will delete all data. Are you sure? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            return
    
    config = get_test_database_config() if args.test else load_database_config()
    reset_database(config, include_sample_data=not args.no_sample_data)
    print(f"Database reset completed: {config.database}")


def cmd_migrate(args):
    """Run database migrations command."""
    config = get_test_database_config() if args.test else load_database_config()
    
    migrations_dir = Path(__file__).parent / "database" / "migrations"
    migration_manager = MigrationManager(str(migrations_dir))
    
    if args.status:
        status = migration_manager.get_migration_status()
        print(f"Applied migrations: {status['total_applied']}")
        print(f"Pending migrations: {status['total_pending']}")
        
        if status['applied']:
            print("\nApplied:")
            for version in status['applied']:
                print(f"  - {version}")
        
        if status['pending']:
            print("\nPending:")
            for version in status['pending']:
                print(f"  - {version}")
    else:
        migration_manager.migrate()
        print("Migrations completed")


def cmd_status(args):
    """Check database status command."""
    config = get_test_database_config() if args.test else load_database_config()
    status = check_database_status(config)
    
    print(f"Database: {status['database']}")
    print(f"Connection: {'✓' if status['connection'] else '✗'}")
    
    if 'migrations' in status:
        migrations = status['migrations']
        print(f"Applied migrations: {migrations['total_applied']}")
        print(f"Pending migrations: {migrations['total_pending']}")
    
    if 'error' in status:
        print(f"Error: {status['error']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FPO Economics Management System Database Manager"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup database")
    setup_parser.add_argument("--test", action="store_true", help="Use test database")
    setup_parser.add_argument("--no-sample-data", action="store_true", help="Skip sample data")
    setup_parser.set_defaults(func=cmd_setup)
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset database")
    reset_parser.add_argument("--test", action="store_true", help="Use test database")
    reset_parser.add_argument("--no-sample-data", action="store_true", help="Skip sample data")
    reset_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    reset_parser.set_defaults(func=cmd_reset)
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    migrate_parser.add_argument("--test", action="store_true", help="Use test database")
    migrate_parser.add_argument("--status", action="store_true", help="Show migration status")
    migrate_parser.set_defaults(func=cmd_migrate)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check database status")
    status_parser.add_argument("--test", action="store_true", help="Use test database")
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging(args.log_level)
    
    try:
        args.func(args)
    except Exception as e:
        logging.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()