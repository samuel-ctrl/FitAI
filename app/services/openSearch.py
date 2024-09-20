import os
import re
import shutil
import uuid
import json
import random
from ast import literal_eval
from fastapi import UploadFile, HTTPException
import openai
import pandas as pd
from logging import error
from typing import List

from pydantic import BaseModel
from app.logger import log_to_csv
from app.main import app
from app.constants import (
    PROMPT_CHAT_TEMPLATE_NO_MENU_AND_INFO,
    PROMPT_CHAT_TEMPLATE_WITH_MENU_AND_INFO,
    PROMPT_CHAT_TEMPLATE_WITH_MENU,
    PROMPT_CHAT_TEMPLATE_WITH_INFO,
    PROMPT_TEMPLATE_EXTRACT_METADATA_FROM_USER,
    NO_RESPONCE_MESSAGE,
    AvailableRestaurants,
    FrequencyPenalty,
    IndexesEnum,
    MaxTokens,
    NucleusSampling,
    PresencePenalty,
    Temperature,
    allowed_file_formats_without_astrics,
)
from langchain_community.vectorstores import OpenSearchVectorSearch
from app.models.openSeachModel import (
    BothFAQAndMenuResponse,
    NoResponse,
    OnlyFAQResponse,
    OnlyMenuResponse,
    MetadataExtraction,
    SearchRequest,
)
from app.utils.opensearch import (
    add_metadata,
    check_entities,
    format_food_item,
    get_combined_chunks,
    get_chat_format,
)
from openai.types.chat import ChatCompletionMessageParam


def handle_response(response):
    try:
        # response = decode_unicode_emoji(response)
        return response.json()
    except json.JSONDecodeError:
        dict_pattern = r"\{[^{}]+\}"
        fixed_dict = re.findall(dict_pattern, response)
        fixed_dict = [literal_eval(item) for item in fixed_dict]
        if "message_res" in response:
            valid_message = response.replace('"', "'")
            valid_message = valid_message.split("message_res':")[1]
            valid_message = valid_message.strip()
            valid_message = (
                valid_message[1:-1] if valid_message[0] == "'" else valid_message
            )
            valid_message = (
                valid_message[:-1] if valid_message[-1] == "'" else valid_message
            )
            message_res = valid_message.replace("}", "").replace("\n", "")
        if not fixed_dict and not message_res:
            return {"message_res": random.choice(NO_RESPONCE_MESSAGE)}
        return {"menus": fixed_dict, "message_res": message_res}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message_res": random.choice(NO_RESPONCE_MESSAGE)}


# response.choices[0].message.content


async def _get_llm_response(
    chat: ChatCompletionMessageParam,
    response_format: BaseModel,
    temperature: float,
    max_tokens: int,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
):
    try:
        completion = await app.llm.beta.chat.completions.parse(
            model=app.settings_instance.LLM_MODEL_NAME,
            temperature=temperature,
            messages=chat,
            max_tokens=max_tokens,
            response_format=response_format,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        message = completion.choices[0].message

        if message.refusal:
            return {
                "error": "REFUSAL",
                "detail": "Refusal from LLM",
            }
        elif message.parsed:
            log_to_csv(
                prompt=chat,
                response=message.parsed.model_dump(),
            )
            # llm_res = re.sub(
            #     r"^[^{]*", "", message.parsed.replace("\n", "").replace("  ", "")
            # )
            return message.parsed

    except Exception as e:
        if e is openai.LengthFinishReasonError:
            raise {
                "error": "TOO_MANY_TOKENS",
                "detail": "Too many tokens",
            }
        else:
            error(e)
            raise {
                "error": "UNKNOWN_ERROR",
                "detail": str(e),
            }


def _default_script_scroling_search(
    vector, cluster: MetadataExtraction, k=4, min_score=0, space_type="innerproduct"
):
    query = []
    for index in cluster.indexes:
        query.append({"index": index.name})
        query.append(
            {
                "_source": {"excludes": ["vector_field"]},
                "size": k,
                "min_score": min_score,
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {"match": {"metadata.entities": entity}}
                                    for entity in index.entities.recommended or []
                                ],
                                "should": [
                                    {"match": {"metadata.entities": entity}}
                                    for entity in index.entities.queries_or_faqs or []
                                ],
                                "must_not": [
                                    {"match_phrase": {"metadata.entities": entity}}
                                    for entity in index.entities.exclude or []
                                ],
                            }
                        },
                        "script": {
                            "lang": "knn",
                            "source": "knn_score",
                            "params": {
                                "field": "vector_field",
                                "query_value": vector,
                                "space_type": space_type,
                            },
                        },
                    }
                },
            }
        )
    return query


