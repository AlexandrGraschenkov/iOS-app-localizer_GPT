# 🌍 iOS App localization 
***.xcstrings** / **metadata** / **release_notes**

<img src="images/github_localize_header.jpg" alt="Localization Banner">

This script helps localize iOS `.xcstrings` files and App Store metadata using OpenAI's GPT models. It preserves formatting, placeholders, and developer comments — all while generating high-quality translations in multiple languages with a single command.

**This is probably the most useful tool I’ve ever built — I use it every day.**

While similar features exist in paid tools, I’m sharing this for free because anyone could build basic version in Cursor in just a few hours. The first version dates back to a time when no proper tools were available. Since then, I've gradually improved it.

🎥 [Mobius Conference Talk (Russian)](https://www.youtube.com/watch?v=lU7EZ2K_4ho)

---

## 📜 Supported GPT Models

<img src="images/modes.jpg" alt="Model Support">

This tool supports the following models:

- `gpt-4.1` ✅ (default and recommended)
- `gpt-4-1106-preview`
- `gpt-4o-2024-05-13`
- `gpt-4o-mini-2024-07-18`
- `gpt-4.1-mini`
- `gpt-3.5-turbo-1106`

> 🧠 `gpt-4.1` provides the best translation quality based on my experience. `gpt-4.1-1106-preview` was even better, but more expensive.
> ⚠️ `gpt-5` and `gpt-5-mini` not tested.

![Terminal animation](/images/anim.gif)


## 🚀 News & Updates

**2025-09-27**
- Added **automatic language detection** from `.xcstrings` files
- `--localize_from` and `--localize_to` are now optional

**2025-06-22**
- Added support for **plural strings**
- Now supports **batching multiple files** in a single request


## 📦 Prerequisites

Make sure you have:

- Python 3.x
- An OpenAI API key
- Required Python packages:

```bash
pip3 install openai tiktoken argparse tqdm glob2
```


## ✅ Features

- [x] Localize App Store metadata and release notes
- [x] Plural string support (handled separately with a special prompt)
- [x] Process multiple `.xcstrings` files at once
- [ ] (Coming soon) Support for complex substitutions (e.g. multiple plurals in one string)


## 🛠 Usage

### Basic Example

```bash
# Auto-detect languages
python3 localize_strings.py \
  --gpt_api_key sk-... \
  --files ./project_path/Localizable.xcstrings

# Or specify languages manually
python3 localize_strings.py \
  --gpt_api_key sk-... \
  --files ./project_path/Localizable.xcstrings \
  --localize_from "en" \
  --localize_to "ar,de,es,fi,fr,..."
```

### Advanced Example (with multiple source languages & wildcards)

```bash
python3 localize_strings.py \
  --gpt_api_key sk-... \
  --files_pattern ./project_path/*.xcstrings \
  --localize_from "en,ru" \
  --localize_to "ar,de,es,fi,fr,hi,it,ja,ko,pl,pt,pt-BR,..."
```


## ⚙️ Available Arguments

| Argument | Description |
|----------|-------------|
| `--gpt_api_key` | Your OpenAI API key (required) |
| `--gpt_model` | GPT model to use (optional, default: `gpt-4.1`) |
| `--files` | Path to `.xcstrings` file(s) (required if `--files_pattern` not used) |
| `--files_pattern` | Pattern to match multiple files (e.g. `*.xcstrings`) |
| `--out_files` | Output path (optional, will overwrite originals if not provided) |
| `--localize_from` | Source language codes (comma-separated, e.g. `en,ru`) - auto-detected if not provided |
| `--localize_to` | Target language codes (comma-separated) - auto-detected if not provided |
| `--app_description` | App description to help GPT understand context (optional) |
| `--max_input_token_count` | Max token count for each request (optional) |


## 📄 Output

- Generates `.xcstrings` files with translated strings
- If `--out_files` is not set, it will overwrite the original files
- Strings needing review will be marked accordingly
- Placeholders like `%@`, `%d`, etc. are preserved
- Ignore keys marked as `do not translate`


## 📝 App Store Release Notes

To use `localize_release_notes`, install [Fastlane](https://docs.fastlane.tools/getting-started/ios/setup/) and provide a valid API key JSON file:

```json
{
  "key_id": "CQC6F7C12K",
  "issuer_id": "39a1de7c-d01c-41se-e052-532c7c1ja4p1",
  "key": "-----BEGIN PRIVATE KEY-----\nMAGTAgEASBcGRyqG...\n-----END PRIVATE KEY-----",
  "duration": 1200,
  "in_house": false 
}
```

## 📝 App Store Metadata

This script allows you to localize your app’s metadata: name, subtitle, description, keywords, and promotional text. While the localization of the name, subtitle, and keywords won't replace professional ASO, it's definitely better than having no localization at all.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 📬 Contact / 🤝 Contributing

Have questions, suggestions, or feedback? Feel free to open an issue on GitHub, fork the repo, or submit a pull request — contributions are always welcome!

📧 Email: alexandr.graschenkov91@gmail.com



### ✨ Happy Localizing! ✨
