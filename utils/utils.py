import openai
from config import OPENAI_API_KEY
from models import Prompt
import os
import json

openai.api_key = OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def render_prompt(form_data):
    main_prompt = Prompt.query.filter_by(name="main_prompt").first().content
    rendered_prompt = main_prompt.format(
        language=form_data.get('language', ''),
        character_name=form_data.get('character_name', ''),
        character_description=form_data.get('character_description', ''),
        story_goal=form_data.get('story_goal', '')
    )
    return rendered_prompt

def calculate_cost(prompt_tokens, completion_tokens):
    # Convert rates from per million tokens to per token
    input_rate = 0.150 / 1_000_000  # $0.150 per 1M tokens
    output_rate = 0.600 / 1_000_000  # $0.600 per 1M tokens
    
    cost = (prompt_tokens * input_rate) + (completion_tokens * output_rate)
    return round(cost, 6)  # Round to 6 decimal places

def call_openai(prompt):
    if os.getenv('IS_LOCAL') == 'true':
        mock_response = {
            "Title": "Tufo, a Raposa Divertida",
            "1": "Era uma vez uma raposa chamada Tufo.",
            "2": "Tufo era muito divertida, com seu pelo laranja brilhante e um rabo fofo.",
            "3": "Ela adorava correr pelo bosque, pulando de alegria e fazendo acrobacias.",
            "4": "Um dia, enquanto brincava, Tufo viu um esquilo triste em uma árvore.",
            "5": "O esquilo se chamava Pipo e estava sozinho, sem amigos para brincar.",
            "6": "Tufo decidiu se aproximar e perguntou se Pipo queria brincar com ela.",
            "7": "Pipo sorriu e desceu da árvore, feliz por ter uma nova amiga.",
            "8": "Juntos, Tufo e Pipo correram, pularam e se divertiram como nunca.",
            "9": "No final do dia, eles ficaram cansados, mas muito felizes por terem se encontrado.",
            "10": "Tufo aprendeu que fazer amigos é uma das melhores coisas do mundo."
        }
        return {"ai_response": json.dumps(mock_response), "estimated_cost": 0.00017}
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
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
