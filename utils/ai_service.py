import json
import re
import requests
from openai import OpenAI
import os

import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
from IPython.display import Markdown
import textwrap
import time
import logging
from flask import Flask
import anthropic
from typing import Any, Dict, List, Union

OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")
OPEN_AI_CHAT_MODEL = 'gpt-3.5-turbo'
OPEN_AI_VISION_MODEL = 'gpt-4o'

GOOGLE_AI_API_KEY = os.environ.get("GOOGLE_AI_API_KEY")
GEMINI_AI_CHAT_MODEL = 'gemini-1.5-flash-latest'
GEMINI_AI_VISION_MODEL = 'gemini-1.5-flash-latest'


ANTHROPIC_AI_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_AI_CHAT_MODEL = "claude-3-5-sonnet-20240620"

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")

# Initialize OpenAI
open_AI_client = OpenAI(
    api_key=OPEN_AI_KEY,
)

# Initialize Anthropics
anthropic_client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=ANTHROPIC_AI_API_KEY
)


# Set up logging
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_AI_API_KEY)


def get_ai_chat_response(prompt, ai_engine='gemini', ai_model=OPEN_AI_CHAT_MODEL, response_format="text", max_tokens=500, num_of_choices=1):
    if ai_engine == 'gemini':
        result = []
        while num_of_choices > 0:
            ai_response = get_gemini_response(
                prompt, response_format, max_tokens, num_of_choices)
            # if ai_response and is a dict, it means it's a json object
            if ai_response:
                result.extend(ai_response)
                num_of_choices -= len(ai_response)
            else:
                app.logger.info(
                    f"Unable to get response from Gemini AI chat, will try OpenAI.")
                return get_open_ai_response(prompt, ai_model, response_format, max_tokens, num_of_choices)
        return result
    else:
        return get_open_ai_response(prompt, ai_model, response_format, max_tokens, num_of_choices)


def get_open_ai_response(prompt, ai_model=OPEN_AI_CHAT_MODEL, response_format="text", max_tokens=500, num_of_choices=1) -> Union[List[str], List[dict]]:
    result = []
    try:
        ai_response = open_AI_client.chat.completions.create(
            model=ai_model,
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            response_format={"type": response_format},
            max_tokens=max_tokens,
            n=num_of_choices,
        )
        for choice in ai_response.choices:
            ai_response_text = choice.message.content
            if response_format == "json_object":
                ai_response_json = json.loads(ai_response_text)
                if isinstance(ai_response_json, dict):
                    result.append(ai_response_json)
            else:
                result.append(ai_response_text)
        return result if result else [{}]
    except Exception as e:
        app.logger.error(
            f"Unable to get response from OpenAI chat will try Claude. error:{e}")
        return get_claude_response(prompt, response_format, max_tokens, num_of_choices)


def get_claude_response(prompt, response_format="text", max_tokens=500, num_of_choices=1) -> Union[List[str], List[dict]]:
    try:
        message = anthropic_client.messages.create(
            model=ANTHROPIC_AI_CHAT_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        if response_format == "json_object":
            response = json.loads(message.content[0].text)
            if isinstance(response, dict):
                return [response]
        else:
            response = message.content[0].text
            return [response]
    except Exception as e:
        app.logger.error(
            f"Unable to get response from Anthropics chat. error:{e}")
    return [{}]


def get_gemini_response(prompt, response_format="text", max_tokens=500, num_of_choices=1) -> Union[List[str], List[dict]]:
    result = []
    model = genai.GenerativeModel(GEMINI_AI_CHAT_MODEL)
    generation_config = genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0,
        top_k=1,
        response_mime_type='application/json' if response_format == "json_object" else 'text/plain',
    )
    retries = 0
    ai_response = None
    while retries < 1:
        try:
            ai_response = model.generate_content(
                prompt, generation_config=generation_config)
            ai_response_candidates = [
                to_markdown(candidate.content.parts[0].text).data for candidate in ai_response.candidates
            ]
            for ai_response_text in ai_response_candidates:
                ai_response_text = ai_response_text.replace('\n', '').replace(
                    '```', '').replace('>', '').replace('JSON', '').replace('json', '').replace('python', '')
                if response_format == "json_object":
                    ai_response_json = json.loads(ai_response_text)
                    if isinstance(ai_response_json, dict):
                        result.append(ai_response_json)
                    else:
                        app.logger.info(
                            f"Unable to parse json from Gemini AI response. response:{ai_response_json}")
                        continue
                else:
                    result.append(ai_response_text)
            return result
        except json.JSONDecodeError as e:
            app.logger.warning(
                f"Unable to parse json from Gemini AI response will retry. response:{ai_response_text}, error:{e}")
        except Exception as e:
            if type(e) == InternalServerError and e.code >= 500:
                app.logger.error(
                    f"Server error: Unable to generate content with Gemini AI, will retry. error:{e}")
                retries += 1
                time.sleep(2 ** retries)
            else:
                app.logger.error(
                    f"Client error: Unable to generate content with Gemini AI. error:{e}, response:{ai_response}, prompt: {prompt}")
                retries += 1
                time.sleep(2 ** retries)
    return []


def get_perplexity_response(prompt: str) -> Dict[str, Any]:
    """
    Send a prompt to Perplexity AI and get the response as a JSON object.

    Args:
        prompt (str): The prompt to send to Perplexity AI.

    Returns:
        Dict[str, Any]: The parsed JSON response from Perplexity AI.
    """
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}"
    }

    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in cybersecurity and risk assessment. Provide your responses in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    # Parse the content as JSON
   # Extract the JSON part from the content
    content = response_data["choices"][0]["message"]["content"]
    json_match = re.search(r'\{.*\}', content, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}
    else:
        print("No JSON object found in the response")
        return {}


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
