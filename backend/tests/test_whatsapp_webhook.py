import asyncio
import unittest

from routers.whatsapp import _extract_upsert_messages, _message_phone
from services.chat_buffer import _evolution_number
from services.router import TEST_PHONE, decide


class EvolutionWebhookPayloadTests(unittest.TestCase):
    def test_extracts_evolution_v2_single_message(self):
        message = {
            "key": {"remoteJid": "919876543210@s.whatsapp.net", "fromMe": False},
            "message": {"conversation": "hello"},
        }

        self.assertEqual(_extract_upsert_messages({"data": message}), [message])

    def test_extracts_legacy_message_list(self):
        messages = [
            {
                "key": {"remoteJid": "919876543210@s.whatsapp.net"},
                "message": {"conversation": "hello"},
            }
        ]

        self.assertEqual(
            _extract_upsert_messages({"data": {"messages": messages}}),
            messages,
        )

    def test_rejects_malformed_data(self):
        self.assertEqual(_extract_upsert_messages({"data": None}), [])
        self.assertEqual(_extract_upsert_messages({"data": {}}), [])

    def test_prefers_phone_jid_over_lid(self):
        message = {
            "key": {
                "remoteJid": "123456789@lid",
                "remoteJidAlt": "919876543210@s.whatsapp.net",
            }
        }

        self.assertEqual(_message_phone(message), "919876543210")

    def test_preserves_full_indian_number_for_outbound_reply(self):
        self.assertEqual(_evolution_number("918287367640"), "918287367640")
        self.assertEqual(_evolution_number("8287367640"), "918287367640")

    def test_other_numbers_are_receive_only(self):
        decision = asyncio.run(decide("919999999999", "hello"))
        self.assertEqual(TEST_PHONE, "918287367640")
        self.assertFalse(decision.use_llm)
        self.assertIsNone(decision.reply)
        self.assertEqual(decision.reason, "phone-not-test-scope")


if __name__ == "__main__":
    unittest.main()
