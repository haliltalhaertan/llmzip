"""EXPLICITLY MALICIOUS test double. NEVER part of any gate, V10, or shipment.

Simulates an attacker-controlled ``v8_runtime`` dependency: every check is a
no-op and module loading returns attacker-chosen collaborators, so any gate
that honors ambient ``sys.modules`` instead of its own authenticated bytes
will accept arbitrary garbage and report attacker-chosen denominators.
"""

from types import SimpleNamespace

INFLATED = (("copy-x", "pop-x", 10 ** 9),)


class V8ValidationError(ValueError):
    pass


def need(condition, message):
    return None


def digest(value, where):
    return None


V7_PATH = "/nonexistent/v7"
PARENT_GUARD_PATH = "/nonexistent/guard"
CONTRACT_PATH = "/nonexistent/contract"
V6_PATH = "/nonexistent/v6"
V7_SOURCE_SHA256 = "1" * 64
PARENT_GUARD_SHA256 = "0" * 64
CONTRACT_SHA256 = "0" * 64
V6_PREFLIGHT_SHA256 = "0" * 64
LONGMEMEVAL_ANCHOR_SHA256 = "0" * 64
LONGMEMEVAL_ID_COLUMN = "question_id"
LONGMEMEVAL_VALUE_COLUMN = "N_archive"
LONGMEMEVAL_EXPECTED_ROWS = 470


class _FakePlan:
    def __init__(self, sha256, contract_sha256):
        self.raw = b"attacker-plan"
        self.sha256 = sha256
        self.contract_sha256 = contract_sha256
        self.data = {"archives": [], "probes": [], "populations": [],
                     "physical_copies": []}


class _FakeGuard:
    Plan = _FakePlan

    @staticmethod
    def load_plan(plan_path, expected_sha256, contract_path):
        return _FakePlan(expected_sha256, CONTRACT_SHA256)


class _FakeProof:
    denominators = INFLATED

    def denominator_map(self):
        return {c: (p, d) for c, p, d in self.denominators}


class _FakeV7:
    PARENT_GUARD_SHA256 = PARENT_GUARD_SHA256
    CONTRACT_SHA256 = CONTRACT_SHA256
    V6_PREFLIGHT_SHA256 = V6_PREFLIGHT_SHA256
    LONGMEMEVAL_ANCHOR_SHA256 = LONGMEMEVAL_ANCHOR_SHA256
    LONGMEMEVAL_ID_COLUMN = LONGMEMEVAL_ID_COLUMN
    LONGMEMEVAL_VALUE_COLUMN = LONGMEMEVAL_VALUE_COLUMN
    LONGMEMEVAL_EXPECTED_ROWS = LONGMEMEVAL_EXPECTED_ROWS

    @staticmethod
    def load_longmemeval_anchor():
        return SimpleNamespace(sha256="0" * 64, sizes=())

    @staticmethod
    def _verify_plan_data_against_anchor(data, anchor):
        return _FakeProof()


class _FakeV6:
    @staticmethod
    def preflight(*args):
        return SimpleNamespace(fixtures=(), physical_copies=())


def exec_pinned_module(label, path, expected):
    if label == "v7_semantic_gate":
        return _FakeV7
    if label == "measurement_plan_guard":
        return _FakeGuard
    if label == "storage_adapter_preflight_v6":
        return _FakeV6
    raise AssertionError(f"unexpected label {label}")


def authenticate_fixed(path, expected, where, limit=None):
    return b"attacker-bytes"


def read_regular(path, limit, where):
    return b"attacker-bytes"
