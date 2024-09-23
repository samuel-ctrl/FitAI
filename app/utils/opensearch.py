from langchain_core.documents import Document
import re
from app.constants import IndexesEnum
from openai.types.chat import ChatCompletionMessageParam


def add_metadata(line, metadata, chunk_id):
    """
    Add metadata to a text line.

    Args:
        line (str): Text line.
        metadata (dict): Metadata.
        chunk_id (str): Chunk ID.

    Returns:
        Document: Document with added metadata.
    """
    return Document(
        id=chunk_id,
        page_content=line,
        metadata=metadata,
    )


def format_food_item(menu_dict) -> str:
    return (
        f"{menu_dict['provider']}'s {menu_dict['name']} for {menu_dict['category']} is {menu_dict['serving_size']} with "
        f"{menu_dict['calories']} calories. It contains {menu_dict['fat_g']}g of fat, "
        f"{menu_dict['sat_fat_g']}g of saturated fat, {menu_dict['cholesterol_mg']}mg of cholesterol, "
        f"{menu_dict['sodium_mg']}mg of sodium, {menu_dict['carbohydrates_g']}g of carbs, "
        f"{menu_dict['sugar_g']}g of sugar, {menu_dict['fiber_g']}g of fiber, and {menu_dict['protein_g']}g of protein."
    )


def get_chat_format(chat_history: dict, system_prompt) -> ChatCompletionMessageParam:
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        *chat_history.get("history", []),
        {"role": "user", "content": chat_history.get("text")},
    ]


def get_completion_format(chat_history: dict, system_prompt: str) -> str:
    formatted_history = [f"System prompt: {system_prompt}"]

    for message in chat_history.get("histrory", []):
        role = message.get("role")
        content = message.get("content")
        formatted_history.append(f"{role.capitalize()}: {content}")

    formatted_history.append(f"User preference: {chat_history.get('text', '')}")

    return "\n".join(formatted_history)


def get_combined_chunks(dataset):
    responses = dataset.get("responses")
    combined_menus_chunks = []
    info_chunks = []
    for response in responses:
        if response.get("status") == 200:
            index = response.get("hits", {}).get("hits", [])
            for docs in index:
                if docs.get("_index") == IndexesEnum.INDEX_OF_MENUS.value:
                    combined_menus_chunks.append(
                        docs.get("_source", {}).get("text", "")
                    )
                elif docs.get("_index") == IndexesEnum.INDEX_OF_FAQ.value:
                    info_chunks.append(
                        docs.get("_source", {}).get("text", ""),
                    )
    return combined_menus_chunks, info_chunks


def decode_unicode_emoji(text):
    """Decode Unicode-encoded emojis while preserving already decoded emojis."""
    # Define a regex pattern to find Unicode escape sequences
    pattern = re.compile(r"\\U[0-9A-Fa-f]{8}", re.DOTALL)

    def decode_match(match):
        """Decode individual Unicode escape sequences."""
        return match.group(0).encode().decode("unicode_escape")

    # Use regex to replace Unicode escape sequences with their actual emoji representations
    decoded_text = re.sub(pattern, decode_match, text)

    return decoded_text


def check_entities(extracted_indexes):
    return extracted_indexes.indexes and any(
        getattr(extracted_indexes.indexes[0].entities, attr, False)
        for attr in ["recommended", "queries_or_faqs", "exclude"]
    )
