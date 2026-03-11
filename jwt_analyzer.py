"""
jwt_analyzer.py
────────────────────
"""
import json
import base64

class JWTAnalyzer:
    def decode_jwt(self, token):
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT"}
        header = base64.b64decode(parts[0] + '==').decode()
        payload = base64.b64decode(parts[1] + '==').decode()
        return {
            "header": json.loads(header),
            "payload": json.loads(payload)
        }