async def _extraction_for_user_prompt(user_chat) -> MetadataExtraction:
    chat = get_chat_format(
        chat_history=user_chat,
        system_prompt=PROMPT_TEMPLATE_EXTRACT_METADATA_FROM_USER.format(
            MENU_INDEX=IndexesEnum.INDEX_OF_MENUS.value,
            INFO_INDEX=IndexesEnum.INDEX_OF_FAQ.value,
            AVAILABLE_RES=", ".join(
                [
                    AvailableRestaurants.CHICK_FIL_A.value,
                ]
            ),
        ),
    )

    return await _get_llm_response(
        chat,
        MetadataExtraction,
        temperature=Temperature.MEDIUM_TEMPERATURE.value,
        max_tokens=MaxTokens.LOW_MAX_TOKENS.value,
        top_p=NucleusSampling.LOW_NUCLEUS_SAMPLING.value,
        frequency_penalty=FrequencyPenalty.LOW_FREQUENCY_PENALTY.value,
        presence_penalty=PresencePenalty.HIGH_PRESENCE_PENALTY.value,
    )


def _extraction_for_custom_prompt(request: SearchRequest) -> MetadataExtraction:
    indexes = [
        {
            "name": IndexesEnum.INDEX_OF_MENUS,
            "entities": {
                "recommended": [
                    *request.meal_restriction,
                    *request.diet_improvement,
                    *request.food_arround_me,
                ],
                "exclude": [*request.allergies],
            },
        }
    ]
    return MetadataExtraction(indexes=indexes)


