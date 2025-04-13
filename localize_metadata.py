from openai import OpenAI
import json, argparse, os
from os.path import join
from tqdm import tqdm
from utils.gpt_utils import gpt_models, GPTWrapper
from utils.languages import LANGUAGES, COUNTRIES
from utils.metadata import get_exceed_fields, print_exceed_fields
import shutil

def get_language(code: str) -> str:
    try:
        language_code, region_code = code.split('-')
    except ValueError:
        language_code = code
        region_code = None  # or you can set to an empty string "" or any default value

    # Get the language name
    language_name = LANGUAGES.get(language_code, language_code.capitalize())

    # Get the country name
    if region_code:
        country_name = COUNTRIES.get(region_code, region_code.capitalize())
        return f'{language_name} ({country_name})'
    
    return language_name


def generate_prompt(lang_code, same_app_name: str|None):
    prompt = """
Help to localize iOS application metadata. As input you get JSON text:
["field":{"lang_code1":"Some text","lang_code2":"Other language text","lang_code3": null}].

Translate fields to {lang_name} language. Optimize the text for ASO language-dependent. Try to keep the length of the translated text. Keep "name" and "subtitle" under 30 characters, and "keywords" under 100 characters. Prepare translations for all "null" fields. Don't repeat the input text!{kepp_app_name}

Example JSON input: 
["name":{"en-US":"Video Player","ru":"Видео Плеер","de-DE":null}]

JSON Output:
["name":{"de-DE":"Videoplayer"}]
"""
    if same_app_name:
        prompt = prompt.replace("{kepp_app_name}", f' Keep name of App on all languages same "{same_app_name}".')
    else:
        prompt = prompt.replace("{kepp_app_name}", "")
    
    lang_name = get_language(lang_code) or "the new"
    prompt = prompt.replace("{lang_name}", f"{lang_name}")
    return prompt


def read_metadata(metadata_path: str, fields: list, src_langs: list, dst_lang: str):
    result = dict()
    for field in fields:
        field_values = dict()
        for src_lang in src_langs:
            full_path = join(metadata_path, src_lang, field+".txt")
            text = open(full_path).read()
            field_values[src_lang] = text.rstrip() # remove new line on the end
        field_values[dst_lang] = None
        result[field] = field_values
    return result

def update_metadata(metadata_path: str, fields: list, dst_lang: str, result: dict):
    os.makedirs(join(metadata_path, dst_lang), exist_ok=True)
    for field in fields:
        if field not in result:
            print(f"WARN!! No {field} inside responce result")
            continue
        if dst_lang not in result[field]:
            print(f"WARN!! No {dst_lang} inside responce result in {field}")
            continue
        
        text = result[field][dst_lang]
        if field == "keywords":
            # with keywords we can automaticly fix exceed text
            while len(text) > 100:
                text = ",".join(text.split(",")[:-1])
        dst_path = join(metadata_path, dst_lang, field+".txt")
        open(dst_path, "w").write(text+"\n")


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
    
    parser.add_argument('--fastlane_meta_path',
                        type=str,
                        required=True,
                        help='Location of json file')
    
    parser.add_argument('--fields',
                        type=str,
                        required=True,
                        help='Metadata fields to localzize, same as file name; Example: "name,subtitle,description"')
    
    parser.add_argument('--copy_fields',
                        type=str,
                        required=True,
                        help='Metadata fields to copy, same as file name; Example: "support_url,marketing_url,privacy_url"')
    
    parser.add_argument('--localize_to',
                        type=str,
                        required=True,
                        help='Array of language codes like "ru,en-US,de-DE"')
    
    parser.add_argument('--localize_from',
                        type=str,
                        required=True,
                        help='Array of language codes like "ru,en-US,de-DE"')
    
    parser.add_argument('--force_app_name',
                        type=str,
                        help='Array of language codes like "ru,en-US,de-DE"')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    gpt = GPTWrapper(api_key=args.gpt_api_key, model=args.gpt_model)
    if not gpt: exit

    src_langs = args.localize_from.split(",")
    fields = args.fields.split(",")
    copy_fields = args.copy_fields.split(",")
    dst_langs = args.localize_to.split(",")
    meta_path = args.fastlane_meta_path

    pbar = tqdm(dst_langs)
    exceed_fields = []
    for dst_lang in pbar:
        if dst_lang in src_langs: continue
        pbar.set_description(f"Processing language {dst_lang}")
        data = read_metadata(meta_path, fields, src_langs, dst_lang)
        prompt = generate_prompt(dst_lang, args.force_app_name)
        result_dict = gpt.process_json(prompt, data)
        
        update_metadata(meta_path, fields, dst_lang, result_dict)
        exceed_fields += get_exceed_fields(fields, dst_lang, result_dict)
        for field in copy_fields:
            copy_field_from_source(field, meta_path, dst_lang, src_langs[0])
    
    print(f"Tokens spended in {gpt.total_in_tokens} / out {gpt.total_out_tokens}")
    print_exceed_fields(exceed_fields)
    print("Done")

def copy_field_from_source(field, meta_path, dst_lang, src_lang):
    """Copy metadata field from first available source language to destination language"""
    dst_file = join(meta_path, dst_lang, f"{field}.txt")
    
    # Skip if destination file exists and not empty
    if os.path.exists(dst_file):
        with open(dst_file, 'r') as file:
            if file.read().strip():
                return
    
    src_file = join(meta_path, src_lang, f"{field}.txt")
    if os.path.exists(src_file):
        with open(src_file, 'r') as src:
            content = src.read()
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        with open(dst_file, 'w') as dst:
            dst.write(content)


if __name__ == '__main__':
    main()