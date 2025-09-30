from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import io
import sys
import os
import tempfile

# Add Python/bin to path to import ades modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Python', 'bin'))

import adesutility
from valutility import validate_xslts, validate_xml_declaration

app = FastAPI(title="ADES Validation API", description="Validate ADES XML files against general schema")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

def validate_all_schemas(xmlfile_path: str) -> dict:
    """
    Validate XML file against all available schemas and return the validation results.
    """
    # Read the candidate XML
    candidate = adesutility.readXML(xmlfile_path)

    # Capture output in a string buffer
    output_buffer = io.StringIO()

    # Validate XML declaration
    validate_xml_declaration(xmlfile_path, output_buffer)

    # Validate against all schemas
    results = validate_xslts(adesutility.schemaxslts, candidate, output_buffer)

    # Get the output
    output = output_buffer.getvalue()
    output_buffer.close()

    return {"results": results, "output": output}

@app.post("/validate")
async def validate_file(file: UploadFile):
    """
    Validate an uploaded ADES XML file against all available schemas.
    """
    if not file.filename or not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML file")

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        # Perform validation
        validation_data = validate_all_schemas(temp_file_path)

        # Check if all validations passed (all results are None)
        is_valid = all(result is None for result in validation_data["results"].values())

        return {
            "filename": file.filename,
            "valid": is_valid,
            "results": validation_data["results"],
            "output": validation_data["output"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the main web interface.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ADES Validation</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-form { margin: 20px 0; }
            .result { margin: 20px 0; padding: 10px; border: 1px solid #ccc; white-space: pre-wrap; }
            .schema-result { margin: 5px 0; }
            .schema-ok { color: green; font-weight: bold; }
            .schema-failed { color: red; font-weight: bold; }
            .full-output { margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; }
            pre { word-wrap: break-word; overflow-wrap: break-word; }
            .valid { background-color: #d4edda; border-color: #c3e6cb; }
            .invalid { background-color: #f8d7da; border-color: #f5c6cb; }
        </style>
    </head>
    <body>
        <h1>ADES XML Validation</h1>
        <p>Upload an ADES XML file to validate it against all available schemas (submit, general, etc.).</p>

        <form class="upload-form" id="uploadForm">
            <input type="file" id="fileInput" accept=".xml" required>
            <button type="submit">Validate</button>
        </form>

        <div id="result" class="result" style="display: none;"></div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const fileInput = document.getElementById('fileInput');
                const resultDiv = document.getElementById('result');

                if (!fileInput.files[0]) {
                    alert('Please select a file');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                try {
                    const response = await fetch('/validate', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result ' + (data.valid ? 'valid' : 'invalid');
                    
                    let html = `<h3>Validation Result for ${data.filename}</h3>`;
                    for (const [schema, error] of Object.entries(data.results)) {
                        const status = error ? 'Failed' : 'OK';
                        const statusClass = error ? 'schema-failed' : 'schema-ok';
                        html += `<div class="schema-result"><strong>${schema}:</strong> <span class="${statusClass}">${status}</span>`;
                        if (error) {
                            html += `<br><small>${error}</small>`;
                        }
                        html += '</div>';
                    }
                    // html += `<div class="full-output"><p>${data.output}</p></div>`;
                    
                    resultDiv.innerHTML = html;
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result invalid';
                    resultDiv.innerHTML = `<h3>Error</h3><p>${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)