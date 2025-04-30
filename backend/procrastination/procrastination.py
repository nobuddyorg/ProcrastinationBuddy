import requests
from .db import get_db, add_task_to_db, get_tasks_from_db

def procrastinate(url):
    favorites = [
        "watch baby animal videos on Youtube", 
        "Count the number of tiles in the bathroom", 
        "Organize your pens by color and size", 
        "Reversing all your stacks of plates and bowls to ensure even wear", 
        "Write a poem about the dust bunnies under your bed"
    ]
    
    prompt = f"""You are 'Procrastination Buddy', a creative generator for procrastination tasks.

Follow these rules:
- It can be casual or complicated, but it should be fun and light-hearted.
- Prefer short over long tasks. 
- Don't give why they should do it, no explanations, just the task.
- Only generate ONE task. 

Consider my favorites: {', '.join(favorites)} 
"""

    response = requests.post(
        url,
        json={
            'model': 'mistral:instruct',
            'prompt': prompt,
            'stream': False
        }
    )

    response.raise_for_status()
    data = response.json()
    task_text = data['response'].strip()

    db = next(get_db())
    add_task_to_db(db, task_text)

    return task_text

def get_tasks(skip=0, limit=10):
    db = next(get_db())
    tasks = get_tasks_from_db(db, skip=skip, limit=limit)
    
    return [{"id": task.id, "task_text": task.task_text, "created_at": task.created_at} for task in tasks]
