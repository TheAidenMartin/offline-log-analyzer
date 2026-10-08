from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
import json
from src.ingest import load_logs_lazily, chunk_iterable

class AnomalyReport(BaseModel):
    threat_level: str = Field(description="High, Medium, Low, or None")
    ip_address: str = Field(description="The source IP address of the anomaly, or 'N/A'")
    reason: str = Field(description="Why this was flagged")

def analyze_logs():
    llm = OllamaLLM(model="llama3.1", format="json")
    print("Starting offline log analysis with lazy loading...")
    
    log_stream = load_logs_lazily("sample_auth.log")
    
    for chunk in chunk_iterable(log_stream, chunk_size=5):
        text_chunk = "\n".join(chunk)
        
        # UPDATED PROMPT: Explicitly forbidding schema regurgitation
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
        
        try:
            response = llm.invoke(prompt)
            
            # Smart Extraction
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                parsed_json = json.loads(json_str)
                print(json.dumps(parsed_json, indent=2))
            else:
                print(f"--- AI Failed to output JSON ---\nRaw Output:\n{response}")
            
        except Exception as e:
            print(f"--- JSON Parse Error ---\nRaw AI Output was:\n{response}\nError: {e}")

if __name__ == "__main__":
    analyze_logs()