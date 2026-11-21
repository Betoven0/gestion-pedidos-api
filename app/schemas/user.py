from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Esquema de base con atributos comunes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower().strip()

# Datos requeridos para registrar al usuario
class UserCreate(UserBase):
    password: str = Field(
        min_length=8, max_length=72, description="Contraseña en texto plano"
    )


# Datos Permitidos para la actuallizacion parcial
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=72)


# Datos devueltos al cliente(Response)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    # Clave técnica en Pydantic v2: permite leer directamente objetos del ORM
    model_config = ConfigDict(from_attributes=True)
