from openai import OpenAI
import json
import tiktoken, argparse
from utils.gpt_utils import gpt_models, GPTWrapper
from tqdm.auto import tqdm
from utils.languages import LANGUAGES

# for easy access to nested elements
class Hasher(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def generate_prompt(app_descrition = None, lang_code = None):
    prompt = """Assist with localizing the iOS application{to_lang}. Only translate fields with 'null' values. Maintain the text length, spacing, indentation, and placeholders such as '%@' and '%d'. Example JSON input: 
{"support":{"en":"Support","ru":null}}
Output:
{"support":{"ru":"Поддержка"}}
"""
    if app_descrition:
        text = f"Application is about of: {app_descrition}. "
        prompt = prompt.replace("{app_descrition}", text)
    else:
        prompt = prompt.replace("{app_descrition}", "")
    if lang_code:
        if lang_code in LANGUAGES:
            lang = LANGUAGES[lang_code]
            prompt = prompt.replace("{to_lang}", f" to {lang} (lang code '{lang_code}')")
        else:
            prompt = prompt.replace("{to_lang}", f" to lang code \"{lang_code}\"")
    else:
        prompt = prompt.replace("{to_lang}", "")
    return prompt

def prepare_translate_dict(original, src_langs, dst_langs):
    result = dict()
    for key in original["strings"]:
        orig_dict = Hasher(original["strings"][key])
        simple_dict = dict()
        if "comment" in orig_dict:
            simple_dict["comment"] = orig_dict["comment"]

        has_original_text = False
        for lang in src_langs:
            if lang not in orig_dict["localizations"]: continue
            val = orig_dict["localizations"][lang]
            if "stringUnit" in val: 
                simple_dict[lang] = val["stringUnit"]["value"]
                has_original_text = True
            elif "variations" in val: 
                plural_dict = val["variations"]["plural"]
                if plural_dict:
                    dict_val = { rule : val["stringUnit"]["value"] for rule, val in plural_dict.items() }
                    simple_dict[lang] = dict_val
                    has_original_text = True
                


        if not has_original_text:
            print(f"Key {key} don't have any translation in {src_langs}")
        
        need_to_translate = False # maybe we already have translation
        for lang in dst_langs:
            if lang not in orig_dict["localizations"]:
            # if lang not in simple_dict:
                need_to_translate = True
                simple_dict[lang] = None
        
        if need_to_translate and has_original_text:
            result[key] = simple_dict
    
    return result

def update_with_translations(original, gpt_result, force_update = False, needs_review = False):
    for key in gpt_result:
        original_dict = original["strings"][key]
        for lang in gpt_result[key]:
            if lang in original_dict["localizations"] and not force_update: continue
            if lang == "comment": continue # gpt somtimes translate comment to

            state = "needs_review" if needs_review else "translated"
            val = gpt_result[key][lang]
            if isinstance(val, str):
                original_dict["localizations"][lang] = {
                    "stringUnit" : {
                        "state" : state,
                        "value" : val
                    }
                }
            elif isinstance(val, dict):
                val_dict = {
                    rule : {"stringUnit" : {"state": state, "value": val}} 
                    for rule, val in val.items() 
                }
                original_dict["localizations"][lang] = {"variations": {"plural": val_dict}}
            


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
    
    parser.add_argument('--file',
                        type=str,
                        required=True,
                        help='Location of `xcstrings` file')
    
    parser.add_argument('--out_file',
                        type=str,
                        default=None,
                        help='Location of `xcstrings` output file')
    
    parser.add_argument('--localize_to',
                        type=str,
                        required=True,
                        help='Array of language codes like "ru,en,de"')
    
    parser.add_argument('--localize_from',
                        type=str,
                        required=True,
                        help='Array of language codes like "ru,en,de"')
    
    parser.add_argument('--app_description',
                        type=str,
                        default=None,
                        help='Short description about your App. For better context understanding.')
    
    parser.add_argument('--max_input_token_count',
                        type=int,
                        default=None,
                        help=f"If 'None', then will use maximum number of tokens for model {gpt_models}")

    return parser.parse_args()

def save(file: str, data: dict):
    json.dump(data, 
              open(file, "w"), 
              indent=2, 
              ensure_ascii=False,
              separators=(',', ' : ')) # override separators to make identical

def main():
    args = parse_arguments()
    gpt = GPTWrapper(api_key=args.gpt_api_key, 
                     model=args.gpt_model, 
                     max_input_token_count=args.max_input_token_count)
    if not gpt: exit
    
    src_langs = args.localize_from.split(",")
    dst_langs = args.localize_to.split(",")
    original = json.load(open(args.file))
    out_file_path = args.out_file
    if not out_file_path:
        out_file_path = args.file


    pbar = tqdm(dst_langs)
    for dst_lang in pbar:
        pbar.set_description_str(f"Translating to {dst_lang}")
        process_dict = prepare_translate_dict(original, src_langs, [dst_lang])

        if len(process_dict) == 0: continue
        prompt = generate_prompt(app_descrition=args.app_descrition, lang_code=dst_lang)
        translated_data = gpt.process_json(prompt, process_dict)
        update_with_translations(original, translated_data, force_update=True)
        save(out_file_path, original) # don't wanna miss progress
    
    print(f"Tokens spended in {gpt.total_in_tokens} / out {gpt.total_out_tokens}")
    print("Save result")
    # update_with_translations(original, result)
    save(out_file_path, original)
    print("Done")

if __name__ == '__main__':
    # test()
    main()