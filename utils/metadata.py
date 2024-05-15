
def get_exceed_fields(fields, dst_lang, result_dict) -> list:
    max_length = {"name": 30, "subtitle": 30, "keywords": 100, "promotional_text": 170, "release_notes": 4000, "description": 4000}
    out_fields = []
    for field in fields:
        text = result_dict[field][dst_lang]
        if field in max_length and len(text) > max_length[field]:
            out_fields.append({"lang": dst_lang, 
                               "name": field, 
                               "value": text, 
                               "len": max_length[field]
                              })
    return out_fields

def add_color_for_print(text, color="6;30;43"):
    # based on https://stackoverflow.com/a/21786287/820795
    return f'\x1b[{color}m' + text + '\x1b[0m'

def print_exceed_fields(fields_info):
    if len(fields_info) > 0:
        print("\nWhile translating, some of the fields below  "+ add_color_for_print("exceeded their boundaries!"), end="\n\n")
    for field in fields_info:
        max_len = field['len']
        print(f"Field: {field['name']}, lang: {field['lang']}, len: {max_len}")
        text = field["value"][:max_len] 
        text += add_color_for_print(field["value"][max_len:])
        print(text, end="\n\n")

