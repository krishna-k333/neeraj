import unittest

from routers.whatsapp import _extract_upsert_messages, _message_phone


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


if __name__ == "__main__":
    unittest.main()
