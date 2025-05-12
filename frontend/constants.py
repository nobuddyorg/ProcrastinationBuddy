import os

LANGUAGE = "en"
LAYOUT = "centered"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

PAGE_ICON = "⏰"

TEXTS = {
    "en": {
        "main": {
            "title": "Procrastination Buddy ⏰🤷",
            "subtitle": "Your partner in crime for finding perfectly pointless tasks!",
            "generate_button": "Generate",
            "spinner_text": "Generating task...",
            "info_button": "ℹ️",
            "like_button": "❤",
            "config_button": "⚙️",
        },
        "help": {
            "title": "Why other tools don't help you!",
            "intro": "**Let's face it**, you’ll end up in the *'Urgent and Important'* quadrant of the Eisenhower Matrix anyway. Why waste time planning? Pomodoro? Sure, take a 25-minute break. Procrastination isn't a sprint, it's art.",
            "middle": "But hey, don’t stress, just enjoy your perfectly unbalanced balance of procrastination and productivity. And if you're still trying to stick to these methods against all reason, feel free to read more about them.",
            "pomodoro_title": "**Pomodoro Technique**",
            "pomodoro_desc": "It’s all about 25-minute bursts of productivity… or of pretending to focus until your next scheduled distraction. Maybe you get something done - or maybe you procrastinate harder, just to avoid the timer.",
            "pomodoro_link": "Learn more about Pomodoro Technique",
            "eisenhower_title": "**Eisenhower Matrix**",
            "eisenhower_desc": "It’s a fancy way of making all your tasks urgent and important at the same time. Congratulations, you're officially stressed - staring at one remaining quadrant with no method left to help with priorities anymore.",
            "eisenhower_link": "Learn more about Eisenhower Matrix",
            "summary": "In the end, these methods might help. But when you're truly embracing procrastination, remember: *all tasks will end up in 'Urgent and Important'.*",
            "irony": "**If you think this is sarcastic, just remember: it's still not as ironic as using a tomato or a 60-year-old matrix to boost your productivity in the 21st century as if the world hasn’t changed since.**",
            "close": "Close",
        },
    },
    # Add other languages here
    # "de": { ... },
    # "es": { ... }
}
