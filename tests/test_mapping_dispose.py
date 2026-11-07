"""task 065 测试：mapping 各入口 engine.dispose() 异常路径 spy 断言（参数化）。

P2 清偿（reports/code-review-tracker-20261005.md）：dispose 异常路径测试
从「路径可达不炸」升级为 spy 断言（dispose 确实被调用），并补 task 037/040/046
后新增的入口（ja_trainer / en_reconcile / effect_tags run_tagging）。
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations

_CASE_RAW = object()  # 占位：需要 raw 的入口由 helper 注入 raw_dir


def _minimal_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "t.db"
    apply_migrations(db_path)
    return db_path


class _SpyEngine:
    """包装真实 Engine，统计 dispose 调用次数。"""

    def __init__(self, real: Any) -> None:
        self._real = real
        self.dispose_calls = 0

    def __getattr__(self, item: str) -> Any:
        return getattr(self._real, item)

    def dispose(self) -> None:
        self.dispose_calls += 1
        self._real.dispose()


class _nullctx:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *args: Any) -> bool:
        return False


# (module, func, call_args, call_kwargs, preload_patches)
CASES = [
    ("ptcgdb.mapping.en", "fill_en", (_CASE_RAW,), {}, None),
    (
        "ptcgdb.mapping.tcgdex", "resolve_en", (_CASE_RAW,), {},
        {"load_set_map": lambda *a, **k: {}, "load_subset_map": lambda *a, **k: {},
         "load_en_cards": lambda *a, **k: {}},
    ),
    (
        "ptcgdb.mapping.tcgdex", "reconcile_sets", (_CASE_RAW,), {},
        {"_load": lambda *a, **k: []},
    ),
    (
        "ptcgdb.mapping.ja", "fill_ja", (_CASE_RAW,), {},
        {
            "load_ja_species": lambda *a, **k: {},
            "load_en_species": lambda *a, **k: {},
            "load_ptcd_dex_index": lambda *a, **k: {},
            "resolve_en": lambda *a, **k: SimpleNamespace(tcgdex_ids={}),
        },
    ),
    (
        "ptcgdb.mapping.tera", "fill_tera", (_CASE_RAW,), {},
        {"_load_ptcd_set_map": lambda *a, **k: {},
         "_load_ptcd_tera_index": lambda *a, **k: {}},
    ),
    (
        "ptcgdb.mapping.ja_trainer", "fill_ja_trainer", (_CASE_RAW,), {},
        {"load_tcgdex_ja_names": lambda raw_dir: set(),
         "load_trainer_vocab": lambda *a, **k: []},
    ),
    (
        "ptcgdb.mapping.en_reconcile", "reconcile_en_fields", (_CASE_RAW,), {},
        {
            "load_en_type_map": lambda *a, **k: {},
            "load_tcgdex_to_ptcd": lambda raw_dir: {},
            "_load_ptcd_cards_by_set": lambda raw_dir: {},
            "build_ptcd_card_index": lambda *a, **k: ({}, set()),
        },
    ),
    ("ptcgdb.mapping.effect_tags", "run_tagging", (), {"dry_run": True}, None),
]


def _run_dispose_case(
    tmp_path: Path,
    module: str,
    func_name: str,
    call_args: tuple,
    call_kwargs: dict | None = None,
    preload_patches: dict[str, Any] | None = None,
) -> int:
    """engine 段注入 commit 异常，返回 dispose 调用次数。"""
    import importlib

    mod = importlib.import_module(module)
    func = getattr(mod, func_name)
    db_path = _minimal_db(tmp_path / "t.db")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(exist_ok=True)
    args = tuple(raw_dir if a is _CASE_RAW else a for a in call_args)

    spy = _SpyEngine(create_engine(f"sqlite:///{db_path}"))
    with (
        patch(f"{module}.create_engine", return_value=spy),
        patch.object(Session, "commit", side_effect=RuntimeError("forced")),
    ):
        with patch.multiple(module, **preload_patches) if preload_patches else _nullctx():
            try:
                func(db_path, *args, **(call_kwargs or {}))
            except RuntimeError:
                pass  # 注入的 commit 异常，预期路径
            except Exception:
                pass  # 前置加载缺夹具等异常同样须经过 finally dispose
    return spy.dispose_calls


@pytest.mark.parametrize(
    "module,func,args,kwargs,pre", CASES,
    ids=[f"{m}.{f}" for m, f, *_ in CASES],
)
def test_dispose_called_on_exception(tmp_path, module, func, args, kwargs, pre):
    """每个入口在异常路径（注入 commit 失败）都执行 engine.dispose()。"""
    calls = _run_dispose_case(tmp_path, module, func, args, kwargs, pre)
    assert calls >= 1, f"{module}.{func} 异常路径未调用 engine.dispose()"
