"""Main application entry point for WatchLockAI Sentinel.

This module provides the main entry point for running Sentinel in various modes:
- Service mode (Windows service)
- Interactive mode (command line)
- Tray mode (with system tray UI)
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from core.config import load_config, save_default_config, validate_config
from core.logging import setup_logging
from detection.knowledge.loader import KnowledgeLoader
from platform.service.wrapper import SentinelService


class SentinelApplication:
    """Main Sentinel application coordinator."""

    def __init__(self, config_path: str | None = None, enable_ui: bool = True) -> None:
        """Initialize Sentinel application.

        Args:
            config_path: Path to configuration file.
            enable_ui: Whether to enable system tray UI.
        """
        self.config_path = config_path
        self.enable_ui = enable_ui
        self.service = SentinelService(config_path)
        self.tray_app = None
        self.tray_thread = None
        self.running = False

        # Signal handling
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, frame: Any) -> None:
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def start(self) -> None:
        """Start the Sentinel application."""
        if self.running:
            logger.warning("Sentinel application already running")
            return

        try:
            logger.info("Starting WatchLockAI Sentinel...")

            # Start core service
            await self.service.start()

            # Start tray UI if enabled
            if self.enable_ui:
                await self._start_tray_ui()

            self.running = True
            logger.info("WatchLockAI Sentinel started successfully")

        except Exception as e:
            logger.error(f"Failed to start Sentinel application: {e}")
            raise

    async def _start_tray_ui(self) -> None:
        """Start system tray UI in background thread."""
        try:
            from ui.tray_app import create_tray_app

            # Create tray app with managers
            self.tray_app = create_tray_app(
                alert_manager=self.service.alert_manager,
                actions_manager=self.service.actions_manager,
            )

            # Start tray in background thread
            self.tray_thread = self.tray_app.run_in_thread()
            logger.info("System tray UI started")

        except Exception as e:
            logger.warning(f"Failed to start tray UI: {e}")

    async def stop(self) -> None:
        """Stop the Sentinel application."""
        if not self.running:
            return

        logger.info("Stopping WatchLockAI Sentinel...")
        self.running = False

        try:
            # Stop tray UI
            if self.tray_app:
                self.tray_app.stop()
                if self.tray_thread:
                    self.tray_thread.join(timeout=5)
                logger.info("Tray UI stopped")

            # Stop core service
            await self.service.stop()

            logger.info("WatchLockAI Sentinel stopped")

        except Exception as e:
            logger.error(f"Error stopping Sentinel application: {e}")

    async def run_forever(self) -> None:
        """Run application until stopped."""
        await self.start()

        try:
            while self.running:
                await asyncio.sleep(1)

                # Update tray status if available
                if self.tray_app and self.service:
                    status = "Running" if self.service.running else "Stopped"
                    if (
                        self.service.actions_manager
                        and self.service.actions_manager.is_monitoring_paused()
                    ):
                        remaining = self.service.actions_manager.get_monitoring_pause_remaining()
                        status = f"Paused ({remaining}s)" if remaining else "Paused"

                    self.tray_app.update_status(status)

        except asyncio.CancelledError:
            logger.info("Application run loop cancelled")
        finally:
            await self.stop()


async def run_interactive(
    config_path: str | None = None, enable_ui: bool = True, debug: bool = False
) -> None:
    """Run Sentinel in interactive mode.

    Args:
        config_path: Path to configuration file.
        enable_ui: Whether to enable system tray UI.
        debug: Whether to enable debug logging.
    """
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(
        log_level=log_level,
        enable_console=True,
        enable_file=True,
        enable_jsonl_events=True,
        enable_jsonl_alerts=True,
    )

    logger.info("Starting WatchLockAI Sentinel in interactive mode")

    # Create and run application
    app = SentinelApplication(config_path, enable_ui)
    await app.run_forever()


def create_default_config() -> None:
    """Create default configuration file."""
    try:
        save_default_config("config.yaml")
        print("Default configuration saved to config.yaml")

        # Also create logs directory
        Path("logs").mkdir(exist_ok=True)
        print("Logs directory created")

    except Exception as e:
        print(f"Failed to create default configuration: {e}")


def validate_configuration(config_path: str) -> None:
    """Validate configuration file.

    Args:
        config_path: Path to configuration file.
    """
    try:
        config = load_config(config_path)
        warnings = validate_config(config)

        print(f"Configuration loaded from: {config_path}")

        if warnings:
            print("\nConfiguration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("Configuration is valid with no warnings")

    except Exception as e:
        print(f"Configuration validation failed: {e}")


def rebuild_knowledge_index(packs_dir: str = "detection/knowledge/packs") -> None:
    """Rebuild knowledge index from packs.

    Args:
        packs_dir: Directory containing knowledge packs.
    """
    try:
        loader = KnowledgeLoader(packs_dir)
        stats = loader.rebuild_index()

        print("Knowledge index rebuilt successfully:")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Sections indexed: {stats['sections_indexed']}")
        print(f"  Directives parsed: {stats['directives_parsed']}")
        print(f"  Mode: {stats['mode']}")

        if stats["errors"]:
            print("\nErrors encountered:")
            for error in stats["errors"]:
                print(f"  - {error}")

    except Exception as e:
        print(f"Failed to rebuild knowledge index: {e}")


def show_status() -> None:
    """Show current Sentinel status (placeholder)."""
    print("Status check not yet implemented")
    # TODO: Connect to running service and get status


def main() -> None:
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="WatchLockAI Sentinel - Host Security Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                           # Run interactively with tray UI
  python app.py --no-ui                   # Run without tray UI
  python app.py --debug                   # Run with debug logging
  python app.py --config custom.yaml     # Use custom configuration
  python app.py --create-config          # Create default configuration
  python app.py --validate-config        # Validate configuration
  python app.py --rebuild-index          # Rebuild knowledge index
        """,
    )

    # Main operation modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--create-config",
        action="store_true",
        help="Create default configuration file and exit",
    )
    mode_group.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration file and exit",
    )
    mode_group.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Rebuild knowledge index and exit",
    )
    mode_group.add_argument(
        "--status",
        action="store_true",
        help="Show Sentinel status and exit",
    )

    # Runtime options
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: search standard locations)",
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Disable system tray UI",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--packs-dir",
        type=str,
        default="detection/knowledge/packs",
        help="Directory containing knowledge packs",
    )

    args = parser.parse_args()

    try:
        # Handle utility commands
        if args.create_config:
            create_default_config()
            return

        elif args.validate_config:
            config_path = args.config or "config.yaml"
            validate_configuration(config_path)
            return

        elif args.rebuild_index:
            rebuild_knowledge_index(args.packs_dir)
            return

        elif args.status:
            show_status()
            return

        # Run interactive mode
        else:
            enable_ui = not args.no_ui
            asyncio.run(run_interactive(args.config, enable_ui, args.debug))

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
