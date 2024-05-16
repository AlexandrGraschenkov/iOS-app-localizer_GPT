## Python Localization Script with GPT Support

<img src="images/github_localize_header.jpg">

This script is designed to help in localizing an iOS application using OpenAI's GPT models. It reads a `.xcstrings` file containing localization strings and generates translations for specified target languages while preserving the format, placeholders, and comments. 

### Localization Scripts
<img src="images/modes.jpg">

**Please note:** only supports `gpt-4-1106-preview`, `gpt-4o-2024-05-13` and `gpt-3.5-turbo-1106` models, which can give back an answer as JSON. I've found that `gpt-4-1106-preview` gives the best translation quality, so I use it by default everywhere.

![Terminal animation](/images/anim.gif)

### Prerequisites

To run this script, you will need:
- Python 3.x
- `openai` Python package
- An OpenAI API key

### Installation

Before you can run the script, make sure to install the necessary Python packages:

```bash
pip3 install openai tiktoken argparse tqdm
```

### Usage

To use the script, run it from the command line with the required arguments.

```bash
python3 localize_strings.py --gpt_api_key YOUR_GPT_API_KEY --file PATH_TO_XCSTRINGS_FILE --localize_from SOURCE_LANG_CODES --localize_to TARGET_LANG_CODES
```

For `localize_metadata` you also need to provide `fastlane_api_key_path` with path to JSON file:
```json
{
  "key_id": "CQC6F7C12K",
  "issuer_id": "39a1de7c-d01c-41se-e052-532c7c1ja4p1",
  "key": "-----BEGIN PRIVATE KEY-----\nMAGTAgEASBcGRyqG...\n-----END PRIVATE KEY-----",
  "duration": 1200,
  "in_house": false 
}
```

#### Available Arguments

- `--gpt_api_key`: Your GPT API key (required).
- `--gpt_model`: The GPT model you want to use (optional, default is `gpt-3.5-turbo-1106`).
- `--file`: The path to the `.xcstrings` file you want to localize (required).
- `--out_file`: The path to the output `.xcstrings` file (optional, will overwrite the original file if not provided).
- `--localize_from`: A comma-separated list of source language codes (required).
- `--localize_to`: A comma-separated list of target language codes (required).
- `--app_description`: A short description of your application for better context understanding (optional).
- `--max_input_token_count`: Maximum number of tokens for the model (optional).

### Example

```bash
python3 localize_strings.py --gpt_api_key "your-api-key" --file "./Localizable.xcstrings" --localize_from "en,de" --localize_to "es,fr,it" --app_description "A productivity app for managing tasks."
```

This command will translate the content of `Localizable.xcstrings` from English to Spanish, French, and Italian.

### Output

The script will generate a new `.xcstrings` file with the translations added. If the `--out_file` argument is not provided, the original file will be overwritten.

### Notes

- Ensure that your GPT API key has sufficient quota for processing the translations.
- The script preserves placeholders such as `%@` and `%d` and attempts to maintain the text length and formatting.
- Translations that need review are marked as such in the resulting file.

### Contributing

Feel free to fork the project and submit pull requests with improvements or report any issues you encounter.

### License

This script is open-sourced under the MIT License. See the LICENSE file for more information.

### Contact

For any additional questions or comments, please open an issue in the repository.

---

Happy Localizing! 🌍📲
