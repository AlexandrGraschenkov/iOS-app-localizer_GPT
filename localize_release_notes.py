import subprocess, json, tiktoken, argparse, os, tempfile
import concurrent.futures
from os.path import join
from openai import OpenAI
from utils.languages import LANGUAGES_LIST
from utils.gpt_utils import gpt_models, GPTWrapper


def get_prompt():
    return """Help to localize iOS release notes. For example as input you get JSON text:
{"notes":"Bug fixes","localize_to":["ru","en-US"]}

As output provide translated text for empty lang code:
{"ru":"Исправлены ошибки","en-US":"Bug fixes"}
"""


def parse_input() -> str:
    print("\nWrite Release Notes until 'END': ")
    release_notes = []
    while True:
        line = input()
        if line.endswith('END'):
            line = line.replace('END', '')  # Remove 'END' from the current line if present
            release_notes.append(line.strip())  # Add the final part of the note
            break  # Break the loop as we found 'END'
        release_notes.append(line.strip())  # Add the line to the release notes

    return "\n".join(release_notes)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Python script localize your application powered with GPT.')
    
    parser.add_argument('--gpt_api_key',
                        type=str,
                        required=True,
                        help='Your GPT API key')
    
    list_models = ", ".join(list(gpt_models.keys()))
    parser.add_argument('--gpt_model',
                        type=str,
                        default="gpt-4-1106-preview",
                        help=f'Choose model from: {list_models}')
    
    parser.add_argument('--fastlane_api_key_path',
                        type=str,
                        required=True,
                        help='For AppStore authorization')
    
    parser.add_argument('--app_id',
                        type=str,
                        required=True,
                        help='Bundle App ID')
    
    return parser.parse_args()


def load_languages(api_key_path, app_identifier):
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = temp_dir.name
    command = f'fastlane deliver download_metadata -m "{temp_path}" --api_key_path "{api_key_path}" -a "{app_identifier}" -f'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        temp_dir.cleanup()
        raise Exception(f"Failed to initialize spaceship: {result.stderr}")
    
    exiting_languages = []
    for f in os.listdir(temp_path):
        if f in LANGUAGES_LIST:
            exiting_languages.append(f)
    temp_dir.cleanup()
    # print("•••", exiting_languages)
    return exiting_languages


def upload(release_notes, api_key_path, app_id):
    temp_dir = tempfile.TemporaryDirectory()
    temp_meta = temp_dir.name

    
    for key in release_notes:
        os.makedirs(join(temp_meta, key), exist_ok=True)
        text = release_notes[key]
        open(join(temp_meta, key, "release_notes.txt"), "w").write(text)

    params = {
        "api_key_path": f'"{api_key_path}"',
        "app_identifier": f'"{app_id}"',
        "skip_binary_upload": "true", # skip binary upload when updating only screenshots/metada
        "force": "true", # Skip the HTML report file verification
        "submit_for_review": "false", # Do not submit for review after metadata update
        "overwrite_screenshots": "false",
        "skip_screenshots": "true",
        "metadata_path": f'"{temp_meta}"',
        "precheck_include_in_app_purchases": "false"
    }

    command = "fastlane run deliver"
    for key in params:
        command += f" {key}:{params[key]}"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        temp_dir.cleanup()
        raise Exception(f"Failed to upload metadata with fastlane: {result.stderr}")

def main():
    global client
    args = parse_arguments()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(load_languages, args.fastlane_api_key_path, args.app_id)
    gpt = GPTWrapper(api_key=args.gpt_api_key, 
                     model=args.gpt_model,
                     temperature=0.4)

    notes = parse_input()
    languages = future.result()

    to_translate = {'notes': notes, 'localize_to': languages}
    prompt = get_prompt()
    release_notes_localized = gpt.process_json(prompt, to_translate)

    release_notes_preview = json.dumps(release_notes_localized, indent=2, ensure_ascii=False)
    print(f"Release notes:\n{release_notes_preview}\n")

    print(f"Tokens spended in {gpt.total_in_tokens} / out {gpt.total_out_tokens}")
    print("Uploading release notes")
    upload(release_notes_localized, args.fastlane_api_key_path, args.app_id)
    print("Done!")


if __name__ == '__main__':
    main()