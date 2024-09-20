import os
import jwt
import base64
from typing import Dict
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.main import app


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        auto_error: bool = True,
        request_limit: int = 100,
        interval: timedelta = timedelta(minutes=1),
    ):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.request_limit = request_limit
        self.interval = interval
        self.requests: Dict[str, list] = {}

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            is_verified, payload = self.verify_jwt(credentials.credentials)
            if not is_verified:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            self.rate_limit(credentials.credentials)
            return payload, credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def _generateJWT(payload) -> str:
        token = jwt.encode(
            payload,
            app.setting_instence.JWT_SECRET_KEY,
            algorithm=app.setting_instence.JWT_ALGORITHM,
        )
        return token

    @staticmethod
    def _decodeJWT(token: str) -> dict:
        try:
            base64_encoded_string = app.setting_instence.get_setting.JWT_SECRET_KEY
            decoded_bytes = base64.b64decode(base64_encoded_string)
            pub_decoded_string = decoded_bytes.decode("utf-8")

            return jwt.decode(
                token,
                pub_decoded_string,
                algorithms=[app.setting_instence.get_setting.JWT_ALGORITHM],
                audience="Client_Identity",
                issuer="FitAi",
            )
        except jwt.ExpiredSignatureError as err:
            print(err)
            return {}

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = self._decodeJWT(jwtoken)
        except Exception as e:
            print(e)
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid, payload

    def rate_limit(self, token: str):
        if token not in self.requests:
            self.requests[token] = []
        self.requests[token].append(datetime.now())
        self.requests[token] = [
            d for d in self.requests[token] if d > datetime.now() - self.interval
        ]
        if len(self.requests[token]) > self.request_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
            )
