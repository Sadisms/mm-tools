import lzma
import base64
import msgpack


def compress_json(data: dict) -> str:
    packed = msgpack.packb(data, use_bin_type=True)
    compressed = lzma.compress(packed, preset=9)
    return base64.b85encode(compressed).decode('ascii')


def decompress_json(compressed_str: str) -> dict:
    compressed = base64.b85decode(compressed_str.encode('ascii'))
    packed = lzma.decompress(compressed)
    return msgpack.unpackb(packed, raw=False)
