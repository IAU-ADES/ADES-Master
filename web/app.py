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
from psvtoxml import psvtoxml

app = FastAPI(title="ADES Validation API", description="Validate ADES XML files against general schema")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

def validate_all_schemas(file_path: str) -> dict:
    """
    Validate ADES file (XML or PSV) against all available schemas and return the validation results.
    For PSV files, converts to XML first.
    """
    # Determine file type and prepare XML file
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.psv':
        # Convert PSV to XML
        xml_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        xml_temp_file.close()
        try:
            psvtoxml(file_path, xml_temp_file.name)
            xml_file_path = xml_temp_file.name
        except Exception as e:
            os.unlink(xml_temp_file.name)
            raise Exception(f"PSV to XML conversion failed: {str(e)}")
    elif file_ext == '.xml':
        xml_file_path = file_path
    else:
        raise Exception("Unsupported file type. Must be .xml or .psv")

    try:
        # Read the candidate XML
        candidate = adesutility.readXML(xml_file_path)

        # Capture output in a string buffer
        output_buffer = io.StringIO()

        # Validate XML declaration
        validate_xml_declaration(xml_file_path, output_buffer)

        # Validate against all schemas
        results = validate_xslts(adesutility.schemaxslts, candidate, output_buffer)

        # Get the output
        output = output_buffer.getvalue()
        output_buffer.close()

        return {"results": results, "output": output}
    finally:
        # Clean up temporary XML file if we created one
        if file_ext == '.psv':
            os.unlink(xml_file_path)

@app.post("/validate")
async def validate_file(file: UploadFile):
    """
    Validate an uploaded ADES file (XML or PSV) against all available schemas.
    PSV files are automatically converted to XML for validation.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.xml', '.psv']:
        raise HTTPException(status_code=400, detail="File must be an XML (.xml) or PSV (.psv) file")

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        # Perform validation
        validation_data = validate_all_schemas(temp_file_path)

        # Check if all validations passed (all results are None)
        is_valid = all(result is None for result in validation_data["results"].values())

        return {
            "filename": file.filename,
            "file_type": file_ext[1:].upper(),  # XML or PSV
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
            .result { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
            .schema-result { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .schema-ok { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .schema-failed { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .full-output { margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; }
            pre { word-wrap: break-word; overflow-wrap: break-word; }
        </style>
    </head>
    <body>
        <h1>ADES Validation</h1>
        <p>Upload an ADES XML or PSV file to validate it against all available schemas (submit, general, etc.). PSV files are automatically converted to XML for validation.</p>

        <form class="upload-form" id="uploadForm">
            <input type="file" id="fileInput" accept=".xml,.psv" required>
            <button type="submit">Validate</button>
        </form>

        <div id="result" class="result" style="display: none;"></div>
        
        <div style="text-align: right; margin-top: 20px; font-size: 14px; color: #666;">
            <a href="/docs" target="_blank" style="color: #007bff; text-decoration: none;">API Documentation</a>
        </div>

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
                    resultDiv.className = 'result';
                    
                    let html = `<h3>Validation Result for ${data.filename} (${data.file_type})</h3>`;
                    for (const [schema, error] of Object.entries(data.results)) {
                        const status = error ? 'Failed' : 'OK';
                        const statusClass = error ? 'schema-failed' : 'schema-ok';
                        html += `<div class="schema-result ${statusClass}"><strong>${schema}:</strong> ${status}`;
                        if (error) {
                            html += `<br><small>${error}</small>`;
                        }
                        html += '</div>';
                    }
                    // html += `<div class="full-output"><p>${data.output}</p></div>`;
                    
                    resultDiv.innerHTML = html;
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result';
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