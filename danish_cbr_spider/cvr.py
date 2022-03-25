
import re
from typing import List

import numpy as np

# based on this implementation https://gist.github.com/henrik/daf364fb7e22b3b10cad
# and this spec: https://web.archive.org/web/20160410033847/https://erhvervsstyrelsen.dk/modulus-11-kontrol

WEIGHTS = [2, 7, 6, 5, 4, 3, 2]
CVR_REX = re.compile(r"^[0-9]{8}$")


def make_cvr_check(digits: List[int]):
    weighed_sum = sum(d*w for d, w in zip(digits, WEIGHTS))
    check = 11 - (weighed_sum % 11)

    if check == 10:
        # not possible as per the spec
        return None
    if check == 11:
        # oh well
        check = 0

    return check


def check_cvr(cvr: str):
    """
    Checks whether the provided cvr is valid as per the spec
    :return: True of False
    """
    if not CVR_REX.match(cvr):
        return False

    digits = [int(d) for d in cvr[:-1]]
    expected_check = int(cvr[-1])

    check = make_cvr_check(digits)

    return expected_check == check


# these can be run with pytest
def test_cvr():
    assert check_cvr("35408002"), "is true for an 8-digit string with valid check digit"
    assert check_cvr("25472020"), "accounts for the special case of a 0 check digit"
    assert not check_cvr("foo 35408002 bar"), "does not allow extra text"
    assert not check_cvr("123"), "rejects too-short strings"
    assert not check_cvr("35408003"), "rejects too-short strings"

    # Let's validate some real examples to make sure we got it right.
    # From: https://datacvr.virk.dk/data/
    for n in ["37272884", "25555619", "21459895", "35408002"]:
        assert check_cvr(n), f"accepts real-life number #{n}"


# don't wanna make a global seed, so use np's rng here
def make_cvr(rng: np.random.Generator) -> str:
    """
    Generate a random CVR that is valid and has a high probability to exist
    :param rng: an rng instance to use
    :return: a valid and hopefully an existent CVR number
    """
    while True:
        digits = [rng.choice(range(0, 10)) for _ in range(0, 7)]
        check = make_cvr_check(digits)

        if not check:
            # if we got an impossible number - try again
            continue

        res = ''.join(map(str, digits + [check]))

        # it seems that actually issued CVRs are in a pretty narrow range, so don't generate the wrong ones
        if not (30000000 < int(res) < 45000000):
            continue

        return res


def test_make_cvr():
    for seed in range(0, 1000):
        rng = np.random.default_rng(seed)
        cvr = make_cvr(rng)
        assert check_cvr(cvr), f"Using make_cvr with seed {seed} produced non-valid cvr {cvr}"


def make_cvrs(count: int, seed: int) -> List[str]:
    rng = np.random.default_rng(seed)
    return [make_cvr(rng) for _ in range(count)]