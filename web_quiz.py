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

import json
import argparse
import logging
import sys
import ssl
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template_string, jsonify, request, send_from_directory, redirect

from quizzer import Quiz, QuizResult, normalize_answer
import run_quiz  # Import for HTML report generation

# SSL Certificate Generation
def generate_self_signed_cert(cert_dir='certs'):
    """
    Generate self-signed SSL certificates for HTTPS.
    
    Args:
        cert_dir: Directory to store certificates (default: 'certs')
        
    Returns:
        tuple: (cert_path, key_path) or (None, None) if generation fails
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        cert_path = Path(cert_dir) / 'cert.pem'
        key_path = Path(cert_dir) / 'key.pem'
        
        # Check if certificates already exist
        if cert_path.exists() and key_path.exists():
            return str(cert_path), str(key_path)
        
        # Create certs directory if it doesn't exist
        Path(cert_dir).mkdir(exist_ok=True)
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Quizzer Development"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate to file
        with open(cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key to file
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ Generated self-signed certificates in '{cert_dir}/' directory")
        return str(cert_path), str(key_path)
        
    except ImportError:
        print("⚠️  cryptography package not installed. Install with: pip install cryptography")
        print("   Running without HTTPS support.")
        return None, None
    except Exception as e:
        print(f"⚠️  Failed to generate SSL certificates: {e}")
        print("   Running without HTTPS support.")
        return None, None


# Setup logging
def setup_logging(file_level=logging.DEBUG, console_level=logging.DEBUG):
    """
    Configure logging with file and console handlers.
    
    Args:
        file_level: Log level for file handler (default: DEBUG - logs everything)
        console_level: Log level for console handler (default: DEBUG - logs everything)
    
    Returns:
        logger: Configured logger instance
    """
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('quizzer')
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with rotation (max 10MB, keep 5 backup files)
    log_file = logs_dir / 'web_quiz.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()  # Will be reconfigured in main() based on CLI args

app = Flask(__name__)

# Flask error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f'404 Not Found: {request.url}')
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'500 Internal Server Error: {error}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f'Unhandled exception: {error}', exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

# HTML Template - Version 2.0 - Sidebar and Dashboard Layout
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <!-- UI Version: 5.0 - BLUE THEME (300px sidebar) + DARK MODE - Generated: {{ timestamp }} -->
    <title>Quizzer - Performance Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-blue: #2563eb;
            --primary-blue-dark: #1e40af;
            --primary-blue-light: #3b82f6;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --sidebar-bg: linear-gradient(180deg, #2563eb 0%, #1e40af 100%);
            --card-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --primary-blue: #3b82f6;
                --primary-blue-dark: #2563eb;
                --primary-blue-light: #60a5fa;
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --bg-tertiary: #334155;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --border-color: #334155;
                --sidebar-bg: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
                --card-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Sidebar Navigation */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 300px;
            background: var(--sidebar-bg);
            color: white;
            padding: 20px;
            overflow-y: auto;
            transition: transform 0.3s ease;
            z-index: 1000;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }

        .sidebar.collapsed {
            transform: translateX(-300px);
        }

        .sidebar-header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }

        .sidebar-header h1 {
            font-size: 1.5em;
            color: white;
        }

        .menu-section {
            margin-bottom: 25px;
        }

        .menu-section-title {
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.7;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .menu-item {
            padding: 10px 12px;
            margin-bottom: 5px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.1);
            font-size: 0.95em;
        }

        .menu-item:hover {
            background: rgba(255,255,255,0.2);
            transform: translateX(3px);
        }

        .menu-item.active {
            background: rgba(255,255,255,0.3);
            font-weight: 600;
        }

        .menu-item-icon {
            font-size: 1.2em;
        }

        .expandable-menu {
            margin-top: 5px;
        }

        .expandable-header {
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255,255,255,0.1);
        }

        .expandable-header:hover {
            background: rgba(255,255,255,0.2);
        }

        .expandable-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding-left: 15px;
        }

        .expandable-content.expanded {
            max-height: 500px;
        }

        .quiz-menu-item {
            padding: 10px 12px;
            margin: 5px 0;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9em;
            background: rgba(255,255,255,0.05);
        }

        .quiz-menu-item:hover {
            background: rgba(255,255,255,0.15);
            transform: translateX(3px);
        }

        .chevron {
            transition: transform 0.3s ease;
        }

        .chevron.rotated {
            transform: rotate(90deg);
        }

        /* Main Content Area */
        .main-content {
            margin-left: 300px;
            padding: 30px;
            min-height: 100vh;
            transition: margin-left 0.3s ease;
        }

        .main-content.expanded {
            margin-left: 0;
        }

        .toggle-sidebar {
            position: fixed;
            left: 260px;
            top: 20px;
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: var(--card-shadow);
            z-index: 999;
            transition: left 0.3s ease;
        }

        .toggle-sidebar.collapsed {
            left: 10px;
        }

        /* Dashboard */
        .dashboard-header {
            background: var(--primary-blue);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        }

        .dashboard-header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: white;
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--bg-primary);
            padding: 25px;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary-blue);
            margin-bottom: 5px;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .report-section {
            background: var(--bg-primary);
            padding: 30px;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
            margin-bottom: 25px;
        }

        .report-section h2 {
            color: var(--text-primary);
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .report-section h3 {
            color: var(--text-secondary);
            margin-top: 20px;
            margin-bottom: 12px;
            font-size: 1.2em;
        }

        .report-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .report-table th {
            background: var(--bg-tertiary);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: var(--text-primary);
            border-bottom: 2px solid var(--border-color);
        }

        .report-table td {
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }

        .report-table tr:hover {
            background: var(--bg-tertiary);
        }

        .trend-bar {
            width: 100%;
            margin: 10px 0;
        }

        .trend-item {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }

        .trend-label {
            width: 150px;
            font-size: 0.9em;
            color: #666;
        }

        .trend-bar-container {
            flex: 1;
            background: var(--bg-tertiary);
            height: 30px;
            border-radius: 5px;
            position: relative;
            overflow: hidden;
        }

        .trend-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-dark));
            border-radius: 5px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: 600;
            font-size: 0.85em;
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .analysis-item {
            background: var(--bg-tertiary);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-blue);
        }

        .analysis-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--primary-blue);
            margin-bottom: 5px;
        }

        .analysis-label {
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .timeline {
            position: relative;
            padding-left: 30px;
        }

        .timeline:before {
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--border-color);
        }

        .timeline-item {
            position: relative;
            padding-bottom: 20px;
        }

        .timeline-item:before {
            content: '';
            position: absolute;
            left: -24px;
            top: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--primary-blue);
            border: 2px solid var(--bg-primary);
        }

        .timeline-content {
            background: var(--bg-tertiary);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid var(--primary-blue);
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }

        .badge-pass {
            background: #d4edda;
            color: #155724;
        }

        .badge-fail {
            background: #f8d7da;
            color: #721c24;
        }

        .badge-excellent {
            background: #cce5ff;
            color: #004085;
        }


        .run-item {
            padding: 15px;
            border-left: 4px solid var(--primary-blue);
            background: var(--bg-tertiary);
            margin-bottom: 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .run-item:hover {
            background: var(--bg-secondary);
            transform: translateX(3px);
        }

        .run-item.passed {
            border-left-color: #28a745;
        }

        .run-item.failed {
            border-left-color: #dc3545;
        }

        .run-title {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 5px;
        }

        .run-meta {
            color: var(--text-secondary);
            font-size: 0.85em;
        }

        /* Quiz Selection */
        .quiz-selection {
            background: var(--bg-primary);
            padding: 30px;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
        }

        .quiz-selection h2 {
            color: var(--text-primary);
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .quiz-list {
            list-style: none;
        }

        .quiz-item {
            background: var(--bg-tertiary);
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .quiz-item:hover {
            background: var(--bg-secondary);
            border-color: var(--primary-blue);
            transform: translateX(5px);
            box-shadow: 0 3px 10px rgba(37, 99, 235, 0.2);
        }

        .quiz-item-title {
            font-weight: 600;
            color: var(--text-primary);
            font-size: 1.2em;
            margin-bottom: 8px;
        }

        .quiz-item-details {
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        /* Full Page Quiz Mode */
        .quiz-fullpage {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--primary-blue);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .quiz-container {
            background: var(--bg-primary);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .question-container {
            margin-bottom: 25px;
        }

        .progress-bar {
            background: var(--bg-tertiary);
            height: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            overflow: hidden;
        }

        .progress-fill {
            background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-dark));
            height: 100%;
            transition: width 0.3s ease;
        }

        .progress-text {
            text-align: center;
            color: var(--text-secondary);
            margin-bottom: 20px;
            font-weight: 600;
        }

        .question-text {
            font-size: 1.3em;
            color: var(--text-primary);
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .answer-input {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border-color);
            background: var(--bg-primary);
            color: var(--text-primary);
            border-radius: 8px;
            font-size: 1.1em;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }

        .answer-input:focus {
            outline: none;
            border-color: var(--primary-blue);
        }

        .button {
            background: var(--primary-blue);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            font-weight: 600;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
            background: var(--primary-blue-dark);
        }

        .button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .button-secondary {
            background: #6c757d;
            margin-left: 10px;
        }

        .feedback {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .feedback-correct {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }

        .feedback-incorrect {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }

        .results-summary {
            text-align: center;
            margin: 30px 0;
        }

        .results-score {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }

        .results-pass {
            color: #28a745;
        }

        .results-fail {
            color: #dc3545;
        }

        .results-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            margin-top: 5px;
        }

        .failures-list {
            margin-top: 30px;
        }

        .failure-item {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ffc107;
        }

        .failure-question {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }

        .failure-answer {
            color: #dc3545;
            margin-bottom: 5px;
        }

        .failure-correct {
            color: #28a745;
        }

        .hidden {
            display: none !important;
        }

        /* Overlay Notifications */
        .notification-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 3000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .notification-box {
            background: var(--bg-primary);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            padding: 30px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        .notification-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .notification-title {
            font-size: 1.5em;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 10px;
        }

        .notification-message {
            color: var(--text-secondary);
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .notification-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
        }

        .notification-btn {
            padding: 10px 25px;
            border-radius: 8px;
            border: none;
            font-size: 1em;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s ease;
        }

        .notification-btn:hover {
            transform: translateY(-2px);
        }

        .notification-btn-primary {
            background: var(--primary-blue);
            color: white;
        }

        .notification-btn-primary:hover {
            background: var(--primary-blue-dark);
        }

        .notification-btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .notification-btn-secondary:hover {
            background: var(--bg-secondary);
        }

        .timer {
            text-align: right;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-300px);
            }

            .sidebar.mobile-visible {
                transform: translateX(0);
            }

            .main-content {
                margin-left: 0;
            }

            .toggle-sidebar {
                left: 10px;
            }

            .dashboard-stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Toggle Sidebar Button -->
    <button class="toggle-sidebar" id="toggleSidebar" onclick="toggleSidebar()">☰</button>

    <!-- Sidebar Navigation -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>🎯 Quizzer</h1>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">Navigation</div>
            <div class="menu-item active" onclick="showView('dashboard')">
                <span class="menu-item-icon">📊</span>
                <span>Dashboard</span>
            </div>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">Quizzes</div>
            <div class="expandable-menu">
                <div class="expandable-header" onclick="toggleQuizMenu()">
                    <span>Available Quizzes</span>
                    <span class="chevron" id="quizChevron">▶</span>
                </div>
                <div class="expandable-content" id="quizMenuContent">
                    <!-- Quiz items will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content" id="mainContent">
        <!-- Dashboard View -->
        <div id="dashboardView" class="view">
            <div class="dashboard-header">
                <h1>Dashboard</h1>
                <p style="opacity: 0.9;">Track your quiz performance and progress</p>
            </div>

            <!-- Overall Statistics -->
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-value" id="totalQuizzes">0</div>
                    <div class="stat-label">Available Quizzes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalRuns">0</div>
                    <div class="stat-label">Quiz Attempts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgScore">0%</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="passRate">0%</div>
                    <div class="stat-label">Pass Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="bestScore">0%</div>
                    <div class="stat-label">Best Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalQuestions">0</div>
                    <div class="stat-label">Questions Answered</div>
                </div>
            </div>

            <!-- Performance Trends -->
            <div class="report-section">
                <h2>📈 Performance Trends</h2>
                <div id="performanceTrends">
                    <p style="color: #666; text-align: center; padding: 20px;">
                        Complete some quizzes to see your performance trends
                    </p>
                </div>
            </div>

            <!-- Quiz Breakdown -->
            <div class="report-section">
                <h2>📊 Quiz Performance Breakdown</h2>
                <div id="quizBreakdown">
                    <p style="color: #666; text-align: center; padding: 20px;">
                        No quiz data available yet
                    </p>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="report-section">
                <h2>🕐 Recent Activity</h2>
                <div id="recentRunsList">
                    <p style="color: #666; text-align: center; padding: 20px;">
                        No quiz runs yet. Select a quiz from the menu to get started!
                    </p>
                </div>
            </div>

            <!-- Pass/Fail Analysis -->
            <div class="report-section">
                <h2>✅ Pass/Fail Analysis</h2>
                <div id="passFailAnalysis">
                    <p style="color: #666; text-align: center; padding: 20px;">
                        Complete quizzes to see pass/fail analysis
                    </p>
                </div>
            </div>
        </div>

        <!-- Quiz Selection View -->
        <div id="quizSelectionView" class="view hidden">
            <div class="quiz-selection">
                <h2>Select a Quiz</h2>
                <ul id="quizList" class="quiz-list"></ul>
            </div>
        </div>
    </div>

    <!-- Full Page Quiz Mode -->
    <div id="quizFullpage" class="quiz-fullpage hidden">
        <div class="quiz-container">
            <div class="timer" id="timer">Time: 0:00</div>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-text" id="progressText">Question 1 of 10</div>

            <div id="feedback" class="feedback hidden"></div>

            <div class="question-container">
                <div class="question-text" id="questionText"></div>
                <input
                    type="text"
                    id="answerInput"
                    class="answer-input"
                    placeholder="Enter your answer..."
                    autocomplete="off"
                />
            </div>

            <button id="submitBtn" class="button">Submit Answer</button>
            <button id="quitBtn" class="button button-secondary">Quit</button>
        </div>
    </div>

    <!-- Results Screen -->
    <div id="resultsScreen" class="quiz-fullpage hidden">
        <div class="quiz-container">
            <h2>Quiz Complete!</h2>
            <div class="results-summary">
                <div id="resultStatus" class="results-score"></div>
            </div>

            <div class="results-stats">
                <div class="stat-card">
                    <div class="stat-value" id="totalQuestions">0</div>
                    <div class="stat-label">Total Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="correctAnswers">0</div>
                    <div class="stat-label">Correct</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="incorrectAnswers">0</div>
                    <div class="stat-label">Incorrect</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="finalScore">0%</div>
                    <div class="stat-label">Score</div>
                </div>
            </div>

            <div id="failuresList" class="failures-list"></div>

            <button id="backBtn" class="button">Back to Dashboard</button>
        </div>
    </div>

    <!-- Notification Overlay -->
    <div id="notificationOverlay" class="notification-overlay hidden">
        <div class="notification-box">
            <div id="notificationIcon" class="notification-icon"></div>
            <div id="notificationTitle" class="notification-title"></div>
            <div id="notificationMessage" class="notification-message"></div>
            <div id="notificationButtons" class="notification-buttons"></div>
        </div>
    </div>

    <script>
        let quizzes = [];
        let currentQuiz = null;
        let currentQuestionIndex = 0;
        let correctCount = 0;
        let failures = [];
        let startTime = null;
        let timerInterval = null;
        let quizRuns = JSON.parse(localStorage.getItem('quizRuns') || '[]');
        let sidebarCollapsed = false;

        // Notification System
        function showNotification(icon, title, message, buttons = [{ text: 'OK', primary: true }]) {
            const overlay = document.getElementById('notificationOverlay');
            const iconEl = document.getElementById('notificationIcon');
            const titleEl = document.getElementById('notificationTitle');
            const messageEl = document.getElementById('notificationMessage');
            const buttonsEl = document.getElementById('notificationButtons');

            iconEl.textContent = icon;
            titleEl.textContent = title;
            messageEl.textContent = message;
            buttonsEl.innerHTML = '';

            buttons.forEach(btn => {
                const button = document.createElement('button');
                button.className = `notification-btn ${btn.primary ? 'notification-btn-primary' : 'notification-btn-secondary'}`;
                button.textContent = btn.text;
                button.onclick = () => {
                    overlay.classList.add('hidden');
                    if (btn.onClick) btn.onClick();
                };
                buttonsEl.appendChild(button);
            });

            overlay.classList.remove('hidden');
        }

        function showConfirm(icon, title, message, onConfirm, onCancel) {
            showNotification(icon, title, message, [
                { text: 'Cancel', primary: false, onClick: onCancel },
                { text: 'Confirm', primary: true, onClick: onConfirm }
            ]);
        }

        // Sidebar Toggle
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const toggleBtn = document.getElementById('toggleSidebar');
            
            sidebarCollapsed = !sidebarCollapsed;
            
            if (sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                toggleBtn.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                toggleBtn.classList.remove('collapsed');
            }
        }

        // Toggle Quiz Menu
        function toggleQuizMenu() {
            const content = document.getElementById('quizMenuContent');
            const chevron = document.getElementById('quizChevron');
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                chevron.classList.remove('rotated');
            } else {
                content.classList.add('expanded');
                chevron.classList.add('rotated');
                // Load quizzes if not already loaded
                if (quizzes.length === 0) {
                    loadQuizzes();
                }
            }
        }

        // Show View
        function showView(viewName) {
            console.log('Showing view:', viewName);
            
            // Hide all views
            document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
            
            // Show selected view
            if (viewName === 'dashboard') {
                document.getElementById('dashboardView').classList.remove('hidden');
                updateDashboard();
            } else if (viewName === 'quizSelection') {
                document.getElementById('quizSelectionView').classList.remove('hidden');
                displayQuizList();
            }

            // Update active menu item
            document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            event.target.closest('.menu-item')?.classList.add('active');
        }

        // Load quiz list
        async function loadQuizzes() {
            console.log('Loading quizzes...');
            const response = await fetch('/api/quizzes');
            quizzes = await response.json();
            console.log('Loaded quizzes:', quizzes.length);
            
            displayQuizMenuItems();
            displayQuizList();
            updateDashboard();
        }

        function displayQuizMenuItems() {
            const menuContent = document.getElementById('quizMenuContent');
            menuContent.innerHTML = '';

            if (quizzes.length === 0) {
                menuContent.innerHTML = '<div style="padding: 10px; color: rgba(255,255,255,0.7); font-size: 0.85em;">No quizzes available</div>';
                return;
            }

            quizzes.forEach(quiz => {
                const div = document.createElement('div');
                div.className = 'quiz-menu-item';
                div.textContent = quiz.quiz_id;
                div.onclick = () => startQuizFromMenu(quiz.path);
                menuContent.appendChild(div);
            });
        }

        function displayQuizList() {
            const listEl = document.getElementById('quizList');
            listEl.innerHTML = '';

            if (quizzes.length === 0) {
                listEl.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No quizzes available. Import some CSV files first!</p>';
                return;
            }

            quizzes.forEach(quiz => {
                const li = document.createElement('li');
                li.className = 'quiz-item';
                li.innerHTML = `
                    <div class="quiz-item-title">${quiz.quiz_id}</div>
                    <div class="quiz-item-details">
                        ${quiz.num_questions} questions
                        ${quiz.source_file ? '• ' + quiz.source_file : ''}
                    </div>
                `;
                li.onclick = () => startQuiz(quiz.path);
                listEl.appendChild(li);
            });
        }

        function startQuizFromMenu(quizPath) {
            console.log('Starting quiz from menu:', quizPath);
            startQuiz(quizPath);
        }

        async function startQuiz(quizPath) {
            console.log('Starting quiz:', quizPath);
            const response = await fetch(`/api/quiz?path=${encodeURIComponent(quizPath)}`);
            currentQuiz = await response.json();
            currentQuestionIndex = 0;
            correctCount = 0;
            failures = [];
            startTime = Date.now();

            // Show full page quiz mode
            document.getElementById('quizFullpage').classList.remove('hidden');
            startTimer();
            displayQuestion();
        }

        function startTimer() {
            timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('timer').textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
        }

        function stopTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }

        function displayQuestion() {
            const question = currentQuiz.questions[currentQuestionIndex];
            document.getElementById('questionText').textContent = question.question;
            document.getElementById('answerInput').value = '';
            document.getElementById('answerInput').focus();

            const progress = ((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent =
                `Question ${currentQuestionIndex + 1} of ${currentQuiz.questions.length}`;

            document.getElementById('feedback').classList.add('hidden');
            document.getElementById('submitBtn').disabled = false;
        }

        async function submitAnswer() {
            const userAnswer = document.getElementById('answerInput').value.trim();
            if (!userAnswer) return;

            document.getElementById('submitBtn').disabled = true;

            const question = currentQuiz.questions[currentQuestionIndex];
            const response = await fetch('/api/check-answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_answer: userAnswer,
                    correct_answer: question.original_answer
                })
            });

            const result = await response.json();
            const feedbackEl = document.getElementById('feedback');
            feedbackEl.classList.remove('hidden', 'feedback-correct', 'feedback-incorrect');

            if (result.correct) {
                correctCount++;
                feedbackEl.textContent = '✓ Correct!';
                feedbackEl.classList.add('feedback-correct');
            } else {
                failures.push({
                    question_id: question.id,
                    question: question.question,
                    user_answer: userAnswer,
                    correct_answer: question.original_answer
                });
                feedbackEl.innerHTML = `✗ Incorrect<br>Correct answer: ${question.original_answer}`;
                feedbackEl.classList.add('feedback-incorrect');
            }

            setTimeout(() => {
                currentQuestionIndex++;
                if (currentQuestionIndex < currentQuiz.questions.length) {
                    displayQuestion();
                } else {
                    showResults();
                }
            }, 2000);
        }

        function showResults() {
            console.log('showResults called');
            stopTimer();
            const totalQuestions = currentQuiz.questions.length;
            const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
            const passed = scorePercentage >= 80;
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);

            console.log('Results:', { totalQuestions, correctCount, scorePercentage, passed });

            // Save run to local storage
            const run = {
                quiz_id: currentQuiz.quiz_id,
                timestamp: new Date().toISOString(),
                score: parseFloat(scorePercentage),
                passed: passed,
                total_questions: totalQuestions,
                correct: correctCount,
                time_spent: timeSpent
            };
            quizRuns.unshift(run);
            if (quizRuns.length > 50) quizRuns = quizRuns.slice(0, 50); // Keep last 50
            localStorage.setItem('quizRuns', JSON.stringify(quizRuns));

            document.getElementById('totalQuestions').textContent = totalQuestions;
            document.getElementById('correctAnswers').textContent = correctCount;
            document.getElementById('incorrectAnswers').textContent = failures.length;
            document.getElementById('finalScore').textContent = scorePercentage + '%';

            const statusEl = document.getElementById('resultStatus');
            statusEl.textContent = passed ? '✓ PASS' : '✗ FAIL';
            statusEl.className = 'results-score ' + (passed ? 'results-pass' : 'results-fail');

            const failuresListEl = document.getElementById('failuresList');
            if (failures.length > 0) {
                failuresListEl.innerHTML = '<h3 style="margin-bottom: 15px;">Incorrect Answers:</h3>';
                failures.forEach(failure => {
                    const div = document.createElement('div');
                    div.className = 'failure-item';
                    div.innerHTML = `
                        <div class="failure-question">Q${failure.question_id}: ${failure.question}</div>
                        <div class="failure-answer">Your answer: ${failure.user_answer}</div>
                        <div class="failure-correct">Correct answer: ${failure.correct_answer}</div>
                    `;
                    failuresListEl.appendChild(div);
                });
            } else {
                failuresListEl.innerHTML = '<p style="text-align: center; color: #28a745; font-size: 1.2em; font-weight: 600;">🎉 Perfect Score!</p>';
            }

            // Hide quiz, show results
            document.getElementById('quizFullpage').classList.add('hidden');
            document.getElementById('resultsScreen').classList.remove('hidden');
            
            // Generate HTML report
            console.log('Generating HTML report...');
            generateHtmlReport();
        }

        function showScreen(screenId) {
            document.getElementById('selectionScreen').classList.add('hidden');
            document.getElementById('quizScreen').classList.add('hidden');
            document.getElementById('resultsScreen').classList.add('hidden');
            document.getElementById(screenId).classList.remove('hidden');
        }

        function quitQuiz() {
            console.log('quitQuiz called');
            if (!currentQuiz) {
                console.error('No quiz loaded');
                showNotification('⚠️', 'No Active Quiz', 'No quiz is currently active.');
                return;
            }
            showConfirm(
                '❓',
                'Quit Quiz',
                'Are you sure you want to quit and see your results?',
                () => {
                    console.log('User confirmed quit, showing results');
                    try {
                        showResults();
                    } catch (error) {
                        console.error('Error showing results:', error);
                        showNotification('❌', 'Error', 'Error showing results: ' + error.message);
                    }
                }
            );
        }

        function backToSelection() {
            document.getElementById('resultsScreen').classList.add('hidden');
            showView('dashboard');
            updateDashboard();
        }

        async function generateHtmlReport() {
            if (!currentQuiz) return;

            const totalQuestions = currentQuiz.questions.length;
            const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
            const passed = scorePercentage >= 80;
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);

            const result = {
                quiz_id: currentQuiz.quiz_id,
                total_questions: totalQuestions,
                correct_count: correctCount,
                failures: failures,
                score_percentage: parseFloat(scorePercentage),
                passed: passed,
                time_spent: timeSpent
            };

            try {
                const response = await fetch('/api/save-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ result: result, quiz: currentQuiz })
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Report saved:', data.report_path);
                    showNotification(
                        '✅',
                        'Quiz Complete!',
                        `Report saved to: ${data.report_path}`,
                        [{ text: 'OK', primary: true }]
                    );
                } else {
                    console.error('Failed to save report');
                    showNotification('⚠️', 'Warning', 'Failed to save report.');
                }
            } catch (error) {
                console.error('Error generating report:', error);
                showNotification('❌', 'Error', 'Error generating report: ' + error.message);
            }
        }

        function updateDashboard() {
            console.log('Updating dashboard');
            
            // Update quiz count
            document.getElementById('totalQuizzes').textContent = quizzes.length;
            
            // Update run statistics
            document.getElementById('totalRuns').textContent = quizRuns.length;
            
            if (quizRuns.length > 0) {
                // Calculate statistics
                const avgScore = quizRuns.reduce((sum, run) => sum + run.score, 0) / quizRuns.length;
                const bestScore = Math.max(...quizRuns.map(run => run.score));
                const totalQuestions = quizRuns.reduce((sum, run) => sum + run.total_questions, 0);
                const passCount = quizRuns.filter(run => run.passed).length;
                const passRate = (passCount / quizRuns.length * 100).toFixed(1);
                
                document.getElementById('avgScore').textContent = avgScore.toFixed(1) + '%';
                document.getElementById('passRate').textContent = passRate + '%';
                document.getElementById('bestScore').textContent = bestScore.toFixed(1) + '%';
                document.getElementById('totalQuestions').textContent = totalQuestions;
                
                // Update all report sections
                displayPerformanceTrends();
                displayQuizBreakdown();
                displayRecentRuns();
                displayPassFailAnalysis();
            } else {
                document.getElementById('avgScore').textContent = '0%';
                document.getElementById('passRate').textContent = '0%';
                document.getElementById('bestScore').textContent = '0%';
                document.getElementById('totalQuestions').textContent = '0';
            }
        }

        function displayPerformanceTrends() {
            const trendsEl = document.getElementById('performanceTrends');
            if (quizRuns.length === 0) return;
            
            // Show last 10 runs as a trend
            const recentRuns = quizRuns.slice(0, 10).reverse();
            let html = '<div class="trend-bar">';
            
            recentRuns.forEach((run, index) => {
                const date = new Date(run.timestamp).toLocaleDateString();
                html += `
                    <div class="trend-item">
                        <div class="trend-label">${date} - ${run.quiz_id.substring(0, 15)}</div>
                        <div class="trend-bar-container">
                            <div class="trend-bar-fill" style="width: ${run.score}%">
                                ${run.score.toFixed(0)}%
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            trendsEl.innerHTML = html;
        }

        function displayQuizBreakdown() {
            const breakdownEl = document.getElementById('quizBreakdown');
            if (quizRuns.length === 0) return;
            
            // Group runs by quiz_id
            const quizStats = {};
            quizRuns.forEach(run => {
                if (!quizStats[run.quiz_id]) {
                    quizStats[run.quiz_id] = {
                        attempts: 0,
                        totalScore: 0,
                        passed: 0,
                        bestScore: 0
                    };
                }
                quizStats[run.quiz_id].attempts++;
                quizStats[run.quiz_id].totalScore += run.score;
                if (run.passed) quizStats[run.quiz_id].passed++;
                if (run.score > quizStats[run.quiz_id].bestScore) {
                    quizStats[run.quiz_id].bestScore = run.score;
                }
            });
            
            let html = '<table class="report-table"><thead><tr>';
            html += '<th>Quiz</th><th>Attempts</th><th>Avg Score</th><th>Best Score</th><th>Pass Rate</th>';
            html += '</tr></thead><tbody>';
            
            Object.entries(quizStats).forEach(([quizId, stats]) => {
                const avgScore = (stats.totalScore / stats.attempts).toFixed(1);
                const passRate = ((stats.passed / stats.attempts) * 100).toFixed(0);
                html += `
                    <tr>
                        <td><strong>${quizId}</strong></td>
                        <td>${stats.attempts}</td>
                        <td>${avgScore}%</td>
                        <td>${stats.bestScore.toFixed(1)}%</td>
                        <td><span class="badge ${stats.passed > 0 ? 'badge-pass' : 'badge-fail'}">${passRate}%</span></td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            breakdownEl.innerHTML = html;
        }

        function displayRecentRuns() {
            const listEl = document.getElementById('recentRunsList');
            if (quizRuns.length === 0) {
                listEl.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No quiz runs yet</p>';
                return;
            }
            
            const recentRuns = quizRuns.slice(0, 10);
            let html = '<div class="timeline">';
            
            recentRuns.forEach(run => {
                const date = new Date(run.timestamp);
                const timeStr = date.toLocaleString();
                const badge = run.score >= 90 ? 'excellent' : (run.passed ? 'pass' : 'fail');
                const badgeText = run.score >= 90 ? '🌟 Excellent' : (run.passed ? '✓ Pass' : '✗ Fail');
                
                html += `
                    <div class="timeline-item">
                        <div class="timeline-content">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong>${run.quiz_id}</strong>
                                <span class="badge badge-${badge}">${badgeText}</span>
                            </div>
                            <div style="color: #666; font-size: 0.9em;">
                                ${timeStr}<br>
                                Score: <strong>${run.score.toFixed(1)}%</strong> • 
                                ${run.correct}/${run.total_questions} correct •
                                Time: ${Math.floor(run.time_spent / 60)}:${(run.time_spent % 60).toString().padStart(2, '0')}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            listEl.innerHTML = html;
        }

        function displayPassFailAnalysis() {
            const analysisEl = document.getElementById('passFailAnalysis');
            if (quizRuns.length === 0) return;
            
            const passed = quizRuns.filter(run => run.passed).length;
            const failed = quizRuns.length - passed;
            const excellent = quizRuns.filter(run => run.score >= 90).length;
            const avgPassScore = passed > 0 
                ? quizRuns.filter(run => run.passed).reduce((sum, run) => sum + run.score, 0) / passed 
                : 0;
            const avgFailScore = failed > 0 
                ? quizRuns.filter(run => !run.passed).reduce((sum, run) => sum + run.score, 0) / failed 
                : 0;
            
            let html = '<div class="analysis-grid">';
            html += `
                <div class="analysis-item" style="border-left-color: #28a745;">
                    <div class="analysis-value" style="color: #28a745;">${passed}</div>
                    <div class="analysis-label">Passed Quizzes</div>
                </div>
                <div class="analysis-item" style="border-left-color: #dc3545;">
                    <div class="analysis-value" style="color: #dc3545;">${failed}</div>
                    <div class="analysis-label">Failed Quizzes</div>
                </div>
                <div class="analysis-item" style="border-left-color: #ffc107;">
                    <div class="analysis-value" style="color: #ffc107;">${excellent}</div>
                    <div class="analysis-label">Excellent (90%+)</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-value">${avgPassScore.toFixed(1)}%</div>
                    <div class="analysis-label">Avg Pass Score</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-value">${avgFailScore.toFixed(1)}%</div>
                    <div class="analysis-label">Avg Fail Score</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-value">${((passed / quizRuns.length) * 100).toFixed(0)}%</div>
                    <div class="analysis-label">Success Rate</div>
                </div>
            `;
            html += '</div>';
            analysisEl.innerHTML = html;
        }

        // Initialize event listeners when DOM is ready
        function initEventListeners() {
            console.log('Initializing event listeners...');
            
            const submitBtn = document.getElementById('submitBtn');
            const quitBtn = document.getElementById('quitBtn');
            const backBtn = document.getElementById('backBtn');
            const answerInput = document.getElementById('answerInput');

            console.log('Elements found:', {
                submitBtn: !!submitBtn,
                quitBtn: !!quitBtn,
                backBtn: !!backBtn,
                answerInput: !!answerInput
            });

            if (submitBtn) {
                submitBtn.addEventListener('click', function(e) {
                    console.log('Submit button clicked');
                    submitAnswer();
                });
                console.log('Submit button listener attached');
            }

            if (quitBtn) {
                quitBtn.addEventListener('click', function(e) {
                    console.log('Quit button clicked!');
                    e.preventDefault();
                    e.stopPropagation();
                    quitQuiz();
                });
                console.log('Quit button listener attached');
            } else {
                console.error('Quit button not found!');
            }

            if (backBtn) {
                backBtn.addEventListener('click', function(e) {
                    console.log('Back button clicked');
                    backToSelection();
                });
                console.log('Back button listener attached');
            }

            if (answerInput) {
                answerInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        console.log('Enter key pressed in answer input');
                        submitAnswer();
                    }
                });
                console.log('Answer input listener attached');
            }

            console.log('All event listeners initialized');
        }

        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOMContentLoaded event fired');
                initEventListeners();
                loadQuizzes();
            });
        } else {
            // DOM is already ready
            console.log('DOM already ready');
            initEventListeners();
            loadQuizzes();
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Serve the main quiz interface."""
    try:
        logger.debug('Serving main page')
        return render_template_string(HTML_TEMPLATE, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f'Error serving main page: {e}', exc_info=True)
        raise


