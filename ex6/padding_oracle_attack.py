"""Code for Exercise 1 on Exercise sheet 6."""

BLOCK_SIZE = 16


def main():
    """Check the correctness of the padding checking."""
    good_padding_1 = b"Hello world\x05\x05\x05\x05\x05"
    good_padding_2 = b"Fancy cryptology" + b"\x10" * 16
    assert is_padding_good(good_padding_1)
    assert is_padding_good(good_padding_2)
    print(is_padding_good(good_padding_1))
    print(is_padding_good(good_padding_2))
    bad_padding_1 = b"Hello world\x04\x04\x04"
    bad_padding_2 = b"Hi world\x04\x04\x04\x04"
    assert not is_padding_good(bad_padding_1)
    assert not is_padding_good(bad_padding_2)
    print(is_padding_good(bad_padding_1))
    print(is_padding_good(bad_padding_2))

def is_padding_good(padded_message: bytes) -> bool:
    """Verify that the message has been padded with a valid padding."""
    N = padded_message[-1]
    res = True
    for ind, m in enumerate(reversed(padded_message)):
        if ind >= N:
            break
        if m != N:
            res = False

    return len(padded_message) % BLOCK_SIZE == 0 and res


if __name__ == "__main__":
    main()
