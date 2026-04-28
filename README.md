# LLM-Based ATS Resume Match Agent

## Overview
This project is a hybrid Python agent that compares a resume against a job description and estimates keyword alignment.

It uses a local LLM through Ollama to extract important job requirements and then uses Python logic to calculate a transparent match score.

This is not a real ATS system and does not guarantee job selection. It is an educational project that simulates resume-job description alignment.

## Features
- Uses a local LLM to extract important job requirements
- Categorizes requirements into:
  - technical skills
  - tools
  - business skills
  - responsibilities
  - qualifications
- Compares extracted requirements with resume text
- Calculates an estimated keyword alignment score
- Identifies matched and missing requirements
- Suggests truthful resume improvements

## Why I Built This
I built this project to understand how AI can support resume-job description matching without relying on paid APIs.

The goal was to avoid simple word counting and instead focus on meaningful job-related requirements.

## Tech Stack
- Python
- Ollama
- Local Llama 3.2 model
- JSON parsing
- Regular expressions

## How It Works
1. User pastes a job description
2. User pastes a resume
3. The local LLM extracts important job requirements
4. Python assigns weights to different requirement categories
5. Python compares the resume against extracted requirements
6. The agent calculates an estimated keyword alignment score
7. The agent lists matched and missing requirements
8. The agent suggests truthful improvements

---

## Setup Instructions

### 1. Install Ollama
Download from:
https://ollama.com

---

### 2. Start Ollama server
```bash
ollama serve
```

### 3. Pull model
```bash
ollama pull llama3.2:1b
```

### 4. Install Python dependency
```bash
pip install ollama
```

### 5. Run the project
```bash
python3 day6_resume_optimizer.py
```
