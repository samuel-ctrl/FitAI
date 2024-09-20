from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional, Annotated
from datetime import datetime
from pydantic.functional_validators import BeforeValidator


# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class InfoModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="id", default=None)
    current_weight: float
    current_height: float
    goal_weight: float
    meal_restriction: List[str]
    diet_improvement: List[str]
    allergies: List[str]
    food_arround_me: List[str]
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "current_weight": 70,
                "current_height": 170,
                "goal_weight": 75,
                "meal_restriction": ["vegetarian", "vegan"],
                "diet_improvement": ["cutting carbs", "cutting fat"],
                "allergies": ["gluten", "peanuts"],
                "food_arround_me": ["PIZZA_HUT", "BURGER_KING"],
            }
        },
    )

    def _to_json(self):
        return self.model_dump(exclude_none=True)


class AllergiesModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="id", default=None)
    name: str = Field(max_length=50)


class AuthUser(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    roles: List[str] = Field(default=["User"])


class Token(BaseModel):
    token: str
    token_type: str = Field(..., examples=["bearer"])


class ResponseToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(..., examples=["bearer"])


class DietImprovementModel(BaseModel):
    name: str = Field(..., max_length=255)


class Allergies(BaseModel):
    name: str = Field(..., max_length=100)


class AllergiesCreate(BaseModel):
    name: str = Field(..., max_length=100)


class AllergiesUpdate(BaseModel):
    name: str = Field(None, max_length=100)


class DietImprovement(BaseModel):
    name: str = Field(..., max_length=100)


class DietImprovementCreate(BaseModel):
    name: str = Field(..., max_length=100)


class DietImprovementUpdate(BaseModel):
    name: str = Field(None, max_length=100)


class Detail(BaseModel):
    detail: str = Field(...)


class NameWithId(BaseModel):
    id: str = Field(...)
    name: str = Field(...)


class BaseResponse(BaseModel):
    total_count: int
    items: List[NameWithId]


class MealRestrictionModel(BaseModel):
    name: str = Field(..., max_length=255)


class MealRestriction(BaseModel):
    name: str = Field(..., max_length=100)


class MealRestrictionCreate(BaseModel):
    name: str = Field(..., max_length=100)


class MealRestrictionUpdate(BaseModel):
    name: str = Field(None, max_length=100)


class PreferenceResponse(BaseModel):
    goals: BaseResponse
    meals_restriction: BaseResponse
    diet_improvements: BaseResponse
    allergies: BaseResponse
    food_around_me: Optional[BaseResponse] = None


class User(BaseModel):
    email: EmailStr = Field(...)
    full_name: str = Field(default="")
    password: str = Field(...)
    is_active: bool = Field(default=True)
    last_login: datetime = Field(default=None)
    roles: List[str] = Field(default=["User"])


class UpdateUser(BaseModel):
    email: EmailStr = Field(..., examples=["test@example.com"])
    full_name: str = Field(default="", examples=["Test User"])
    roles: List[str] = Field(default=[], examples=[["admin", "editor"]])


class ResponseUser(BaseModel):
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    roles: Optional[List[str]]
    is_active: bool = True


class UserBasicInfoResponse(BaseModel):
    id: Optional[str]
    email: Optional[EmailStr]
    full_name: Optional[str]
