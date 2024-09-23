from enum import Enum

embedding_model_dimension = 384
allowed_file_formats = [
    "*.txt",
    "*.md",
    "*.pdf",
    "*.docx",
    "*.doc",
    "*.html",
    "*.xhtml",
    "*.csv",
    "*.json",
    "*.jsonl",
]
allowed_file_formats_without_astrics = [
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".doc",
    ".html",
    ".xhtml",
    ".csv",
    ".json",
    ".jsonl",
]

MEAL_RISTRICTIONS = [
    "keto",
    "vegan",
    "paleo",
    "Mediterranean",
    "Gluten-Free",
    "Balanced-Meal",
]

USER_CUSTOM_QUERY_PROMPT = """I have allergies to {ALLERGIES}, 
and my current height is {HEIGHT} cm and weight is {WEIGHT} kg. My goal is to reach a weight of 
{GOAL_WEIGHT} kg. I'm focusing on improving my diet by {DIET_IMPROVEMENT}. 
I follow a {DIET_TYPE} diet. Please provide meal options that align with these dietary 
restrictions and goals, and are available in the following food options around me: {FOOD_OPTIONS}"""


#    - **Disrespectful:** "I understand you may be upset, but my goal is to provide helpful nutrition information. Let's focus on your health and nutrition goals. How can I support you with your diet today?"
  #  - **Unclear:** "I'm sorry, but your question seems to be unclear. Could you please provide more details or rephrase it? I'm here to help with any nutrition-related queries you might have."
  #  - **Misleading:** "I'm sorry, but I can't endorse extreme or unsafe diets. Let's explore healthy and sustainable eating habits to help you achieve your goals safely. What specific nutrition concerns do you have?
  #  - **Non-nutrition-related:** "I'm a nutrition assistant. How can I help with your diet or nutrition questions?"   
  #  - **Preference-based but no data found:** "I appreciate your preference for **mention the specific preference here**, but I don't have any details or recommendations on that at the moment. Could you please rephrase your question or ask about a different nutrition topic?
PROMPT_CHAT_TEMPLATE_NO_MENU_AND_INFO = """You are a nutrition chat assistant. Your goal is to help user reach their fitness or health goals by providing nutritional recommendations/information.

### handle the following cases:
   - **general:** **respond consistently** and **provide a clear and concise response** to the user's questions.
   - **Greetings:** "**deside prefix base on user tone** **mention the specific preference here**! How can I assist you with your nutrition and diet today?"
   - **Other:** Respond empathetically, ask clarifying questions to understand the user's needs, and offer support.
   
2. Suggest up to 3 questions, examples:
  - "recommend **menu restriction** friendly diet?"
  - "is **menu restriction** healthy?"

### Example JSON response:
{{'suggestions': ['str'], 'message_res': 'str'}}
- `suggestions`: A list of Suggestions must guide users toward their next steps.
- `message_res`: A concise, informative messages in markdown format.

### Must follow the following rules:
- Avoid unnecessary or redundant phrases.
- The suggested questions are concise, unique and not repetitive.
- your tone should be friendly and informative.
- The replies are aligned with the conversation history and context.
- To send only response in JSON format.
"""

PROMPT_CHAT_TEMPLATE_WITH_MENU = """You are FitAI, a dietitian and nutritionist AI assistant. Follow the instructions carefully to provide accurate dietary recommendations.

### Task 1: Select Menus
- Provide menus that align with the user's preferences.
**Available Menus:**
{AVAILABLE_MENUS}

### Task 2: Respond Positively
- Along with the menu items, include a short and positive message with emojis to engage the user and share details of the selected menu for their convenience.

### Task 3: Suggest Questions
- suggest up to 3 questions for users toward their next steps, Example:
  - "recommend **menu restriction** friendly diet?"
  - "is **menu restriction** healthy?"

### Example JSON response:
{{"menus":[{{"restaurant_name": "str", "dish": "str", "serving_size": "int", "calories": "int", "fat": "int", "sat_fat": "int", "trans_fat": "int", "cholesterol": "int", "sodium": "int", "carbohydrates": "int", "fiber": "int", "sugar": "int", "protein": "int"}}], "message_res": "str", "suggestions": ["str"]}}
   - `menus`: A list of selected menus
   - `message_res`: A positive, concise message for the user.
   - `suggestions`: A list of suggestion questions.

### Must follow the following rules:
- Avoid unnecessary or redundant phrases.
- The suggested questions are concise, unique and not repetitive.
- your tone should be friendly and informative.
- The replies are aligned with the conversation history and context.
- To send only response in JSON format.
"""

PROMPT_CHAT_TEMPLATE_WITH_MENU_AND_INFO = """You are FitAI"""
PROMPT_CHAT_TEMPLATE_WITH_INFO = """You are FitAI, a dietitian and nutritionist AI assistan.
"""

