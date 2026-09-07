"""Testes das funções de hash e verificação de senha (app.password_hash / verify_password)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import app  # noqa: E402


class PasswordHashTest(unittest.TestCase):
    def test_retorna_salt_e_hash_em_hexadecimal(self):
        salt, hashed = app.password_hash("senha-secreta")
        # Ambos devem ser strings hexadecimais decodificáveis.
        self.assertEqual(len(salt), 32)  # 16 bytes de salt -> 32 chars hex
        bytes.fromhex(salt)
        bytes.fromhex(hashed)

    def test_salts_aleatorios_geram_hashes_diferentes(self):
        _, hash_a = app.password_hash("mesma-senha")
        _, hash_b = app.password_hash("mesma-senha")
        # Sem salt informado, cada chamada usa salt novo -> hashes distintos.
        self.assertNotEqual(hash_a, hash_b)

    def test_mesmo_salt_gera_hash_deterministico(self):
        salt, hash_a = app.password_hash("mesma-senha")
        _, hash_b = app.password_hash("mesma-senha", salt)
        self.assertEqual(hash_a, hash_b)

    def test_senhas_diferentes_com_mesmo_salt_geram_hashes_diferentes(self):
        salt, hash_a = app.password_hash("senha-um")
        _, hash_b = app.password_hash("senha-dois", salt)
        self.assertNotEqual(hash_a, hash_b)


class VerifyPasswordTest(unittest.TestCase):
    def test_verifica_senha_correta(self):
        salt, hashed = app.password_hash("minha-senha")
        self.assertTrue(app.verify_password("minha-senha", salt, hashed))

    def test_rejeita_senha_incorreta(self):
        salt, hashed = app.password_hash("minha-senha")
        self.assertFalse(app.verify_password("senha-errada", salt, hashed))

    def test_rejeita_com_salt_diferente(self):
        salt, hashed = app.password_hash("minha-senha")
        outro_salt, _ = app.password_hash("qualquer")
        self.assertNotEqual(salt, outro_salt)
        self.assertFalse(app.verify_password("minha-senha", outro_salt, hashed))


if __name__ == "__main__":
    unittest.main()
