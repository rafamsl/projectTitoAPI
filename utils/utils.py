import openai
from config import OPENAI_API_KEY, STABILITY_API_KEY
from models import Prompt
import os
import json
import requests

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def render_prompt(form_data):
    main_prompt = Prompt.query.filter_by(name="main_prompt").first().content
    # Use Template string substitution for specific placeholders only
    replacements = {
        '{language}': form_data.get('language', ''),
        '{character_name}': form_data.get('character_name', ''),
        '{character_description}': form_data.get('character_description', ''),
        '{story_goal}': form_data.get('story_goal', '')
    }
    
    rendered_prompt = main_prompt
    for key, value in replacements.items():
        rendered_prompt = rendered_prompt.replace(key, value)
    
    return rendered_prompt

def calculate_cost(prompt_tokens, completion_tokens):
    # Convert rates from per million tokens to per token
    input_rate = 0.150 / 1_000_000  # $0.150 per 1M tokens
    output_rate = 0.600 / 1_000_000  # $0.600 per 1M tokens
    
    cost = (prompt_tokens * input_rate) + (completion_tokens * output_rate)
    return round(cost, 6)  # Round to 6 decimal places

def call_stability(host,params,files = None):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }

    if files is None:
        files = {}

    # Encode parameters
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files)==0:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host}...")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def call_openai(prompt,json=True):
    if os.getenv('IS_LOCAL') == 'true':
        mock_response = {
            "scene_1": {
                "quote": "In a bright green forest, there lived a happy fox named Ludo. Ludo had a fluffy orange tail and sparkling eyes that twinkled like stars.",
                "description": "A vivid, lush green forest with tall trees and beams of sunlight streaming through the leaves. Ludo, a bright orange fox with a fluffy tail and twinkling eyes, stands in the middle, smiling cheerfully. Surrounding him are colorful plants, creating a vibrant and peaceful atmosphere."
            },
            "scene_2": {
                "quote": "Every day, Ludo would explore the forest, hopping from tree to tree. He loved to chase butterflies and smell the colorful flowers. But sometimes, Ludo felt a little lonely as he played all by himself.",
                "description": "Ludo is depicted hopping between tall trees, with golden butterflies fluttering around him. A variety of colorful flowers bloom in the foreground, and Ludo sniffs one of them with a content expression. In the background, a moment shows him sitting alone with a wistful look, capturing his loneliness."
            },
            "scene_3": {
                "quote": "One sunny morning, Ludo decided to find some friends to play with. He scampered through the forest, calling out to the other animals. Soon, he met a cheerful rabbit named Bella and a playful squirrel named Sammy.",
                "description": "A sunlit forest with Ludo scampering joyfully through, calling out. Bella, a white rabbit with long ears, appears smiling near a patch of clover. Sammy, a brown squirrel with a bushy tail, climbs down a tree to greet him. The three animals are shown meeting for the first time, their faces glowing with excitement."
            },
            "scene_4": {
                "quote": "Together, they laughed and danced, sharing joy in their games. From that day on, Ludo, Bella, and Sammy played together, making their friendship grow stronger.",
                "description": "Ludo, Bella, and Sammy are shown playing together in a clearing surrounded by trees. Ludo leaps with joy, Bella hops in delight, and Sammy scurries around playfully. Their laughter fills the air as they chase each other, showcasing their blossoming friendship."
            }
        }
        return {"ai_response": json.dumps(mock_response), "estimated_cost": 0.00017}
        
    if json:
        response_format={"type": "json_object"}
    else:
        response_format={"type": "text"}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format=response_format
        )
        # Calculate cost from token usage
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        estimated_cost = calculate_cost(prompt_tokens, completion_tokens)
        
        return {
            'ai_response': response.choices[0].message.content,
            'estimated_cost': estimated_cost
        }
    except Exception as e:
        return {"error": str(e)}
    
def render_prompt_for_cover_image(story_id):
    cover_image_prompt = Prompt.query.filter_by(name="cover_image").first().content
    story = Prompt.query.filter_by(id=story_id).first().content

    replacements = {
        '{story}' : story
    }
    rendered_prompt = cover_image_prompt
    for key, value in replacements.items():
        rendered_prompt = rendered_prompt.replace(key, value)
    return rendered_prompt

def generate_cover_image(prompt):
    host = f"https://api.stability.ai/v2beta/stable-image/generate/core"
    aspect_ratio = "21:9" #@param ["21:9", "16:9", "3:2", "5:4", "1:1", "4:5", "2:3", "9:16", "9:21"]
    seed = 0 #@param {type:"integer"}
    output_format = "jpeg" #@param ["webp", "jpeg", "png"]

    params = {
    "prompt" : prompt,
    "aspect_ratio" : aspect_ratio,
        "seed" : seed,
        "output_format": output_format
    }

    response = call_stability(host,params)

    output_image = response.content
    finish_reason = response.headers.get("finish-reason")
    seed = response.headers.get("seed")

    print({
        "output_image": output_image,
        "finish_reason": finish_reason,
        "seed": seed
    })

    return

def generate_scene_images(data):
    pass   