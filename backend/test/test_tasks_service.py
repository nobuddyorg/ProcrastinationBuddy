from services.tasks import generate_prompt


def test_generate_prompt_contains_language_and_examples():
    lang = "french"
    prompt = generate_prompt(lang)

    assert f"Language (no translations): {lang}" in prompt
    assert "Examples of my favorites" in prompt
    assert "You are 'Procrastination Buddy'" in prompt
    assert prompt.count("\n") > 5
