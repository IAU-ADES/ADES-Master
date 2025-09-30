# ADES Validation Web Service

A FastAPI-based web service for validating ADES (Astrodynamics Data Exchange Standard) XML files against multiple schema variants.

## Overview

This service provides both a REST API and web interface for validating ADES XML files. It validates files against all available ADES schemas:
- `submit` - Submission schema
- `submithuman` - Human-readable submission schema
- `general` - General schema
- `generalhuman` - Human-readable general schema

## Prerequisites

- Python 3.8+
- Conda environment (recommended)
- The ADES-Master project dependencies

## Installation

1. Follow the installation instructions for the main ADES-Master project to set up the required dependencies and environment.

2. The web service dependencies (FastAPI, Uvicorn, python-multipart) should be included in the main project's environment. If not, install them:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

## Running the Service

### Development Mode
```bash
python web/app.py
```

### Production Mode
```bash
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

The service will start on `http://localhost:8000`

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Click "Choose File" and select an ADES XML file
3. Click "Validate" to check the file against all schemas
4. View the results showing pass/fail status for each schema

### REST API

#### Validate File
```http
POST /validate
Content-Type: multipart/form-data

file: <xml_file>
```

**Response:**
```json
{
  "filename": "example.xml",
  "valid": false,
  "results": {
    "general": "lxml.etree.DocumentInvalid: Element 'ades', attribute 'version': [facet 'enumeration'] The value '2017' is not an element of the set {'2022'}.",
    "submit": null,
    "generalhuman": null,
    "submithuman": null
  },
  "output": "general has failed: lxml.etree.DocumentInvalid..."
}
```

- `valid`: `true` if all schemas pass, `false` otherwise
- `results`: Object with schema names as keys; `null` for passed schemas, error string for failed ones
- `output`: Full validation output text

#### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## File Requirements

- Files must have `.xml` extension
- Must be valid XML with proper ADES structure
- Current schemas expect ADES version '2022'

## Error Handling

- Invalid file types return HTTP 400
- Validation errors return HTTP 500 with details
- Network errors are handled gracefully in the web interface

## Development

The service reuses the existing ADES validation infrastructure from the ADES-Master project, specifically:
- `adesutility.py` for schema management
- `valutility.py` for validation logic
- XSLT transforms for schema generation

## Troubleshooting

- **"uvicorn command not found"**: Ensure you're in the correct conda environment
- **Import errors**: Check that ADES-Master dependencies are installed
- **Schema validation fails**: Verify your XML conforms to ADES version 2022 standards</content>
<parameter name="filePath">/Users/mjuric/projects/github.com/mjuric/ADES-Master/web/README.md