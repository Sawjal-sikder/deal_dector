# PDF Export Installation Guide

## Install ReportLab for PDF functionality

To enable PDF export functionality, install reportlab:

```bash
# Activate your virtual environment first
source venv/bin/activate

# Install reportlab
pip install reportlab

# Update requirements.txt
pip freeze > requirements.txt
```

## Alternative: Add to requirements.txt

Add this line to your requirements.txt:

```
reportlab==4.0.4
```

Then install:

```bash
pip install -r requirements.txt
```

## If reportlab is not available

The system will automatically fallback to CSV export if reportlab is not installed.
