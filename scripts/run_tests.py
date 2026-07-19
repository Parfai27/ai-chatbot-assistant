#!/usr/bin/env python
"""
Run tests for the AI Chatbot Assistant.
Usage:
    pytest tests/
    pytest tests/ -v --cov=app --cov-report=html
"""
import os
import sys
import sys
sys.path.insert(0, 'backend')
sys.path.insert(0, 'tests')

sys.exit(pytest.main(sys.argv[1:]))
