import zlib
import bz2
import lzma
import gzip
import base64
import binascii
import codecs

from Crypto.Cipher import ARC4, AES, ChaCha20, Salsa20
from Crypto.Util.Padding import pad


def chunk_payload(data, chunk_size=120):
    text = data.decode()
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def process_shellcode(shellcode, key, compression, encryption, encoding):

    data = shellcode
    decompress = None
    decrypt = None
    decode = None

    if compression == "zlib":
        data = zlib.compress(data, 9)
        decompress = "zlib.decompress"

    elif compression == "bz2":
        data = bz2.compress(data)
        decompress = "bz2.decompress"

    elif compression == "lzma":
        data = lzma.compress(data)
        decompress = "lzma.decompress"

    elif compression == "gzip":
        data = gzip.compress(data)
        decompress = "gzip.decompress"

    elif compression == "none":
        decompress = None

    else:
        raise ValueError("Invalid compression method")

    if encryption == "rc4":
        cipher = ARC4.new(key)
        data = cipher.encrypt(data)
        decrypt = "ARC4.new(key).decrypt"

    elif encryption == "none":
        decrypt = "lambda d: d"

    else:
        raise ValueError("Invalid encryption")

    if encoding == "base85":
        data = base64.b85encode(data)
        decode = "base64.b85decode"

    elif encoding == "base64":
        data = base64.b64encode(data)
        decode = "base64.b64decode"

    elif encoding == "base32":
        data = base64.b32encode(data)
        decode = "base64.b32decode"

    elif encoding == "urlsafe_b64":
        data = base64.urlsafe_b64encode(data)
        decode = "base64.urlsafe_b64decode"

    elif encoding == "ascii85":
        data = base64.a85encode(data)
        decode = "base64.a85decode"

    elif encoding == "hex":
        data = binascii.hexlify(data)
        decode = "binascii.unhexlify"

    elif encoding == "base16":
        data = base64.b16encode(data)
        decode = "base64.b16decode"

    elif encoding == "rot13":
        data = codecs.encode(data.decode(), "rot_13").encode()
        decode = "codecs.decode"

    elif encoding == "none":
        decode = "lambda d: d"

    else:
        raise ValueError("Invalid encoding")

    payload_chunks = chunk_payload(data)

    payload_code = "[\n" + ",\n".join(repr(c) for c in payload_chunks) + "\n]"

    lines = []
    lines.append(f"    data = {decode}(encoded_data)")
    lines.append(f"    data = {decrypt}(data)")

    if decompress:
        lines.append(f"    data = {decompress}(data)")

    lines.append("    return data")

    body = "\n".join(lines)

    decrypt_func = "def decode_and_decompress(encoded_data, key):\n" + body

    return payload_code, decrypt_func
