# ADES Validation Web Service

A FastAPI-based web service for validating ADES (Astrodynamics Data Exchange Standard) files in XML and PSV formats against multiple schema variants.

## Overview

This service provides both a REST API and web interface for validating ADES files in XML and PSV (Pipe Separated Value) formats. It validates files against all available ADES schemas and provides additional metadata including the count of optical elements in the file.
- `submit` - Submission schema
- `submithuman` - Human-readable submission schema
- `general` - General schema
- `generalhuman` - Human-readable general schema

PSV files are automatically converted to XML format before validation.

## Installation

### Option 1: Local Installation

1. Follow the installation instructions for the main ADES-Master project to set up the required dependencies and environment.

2. The web service dependencies (FastAPI, Uvicorn, python-multipart) should be included in the main project's environment. If not, install them:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

### Option 2: Docker Installation

1. Ensure Docker and Docker Compose are installed on your system.

2. Build and run the service using Docker Compose:
   ```bash
   cd web
   docker-compose up --build
   ```

   Or build and run manually:
   ```bash
   # Use the build script (recommended - checks Docker installation and provides usage instructions)
   # Run from the repository root
   ./web/build.sh

   # Or build manually from the repository root
   docker build -f web/Dockerfile -t ades-validation .

   # Run the container
   docker run -p 8000:8000 ades-validation
   ```

The service will be available at `http://localhost:8000`

## Running the Service

### Docker (Recommended for Production)
```bash
cd web
docker-compose up --build
```

### Development Mode
```bash
python web/app.py
```

### Production Mode (Local)
```bash
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

The service will start on `http://localhost:8000`

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Click "Choose File" and select an ADES XML or PSV file
3. Click "Validate" to check the file against all schemas
4. Watch the progress bar during upload and validation processing
5. View the results showing pass/fail status for each schema and observation count

### REST API

#### Validate File
```http
POST /validate
Content-Type: multipart/form-data

file: <xml_file> or <psv_file>
```

**Response:**
```json
{
  "filename": "example.xml",
  "file_type": "XML",
  "valid": false,
  "optical_count": 42,
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
- `optical_count`: Number of `<optical>` elements found in the ADES file
- `results`: Object with schema names as keys; `null` for passed schemas, error string for failed ones
- `output`: Full validation output text

#### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## File Requirements

- Files must have `.xml` or `.psv` extension
- Must contain valid ADES data in the respective format
- PSV files are converted to XML before validation
- Current schemas expect ADES version '2022'

## Error Handling

- Invalid file types return HTTP 400
- Validation errors return HTTP 500 with details
- Network errors are handled gracefully in the web interface

## Development

The service reuses the existing ADES validation infrastructure from the ADES-Master project, specifically:
- `adesutility.py` for schema management
- `valutility.py` for validation logic
- `psvtoxml.py` for PSV to XML conversion
- XSLT transforms for schema generation

## Troubleshooting

- **"docker command not found"**: Ensure Docker Desktop is installed and running. The `web/build.sh` script will check for this automatically.
- **"uvicorn command not found"**: Ensure you're in the correct conda environment
- **Import errors**: Check that ADES-Master dependencies are installed
- **Schema validation fails**: Verify your XML conforms to ADES version 2022 standards</content>
<parameter name="filePath">/Users/mjuric/projects/github.com/mjuric/ADES-Master/web/README.md