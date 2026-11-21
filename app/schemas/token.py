from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type:str= "bearer"
class TokenPayload(BaseModel):
    sub: Optional[str] = None #Subject (Este es el identificador unico del usuario)
    exp: Optional[int] = None #Timestamp de expiracion 