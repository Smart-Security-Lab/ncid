from cipherImplementations.bifid import Bifid
from cipherImplementations.polybius import Polybius
import random


class CMBifid(Bifid):
    """Adapted implementation from https://github.com/tigertv/secretpy"""
    def __init__(self, alphabet, unknown_symbol, unknown_symbol_number):
        self.alphabet = alphabet
        self.unknown_symbol = unknown_symbol
        self.unknown_symbol_number = unknown_symbol_number

    def generate_random_key(self, length):
        key1 = super().generate_random_key(length)
        key2 = super().generate_random_key(length)
        return [length, key1[1], key2[1]]

    def encrypt(self, plaintext, key):
        pt = []
        for p in plaintext:
            pt.append(key[1].index(self.alphabet[p]))
        plaintext = pt
        __polybius = Polybius(key[1], self.unknown_symbol, self.unknown_symbol_number)
        if not key[0] > 0:
            key[0] = len(plaintext)
        code = __polybius.encrypt(plaintext)
        even = code[::2]
        odd = code[1::2]
        ret = []
        for i in range(0, len(even), key[0]):
            ret += even[i:i + key[0]] + odd[i:i + key[0]]
        ct = __polybius.decrypt(ret)
        ciphertext = []
        for c in ct:
            ciphertext.append(self.alphabet.index(key[2][c]))
        return ciphertext

    def decrypt(self, ciphertext, key):
        ct = []
        for c in ciphertext:
            ct.append(key[2].index(self.alphabet[c]))
        ciphertext = ct
        __polybius = Polybius(key[1], self.unknown_symbol, self.unknown_symbol_number)
        if not key[0] > 0:
            key[0] = len(ciphertext)
        code = __polybius.encrypt(ciphertext)
        even = ''
        odd = ''
        rem = len(code) % (key[0] << 1)
        for i in range(0, len(code) - rem, key[0] << 1):
            ikey = i + key[0]
            even += code[i:ikey]
            odd += code[ikey:ikey + key[0]]

        even += code[-rem:-(rem >> 1)]
        odd += code[-(rem >> 1):]

        code = []
        for i in range(len(even)):
            code += even[i] + odd[i]
        pt = __polybius.decrypt(code)
        plaintext = []
        for p in pt:
            plaintext.append(self.alphabet.index(key[1][p]))
        return plaintext