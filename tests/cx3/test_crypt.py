# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

from krkrz.cx3.crypt import KeyDerivator


def test_keyderivator():
    derivator = KeyDerivator(
        bootstrap_string="BOOTSTRAPbootstrap0123456789",
        warning_string="WARNINGwarning0123456789",
        params_blob=b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09",
        archive_unique_key="ArchiveUniqueKey0123456789",
        upper_key_seed=b"\x00\x11\x22\x33\x44\x55\x66\x77",
    )
    keys = derivator.derive()
    assert keys.key == bytes.fromhex(
        "59cacc6137c3ba197b2656b63c79c63d5341867a0d9e6445e809cad2f7b9dff0"
    )
    assert keys.nonce_a == bytes.fromhex(
        "23e8bfd929bcac04e775d168e37f1871287b5676925105a0"
    )
    assert keys.nonce_b == bytes.fromhex(
        "98d9fc0c47eb2684aad17ca33ee8cb1aed30812ee8990500"
    )
