from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dependencies import get_current_user
from app.models.user import UserContext
from app.services import ai_service
import json
import logging
import random
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ai-health")
async def get_system_health(user: UserContext = Depends(get_current_user)):
    """
    Simulates a system health check by gathering stats and asking Gemini to evaluate them.
    Only allows users with 'admin' role (this mock checks if user exists).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify user role via Firestore or custom claims
    from app.services.firebase_service import get_firestore
    db = get_firestore()
    if db:
        user_doc = db.collection("users").document(user.uid).get()
        if not user_doc.exists or user_doc.to_dict().get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
    elif not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Gather mock system metrics
    active_users = random.randint(100, 500)
    cpu_usage = round(random.uniform(20.0, 95.0), 1)
    memory_usage = round(random.uniform(40.0, 90.0), 1)
    error_rate = round(random.uniform(0.1, 5.0), 2)
    api_latency = random.randint(50, 400)
    
    system_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "active_users": active_users,
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "error_rate_percent": error_rate,
            "api_latency_ms": api_latency,
            "recent_flags": ["Spam review detected", "Multiple failed login attempts for user xyz", "Payment gateway latency spike"]
        }
    }
    
    # Prompt Gemini to act as a System Health Analyst
    prompt = f"""
You are the GameHub AI System Monitor. Analyze the following real-time system metrics and provide a brief, professional health report (max 4 sentences).
Highlight any critical issues (like high CPU or error rates). If everything is fine, confirm system stability.

System Data:
{json.dumps(system_data, indent=2)}

Format: Return a plain text paragraph. No markdown headers.
    """
    
    try:
        # ai_service allows direct prompt without chatbot history if we use the underlying generation,
        # but generate_response includes standard rules. It's fine here.
        # However, to avoid "I cannot answer this" hallucination guards, we might need a direct call.
        # But we'll try standard method first.
        analysis = await ai_service.generate_response(prompt)
        
        return {
            "metrics": system_data["metrics"],
            "analysis": analysis,
            "status": "warning" if (cpu_usage > 85 or error_rate > 3) else "healthy"
        }
    except Exception as e:
        logger.error(f"Error generating AI health report: {e}")
        return {
            "metrics": system_data["metrics"],
            "analysis": "AI analysis temporarily unavailable due to server error.",
            "status": "unknown"
        }
