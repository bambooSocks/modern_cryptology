"""Code for Exercise 3 on Exercise sheet 6."""
import base64

# You need the `pycryptodome` package for these modules
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

BLOCK_SIZE = 16


def main():
    """Pass a ciphertext together with the IV and an oracle to the attacker."""
    ciphertext = create_ciphertext()
    attack(ciphertext, IV, padding_oracle)


def attack_block(cipherblock: bytes, iv: bytes, oracle):
    intermediate_values = []
    guesses = []
    for b in range(1, BLOCK_SIZE + 1):
        guess = 0
        for g in range(256):
            new_iv = list(iv)
            for n in range(1, b):
                new_iv[-n] = intermediate_values[n - 1] ^ b
            new_iv[-b] = g
            if oracle(cipherblock, bytes(new_iv)):
                guess = g
                break
        guess ^= b
        intermediate_values.append(guess)
        guess ^= list(iv)[-b]
        guesses.append(guess)

    return list(reversed(guesses))


def attack(ciphertext: bytes, iv: bytes, oracle):
    """Determine the plaintext from the ciphertext using the oracle."""
    result = []

    for i in range(len(ciphertext) // BLOCK_SIZE):
        current_iv = iv if i == 0 else ciphertext[(
            i-1)*BLOCK_SIZE:i*BLOCK_SIZE]
        block = ciphertext[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]
        result.append(attack_block(block, current_iv, oracle))

    result = [item for sublist in result for item in sublist]
    print(bytes(result))


KEY = get_random_bytes(16)
IV = get_random_bytes(16)
SECRET = (
    b"SXQncyBiZWVuIGEgaGFyZCBkYXkncyBuaWdodCwgYW5kIEkndmUgYmVlbiB3b3Jr"
    b"aW5nIGxpa2UgYSBkb2c="
)


def create_ciphertext() -> bytes:
    """Return the secret after padding and encrypting in CBC mode."""
    cipher = AES.new(KEY, AES.MODE_CBC, iv=IV)
    secret = base64.b64decode(SECRET)
    padded_secret = pkcs7_pad(secret, BLOCK_SIZE)
    print(padded_secret)
    ciphertext = cipher.encrypt(padded_secret)
    return ciphertext


def padding_oracle(ciphertext: bytes, initialization_vector: bytes) -> bool:
    """Verify that the ciphertext contains correct padding after decryption."""
    cipher = AES.new(KEY, AES.MODE_CBC, iv=initialization_vector)
    plaintext = cipher.decrypt(ciphertext)
    return is_padding_good(plaintext)


def is_padding_good(padded_message: bytes) -> bool:
    """Verify that the padding of the message is valid."""
    if not padded_message or len(padded_message) % BLOCK_SIZE != 0:
        return False
    last_byte = padded_message[-1]
    padding_length = int(last_byte)
    if padding_length > len(padded_message):
        return False
    if not all(byte == last_byte for byte in padded_message[-padding_length:]):
        return False
    return True


def pkcs7_pad(message: bytes, bytes_per_block: int) -> bytes:
    """Return the message padded to a multiple of `bytes_per_block`."""
    if bytes_per_block >= 256 or bytes_per_block < 1:
        raise Exception("Invalid padding modulus")
    remainder = len(message) % bytes_per_block
    padding_length = bytes_per_block - remainder
    padding = bytes([padding_length] * padding_length)
    return message + padding


if __name__ == "__main__":
    main()
