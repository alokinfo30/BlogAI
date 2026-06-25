# Blog-AI
Multi-Agent AI Article Writer using CrewAI Framework


blog-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agents.py
│   ├── tasks.py
│   ├── crew.py
│   └── utils.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── .env
├── .gitignore
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.md

# AI Article Generator - Multi-Agent System

## Overview
An intelligent article generation system using CrewAI multi-agent architecture. The system uses three specialized AI agents (Planner, Writer, Editor) to create high-quality content.

## Features
- 🤖 Multi-agent system with specialized roles
- 🔒 Secure and production-ready
- 📱 Responsive design for mobile and desktop
- ⚡ Rate limiting and input validation
- 🚀 Easy deployment to free hosting services

## Tech Stack
- **Backend**: Flask, CrewAI, OpenAI GPT-3.5
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Gunicorn, Heroku/Railway

## Installation

### Local Development
1. Clone the repository
2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

**Security Features**
Input sanitization using Bleach

Rate limiting to prevent abuse

Secure session configuration

Environment variables for sensitive data

CORS protection

**Usage**
Enter a topic (3-100 characters)

Click "Generate Article"

Wait for AI agents to process

Copy or read the generated article


**Security Checklist**
Environment variables for secrets

Input validation and sanitization

Rate limiting

Secure session configuration

CORS restrictions

SQL injection protection (using parameterized queries if DB is added)

XSS protection

HTTPS enforcement

Logging for monitoring


**Testing**
Test locally with python -m app.main

Test API endpoints:

GET /api/health

POST /api/generate

Test rate limiting

Test input validation


 The multi-agent architecture ensures high-quality article generation while maintaining security best practices.
