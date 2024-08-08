import json
from openai import OpenAI
import tiktoken
from tqdm.auto import tqdm

# only this models supprot json response
gpt_models = {
	"gpt-4-1106-preview": 128000,
	"gpt-3.5-turbo-1106": 16385,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4o-mini-2024-07-18": 128000
}

def split_dictionary_by_half(d):
    midpoint = len(d) // 2
    items = list(d.items())
    return dict(items[:midpoint]), dict(items[midpoint:])

class GPTWrapper:
    def __init__(self, api_key, model, temperature = 0.2, max_input_token_count = None):
        if model not in gpt_models:
            print(f"Can't find {model} in list available models")
            return None
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.enc = tiktoken.encoding_for_model("gpt-4")
        self.max_input_token_count = max_input_token_count if max_input_token_count else gpt_models[model]
        self.total_in_tokens = 0
        self.total_out_tokens = 0

    def process_json(self, prompt: str, json_input: dict):
        splitted_jsons = [json_input]
        idx = 0
        # split input into chunks, to fit max token limit
        while idx < len(splitted_jsons):
            val = splitted_jsons[idx]
            message = json.dumps(val, ensure_ascii=False, separators=(',', ':'))
            tokens_count = len(self.enc.encode(f"{prompt}\n{message}"))
            if tokens_count > self.max_input_token_count:
                if len(val) < 2: 
                    print(f"Not enought input tokens: {self.max_input_token_count}")
                    return None
                val1, val2 = split_dictionary_by_half(val)
                splitted_jsons[idx] = val1
                splitted_jsons.insert(idx+1, val2)
            else:
                idx += 1

        result_json = dict()
        pbar = tqdm(splitted_jsons, leave=False)
        translated_count = 0
        for json_val in pbar:
            message = json.dumps(json_val, ensure_ascii=False, separators=(',', ':'))
            tokens_count = len(self.enc.encode(f"{prompt}\n{message}"))
            self.total_in_tokens += tokens_count
            translated_count += len(json_val)
            pbar.set_description_str(f"Translating {translated_count}/{len(json_input)}, tokens count: in {self.total_in_tokens} / out {self.total_out_tokens}")
            data = self.__process_json_internal(prompt, json_val)
            result_json = {**result_json, **data}
            # import time # just for debug
            # time.sleep(2)
            # result_json = {**result_json, **json_val}

        return result_json


    def __process_json_internal(self, prompt, json_input):
        message = json.dumps(json_input, ensure_ascii=False, separators=(',', ':'))
        response = self.client.chat.completions.create(
            model = self.model,
            temperature = self.temperature,
            response_format = { "type": "json_object" },
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        output_text = response.choices[0].message.content
        # print("Output Tokens:", len(enc.encode(output_text)))
        self.total_out_tokens += len(self.enc.encode(output_text))
        return json.loads(output_text)