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

        # Count optical elements
        optical_count = len(candidate.findall('.//optical'))

        # Capture output in a string buffer
        output_buffer = io.StringIO()

        # Validate XML declaration
        validate_xml_declaration(xml_file_path, output_buffer)

        # Validate against all schemas
        results = validate_xslts(adesutility.schemaxslts, candidate, output_buffer)

        # Get the output
        output = output_buffer.getvalue()
        output_buffer.close()

        return {"results": results, "output": output, "optical_count": optical_count}
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
            "output": validation_data["output"],
            "optical_count": validation_data["optical_count"]
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
            .progress-container { margin: 10px 0; display: none; }
            .progress-bar { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }
            .progress-fill { height: 100%; background-color: #007bff; width: 0%; transition: width 0.3s ease; }
            .progress-text { text-align: center; margin-top: 5px; font-size: 14px; color: #666; }
        </style>
    </head>
    <body>
        <h1>ADES Validation</h1>
        <p>Upload an ADES XML or PSV file to validate it against all available schemas (submit, general, etc.). PSV files are automatically converted to XML for validation.</p>

        <form class="upload-form" id="uploadForm">
            <input type="file" id="fileInput" accept=".xml,.psv" required>
            <button type="submit">Validate</button>
        </form>

        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Uploading...</div>
        </div>

        <div id="result" class="result" style="display: none;"></div>
        
        <div style="text-align: right; margin-top: 20px; font-size: 14px; color: #666;">
            <a href="/docs" target="_blank" style="color: #007bff; text-decoration: none;">API Documentation</a>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const fileInput = document.getElementById('fileInput');
                const resultDiv = document.getElementById('result');
                const progressContainer = document.getElementById('progressContainer');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');

                if (!fileInput.files[0]) {
                    alert('Please select a file');
                    return;
                }

                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);

                // Show progress bar
                progressContainer.style.display = 'block';
                progressFill.style.width = '0%';
                progressText.textContent = 'Uploading...';

                // Hide previous results
                resultDiv.style.display = 'none';

                try {
                    const xhr = new XMLHttpRequest();

                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                            const percentComplete = (e.loaded / e.total) * 100;
                            progressFill.style.width = percentComplete + '%';
                            progressText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
                        }
                    });

                    xhr.addEventListener('load', () => {
                        if (xhr.status === 200) {
                            const data = JSON.parse(xhr.responseText);

                            progressContainer.style.display = 'none';

                            resultDiv.style.display = 'block';
                            resultDiv.className = 'result';
                            
                            let html = `<h3>Validation Result for ${data.filename} (${data.file_type})</h3>`;
                            html += `<p><strong>Observations:</strong> ${data.optical_count.toLocaleString()}</p>`;
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
                        } else {
                            throw new Error(xhr.responseText || 'Upload failed');
                        }
                    });

                    xhr.addEventListener('error', () => {
                        progressContainer.style.display = 'none';
                        resultDiv.style.display = 'block';
                        resultDiv.className = 'result';
                        resultDiv.innerHTML = `<h3>Error</h3><p>Network error occurred during upload</p>`;
                    });

                    xhr.open('POST', '/validate');
                    xhr.send(formData);

                } catch (error) {
                    progressContainer.style.display = 'none';
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