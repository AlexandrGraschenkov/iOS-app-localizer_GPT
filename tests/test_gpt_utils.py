import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from utils.gpt_utils import (
    GPTWrapper,
    OPENAI_MAX_RETRIES,
    OPENAI_TIMEOUT_SECONDS,
)


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.arguments = None

    def create(self, **kwargs):
        self.arguments = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content),
                )
            ],
            _request_id="req_test",
        )


class GPTWrapperTests(unittest.TestCase):
    @patch("utils.gpt_utils.tiktoken.encoding_for_model")
    @patch("utils.gpt_utils.OpenAI")
    def test_client_has_retry_and_timeout_settings(self, openai_mock, encoding_mock):
        encoding_mock.return_value.encode.return_value = []

        GPTWrapper("test-key", "gpt-4.1")

        openai_mock.assert_called_once_with(
            api_key="test-key",
            max_retries=OPENAI_MAX_RETRIES,
            timeout=OPENAI_TIMEOUT_SECONDS,
        )

    @patch("utils.gpt_utils.tiktoken.encoding_for_model")
    @patch("utils.gpt_utils.OpenAI")
    def test_process_json_uses_json_mode(self, openai_mock, encoding_mock):
        encoding_mock.return_value.encode.return_value = []
        completions = FakeCompletions('{"hello":"Привет"}')
        openai_mock.return_value.chat.completions = completions
        wrapper = GPTWrapper("test-key", "gpt-4.1")

        result = wrapper.process_json(
            "Translate and return JSON.",
            {"hello": None},
        )

        self.assertEqual(result, {"hello": "Привет"})
        self.assertEqual(
            completions.arguments["response_format"],
            {"type": "json_object"},
        )
        self.assertEqual(
            json.loads(completions.arguments["messages"][1]["content"]),
            {"hello": None},
        )


if __name__ == "__main__":
    unittest.main()
