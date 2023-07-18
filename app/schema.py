from pydantic import BaseModel, field_validator
from typing import Optional, Type


class CreateUser(BaseModel):
    name: str
    password: str
    email: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password is too short")
        return password


class UpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]
    email: Optional[str]

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password is too short")
        return password


VALIDATION_CLASS = Type[CreateUser] | Type[UpdateUser]
