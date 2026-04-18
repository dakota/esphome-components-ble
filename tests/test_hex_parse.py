# Mirrors BleAdvParam::from_hex_string (ble_adv_handler.cpp) for regression testing.
from __future__ import annotations

MAX_PACKET_LEN = 31


def parse_hex_like_ble_adv_param(raw_in: str) -> bytes:
    """Return parsed bytes; must stay in sync with C++ from_hex_string."""
    raw = raw_in
    paren = raw.find("(")
    if paren != -1:
        raw = raw[:paren]
    raw = raw.replace(".", "").replace(" ", "")
    if raw[:2].lower() == "0x":
        raw = raw[2:]

    def nibble(c: str) -> int:
        if "0" <= c <= "9":
            return ord(c) - ord("0")
        o = ord(c.lower()) - ord("a") + 10
        if 0 <= o <= 15:
            return o
        return -1

    out = bytearray()
    i = 0
    while i + 1 < len(raw) and len(out) < MAX_PACKET_LEN:
        hi = nibble(raw[i])
        lo = nibble(raw[i + 1])
        if hi < 0 or lo < 0:
            break
        out.append((hi << 4) | lo)
        i += 2
    return bytes(out)


def test_strip_paren_and_length_suffix():
    s = "0201021B03F9 (31)"
    assert parse_hex_like_ble_adv_param(s).hex() == "0201021b03f9"


def test_0x_prefix():
    assert parse_hex_like_ble_adv_param("0xABCD") == bytes([0xAB, 0xCD])


def test_dots_and_spaces():
    inp = "02 01 02 1B 03 F9"
    assert parse_hex_like_ble_adv_param(inp) == bytes([0x02, 0x01, 0x02, 0x1B, 0x03, 0xF9])


def test_odd_length_ignores_trailing_nibble():
    # C++ logs warning and stops at last full byte pair
    assert parse_hex_like_ble_adv_param("ABC") == bytes([0xAB])


def test_invalid_hex_stops_parse():
    assert parse_hex_like_ble_adv_param("ABXX") == bytes([0xAB])


def test_golden_readme_sample():
    # CUSTOM.md / README style full packet (truncated for test)
    h = "0201021B03F9084913F069254E3151BA32080A24CB3B7C71DC8BB89708D04C"
    b = parse_hex_like_ble_adv_param(h)
    assert len(b) <= 31
    assert b[0] == 0x02 and b[1] == 0x01


def test_empty():
    assert parse_hex_like_ble_adv_param("") == b""


# --- Golden samples (protocol docs) ---


def test_fanlamp_style_packet_length():
    """31-byte manufacturer-style advertisement from docs."""
    h = (
        "02.01.02.1B.03.F9.08.49.13.F0.69.25.4E.31.51.BA.32.08.0A.24.CB.3B.7C.71.DC.8B.B8.97.08.D0.4C"
    )
    b = parse_hex_like_ble_adv_param(h)
    assert len(b) == 31


def test_zhijia_header_bytes():
    """zhijia v2 header prefix from encoder tables."""
    assert parse_hex_like_ble_adv_param("229D") == bytes([0x22, 0x9D])
