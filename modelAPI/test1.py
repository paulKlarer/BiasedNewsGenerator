from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
import uvicorn
from initModel import InitializeModel

app = FastAPI()
model1 = InitializeModel()
# HTTP Basic Auth Konfiguration
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Pydantic-Modell, das einen Prompt definiert
class PromptRequest(BaseModel):
    prompt: str

# POST-Endpoint, der den Prompt entgegennimmt und eine Antwort zurückgibt
@app.post("/generate-response", dependencies=[Depends(get_current_username)])
async def generate_response(data: PromptRequest):
    #log info into console
    print(f"Received prompt: {data.prompt}---yonis")
    prompt = model1.runPromt(data.prompt)
    # Hier könnte eine komplexere Logik zur Antwortgenerierung implementiert werden
    response_text = f"Antwort auf deinen Prompt: '{prompt}'"
    return {"response": response_text}

# Optional: Starte den Server direkt mit diesem Skript
if __name__ == "__main__":
    print("Server wird gestartet...-Yonis")
    uvicorn.run("test1:app", host="0.0.0.0", port=8000, reload=True)
