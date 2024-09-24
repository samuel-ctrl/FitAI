from datetime import datetime
from typing import List, Optional, Annotated, Union
from pydantic import BaseModel, Field, model_validator
from pydantic.functional_validators import BeforeValidator

"============================== REQUEST MODEL =================================="
PyObjectId = Annotated[str, BeforeValidator(str)]


class SearchRequest(BaseModel):
    prompt: bool
    text: Optional[str] = Field(None, example="what is the usage of the docs?")
    current_weight: Optional[float] = 70
    current_height: Optional[float] = 170
    goal_weight: Optional[float] = 75
    meal_restriction: Optional[List[str]] = []
    diet_improvement: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    food_arround_me: Optional[List[str]] = []
    history: Optional[List[dict]] = []

    @model_validator(mode="before")
    def check_fields_based_on_prompt(cls, values):
        prompt = values.get("prompt")
        text = values.get("text")

        if prompt:
            if text is None:
                raise ValueError("text is required when prompt is true")
        else:
            required_fields = [
                "current_weight",
                "current_height",
                "goal_weight",
                "meal_restriction",
                "diet_improvement",
                "allergies",
            ]
            if any(values.get(field) is None for field in required_fields):
                raise ValueError(
                    "Required fields for non-prompt search are current_weight, current_height, goal_weight,allergies, food_arround_me, meal_restriction, and diet_improvement"
                )
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": False,
                "current_weight": 70,
                "current_height": 170,
                "goal_weight": 75,
                "meal_restriction": ["paleo"],
                "diet_improvement": ["low-sodium", "high-protein"],
                "allergies": ["gluten", "peanuts"],
                "food_arround_me": ["chick-fil-a"],
                "history": [],
            }
        }

    def _to_json(self):
        return self.model_dump(exclude_none=True)


class NutritionalInfo(BaseModel):
    DISH: str
    SERVING_SIZE: str
    CALORIES: str
    FAT: str
    SAT_FAT: str
    TRANS_FAT: str
    CHOLESTEROL: str
    SODIUM: str
    CARBOHYDRATES: str
    FIBER: str
    SUGAR: str
    PROTEIN: str


class AddTextsRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, example=["text1", "text2"])
    metadatas: Optional[List[dict]] = None


class CountRequest(BaseModel):
    prompt: str = Field(...)


class AIResponse(BaseModel):
    menu_list: Optional[List[dict]] = Field(
        ...,
        example=[
            {"name": "item1", "description": "desc1"},
            {"name": "item2", "description": "desc2"},
        ],
    )
    message: Optional[str] = Field(..., example="This is a message from AI")

    def to_dict(self):
        return self.model_dump()


class AIFeedbackRequest(BaseModel):
    text: Optional[str] = Field(..., example="This is a feedback")
    rating: int = Field(..., example=5)
    user_id: Optional[str] = Field(..., example="user1")
    ai_response: Optional[AIResponse] = Field(
        ..., example={"menu_list": [], "message": "This is a message from AI"}
    )

    def to_dict(self):
        return self.model_dump()


class PromptLogger(BaseModel):
    c_datetime: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    prompt: str
    response: str

    def to_dict(self):
        return self.model_dump()


"============================== RESPONCE MODEL =================================="


class AddTextsResponce(BaseModel):
    ids: List[str] = Field(example=["id1", "id2"])


class EntityClassification(BaseModel):
    recommended: List[str]
    queries_or_faqs: Optional[List[str]] = None
    exclude: List[str]


class IndexMetadata(BaseModel):
    name: str
    entities: EntityClassification


class MetadataExtraction(BaseModel):
    indexes: List[IndexMetadata]
    query_expansion: Optional[str] = None


class DishInfo(BaseModel):
    restaurant_name: str
    dish: str
    serving_size: int
    calories: int
    fat: int
    sat_fat: int
    trans_fat: int
    cholesterol: int
    sodium: int
    carbohydrates: int
    fiber: int
    sugar: int
    protein: int


class OnlyMenuResponse(BaseModel):
    menus: Optional[List[DishInfo]] = None
    message_res: Optional[str] = None
    suggestions: Optional[List[str]] = None


class OnlyFAQResponse(BaseModel):
    details: str
    message_res: str
    suggestions: Optional[List[str]] = None


class BothFAQAndMenuResponse(BaseModel):
    details: str
    menus: List[DishInfo]
    message_res: str
    suggestions: Optional[List[str]] = None


class NoResponse(BaseModel):
    suggestions: List[str]
    message_res: str


class SearchResponse(BaseModel):
    result: Union[OnlyMenuResponse, NoResponse]
    time_taken_in_seconds: str