@app.route('/version')
def version():
    """Return version info to verify what's being served."""
    return jsonify({
        'version': '5.0',
        'layout': 'Two-Column: Blue Theme Sidebar (300px) + Comprehensive Dashboard',
        'sidebar_width': '300px',
        'main_content_margin': '300px from left',
        'theme': 'Blue on white with dark mode support',
        'dashboard_features': [
            'Overall Statistics (6 stat cards)',
            'Performance Trends (visual bars)',
            'Quiz Performance Breakdown (detailed table)',
            'Recent Activity (timeline view)',
            'Pass/Fail Analysis (comprehensive stats)'
        ],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/quizzes')
def get_quizzes():
    """Get list of available quizzes."""
    try:
        logger.debug('Fetching quiz list')
        quizzes_dir = Path('data/quizzes')
        quiz_files = []

        if quizzes_dir.exists():
            # Search recursively for all quiz JSON files
            for quiz_file in quizzes_dir.rglob('*.json'):
                # Skip last_import.json metadata file
                if quiz_file.name == 'last_import.json':
                    continue

                try:
                    with open(quiz_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        quiz_files.append({
                            'path': str(quiz_file),
                            'quiz_id': data.get('quiz_id', quiz_file.stem),
                            'num_questions': len(data.get('questions', [])),
                            'source_file': data.get('source_file', ''),
                            'created_at': data.get('created_at', '')
                        })
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f'Error loading quiz file {quiz_file}: {e}')
                    continue
        else:
            logger.warning(f'Quizzes directory does not exist: {quizzes_dir}')

        # Sort by creation date (newest first)
        quiz_files.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        logger.info(f'Found {len(quiz_files)} quizzes')
        return jsonify(quiz_files)
    except Exception as e:
        logger.error(f'Error fetching quizzes: {e}', exc_info=True)
        return jsonify({'error': 'Failed to fetch quizzes'}), 500


@app.route('/api/quiz')
def get_quiz():
    """Get a specific quiz by path."""
    quiz_path = request.args.get('path')
    if not quiz_path:
        logger.warning('Quiz path not provided in request')
        return jsonify({'error': 'No quiz path provided'}), 400

    try:
        logger.debug(f'Loading quiz: {quiz_path}')
        quiz = Quiz.load(quiz_path)
        logger.info(f'Quiz loaded successfully: {quiz.quiz_id}')
        return jsonify(quiz.to_dict())
    except FileNotFoundError:
        logger.error(f'Quiz file not found: {quiz_path}')
        return jsonify({'error': 'Quiz not found'}), 404
    except Exception as e:
        logger.error(f'Error loading quiz {quiz_path}: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    """Check if user's answer is correct."""
    try:
        data = request.json
        user_answer = data.get('user_answer', '')
        correct_answer = data.get('correct_answer', '')

        # Normalize and compare answers
        user_normalized = normalize_answer(user_answer)
        correct_normalized = normalize_answer(correct_answer)

        is_correct = user_normalized == correct_normalized
        
        logger.debug(f'Answer check: user="{user_answer}" correct="{correct_answer}" result={is_correct}')

        return jsonify({
            'correct': is_correct,
            'normalized_user': user_normalized,
            'normalized_correct': correct_normalized
        })
    except Exception as e:
        logger.error(f'Error checking answer: {e}', exc_info=True)
        return jsonify({'error': 'Failed to check answer'}), 500


@app.route('/api/save-report', methods=['POST'])
def save_report():
    """Generate and save HTML report for quiz results."""
    try:
        logger.debug('Saving quiz report')
        data = request.json
        result_data = data.get('result', {})
        quiz_data = data.get('quiz', {})

        # Reconstruct Quiz object
        quiz = Quiz(
            quiz_id=quiz_data['quiz_id'],
            created_at=quiz_data.get('created_at', ''),
            source_file=quiz_data.get('source_file', ''),
            questions=[]
        )

        # Reconstruct QuizResult object
        result = QuizResult(
            quiz_id=result_data['quiz_id'],
            total_questions=result_data['total_questions'],
            correct_answers=result_data['correct_count'],
            failures=result_data['failures'],
            score_percentage=result_data['score_percentage'],
            passed=result_data['passed'],
            completed_at=datetime.now().isoformat(),
            time_spent=result_data.get('time_spent', 0)
        )

        # Generate and save HTML report
        report_path = run_quiz.save_html_report(result, quiz)
        logger.info(f'Report saved successfully: {report_path}')

        return jsonify({
            'success': True,
            'report_path': str(report_path)
        })

    except Exception as e:
        logger.error(f'Error saving report: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(
        description='Run the Quizzer web interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Start server on default port (5000):
    python web_quiz.py

  Start server on custom port:
    python web_quiz.py --port 8080

  Make server accessible from other devices:
    python web_quiz.py --host 0.0.0.0 --port 8080
        '''
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='host to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='port to run server on (default: 5000)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='run in debug mode'
    )
    
    parser.add_argument(
        '--no-https',
        action='store_true',
        help='disable HTTPS (use HTTP only, not recommended for production)'
    )
    
    parser.add_argument(
        '--cert',
        default='certs/cert.pem',
        help='path to SSL certificate file (default: certs/cert.pem)'
    )
    
    parser.add_argument(
        '--key',
        default='certs/key.pem',
        help='path to SSL private key file (default: certs/key.pem)'
    )
    
    parser.add_argument(
        '--log-level',
        default='ALL',
        choices=['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='log level for both file and console (default: ALL)'
    )
    
    parser.add_argument(
        '--log-file-level',
        default=None,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='log level for file only (overrides --log-level for file)'
    )
    
    parser.add_argument(
        '--log-console-level',
        default=None,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='log level for console only (overrides --log-level for console)'
    )

    args = parser.parse_args()
    
    # Configure logging based on arguments
    log_level_map = {
        'ALL': logging.DEBUG,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # Determine log levels
    base_level = log_level_map[args.log_level]
    file_level = log_level_map[args.log_file_level] if args.log_file_level else base_level
    console_level = log_level_map[args.log_console_level] if args.log_console_level else base_level
    
    # Reconfigure logger with specified levels
    global logger
    logger = setup_logging(file_level=file_level, console_level=console_level)
    
    # Log the configuration
    level_names = {v: k for k, v in log_level_map.items()}
    logger.info(f'Logging configured - File: {level_names.get(file_level, "DEBUG")}, Console: {level_names.get(console_level, "DEBUG")}')
    
    # Setup SSL context
    ssl_context = None
    protocol = 'http'
    
    if not args.no_https:
        # Generate or use existing certificates
        cert_path = args.cert
        key_path = args.key
        
        # Try to use provided certificates or generate new ones
        if not (Path(cert_path).exists() and Path(key_path).exists()):
            print("🔒 Generating self-signed SSL certificates...")
            cert_path, key_path = generate_self_signed_cert('certs')
        
        if cert_path and key_path:
            try:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_path, key_path)
                protocol = 'https'
                print("✅ HTTPS enabled with SSL certificates")
                logger.info('HTTPS enabled')
            except Exception as e:
                print(f"⚠️  Failed to load SSL certificates: {e}")
                print("   Falling back to HTTP")
                logger.warning(f'Failed to enable HTTPS: {e}')
                ssl_context = None
                protocol = 'http'
        else:
            print("⚠️  Could not generate SSL certificates, using HTTP")
            logger.warning('Running without HTTPS')
    else:
        print("⚠️  HTTPS disabled by --no-https flag (not recommended for production)")
        logger.warning('HTTPS explicitly disabled')

    print(f"\n{'='*60}")
    print("🎯 Quizzer Web Interface")
    print(f"{'='*60}")
    print(f"\n🌐 Server starting at: {protocol}://{args.host}:{args.port}")
    
    # Show logging configuration
    level_names_display = {
        logging.DEBUG: 'ALL (DEBUG)',
        logging.INFO: 'INFO',
        logging.WARNING: 'WARNING',
        logging.ERROR: 'ERROR',
        logging.CRITICAL: 'CRITICAL'
    }
    print(f"📝 Logging: File={level_names_display.get(file_level, 'DEBUG')}, Console={level_names_display.get(console_level, 'DEBUG')}")
    
    if protocol == 'https':
        print("\n🔒 HTTPS enabled (secure connection)")
        if 'localhost' in args.host or '127.0.0.1' in args.host:
            print("   ⚠️  Self-signed certificate - your browser may show a warning")
            print("   📝 Click 'Advanced' and 'Proceed to localhost' to continue")
    else:
        print("\n⚠️  HTTP only (not secure - use HTTPS for production)")
    
    if args.host == '127.0.0.1':
        print("   📍 Local access only")
    else:
        print("   📍 Accessible from network")
    
    print("\n📝 To stop the server, press Ctrl+C")
    print(f"📋 Logs saved to: logs/web_quiz.log")
    print(f"\n💡 Tip: Use --log-level to control logging verbosity (ALL/INFO/WARNING/ERROR)")
    print(f"{'='*60}\n")

    logger.info(f'Starting Quizzer web server on {args.host}:{args.port}')
    logger.info(f'Protocol: {protocol.upper()}')
    logger.info(f'Debug mode: {args.debug}')

    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        logger.info('Server stopped by user')
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.critical(f'Server error: {e}', exc_info=True)


if __name__ == '__main__':
    main()
