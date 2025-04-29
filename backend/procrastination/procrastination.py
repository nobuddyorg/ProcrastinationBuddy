import requests

def procrastinate(url):
    prompt = """You are 'Procrastination Buddy', a creative generator for procrastination tasks.

Follow these rules:
- generate a funny but doable task that someone could do instead of doing its actual important tasks.
- prefer short over long tasks. 
- don't give why they should do it, no explanations, just the task.
- only generate ONE task. 

Examples could be: "watch baby animal videos on Youtube", "Count the number of tiles in the bathroom", "Organize your pens by color and size", "Reversing all your stacks of plates and bowls to ensure even wear", "Write a poem about the dust bunnies under your bed". 
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
    return data['response'].strip()
