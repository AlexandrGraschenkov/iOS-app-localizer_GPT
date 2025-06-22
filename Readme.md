## Python Localization Script with GPT Support

<img src="images/github_localize_header.jpg">

This script is designed to help in localizing an iOS application using OpenAI's GPT models. It reads a `.xcstrings` file containing localization strings and generates translations for specified target languages while preserving the format, placeholders, and comments. You can also localize your release notes into all App Store languages with a single command. Honestly, this is probably **the most useful tool** I’ve ever built - I use these scripts every day.

While there are paid apps offering similar features, I’m sharing this script for free because I believe anyone could build something like this in Cursor in just a few hours. I originally wrote the first version years ago, back when there weren’t any good tools for translation. Since then, I’ve been improving it from time to time.

[Mobius Conference Speech (Russian, YouTube)](https://www.youtube.com/watch?v=lU7EZ2K_4ho)

### Localization Scripts
<img src="images/modes.jpg">

**Please note:** only supports `gpt-4.1`, `gpt-4.1-mini`, `gpt-4-1106-preview`, `gpt-4o-2024-05-13`, `gpt-4o-mini-2024-07-18` and `gpt-3.5-turbo-1106` models, which can give back an answer as JSON. I've found that `gpt-4-1106-preview` gives the best translation quality, so I use it by default everywhere. Did't test quality with `gpt-4.1`, `gpt-4.1-mini`.

![Terminal animation](/images/anim.gif)

## News 🚀
* **2025.06.22** - Improved support for **plural strings**; added ability to process **multiple files** with batching in 1 request

### Prerequisites

To run this script, you will need:
- Python 3.x
- `openai` Python package
- An OpenAI API key

```bash
pip3 install openai tiktoken argparse tqdm glob2
```

### ✅ Features
- [x] Localize release notes and App Store metadata
- [x] Support for plural string localization (handled in a separate request with a dedicated prompt)  
- [x] Localize multiple files in a single request
- [ ] Support for complex substitutions (e.g. strings with multiple plurals) 

### Usage

To use the script, run it from the command line with the required arguments.

```bash
python3 localize_strings.py \
  --gpt_api_key YOUR_GPT_API_KEY \
  --files ./project_path/Localizable.xcstrings \
  --localize_from "en" \
  --localize_to "ar,de,es,fi,fr,..."
```

Or just pass the project folder, and it will localize all `*.xcstrings` files inside the project. You can also use multiple source languages to provide more context for GPT translations.
```bash
python3 localize_strings.py \
  --gpt_api_key sk-fR... \
  --files_pattern ./project_path/*.xcstrings \
  --localize_from "en,ru" \
  --localize_to "ar,de,es,fi,fr,hi,it,ja,ko,pl,pt,pt-BR,.."
```

#### Available Arguments

- `--gpt_api_key`: Your GPT API key (required).
- `--gpt_model`: The GPT model you want to use (optional, default is `gpt-4-1106-preview`).
- `--files`: The path to the `.xcstrings` files you want to localize (required).
- `--out_files`: The path to the output `.xcstrings` files (optional, will overwrite the original file if not provided).
- `--localize_from`: A comma-separated list of source language codes (required).
- `--localize_to`: A comma-separated list of target language codes (required).
- `--app_description`: A short description of your application for better context understanding (optional).
- `--max_input_token_count`: Maximum number of tokens for the model (optional).


### Output

The script will generate a new `.xcstrings` file with the translations added. If the `--out_files` argument is not provided, the original file will be overwritten.

### Notes

- Ensure that your GPT API key has sufficient quota for processing the translations.
- The script preserves placeholders such as `%@` and `%d` and attempts to maintain the text length and formatting.
- Translations that need review are marked as such in the resulting file.
  
For `localize_release_notes` you need to [install Fastlane](https://docs.fastlane.tools/getting-started/ios/setup/). You also need to provide `fastlane_api_key_path` with path to JSON file:
```json
{
  "key_id": "CQC6F7C12K",
  "issuer_id": "39a1de7c-d01c-41se-e052-532c7c1ja4p1",
  "key": "-----BEGIN PRIVATE KEY-----\nMAGTAgEASBcGRyqG...\n-----END PRIVATE KEY-----",
  "duration": 1200,
  "in_house": false 
}
```

### Contributing

Feel free to fork the project and submit pull requests with improvements or report any issues you encounter.

### License

This script is open-sourced under the MIT License. See the LICENSE file for more information.

### Contact

For any additional questions or comments, please open an issue in the repository.

---

Happy Localizing! 🌍📲