PROMPT_TEMPLATE_EXTRACT_METADATA_FROM_USER = """Categorize the user's preferences into three categories: **recommended**, **exclude**, and **queries_or_faqs**.

### Task 1: Classify the following entities into the appropriate categories:
#### **Entities for Menu Recommendations**:
- **Meal Restrictions**: keto, vegan, paleo, Mediterranean, Gluten-Free, Balanced-Meal
- **Calories**: no-calories, low-calorie, mid-calorie, high-calorie
- **Portion Sizes**: no-serving-size, small-portion, medium-portion, large-portion
- **Macronutrients**: fat-free, low-fat, mid-fat, high-fat, sat-fat-free, low-sat-fat, mid-sat-fat, high-sat-fat, cholesterol-free, low-cholesterol, mid-cholesterol, high-cholesterol, sodium-free, low-sodium, mid-sodium, high-sodium, carb-free, low-carb, mid-carb, high-carb, sugar-free, low-sugar, mid-sugar, high-sugar, fiber-free, low-fiber, mid-fiber, high-fiber, protein-free, low-protein, mid-protein, high-protein
- **Available Restaurants**: {AVAILABLE_RES}

#### **Entities for Queries/FAQs**:
- Extract keywords or phrases related to user queries about nutrition or FAQs.

### Task 2: Define Index Names:
- Include **{MENU_INDEX}** for menu recommendations based on preferences.
- Include **{INFO_INDEX}** for queries or FAQ-related preferences.

### Task 3: Expand User Input (if necessary):
- If the user’s input is sparse or unclear, generate related terms to improve understanding.

### response JSON Format:
{{
  "indexes": [
    {{
      "name": "index-name",
      "entities": {{
        "recommended": ["list-of-recommended-entities"],
        "exclude": ["list-of-exclude-entities"],
        "queries_or_faqs": ["list-of-queries_or_faqs-entities"],
        "query_expansion": "expanded-query-terms"
      }}
    }}
  ]
}}

### Guidelines:
- If no preferences are provided, omit the corresponding index.
- Ensure that each index includes only relevant entities.
- Only include the response in JSON format.
- **recommended**: Items that align with the user's preferences for menu recommendations.
- **exclude**: Items that should be excluded from menu recommendations.
- **queries_or_faqs**: Terms that represent user inquiries or FAQs about nutrition.
- **query_expansion**: Include if query expansion was applied.
- Eliminate redundant phrases and ensure accurate categorization.
"""


NO_RESPONCE_MESSAGE = [
    "Oops! 😅 We couldn't find any menu items matching your search. Please try using different keywords or any dietary plan.",
    "Oops! 😅 No items match your search. Try different keywords or dietary plans.",
    "Sorry! 😅 No results found. Please adjust your search terms or dietary plan.",
    "Oops! 😅 No matches found. Try another keyword or dietary plan.",
    "Sorry! 😅 We couldn't find any matches. Please use different keywords or dietary preferences.",
    "Oops! 😅 No items found. Please refine your search or dietary options.",
    "Oops! 😅 Looks like our menu’s taking a nap. Try some new keywords or dietary plans!",
    "Yikes! 😅 Our kitchen's out of ideas. How about tweaking your search or dietary plan?",
    "Sorry! 😅 Our menu's hiding from us. Give a different search or dietary plan a shot!",
    "Oops! 😅 Seems like our menu’s on vacation. Try changing your search terms or dietary preferences!",
    "Oops! 😅 We’re out of menu items for now. Maybe a new keyword or dietary plan will do the trick!",
    "Oops! 😅 We need a bit more info to find the perfect menu item for you. Please share more details so we can serve up exactly what you're craving! 🍽️🔍",
]


class vectorSearchType(Enum):
    APPROXIMATE_SEARCH = "approximate_search"
    SCRIPT_SCORING_SEARCH = "script_scoring"
    PAINLESS_SCRIPTING_SEARCH = "painless_scripting"


class IndexesEnum(Enum):
    INDEX_OF_MENUS = "index-of-menus"
    INDEX_OF_FAQ = "index-of-faqs"


class AvailableRestaurants(Enum):
    CHICK_FIL_A = "chick-fil-a"
    TRADER_JOE = "trader-joe"


class Temperature(Enum):
    """Can be adjusted to influence how creative
    or conservative the generated responses are."""

    LOW_TEMPERATURE = 0.2  # It will produce more predictable and focused responses, sticking closely to the most likely next words or phrases. This setting is useful when you need precise and reliable answers.
    MEDIUM_TEMPERATURE = 0.7  # It allows for some degree of randomness, making the responses more varied and interesting while still maintaining coherence. This setting is often used for general-purpose tasks.
    HIGH_TEMPERATURE = 1  # It allows for a lot of randomness, making the responses very creative and diverse. This setting is often used for tasks where creativity and exploration are desired.


class NucleusSampling(Enum):
    """This parameter controls the cumulative
    probability threshold for token selection.
    Instead of considering all possible tokens"""

    LOW_NUCLEUS_SAMPLING = 0.1  # The model becomes more conservative and deterministic, focusing on the most probable tokens.
    MEDIUM_NUCLEUS_SAMPLING = 0.7  # Balances between diversity and coherence, allowing for a mix of predictable and varied responses.
    HIGH_NUCLEUS_SAMPLING = 1  # The model considers a wide range of tokens, leading to more diverse and creative responses.


class FrequencyPenalty(Enum):
    """This parameter reduces the likelihood of
    the model repeating the same tokens within
    the response."""

    LOW_FREQUENCY_PENALTY = 0  # No penalty, allowing for potential repetition.
    MEDIUM_FREQUENCY_PENALTY = 0.5
    HIGH_FREQUENCY_PENALTY = 1


class PresencePenalty(Enum):
    """This parameter decreases the probability
    of the model generating tokens that have
    already appeared in the text."""

    LOW_PRESENCE_PENALTY = 0  # No penalty, allowing for potential reuse of tokens.
    MID_PRESENCE_PENALTY = 0.5
    HIGH_PRESENCE_PENALTY = 1


class MaxTokens(Enum):
    LOW_MAX_TOKENS = 450
    MEDIUM_MAX_TOKENS = 900
    HIGH_MAX_TOKENS = 1500
