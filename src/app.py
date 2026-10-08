from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
import json
import os
import tempfile

# Import your updated memory-efficient generators
from src.ingest import load_logs_lazily, chunk_iterable

class AnomalyReport(BaseModel):
    threat_level: str = Field(description="High, Medium, Low, or None")
    ip_address: str = Field(description="The source IP address of the anomaly, or 'N/A'")
    reason: str = Field(description="Why this was flagged")

app = FastAPI(title="Air-Gapped Log Anomaly API", version="1.0")
llm = OllamaLLM(model="llama3.1", format="json") # Force JSON mode

@app.post("/analyze-logs")
async def analyze_logs_endpoint(file: UploadFile = File(...)):
    """Receives a log file via API and returns AI-generated security anomalies."""
    
    # 1. Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    results = []
    
    # 2. Run your updated generator pipeline
    try:
        log_stream = load_logs_lazily(tmp_path)
        for chunk in chunk_iterable(log_stream, chunk_size=5):
            text_chunk = "\n".join(chunk)
            
            # 3. Use the strict example-based prompt
            prompt = f"""
            Analyze these system logs for security anomalies (like brute force attacks).
            
            You must output ONLY a populated JSON object. Do NOT output the schema definition itself.
            Use exactly this JSON format:
            {{
              "threat_level": "High",
              "ip_address": "extract_the_ip_here",
              "reason": "Explain what happened here"
            }}
            
            Logs to analyze:
            {text_chunk}
            """
            
            # 4. Get AI prediction and use Smart Extraction
            response = llm.invoke(prompt)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                parsed_json = json.loads(json_str)
                results.append(parsed_json)
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.remove(tmp_path) # Clean up the temp file
        
    return {"status": "success", "anomalies_found": results}