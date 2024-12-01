import openai
from config import OPENAI_API_KEY
from models import Prompt

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

def call_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        return {"ai_response": response['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}
