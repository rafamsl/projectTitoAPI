from flask import Flask, request, jsonify
from models import db, Prompt, User, Story
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from utils import render_prompt, call_openai
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'name' not in data:
        return jsonify({"error": "Email, name, and password are required"}), 400

    email = data['email']
    name = data['name']
    password = data['password']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, name=name, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

# Add a new prompt
@app.route('/add_prompt', methods=['POST'])
def add_prompt():
    data = request.get_json()
    if not data or 'name' not in data or 'category' not in data or 'content' not in data:
        return jsonify({"error": "Name, category, and content are required"}), 400

    new_prompt = Prompt(name=data['name'], category=data['category'], content=data['content'])
    db.session.add(new_prompt)
    db.session.commit()
    return jsonify({"message": "Prompt added successfully!"}), 201

# Get all prompts
@app.route('/prompts', methods=['GET'])
def get_prompts():
    prompts = Prompt.query.all()
    prompts_data = [{"id": prompt.id, "name": prompt.name, "category": prompt.category, "content": prompt.content}
                    for prompt in prompts]
    return jsonify(prompts_data), 200

# Route to delete a prompt by ID
@app.route('/delete_prompt/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    prompt_to_delete = Prompt.query.get(prompt_id)
    if not prompt_to_delete:
        return jsonify({"error": "Prompt not found"}), 404

    db.session.delete(prompt_to_delete)
    db.session.commit()
    return jsonify({"message": f"Prompt with ID {prompt_id} deleted successfully"}), 200

# Route to delete a story by ID
@app.route('/delete_story/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    story_to_delete = Story.query.get(story_id)
    if not story_to_delete:
        return jsonify({"error": "Story not found"}), 404

    db.session.delete(story_to_delete)
    db.session.commit()
    return jsonify({"message": f"Story with ID {story_id} deleted successfully"}), 200

# Submit a prompt and create a story
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    form_data = {
        'language': data.get('language'),
        'character_name': data.get('character_name'),
        'character_description': data.get('character_description'),
        'story_goal': data.get('story_goal'),
    }

    rendered_prompt = render_prompt(form_data)
    openai_result = call_openai(rendered_prompt)

    if 'error' in openai_result:
        return jsonify({"error": openai_result['error']}), 500

    ai_response_str = openai_result['ai_response']
    estimated_cost = openai_result['estimated_cost']

    try:
        ai_response_json = json.loads(ai_response_str)
    except json.JSONDecodeError:
        return jsonify({"error": "Unable to parse AI response as JSON."}), 500

    story_title = ai_response_json.get("Title", "Untitled Story")
    user_id = 1  # Hardcoded user ID

    new_story = Story(
        user_id=user_id,
        title=story_title,
        content=ai_response_json,
        created_date=datetime.utcnow()
    )
    db.session.add(new_story)
    db.session.commit()

    return jsonify({
        "story_id": new_story.id,
        "title": new_story.title,
        "content": new_story.content,
        "estimated_cost": estimated_cost
    }), 201

# Route to get all stories
@app.route('/stories', methods=['GET'])
def get_stories():
    stories = Story.query.all()
    stories_data = [
        {
            "id": story.id,
            "user_id": story.user_id,
            "title": story.title,
            "content": story.content,
            "created_date": story.created_date.isoformat()
        } for story in stories
    ]
    return jsonify(stories_data), 200

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = [{"id": user.id, "email": user.email, "name": user.name} for user in users]
    return jsonify(users_data), 200

if __name__ == '__main__':
    app.run(debug=True)
