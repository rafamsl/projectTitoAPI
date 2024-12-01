import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def render_prompt(form_data):
    main_prompt = "Your template prompt here"  # Replace with a database query or fixed string
    rendered_prompt = main_prompt.format(
        language=form_data.get('language', ''),
        character_name=form_data.get('character_name', ''),
        character_description=form_data.get('character_description', ''),
        story_goal=form_data.get('story_goal', '')
    )
    return rendered_prompt

def call_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )
        return {"ai_response": response['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}
