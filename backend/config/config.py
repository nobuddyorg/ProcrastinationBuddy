import argparse

def get_config():
    parser = argparse.ArgumentParser(description="Generate a creative procrastination excuse.")
    parser.add_argument('--url', type=str, default='http://localhost:11434/api/generate', help="URL for the API to call.")
    args = parser.parse_args()
    return args.url
