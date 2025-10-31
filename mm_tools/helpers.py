import lzma
import base64
import json

import msgpack


def compress_json(data: dict) -> str:
    packed = msgpack.packb(data, use_bin_type=True)
    compressed = lzma.compress(packed, preset=9)
    return base64.b85encode(compressed).decode('ascii')


def decompress_json(compressed_str: str) -> dict:
    compressed = base64.b85decode(compressed_str.encode('ascii'))
    packed = lzma.decompress(compressed)
    return msgpack.unpackb(packed, raw=False)


def read_dialog_state(state: str) -> dict:
    try:
        data = json.loads(state)
        if data.get('payload'):
            data['payload'] = decompress_json(data['payload'])
    except json.JSONDecodeError:
        return {}
    return data
