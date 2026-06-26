# Blog-AI
Multi-Agent AI Article Generator using CrewAI Framework. #  The multi-agent architecture ensures high-quality article generation while maintaining security best practices handle synchronous task



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

BlogAI\
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agents.py
│   ├── tasks.py
│   ├── crew.py
│   └── model_manager.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── .env
├── .gitignore
├── requirements.txt
├── generate_secret.py
├── test_models.py
└── test_api.py


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


# Running the System

# 1. Generate your SECRET_KEY:powershell
python generate_secret.py
# 2. Copy the generated key and paste it in .env: text
SECRET_KEY=your_generated_key_here
# 3. Test all models:powershell
python test_models.py
# 4. Run the application:powershell
python -m app.main
# 5. Test with API:powershell
Invoke-RestMethod -Uri "http://192.168.1.39:5000/api/health"

# Test API Key

python test_api_key.py

# Run the Python Test Script

python test_api.py

**Testing**
Test locally with python -m app.main

Test API endpoints:

GET /api/health

POST /api/generate

Test rate limiting

Test input validation


**Usage**
Enter a topic (3-100 characters)

Click "Generate Article"

Wait for AI agents to process

Copy or read the generated article

What to Expect
When everything works, the terminal will show:

Planner agent analyzing the topic

Writer agent creating the article

Editor agent reviewing and polishing

Final article returned to the frontend

The response will be a JSON object with:

json
{
  "status": "success",
  "topic": "artificial intelligence",
  "article": "Generated article content here...",
  "generated_at": "2026-06-25T14:06:00.869211"
}

# If the Request Hangs
# The article generation can take 30-60 seconds because:

# Planner agent analyzes the topic

# Writer agent creates content

# Editor agent reviews and polishes

# Be patient and watch the Flask terminal for progress updates.






How the Multi-Model System Works
1. Model Configuration
Primary model: gpt-3.5-turbo

Fallback models: gpt-4, gpt-3.5-turbo-16k, gpt-4-turbo-preview

Each agent can have its own model

2. Fallback Strategies
Sequential: Try primary, then fallback1, then fallback2

Random: Pick a random available model

Round Robin: Cycle through available models

3. Per-Agent Models
env
PLANNER_MODEL=gpt-4           # Planner uses GPT-4
WRITER_MODEL=gpt-3.5-turbo    # Writer uses GPT-3.5
EDITOR_MODEL=gpt-4            # Editor uses GPT-4
4. Automatic Fallback
If a model is unavailable, the system automatically:

Detects the failure

Switches to the next available model

Logs the fallback

Continues processing

# Testing the Multi-Model System
# 1. Test all models:powershell
python test_models.py
# 2. Check model status via API:powershell
Invoke-RestMethod -Uri "http://192.168.1.39:5000/api/models"
# 3. Health check with model info:powershell, Use the health check to verify everything is working
Invoke-RestMethod -Uri "http://192.168.1.39:5000/api/health"


Benefits of This Multi-Model System
High Availability: If one model fails, others take over

Cost Optimization: Use cheaper models for simple tasks

Performance: Use different models for different agent roles

Flexibility: Easy to add/remove models

Monitoring: Track which models are being used

Automatic Recovery: No manual intervention needed

Example Agent-Model Mapping
Agent	Model	Purpose
Planner	GPT-4	Better understanding and planning
Writer	GPT-3.5-turbo	Cost-effective content generation
Editor	GPT-4	Better editing and refinement
Monitoring and Logging
The system logs:

Which model each agent uses

Model availability status

Fallback events

Performance metrics


**Security Features/Checklist**
Environment variables for secrets /sensitive data
SECRET_KEY is generated securely

SECRET_KEY is at least 32 characters

SECRET_KEY is stored in .env (not in code)
.env is in .gitignore

API keys are in .env

Output is sanitized

Error messages don't expose sensitive info  

Input validation and sanitization using Bleach

Rate limiting to prevent abuse

Secure session configuration

CORS restrictions / protection

SQL injection protection (using parameterized queries if DB is added)

XSS protection

HTTPS enforcement

Logging for monitoring







Fix: Ignore S3 Extension Errors
The S3 errors are from the "Teal" browser extension. To stop them:

Option 1: Disable the Extension
Open Chrome/Edge

Go to chrome://extensions/

Find "Teal" or any similar extension

Toggle it OFF

Option 2: Filter Console Errors (Not Recommended)
In Chrome DevTools Console:

Click on the filter icon

Add negative filter: -teal.extension

This hides those messages

