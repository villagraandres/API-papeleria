from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    contrasena: str
    role: str = "Empleado"  


class UserLogin(BaseModel):
    email: EmailStr
    contrasena: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)