class OpenSearchService:
    def __init__(self, openseach_client: OpenSearchVectorSearch):
        self.vdb_handler = openseach_client

    @staticmethod
    def read_jsonl_file_with_metadata(file_path):
        try:
            chunks = []
            with open(file_path, "r") as file:
                for i, line in enumerate(file):
                    chunk_with_metadata = add_metadata(
                        line=line.strip(), metadata={}, chunk_id=f"{i}-{uuid.uuid4()}"
                    )
                    chunks.append(chunk_with_metadata)
            return chunks

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read file: {str(e)}"
            )

    @staticmethod
    def read_csv_file_with_metadata(file_path):
        try:
            chunks = []
            df = pd.read_csv(file_path)

            for i, row in df.iterrows():
                # Convert the 'entities' column from string to list using ast.literal_eval
                row["entities"] = literal_eval(row["entities"])

                # Generate the formatted description
                formatted_item = format_food_item(row)

                # Create the chunk with both formatted description and entities
                chunk_with_metadata = add_metadata(
                    line=formatted_item,
                    metadata={"entities": row.entities},
                    chunk_id=f"{i}-{uuid.uuid4()}",
                )
                chunks.append(chunk_with_metadata)
            return chunks
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read file: {str(e)}"
            )

    def load_documents(self, folder_path):
        chunks = self.read_csv_file_with_metadata(folder_path)
        if not chunks:
            raise ValueError("No chunks loaded.")
        return chunks

    async def upload_to_opensearch(self, folder_path, index_name):
        chunks = self.load_documents(folder_path)
        await self.vdb_handler.aadd_documents(documents=chunks, index_name=index_name)

    async def save_uploaded_file(self, files: List[UploadFile]):
        folder_path = str(uuid.uuid4())
        os.makedirs(folder_path)

        for file in files:
            if not file.filename or not file.filename.endswith(
                tuple(allowed_file_formats_without_astrics)
            ):
                shutil.rmtree(folder_path)
                raise ValueError(f"Invalid file type: {file.filename}")

            file_path = os.path.join(str(folder_path), str(file.filename))
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

        return folder_path, file.filename

    async def search(
        self,
        request: SearchRequest,
        prompt: str,
    ):
        user_chat = {"history": request.history, "text": prompt}
        if request.prompt:
            extracted_indexes = await _extraction_for_user_prompt(user_chat)
        else:
            extracted_indexes = _extraction_for_custom_prompt(request)

        available_menus, available_infos = [], []
        if check_entities(extracted_indexes):
            user_chat["text"] = extracted_indexes.query_expansion or user_chat["text"]
            embedding = app.embedding_model_instance.embed_query(user_chat["text"])
            search_query = _default_script_scroling_search(
                k=len(extracted_indexes.indexes) * 10,
                vector=embedding,
                cluster=extracted_indexes,
                min_score=1,
            )

            dataset = await self.vdb_handler.async_client.msearch(body=search_query)
            available_menus, available_infos = get_combined_chunks(dataset)
        (
            system_prompt,
            response_format,
            temperature,
            max_tokens,
            top_p,
            frequency_penalty,
            presence_penalty,
        ) = (
            (
                PROMPT_CHAT_TEMPLATE_WITH_MENU_AND_INFO,
                BothFAQAndMenuResponse,
                Temperature.LOW_TEMPERATURE.value,
                MaxTokens.HIGH_MAX_TOKENS.value,
                NucleusSampling.LOW_NUCLEUS_SAMPLING.value,
                FrequencyPenalty.HIGH_FREQUENCY_PENALTY.value,
                PresencePenalty.HIGH_PRESENCE_PENALTY.value,
            )
            if available_menus and available_infos
            else (
                (
                    PROMPT_CHAT_TEMPLATE_WITH_MENU,
                    OnlyMenuResponse,
                    Temperature.LOW_TEMPERATURE.value,
                    MaxTokens.HIGH_MAX_TOKENS.value,
                    NucleusSampling.LOW_NUCLEUS_SAMPLING.value,
                    FrequencyPenalty.HIGH_FREQUENCY_PENALTY.value,
                    PresencePenalty.HIGH_PRESENCE_PENALTY.value,
                )
                if available_menus
                else (
                    (
                        PROMPT_CHAT_TEMPLATE_WITH_INFO,
                        OnlyFAQResponse,
                        Temperature.MEDIUM_TEMPERATURE.value,
                        MaxTokens.LOW_MAX_TOKENS.value,
                        NucleusSampling.LOW_NUCLEUS_SAMPLING.value,
                        FrequencyPenalty.HIGH_FREQUENCY_PENALTY.value,
                        PresencePenalty.MID_PRESENCE_PENALTY.value,
                    )
                    if available_infos
                    else (
                        PROMPT_CHAT_TEMPLATE_NO_MENU_AND_INFO,
                        NoResponse,
                        Temperature.HIGH_TEMPERATURE.value,
                        MaxTokens.LOW_MAX_TOKENS.value,
                        NucleusSampling.LOW_NUCLEUS_SAMPLING.value,
                        FrequencyPenalty.HIGH_FREQUENCY_PENALTY.value,
                        PresencePenalty.LOW_PRESENCE_PENALTY.value,
                    )
                )
            )
        )
        chat = get_chat_format(
            chat_history=user_chat,
            system_prompt=system_prompt.format(
                AVAILABLE_MENUS="\n-".join(available_menus),
                AVAILABLE_INFOS="\n-".join(available_infos),
            ),
        )
        final_llm_res = await _get_llm_response(
            chat,
            response_format,
            temperature,
            max_tokens,
            top_p,
            frequency_penalty,
            presence_penalty,
        )
        return final_llm_res
