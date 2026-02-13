#!/usr/bin/env python3
"""
Web Quiz Server - Browser-based quiz interface

This script provides a web interface for taking quizzes in the browser.

Usage:
    python web_quiz.py
    python web_quiz.py --port 8080
    python web_quiz.py --host 0.0.0.0 --port 8080

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import argparse
import logging
import ssl
import sys
from pathlib import Path

from quizzer.web import create_app
from quizzer.web.logging_config import setup_logging
from quizzer.web.ssl_utils import generate_self_signed_cert


def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(
        description="Run the Quizzer web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Start server on default port (5000):
    python web_quiz.py

  Start server on custom port:
    python web_quiz.py --port 8080

  Make server accessible from other devices:
    python web_quiz.py --host 0.0.0.0 --port 8080
        """,
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="host to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)",
    )

    parser.add_argument(
        "--port", type=int, default=5000, help="port to run server on (default: 5000)"
    )

    parser.add_argument("--debug", action="store_true", help="run in debug mode")

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="enable test mode (show sample quizzes, hidden by default in production)",
    )

    parser.add_argument(
        "--no-https",
        action="store_true",
        help="disable HTTPS (use HTTP only, not recommended for production)",
    )

    parser.add_argument(
        "--cert",
        default="certs/cert.pem",
        help="path to SSL certificate file (default: certs/cert.pem)",
    )

    parser.add_argument(
        "--key",
        default="certs/key.pem",
        help="path to SSL private key file (default: certs/key.pem)",
    )

    parser.add_argument(
        "--log-level",
        default="ALL",
        choices=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="log level for both file and console (default: ALL)",
    )

    parser.add_argument(
        "--log-file-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="log level for file only (overrides --log-level for file)",
    )

    parser.add_argument(
        "--log-console-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="log level for console only (overrides --log-level for console)",
    )

    args = parser.parse_args()

    # Configure logging based on arguments
    log_level_map = {
        "ALL": logging.DEBUG,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Determine log levels
    base_level = log_level_map[args.log_level]
    file_level = (
        log_level_map[args.log_file_level] if args.log_file_level else base_level
    )
    console_level = (
        log_level_map[args.log_console_level] if args.log_console_level else base_level
    )

    # Setup logger
    logger = setup_logging(file_level=file_level, console_level=console_level)

    # Log the configuration
    level_names = {v: k for k, v in log_level_map.items()}
    logger.info(
        f'Logging configured - File: {level_names.get(file_level, "DEBUG")}, Console: {level_names.get(console_level, "DEBUG")}'
    )

    # Create Flask app
    app = create_app(test_mode=args.test_mode)

    # Setup SSL context
    ssl_context = None
    protocol = "http"

    if not args.no_https:
        # Generate or use existing certificates
        cert_path = args.cert
        key_path = args.key

        # Try to use provided certificates or generate new ones
        if not (Path(cert_path).exists() and Path(key_path).exists()):
            print("🔒 Generating self-signed SSL certificates...")
            cert_path, key_path = generate_self_signed_cert("certs")

        if cert_path and key_path:
            try:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_path, key_path)
                protocol = "https"
                print("✅ HTTPS enabled with SSL certificates")
                logger.info("HTTPS enabled")
            except Exception as e:
                print(f"⚠️  Failed to load SSL certificates: {e}")
                print("   Falling back to HTTP")
                logger.warning(f"Failed to enable HTTPS: {e}")
                ssl_context = None
                protocol = "http"
        else:
            print("⚠️  Could not generate SSL certificates, using HTTP")
            logger.warning("Running without HTTPS")
    else:
        print("⚠️  HTTPS disabled by --no-https flag (not recommended for production)")
        logger.warning("HTTPS explicitly disabled")

    print(f"\n{'='*60}")
    print("🎯 Quizzer Web Interface")
    print(f"{'='*60}")
    print(f"\n🌐 Server starting at: {protocol}://{args.host}:{args.port}")

    if args.test_mode:
        print("⚠️  TEST MODE: Sample quizzes are visible")
    else:
        print("✅ PRODUCTION MODE: Sample quizzes hidden")

    # Show logging configuration
    level_names_display = {
        logging.DEBUG: "ALL (DEBUG)",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }
    print(
        f"📝 Logging: File={level_names_display.get(file_level, 'DEBUG')}, Console={level_names_display.get(console_level, 'DEBUG')}"
    )

    if protocol == "https":
        print("\n🔒 HTTPS enabled (secure connection)")
        if "localhost" in args.host or "127.0.0.1" in args.host:
            print("   ⚠️  Self-signed certificate - your browser may show a warning")
            print("   📝 Click 'Advanced' and 'Proceed to localhost' to continue")
    else:
        print("\n⚠️  HTTP only (not secure - use HTTPS for production)")

    if args.host == "127.0.0.1":
        print("   📍 Local access only")
    else:
        print("   📍 Accessible from network")

    print("\n📝 To stop the server, press Ctrl+C")
    print("📋 Logs saved to: logs/web_quiz.log")
    print(
        "\n💡 Tip: Use --log-level to control logging verbosity (ALL/INFO/WARNING/ERROR)"
    )
    print(f"{'='*60}\n")

    logger.info(f"Starting Quizzer web server on {args.host}:{args.port}")
    logger.info(f"Protocol: {protocol.upper()}")
    logger.info(f"Debug mode: {args.debug}")

    try:
        app.run(
            host=args.host, port=args.port, debug=args.debug, ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        logger.info("Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.critical(f"Server error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
