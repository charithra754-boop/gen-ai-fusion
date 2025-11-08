from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import root_agent
import json

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/agent/master/")
async def chat_endpoint(request: Request):
    try:
        # Parse incoming request
        body = await request.json()
        user_query = body['contents'][0]['parts'][0]['text']
        
        # Call your agent
        response = root_agent.generate_content(user_query)
        
        # Format response in Gemini API structure
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": response.text
                    }]
                }
            }]
        }
    except Exception as e:
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": f"Error: {str(e)}"
                    }]
                }
            }]
        }

@app.get("/")
async def health_check():
    return {"status": "KisaanMitra API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)