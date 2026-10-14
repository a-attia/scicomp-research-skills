#!/usr/bin/env python3
"""Static compatibility validator for the SKILL.md files in this catalog.

One command checks every skill against five profiles::

    python3 tools/validate_skills.py                     # whole catalog, all profiles
    python3 tools/validate_skills.py skills/hpc-skills/slurm
    python3 tools/validate_skills.py --profile codex --changed-since main --format github

Profiles: ``spec`` (the Agent Skills specification as enforced by the reference
validator skills-ref 0.1.1), ``claude-code`` (Claude Code CLI 2.1.259),
``codex`` (OpenAI Codex CLI 0.147.0 / 0.153.0), ``antigravity`` (Google
Antigravity CLI agy 1.1.25) and ``cursor`` (Cursor 3.18.25).

Rules
-----
Every finding names the rule it implements.  Each rule id, its profile, the
severities it can emit and what it checks are registered in ``RULES`` below.
Rules that cannot be checked statically (runtime state, user settings, install
location outside the skill directory) are not checked.

Install-layout assumption: ``unpack.sh`` installs each catalog skill as
``<root>/.claude/skills/<dirname>/`` or ``<root>/.agents/skills/<dirname>/``
(directory symlink or copy), so this validator checks everything that survives
that install (directory name, exact ``SKILL.md`` filename, file size, nested
``SKILL.md`` files, symlinked files, frontmatter dialect, body constructs,
name uniqueness across the catalog, the ``agents/openai.yaml`` sidecar) and
never where the repository checkout itself sits.

Severity policy: ``error`` = the harness would not load the skill, would load it
with missing required metadata, or skills-ref 0.1.1 would fail it;
``warning`` = the skill loads but a key is ignored, a value is silently altered,
or a documented limit / recommendation is exceeded; ``info`` = a note that
needs no action.  Exit status: 0 = no findings at the failing level (errors, or
warnings too with ``--strict``), 1 = findings at the failing level, 2 = usage or
internal error.

Runtime dependency: PyYAML only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections.abc import Hashable
from pathlib import Path
from typing import Callable, Iterable, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - reported as a usage error
    yaml = None  # type: ignore[assignment]

__all__ = [
    "Finding",
    "SkillContext",
    "SkillEntry",
    "discover_skills",
    "load_skill",
    "run_profiles",
    "main",
]

PROFILES: tuple[str, ...] = ("spec", "claude-code", "codex", "antigravity", "cursor")
SEVERITIES: tuple[str, ...] = ("error", "warning", "info")
_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}

SPEC_KEYS = frozenset({"name", "description", "license", "allowed-tools", "metadata", "compatibility"})
CLAUDE_KEYS = frozenset(
    {
        "name", "description", "model", "allowed-tools", "disallowed-tools", "disallowedTools",
        "argument-hint", "arguments", "disable-model-invocation", "user-invocable", "effort",
        "shell", "version", "when_to_use", "paths", "hooks", "context", "agent", "background",
        "metadata", "license", "compatibility",
    }
)
CODEX_KEYS = frozenset({"name", "description", "metadata"})
ANTIGRAVITY_KEYS = frozenset({"name", "description", "disable-model-invocation", "disable-slash-command", "metadata"})
CURSOR_KEYS = frozenset(
    {
        "name", "description", "paths", "globs", "disable-model-invocation", "alwaysApply",
        "environments", "disabled-environments", "metadata", "icon", "color",
    }
)
# Keys that change loading, listing or invocation behaviour in at least one
# harness.  When such a key is present and a profile ignores it, the author
# probably expected it to work, so the ignored-key note is a warning there.
BEHAVIORAL_KEYS = frozenset(
    {
        "disable-model-invocation", "user-invocable", "paths", "globs", "context", "agent",
        "background", "hooks", "model", "effort", "shell", "argument-hint", "arguments",
        "when_to_use", "disallowed-tools", "disallowedTools", "alwaysApply", "environments",
        "disabled-environments", "disable-slash-command", "hidden",
    }
)
ALL_KNOWN_KEYS = SPEC_KEYS | CLAUDE_KEYS | CODEX_KEYS | ANTIGRAVITY_KEYS | CURSOR_KEYS | {"requires"}

CLAUDE_BUNDLED_SKILLS = frozenset(
    {"doctor", "code-review", "verify", "run", "loop", "batch", "debug", "claude-api", "simplify",
     "security-review", "init"}
)
CLAUDE_TOOL_NAMES = frozenset(
    {
        "Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS", "WebFetch", "WebSearch",
        "Task", "Agent", "Skill", "AskUserQuestion", "NotebookEdit", "NotebookRead", "TodoWrite",
        "TodoRead", "BashOutput", "KillShell", "KillBash", "ExitPlanMode", "EnterPlanMode",
        "SlashCommand", "ListMcpResourcesTool", "ReadMcpResourceTool", "ToolSearch", "Monitor",
        "SendMessage", "Explore", "Plan",
    }
)
CLAUDE_SUBSTITUTIONS = frozenset({"CLAUDE_SKILL_DIR", "CLAUDE_PROJECT_DIR", "CLAUDE_SESSION_ID", "CLAUDE_EFFORT"})
CLAUDE_PLUGIN_SUBSTITUTIONS = frozenset({"CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA"})
CLAUDE_EFFORT_VALUES = frozenset({"low", "med", "medium", "high", "xhigh", "max"})
CLAUDE_BOOL_TRUE = frozenset({"1", "true", "yes", "on"})
CLAUDE_BOOL_FALSE = frozenset({"0", "false", "no", "off"})
CLAUDE_SIZE_LIMIT = 1_000_000
CLAUDE_LISTING_DESC_CAP = 1536
CLAUDE_LISTING_BUDGET = 8000

CODEX_ENV_VAR_NAMES = frozenset(
    {"PATH", "HOME", "USER", "SHELL", "PWD", "TMPDIR", "TEMP", "TMP", "LANG", "TERM", "XDG_CONFIG_HOME"}
)
CODEX_MENTION_RE = re.compile(r"[A-Za-z0-9_:-]+")
CODEX_MAX_DIRS_PER_ROOT = 2000
CODEX_MAX_ENTRIES_PER_ROOT = 20_000
CODEX_CATALOG_BUDGET = 8000
CODEX_CATALOG_DESC_CAP = 1024
PLUGIN_MANIFESTS = (".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json")

GOYAML_BOOL_UNQUOTED = frozenset(
    {"true", "True", "TRUE", "false", "False", "FALSE", "y", "Y", "yes", "Yes", "YES", "n", "N", "no",
     "No", "NO", "on", "On", "ON", "off", "Off", "OFF", "~", "null", "Null", "NULL", ""}
)
GOYAML_BOOL_QUOTED_OK = frozenset(
    {"y", "Y", "yes", "Yes", "YES", "n", "N", "no", "No", "NO", "on", "On", "ON", "off", "Off", "OFF"}
)
JSYAML_TRUE = frozenset({"true", "True", "TRUE"})
JSYAML_FALSE = frozenset({"false", "False", "FALSE"})
JSYAML_NULL = frozenset({"~", "null", "Null", "NULL", ""})
CURSOR_EXCLUDED_DIRS = frozenset({"node_modules", "__pycache__", "dist", "build"})
CURSOR_CODEX_SYSTEM_SKILLS = frozenset(
    {"imagegen", "openai-docs", "opneai-docs", "plugin-creator", "skill-creator", "skill-installer"}
)
CURSOR_COLORS = frozenset({"default", "green", "cyan", "blue", "purple", "magenta", "orange", "yellow", "red", "brand"})
CURSOR_DESC_CAP = 1536
CURSOR_PROMPT_BUDGET = 16_000
CURSOR_ATTACH_CAP = 100_000
CURSOR_ENVIRONMENTS = frozenset({"local", "cloud"})
CURSOR_SURFACES = frozenset({"ide", "cli"})

SPEC_NAME_PORTABLE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROL_CHARS_RE = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x84\x86-\x9f￾￿]")
UNICODE_SEPARATORS = {
    "\x85": "U+0085 NEL", " ": "U+2028 LINE SEPARATOR", " ": "U+2029 PARAGRAPH SEPARATOR",
    "​": "U+200B ZERO WIDTH SPACE", "﻿": "U+FEFF BOM", "\xa0": "U+00A0 NO-BREAK SPACE",
}
KNOWN_SKILL_SUBDIRS = ("scripts", "references", "assets", "templates", "examples", "docs", "resources")


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclasses.dataclass
class Finding:
    """One validator finding; ``message`` always starts with ``rule_id``."""

    profile: str
    rule_id: str
    severity: str
    skill: str
    file: str
    line: int | None
    message: str
    hint: str

    def as_dict(self) -> dict[str, object]:
        return {
            "profile": self.profile,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "skill": self.skill,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "hint": self.hint,
        }


@dataclasses.dataclass(frozen=True)
class RuleInfo:
    rule_id: str
    profile: str
    severities: tuple[str, ...]
    check: str


RULES: dict[str, RuleInfo] = {}


def _rule(rule_id: str, profile: str, severities: str, check: str) -> str:
    """Register a rule id (profile, severities it can emit, what is checked)."""

    sev = tuple(severities.split("/"))
    for s in sev:
        if s not in SEVERITIES:
            raise ValueError(f"bad severity {s!r} for {rule_id}")
    RULES[rule_id] = RuleInfo(rule_id, profile, sev, check)
    return rule_id


@dataclasses.dataclass(frozen=True)
class SkillEntry:
    """A discovered skill directory."""

    dir: Path
    skill_md: Path
    filename: str
    root: Path

    @property
    def name(self) -> str:
        return self.dir.name


@dataclasses.dataclass
class RawEntry:
    """One ``key: value`` or ``- item`` line of the frontmatter as written."""

    path: tuple[object, ...]
    line: int
    indent: int
    key: str | None
    raw: str
    style: str  # plain | single | double | block | flow | empty | stray
    extra_lines: list[str] = dataclasses.field(default_factory=list)
    quote_closed: bool = True
    quote_trailer: str = ""
    inner_quote_error: bool = False

    @property
    def top_key(self) -> str | None:
        return self.path[0] if self.path and isinstance(self.path[0], str) else None

    @property
    def plain_value(self) -> str:
        """The plain scalar without a trailing ``# comment``."""

        if self.style != "plain":
            return self.raw
        return re.split(r"[ \t]#", self.raw, maxsplit=1)[0].rstrip()


@dataclasses.dataclass
class FileRef:
    text: str
    line: int
    kind: str  # link | code | bare
    resolved: Path | None
    exists: bool
    depth: int
    absolute: bool
    parent_escape: bool


@dataclasses.dataclass
class OpenAIYaml:
    path: Path
    parsed: object | None
    error: str | None
    variants: list[str]


@dataclasses.dataclass
class SkillContext:
    """Everything one parse pass learns about a skill; profiles only read it."""

    entry: SkillEntry
    raw: bytes = b""
    size: int = 0
    read_error: str | None = None
    decode_error: str | None = None
    text: str = ""
    text_raw: str = ""  # BOM stripped, line endings NOT normalised
    has_bom: bool = False
    has_crlf: bool = False
    has_cr_only: bool = False
    has_nul: bool = False
    is_symlink: bool = False
    dangling_symlink: bool = False
    is_regular_file: bool = True
    readable: bool = True
    lines: list[str] = dataclasses.field(default_factory=list)
    line_count: int = 0
    # frontmatter
    opener: str | None = None
    fm_present: bool = False
    fm_close_index: int | None = None
    fm_close_line_raw: str = ""
    fm_lines: list[str] = dataclasses.field(default_factory=list)
    fm_first_line: int = 2  # file line of fm_lines[0]
    fm_text: str = ""
    fm_first_dash_line: int | None = None  # file line of the first inner line starting with ---
    fm_inner_dash_lines: list[int] = dataclasses.field(default_factory=list)  # lines with --- anywhere inside
    fm_codex_close_index: int | None = None
    fm_doc_end_lines: list[int] = dataclasses.field(default_factory=list)
    parsed: object = None
    parse_error: str | None = None
    parse_error_line: int | None = None
    data: dict = dataclasses.field(default_factory=dict)
    dup_keys: list[tuple[str, int, int]] = dataclasses.field(default_factory=list)
    flow_lines: list[int] = dataclasses.field(default_factory=list)
    anchors: list[str] = dataclasses.field(default_factory=list)
    aliases: list[int] = dataclasses.field(default_factory=list)
    tags: list[tuple[str, int]] = dataclasses.field(default_factory=list)
    merge_keys: list[int] = dataclasses.field(default_factory=list)
    key_lines: dict[str, int] = dataclasses.field(default_factory=dict)
    entries: list[RawEntry] = dataclasses.field(default_factory=list)
    claude_repair_parsed: object = None
    claude_repair_ok: bool | None = None
    codex_repair_parsed: object = None
    codex_repair_ok: bool | None = None
    # body
    body: str = ""
    body_start_line: int = 0
    body_lines: int = 0
    headings: list[tuple[int, str]] = dataclasses.field(default_factory=list)
    file_refs: list[FileRef] = dataclasses.field(default_factory=list)
    constructs: dict[str, list[int]] = dataclasses.field(default_factory=dict)
    substitutions: dict[str, list[int]] = dataclasses.field(default_factory=dict)
    # directory
    nested_skill_files: list[tuple[str, bool]] = dataclasses.field(default_factory=list)  # (relpath, hidden_or_excluded)
    case_variant_files: list[str] = dataclasses.field(default_factory=list)
    dir_count: int = 0
    entry_count: int = 0
    plugin_manifest: Path | None = None
    plugin_manifest_rel: str | None = None  # which of PLUGIN_MANIFESTS matched
    plugin_manifest_name: str | None = None
    openai_yaml: OpenAIYaml | None = None
    catalog_names: set[str] = dataclasses.field(default_factory=set)
    # The block skills-ref parses (content.split("---", 2)[1]) when it differs
    # from the line-anchored block every other harness uses; None when they agree.
    spec_view: "SkillContext | None" = None
    spec_cut_line: int | None = None  # file line where the substring split lands
    spec_cut_midline: bool = False  # the split lands inside a line, not on one

    # convenience -----------------------------------------------------------
    @property
    def name(self) -> str:
        return self.entry.name

    @property
    def rel_file(self) -> str:
        return _display_path(self.entry.skill_md)

    def top(self, key: str) -> RawEntry | None:
        for e in self.entries:
            if e.path == (key,):
                return e
        return None

    def under(self, key: str) -> list[RawEntry]:
        return [e for e in self.entries if len(e.path) > 1 and e.path[0] == key]

    def key_line(self, key: str) -> int | None:
        line = self.key_lines.get(key)
        if line is None:
            entry = self.top(key)
            line = entry.line if entry else None
        return line

    def value(self, key: str) -> object:
        return self.data.get(key) if isinstance(self.data, dict) else None

    def has_key(self, key: str) -> bool:
        return isinstance(self.data, dict) and key in self.data


_REPO_ROOT: Path | None = Path(__file__).resolve().parent.parent


def _display_path(path: Path) -> str:
    """Path relative to the repository root when inside it, else as given.

    Only the parent is resolved: a finding about a symlinked ``SKILL.md`` must
    name the link the contributor has to change, not the file it points at
    (which may not even be in the repository, where a GitHub annotation would
    silently drop it).
    """

    try:
        resolved = path.parent.resolve() / path.name
    except OSError:
        return str(path)
    if _REPO_ROOT is not None:
        try:
            return resolved.relative_to(_REPO_ROOT).as_posix()
        except ValueError:
            pass
    try:
        return resolved.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return str(resolved)


# --------------------------------------------------------------------------- #
# Discovery (mirrors skill-search/skill_search/catalog.py and unpack.sh)
# --------------------------------------------------------------------------- #


@dataclasses.dataclass
class Discovery:
    entries: list[SkillEntry]
    orphans: list[tuple[Path, str]]  # explicit inputs that are not skills
    case_variants: list[tuple[Path, list[str]]]  # dirs whose skill file only exists in another case
    hidden_skills: list[Path] = dataclasses.field(default_factory=list)  # dot-dirs the walk skips but harnesses load


def _skill_file_in(directory: Path) -> tuple[str | None, list[str]]:
    """Byte-exact ``SKILL.md`` / ``skill.md`` lookup via os.listdir (never Path.exists)."""

    try:
        names = os.listdir(directory)
    except OSError:
        return None, []
    exact = "SKILL.md" if "SKILL.md" in names else ("skill.md" if "skill.md" in names else None)
    variants = sorted(n for n in names if n.lower() == "skill.md" and n not in ("SKILL.md", "skill.md"))
    return exact, variants


def _walk_collection(root: Path, start: Path, entries: list[SkillEntry], variants: list[tuple[Path, list[str]]],
                     seen: set[Path], hidden: list[Path]) -> None:
    try:
        children = sorted(start.iterdir(), key=lambda p: p.name)
    except OSError:
        return
    for child in children:
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            # The walk skips hidden directories (like unpack.sh and skill-search),
            # but Claude Code and Antigravity load them, so record the miss.
            if _skill_file_in(child)[0] is not None and child not in hidden:
                hidden.append(child)
            continue
        exact, var = _skill_file_in(child)
        if exact is not None:
            key = child.resolve()
            if key in seen:
                continue
            seen.add(key)
            entries.append(SkillEntry(dir=child, skill_md=child / exact, filename=exact, root=root))
        else:
            if var:
                variants.append((child, var))
            _walk_collection(root, child, entries, variants, seen, hidden)


def discover_skills(paths: Sequence[str | Path]) -> Discovery:
    """Resolve inputs into skill directories.

    A path that is a skill directory (contains ``SKILL.md`` or ``skill.md``) is
    one skill; a ``SKILL.md`` path means its parent; anything else is walked
    recursively in sorted order, skipping hidden entries and stopping at the
    first directory that contains a skill file.  Raises ``FileNotFoundError``
    for a missing input.
    """

    entries: list[SkillEntry] = []
    orphans: list[tuple[Path, str]] = []
    variants: list[tuple[Path, list[str]]] = []
    hidden: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        path = Path(raw).expanduser()
        if not path.exists() and not path.is_symlink():
            raise FileNotFoundError(f"path does not exist: {path}")
        root = path.parent if path.is_file() else path
        if path.is_file() or (path.is_symlink() and not path.is_dir()):
            if path.name.lower() != "skill.md":
                orphans.append((path, "expected a skill directory or SKILL.md file"))
                continue
            directory = path.parent
        else:
            directory = path
        exact, var = _skill_file_in(directory)
        if exact is not None:
            key = directory.resolve()
            if key in seen:
                continue
            seen.add(key)
            entries.append(SkillEntry(dir=directory, skill_md=directory / exact, filename=exact, root=root))
            continue
        if path.is_file() or var:
            orphans.append((directory, "no file named exactly SKILL.md" + (f" (found {', '.join(var)})" if var else "")))
            if var:
                variants.append((directory, var))
            if path.is_file():
                continue
            continue
        before_entries, before_variants = len(entries), len(variants)
        _walk_collection(root, directory, entries, variants, seen, hidden)
        if len(entries) == before_entries and len(variants) == before_variants:
            # An explicit input that holds no skill at all: skills-ref rejects it
            # with "Missing required file: SKILL.md" instead of silently passing.
            orphans.append((directory, "no file named exactly SKILL.md and no skill directory below it"))
    return Discovery(entries=entries, orphans=orphans, case_variants=variants, hidden_skills=hidden)


# --------------------------------------------------------------------------- #
# YAML parsing with duplicate-key / flow / anchor / tag / merge-key detection
# --------------------------------------------------------------------------- #


def _make_loader_class():
    class _Loader(yaml.SafeLoader):  # type: ignore[misc,name-defined]
        def __init__(self, stream):
            super().__init__(stream)
            self.dup_keys: list[tuple[str, int, int]] = []
            self.flow_lines: list[int] = []
            self.alias_lines: list[int] = []
            self.tag_events: list[tuple[str, int]] = []
            self.merge_lines: list[int] = []
            self.anchor_names: list[str] = []

        def compose_node(self, parent, index):
            event = self.peek_event()
            line = event.start_mark.line + 1
            if isinstance(event, yaml.AliasEvent):
                self.alias_lines.append(line)
            else:
                tag = getattr(event, "tag", None)
                if tag is not None and tag != "!":
                    self.tag_events.append((tag, line))
                if getattr(event, "anchor", None):
                    self.anchor_names.append(event.anchor)
                if isinstance(event, (yaml.SequenceStartEvent, yaml.MappingStartEvent)) and event.flow_style:
                    self.flow_lines.append(line)
            return super().compose_node(parent, index)

        def construct_mapping(self, node, deep=False):
            seen: dict[object, int] = {}
            for key_node, _value_node in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    self.merge_lines.append(key_node.start_mark.line + 1)
                    continue
                try:
                    key = self.construct_object(key_node, deep=True)
                except yaml.YAMLError:
                    continue
                if not isinstance(key, Hashable):
                    continue
                line = key_node.start_mark.line + 1
                if key in seen:
                    self.dup_keys.append((str(key), line, seen[key]))
                else:
                    seen[key] = line
            return super().construct_mapping(node, deep)

    return _Loader


_LOADER_CLASS = None


def _yaml_error_text(exc: Exception) -> tuple[str, int | None]:
    problem = getattr(exc, "problem", None)
    context = getattr(exc, "context", None)
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    line = (mark.line + 1) if mark is not None else None
    parts = [p for p in (context, problem) if p]
    text = "; ".join(parts) if parts else str(exc).splitlines()[0]
    return text, line


def parse_yaml(text: str) -> tuple[object, str | None, int | None, object | None, object]:
    """Parse ``text`` with the detecting loader.

    Returns (parsed, error, error_line, loader, root_node).  ``parsed`` is the
    constructed document (``None`` for an empty document).
    """

    global _LOADER_CLASS
    if yaml is None:
        raise RuntimeError("PyYAML is not installed")
    if _LOADER_CLASS is None:
        _LOADER_CLASS = _make_loader_class()
    loader = None
    node = None
    try:
        # The constructor already scans the stream: a control character raises
        # yaml.reader.ReaderError here, so it must sit inside the try as well.
        loader = _LOADER_CLASS(text)
        node = loader.get_single_node()
        parsed = loader.construct_document(node) if node is not None else None
        return parsed, None, None, loader, node
    except yaml.YAMLError as exc:
        message, line = _yaml_error_text(exc)
        return None, message, line, loader, node
    except (ValueError, TypeError, OverflowError) as exc:  # e.g. bad timestamps
        return None, f"{type(exc).__name__}: {exc}", None, loader, node
    finally:
        if loader is not None:
            loader.dispose()


def _safe_load(text: str) -> tuple[bool, object]:
    try:
        return True, yaml.safe_load(text)
    except yaml.YAMLError:
        return False, None
    except (ValueError, TypeError, OverflowError):
        return False, None


_CLAUDE_HAZARD_RE = re.compile(r"[{}\[\]*&#!|>%@`]|: ")


def claude_repair(text: str) -> str:
    """Emulate Claude Code's YAML repair pass (re-quote hazardous single-line values, expand leading tabs)."""

    out: list[str] = []
    for line in text.split("\n"):
        match = re.match(r"^([a-zA-Z_-]+):\s+(.+)$", line)
        if match:
            key, value = match.group(1), match.group(2)
            fully_quoted = (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))
            if not fully_quoted:
                ok, loaded = _safe_load(value)
                if not (ok and isinstance(loaded, list)) and _CLAUDE_HAZARD_RE.search(value):
                    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                    out.append(f'{key}: "{escaped}"')
                    continue
        out.append(line)
    repaired = "\n".join(out)
    return re.sub(r"^\t+", lambda m: "  " * len(m.group(0)), repaired, flags=re.MULTILINE)


def codex_repair(text: str) -> str:
    """Emulate Codex's one-shot colon repair (single-quote ``key: a: b`` style plain scalars)."""

    out: list[str] = []
    for line in text.split("\n"):
        match = re.match(r"^([ \t]*[^\s#\-][^:]*?:)([ \t]+)(.*)$", line)
        if match and match.group(3):
            value = match.group(3)
            if value[0] not in "\"'|>":
                parts = re.split(r"([ \t]#)", value, maxsplit=1)
                scalar = parts[0].rstrip()
                tail = "".join(parts[1:])
                colon = re.search(r":[ \t]", scalar) is not None
                flow_like = scalar[:1] in ("[", "{", "@", "`") and not _safe_load(scalar)[0]
                if scalar and (colon or flow_like):
                    quoted = "'" + scalar.replace("'", "''") + "'"
                    line = f"{match.group(1)}{match.group(2)}{quoted}{(' ' + tail.lstrip()) if tail else ''}"
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Frontmatter lexer (raw scalar text per key, for parser-dialect checks)
# --------------------------------------------------------------------------- #

_KEY_RE = re.compile(
    r"""^(?P<key>"(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^\s"'#\-?\[\]{},&*!|>%@`][^:]*?)[ \t]*:(?:[ \t]+(?P<val>.*)|[ \t]*)$"""
)
_ITEM_RE = re.compile(r"^-(?:[ \t]+(?P<val>.*)|[ \t]*)$")
_BLOCK_HEADER_RE = re.compile(r"^[|>][+-]?[1-9]?[+-]?(?:[ \t]+#.*)?[ \t]*$")


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _classify(raw: str) -> str:
    if raw == "":
        return "empty"
    first = raw[0]
    if first == '"':
        return "double"
    if first == "'":
        return "single"
    if first in "[{":
        return "flow"
    if _BLOCK_HEADER_RE.match(raw):
        return "block"
    return "plain"


def _unquote_key(key: str) -> str:
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        inner = key[1:-1]
        return inner.replace("''", "'") if key[0] == "'" else inner.replace('\\"', '"')
    return key.strip()


def _check_quote(text: str, style: str) -> tuple[bool, str, bool]:
    """(closed, trailer_after_close, inner_error) for a quoted scalar starting at text[0]."""

    quote = '"' if style == "double" else "'"
    i = 1
    while i < len(text):
        ch = text[i]
        if style == "double" and ch == "\\":
            i += 2
            continue
        if ch == quote:
            if style == "single" and i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            trailer = text[i + 1 :].strip()
            return True, trailer, bool(trailer) and not trailer.startswith("#")
        i += 1
    return False, "", False


def _bracket_delta(text: str) -> int:
    depth = 0
    quote: str | None = None
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
    return depth


def _looks_structural(line: str) -> bool:
    content = line.strip()
    return bool(_ITEM_RE.match(content) or _KEY_RE.match(content))


def lex_frontmatter(fm_lines: Sequence[str], first_file_line: int = 2) -> list[RawEntry]:
    """Record every ``key: value`` / ``- item`` line with its raw scalar text and style."""

    entries: list[RawEntry] = []
    stack: list[tuple[int, tuple[object, ...]]] = []
    counters: dict[tuple[object, ...], int] = {}
    i, n = 0, len(fm_lines)
    while i < n:
        line = fm_lines[i]
        file_line = first_file_line + i
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = _indent_of(line)
        content = line[indent:]
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else ()
        m_item = _ITEM_RE.match(content)
        m_key = None if m_item else _KEY_RE.match(content)
        if m_item:
            idx = counters.get(parent, 0)
            counters[parent] = idx + 1
            path = parent + (idx,)
            raw = (m_item.group("val") or "").rstrip()
            m_inner = _KEY_RE.match(raw) if raw and raw[0] not in "\"'[{|>" else None
            if m_inner:
                key = _unquote_key(m_inner.group("key"))
                raw2 = (m_inner.group("val") or "").rstrip()
                entry = RawEntry(path + (key,), file_line, indent + 2, key, raw2, _classify(raw2))
                stack.append((indent, path))
                if entry.style == "empty":
                    stack.append((indent + 2, path + (key,)))
            else:
                entry = RawEntry(path, file_line, indent, None, raw, _classify(raw))
                if entry.style == "empty":
                    stack.append((indent, path))
        elif m_key:
            key = _unquote_key(m_key.group("key"))
            raw = (m_key.group("val") or "").rstrip()
            path = parent + (key,)
            entry = RawEntry(path, file_line, indent, key, raw, _classify(raw))
            if entry.style == "empty":
                stack.append((indent, path))
        else:
            entry = RawEntry(parent + (f"?{file_line}",), file_line, indent, None, content.rstrip(), "stray")
        i += 1
        if entry.style == "block":
            while i < n and (not fm_lines[i].strip() or _indent_of(fm_lines[i]) > entry.indent):
                entry.extra_lines.append(fm_lines[i])
                i += 1
        elif entry.style in ("single", "double"):
            closed, trailer, inner_err = _check_quote(entry.raw, entry.style)
            while not closed and i < n:
                entry.extra_lines.append(fm_lines[i])
                i += 1
                closed, trailer, inner_err = _check_quote(entry.raw + "\n" + "\n".join(entry.extra_lines), entry.style)
            entry.quote_closed, entry.quote_trailer, entry.inner_quote_error = closed, trailer, inner_err
        elif entry.style == "plain":
            while i < n and fm_lines[i].strip() and _indent_of(fm_lines[i]) > entry.indent and not _looks_structural(fm_lines[i]):
                entry.extra_lines.append(fm_lines[i])
                i += 1
        elif entry.style == "flow":
            depth = _bracket_delta(entry.raw)
            while depth > 0 and i < n:
                entry.extra_lines.append(fm_lines[i])
                depth += _bracket_delta(fm_lines[i])
                i += 1
        entries.append(entry)
    return entries


# --------------------------------------------------------------------------- #
# Shared parse pass
# --------------------------------------------------------------------------- #

_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
_BARE_PATH_RE = re.compile(r"(?<![\w/.$@{-])((?:scripts|references|assets|templates|examples|docs|resources)/[\w./-]+)")
_PATH_LIKE_RE = re.compile(
    r"^(?:\./)?[\w.@-]+(?:/[\w.@-]+)+/?$"
    r"|^[\w.-]+\.(?:md|py|sh|txt|json|ya?ml|toml|csv|ipynb|j2|jinja2?|cfg|ini|R|jl|lua|f90|F90|c|cc|cpp|h|hpp|rs|go|js|ts|tsv|xml|html|css)$"
)
_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_SKILL_DIR_PREFIX_RE = re.compile(r"^\$\{?CLAUDE_SKILL_DIR\}?/")
_CONSTRUCT_PATTERNS: dict[str, re.Pattern[str]] = {
    "arguments": re.compile(r"\$ARGUMENTS(?:\[\d+\])?"),
    "inline_shell": re.compile(r"(?:^|(?<=\s))!`[^`]+`"),
    "claude_dir": re.compile(r"(?<![\w-])\.claude/"),
    "claude_tools": re.compile(
        r"\b(?:Skill tool|AskUserQuestion|TodoWrite|NotebookEdit|MultiEdit|BashOutput|KillShell|SlashCommand"
        r"|EnterPlanMode|ExitPlanMode|the Task tool|Agent tool)\b|\bBash\([^)\n]*\)"
    ),
    "base_directory": re.compile(r"Base directory for this skill"),
}
_POSITIONAL_RE = re.compile(r"(?<![\w$])\$\d+(?!\w)")
_SUBST_RE = re.compile(r"\$\{(CLAUDE_[A-Z_]+)\}")
_SLASH_RE = re.compile(r"(?<![\w/.:~$@-])/([a-z0-9]+(?:-[a-z0-9]+)*)\b")
_DOLLAR_RE = re.compile(r"(?<![\w$])\$([a-z0-9]+(?:-[a-z0-9]+)+)\b")
_TODO_RE = re.compile(r"^ {0,3}\[TODO:[^\n]*\]")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _normalize_ref(target: str) -> str:
    target = target.strip().strip("<>")
    target = _SKILL_DIR_PREFIX_RE.sub("", target)
    return target.rstrip(".,;:)")


def _make_ref(skill_dir: Path, text: str, line: int, kind: str) -> FileRef | None:
    if not text or _URL_RE.match(text) or text.startswith("#") or any(ch in text for ch in "*?{}<>|$"):
        return None
    absolute = text.startswith(("/", "~"))
    parts = [p for p in text.split("/") if p not in ("", ".")]
    parent_escape = ".." in parts
    resolved: Path | None = None
    exists = False
    if not absolute and not parent_escape:
        resolved = skill_dir.joinpath(*parts) if parts else skill_dir
        try:
            exists = resolved.exists()
        except OSError:
            exists = False
    depth = max(len(parts) - 1, 0)
    return FileRef(text, line, kind, resolved, exists, depth, absolute, parent_escape)


def _scan_body(ctx: SkillContext) -> None:
    body = ctx.body
    ctx.body_lines = len(body.splitlines())
    skill_dir = ctx.entry.dir
    refs: dict[str, FileRef] = {}
    fence_open = False
    todo_lines: list[int] = []
    for offset, line in enumerate(body.split("\n")):
        file_line = ctx.body_start_line + offset
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if stripped.startswith("```!"):
                ctx.constructs.setdefault("shell_fence", []).append(file_line)
            fence_open = not fence_open
            continue
        if not fence_open:
            heading = _HEADING_RE.match(line)
            if heading:
                ctx.headings.append((file_line, heading.group(2).strip()))
            if _TODO_RE.match(line):
                todo_lines.append(file_line)
        for match in _MD_LINK_RE.finditer(line):
            ref = _make_ref(skill_dir, _normalize_ref(match.group(1)), file_line, "link")
            if ref and ref.text not in refs:
                refs[ref.text] = ref
        for match in _CODE_SPAN_RE.finditer(line):
            for token in match.group(1).split():
                token = _normalize_ref(token)
                if _PATH_LIKE_RE.match(token):
                    ref = _make_ref(skill_dir, token, file_line, "code")
                    if ref and ref.text not in refs:
                        refs[ref.text] = ref
        plain = _CODE_SPAN_RE.sub(" ", line)
        for match in _BARE_PATH_RE.finditer(plain):
            ref = _make_ref(skill_dir, _normalize_ref(match.group(1)), file_line, "bare")
            if ref and ref.text not in refs:
                refs[ref.text] = ref
        for name, pattern in _CONSTRUCT_PATTERNS.items():
            if pattern.search(line):
                ctx.constructs.setdefault(name, []).append(file_line)
        # A bare $1 is a Claude Code positional substitution in prose, but a
        # shell/awk positional parameter inside a fence ("awk '{print $4}'") -
        # only flag it outside code fences.  $ARGUMENTS is flagged everywhere.
        if not fence_open and _POSITIONAL_RE.search(line):
            ctx.constructs.setdefault("arguments", []).append(file_line)
        for match in _SUBST_RE.finditer(line):
            ctx.substitutions.setdefault(match.group(1), []).append(file_line)
        for match in _SLASH_RE.finditer(line):
            ctx.constructs.setdefault("slash:" + match.group(1), []).append(file_line)
        for match in _DOLLAR_RE.finditer(line):
            ctx.constructs.setdefault("dollar:" + match.group(1), []).append(file_line)
    if todo_lines:
        ctx.constructs["todo"] = todo_lines
    ctx.file_refs = list(refs.values())


def _scan_directory(ctx: SkillContext) -> None:
    top = ctx.entry.dir
    try:
        top_names = os.listdir(top)
    except OSError:
        return
    ctx.case_variant_files = sorted(n for n in top_names if n.lower() == "skill.md" and n not in ("SKILL.md", "skill.md"))
    for root, dirs, files in os.walk(top):
        rel_parts = Path(root).relative_to(top).parts
        hidden = any(p.startswith(".") for p in rel_parts)
        excluded = any(p in CURSOR_EXCLUDED_DIRS for p in rel_parts)
        ctx.dir_count += len(dirs)
        ctx.entry_count += len(dirs) + len(files)
        if rel_parts:
            for f in files:
                if f == "SKILL.md":
                    ctx.nested_skill_files.append(("/".join(rel_parts + (f,)), hidden or excluded))
        if ctx.entry_count > CODEX_MAX_ENTRIES_PER_ROOT + 1:
            break
    ctx.nested_skill_files.sort()
    # agents/openai.yaml sidecar (Codex)
    agents_dirs = [n for n in top_names if n.lower() == "agents" and (top / n).is_dir()]
    variants: list[str] = []
    exact_exists = False
    for d in agents_dirs:
        try:
            inner = os.listdir(top / d)
        except OSError:
            continue
        for f in inner:
            # Codex probes exactly agents/openai.yaml; `Agents/`, `OpenAI.yaml`
            # and the .yml spelling are all invisible to it on Linux.
            if f.lower() in ("openai.yaml", "openai.yml"):
                if d == "agents" and f == "openai.yaml":
                    exact_exists = True
                else:
                    variants.append(f"{d}/{f}")
    if exact_exists or variants:
        path = top / "agents" / "openai.yaml"
        parsed: object = None
        error: str | None = None
        if exact_exists:
            try:
                parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError) as exc:
                error = f"cannot read: {exc}"
            except yaml.YAMLError as exc:
                error = _yaml_error_text(exc)[0]
        ctx.openai_yaml = OpenAIYaml(path, parsed, error, sorted(variants))
    # Plugin manifest inside the skill directory.  Codex searches upward without
    # limit, but only the skill directory itself is copied or symlinked into
    # <root>/.agents/skills/<dirname>/, so a manifest in a repository ancestor
    # never reaches the install; searching upward would also make the result a
    # function of the path the contributor typed rather than of the skill.
    current = top.resolve()
    for rel in PLUGIN_MANIFESTS:
        candidate = current / rel
        if candidate.is_file():
            ctx.plugin_manifest = candidate
            ctx.plugin_manifest_rel = rel
            try:
                manifest = json.loads(candidate.read_text(encoding="utf-8"))
                name = manifest.get("name") if isinstance(manifest, dict) else None
                ctx.plugin_manifest_name = name.strip() if isinstance(name, str) and name.strip() else current.name
            except (OSError, ValueError, UnicodeDecodeError):
                ctx.plugin_manifest_name = None
            break


def load_skill(entry: SkillEntry, *, catalog_names: Iterable[str] = ()) -> SkillContext:
    """Read, decode, split and parse one skill once; every profile reads the result."""

    ctx = SkillContext(entry=entry, catalog_names=set(catalog_names))
    path = entry.skill_md
    ctx.is_symlink = path.is_symlink()
    _scan_directory(ctx)
    if ctx.is_symlink and not path.exists():
        ctx.dangling_symlink = True
        ctx.read_error = "dangling symlink"
        return ctx
    if not path.is_file():
        ctx.is_regular_file = False
        ctx.read_error = "not a regular file"
        return ctx
    ctx.readable = os.access(path, os.R_OK)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        ctx.read_error = str(exc)
        ctx.readable = False
        return ctx
    ctx.raw = raw
    ctx.size = len(raw)
    ctx.has_bom = raw.startswith(b"\xef\xbb\xbf")
    ctx.has_nul = b"\x00" in raw
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        ctx.decode_error = f"invalid UTF-8 at byte {exc.start}"
        text = raw.decode("utf-8", errors="replace")
    if ctx.has_bom:
        text = text[1:]
    ctx.has_crlf = "\r\n" in text
    ctx.has_cr_only = re.search(r"\r(?!\n)", text) is not None
    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    ctx.text = norm
    lines = norm.split("\n")
    ctx.lines = lines
    ctx.line_count = len(norm.splitlines())
    ctx.body = norm
    ctx.body_start_line = 1
    ctx.text_raw = text
    if lines and lines[0].startswith("---"):
        ctx.opener = lines[0]
        close: int | None = None
        for i in range(1, len(lines)):
            if lines[i].rstrip() == "---":
                close = i
                break
        if close is None:
            for i in range(1, len(lines)):
                if lines[i].startswith("---"):
                    close = i
                    break
        if close is not None:
            _fill_frontmatter(ctx, lines[1:close], 2, close, lines[close], "\n".join(lines[close + 1 :]))
    _scan_body(ctx)
    if ctx.opener is not None:
        _build_spec_view(ctx)
    return ctx


def _fill_frontmatter(ctx: SkillContext, fm_lines: list[str], first_line: int, close_index: int | None,
                      close_raw: str, body: str) -> None:
    """Record and parse one frontmatter block on ``ctx`` (shared by the spec view)."""

    ctx.fm_present = True
    ctx.fm_close_index = close_index
    ctx.fm_close_line_raw = close_raw
    ctx.fm_lines = fm_lines
    ctx.fm_first_line = first_line
    # Keep the line break before the closing delimiter: skills-ref parses
    # everything between the delimiters, so a block scalar that is the
    # last key keeps its trailing newline (it counts toward the limits).
    ctx.fm_text = "\n".join(fm_lines) + "\n"
    for j, l in enumerate(fm_lines):
        file_line = first_line + j
        if "---" in l:
            ctx.fm_inner_dash_lines.append(file_line)
            if l.startswith("---") and ctx.fm_first_dash_line is None:
                ctx.fm_first_dash_line = file_line
        if l.strip() == "---" and ctx.fm_codex_close_index is None:
            ctx.fm_codex_close_index = file_line - 1
        if l.rstrip() == "...":
            ctx.fm_doc_end_lines.append(file_line)
    ctx.body = body
    # Without a closing line the split lands inside the last line of the block,
    # so the body continues on that same file line.
    ctx.body_start_line = (close_index + 2) if close_index is not None else first_line + len(fm_lines) - 1
    parsed, error, err_line, loader, node = parse_yaml(ctx.fm_text)
    ctx.parsed = parsed
    ctx.parse_error = error
    ctx.parse_error_line = (err_line + first_line - 1) if err_line is not None else None
    if loader is not None:
        ctx.dup_keys = [(k, l + first_line - 1, first + first_line - 1) for k, l, first in loader.dup_keys]
        ctx.flow_lines = [l + first_line - 1 for l in loader.flow_lines]
        ctx.aliases = [l + first_line - 1 for l in loader.alias_lines]
        ctx.tags = [(t, l + first_line - 1) for t, l in loader.tag_events]
        ctx.merge_keys = [l + first_line - 1 for l in loader.merge_lines]
        ctx.anchors = list(loader.anchor_names)
    if isinstance(parsed, dict):
        ctx.data = parsed
    if node is not None and isinstance(node, yaml.MappingNode):
        for key_node, _ in node.value:
            if isinstance(key_node, yaml.ScalarNode) and key_node.value not in ctx.key_lines:
                ctx.key_lines[str(key_node.value)] = key_node.start_mark.line + first_line
    ctx.entries = lex_frontmatter(fm_lines, first_line)
    if error is not None:
        ok, value = _safe_load(claude_repair(ctx.fm_text))
        ctx.claude_repair_ok, ctx.claude_repair_parsed = ok, value
        ok, value = _safe_load(codex_repair(ctx.fm_text))
        ctx.codex_repair_ok, ctx.codex_repair_parsed = ok, value


def _build_spec_view(ctx: SkillContext) -> None:
    """Attach the block skills-ref parses when it differs from the line-anchored one.

    ``parse_frontmatter`` does ``content.split("---", 2)``, so the block starts
    right after the first three bytes (``---name: foo`` keeps the first key) and
    ends at the next ``---`` substring anywhere (an indented ``  ---`` closes it,
    and so does a ``---`` in the middle of a value).  Every other harness scans
    lines, so this second view is spec-only.
    """

    opener_rest = (ctx.opener or "")[3:]
    merged = bool(opener_rest.strip()) and not opener_rest.lstrip().startswith("#")
    if ctx.fm_present and not merged:
        return
    block, sep, _rest = ctx.text[3:].partition("---")
    if not sep:
        return  # no closing '---' anywhere: spec-fm-closing-delimiter
    view = dataclasses.replace(ctx, raw=b"", spec_view=None)
    for field in ("fm_inner_dash_lines", "fm_doc_end_lines", "dup_keys", "flow_lines", "anchors", "aliases",
                  "tags", "merge_keys", "entries", "file_refs", "headings"):
        setattr(view, field, [])
    view.key_lines, view.constructs, view.substitutions, view.data = {}, {}, {}, {}
    view.fm_first_dash_line = view.fm_codex_close_index = None
    view.parsed = view.parse_error = view.parse_error_line = None
    view.claude_repair_ok = view.codex_repair_ok = None
    fm_lines = block.split("\n")
    cut_line = len(fm_lines)  # the file line the split lands on
    ctx.spec_cut_line = cut_line
    ctx.spec_cut_midline = bool(fm_lines[-1].strip())
    _fill_frontmatter(view, fm_lines, 1, None, "", ctx.text[3 + len(block) + 3 :])
    _scan_body(view)
    ctx.spec_view = view


# --------------------------------------------------------------------------- #
# Rule helpers shared by the profiles
# --------------------------------------------------------------------------- #


class Emitter:
    """Collects findings for one (skill, profile) pair."""

    def __init__(self, ctx: SkillContext, profile: str):
        self.ctx = ctx
        self.profile = profile
        self.findings: list[Finding] = []

    def add(self, rule_id: str, severity: str, text: str, hint: str, *, line: int | None = None,
            file: str | None = None, skill: str | None = None) -> None:
        info = RULES.get(rule_id)
        if info is None:
            raise KeyError(f"unregistered rule id {rule_id}")
        if info.profile != self.profile:
            raise ValueError(f"{rule_id} belongs to profile {info.profile}, not {self.profile}")
        if severity not in info.severities:
            raise ValueError(f"{rule_id} may not emit severity {severity}")
        self.findings.append(
            Finding(self.profile, rule_id, severity, skill or self.ctx.name, file if file is not None else self.ctx.rel_file,
                    line, f"{rule_id}: {text}", hint)
        )

    def line(self, key: str) -> int | None:
        return self.ctx.key_line(key)


def _raw_value(ctx: SkillContext, key: str, limit: int = 30) -> str:
    """The value as written in the file when available, else a short repr."""

    entry = ctx.top(key)
    if entry is not None and entry.style not in ("empty", "stray"):
        return _short(entry.raw, limit)
    return _short(ctx.value(key), limit)


def _short(value: object, limit: int = 60) -> str:
    text = value if isinstance(value, str) else repr(value)
    text = text.replace("\n", "\\n")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _type_name(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "mapping"
    return type(value).__name__


def _is_scalar(value: object) -> bool:
    return not isinstance(value, (list, dict))


def _yaml11_kind(raw: str) -> str | None:
    """Kind PyYAML (YAML 1.1) gives a plain scalar when it is not a string, else None."""

    ok, value = _safe_load(raw)
    if not ok or isinstance(value, str):
        return None
    return _type_name(value) if not hasattr(value, "isoformat") else "timestamp"


_JS_INT_RE = re.compile(r"^[-+]?(?:0b[01_]+|0x[0-9a-fA-F_]+|0o?[0-7_]+|(?:0|[1-9][0-9_]*)|[1-9][0-9_]*(?::[0-5]?[0-9])+)$")
_JS_FLOAT_RE = re.compile(
    r"^[-+]?(?:(?:\.[0-9_]+|[0-9][0-9_]*(?:\.[0-9_]*)?)(?:[eE][-+]?[0-9]+)?|[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*|\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$"
)
_JS_TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt ]|$)")


def _jsyaml_kind(raw: str) -> str:
    """Type js-yaml 3 (DEFAULT_SAFE_SCHEMA) assigns to a plain scalar."""

    if raw in JSYAML_TRUE or raw in JSYAML_FALSE:
        return "boolean"
    if raw in JSYAML_NULL:
        return "null"
    if _JS_INT_RE.match(raw) or (_JS_FLOAT_RE.match(raw) and raw not in (".", "-", "+")):
        return "number"
    if _JS_TIMESTAMP_RE.match(raw):
        return "timestamp"
    return "string"


def _goyaml_bool_ok(entry: RawEntry) -> bool:
    raw = entry.raw.strip()
    if entry.style == "plain":
        return entry.plain_value.strip() in GOYAML_BOOL_UNQUOTED
    if entry.style == "empty":
        return True
    if entry.style in ("single", "double") and entry.quote_closed and not entry.inner_quote_error:
        return raw[1:-1] in GOYAML_BOOL_QUOTED_OK
    return False


def _claude_bool(value: object) -> bool | None:
    """Claude Code's boolean coercion (ZG): true/false/yes/no/on/off/1/0 in any case."""

    if isinstance(value, bool):
        return value
    if not isinstance(value, (str, int, float)):
        return None
    text = str(value).strip().lower()
    if text in CLAUDE_BOOL_TRUE:
        return True
    if text in CLAUDE_BOOL_FALSE:
        return False
    return None


@dataclasses.dataclass
class Hazards:
    lead: str | None = None  # the offending first character
    lead_kind: str = ""
    colon_space: bool = False
    trailing_colon: bool = False
    space_hash: bool = False
    quote_then_text: bool = False
    unterminated_quote: bool = False


_LEAD_KINDS = {
    "%": "directive", "@": "reserved", "`": "reserved", "*": "alias", "&": "anchor", "!": "tag",
    "[": "flow sequence", "{": "flow mapping", "]": "flow", "}": "flow", ",": "flow", "|": "block indicator",
    ">": "block indicator", "#": "comment", ":": "mapping value",
}


def _hazards(entry: RawEntry) -> Hazards:
    h = Hazards()
    if entry.style == "plain":
        raw = entry.raw
        first = raw[0]
        if first in "%@`*&![{]},|>":
            h.lead, h.lead_kind = first, _LEAD_KINDS[first]
        elif first == "-" and (len(raw) == 1 or raw[1] in " \t"):
            h.lead, h.lead_kind = "-", "sequence entry"
        elif first == "?" and (len(raw) == 1 or raw[1] in " \t"):
            h.lead, h.lead_kind = "?", "mapping key"
        elif first == ":" and (len(raw) == 1 or raw[1] in " \t"):
            h.lead, h.lead_kind = ":", "mapping value"
        text = entry.plain_value + ("\n" + "\n".join(entry.extra_lines) if entry.extra_lines else "")
        h.colon_space = re.search(r":[ \t]", text) is not None or "\n" in text and re.search(r":\s*$", text, re.MULTILINE) is not None
        h.trailing_colon = entry.plain_value.endswith(":")
        h.space_hash = re.search(r"[ \t]#", raw) is not None
    elif entry.style in ("single", "double"):
        h.unterminated_quote = not entry.quote_closed
        h.quote_then_text = entry.inner_quote_error
    return h


def _walk_fm_lines(ctx: SkillContext):
    """Yield (file line, line, leading whitespace, value after 'key:', in_block).

    ``in_block`` marks a continuation line of a ``|`` / ``>`` block scalar, whose
    content is free text: a tab there is legal YAML 1.2 and parses on the first
    pass, so it is not indentation.  Block state is tracked on every line, not
    only on the lines that happen to contain a tab.
    """

    block_indent: int | None = None
    for j, line in enumerate(ctx.fm_lines):
        file_line = ctx.fm_first_line + j
        if block_indent is not None:
            if not line.strip() or _indent_of(line) > block_indent:
                lead = line[: len(line) - len(line.lstrip(" \t"))]
                yield file_line, line, lead, "", True
                continue
            block_indent = None
        stripped = line.lstrip(" \t")
        lead = line[: len(line) - len(stripped)]
        m = _KEY_RE.match(stripped) or _ITEM_RE.match(stripped)
        val = (m.group("val") or "") if m else stripped
        if val and _BLOCK_HEADER_RE.match(val):
            block_indent = _indent_of(line)
        yield file_line, line, lead, val, False


def _tab_positions(ctx: SkillContext) -> list[tuple[int, str]]:
    """(file line, kind) for tabs in the frontmatter: kind is 'indent', 'comment', 'quoted', 'block' or 'value'."""

    out: list[tuple[int, str]] = []
    for file_line, line, lead, val, in_block in _walk_fm_lines(ctx):
        if "\t" not in line:
            continue
        if in_block:
            out.append((file_line, "block"))
        elif "\t" in lead:
            out.append((file_line, "indent"))
        elif line.lstrip(" \t").startswith("#"):
            out.append((file_line, "comment"))
        elif val.startswith(("'", '"')):
            out.append((file_line, "quoted"))
        elif val and _BLOCK_HEADER_RE.match(val):
            out.append((file_line, "value"))
        elif re.search(r"[ \t]#.*\t", line) and "\t" not in line.split("#", 1)[0]:
            out.append((file_line, "comment"))
        else:
            out.append((file_line, "value"))
    return out


def _tab_scan_error(message: str | None) -> bool:
    """True for the scanner error PyYAML raises for a tab it will not accept."""

    return bool(message) and "cannot start any token" in message and "\\t" in message


def _jsyaml_tab_throws(ctx: SkillContext) -> bool:
    """True when js-yaml 3 really throws on the frontmatter's tabs.

    js-yaml tolerates a tab before a top-level key, after a colon, inside a
    value, a comment or a quoted scalar, and mis-nests (but loads) a tab-indented
    mapping entry; only a tab-indented sequence item or block-scalar continuation
    line raises (cursor-frontmatter-tabs).
    """

    for _line, _raw, lead, val, in_block in _walk_fm_lines(ctx):
        if "\t" not in lead:
            continue
        if in_block or _ITEM_RE.match(_raw.lstrip(" \t")):
            return True
    return False


def _near_miss(key: str, canonical: Iterable[str]) -> str | None:
    norm = key.lower().replace("_", "").replace("-", "")
    for cand in canonical:
        if cand != key and cand.lower().replace("_", "").replace("-", "") == norm:
            return cand
    return None


def _split_tools(value: object) -> list[str]:
    """Claude Code's allowed-tools tokeniser: split on ',' and ' ' outside parentheses."""

    items: list[str] = []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = [v for v in value if isinstance(v, str)]
    tokens: list[str] = []
    for item in items:
        depth = 0
        current: list[str] = []
        for ch in item:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            if ch in ", " and depth == 0:
                if current:
                    tokens.append("".join(current))
                    current = []
                continue
            current.append(ch)
        if current:
            tokens.append("".join(current))
    return [t for t in tokens if t]


def _anchored(ctx: SkillContext, ref: FileRef) -> bool:
    """Only report missing targets that clearly point inside the skill."""

    parts = [p for p in ref.text.split("/") if p not in ("", ".")]
    if not parts:
        return False
    if ref.kind == "link" and not ref.text.startswith("./"):
        return True
    first = parts[0]
    if first in KNOWN_SKILL_SUBDIRS:
        return True
    try:
        return len(parts) > 1 and (ctx.entry.dir / first).exists()
    except OSError:
        return False


def _missing_refs(ctx: SkillContext) -> list[FileRef]:
    return [r for r in ctx.file_refs if r.resolved is not None and not r.exists and _anchored(ctx, r)]


def _desc_text(ctx: SkillContext) -> str | None:
    value = ctx.value("description")
    return value if isinstance(value, str) else None


def _has_when_cue(desc: str) -> bool:
    return re.search(r"\b(use|when)\b", desc, re.IGNORECASE) is not None


def _control_char_lines(ctx: SkillContext) -> list[int]:
    return [ctx.fm_first_line + j for j, line in enumerate(ctx.fm_lines) if CONTROL_CHARS_RE.search(line)]


def _separator_lines(ctx: SkillContext) -> list[tuple[int, str]]:
    out = []
    for j, line in enumerate(ctx.fm_lines):
        for ch, name in UNICODE_SEPARATORS.items():
            if ch in line:
                out.append((ctx.fm_first_line + j, name))
    return out


def _top_keys(ctx: SkillContext) -> list[str]:
    return [str(k) for k in ctx.data.keys()] if isinstance(ctx.data, dict) else []


def _utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def _fmt_lines(lines: Iterable[int], limit: int = 4) -> str:
    items = sorted(set(lines))
    shown = ", ".join(str(l) for l in items[:limit])
    return shown + (f" (+{len(items) - limit} more)" if len(items) > limit else "")


def _ignored_key_findings(e: Emitter, honored: Iterable[str], rule_ignored: str, rule_behavioral: str | None,
                          harness: str, consequence: dict[str, str], skip: Iterable[str] = ()) -> None:
    """Report keys the harness ignores: warning for behavioural keys, info for the rest."""

    honored_set = set(honored) | set(skip)
    ignored = [k for k in _top_keys(e.ctx) if k not in honored_set]
    behavioral = [k for k in ignored if k in BEHAVIORAL_KEYS]
    other = [k for k in ignored if k not in BEHAVIORAL_KEYS and k not in SPEC_KEYS]
    for key in behavioral:
        rid = rule_behavioral or rule_ignored
        note = consequence.get(key, "the key has no effect")
        e.add(rid, "warning", f"`{key}: {_raw_value(e.ctx, key)}` is ignored by {harness}: {note}",
              "expect the behaviour to differ from Claude Code; document it in the description if it matters", line=e.line(key))
    if other:
        e.add(rule_ignored, "info", f"keys ignored by {harness}: {', '.join(other)}",
              "no action needed; the keys are accepted but never read", line=e.line(other[0]))


# --------------------------------------------------------------------------- #
# Profile: spec (Agent Skills specification + skills-ref 0.1.1)
# --------------------------------------------------------------------------- #

_rule("spec-discovery-skill-md-required", "spec", "error/warning", "the skill directory holds a regular, resolvable file named SKILL.md (or skill.md); an explicit input without one is rejected (error); a nested SKILL.md is not a skill for skills-ref (warning)")
_rule("spec-discovery-case-insensitive-filesystem", "spec", "error", "a directory whose only skill file is a case variant (Skill.md, SKILL.MD) validates on macOS but fails on Linux; names are compared byte-exactly from os.listdir")
_rule("spec-discovery-exact-filename-for-clients", "spec", "warning", "the skill file is not named exactly SKILL.md (lowercase skill.md passes skills-ref but clients look for the exact name)")
_rule("spec-discovery-name-collisions", "spec", "error", "two skills in the catalog share a directory name or a frontmatter name (only one would load per scope; unpack.sh refuses to flatten)")
_rule("spec-discovery-symlink-dir-name", "spec", "error", "a symlinked SKILL.md resolves to an existing file (dangling links are 'Missing required file')")
_rule("spec-fm-must-start-with-dashes", "spec", "error", "the file starts with the bytes '---' (a BOM, blank line or leading text is rejected)")
_rule("spec-fm-closing-delimiter", "spec", "error", "a second '---' exists to close the frontmatter")
_rule("spec-fm-triple-dash-truncates", "spec", "error", "no '---' occurs inside the frontmatter block (skills-ref splits on the substring and silently truncates)")
_rule("spec-fm-delimiter-leniency-vs-clients", "spec", "warning", "the opening and closing delimiters are exactly '---' on their own lines (skills-ref is lenient, other parsers are not)")
_rule("spec-fm-must-be-mapping", "spec", "error", "the frontmatter parses to a non-empty YAML mapping")
_rule("spec-fm-no-flow-style", "spec", "error", "no flow collections ([...] / {...}) and no unquoted value starting with [ { , ] }")
_rule("spec-fm-no-anchors-aliases", "spec", "error", "no anchors (&x), aliases (*x) or unquoted values starting with * or &")
_rule("spec-fm-no-tags", "spec", "error", "no explicit tags (!!str, !x) or unquoted values starting with !")
_rule("spec-fm-no-duplicate-keys", "spec", "error", "no key appears twice in the same mapping")
_rule("spec-fm-tabs-structural", "spec", "error/warning", "no tab used as indentation or inside a plain value (error); tabs inside quoted scalars, block bodies or comments are noted (warning)")
_rule("spec-fm-scalars-are-strings", "spec", "warning", "an unquoted value that YAML 1.2 clients would type as a boolean, number or null (true, yes, 1.0, ~) is a string for skills-ref; quote it for consistent meaning")
_rule("spec-fm-plain-scalar-reserved-starts", "spec", "error/warning", "unquoted values do not start with % @ ` * & ! [ { | > , ] } '- ' '? ' ': ' and contain no ': ' or trailing ':' (error); ' #' truncates the value (warning)")
_rule("spec-fm-quoted-scalars", "spec", "error", "quoted values close on the same quote with no unescaped inner quote and nothing after the closing quote")
_rule("spec-fm-block-scalars-and-multiline", "spec", "info", "a description written as a block scalar keeps its final newline, which counts toward the 1024-character limit; '>-' avoids it")
_rule("spec-fm-control-characters-crash", "spec", "error", "no C0/C1 control character (other than tab, LF, CR), DEL or U+FFFE/U+FFFF in the frontmatter (skills-ref crashes)")
_rule("spec-fm-unicode-line-separators", "spec", "warning", "no NEL, U+2028/2029, zero-width space, mid-file BOM or NBSP in the frontmatter")
_rule("spec-fm-utf8-required", "spec", "error", "the file decodes as UTF-8")
_rule("spec-fm-keys-case-and-hyphen-exact", "spec", "error", "keys use the exact lowercase hyphenated spelling (Name, Description, allowed_tools are unexpected fields)")
_rule("spec-fm-sequence-indent-absorbed", "spec", "error", "no list item that absorbed a mis-indented sibling ('a - b' or an embedded newline)")
_rule("spec-fm-merge-keys", "spec", "warning", "no '<<' merge keys (accepted by strictyaml's ruamel core, treated differently by the other parsers)")
_rule("spec-keys-allowed-set", "spec", "error", "only name, description, license, allowed-tools, metadata and compatibility appear at the top level")
_rule("spec-keys-required-name-description", "spec", "error", "name and description are both present")
_rule("spec-keys-extensions-belong-in-metadata", "spec", "info", "client-specific keys would be spec-legal under metadata: (but Claude Code, Antigravity and Cursor honour only the top-level spelling)")
_rule("spec-keys-empty-optional-values", "spec", "warning", "an optional key that is present is not empty")
_rule("spec-name-nonempty-string", "spec", "error", "name is a non-empty string")
_rule("spec-name-length-1-64", "spec", "error", "NFKC-normalised name has at most 64 code points")
_rule("spec-name-lowercase", "spec", "error", "name equals name.lower()")
_rule("spec-name-charset-unicode-alnum-hyphen", "spec", "error/warning", "every character is alphanumeric or '-' (error); non-ASCII letters are accepted by skills-ref but flagged for portability (warning)")
_rule("spec-name-no-edge-hyphens", "spec", "error", "name does not start or end with '-'")
_rule("spec-name-no-consecutive-hyphens", "spec", "error", "name contains no '--'")
_rule("spec-name-must-match-directory", "spec", "error", "NFKC(name) equals the directory name byte-for-byte")
_rule("spec-name-nfkc-normalization", "spec", "warning", "name is already NFKC-normalised (compatibility characters are silently folded)")
_rule("spec-desc-nonempty-string", "spec", "error", "description is a non-empty string")
_rule("spec-desc-max-1024", "spec", "error", "the parsed (unstripped) description has at most 1024 code points")
_rule("spec-desc-block-scalar-trailing-newline", "spec", "error", "a block-scalar description of exactly 1024 visible characters exceeds the limit because the trailing newline counts")
_rule("spec-desc-content-guidance", "spec", "warning", "description says what the skill does and when to use it (a 'use'/'when' cue, at least 40 characters)")
_rule("spec-desc-unquoted-colon-space", "spec", "error", "an unquoted description contains no ': ' and does not end with ':'")
_rule("spec-compat-string-max-500", "spec", "error/warning", "compatibility, if present, is a string of 1-500 code points (empty is a warning)")
_rule("spec-license-freeform", "spec", "warning", "license, if present, is a non-empty string")
_rule("spec-metadata-string-map-coercion", "spec", "error", "metadata is a mapping of scalar string values (nested lists/mappings become Python reprs)")
_rule("spec-allowed-tools-space-separated-string", "spec", "warning", "allowed-tools is a non-empty space-separated string (comma form and YAML lists are the Claude Code dialect)")
_rule("spec-body-unrestricted-may-be-empty", "spec", "warning", "the body is not empty")
_rule("spec-body-under-500-lines", "spec", "warning", "SKILL.md has at most 500 lines")
_rule("spec-body-under-5000-tokens", "spec", "warning", "the body is under ~5000 tokens (len/4)")
_rule("spec-files-relative-paths-from-root", "spec", "warning", "relative file references from the body exist inside the skill; no absolute or ../ paths")
_rule("spec-files-one-level-deep", "spec", "info", "file references are one directory level deep from SKILL.md")
_rule("spec-sem-body-tokens-not-interpreted", "spec", "info", "$ARGUMENTS, ${CLAUDE_*} and !`command` in the body are client-specific and have no spec meaning")


def _map_spec_parse_error(message: str) -> str:
    low = message.lower()
    if "special characters" in low or "unacceptable character" in low:
        return "spec-fm-control-characters-crash"
    if "tab" in low or "\\t" in low:
        return "spec-fm-tabs-structural"
    if "alias" in low or "anchor" in low:
        return "spec-fm-no-anchors-aliases"
    if "tag" in low:
        return "spec-fm-no-tags"
    if "quoted scalar" in low or "block end" in low and "scalar" in low:
        return "spec-fm-quoted-scalars"
    if "mapping values are not allowed" in low:
        return "spec-fm-plain-scalar-reserved-starts"
    if "flow" in low or "','" in low or "']'" in low or "'}'" in low:
        return "spec-fm-no-flow-style"
    return "spec-fm-must-be-mapping"


def _spec_scalar(ctx: SkillContext, key: str) -> object:
    """The value strictyaml produces: a plain scalar is always its literal text.

    skills-ref performs no implicit typing (spec-fm-scalars-are-strings), so
    ``description: true`` is the string ``'true'`` and ``compatibility:`` is
    ``''`` - typing them the way PyYAML does would invent hard errors that the
    reference validator does not raise.
    """

    value = ctx.value(key)
    if isinstance(value, (str, list, dict)):
        return value
    entry = ctx.top(key)
    if entry is None:
        return value
    if entry.style == "plain":
        text = entry.plain_value.strip()
        return "" if text.startswith("#") else text  # a value that is only a comment is empty
    if entry.style == "empty" and value is None:
        return ""
    return value


def _check_spec_name(e: Emitter, name: object) -> None:
    ctx = e.ctx
    line = e.line("name")
    if not isinstance(name, str) or not name.strip():
        e.add("spec-name-nonempty-string", "error", f"name must be a non-empty string, got {_type_name(name)} {_short(name)}",
              "write `name: <directory-name>`", line=line)
        return
    norm = unicodedata.normalize("NFKC", name.strip())
    if norm != name.strip():
        e.add("spec-name-nfkc-normalization", "warning", f"name {_short(name)} is not NFKC-normalised; skills-ref compares {_short(norm)}",
              "write the name with normalised characters", line=line)
    if len(norm) > 64:
        e.add("spec-name-length-1-64", "error", f"name has {len(norm)} code points (max 64)", "shorten the name (and the directory)", line=line)
    if norm != norm.lower():
        e.add("spec-name-lowercase", "error", f"name {_short(name)} must be lowercase", "use lowercase letters, digits and hyphens", line=line)
    if not all(c.isalnum() or c == "-" for c in norm):
        bad = sorted({c for c in norm if not (c.isalnum() or c == "-")})
        e.add("spec-name-charset-unicode-alnum-hyphen", "error", f"name contains invalid characters {bad}",
              "use only letters, digits and hyphens", line=line)
    elif not SPEC_NAME_PORTABLE_RE.match(norm):
        e.add("spec-name-charset-unicode-alnum-hyphen", "warning", f"name {_short(name)} is accepted by skills-ref but is not ^[a-z0-9]+(-[a-z0-9]+)*$ (Codex's quick_validate enforces ASCII)",
              "prefer ASCII lowercase letters, digits and single hyphens", line=line)
    if norm.startswith("-") or norm.endswith("-"):
        e.add("spec-name-no-edge-hyphens", "error", "name starts or ends with a hyphen", "remove the leading/trailing hyphen", line=line)
    if "--" in norm:
        e.add("spec-name-no-consecutive-hyphens", "error", "name contains consecutive hyphens", "collapse '--' to '-'", line=line)
    dir_name = unicodedata.normalize("NFKC", ctx.entry.dir.name)
    if norm != dir_name:
        e.add("spec-name-must-match-directory", "error", f"name {_short(name)} does not match directory name {_short(ctx.entry.dir.name)}",
              "rename the directory or the name so they are identical (skills-ref: \"Directory name '...' must match skill name\")", line=line)


def _check_spec_description(e: Emitter, desc: object) -> None:
    ctx = e.ctx
    line = e.line("description")
    entry = ctx.top("description")
    if not isinstance(desc, str) or not desc.strip():
        e.add("spec-desc-nonempty-string", "error", f"description must be a non-empty string, got {_type_name(desc)} {_short(desc)}",
              "write a one-paragraph description of what the skill does and when to use it", line=line)
        return
    length = len(desc)
    if length > 1024:
        if entry is not None and entry.style == "block" and len(desc.rstrip("\n")) <= 1024:
            e.add("spec-desc-block-scalar-trailing-newline", "error",
                  f"description is {length} code points because the block scalar keeps its trailing newline (limit 1024)",
                  "use the strip-chomping form `description: >-`", line=line)
        else:
            e.add("spec-desc-max-1024", "error", f"description has {length} code points (max 1024; skills-ref: 'Description exceeds 1024 character limit')",
                  "shorten the description; move detail into the body", line=line)
    elif entry is not None and entry.style == "block" and "-" not in entry.raw[:3]:
        e.add("spec-fm-block-scalars-and-multiline", "info",
              f"block-scalar description keeps a trailing newline ({length} code points counted, {len(desc.rstrip())} visible)",
              "use `>-` to drop the final newline", line=line)
    if len(desc.strip()) < 40 or not _has_when_cue(desc):
        e.add("spec-desc-content-guidance", "warning", "description should say what the skill does and when to use it (no 'use'/'when' cue or under 40 characters)",
              "add a 'Use when ...' sentence with the task keywords agents should match", line=line)


def profile_spec(ctx: SkillContext) -> list[Finding]:
    e = Emitter(ctx, "spec")
    if ctx.dangling_symlink:
        e.add("spec-discovery-symlink-dir-name", "error", "SKILL.md is a dangling symlink (skills-ref: 'Missing required file: SKILL.md')", "fix or replace the symlink")
        return e.findings
    if ctx.read_error:
        e.add("spec-discovery-skill-md-required", "error", f"SKILL.md cannot be read: {ctx.read_error}", "make SKILL.md a readable regular file")
        return e.findings
    if ctx.entry.filename != "SKILL.md":
        e.add("spec-discovery-exact-filename-for-clients", "warning", f"skill file is named {ctx.entry.filename}; the client guide asks for exactly SKILL.md",
              "rename the file to SKILL.md")
    if ctx.decode_error:
        e.add("spec-fm-utf8-required", "error", f"SKILL.md is not valid UTF-8 ({ctx.decode_error}); skills-ref raises UnicodeDecodeError", "re-save the file as UTF-8")
        return e.findings
    if ctx.has_bom:
        e.add("spec-fm-must-start-with-dashes", "error", "file starts with a UTF-8 BOM, so the first bytes are not '---' (skills-ref: 'SKILL.md must start with YAML frontmatter')",
              "save without a byte-order mark", line=1)
    if ctx.opener is None:
        e.add("spec-fm-must-start-with-dashes", "error", "file does not start with '---'", "put `---` on line 1 followed by the frontmatter", line=1)
        return e.findings
    if not ctx.fm_present and ctx.spec_view is None:
        e.add("spec-fm-closing-delimiter", "error", "no closing '---' anywhere after the opening delimiter (skills-ref: 'not properly closed')", "add a line containing only `---` after the last key", line=1)
        return e.findings
    if ctx.opener.rstrip() != "---":
        e.add("spec-fm-delimiter-leniency-vs-clients", "warning", f"opening delimiter is {_short(ctx.opener)!s}; only a bare `---` line is read identically by every parser",
              "make line 1 exactly `---`", line=1)
    if not ctx.fm_present:
        # skills-ref splits on the '---' substring, so this block still closes;
        # every other harness scans lines and never finds the delimiter.
        cut = ctx.spec_cut_line or 1
        e.add("spec-fm-delimiter-leniency-vs-clients", "warning",
              f"the frontmatter is closed only by the '---' inside line {cut}; skills-ref accepts it, Claude Code, Codex, Antigravity and Cursor need a `---` line of its own",
              "put `---` alone on its own line at column 0", line=cut)
        if ctx.spec_cut_midline:
            e.add("spec-fm-triple-dash-truncates", "error", f"'---' occurs inside line {cut}; skills-ref ends the frontmatter there and silently drops the rest of the value",
                  "remove the '---' from the value or rewrite it", line=cut)
    elif ctx.fm_close_line_raw.rstrip() != "---":
        e.add("spec-fm-delimiter-leniency-vs-clients", "warning", f"closing delimiter line is {_short(ctx.fm_close_line_raw)!s}",
              "make the closing line exactly `---`", line=(ctx.fm_close_index or 0) + 1)
    if ctx.fm_inner_dash_lines:
        e.add("spec-fm-triple-dash-truncates", "error", f"'---' occurs inside the frontmatter (line {ctx.fm_inner_dash_lines[0]}); skills-ref ends the frontmatter there and silently drops what follows",
              "remove the '---' from the value or rewrite it", line=ctx.fm_inner_dash_lines[0])
    if ctx.spec_view is not None:
        # From here on read the block skills-ref actually parses.
        e.findings.extend(_spec_frontmatter_checks(Emitter(ctx.spec_view, "spec")))
        return e.findings
    return _spec_frontmatter_checks(e)


def _spec_frontmatter_checks(e: Emitter) -> list[Finding]:
    ctx = e.ctx
    for line in _control_char_lines(ctx):
        e.add("spec-fm-control-characters-crash", "error", "control character inside the frontmatter (skills-ref crashes with AttributeError)", "delete the control character", line=line)
    for line, name in _separator_lines(ctx):
        e.add("spec-fm-unicode-line-separators", "warning", f"{name} inside the frontmatter", "replace it with a plain space or newline", line=line)
    for line, kind in _tab_positions(ctx):
        if kind in ("indent", "value"):
            e.add("spec-fm-tabs-structural", "error", f"tab used as {'indentation' if kind == 'indent' else 'part of an unquoted value'} (strictyaml: \"found character '\\t' that cannot start any token\")",
                  "replace tabs with spaces", line=line)
        else:
            e.add("spec-fm-tabs-structural", "warning", f"tab inside a {kind}; accepted by skills-ref but fragile", "replace the tab with spaces", line=line)
    parse_failed = ctx.parse_error is not None
    if parse_failed:
        rid = _map_spec_parse_error(ctx.parse_error or "")
        e.add(rid, "error", f"frontmatter does not parse as YAML: {ctx.parse_error}", "fix the YAML (quote hazardous values, use spaces, one key per line)", line=ctx.parse_error_line)
    elif not isinstance(ctx.parsed, dict) or not ctx.parsed:
        e.add("spec-fm-must-be-mapping", "error", f"frontmatter is {'empty' if ctx.parsed is None else 'a ' + _type_name(ctx.parsed)}, not a mapping (skills-ref: 'must be a YAML mapping')",
              "write `key: value` lines between the delimiters", line=2)
    for line in ctx.flow_lines:
        e.add("spec-fm-no-flow-style", "error", "flow-style collection ([...] or {...}) in the frontmatter (strictyaml: FlowMappingDisallowed)", "use block style: one `- item` or `key: value` per line", line=line)
    if ctx.anchors or ctx.aliases:
        e.add("spec-fm-no-anchors-aliases", "error", "anchor or alias in the frontmatter (strictyaml: AnchorTokenDisallowed)", "remove &anchors/*aliases; repeat the value instead", line=(ctx.aliases or [ctx.key_lines.get(next(iter(ctx.key_lines), ""), 2)])[0] if (ctx.aliases or ctx.key_lines) else 2)
    for tag, line in ctx.tags:
        e.add("spec-fm-no-tags", "error", f"explicit tag {tag} in the frontmatter (strictyaml: TagTokenDisallowed)", "remove the tag", line=line)
    for key, line, first in ctx.dup_keys:
        e.add("spec-fm-no-duplicate-keys", "error", f"duplicate key {key!r} (first defined on line {first}; strictyaml: DuplicateKeysDisallowed)", "keep one occurrence", line=line)
    for line in ctx.merge_keys:
        e.add("spec-fm-merge-keys", "warning", "'<<' merge key is honoured by skills-ref's ruamel core but not portable", "write the merged keys explicitly", line=line)
    for entry in ctx.entries:
        h = _hazards(entry)
        key = entry.top_key or "?"
        if entry.style in ("single", "double"):
            if h.unterminated_quote:
                e.add("spec-fm-quoted-scalars", "error", f"unterminated quoted value for {key}", "close the quote", line=entry.line)
            elif h.quote_then_text:
                e.add("spec-fm-quoted-scalars", "error", f"text after the closing quote in {key} (an unescaped inner quote?)", 'escape inner quotes (\\" or \'\') or use a block scalar', line=entry.line)
            continue
        if entry.style != "plain":
            if entry.style == "flow" and not ctx.flow_lines:
                e.add("spec-fm-no-flow-style", "error", f"value of {key} starts with '{entry.raw[0]}' (flow style is disallowed)", "use block style or quote the value", line=entry.line)
            continue
        if h.lead in ("[", "{", "]", "}", ","):
            if not ctx.flow_lines or h.lead in ("]", "}", ","):
                e.add("spec-fm-no-flow-style", "error", f"unquoted value of {key} starts with '{h.lead}'", "quote the value", line=entry.line)
        elif h.lead in ("*", "&"):
            if not (ctx.anchors or ctx.aliases):
                e.add("spec-fm-no-anchors-aliases", "error", f"unquoted value of {key} starts with '{h.lead}' (read as an {'alias' if h.lead == '*' else 'anchor'})", "quote the value", line=entry.line)
        elif h.lead == "!":
            if not ctx.tags:
                e.add("spec-fm-no-tags", "error", f"unquoted value of {key} starts with '!' (read as a tag)", "quote the value", line=entry.line)
        elif h.lead is not None:
            e.add("spec-fm-plain-scalar-reserved-starts", "error", f"unquoted value of {key} starts with '{h.lead}' ({h.lead_kind}); strictyaml rejects or empties it",
                  "quote the value or use a block scalar", line=entry.line)
        if h.colon_space or h.trailing_colon:
            what = "contains ': '" if h.colon_space else "ends with ':'"
            rid = "spec-desc-unquoted-colon-space" if key == "description" else "spec-fm-plain-scalar-reserved-starts"
            e.add(rid, "error", f"unquoted value of {key} {what} (strictyaml: 'mapping values are not allowed here')",
                  "quote the value or write it as `>-` block scalar", line=entry.line)
        if h.space_hash:
            e.add("spec-fm-plain-scalar-reserved-starts", "warning", f"unquoted value of {key} contains ' #', everything after it is a comment",
                  "quote the value", line=entry.line)
        kind = _yaml11_kind(entry.plain_value) if entry.plain_value and key in SPEC_KEYS else None
        if kind in ("boolean", "number", "null", "timestamp"):
            e.add("spec-fm-scalars-are-strings", "warning", f"value {_short(entry.plain_value)} of {'.'.join(str(p) for p in entry.path)} is a string for skills-ref but a {kind} for YAML 1.2 clients",
                  "quote the value so every parser reads a string", line=entry.line)
    if parse_failed or not isinstance(ctx.data, dict) or not ctx.data:
        _spec_body_checks(e)
        return e.findings
    data = ctx.data
    keys = _top_keys(ctx)
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and ("\n" in item or re.search(r"\s-\s", item)):
                    e.add("spec-fm-sequence-indent-absorbed", "error", f"list item {_short(item)} under {key} absorbed a mis-indented sibling",
                          "indent every `- item` line identically", line=e.line(str(key)))
                    break
    unexpected = [k for k in keys if k not in SPEC_KEYS]
    near = {k: _near_miss(k, SPEC_KEYS) for k in unexpected}
    for key in unexpected:
        if near[key]:
            e.add("spec-fm-keys-case-and-hyphen-exact", "error", f"unexpected key {key!r}; did you mean {near[key]!r}? (keys are case- and hyphen-exact)",
                  f"rename the key to {near[key]}", line=e.line(key))
    plain_unexpected = [k for k in unexpected if not near[k]]
    if plain_unexpected:
        e.add("spec-keys-allowed-set", "error", f"unexpected keys {', '.join(plain_unexpected)} (skills-ref: 'Unexpected fields in frontmatter'; only {', '.join(sorted(SPEC_KEYS))} are allowed)",
              "remove the keys or move them under `metadata:`", line=e.line(plain_unexpected[0]))
        e.add("spec-keys-extensions-belong-in-metadata", "info", f"{', '.join(plain_unexpected)} would be spec-legal under `metadata:`, but Claude Code, Antigravity and Cursor honour only the top-level spelling",
              "keep the top-level key if the harness needs it and accept the spec error, or drop it", line=e.line(plain_unexpected[0]))
    for req in ("name", "description"):
        if req not in data:
            e.add("spec-keys-required-name-description", "error", f"missing required key {req} (skills-ref: 'Missing required field in frontmatter: {req}')",
                  f"add `{req}: ...`", line=2)
    compat_reported = False
    if "compatibility" in data:
        compat = _spec_scalar(ctx, "compatibility")
        if not isinstance(compat, str):
            e.add("spec-compat-string-max-500", "error", f"compatibility must be a string, got {_type_name(compat)} (skills-ref: \"Field 'compatibility' must be a string\")", "write a one-line string", line=e.line("compatibility"))
            compat_reported = True
        elif len(compat) == 0:
            e.add("spec-compat-string-max-500", "warning", "compatibility is empty (skills-ref accepts it; the spec says 1-500 characters if provided)", "fill it in or remove the key", line=e.line("compatibility"))
            compat_reported = True
        elif len(compat) > 500:
            e.add("spec-compat-string-max-500", "error", f"compatibility has {len(compat)} code points (max 500)", "shorten it", line=e.line("compatibility"))
            compat_reported = True
    for opt in ("license", "allowed-tools", "metadata", "compatibility"):
        if opt == "compatibility" and compat_reported:
            continue  # already reported, more precisely, by spec-compat-string-max-500
        if opt in data and (data[opt] is None or (isinstance(data[opt], (str, list, dict)) and not data[opt])):
            e.add("spec-keys-empty-optional-values", "warning", f"{opt} is present but empty", f"give {opt} a value or remove it", line=e.line(opt))
    if "name" in data:
        _check_spec_name(e, _spec_scalar(ctx, "name"))
    if "description" in data:
        _check_spec_description(e, _spec_scalar(ctx, "description"))
    if "license" in data and (not isinstance(data["license"], str) or not data["license"].strip()):
        e.add("spec-license-freeform", "warning", f"license should be a short non-empty string, got {_type_name(data['license'])}", "e.g. `license: MIT` or the name of a bundled LICENSE file", line=e.line("license"))
    if "metadata" in data and data["metadata"] is not None:
        meta = data["metadata"]
        if not isinstance(meta, dict):
            e.add("spec-metadata-string-map-coercion", "error", f"metadata must be a mapping, got {_type_name(meta)}", "write `metadata:` followed by indented `key: value` lines", line=e.line("metadata"))
        else:
            for k, v in meta.items():
                if isinstance(v, (list, dict)):
                    e.add("spec-metadata-string-map-coercion", "error", f"metadata.{k} is a {_type_name(v)}; the spec allows only string values (skills-ref coerces it to a Python repr)",
                          "flatten it to a string", line=e.line("metadata"))
    if "allowed-tools" in data:
        tools = data["allowed-tools"]
        if not isinstance(tools, str):
            e.add("spec-allowed-tools-space-separated-string", "warning", f"allowed-tools is a {_type_name(tools)}; the spec defines a space-separated string", "write `allowed-tools: Bash(git:*) Read`", line=e.line("allowed-tools"))
        elif "," in tools:
            e.add("spec-allowed-tools-space-separated-string", "warning", "allowed-tools uses commas (Claude Code dialect); the spec form is space-separated", "separate entries with spaces", line=e.line("allowed-tools"))
    _spec_body_checks(e)
    return e.findings


def _spec_body_checks(e: Emitter) -> None:
    ctx = e.ctx
    if not ctx.body.strip():
        e.add("spec-body-unrestricted-may-be-empty", "warning", "the body after the frontmatter is empty", "add the instructions", line=ctx.body_start_line)
    if ctx.line_count > 500:
        e.add("spec-body-under-500-lines", "warning", f"SKILL.md has {ctx.line_count} lines (recommended maximum 500)", "move reference material into references/ files", line=501)
    tokens = len(ctx.body) // 4
    if tokens > 5000:
        e.add("spec-body-under-5000-tokens", "warning", f"body is roughly {tokens} tokens (recommended under 5000)", "split detail into referenced files", line=ctx.body_start_line)
    for ref in _missing_refs(ctx):
        e.add("spec-files-relative-paths-from-root", "warning", f"referenced file {ref.text} does not exist in the skill directory", "fix the path or add the file", line=ref.line)
    for ref in ctx.file_refs:
        if (ref.absolute or ref.parent_escape) and ref.kind == "link":
            e.add("spec-files-relative-paths-from-root", "warning", f"file reference {ref.text} is {'absolute' if ref.absolute else 'outside the skill (..)'}; use paths relative to the skill root",
                  "reference bundled files as scripts/x.py, references/x.md", line=ref.line)
        elif ref.exists and ref.depth > 1:
            e.add("spec-files-one-level-deep", "info", f"file reference {ref.text} is {ref.depth} levels deep (spec recommends one level from SKILL.md)", "consider flattening the layout", line=ref.line)
    tokens_present = []
    if "arguments" in ctx.constructs:
        tokens_present.append("$ARGUMENTS/$N")
    if ctx.substitutions:
        tokens_present.append("${CLAUDE_*}")
    if "inline_shell" in ctx.constructs or "shell_fence" in ctx.constructs:
        tokens_present.append("!`command`")
    if tokens_present:
        line = min(l for k, ls in ctx.constructs.items() for l in ls if k in ("arguments", "inline_shell", "shell_fence")) if any(k in ctx.constructs for k in ("arguments", "inline_shell", "shell_fence")) else min(l for ls in ctx.substitutions.values() for l in ls)
        e.add("spec-sem-body-tokens-not-interpreted", "info", f"body uses {', '.join(tokens_present)}, which the spec does not interpret (Claude Code substitutions)",
              "fine for Claude Code; other harnesses inject the text verbatim", line=line)


# --------------------------------------------------------------------------- #
# Profile: claude-code (Claude Code CLI 2.1.259)
# --------------------------------------------------------------------------- #

_rule("claude-code-discovery-entry-layout", "claude-code", "error", "the skill file is a regular file named exactly SKILL.md (skill.md loads only on case-insensitive filesystems)")
_rule("claude-code-discovery-dot-dirs", "claude-code", "warning", "the skill directory name does not start with '.' (Claude Code loads it, this repo's tools skip it)")
_rule("claude-code-discovery-reserved-synced", "claude-code", "error", "the directory name does not fold to the reserved name 'synced'")
_rule("claude-code-discovery-size-limit", "claude-code", "error", "SKILL.md is at most 1,000,000 bytes")
_rule("claude-code-discovery-symlinks", "claude-code", "error/warning", "a symlinked SKILL.md resolves (error); two catalog entries resolving to the same file load once (warning)")
_rule("claude-code-fm-opening-delimiter", "claude-code", "error", "line 1 is '---' followed by a newline (otherwise the whole file is body with empty frontmatter)")
_rule("claude-code-fm-closing-delimiter-first-occurrence", "claude-code", "error", "no '---' inside a frontmatter value or comment (the block ends at the first '---' anywhere)")
_rule("claude-code-fm-missing-closing-delimiter", "claude-code", "error", "a closing '---' line exists")
_rule("claude-code-fm-yaml-parser-and-repair", "claude-code", "error/warning", "the frontmatter parses; if only the repair pass (re-quoting hazardous values, expanding tabs) makes it parse that is a warning; if the repair fails too the skill loads with EMPTY frontmatter (error)")
_rule("claude-code-fm-mapping-required", "claude-code", "error", "the frontmatter parses to a mapping (anything else is replaced by {} and every field is lost)")
_rule("claude-code-fm-anchor-stripped", "claude-code", "error/warning", "no unquoted value starts with & or ! (silently stripped); '<<' merge keys are noted")
_rule("claude-code-fm-duplicate-keys-last-wins", "claude-code", "error", "no duplicate keys (the last silently wins)")
_rule("claude-code-fm-keys-exact-case", "claude-code", "warning", "no near-miss key spellings (Description, disable_model_invocation, allowedTools are ignored)")
_rule("claude-code-fm-unknown-keys-ignored", "claude-code", "info", "keys outside the documented table have no effect in Claude Code")
_rule("claude-code-fm-inline-comment-truncation", "claude-code", "error", "no unquoted honoured value contains ' #' or starts with '#' (silently truncated / null)")
_rule("claude-code-fm-crlf-bom-tabs", "claude-code", "warning", "no tab indentation (it loads only through the repair pass)")
_rule("claude-code-name-from-directory", "claude-code", "error/warning", "frontmatter name equals the directory name (warning); it does not equal another catalog skill's directory or frontmatter name (error)")
_rule("claude-code-name-case-sensitive-lookup", "claude-code", "warning", "the directory name has no uppercase letters (lookup is case-sensitive)")
_rule("claude-code-name-no-format-validation", "claude-code", "error/warning", "the directory name has no surrounding whitespace, leading '/', parentheses, commas or control characters (error); ^[a-z0-9]+(-[a-z0-9]+)*$ is recommended (warning)")
_rule("claude-code-name-type", "claude-code", "warning", "name, when present, is a string")
_rule("claude-code-name-precedence", "claude-code", "warning", "the directory name does not shadow a bundled skill (doctor, code-review, verify, run, loop, batch, debug, claude-api, simplify, security-review, init)")
_rule("claude-code-description-optional-fallback", "claude-code", "warning", "description is present (otherwise the first body line is used)")
_rule("claude-code-description-empty-value", "claude-code", "warning", "description is not empty, null or '#'-leading (treated as missing at runtime)")
_rule("claude-code-description-type", "claude-code", "error/warning", "description is a string (list/map is dropped: error; number/boolean is stringified: warning)")
_rule("claude-code-description-listing-cap", "claude-code", "warning", "description (+ ' - ' + when_to_use) is at most 1536 characters in the model listing")
_rule("claude-code-description-listing-budget", "claude-code", "warning", "the catalog's listing entries fit the 8,000-character budget of a 200k context (1%)")
_rule("claude-code-key-disable-model-invocation", "claude-code", "error", "disable-model-invocation is true/false/yes/no/on/off/1/0 in any case (anything else silently counts as false)")
_rule("claude-code-key-user-invocable", "claude-code", "error", "user-invocable, when present, is a recognised boolean (anything else hides the skill from users)")
_rule("claude-code-key-allowed-tools", "claude-code", "error/warning/info", "allowed-tools is a string or list of strings (error); a bare '*' or odd token is a warning; unknown tool names are noted")
_rule("claude-code-key-disallowed-tools", "claude-code", "error/warning/info", "disallowed-tools follows the same rules as allowed-tools")
_rule("claude-code-key-shell", "claude-code", "warning", "shell is bash or powershell")
_rule("claude-code-key-effort", "claude-code", "warning", "effort is low/med/medium/high/xhigh/max or an integer")
_rule("claude-code-key-context-agent-background", "claude-code", "warning", "context is exactly 'fork' when present; agent/background are used only with context: fork")
_rule("claude-code-key-model", "claude-code", "warning", "model is a non-empty string")
_rule("claude-code-key-paths", "claude-code", "error/warning/info", "paths is a string or list of strings (error); '**' mixed with other globs and >1000 brace expansions are warnings; the skill is withheld until a matching file is touched (info)")
_rule("claude-code-key-hooks", "claude-code", "error", "no top-level PreToolUse/PermissionRequest keys; hooks is a mapping of event -> list of {matcher?, hooks: [{type, ...}]}")
_rule("claude-code-key-metadata-license-compatibility", "claude-code", "warning", "metadata is a mapping (else dropped) and reuses no frontmatter field names as keys")
_rule("claude-code-key-scalar-coercions", "claude-code", "warning", "argument-hint, when_to_use, version and agent are scalars; arguments is a string or list of non-numeric identifiers")
_rule("claude-code-body-substitutions", "claude-code", "warning/info", "${CLAUDE_*} names are supported (SKILL_DIR, PROJECT_DIR, SESSION_ID, EFFORT); plugin-only variables and unused declared arguments are noted")
_rule("claude-code-body-inline-shell", "claude-code", "warning", "!`command` / ```! blocks run at invocation; a failing command aborts the invocation")
_rule("claude-code-body-500-lines", "claude-code", "warning", "SKILL.md has at most 500 lines")
_rule("claude-code-body-compaction-budget", "claude-code", "warning", "the body is under ~20,000 characters (5,000 tokens re-attached after compaction)")
_rule("claude-code-files-supporting", "claude-code", "warning", "no .claude-plugin/plugin.json inside the skill (dual identity); relative file references resolve")

_CLAUDE_HONORED_SCALARS = ("description", "name", "model", "argument-hint", "when_to_use", "version", "agent", "shell", "effort", "context", "allowed-tools", "disallowed-tools", "paths")


def _check_claude_tools(e: Emitter, key: str, rule_id: str) -> None:
    ctx = e.ctx
    value = ctx.value(key)
    line = e.line(key)
    if isinstance(value, list):
        if any(not isinstance(v, str) for v in value):
            e.add(rule_id, "error", f"{key} list contains non-string items (dropped at runtime; `claude plugin validate`: 'array must contain only strings')", "quote every entry", line=line)
    elif not isinstance(value, str):
        e.add(rule_id, "error", f"{key} must be a string or list of strings, got {_type_name(value)} (the grant becomes empty)", "write `allowed-tools: Bash(git:*) Read`", line=line)
        return
    tokens = _split_tools(value)
    if "*" in tokens:
        e.add(rule_id, "warning", f"{key} contains a bare '*', which collapses the grant to every tool", "list the tools explicitly", line=line)
    unknown = []
    for token in tokens:
        if token == "*":
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(\(.*\))?$", token)
        if not m:
            e.add(rule_id, "warning", f"{key} token {_short(token)} is not of the form Tool or Tool(pattern)", "check the permission-rule syntax", line=line)
        elif m.group(1) not in CLAUDE_TOOL_NAMES and not m.group(1).startswith("mcp__"):
            unknown.append(m.group(1))
    if unknown:
        e.add(rule_id, "info", f"{key} names tools unknown to this validator: {', '.join(sorted(set(unknown)))}", "verify the tool names against the current Claude Code release", line=line)


def _check_claude_hooks(e: Emitter) -> None:
    ctx = e.ctx
    hooks = ctx.value("hooks")
    line = e.line("hooks")
    ok = isinstance(hooks, dict)
    if ok:
        for event, handlers in hooks.items():
            if not isinstance(handlers, list):
                ok = False
                break
            for handler in handlers:
                if not isinstance(handler, dict) or not isinstance(handler.get("hooks"), list):
                    ok = False
                    break
                for hook in handler["hooks"]:
                    if not isinstance(hook, dict) or not isinstance(hook.get("type"), str):
                        ok = False
                        break
    if not ok:
        e.add("claude-code-key-hooks", "error", "hooks is not a mapping of event -> list of {matcher?, hooks: [{type, command|prompt}]}; the skill loads with no hooks and an EMPTY allowed-tools grant",
              "follow the hooks schema (see the Claude Code hooks reference)", line=line)


def profile_claude_code(ctx: SkillContext) -> list[Finding]:
    e = Emitter(ctx, "claude-code")
    dir_name = ctx.entry.dir.name
    if ctx.dangling_symlink:
        e.add("claude-code-discovery-symlinks", "error", "SKILL.md is a dangling symlink; the skill is skipped silently", "fix the symlink")
        return e.findings
    if not ctx.is_regular_file:
        e.add("claude-code-discovery-entry-layout", "error", f"SKILL.md is {ctx.read_error} ('[skills] skipping ...: not a regular file')", "make SKILL.md a regular file")
        return e.findings
    if ctx.entry.filename != "SKILL.md":
        e.add("claude-code-discovery-entry-layout", "error", f"skill file is named {ctx.entry.filename}; Claude Code stats exactly SKILL.md, so it is skipped on Linux", "rename it to SKILL.md")
    if dir_name.startswith("."):
        e.add("claude-code-discovery-dot-dirs", "warning", f"directory name {dir_name!r} starts with '.'; Claude Code loads it (named with the dot) but this repo's catalog walk skips it", "use a visible directory name")
    folded = unicodedata.normalize("NFKC", dir_name).casefold().replace("-", "")
    if folded == "synced":
        e.add("claude-code-discovery-reserved-synced", "error", f"directory name {dir_name!r} folds to the reserved name 'synced' and is skipped", "rename the directory")
    if ctx.read_error:
        e.add("claude-code-discovery-entry-layout", "error", f"SKILL.md cannot be read: {ctx.read_error}", "make SKILL.md readable")
        return e.findings
    if ctx.size > CLAUDE_SIZE_LIMIT:
        e.add("claude-code-discovery-size-limit", "error", f"SKILL.md is {ctx.size} bytes; files over {CLAUDE_SIZE_LIMIT} bytes are skipped", "move content out of SKILL.md")
    if re.search(r"^\s|\s$", dir_name) or dir_name.startswith("/") or re.search(r"[(),\x00-\x1f\x7f-\x9f]", dir_name):
        e.add("claude-code-name-no-format-validation", "error", f"directory name {dir_name!r} cannot be invoked (surrounding whitespace, leading '/', parentheses, commas or control characters)", "rename the directory")
    elif not SPEC_NAME_PORTABLE_RE.match(dir_name):
        e.add("claude-code-name-no-format-validation", "warning", f"directory name {dir_name!r} loads but is not ^[a-z0-9]+(-[a-z0-9]+)*$", "use lowercase letters, digits and hyphens")
    if dir_name != dir_name.lower():
        e.add("claude-code-name-case-sensitive-lookup", "warning", f"directory name {dir_name!r} has uppercase letters; /{dir_name} and Skill({dir_name}) are case-sensitive", "use a lowercase directory name")
    if dir_name in CLAUDE_BUNDLED_SKILLS:
        e.add("claude-code-name-precedence", "warning", f"{dir_name!r} is also a bundled Claude Code skill name; the project skill overrides it (but not its aliases)", "pick a more specific name")
    # Only Claude Code's own manifest gives the directory a second identity;
    # .codex-plugin / .cursor-plugin are never read by Claude Code.
    if ctx.plugin_manifest_rel == ".claude-plugin/plugin.json":
        e.add("claude-code-files-supporting", "warning", "the skill directory contains .claude-plugin/plugin.json, so it loads both as a plain skill and as a <name>@skills-dir plugin", "remove the manifest unless the dual identity is intended")
    if ctx.decode_error:
        e.add("claude-code-fm-opening-delimiter", "error", f"SKILL.md is not valid UTF-8 ({ctx.decode_error}); the frontmatter regex will not match cleanly", "re-save as UTF-8", line=1)
    # Frontmatter block.  The regex is applied to the file as written (only the
    # BOM is stripped), so a file with no LF after the opener - CR-only line
    # endings, for instance - has no frontmatter block at all; `claude plugin
    # validate` 2.1.260 reports "No frontmatter block found." for exactly these.
    if not re.match(r"^---[ \t\r]*\n", ctx.text_raw):
        e.add("claude-code-fm-opening-delimiter", "error", "line 1 is not '---' followed by a newline; the whole file becomes body with EMPTY frontmatter (first line used as description)",
              "start the file with `---` on its own line", line=1)
        _claude_body_checks(e)
        return e.findings
    if not ctx.fm_present:
        e.add("claude-code-fm-missing-closing-delimiter", "error", "no closing '---' line; the block extends to the next '---' anywhere (or the whole file becomes body)", "close the frontmatter with a `---` line", line=1)
        _claude_body_checks(e)
        return e.findings
    if ctx.has_cr_only:
        e.add("claude-code-fm-crlf-bom-tabs", "warning", "a stray CR that is not part of a CRLF pair inside the frontmatter is read as a line break, so the value silently continues on the next line",
              "convert the file to LF (or CRLF) line endings", line=1)
    if ctx.fm_inner_dash_lines:
        e.add("claude-code-fm-closing-delimiter-first-occurrence", "error", f"'---' inside the frontmatter (line {ctx.fm_inner_dash_lines[0]}); Claude Code ends the block at the first '---' anywhere, silently truncating the value and turning later keys into body text",
              "remove '---' from the value", line=ctx.fm_inner_dash_lines[0])
    tab_indent = [l for l, k in _tab_positions(ctx) if k == "indent"]
    repaired = False
    if ctx.parse_error is not None:
        if ctx.claude_repair_ok:
            repaired = True
            e.add("claude-code-fm-yaml-parser-and-repair", "warning", f"frontmatter parses only after Claude Code's repair pass ({ctx.parse_error}); other harnesses do not repair it",
                  "quote the hazardous value / replace tabs so the YAML is valid as written", line=ctx.parse_error_line)
        else:
            e.add("claude-code-fm-yaml-parser-and-repair", "error", f"frontmatter fails to parse even after the repair pass ({ctx.parse_error}); the skill loads with EMPTY frontmatter (no description, no keys)",
                  "fix the YAML", line=ctx.parse_error_line)
            _claude_body_checks(e)
            return e.findings
    elif tab_indent:
        e.add("claude-code-fm-crlf-bom-tabs", "warning", f"tab indentation on line {tab_indent[0]} loads only through the repair pass", "indent with spaces", line=tab_indent[0])
    data = ctx.claude_repair_parsed if repaired else ctx.parsed
    if not isinstance(data, dict) or not data:
        if isinstance(data, dict):
            text = "frontmatter block is an empty mapping; no description and no keys reach Claude Code"
        else:
            text = f"frontmatter is {'empty' if data is None else 'a ' + _type_name(data)}, not a mapping; it is replaced by {{}} and every field is lost"
        e.add("claude-code-fm-mapping-required", "error", text, "write `key: value` lines", line=2)
        _claude_body_checks(e)
        return e.findings
    for key, line, first in ctx.dup_keys:
        e.add("claude-code-fm-duplicate-keys-last-wins", "error", f"duplicate key {key!r}: the last value silently wins (first on line {first})", "keep one occurrence", line=line)
    for line in ctx.merge_keys:
        e.add("claude-code-fm-anchor-stripped", "warning", "'<<' merge key; Bun.YAML handling of merge keys is unverified", "write the keys explicitly", line=line)
    for entry in ctx.entries:
        if entry.style != "plain" or not entry.top_key:
            continue
        key = entry.top_key
        h = _hazards(entry)
        if key in CLAUDE_KEYS:
            if h.lead == "&" or h.lead == "!":
                e.add("claude-code-fm-anchor-stripped", "error", f"unquoted value of {key} starts with '{h.lead}'; the token is silently removed ({_short(entry.raw)} -> {_short(entry.raw.split(None, 1)[1] if ' ' in entry.raw else '')})",
                      "quote the value", line=entry.line)
            if entry.raw.startswith("#"):
                e.add("claude-code-fm-inline-comment-truncation", "error", f"value of {key} starts with '#', so it parses as null (treated as missing)", "quote the value", line=entry.line)
            elif h.space_hash:
                e.add("claude-code-fm-inline-comment-truncation", "error", f"unquoted value of {key} contains ' #'; it silently loads as {_short(entry.plain_value)!r}", "quote the value", line=entry.line)
    keys = [str(k) for k in data.keys()]
    for key in keys:
        if key in CLAUDE_KEYS:
            continue
        cand = _near_miss(key, CLAUDE_KEYS)
        if cand and key != "disallowedTools":
            e.add("claude-code-fm-keys-exact-case", "warning", f"key {key!r} is ignored; Claude Code reads only the exact spelling {cand!r}", f"rename it to {cand}", line=e.line(key))
    unknown = [k for k in keys if k not in CLAUDE_KEYS and not _near_miss(k, CLAUDE_KEYS)]
    if unknown:
        e.add("claude-code-fm-unknown-keys-ignored", "info", f"keys ignored by Claude Code: {', '.join(unknown)}", "no action needed unless a behaviour was expected", line=e.line(unknown[0]))
    if "PreToolUse" in data or "PermissionRequest" in data:
        e.add("claude-code-key-hooks", "error", "PreToolUse/PermissionRequest at the frontmatter top level (outside hooks); the skill loads with no hooks and an EMPTY allowed-tools grant",
              "nest them under `hooks:`", line=e.line("PreToolUse") or e.line("PermissionRequest"))
    if "hooks" in data:
        _check_claude_hooks(e)
    # name
    name = data.get("name")
    if "name" in data and name is not None and not isinstance(name, str):
        e.add("claude-code-name-type", "warning", f"name is a {_type_name(name)}; `claude plugin validate` reports 'name must be a string' (runtime stringifies it)", "quote the name", line=e.line("name"))
    elif isinstance(name, str) and name.strip() and name.strip() != dir_name:
        e.add("claude-code-name-from-directory", "warning", f"frontmatter name {name.strip()!r} differs from the directory name {dir_name!r}; the command is /{dir_name} and the name is only a display label and alias",
              "make name equal to the directory name", line=e.line("name"))
    # description
    desc = data.get("description")
    if "description" not in data:
        e.add("claude-code-description-optional-fallback", "warning", "no description; Claude Code falls back to the first body line, which is rarely a good trigger", "add a description", line=2)
    elif desc is None or (isinstance(desc, str) and (not desc.strip() or desc.lstrip().startswith("#"))):
        e.add("claude-code-description-empty-value", "warning", "description is empty/null and is treated as missing at runtime (body-line fallback)", "write a real description", line=e.line("description"))
    elif isinstance(desc, (list, dict)):
        e.add("claude-code-description-type", "error", f"description is a {_type_name(desc)}; it is dropped ('Description invalid ... omitting') and the body line is used", "write a string", line=e.line("description"))
    elif not isinstance(desc, str):
        e.add("claude-code-description-type", "warning", f"description is a {_type_name(desc)} and is stringified to {_short(str(desc))!r}", "quote it", line=e.line("description"))
    else:
        wtu = data.get("when_to_use")
        combined = len(desc.strip()) + (3 + len(str(wtu)) if wtu is not None else 0)
        if combined > CLAUDE_LISTING_DESC_CAP:
            e.add("claude-code-description-listing-cap", "warning", f"description{' + when_to_use' if wtu is not None else ''} is {combined} characters; the model listing cuts it at {CLAUDE_LISTING_DESC_CAP}",
                  "front-load the key use cases and shorten", line=e.line("description"))
    # keys
    for key in ("disable-model-invocation", "user-invocable"):
        if key in data and _claude_bool(data[key]) is None:
            rid = "claude-code-key-disable-model-invocation" if key == "disable-model-invocation" else "claude-code-key-user-invocable"
            consequence = "silently counts as false" if key == "disable-model-invocation" else "counts as FALSE and hides the skill from the / menu"
            e.add(rid, "error", f"{key}: {_short(data[key])} is not a recognised boolean; it {consequence}", "use true or false", line=e.line(key))
    if "allowed-tools" in data:
        _check_claude_tools(e, "allowed-tools", "claude-code-key-allowed-tools")
    for key in ("disallowed-tools", "disallowedTools"):
        if key in data:
            _check_claude_tools(e, key, "claude-code-key-disallowed-tools")
    if "shell" in data and data["shell"] not in (None, "") and str(data["shell"]).strip().lower() not in ("bash", "powershell"):
        e.add("claude-code-key-shell", "warning", f"shell: {_short(data['shell'])} is not bash or powershell; Claude Code falls back to bash", "use bash or powershell", line=e.line("shell"))
    if "effort" in data and data["effort"] not in (None, ""):
        eff = data["effort"]
        ok = (isinstance(eff, int) and not isinstance(eff, bool)) or (isinstance(eff, str) and (eff.lower() in CLAUDE_EFFORT_VALUES or re.match(r"^\s*-?\d+", eff)))
        if not ok:
            e.add("claude-code-key-effort", "warning", f"effort: {_short(eff)} is invalid and ignored ('Valid options: low, medium, high, xhigh, max or an integer')", "use one of the listed values", line=e.line("effort"))
    if "context" in data and data["context"] != "fork":
        e.add("claude-code-key-context-agent-background", "warning", f"context: {_short(data['context'])} has no effect; only the exact string fork does", "use `context: fork` or remove the key", line=e.line("context"))
    if data.get("context") != "fork":
        for key in ("agent", "background"):
            if key in data:
                e.add("claude-code-key-context-agent-background", "warning", f"{key} is only used together with `context: fork`", "add `context: fork` or remove the key", line=e.line(key))
    if "model" in data and (not isinstance(data["model"], str) or not data["model"].strip()):
        e.add("claude-code-key-model", "warning", f"model must be a non-empty string, got {_type_name(data['model'])}; it is ignored", "use a model alias, id or inherit", line=e.line("model"))
    if "paths" in data:
        paths = data["paths"]
        if isinstance(paths, str):
            patterns = [p.strip() for p in re.split(r",(?![^{]*})", paths) if p.strip()]
        elif isinstance(paths, list):
            patterns = [p.strip() for p in paths if isinstance(p, str) and p.strip()]
            if any(not isinstance(p, str) for p in paths):
                e.add("claude-code-key-paths", "error", "paths list contains non-string items (dropped)", "quote every glob", line=e.line("paths"))
        else:
            patterns = []
            e.add("claude-code-key-paths", "error", f"paths must be a comma-separated string or a list, got {_type_name(paths)}", "write `paths: \"src/**/*.py\"`", line=e.line("paths"))
        patterns = [p[:-3] if p.endswith("/**") else p for p in patterns]
        real = [p for p in patterns if p and p != "**"]
        if real:
            e.add("claude-code-key-paths", "info", f"paths is set ({', '.join(_short(p, 30) for p in real[:3])}); the skill is withheld from the model until a matching file is read or edited",
                  "no action needed if the scoping is intended", line=e.line("paths"))
            if "**" in patterns:
                e.add("claude-code-key-paths", "warning", "paths mixes '**' with other globs; the skill activates on the first file touched", "drop the '**' entry", line=e.line("paths"))
            expansions = 0
            for p in patterns:
                sets = re.findall(r"\{([^{}]*)\}", p)
                count = 1
                for s in sets:
                    count *= max(1, len(s.split(",")))
                expansions += count
            if expansions > 1000:
                e.add("claude-code-key-paths", "warning", f"paths expands to about {expansions} patterns (budget 1,000); patterns over budget are used unexpanded", "simplify the brace sets", line=e.line("paths"))
    if "metadata" in data and data["metadata"] is not None:
        meta = data["metadata"]
        if not isinstance(meta, dict):
            e.add("claude-code-key-metadata-license-compatibility", "warning", f"metadata is a {_type_name(meta)}; Claude Code drops a value that is not a map", "write a mapping", line=e.line("metadata"))
        else:
            reused = [str(k) for k in meta if str(k) in CLAUDE_KEYS and str(k) not in ("metadata", "license", "compatibility", "version", "name", "description")]
            if reused:
                e.add("claude-code-key-metadata-license-compatibility", "warning", f"metadata reuses frontmatter field names as keys: {', '.join(reused)} (the docs advise against it)", "rename the metadata keys", line=e.line("metadata"))
    for key in ("argument-hint", "when_to_use", "version", "agent"):
        if key in data and not _is_scalar(data[key]):
            e.add("claude-code-key-scalar-coercions", "warning", f"{key} is a {_type_name(data[key])} and is stringified with String()", "use a scalar", line=e.line(key))
    if "arguments" in data:
        args = data["arguments"]
        names: list[str] = []
        if isinstance(args, str):
            names = args.split()
        elif isinstance(args, list):
            names = [a for a in args if isinstance(a, str)]
            if any(not isinstance(a, str) for a in args):
                e.add("claude-code-key-scalar-coercions", "warning", "arguments list contains non-string items (dropped)", "list identifiers as strings", line=e.line("arguments"))
        else:
            e.add("claude-code-key-scalar-coercions", "warning", f"arguments must be a space-separated string or a list, got {_type_name(args)}", "write `arguments: source target`", line=e.line("arguments"))
        for n in names:
            if re.fullmatch(r"\d+", n):
                e.add("claude-code-key-scalar-coercions", "warning", f"argument name {n!r} is all digits and is dropped", "use a word", line=e.line("arguments"))
            elif f"${n}" not in ctx.body:
                e.add("claude-code-body-substitutions", "info", f"declared argument {n!r} is never used as ${n} in the body", "use the placeholder or drop the declaration", line=e.line("arguments"))
    _claude_body_checks(e)
    return e.findings


def _claude_body_checks(e: Emitter) -> None:
    ctx = e.ctx
    for name, lines in ctx.substitutions.items():
        if name in CLAUDE_PLUGIN_SUBSTITUTIONS:
            e.add("claude-code-body-substitutions", "warning", f"${{{name}}} is substituted only in plugin skills; here it stays literal", "use ${CLAUDE_SKILL_DIR} for bundled files", line=lines[0])
        elif name not in CLAUDE_SUBSTITUTIONS:
            e.add("claude-code-body-substitutions", "warning", f"${{{name}}} is not a Claude Code substitution (supported: CLAUDE_SKILL_DIR, CLAUDE_PROJECT_DIR, CLAUDE_SESSION_ID, CLAUDE_EFFORT); it stays literal",
                  "check the variable name", line=lines[0])
    shell_lines = ctx.constructs.get("inline_shell", []) + ctx.constructs.get("shell_fence", [])
    if shell_lines:
        e.add("claude-code-body-inline-shell", "warning", f"inline shell (!`command` or ```!) on line {min(shell_lines)} runs before the body is sent; a non-zero exit aborts the whole invocation",
              "append `|| true` to tolerant commands and grant the tool in allowed-tools", line=min(shell_lines))
    if ctx.line_count > 500:
        e.add("claude-code-body-500-lines", "warning", f"SKILL.md has {ctx.line_count} lines (docs: keep it under 500)", "move detail to referenced files", line=501)
    if len(ctx.body) > 20_000:
        e.add("claude-code-body-compaction-budget", "warning", f"body is {len(ctx.body)} characters (~{len(ctx.body) // 4} tokens); after auto-compaction only the first 5,000 tokens are re-attached",
              "put the essential instructions first or shorten the body", line=ctx.body_start_line)
    for ref in _missing_refs(ctx):
        e.add("claude-code-files-supporting", "warning", f"referenced file {ref.text} does not exist in the skill directory", "fix the path or add the file", line=ref.line)


# --------------------------------------------------------------------------- #
# Profile: codex (OpenAI Codex CLI 0.147.0, with 0.153.0 drift)
# --------------------------------------------------------------------------- #

_rule("codex-disc-no-claude-skills-dir", "codex", "warning", "the body does not point at .claude/ paths (Codex never scans .claude/skills)")
_rule("codex-disc-skill-filename-case-sensitive", "codex", "error", "the skill file is named exactly SKILL.md")
_rule("codex-disc-every-skill-md-is-a-skill", "codex", "warning", "no second SKILL.md below the skill directory (it would load as a separate skill)")
_rule("codex-disc-hidden-dirs-pruned", "codex", "error", "the skill directory name does not start with '.'")
_rule("codex-disc-symlinked-skill-md-ignored", "codex", "error", "SKILL.md is not a symlinked file (directory symlinks are fine)")
_rule("codex-disc-scan-truncation-limits", "codex", "error", "the skill directory holds fewer than 2,000 directories and 20,000 entries")
_rule("codex-disc-plugin-manifest-namespacing", "codex", "error/warning", "a plugin manifest above the skill namespaces it as plugin:name (warning); the qualified name is at most 128 characters (error)")
_rule("codex-disc-dedupe-by-path-only", "codex", "warning", "runtime names are unique across the catalog (duplicates make $name ambiguous; see codex-name-mention-exact-and-unique)")
_rule("codex-files-unreadable-or-directory", "codex", "error", "SKILL.md is a readable regular file")
_rule("codex-fm-opening-delimiter", "codex", "error", "the first line trims to '---' and there is no BOM")
_rule("codex-fm-closing-delimiter-and-nonempty-block", "codex", "error", "a later line trims to '---' with at least one line between")
_rule("codex-fm-triple-dash-line-truncates", "codex", "error", "no line inside the block (e.g. inside a block scalar) trims to '---'")
_rule("codex-fm-cr-only-rejected", "codex", "error", "line endings are LF or CRLF")
_rule("codex-fm-must-be-yaml-mapping", "codex", "error", "the block is a YAML mapping")
_rule("codex-fm-yaml-dialect", "codex", "error", "serde_yaml accepts the block: no tab indentation, no unquoted %-leading value, no undefined *alias, no trailing ':'")
_rule("codex-fm-duplicate-keys-typed-fields", "codex", "error/warning", "no duplicate name/description/metadata/metadata.short-description keys (error); other duplicates load silently (warning)")
_rule("codex-fm-anchors-tags-stripped", "codex", "warning", "no unquoted name/description starting with & or ! (token stripped) or containing ' #' (truncated)")
_rule("codex-fm-colon-repair", "codex", "info", "an unquoted ': ' loads only through Codex's colon repair")
_rule("codex-fm-flow-collections-coerced", "codex", "warning", "a flow collection containing ': ' becomes a literal string name/description")
_rule("codex-keys-ignored-values-must-parse", "codex", "error", "values of ignored keys still parse: no unquoted value or list item starting with * or %")
_rule("codex-files-utf8-required", "codex", "error", "the file decodes as UTF-8")
_rule("codex-name-fallback-to-directory", "codex", "warning", "name is present (a missing name falls back to the directory basename)")
_rule("codex-name-max-64-chars", "codex", "error", "the whitespace-collapsed effective name has at most 64 code points")
_rule("codex-name-whitespace-collapsed", "codex", "warning", "name has no runs of whitespace (collapsed at runtime)")
_rule("codex-name-scalar-coercion", "codex", "error/warning", "name is a scalar (list/mapping rejects the skill: error; a non-string scalar is stringified: warning)")
_rule("codex-name-charset-unrestricted", "codex", "warning", "name matches the skill-creator rule ^[a-z0-9-]+$ without edge or double hyphens")
_rule("codex-name-directory-match-not-required", "codex", "warning", "name equals the directory basename")
_rule("codex-name-mentionable-charset", "codex", "warning", "the effective name matches [A-Za-z0-9_:-]+ so $name can be typed")
_rule("codex-name-env-var-blocklist", "codex", "warning", "the name is not PATH, HOME, USER, SHELL, PWD, TMPDIR, TEMP, TMP, LANG, TERM or XDG_CONFIG_HOME")
_rule("codex-name-colon-space", "codex", "warning", "the effective name contains no whitespace or ': '")
_rule("codex-desc-required-nonempty", "codex", "error", "description is present and non-empty after whitespace collapsing")
_rule("codex-desc-must-be-scalar", "codex", "error/warning", "description is a scalar (list/mapping rejects the skill; a non-string scalar is stringified)")
_rule("codex-desc-collapsed-to-one-line", "codex", "info", "line breaks in the description are flattened to spaces")
_rule("codex-desc-no-load-limit-but-1024-in-catalog", "codex", "warning", "description is at most 1024 characters (the catalog line is cut there)")
_rule("codex-desc-catalog-budget", "codex", "warning", "the catalog's skill lines fit the 8,000-character model-visible budget (0.153.0 root-relative rendering; see codex-desc-catalog-render-0153)")
_rule("codex-desc-angle-brackets", "codex", "warning", "description contains no < or > (skill-creator quick_validate rejects them)")
_rule("codex-desc-todo-placeholder", "codex", "warning", "no '[TODO:' placeholder in the description or an unfenced body line")
_rule("codex-keys-only-name-description-short-description", "codex", "warning/info", "keys other than name, description and metadata.short-description have no effect (behavioural keys: warning)")
_rule("codex-key-disable-model-invocation-ignored", "codex", "warning/info", "disable-model-invocation / user-invocable have no effect (a true value is a warning: the skill stays model-visible)")
_rule("codex-key-metadata-short-description", "codex", "warning/info", "metadata.short-description, when present, is a non-empty scalar (feeds the TUI picker only); short_description / top-level short-description are not read")
_rule("codex-key-metadata-must-be-mapping", "codex", "error", "metadata is a mapping or null and metadata.short-description is a scalar")
_rule("codex-body-explicit-injection-no-cap", "codex", "warning/info", "$ARGUMENTS/${CLAUDE_*}/inline shell in the body are injected verbatim (warning); very large bodies are injected uncapped (info)")
_rule("codex-body-size-recommendations", "codex", "warning", "SKILL.md has at most 500 lines")
_rule("codex-files-openai-yaml-fail-open", "codex", "warning", "agents/openai.yaml, when present, parses as YAML with recognised field types")
_rule("codex-files-openai-yaml-exact-case", "codex", "warning", "the sidecar is at exactly agents/openai.yaml (case variants are ignored on Linux)")
_rule("codex-files-openai-yaml-allow-implicit-invocation", "codex", "warning/info", "policy.allow_implicit_invocation is a boolean; false hides the skill from implicit selection")
_rule("codex-files-openai-yaml-interface-constraints", "codex", "warning", "interface.display_name <= 64, short_description/default_prompt <= 1024, brand_color is #RRGGBB, icons live under assets/")
_rule("codex-files-openai-yaml-dependencies", "codex", "warning", "dependencies.tools[] entries have string type (<= 64) and value (<= 1024)")


def _codex_hidden_from_catalog(ctx: SkillContext) -> bool:
    """True when agents/openai.yaml keeps the skill out of the model-visible list."""

    oy = ctx.openai_yaml
    if oy is None or oy.error is not None or not isinstance(oy.parsed, dict):
        return False
    policy = oy.parsed.get("policy")
    return isinstance(policy, dict) and policy.get("allow_implicit_invocation") is False


def _codex_effective_name(ctx: SkillContext, data: dict) -> tuple[str, str]:
    """(effective runtime name, source) following Codex's fallback rules."""

    name = data.get("name")
    if isinstance(name, str) and name.strip():
        return " ".join(name.split()), "frontmatter"
    if name is not None and not isinstance(name, (str, list, dict)):
        return " ".join(str(name).split()), "frontmatter"
    try:
        base = ctx.entry.dir.resolve().name
    except OSError:
        base = ctx.entry.dir.name
    return " ".join(base.split()) or "skill", "directory"


def _check_openai_yaml(e: Emitter) -> None:
    ctx = e.ctx
    oy = ctx.openai_yaml
    if oy is None:
        return
    file = _display_path(oy.path)
    for variant in oy.variants:
        e.add("codex-files-openai-yaml-exact-case", "warning", f"{variant} is not read: Codex probes only the exact path <skill>/agents/openai.yaml (a case variant works on macOS, never on Linux)",
              "rename it to agents/openai.yaml", file=_display_path(ctx.entry.dir / variant))
    if oy.error is not None:
        e.add("codex-files-openai-yaml-fail-open", "warning", f"agents/openai.yaml is ignored ('invalid openai.yaml: {oy.error}'); the skill loads without interface/policy", "fix the YAML", file=file)
        return
    doc = oy.parsed
    if doc is None:
        return
    if not isinstance(doc, dict):
        e.add("codex-files-openai-yaml-fail-open", "warning", f"agents/openai.yaml is a {_type_name(doc)}, not a mapping; it is ignored", "use interface/policy/dependencies mappings", file=file)
        return
    policy = doc.get("policy")
    if policy is not None:
        if not isinstance(policy, dict):
            e.add("codex-files-openai-yaml-fail-open", "warning", "policy is not a mapping; the whole openai.yaml is discarded", "write `policy:\\n  allow_implicit_invocation: false`", file=file)
        elif "allow_implicit_invocation" in policy:
            aii = policy["allow_implicit_invocation"]
            if not isinstance(aii, bool):
                e.add("codex-files-openai-yaml-allow-implicit-invocation", "warning", f"policy.allow_implicit_invocation is {_short(aii)}, not a boolean; the whole openai.yaml is discarded and implicit invocation stays allowed", "use true or false", file=file)
            elif aii is False:
                e.add("codex-files-openai-yaml-allow-implicit-invocation", "info", "policy.allow_implicit_invocation: false hides the skill from the model catalog; $name still works", "no action needed if intended", file=file)
    iface = doc.get("interface")
    if iface is not None:
        if not isinstance(iface, dict):
            e.add("codex-files-openai-yaml-fail-open", "warning", "interface is not a mapping; the whole openai.yaml is discarded", "write a mapping", file=file)
        else:
            limits = {"display_name": 64, "short_description": 1024, "default_prompt": 1024}
            for key, limit in limits.items():
                val = iface.get(key)
                if val is not None:
                    text = " ".join(str(val).split())
                    if not text or len(text) > limit:
                        e.add("codex-files-openai-yaml-interface-constraints", "warning", f"interface.{key} is {'empty' if not text else f'{len(text)} characters (max {limit})'} and is dropped", "shorten it", file=file)
            color = iface.get("brand_color")
            if color is not None and not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(color).strip()):
                e.add("codex-files-openai-yaml-interface-constraints", "warning", f"interface.brand_color {_short(color)} is not #RRGGBB and is dropped", "use a 6-digit hex colour", file=file)
            for key in ("icon_small", "icon_large"):
                icon = iface.get(key)
                if icon is not None and not re.match(r"^(\./)*assets(/|$)", str(icon)):
                    e.add("codex-files-openai-yaml-interface-constraints", "warning", f"interface.{key} {_short(icon)} must be a relative path under assets/", "move the icon under assets/", file=file)
    deps = doc.get("dependencies")
    if deps is not None:
        tools = deps.get("tools") if isinstance(deps, dict) else None
        if not isinstance(deps, dict):
            e.add("codex-files-openai-yaml-fail-open", "warning", "dependencies is not a mapping; the whole openai.yaml is discarded", "write `dependencies:\\n  tools: [...]`", file=file)
        elif tools is not None:
            if not isinstance(tools, list):
                e.add("codex-files-openai-yaml-dependencies", "warning", "dependencies.tools is not a list", "write a list of {type, value} entries", file=file)
            else:
                for i, tool in enumerate(tools):
                    if not isinstance(tool, dict) or not isinstance(tool.get("type"), str) or not isinstance(tool.get("value"), str):
                        e.add("codex-files-openai-yaml-dependencies", "warning", f"dependencies.tools[{i}] needs string type and value; it is dropped", "add both fields", file=file)
                    elif len(tool["type"]) > 64 or len(tool["value"]) > 1024:
                        e.add("codex-files-openai-yaml-dependencies", "warning", f"dependencies.tools[{i}] exceeds the length limits (type 64, value 1024)", "shorten the entry", file=file)


def profile_codex(ctx: SkillContext) -> list[Finding]:
    e = Emitter(ctx, "codex")
    dir_name = ctx.entry.dir.name
    if ctx.is_symlink:
        e.add("codex-disc-symlinked-skill-md-ignored", "error", "SKILL.md is a symbolic link; Codex ignores symlinked files (symlink the directory instead)", "replace the file link with a directory symlink or a copy")
        if ctx.dangling_symlink:
            return e.findings
    if ctx.entry.filename != "SKILL.md":
        e.add("codex-disc-skill-filename-case-sensitive", "error", f"skill file is named {ctx.entry.filename}; Codex only loads the exact name SKILL.md", "rename it to SKILL.md")
    if dir_name.startswith("."):
        e.add("codex-disc-hidden-dirs-pruned", "error", f"directory {dir_name!r} is hidden and is never descended", "use a visible directory name")
    if ctx.read_error and not ctx.dangling_symlink:
        e.add("codex-files-unreadable-or-directory", "error", f"SKILL.md cannot be read ({ctx.read_error}): 'failed to read file'", "make SKILL.md a readable regular file")
        return e.findings
    if not ctx.readable:
        e.add("codex-files-unreadable-or-directory", "error", "SKILL.md is not readable ('failed to read file: Permission denied')", "chmod +r SKILL.md")
    if ctx.dir_count >= CODEX_MAX_DIRS_PER_ROOT or ctx.entry_count > CODEX_MAX_ENTRIES_PER_ROOT:
        e.add("codex-disc-scan-truncation-limits", "error", f"the skill directory holds {ctx.dir_count} directories / {ctx.entry_count}+ entries; a root scan stops at 2,000 directories or 20,000 entries",
              "remove generated data from the skill directory")
    # Installed as <root>/.agents/skills/<dirname>/, a nested SKILL.md sits
    # 1 + <its depth below the skill> levels under the root; Codex stops at 6.
    visible_nested = [p for p, hidden in ctx.nested_skill_files if not hidden]
    loaded_nested = [p for p in visible_nested if 1 + p.count("/") <= 6]
    deep_nested = [p for p in visible_nested if 1 + p.count("/") > 6]
    if loaded_nested:
        e.add("codex-disc-every-skill-md-is-a-skill", "warning", f"additional SKILL.md below the skill ({loaded_nested[0]}); Codex loads it as a separate skill named after its parent directory",
              "rename or move the nested file", file=_display_path(ctx.entry.dir / loaded_nested[0]))
    elif deep_nested:
        e.add("codex-disc-every-skill-md-is-a-skill", "warning", f"additional SKILL.md below the skill ({deep_nested[0]}); installed it sits more than 6 directory levels below the skills root, so Codex silently skips it (codex-disc-max-depth-6)",
              "move it nearer the skill root if it is meant to load, or rename it", file=_display_path(ctx.entry.dir / deep_nested[0]))
    if ctx.decode_error:
        e.add("codex-files-utf8-required", "error", f"SKILL.md is not valid UTF-8 ({ctx.decode_error}): 'failed to read file: invalid utf-8 sequence'", "re-save as UTF-8")
        return e.findings
    if ctx.has_cr_only:
        e.add("codex-fm-cr-only-rejected", "error", "CR-only line endings; Rust str::lines never finds the '---' lines ('missing YAML frontmatter delimited by ---')", "convert the file to LF line endings", line=1)
    # delimiters
    lines = ctx.lines
    opener_ok = bool(lines) and lines[0].strip() == "---" and not ctx.has_bom
    if not opener_ok:
        why = "a UTF-8 BOM precedes it" if ctx.has_bom else f"the first line is {_short(lines[0] if lines else '')!r}"
        e.add("codex-fm-opening-delimiter", "error", f"first line must trim to '---' but {why} ('missing YAML frontmatter delimited by ---')", "start the file with a bare `---` line (no BOM)", line=1)
        _codex_body_checks(e)
        return e.findings
    closer = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closer = i
            break
    if closer is None or closer == 1:
        e.add("codex-fm-closing-delimiter-and-nonempty-block", "error", "no closing line trimming to '---' with at least one line before it ('missing YAML frontmatter delimited by ---')", "close the frontmatter with a `---` line after the keys", line=1)
        _codex_body_checks(e)
        return e.findings
    strict_close = ctx.fm_close_index
    if strict_close is not None and closer < strict_close:
        e.add("codex-fm-triple-dash-line-truncates", "error", f"line {closer + 1} trims to '---' inside the frontmatter; Codex ends the block there and the rest becomes body", "remove the '---' line from the value", line=closer + 1)
    if ctx.fm_doc_end_lines and strict_close is None:
        pass
    # YAML
    repaired = False
    if ctx.parse_error is not None:
        if ctx.codex_repair_ok:
            repaired = True
            e.add("codex-fm-colon-repair", "info", f"frontmatter parses only through Codex's colon repair ({ctx.parse_error}); other harnesses reject or truncate it", "quote the value with ': '", line=ctx.parse_error_line)
        else:
            e.add("codex-fm-yaml-dialect", "error", f"invalid YAML for serde_yaml ({ctx.parse_error}); the skill is not loaded ('invalid YAML: ...')", "fix the YAML: spaces for indentation, quote values starting with % * or containing ': ', no trailing ':'", line=ctx.parse_error_line)
    data = ctx.codex_repair_parsed if repaired else ctx.parsed
    if ctx.parse_error is not None and not repaired:
        _codex_lexical_checks(e)
        _codex_body_checks(e)
        return e.findings
    if data is None or (isinstance(data, dict) and not data):
        e.add("codex-desc-required-nonempty", "error", "empty (or comment-only) frontmatter: 'missing field `description`'", "add name and description", line=2)
        _codex_body_checks(e)
        return e.findings
    if not isinstance(data, dict):
        e.add("codex-fm-must-be-yaml-mapping", "error", f"frontmatter is a {_type_name(data)} ('invalid type: {_type_name(data)}, expected struct SkillFrontmatter')", "write `key: value` lines", line=2)
        _codex_body_checks(e)
        return e.findings
    for key, line, first in ctx.dup_keys:
        if key in ("name", "description", "metadata", "short-description"):
            e.add("codex-fm-duplicate-keys-typed-fields", "error", f"duplicate key {key!r} ('invalid YAML: duplicate field `{key}`'); the skill is not loaded", "keep one occurrence", line=line)
        else:
            e.add("codex-fm-duplicate-keys-typed-fields", "warning", f"duplicate key {key!r} loads silently in Codex (last wins) but is rejected by skills-ref, Antigravity and Cursor", "keep one occurrence", line=line)
    _codex_lexical_checks(e)
    # name
    name = data.get("name")
    eff, source = _codex_effective_name(ctx, data)
    if isinstance(name, (list, dict)):
        raw = ctx.top("name")
        if raw is not None and raw.style == "flow" and re.search(r":[ \t]", raw.raw):
            e.add("codex-fm-flow-collections-coerced", "warning", f"name is a flow collection containing ': '; Codex loads the literal text {_short(raw.raw)!r} as the name", "write a plain string name", line=e.line("name"))
        else:
            e.add("codex-name-scalar-coercion", "error", f"name is a {_type_name(name)} ('invalid type: sequence|map, expected a string'); the skill is not loaded", "write a string", line=e.line("name"))
    elif "name" in data and name is not None and not isinstance(name, str):
        e.add("codex-name-scalar-coercion", "warning", f"name is a {_type_name(name)}; Codex uses its literal text {eff!r} (other validators reject it)", "quote the name", line=e.line("name"))
    if source == "directory":
        e.add("codex-name-fallback-to-directory", "warning", f"no usable name; Codex uses the directory basename {eff!r} (other harnesses need an explicit name)", f"add `name: {dir_name}`", line=e.line("name") or 2)
    elif isinstance(name, str) and " ".join(name.split()) != name:
        e.add("codex-name-whitespace-collapsed", "warning", f"name {_short(name)!r} is whitespace-collapsed to {eff!r} at runtime", "write the name without extra whitespace", line=e.line("name"))
    if len(eff) > 64:
        e.add("codex-name-max-64-chars", "error", f"effective name {_short(eff)!r} has {len(eff)} code points ('invalid name: exceeds maximum length of 64 characters')", "shorten the name" + (" (directory)" if source == "directory" else ""), line=e.line("name"))
    if ctx.plugin_manifest is not None:
        qualified = f"{ctx.plugin_manifest_name}:{eff}" if ctx.plugin_manifest_name else eff
        if ctx.plugin_manifest_name:
            e.add("codex-disc-plugin-manifest-namespacing", "warning", f"{ctx.plugin_manifest_rel} inside the skill namespaces it as {qualified!r} (that is the $mention name)", "remove the manifest or use the qualified name", line=e.line("name"))
            if len(qualified) > 128:
                e.add("codex-disc-plugin-manifest-namespacing", "error", f"qualified name {_short(qualified)!r} has {len(qualified)} characters (max 128 on 0.147.0)", "shorten the plugin or skill name", line=e.line("name"))
    if not re.fullmatch(r"[a-z0-9-]+", eff) or eff.startswith("-") or eff.endswith("-") or "--" in eff:
        e.add("codex-name-charset-unrestricted", "warning", f"effective name {_short(eff)!r} does not follow skill-creator's ^[a-z0-9-]+$ / no edge or double hyphen rule (loads anyway)", "use lowercase letters, digits and single hyphens", line=e.line("name"))
    if source == "frontmatter" and eff != dir_name:
        e.add("codex-name-directory-match-not-required", "warning", f"name {eff!r} differs from the directory {dir_name!r} (Codex does not care; the spec and unpack.sh do)", "make them identical", line=e.line("name"))
    if re.search(r"\s", eff) or ": " in eff:
        e.add("codex-name-colon-space", "warning", f"effective name {_short(eff)!r} contains whitespace or ': '; it renders ambiguously in the model list and cannot be $-mentioned", "use a single hyphenated token", line=e.line("name"))
    elif not CODEX_MENTION_RE.fullmatch(eff):
        e.add("codex-name-mentionable-charset", "warning", f"effective name {_short(eff)!r} is not [A-Za-z0-9_:-]+, so $name cannot be typed (only the /skills picker works)", "use ASCII letters, digits, '_', '-' or ':'", line=e.line("name"))
    if eff.upper() in CODEX_ENV_VAR_NAMES:
        e.add("codex-name-env-var-blocklist", "warning", f"name {eff!r} is treated as an environment variable; $name never selects the skill", "rename the skill", line=e.line("name"))
    # description
    desc = data.get("description")
    raw_desc = ctx.top("description")
    if isinstance(desc, (list, dict)):
        if raw_desc is not None and raw_desc.style == "flow" and re.search(r":[ \t]", raw_desc.raw):
            e.add("codex-fm-flow-collections-coerced", "warning", f"description is a flow collection containing ': '; Codex loads the literal text {_short(raw_desc.raw)!r}", "write a plain string", line=e.line("description"))
        else:
            e.add("codex-desc-must-be-scalar", "error", f"description is a {_type_name(desc)} ('invalid type: sequence|map, expected a string'); the skill is not loaded", "write a string", line=e.line("description"))
    else:
        text = " ".join(str(desc).split()) if desc is not None else ""
        if raw_desc is not None and raw_desc.style == "plain" and raw_desc.raw.startswith("#"):
            text = ""
        if not text:
            e.add("codex-desc-required-nonempty", "error", "description is missing or empty ('missing field `description`'); the skill is not loaded", "add a non-empty description", line=e.line("description") or 2)
        else:
            if not isinstance(desc, str):
                e.add("codex-desc-must-be-scalar", "warning", f"description is a {_type_name(desc)} and is used as the text {_short(text)!r}", "quote it", line=e.line("description"))
            if isinstance(desc, str) and "\n" in desc.strip():
                e.add("codex-desc-collapsed-to-one-line", "info", "line breaks in the description are collapsed to single spaces in the catalog", "no action needed", line=e.line("description"))
            if len(text) > CODEX_CATALOG_DESC_CAP:
                e.add("codex-desc-no-load-limit-but-1024-in-catalog", "warning", f"description is {len(text)} characters; the model-visible catalog line is cut at 1024", "shorten the description", line=e.line("description"))
            if "<" in text or ">" in text:
                e.add("codex-desc-angle-brackets", "warning", "description contains '<' or '>' (loads at runtime, but skill-creator's quick_validate rejects it)", "rephrase without angle brackets", line=e.line("description"))
            if text.startswith("[TODO:"):
                e.add("codex-desc-todo-placeholder", "warning", "description starts with a [TODO: placeholder", "finish the description", line=e.line("description"))
    if "todo" in ctx.constructs:
        e.add("codex-desc-todo-placeholder", "warning", f"[TODO: ...] placeholder line in the body (line {ctx.constructs['todo'][0]})", "resolve the placeholder", line=ctx.constructs["todo"][0])
    # metadata
    if "metadata" in data and data["metadata"] is not None:
        meta = data["metadata"]
        if not isinstance(meta, dict):
            e.add("codex-key-metadata-must-be-mapping", "error", f"metadata is a {_type_name(meta)} ('invalid type: ..., expected struct SkillFrontmatterMetadata'); the skill is not loaded", "write a mapping or remove the key", line=e.line("metadata"))
        else:
            sd = meta.get("short-description")
            if "short-description" in meta:
                if isinstance(sd, (list, dict)):
                    e.add("codex-key-metadata-must-be-mapping", "error", "metadata.short-description is not a scalar; the skill is not loaded", "write a string", line=e.line("metadata"))
                elif sd is None or not " ".join(str(sd).split()):
                    e.add("codex-key-metadata-short-description", "warning", "metadata.short-description is empty and is ignored", "fill it in or remove it", line=e.line("metadata"))
                else:
                    e.add("codex-key-metadata-short-description", "info", "metadata.short-description feeds the /skills picker only; the model still sees description", "no action needed", line=e.line("metadata"))
            if "short_description" in meta:
                e.add("codex-key-metadata-short-description", "warning", "metadata.short_description (underscore) is not read; the key is metadata.short-description", "rename the key", line=e.line("metadata"))
    if "short-description" in data:
        e.add("codex-key-metadata-short-description", "warning", "top-level short-description is not read; only metadata.short-description is", "move it under metadata:", line=e.line("short-description"))
    # ignored keys
    for key in ("disable-model-invocation", "user-invocable"):
        if key in data:
            val = data[key]
            truthy = _claude_bool(val)
            if (key == "disable-model-invocation" and truthy) or (key == "user-invocable" and truthy is False):
                e.add("codex-key-disable-model-invocation-ignored", "warning", f"`{key}: {_raw_value(ctx, key)}` has no effect in Codex: the skill stays model-visible and user-invocable", "use agents/openai.yaml `policy.allow_implicit_invocation: false` to hide it from the model", line=e.line(key))
            else:
                e.add("codex-key-disable-model-invocation-ignored", "info", f"{key} is ignored by Codex", "no action needed", line=e.line(key))
    honored = set(CODEX_KEYS) | {"disable-model-invocation", "user-invocable", "short-description"}
    _ignored_key_findings(e, honored, "codex-keys-only-name-description-short-description", None, "Codex", skip=(), consequence={
        "paths": "the skill is never scoped to files", "context": "no forked subagent", "hooks": "no hooks are registered",
        "allowed-tools": "no tool permissions are granted", "model": "the model is not switched", "effort": "effort is unchanged",
    })
    _check_openai_yaml(e)
    _codex_body_checks(e)
    return e.findings


def _codex_lexical_checks(e: Emitter) -> None:
    ctx = e.ctx
    for line, kind in _tab_positions(ctx):
        if kind == "indent":
            e.add("codex-fm-yaml-dialect", "error", "tab used as indentation ('found character that cannot start any token'); the skill is not loaded", "indent with spaces", line=line)
    for entry in ctx.entries:
        if entry.style != "plain":
            continue
        h = _hazards(entry)
        key = entry.top_key or "?"
        typed = key in ("name", "description")
        if h.lead == "%" or (h.lead == "*" and ctx.parse_error is not None):
            rid = "codex-fm-yaml-dialect" if typed else "codex-keys-ignored-values-must-parse"
            e.add(rid, "error", f"unquoted value of {'.'.join(str(p) for p in entry.path)} starts with '{h.lead}' ({'directive' if h.lead == '%' else 'undefined alias'}); the whole skill is rejected",
                  "quote the value (globs like **/*.py must be quoted)", line=entry.line)
        if h.trailing_colon and not h.colon_space:
            e.add("codex-fm-yaml-dialect", "error", f"unquoted value of {key} ends with ':' ('mapping values are not allowed in this context'); the colon repair does not cover it", "quote the value", line=entry.line)
        if typed:
            if h.lead in ("&", "!"):
                e.add("codex-fm-anchors-tags-stripped", "warning", f"unquoted {key} starts with '{h.lead}'; the token is silently removed", "quote the value", line=entry.line)
            if h.space_hash:
                e.add("codex-fm-anchors-tags-stripped", "warning", f"unquoted {key} contains ' #'; the rest is a comment and the value loads as {_short(entry.plain_value)!r}", "quote the value", line=entry.line)


def _codex_body_checks(e: Emitter) -> None:
    ctx = e.ctx
    if ctx.line_count > 500:
        e.add("codex-body-size-recommendations", "warning", f"SKILL.md has {ctx.line_count} lines (spec recommendation: under 500)", "move detail to referenced files", line=501)
    if len(ctx.body) > 20_000:
        e.add("codex-body-explicit-injection-no-cap", "info", f"$name injects the whole file ({ctx.size} bytes, ~{ctx.size // 4} tokens) uncapped", "keep SKILL.md focused", line=ctx.body_start_line)
    claude_only = []
    if "arguments" in ctx.constructs:
        claude_only.append(("$ARGUMENTS/$N", ctx.constructs["arguments"][0]))
    if ctx.substitutions:
        name, lines = next(iter(ctx.substitutions.items()))
        claude_only.append((f"${{{name}}}", lines[0]))
    shell = ctx.constructs.get("inline_shell", []) + ctx.constructs.get("shell_fence", [])
    if shell:
        claude_only.append(("!`command`", min(shell)))
    for construct, line in claude_only:
        e.add("codex-body-explicit-injection-no-cap", "warning", f"{construct} is a Claude Code substitution; Codex injects it as literal text", "write skill-root-relative paths and avoid substitution placeholders, or document them as Claude-only", line=line)
    if "claude_dir" in ctx.constructs:
        e.add("codex-disc-no-claude-skills-dir", "warning", "body refers to .claude/ paths; Codex never scans .claude/skills (it uses .agents/skills)", "describe locations relative to the skill root", line=ctx.constructs["claude_dir"][0])
    if "claude_tools" in ctx.constructs:
        e.add("codex-body-explicit-injection-no-cap", "info", "body names Claude Code tools (Skill tool, AskUserQuestion, Bash(...) rules, ...); Codex has different tools", "phrase tool use generically", line=ctx.constructs["claude_tools"][0])
    for key, lines in ctx.constructs.items():
        if key.startswith("slash:") and key[6:] in ctx.catalog_names | {ctx.name}:
            e.add("codex-body-explicit-injection-no-cap", "info", f"body invokes /{key[6:]}; Codex has no slash invocation (mention it as ${key[6:]})", "mention skills as $name", line=lines[0])
            break


# --------------------------------------------------------------------------- #
# Profile: antigravity (Google Antigravity CLI agy 1.1.25)
# --------------------------------------------------------------------------- #

_rule("antigravity-workspace-root", "antigravity", "warning", "the body does not point at .claude/ paths (Antigravity scans only .agents/skills)")
_rule("antigravity-skill-file-name", "antigravity", "error/warning", "the skill file is SKILL.md (skill.md/Skill.md load but are not portable: warning; an uppercase .MD extension is not found: error)")
_rule("antigravity-symlinks-followed", "antigravity", "error", "a symlinked SKILL.md resolves (dangling links are dropped)")
_rule("antigravity-dot-dirs-discovered", "antigravity", "warning", "the skill directory name does not start with '.'")
_rule("antigravity-frontmatter-delimiters", "antigravity", "error/warning", "the opener is exactly '---' (optionally '--- # comment'), no '---' substring occurs inside the block, and the closer is exactly '---'")
_rule("antigravity-fm-indented-block-dropped", "antigravity", "error", "top-level keys start at column 0 (a uniformly indented block is trimmed and fails)")
_rule("antigravity-yaml-parser-go-yaml-v3", "antigravity", "error", "the block parses with go-yaml v3 semantics (any syntax error silently drops the skill)")
_rule("antigravity-yaml-duplicate-keys", "antigravity", "error", "no duplicate keys at any level")
_rule("antigravity-yaml-tabs", "antigravity", "error", "no tab used as indentation")
_rule("antigravity-yaml-type-errors", "antigravity", "error", "name/description are scalars, metadata is a mapping, disable-model-invocation / disable-slash-command are go-yaml booleans, the top level is a mapping")
_rule("antigravity-desc-plain-scalar-hazards", "antigravity", "error/warning", "an unquoted name/description has no ': ' and does not start with * @ ` % { [ '? ' '- ' or a block indicator (error); ' #', & and ! silently alter it (warning)")
_rule("antigravity-files-utf8-required", "antigravity", "error", "the file is UTF-8 without NUL bytes")
_rule("antigravity-unknown-keys-ignored", "antigravity", "warning/info", "keys other than name, description, disable-model-invocation, disable-slash-command and metadata have no effect")
_rule("antigravity-keys-case-sensitive", "antigravity", "error/warning", "keys are lowercase: Name/Description make the skill nameless 'SKILL' (error); disable_model_invocation is ignored (warning)")
_rule("antigravity-name-optional-defaults-to-file-stem", "antigravity", "error", "name is present and non-empty (a missing name becomes 'SKILL' and collides with every other nameless skill)")
_rule("antigravity-name-not-validated", "antigravity", "warning", "name follows ^[a-z0-9]+(-[a-z0-9]+)*$ (Antigravity accepts anything; the spec and slash usability do not)")
_rule("antigravity-name-whitespace-preserved", "antigravity", "warning", "name has no surrounding or internal whitespace (kept verbatim, so /name cannot be typed)")
_rule("antigravity-name-need-not-match-directory", "antigravity", "warning", "name equals the directory name (portability)")
_rule("antigravity-name-dedup", "antigravity", "error", "resolved names are unique across the catalog (nameless skills all resolve to 'SKILL')")
_rule("antigravity-slash-command", "antigravity", "warning", "name can be typed as one slash token")
_rule("antigravity-description-optional-degrades", "antigravity", "error", "description is present and non-empty (a missing one loads with no trigger text)")
_rule("antigravity-description-scalar-coercion", "antigravity", "warning", "description is a string (numbers/booleans keep their literal text)")
_rule("antigravity-description-no-length-limit", "antigravity", "warning", "description is at most 1024 characters (portability)")
_rule("antigravity-desc-literal-block-newlines", "antigravity", "warning", "the description has no internal newlines (they wrap the /skills row and roster line)")
_rule("antigravity-trigger-fields", "antigravity", "info", "description says what the skill does and when to use it (only name and description are trigger-matched)")
_rule("antigravity-disable-model-invocation", "antigravity", "error/info", "disable-model-invocation uses a go-yaml bool spelling (other values drop the skill); true hides the skill from the model")
_rule("antigravity-disable-slash-command", "antigravity", "error/warning", "disable-slash-command uses a go-yaml bool spelling; true hides the skill from /skills and /name")
_rule("antigravity-metadata-mapping", "antigravity", "error", "metadata is a mapping and metadata.icon/logo/publisher/version are scalars")
_rule("antigravity-hidden-key-not-for-skills", "antigravity", "warning", "no `hidden` key (it is a markdown-agent field with no effect on skills)")
_rule("antigravity-body-verbatim", "antigravity", "warning/info", "$ARGUMENTS/${CLAUDE_*}/inline shell in the body are injected verbatim")
_rule("antigravity-body-size-guidance", "antigravity", "warning", "SKILL.md has at most 500 lines")
_rule("antigravity-supporting-files", "antigravity", "warning", "relative file references from the body resolve inside the skill")


def _antigravity_bool_check(e: Emitter, key: str, rule_id: str, true_note: str, true_sev: str) -> None:
    ctx = e.ctx
    entry = ctx.top(key)
    if entry is None:
        return
    value = ctx.value(key)
    if isinstance(value, (list, dict)):
        # A block mapping/sequence leaves the raw entry "empty" (the value is on
        # the following lines), which is the go-yaml null form; the parsed value
        # is what go-yaml cannot unmarshal into a bool.
        e.add(rule_id, "error", f"{key} is a {_type_name(value)} ('cannot unmarshal'); the skill is silently dropped",
              "use `true` or `false`", line=entry.line)
        return
    if entry.style == "empty" and value is not None:
        e.add(rule_id, "error", f"{key} is a {_type_name(value)} ('cannot unmarshal'); the skill is silently dropped",
              "use `true` or `false`", line=entry.line)
        return
    if not _goyaml_bool_ok(entry):
        e.add(rule_id, "error", f"{key}: {_short(entry.raw)} is not a go-yaml boolean spelling (true/True/TRUE, false/False/FALSE, yes/no/on/off in three casings, quoted only for yes/no/on/off); the skill is silently dropped",
              "use `true` or `false`", line=entry.line)
        return
    raw = entry.raw.strip().strip("'\"") if entry.style in ("single", "double") else entry.plain_value.strip()
    if raw in ("true", "True", "TRUE", "y", "Y", "yes", "Yes", "YES", "on", "On", "ON"):
        e.add(rule_id, true_sev, f"{key}: {raw} {true_note}", "no action needed if intended", line=entry.line)


def profile_antigravity(ctx: SkillContext) -> list[Finding]:
    e = Emitter(ctx, "antigravity")
    dir_name = ctx.entry.dir.name
    if ctx.dangling_symlink:
        e.add("antigravity-symlinks-followed", "error", "SKILL.md is a dangling symlink; the skill is dropped ('failed to read file')", "fix the symlink")
        return e.findings
    if ctx.read_error:
        e.add("antigravity-files-utf8-required", "error", f"SKILL.md cannot be read ({ctx.read_error}); the skill is dropped", "make SKILL.md a readable regular file")
        return e.findings
    fname = ctx.entry.filename
    if fname != "SKILL.md":
        if not fname.endswith(".md"):
            e.add("antigravity-skill-file-name", "error", f"{fname}: the extension must be lowercase .md; the file is not found", "rename it to SKILL.md")
        else:
            e.add("antigravity-skill-file-name", "warning", f"{fname} loads in Antigravity (case-insensitive stem) but not in Claude Code, Codex or Cursor", "rename it to SKILL.md")
    if dir_name.startswith("."):
        e.add("antigravity-dot-dirs-discovered", "warning", f"hidden directory {dir_name!r} is loaded by Antigravity but skipped by this repo's tools and by Codex/Cursor", "use a visible name")
    if ctx.decode_error or ctx.has_nul:
        e.add("antigravity-files-utf8-required", "error", "SKILL.md is not valid UTF-8 or contains a NUL byte; the skill is dropped ('invalid trailing UTF-8 octet')", "re-save as UTF-8 without NUL bytes")
        return e.findings
    # delimiters (substring semantics)
    if ctx.opener is None:
        e.add("antigravity-frontmatter-delimiters", "error", "no '---' opener; 'invalid frontmatter format' and the skill is dropped", "start the file with `---`", line=1)
        _antigravity_body_checks(e)
        return e.findings
    opener_rest = ctx.opener[3:]
    if opener_rest.strip() and not opener_rest.lstrip().startswith("#"):
        if re.match(r"^[A-Za-z_-][^:]*:", opener_rest):
            e.add("antigravity-frontmatter-delimiters", "warning", f"opener {_short(ctx.opener)!r} runs the first key into the delimiter line; Antigravity parses it but nothing else does", "put `---` alone on line 1", line=1)
        else:
            e.add("antigravity-frontmatter-delimiters", "error", f"opener {_short(ctx.opener)!r} is fed to the YAML parser and drops the skill", "put `---` alone on line 1", line=1)
    if not ctx.fm_present:
        e.add("antigravity-frontmatter-delimiters", "error", "fewer than two '---' delimiters ('invalid frontmatter format'); the skill is dropped", "close the frontmatter with `---`", line=1)
        _antigravity_body_checks(e)
        return e.findings
    if ctx.fm_inner_dash_lines:
        e.add("antigravity-frontmatter-delimiters", "error", f"'---' occurs inside the frontmatter (line {ctx.fm_inner_dash_lines[0]}); Antigravity splits on the substring, truncating the value and losing the later keys",
              "remove '---' from the value", line=ctx.fm_inner_dash_lines[0])
    if ctx.fm_close_line_raw.rstrip() != "---":
        e.add("antigravity-frontmatter-delimiters", "warning", f"closing line {_short(ctx.fm_close_line_raw)!r} is not a bare '---'; the remainder of that line starts the body", "make the closing line exactly `---`", line=(ctx.fm_close_index or 0) + 1)
    first_content = next((l for l in ctx.fm_lines if l.strip() and not l.strip().startswith("#")), None)
    if first_content is not None and first_content[0] in " \t":
        e.add("antigravity-fm-indented-block-dropped", "error", "the frontmatter block is indented; Antigravity trims it before decoding and the skill is dropped", "start every top-level key at column 0", line=2)
    for line, kind in _tab_positions(ctx):
        if kind == "indent":
            e.add("antigravity-yaml-tabs", "error", "tab used as indentation ('found a tab character that violates indentation'); the skill is dropped", "indent with spaces", line=line)
    for key, line, first in ctx.dup_keys:
        e.add("antigravity-yaml-duplicate-keys", "error", f"duplicate key {key!r} ('mapping key already defined'); the skill is dropped", "keep one occurrence", line=line)
    for entry in ctx.entries:
        if entry.style != "plain":
            continue
        h = _hazards(entry)
        key = entry.top_key or "?"
        undefined_alias = h.lead == "*" and ctx.parse_error is not None
        if key not in ("name", "description"):
            if h.lead in ("%", "@", "`", "{", "[") or undefined_alias or h.colon_space:
                e.add("antigravity-yaml-parser-go-yaml-v3", "error", f"unquoted value of {'.'.join(str(p) for p in entry.path)} {'starts with ' + repr(h.lead) if h.lead else 'contains a colon-space'}; go-yaml rejects it and the skill is dropped",
                      "quote the value", line=entry.line)
            continue
        if h.colon_space or h.trailing_colon:
            e.add("antigravity-desc-plain-scalar-hazards", "error", f"unquoted {key} contains ': ' or ends with ':' ('mapping values are not allowed in this context'); no repair pass exists and the skill is dropped", "quote the value or use `>-`", line=entry.line)
        if h.lead in ("@", "`", "%", "{", "[", "?", "-", "|", ">", ",", "]", "}", ":") or undefined_alias:
            e.add("antigravity-desc-plain-scalar-hazards", "error", f"unquoted {key} starts with '{h.lead}' ({h.lead_kind}); the skill is dropped", "quote the value", line=entry.line)
        elif h.lead in ("&", "!"):
            e.add("antigravity-desc-plain-scalar-hazards", "warning", f"unquoted {key} starts with '{h.lead}'; the token is silently consumed as an {'anchor' if h.lead == '&' else 'tag'}", "quote the value", line=entry.line)
        if h.space_hash:
            e.add("antigravity-desc-plain-scalar-hazards", "warning", f"unquoted {key} contains ' #'; the rest is a comment ({_short(entry.plain_value)!r})", "quote the value", line=entry.line)
    for entry in ctx.entries:
        if entry.style in ("single", "double") and (not entry.quote_closed or entry.inner_quote_error):
            e.add("antigravity-yaml-parser-go-yaml-v3", "error", f"malformed quoted value for {entry.top_key}; the skill is dropped", "fix the quotes", line=entry.line)
    data = ctx.parsed
    if ctx.parse_error is not None:
        # PyYAML rejects a tab anywhere in a plain scalar; go-yaml only rejects
        # tabs used as indentation (antigravity-yaml-tabs, already reported
        # above), so re-read a tab-normalised copy before calling it a syntax
        # error the harness would hit.
        retry: object = None
        if _tab_scan_error(ctx.parse_error) and not any(k == "indent" for _l, k in _tab_positions(ctx)):
            ok, value = _safe_load(ctx.fm_text.replace("\t", " "))
            retry = value if ok else None
        if retry is None:
            e.add("antigravity-yaml-parser-go-yaml-v3", "error", f"YAML syntax error ({ctx.parse_error}); the skill silently disappears from the roster (logged only in the CLI log)", "fix the YAML", line=ctx.parse_error_line)
            _antigravity_body_checks(e)
            return e.findings
        data = retry
    if data is None:
        e.add("antigravity-name-optional-defaults-to-file-stem", "error", "empty (or comment-only) frontmatter: the skill loads as nameless 'SKILL' with no description", "add name and description", line=2)
        _antigravity_body_checks(e)
        return e.findings
    if not isinstance(data, dict):
        e.add("antigravity-yaml-type-errors", "error", f"frontmatter is a {_type_name(data)}, not a mapping ('cannot unmarshal'); the skill is dropped", "write `key: value` lines", line=2)
        _antigravity_body_checks(e)
        return e.findings
    keys = [str(k) for k in data.keys()]
    for key in keys:
        if key in ANTIGRAVITY_KEYS:
            continue
        cand = _near_miss(key, ANTIGRAVITY_KEYS)
        if cand in ("name", "description"):
            e.add("antigravity-keys-case-sensitive", "error", f"key {key!r} is not {cand!r}; the skill loads as nameless 'SKILL' / without description", f"rename it to {cand}", line=e.line(key))
        elif cand:
            e.add("antigravity-keys-case-sensitive", "warning", f"key {key!r} is ignored (Antigravity reads {cand!r}); the skill stays model-visible", f"rename it to {cand}", line=e.line(key))
    # name
    name = data.get("name")
    if isinstance(name, (list, dict)):
        e.add("antigravity-yaml-type-errors", "error", f"name is a {_type_name(name)} ('cannot unmarshal'); the skill is dropped", "write a string", line=e.line("name"))
    elif name is None or (isinstance(name, str) and not name.strip()):
        e.add("antigravity-name-optional-defaults-to-file-stem", "error", "name is missing or empty; the skill is named 'SKILL' (not the folder name) and collides with every other nameless skill", f"add `name: {dir_name}`", line=e.line("name") or 2)
    else:
        text = name if isinstance(name, str) else str(name)
        raw = ctx.top("name")
        if raw is not None and raw.style == "plain" and not isinstance(name, str):
            text = raw.plain_value.strip()
        if text != text.strip() or re.search(r"\s", text):
            e.add("antigravity-name-whitespace-preserved", "warning", f"name {_short(text)!r} contains whitespace and is kept verbatim, so /name cannot be typed", "use a single hyphenated token", line=e.line("name"))
        elif not re.fullmatch(r"[A-Za-z0-9_.:/-]+", text):
            e.add("antigravity-slash-command", "warning", f"name {_short(text)!r} contains characters that cannot be typed as one slash token", "use letters, digits and hyphens", line=e.line("name"))
        if not SPEC_NAME_PORTABLE_RE.match(text):
            e.add("antigravity-name-not-validated", "warning", f"name {_short(text)!r} loads verbatim but is not ^[a-z0-9]+(-[a-z0-9]+)*$", "use lowercase letters, digits and hyphens", line=e.line("name"))
        if text != dir_name:
            e.add("antigravity-name-need-not-match-directory", "warning", f"name {_short(text)!r} differs from the directory {dir_name!r} (fine for Antigravity, not for the spec)", "make them identical", line=e.line("name"))
    # description
    desc = data.get("description")
    raw_desc = ctx.top("description")
    if isinstance(desc, (list, dict)):
        e.add("antigravity-yaml-type-errors", "error", f"description is a {_type_name(desc)} ('cannot unmarshal'); the skill is dropped", "write a string", line=e.line("description"))
    elif desc is None or (isinstance(desc, str) and not desc.strip()) or (raw_desc is not None and raw_desc.style == "plain" and raw_desc.raw.startswith("#")):
        e.add("antigravity-description-optional-degrades", "error", "description is missing or empty; the skill loads with nothing for the model to trigger on", "add a description", line=e.line("description") or 2)
    else:
        text = desc if isinstance(desc, str) else str(desc)
        if not isinstance(desc, str):
            # go-yaml keeps the scalar exactly as written (007 stays '007',
            # 0.10 stays '0.10', yes stays 'yes'), unlike str(parsed value).
            if raw_desc is not None and raw_desc.style == "plain":
                text = raw_desc.plain_value.strip()
            e.add("antigravity-description-scalar-coercion", "warning", f"description is a {_type_name(desc)}; its literal text {_short(text)!r} is used", "quote it", line=e.line("description"))
        if len(text) > 1024:
            e.add("antigravity-description-no-length-limit", "warning", f"description is {len(text)} characters (no Antigravity limit, but 1024 elsewhere)", "shorten it", line=e.line("description"))
        if "\n" in text.strip():
            e.add("antigravity-desc-literal-block-newlines", "warning", "description contains line breaks; they wrap the /skills row and the model roster line", "use `>-` (folded) or a single line", line=e.line("description"))
        if len(text.strip()) < 40 or not _has_when_cue(text):
            e.add("antigravity-trigger-fields", "info", "only name and description are trigger-matched; say what the skill does and when to use it", "add a 'Use when ...' cue", line=e.line("description"))
    # booleans
    _antigravity_bool_check(e, "disable-model-invocation", "antigravity-disable-model-invocation", "hides the skill from the model roster (/name still works)", "info")
    _antigravity_bool_check(e, "disable-slash-command", "antigravity-disable-slash-command", "hides the skill from /skills and /name (CLI >= 1.1.12; the IDE ignores the key)", "warning")
    # metadata
    if "metadata" in data and data["metadata"] is not None:
        meta = data["metadata"]
        if not isinstance(meta, dict):
            e.add("antigravity-metadata-mapping", "error", f"metadata is a {_type_name(meta)}; go-yaml cannot decode it and the skill is dropped", "write a mapping", line=e.line("metadata"))
        else:
            for key in ("icon", "logo", "publisher", "version"):
                if key in meta and isinstance(meta[key], (list, dict)):
                    e.add("antigravity-metadata-mapping", "error", f"metadata.{key} is a {_type_name(meta[key])}; the typed field must be a scalar and the skill is dropped", "write a scalar", line=e.line("metadata"))
    if "hidden" in data:
        e.add("antigravity-hidden-key-not-for-skills", "warning", "`hidden` is a markdown-agent field with no effect on skills", "use disable-model-invocation instead", line=e.line("hidden"))
    _ignored_key_findings(e, ANTIGRAVITY_KEYS | {"hidden"}, "antigravity-unknown-keys-ignored", None, "Antigravity", {
        "user-invocable": "the skill stays user-invocable", "allowed-tools": "no tool permissions are granted", "paths": "the skill is never scoped to files",
        "context": "no forked subagent", "hooks": "no hooks are registered",
    }, skip=[k for k in keys if _near_miss(k, ANTIGRAVITY_KEYS)])
    _antigravity_body_checks(e)
    return e.findings


def _antigravity_body_checks(e: Emitter) -> None:
    ctx = e.ctx
    if ctx.line_count > 500:
        e.add("antigravity-body-size-guidance", "warning", f"SKILL.md has {ctx.line_count} lines ('Keep under 500 lines')", "move detail into references/", line=501)
    for ref in _missing_refs(ctx):
        e.add("antigravity-supporting-files", "warning", f"referenced file {ref.text} does not exist in the skill directory", "fix the path or add the file", line=ref.line)
    claude_only = []
    if "arguments" in ctx.constructs:
        claude_only.append(("$ARGUMENTS/$N", ctx.constructs["arguments"][0]))
    if ctx.substitutions:
        name, lines = next(iter(ctx.substitutions.items()))
        claude_only.append((f"${{{name}}}", lines[0]))
    shell = ctx.constructs.get("inline_shell", []) + ctx.constructs.get("shell_fence", [])
    if shell:
        claude_only.append(("!`command`", min(shell)))
    for construct, line in claude_only:
        e.add("antigravity-body-verbatim", "warning", f"{construct} is a Claude Code substitution; Antigravity injects the body verbatim", "write skill-root-relative paths and avoid substitution placeholders, or document them as Claude-only", line=line)
    if "claude_dir" in ctx.constructs:
        e.add("antigravity-workspace-root", "warning", "body refers to .claude/ paths; Antigravity scans only .agents/skills (and .agent/_agents/_agent)", "describe locations relative to the skill root", line=ctx.constructs["claude_dir"][0])
    if "claude_tools" in ctx.constructs:
        e.add("antigravity-body-verbatim", "info", "body names Claude Code tools; Antigravity's tools differ (view_file, run_command, ...)", "phrase tool use generically", line=ctx.constructs["claude_tools"][0])


# --------------------------------------------------------------------------- #
# Profile: cursor (Cursor 3.18.25 IDE agent)
# --------------------------------------------------------------------------- #

_rule("cursor-discovery-filename-case", "cursor", "error", "the skill file is named exactly SKILL.md")
_rule("cursor-discovery-walk", "cursor", "error/warning", "the directory name is not hidden or node_modules/__pycache__/dist/build (error); no second SKILL.md below the skill (warning; see cursor-files-optional-dirs)")
_rule("cursor-discovery-hidden-and-codex-system-prune", "cursor", "warning", "the directory name is not one of Codex's system skills (pruned when installed under .codex/skills)")
_rule("cursor-discovery-symlinks", "cursor", "error/warning", "a symlinked SKILL.md resolves (error); two catalog entries resolving to the same file load once (warning)")
_rule("cursor-semantics-third-party-dirs-default-on", "cursor", "warning", "the body does not depend on .claude/ paths (loaded only while the third-party toggle is on)")
_rule("cursor-frontmatter-parser", "cursor", "error", "the file starts with '---' plus newline or a yaml tag and the block ends at a '\\n---' line")
_rule("cursor-frontmatter-no-leading-whitespace", "cursor", "error", "nothing precedes the opening '---' (else the skill has no description)")
_rule("cursor-frontmatter-four-dashes-not-frontmatter", "cursor", "error/warning", "the opener is exactly '---' (error) and the closer is a bare '---' at column 0 (indented: error; trailing text: warning)")
_rule("cursor-frontmatter-missing-closing", "cursor", "error", "a closing '\\n---' exists")
_rule("cursor-frontmatter-first-closing-anywhere", "cursor", "error", "no line starting with '---' or equal to '...' inside the block and no NUL byte")
_rule("cursor-frontmatter-cr-only", "cursor", "error", "line endings are LF or CRLF")
_rule("cursor-frontmatter-language-tag", "cursor", "error", "text after the opening '---' is at most a yaml/yml language tag")
_rule("cursor-frontmatter-duplicate-keys", "cursor", "error", "no duplicate keys ('duplicated mapping key' leaves a path-only entry)")
_rule("cursor-frontmatter-yaml-exception-effect", "cursor", "error", "js-yaml parses the block (an exception leaves an undescribed path-only entry)")
_rule("cursor-frontmatter-must-be-mapping", "cursor", "error", "the frontmatter is a non-empty mapping with a space after each key colon")
_rule("cursor-frontmatter-tabs", "cursor", "error/warning", "no tab indentation (mis-nesting or exception: error); other tabs are noted (warning)")
_rule("cursor-yaml-boolean-semantics", "cursor", "warning", "disable-model-invocation / alwaysApply use bare true/false (yes/on/1/\"true\" are not booleans for js-yaml 3)")
_rule("cursor-keys-exact-spelling", "cursor", "error/warning", "keys use the exact spelling: Description is ignored (error), disable_model_invocation variants are ignored (warning)")
_rule("cursor-description-required-string", "cursor", "error", "description parses as a non-empty string ('Description is required' otherwise)")
_rule("cursor-description-truncated-1536", "cursor", "warning", "description is at most 1536 UTF-16 code units")
_rule("cursor-description-prompt-budget", "cursor", "warning/info", "descriptions over 480 characters are cut first under budget pressure (info); the catalog fits ~16,000 characters (warning)")
_rule("cursor-description-yaml-hazards", "cursor", "error/warning", "an unquoted description has no ': ', trailing ':' or hazardous leading character (error); ' #' and & silently alter it (warning)")
_rule("cursor-name-ignored-by-loader", "cursor", "warning", "name equals the parent folder (the loader ignores name; the IDE shows both when they differ; see cursor-semantics-slash-menu-dir-filter)")
_rule("cursor-key-disable-model-invocation", "cursor", "info", "disable-model-invocation: true hides the skill from the model entirely")
_rule("cursor-key-paths-globs", "cursor", "warning/info", "paths/globs is a string or list of non-empty strings; the skill is absent from the initial list")
_rule("cursor-key-paths-matching", "cursor", "warning", "paths patterns are POSIX-style, relative, without a leading ./")
_rule("cursor-key-alwaysApply-turns-skill-into-rule", "cursor", "warning", "no `alwaysApply: true` (turns the file into an always-applied rule)")
_rule("cursor-key-environments", "cursor", "error/warning", "environments / disabled-environments values are local or cloud (error otherwise); environments without local hides the skill in the IDE")
_rule("cursor-key-metadata-surfaces-scopedTo", "cursor", "error/warning/info", "metadata.surfaces values are ide/cli (error otherwise); omitting ide hides the skill in the IDE (warning); scopedTo restricts users (info)")
_rule("cursor-key-icon-color", "cursor", "warning", "color is one of the documented badge colours")
_rule("cursor-keys-unknown-ignored", "cursor", "warning/info", "keys outside the loader's read set have no effect (behavioural keys: warning)")
_rule("cursor-body-model-visible-form", "cursor", "warning/info", "the body is non-empty; the description contains no XML-looking text; Claude-only constructs are injected verbatim")
_rule("cursor-body-size", "cursor", "warning", "SKILL.md is under 100,000 characters (manual attach is cut there)")


def _cursor_list_or_string(value: object) -> list[str] | None:
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    if isinstance(value, list):
        return [p.strip() for p in value if isinstance(p, str) and p.strip()]
    return None


def profile_cursor(ctx: SkillContext) -> list[Finding]:
    e = Emitter(ctx, "cursor")
    dir_name = ctx.entry.dir.name
    if ctx.dangling_symlink:
        e.add("cursor-discovery-symlinks", "error", "SKILL.md is a dangling symlink and is skipped silently", "fix the symlink")
        return e.findings
    if ctx.entry.filename != "SKILL.md":
        e.add("cursor-discovery-filename-case", "error", f"skill file is named {ctx.entry.filename}; Cursor compares the entry name with 'SKILL.md' byte-for-byte", "rename it to SKILL.md")
    if dir_name.startswith(".") or dir_name in CURSOR_EXCLUDED_DIRS:
        e.add("cursor-discovery-walk", "error", f"directory {dir_name!r} is skipped by the walk (hidden or one of node_modules/__pycache__/dist/build)", "rename the directory")
    if dir_name in CURSOR_CODEX_SYSTEM_SKILLS:
        e.add("cursor-discovery-hidden-and-codex-system-prune", "warning", f"{dir_name!r} is a Codex system-skill name and is pruned when installed under .codex/skills", "rename the directory or install under .agents/skills")
    visible_nested = [p for p, hidden in ctx.nested_skill_files if not hidden]
    if visible_nested:
        e.add("cursor-discovery-walk", "warning", f"additional SKILL.md below the skill ({visible_nested[0]}); Cursor registers it as a separate skill named after its folder (cursor-files-optional-dirs)",
              "rename or move the nested file", file=_display_path(ctx.entry.dir / visible_nested[0]))
    if ctx.read_error:
        e.add("cursor-frontmatter-parser", "error", f"SKILL.md cannot be read ({ctx.read_error}); it becomes a path-only entry", "make SKILL.md a readable regular file")
        return e.findings
    if ctx.has_nul:
        e.add("cursor-frontmatter-first-closing-anywhere", "error", "NUL byte in the file ('null byte is not allowed in input'); path-only entry", "remove the NUL byte", line=1)
    if ctx.has_cr_only:
        e.add("cursor-frontmatter-cr-only", "error", "CR-only line endings; gray-matter reads everything up to the first LF as a language tag and throws", "convert to LF line endings", line=1)
    if ctx.opener is None:
        e.add("cursor-frontmatter-no-leading-whitespace", "error", "the file does not start with '---'; gray-matter finds no frontmatter and the skill loads with 'Description is required'", "start the file with `---`", line=1)
        _cursor_body_checks(e)
        return e.findings
    rest = ctx.opener[3:]
    if rest.startswith("-"):
        e.add("cursor-frontmatter-four-dashes-not-frontmatter", "error", f"opener {_short(ctx.opener)!r} (four or more dashes) is not treated as frontmatter", "use exactly `---`", line=1)
        _cursor_body_checks(e)
        return e.findings
    tag = rest.strip().lower()
    if tag and tag not in ("yaml", "yml"):
        what = "a neutered js engine (no data)" if tag in ("js", "javascript") else "an unregistered gray-matter engine (exception)"
        e.add("cursor-frontmatter-language-tag", "error", f"text after the opening '---' ({rest.strip()!r}) selects {what}; the skill has no description", "put `---` alone on line 1", line=1)
    if not ctx.fm_present:
        e.add("cursor-frontmatter-missing-closing", "error", "no '\\n---' closing line; the whole remainder is parsed as YAML (usually an exception, or an empty body)", "close the frontmatter with `---`", line=1)
        _cursor_body_checks(e)
        return e.findings
    if ctx.fm_first_dash_line is not None:
        e.add("cursor-frontmatter-first-closing-anywhere", "error", f"line {ctx.fm_first_dash_line} starts with '---' inside the frontmatter; Cursor ends the block at the first '\\n---' and the rest leaks into the body", "remove the '---' line", line=ctx.fm_first_dash_line)
    for line in ctx.fm_doc_end_lines:
        e.add("cursor-frontmatter-first-closing-anywhere", "error", "'...' document-end marker inside the frontmatter ('expected a single document in the stream'); path-only entry", "remove the line", line=line)
    closer_raw = ctx.fm_close_line_raw
    if closer_raw.rstrip() != "---":
        if closer_raw.startswith("---"):
            e.add("cursor-frontmatter-four-dashes-not-frontmatter", "warning", f"closing line {_short(closer_raw)!r} closes the block but its remainder leaks into the body", "make the closing line exactly `---`", line=(ctx.fm_close_index or 0) + 1)
        else:
            e.add("cursor-frontmatter-four-dashes-not-frontmatter", "error", f"closing line {_short(closer_raw)!r} is indented; gray-matter needs '---' at column 0 (YAML exception)", "put `---` at column 0", line=(ctx.fm_close_index or 0) + 1)
    tabs = _tab_positions(ctx)
    for line, kind in tabs:
        if kind == "indent":
            e.add("cursor-frontmatter-tabs", "error", "tab indentation: js-yaml 3 mis-nests the mapping (metadata becomes null) or throws", "indent with spaces", line=line)
        else:
            e.add("cursor-frontmatter-tabs", "warning", f"tab inside a {kind}; js-yaml 3 tab handling is inconsistent", "replace the tab with spaces", line=line)
    for key, line, first in ctx.dup_keys:
        e.add("cursor-frontmatter-duplicate-keys", "error", f"duplicate key {key!r} ('duplicated mapping key'); the skill becomes a path-only entry with no description", "keep one occurrence", line=line)
    raw_desc = ctx.top("description")
    if raw_desc is not None:
        h = _hazards(raw_desc)
        if raw_desc.style == "plain":
            if h.colon_space or h.trailing_colon:
                e.add("cursor-description-yaml-hazards", "error", "unquoted description contains ': ' or ends with ':'; js-yaml throws and the skill becomes a path-only entry", "quote the value or use `>-`", line=raw_desc.line)
            if h.lead == "?":
                e.add("cursor-description-yaml-hazards", "error", "unquoted description starts with '? ' and parses as an explicit key (description null)", "quote the value", line=raw_desc.line)
            elif h.lead == "&":
                e.add("cursor-description-yaml-hazards", "warning", "unquoted description starts with '&'; the first word is consumed as an anchor", "quote the value", line=raw_desc.line)
            elif h.lead == "*" and ctx.parse_error is None:
                pass  # a defined alias resolves in js-yaml
            elif h.lead is not None:
                e.add("cursor-description-yaml-hazards", "error", f"unquoted description starts with '{h.lead}' ({h.lead_kind}); js-yaml throws and the skill becomes a path-only entry", "quote the value", line=raw_desc.line)
            if h.space_hash:
                e.add("cursor-description-yaml-hazards", "warning", f"unquoted description contains ' #'; it silently loads as {_short(raw_desc.plain_value)!r}", "quote the value", line=raw_desc.line)
        elif raw_desc.style in ("single", "double") and (h.unterminated_quote or h.quote_then_text):
            e.add("cursor-description-yaml-hazards", "error", "malformed quoted description (unterminated quote or text after the closing quote); js-yaml throws", "escape inner quotes ('' or \\\")", line=raw_desc.line)
    if ctx.parse_error is None:
        # With a parse error the generic emit below carries the same rule id and
        # a more precise message, so only report the tag when nothing else did.
        for tag, line in ctx.tags:
            if tag.startswith("!") and not tag.startswith("!!"):
                e.add("cursor-frontmatter-yaml-exception-effect", "error", f"unknown local tag {tag} ('unknown tag'); path-only entry", "remove the tag", line=line)
    if ctx.parse_error is not None:
        # Two PyYAML errors are not js-yaml exceptions: tabs js-yaml tolerates
        # (cursor-frontmatter-tabs already reports them) and a second document,
        # which cannot happen because Cursor closed the block at the first
        # '\n---' (cursor-frontmatter-first-closing-anywhere reports that).
        tolerated = ctx.fm_first_dash_line is not None or (
            _tab_scan_error(ctx.parse_error) and not _jsyaml_tab_throws(ctx)
        )
        if not tolerated:
            e.add("cursor-frontmatter-yaml-exception-effect", "error", f"js-yaml would throw ({ctx.parse_error}); the skill becomes an undescribed path-only entry that /name cannot attach", "fix the YAML", line=ctx.parse_error_line)
        _cursor_body_checks(e)
        return e.findings
    data = ctx.parsed
    if not isinstance(data, dict) or not data:
        e.add("cursor-frontmatter-must-be-mapping", "error", f"frontmatter is {'empty' if data is None else 'a ' + _type_name(data)}, not a mapping; the skill loads with 'Description is required'", "write `key: value` lines (with a space after the colon)", line=2)
        _cursor_body_checks(e)
        return e.findings
    keys = [str(k) for k in data.keys()]
    for key in keys:
        if key in CURSOR_KEYS:
            continue
        cand = _near_miss(key, CURSOR_KEYS)
        if cand == "description":
            e.add("cursor-keys-exact-spelling", "error", f"key {key!r} is not 'description'; the skill loads with 'Description is required'", "rename it to description", line=e.line(key))
        elif cand == "disable-model-invocation":
            e.add("cursor-keys-exact-spelling", "warning", f"key {key!r} is ignored; only the exact top-level disable-model-invocation is honoured (the skill stays model-visible)", "rename it to disable-model-invocation", line=e.line(key))
    # description
    desc = data.get("description")
    if raw_desc is not None and raw_desc.style == "plain":
        kind = _jsyaml_kind(raw_desc.plain_value.strip())
    else:
        kind = "string" if isinstance(desc, str) else _type_name(desc)
    if "description" not in data or desc is None or (isinstance(desc, str) and not desc.strip()) or isinstance(desc, (list, dict)) or kind != "string":
        e.add("cursor-description-required-string", "error", f"description {'is missing' if 'description' not in data else 'is a ' + kind + ' for js-yaml'}; the skill loads with 'Description is required' and no description", "write a non-empty quoted string", line=e.line("description") or 2)
    else:
        text = desc if isinstance(desc, str) else str(desc)
        units = _utf16_units(text)
        if units > CURSOR_DESC_CAP:
            e.add("cursor-description-truncated-1536", "warning", f"description is {units} UTF-16 units; Cursor cuts it at {CURSOR_DESC_CAP} without an ellipsis", "shorten the description", line=e.line("description"))
        elif len(text) > 480:
            e.add("cursor-description-prompt-budget", "info", f"description is {len(text)} characters; under budget pressure Cursor shortens descriptions to at most 480", "front-load the key use cases", line=e.line("description"))
        if "</" in text or "<agent_skill" in text:
            e.add("cursor-body-model-visible-form", "warning", "description contains XML-looking text; it is rendered unescaped inside <agent_skill>", "rephrase without tags", line=e.line("description"))
    # booleans
    for key in ("disable-model-invocation", "alwaysApply"):
        raw = ctx.top(key)
        if raw is None:
            continue
        token = raw.plain_value.strip() if raw.style == "plain" else None
        if token in JSYAML_TRUE:
            if key == "disable-model-invocation":
                e.add("cursor-key-disable-model-invocation", "info", "disable-model-invocation: true removes the skill from <available_skills> and paths auto-surfacing; /name still works", "no action needed if intended", line=raw.line)
            else:
                e.add("cursor-key-alwaysApply-turns-skill-into-rule", "warning", "alwaysApply: true turns SKILL.md into an always-applied rule (injected every turn, absent from the skills list)", "remove alwaysApply unless intended", line=raw.line)
        elif token not in JSYAML_FALSE:
            shown = raw.raw if raw.raw else "<empty>"
            e.add("cursor-yaml-boolean-semantics", "warning", f"{key}: {_short(shown)} is not a js-yaml boolean (only bare true/false in three casings); the flag is silently not honoured", "write `true` or `false` unquoted", line=raw.line)
    # paths / globs
    for key in ("paths", "globs"):
        if key not in data:
            continue
        if key == "globs" and data.get("paths") is not None:
            e.add("cursor-keys-unknown-ignored", "info", "globs is ignored because paths is set", "drop the legacy globs key", line=e.line("globs"))
            continue
        if key == "paths" and data.get("paths") is None:
            continue  # a null paths behaves as absent and leaves the globs fallback active
        value = data[key]
        patterns = _cursor_list_or_string(value)
        if patterns is None:
            e.add("cursor-key-paths-globs", "warning", f"{key} is a {_type_name(value)}; no globs are read", "use a comma-separated string or a list", line=e.line(key))
        elif not patterns:
            e.add("cursor-key-paths-globs", "warning", f"{key} is empty (and an empty paths suppresses the globs fallback)", "remove the key or add patterns", line=e.line(key))
        else:
            e.add("cursor-key-paths-globs", "info", f"{key} is set; the skill is absent from the initial list until a matching file is read or edited", "no action needed if intended", line=e.line(key))
            for pattern in patterns:
                if "\\" in pattern or pattern.startswith("./") or pattern.startswith("/"):
                    e.add("cursor-key-paths-matching", "warning", f"pattern {_short(pattern)!r} should be POSIX-style, relative to the repository root, without a leading ./", "rewrite the glob", line=e.line(key))
                    break
    # environments
    def check_environments(key: str, label: str, values: list[str], line: int | None) -> None:
        bad = [v for v in values if v not in CURSOR_ENVIRONMENTS]
        disabled = key.lower().startswith("disabled")
        if bad:
            e.add("cursor-key-environments", "error", f"{label} contains {bad}; values are matched exactly against local/cloud, so the skill is "
                  + ("never disabled where it was meant to be" if disabled else "hidden on every surface"), "use local and/or cloud", line=line)
        elif disabled and CURSOR_ENVIRONMENTS.issubset(set(values)):
            e.add("cursor-key-environments", "error", f"{label} disables both local and cloud, so the skill loads on no surface at all", "drop one environment or remove the key", line=line)
        elif disabled and "local" in values:
            e.add("cursor-key-environments", "warning", f"{label} includes local, so the skill is hidden in the IDE and CLI", "remove local or remove the key", line=line)
        elif not disabled and values and "local" not in values:
            e.add("cursor-key-environments", "warning", f"{label} does not include local, so the skill is hidden in the IDE and CLI", "add local or remove the key", line=line)

    for key in ("environments", "disabled-environments"):
        if key in data:
            check_environments(key, key, _cursor_list_or_string(data[key]) or [], e.line(key))
    meta = data.get("metadata")
    if isinstance(meta, dict):
        for key in ("environments", "disabledEnvironments"):
            if key in meta:
                check_environments(key, f"metadata.{key}", _cursor_list_or_string(meta[key]) or [], e.line("metadata"))
        if "surfaces" in meta:
            values = _cursor_list_or_string(meta["surfaces"]) or []
            bad = [v for v in values if v not in CURSOR_SURFACES]
            if bad:
                e.add("cursor-key-metadata-surfaces-scopedTo", "error", f"metadata.surfaces contains {bad}; the skill is dropped on every surface not listed exactly", "use ide and/or cli", line=e.line("metadata"))
            elif values and "ide" not in values:
                e.add("cursor-key-metadata-surfaces-scopedTo", "warning", "metadata.surfaces omits ide, so the skill is dropped in the IDE", "add ide or remove the key", line=e.line("metadata"))
        if "scopedTo" in meta:
            e.add("cursor-key-metadata-surfaces-scopedTo", "info", "metadata.scopedTo restricts the skill to the listed user emails (dropped when no user context exists)", "no action needed if intended", line=e.line("metadata"))
    if "metadata.scopedTo" in data:
        e.add("cursor-key-metadata-surfaces-scopedTo", "info", "flat key metadata.scopedTo restricts the skill to the listed user emails", "no action needed if intended", line=e.line("metadata.scopedTo"))
    if "color" in data and str(data["color"]).strip() not in CURSOR_COLORS:
        e.add("cursor-key-icon-color", "warning", f"color {_short(data['color'])} is not one of {', '.join(sorted(CURSOR_COLORS))}; the badge falls back to default", "use a documented colour", line=e.line("color"))
    name = data.get("name")
    if isinstance(name, str) and name.strip() and name.strip() != dir_name:
        e.add("cursor-name-ignored-by-loader", "warning", f"name {name.strip()!r} is ignored by the loader; the skill is {dir_name!r} (folder name) and the IDE menu shows both strings", "make name equal to the folder name", line=e.line("name"))
    elif isinstance(name, str) and not re.fullmatch(r"[a-z0-9-]+", name.strip()):
        e.add("cursor-name-ignored-by-loader", "warning", f"name {_short(name)!r} is not lowercase letters, digits and hyphens (docs recommendation; the loader ignores name anyway)", "use a hyphen-case name", line=e.line("name"))
    _ignored_key_findings(e, CURSOR_KEYS | {"metadata.scopedTo"}, "cursor-keys-unknown-ignored", None, "Cursor", {
        "user-invocable": "the skill stays user-invocable", "allowed-tools": "no tool permissions are granted", "context": "no forked subagent",
        "hooks": "no hooks are registered", "model": "the model is not switched",
    }, skip=[k for k in keys if _near_miss(k, CURSOR_KEYS) in ("description", "disable-model-invocation")])
    _cursor_body_checks(e)
    return e.findings


def _cursor_body_checks(e: Emitter) -> None:
    ctx = e.ctx
    if ctx.fm_present and not ctx.body.strip():
        e.add("cursor-body-model-visible-form", "warning", "the body is empty; the agent reads the file after choosing the skill and finds nothing", "add the instructions", line=ctx.body_start_line)
    if len(ctx.text) > CURSOR_ATTACH_CAP:
        e.add("cursor-body-size", "warning", f"SKILL.md is {len(ctx.text)} characters; manual /name attachment is cut at {CURSOR_ATTACH_CAP}", "shorten SKILL.md", line=1)
    claude_only = []
    if "arguments" in ctx.constructs:
        claude_only.append(("$ARGUMENTS/$N", ctx.constructs["arguments"][0]))
    if ctx.substitutions:
        name, lines = next(iter(ctx.substitutions.items()))
        claude_only.append((f"${{{name}}}", lines[0]))
    shell = ctx.constructs.get("inline_shell", []) + ctx.constructs.get("shell_fence", [])
    if shell:
        claude_only.append(("!`command`", min(shell)))
    for construct, line in claude_only:
        e.add("cursor-body-model-visible-form", "warning", f"{construct} is a Claude Code substitution; Cursor reads the file verbatim", "write skill-root-relative paths and avoid substitution placeholders, or document them as Claude-only", line=line)
    if "claude_dir" in ctx.constructs:
        e.add("cursor-semantics-third-party-dirs-default-on", "warning", "body refers to .claude/ paths; Cursor reads .claude/skills only while the third-party toggle is on", "prefer .agents/skills or .cursor/skills and skill-root-relative paths", line=ctx.constructs["claude_dir"][0])
    if "claude_tools" in ctx.constructs:
        e.add("cursor-body-model-visible-form", "info", "body names Claude Code tools; Cursor's tools differ (read tool, ...)", "phrase tool use generically", line=ctx.constructs["claude_tools"][0])


# --------------------------------------------------------------------------- #
# Catalog-level checks (computed once over every loaded skill)
# --------------------------------------------------------------------------- #


def _catalog_finding(profile: str, rule_id: str, severity: str, text: str, hint: str, *, ctx: SkillContext | None = None,
                     skill: str = "", file: str = "", line: int | None = None) -> Finding:
    info = RULES[rule_id]
    if info.profile != profile or severity not in info.severities:
        raise ValueError(f"bad catalog finding {rule_id}/{severity}")
    # An explicit skill/file wins over the context (e.g. a nested SKILL.md is
    # reported at its own path, not at the enclosing skill's SKILL.md).
    return Finding(profile, rule_id, severity, skill or (ctx.name if ctx else ""), file or (ctx.rel_file if ctx else ""),
                   line, f"{rule_id}: {text}", hint)


def _names_by(contexts: Sequence[SkillContext], key: Callable[[SkillContext], str | None]) -> dict[str, list[SkillContext]]:
    groups: dict[str, list[SkillContext]] = {}
    for ctx in contexts:
        value = key(ctx)
        if value:
            groups.setdefault(value, []).append(ctx)
    return groups


def _fm_name(ctx: SkillContext) -> str | None:
    name = ctx.value("name")
    return unicodedata.normalize("NFKC", name.strip()) if isinstance(name, str) and name.strip() else None


def _realpath_groups(contexts: Sequence[SkillContext]) -> list[list[SkillContext]]:
    groups: dict[Path, list[SkillContext]] = {}
    for ctx in contexts:
        try:
            groups.setdefault(ctx.entry.skill_md.resolve(), []).append(ctx)
        except OSError:
            continue
    return [sorted(g, key=lambda c: c.name) for g in groups.values() if len(g) > 1]


def _discovery_findings(discovery: Discovery, profiles: Sequence[str]) -> list[Finding]:
    """Per-profile findings for directories that never became a skill context.

    A case variant (``Skill.md``, ``SKILL.MD``) and a hidden skill directory are
    discovery facts, not properties of a loaded skill, so every selected profile
    reports them under its own rule id - otherwise a single-profile run exits 0
    with nothing printed at all.
    """

    out: list[Finding] = []
    for directory, variants in discovery.case_variants:
        found = ", ".join(variants)
        name, file = directory.name, _display_path(directory / variants[0])
        md = [v for v in variants if v.endswith(".md")]
        per_profile: list[tuple[str, str, str, str]] = [
            ("spec", "spec-discovery-case-insensitive-filesystem", "error",
             f"{name}/ contains {found} but no file named exactly SKILL.md; it validates on macOS and fails on Linux ('Missing required file: SKILL.md')"),
            ("claude-code", "claude-code-discovery-entry-layout", "error",
             f"{name}/ contains {found} but no file named exactly SKILL.md; Claude Code stats exactly SKILL.md, so the skill is skipped on Linux"),
            ("codex", "codex-disc-skill-filename-case-sensitive", "error",
             f"{name}/ contains {found} but no file named exactly SKILL.md; Codex compares the name byte-for-byte and never loads it"),
            ("antigravity", "antigravity-skill-file-name", "warning" if md else "error",
             (f"{name}/ contains {found}: Antigravity matches the stem case-insensitively and loads it, but Claude Code, Codex and Cursor do not"
              if md else f"{name}/ contains {found}: the extension must be lowercase .md, so Antigravity does not find the file either")),
            ("cursor", "cursor-discovery-filename-case", "error",
             f"{name}/ contains {found} but no file named exactly SKILL.md; Cursor compares the entry name with 'SKILL.md' byte-for-byte"),
        ]
        for profile, rule_id, severity, text in per_profile:
            if profile in profiles:
                out.append(_catalog_finding(profile, rule_id, severity, text, "rename the file to SKILL.md", skill=name, file=file))
    for directory in discovery.hidden_skills:
        name, file = directory.name, _display_path(directory / "SKILL.md")
        per_profile = [
            ("claude-code", "claude-code-discovery-dot-dirs", "warning",
             f"directory name {name!r} starts with '.'; Claude Code loads it (named with the dot) but this repo's catalog walk, unpack.sh and skill-search all skip it"),
            ("codex", "codex-disc-hidden-dirs-pruned", "error",
             f"directory {name!r} is hidden and is never descended by Codex"),
            ("antigravity", "antigravity-dot-dirs-discovered", "warning",
             f"hidden directory {name!r} is loaded by Antigravity and is model-visible, but is skipped by this repo's tools and by Codex/Cursor"),
            ("cursor", "cursor-discovery-walk", "error",
             f"directory {name!r} is hidden, so Cursor's walk skips it"),
        ]
        for profile, rule_id, severity, text in per_profile:
            if profile in profiles:
                out.append(_catalog_finding(profile, rule_id, severity, text, "use a visible directory name", skill=name, file=file))
    return out


def catalog_checks(contexts: Sequence[SkillContext], profiles: Sequence[str], *, full_catalog: bool = True,
                   discovery: Discovery | None = None) -> list[Finding]:
    out: list[Finding] = []
    by_dir = _names_by(contexts, lambda c: c.name)
    by_fm = _names_by(contexts, _fm_name)
    if "spec" in profiles:
        for name, group in by_dir.items():
            if len(group) > 1:
                for ctx in group:
                    others = ", ".join(_display_path(o.entry.dir) for o in group if o is not ctx)
                    out.append(_catalog_finding("spec", "spec-discovery-name-collisions", "error", f"directory name {name!r} is also used by {others}; only one loads per install root and unpack.sh refuses to flatten",
                                                "rename one of the skills", ctx=ctx))
        for name, group in by_fm.items():
            dirs = {c.name for c in group}
            if len(group) > 1 and len(dirs) > 1:
                for ctx in group:
                    others = ", ".join(_display_path(o.entry.dir) for o in group if o is not ctx)
                    out.append(_catalog_finding("spec", "spec-discovery-name-collisions", "error", f"frontmatter name {name!r} is also declared by {others}",
                                                "give each skill a unique name", ctx=ctx, line=ctx.key_line("name")))
        for ctx in contexts:
            for rel, hidden in ctx.nested_skill_files:
                if hidden:
                    continue
                loads = "Codex and Cursor load it as a separate skill" if 1 + rel.count("/") <= 6 else (
                    "Cursor loads it as a separate skill and Codex silently skips it (more than 6 levels below the skills root)")
                out.append(_catalog_finding("spec", "spec-discovery-skill-md-required", "warning", f"nested SKILL.md at {rel} is not a skill for skills-ref, Claude Code or Antigravity (they never recurse) but {loads}",
                                            "rename it (e.g. README.md) or move it to its own skill directory", ctx=ctx, file=_display_path(ctx.entry.dir / rel)))
            for variant in ctx.case_variant_files:
                out.append(_catalog_finding("spec", "spec-discovery-case-insensitive-filesystem", "error", f"{variant} sits next to {ctx.entry.filename}; on a case-insensitive filesystem the two collide",
                                            "keep exactly one file named SKILL.md", ctx=ctx, file=_display_path(ctx.entry.dir / variant)))
        if discovery is not None:
            for path, reason in discovery.orphans:
                if any(path == d for d, _ in discovery.case_variants):
                    continue
                out.append(_catalog_finding("spec", "spec-discovery-skill-md-required", "error", f"{_display_path(path)}: {reason} (skills-ref: 'Missing required file: SKILL.md')",
                                            "add a SKILL.md with frontmatter", skill=path.name, file=_display_path(path)))
    # Directories the walk found but never turned into a context: reported once
    # per selected profile, so a single-profile run cannot pass them silently.
    if discovery is not None:
        out.extend(_discovery_findings(discovery, profiles))
    if "claude-code" in profiles:
        for group in _realpath_groups(contexts):
            for ctx in group[1:]:
                out.append(_catalog_finding("claude-code", "claude-code-discovery-symlinks", "warning", f"resolves to the same file as {_display_path(group[0].entry.dir)}; Claude Code loads it once under the entry that sorts first ({group[0].name})",
                                            "keep one entry per target", ctx=ctx))
        for ctx in contexts:
            fm = _fm_name(ctx)
            if not fm or fm == ctx.name:
                continue
            clash = [c for c in by_dir.get(fm, []) if c is not ctx]
            clash += [c for c in by_fm.get(fm, []) if c is not ctx and c not in clash]
            if clash:
                out.append(_catalog_finding("claude-code", "claude-code-name-from-directory", "error", f"frontmatter name {fm!r} equals the name of {', '.join(_display_path(c.entry.dir) for c in clash)}; /{fm} and Skill({fm}) become ambiguous",
                                            "make name equal to this skill's own directory name", ctx=ctx, line=ctx.key_line("name")))
        if full_catalog:
            total = 0
            for ctx in contexts:
                if _claude_bool(ctx.value("disable-model-invocation")):
                    continue
                desc = _desc_text(ctx)
                wtu = ctx.value("when_to_use")
                combined = (desc.strip() if desc else "") + (f" - {wtu}" if wtu is not None else "")
                total += len(ctx.name) + (4 + min(len(combined), CLAUDE_LISTING_DESC_CAP) if combined else 2)
            if total > CLAUDE_LISTING_BUDGET:
                out.append(_catalog_finding("claude-code", "claude-code-description-listing-budget", "warning", f"installing every catalog skill puts the model listing at about {total} characters, over the {CLAUDE_LISTING_BUDGET}-character budget of a 200k context; Claude Code drops descriptions of the least-used skills (personal and plugin skills add to this)",
                                            "install only the skills a project needs, shorten descriptions, or raise skillListingBudgetFraction"))
    if "codex" in profiles:
        def codex_name(ctx: SkillContext) -> str | None:
            if ctx.parse_error is not None and not ctx.codex_repair_ok:
                return None
            data = ctx.codex_repair_parsed if ctx.parse_error is not None else ctx.parsed
            if not isinstance(data, dict):
                return None
            return _codex_effective_name(ctx, data)[0]
        for name, group in _names_by(contexts, codex_name).items():
            if len(group) > 1:
                for ctx in group:
                    others = ", ".join(_display_path(o.entry.dir) for o in group if o is not ctx)
                    out.append(_catalog_finding("codex", "codex-disc-dedupe-by-path-only", "warning", f"runtime name {name!r} is shared with {others}; both load and $" + name + " selects neither (core path) or the first (extension path)",
                                                "give each skill a unique name", ctx=ctx, line=ctx.key_line("name")))
        if full_catalog:
            total = 0
            for ctx in contexts:
                if _codex_hidden_from_catalog(ctx):
                    continue  # allow_implicit_invocation: false keeps it loaded but out of the list
                name = codex_name(ctx) or ctx.name
                desc = " ".join(str(ctx.value("description") or "").split())
                if len(desc) > CODEX_CATALOG_DESC_CAP:
                    desc = desc[: CODEX_CATALOG_DESC_CAP - 3] + "..."
                total += len(f"- {name}: {desc} (file: r0/{ctx.name}/SKILL.md)\n")
            if total > CODEX_CATALOG_BUDGET:
                out.append(_catalog_finding("codex", "codex-desc-catalog-budget", "warning", f"installing every catalog skill renders about {total} characters of skill lines (0.153.0 root-relative locators; 0.147.0 absolute paths are longer), over the {CODEX_CATALOG_BUDGET}-character / 2%-of-context budget; Codex shortens descriptions round-robin and may omit skills",
                                            "install only the skills a project needs or shorten descriptions"))
    if "antigravity" in profiles:
        def agy_name(ctx: SkillContext) -> str | None:
            if ctx.parse_error is not None or not ctx.fm_present:
                return None
            name = ctx.value("name")
            if isinstance(name, (list, dict)):
                return None
            if name is None or (isinstance(name, str) and not name.strip()):
                return "SKILL"
            return str(name)
        for name, group in _names_by(contexts, agy_name).items():
            if len(group) > 1:
                for ctx in group:
                    others = ", ".join(_display_path(o.entry.dir) for o in group if o is not ctx)
                    out.append(_catalog_finding("antigravity", "antigravity-name-dedup", "error", f"resolved name {name!r} is shared with {others}; only the first in path order survives",
                                                "give each skill a unique name", ctx=ctx, line=ctx.key_line("name")))
    if "cursor" in profiles:
        for group in _realpath_groups(contexts):
            for ctx in group[1:]:
                out.append(_catalog_finding("cursor", "cursor-discovery-symlinks", "warning", f"resolves to the same file as {_display_path(group[0].entry.dir)}; Cursor de-duplicates by realpath and keeps the first",
                                            "keep one entry per target", ctx=ctx))
        if full_catalog:
            total = 0
            for ctx in contexts:
                if _claude_bool(ctx.value("disable-model-invocation")) is True:
                    continue
                desc = _desc_text(ctx) or ""
                total += len(str(ctx.entry.skill_md.resolve())) + min(len(desc), CURSOR_DESC_CAP) + 60
            if total > CURSOR_PROMPT_BUDGET:
                out.append(_catalog_finding("cursor", "cursor-description-prompt-budget", "warning", f"installing every catalog skill renders about {total} characters in <available_skills>, over the ~{CURSOR_PROMPT_BUDGET}-character (2% of 200k) budget; Cursor shortens descriptions to <=480 characters, then drops them, then omits skills from the end of the list",
                                            "install only the skills a project needs or shorten descriptions"))
    return out


PROFILE_FUNCS: dict[str, Callable[[SkillContext], list[Finding]]] = {
    "spec": profile_spec,
    "claude-code": profile_claude_code,
    "codex": profile_codex,
    "antigravity": profile_antigravity,
    "cursor": profile_cursor,
}


def run_profiles(contexts: Sequence[SkillContext], profiles: Sequence[str] = PROFILES, *, catalog: bool = True,
                 full_catalog: bool = True, discovery: Discovery | None = None) -> list[Finding]:
    """Run the selected profiles over every context, plus the catalog-level checks."""

    findings: list[Finding] = []
    for ctx in contexts:
        for profile in profiles:
            findings.extend(PROFILE_FUNCS[profile](ctx))
    if catalog:
        findings.extend(catalog_checks(contexts, profiles, full_catalog=full_catalog, discovery=discovery))
    return findings


def sort_findings(findings: Iterable[Finding]) -> list[Finding]:
    order = {p: i for i, p in enumerate(PROFILES)}
    return sorted(findings, key=lambda f: (f.file or "~", f.skill, order.get(f.profile, 99), _SEVERITY_RANK[f.severity], f.line or 0, f.rule_id))


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

_COLORS = {"error": "\033[31m", "warning": "\033[33m", "info": "\033[36m", "reset": "\033[0m", "bold": "\033[1m"}


def _counts(findings: Iterable[Finding]) -> dict[str, int]:
    counts = {"errors": 0, "warnings": 0, "infos": 0}
    for f in findings:
        counts[f.severity + "s"] += 1
    return counts


def format_text(findings: Sequence[Finding], contexts: Sequence[SkillContext], profiles: Sequence[str], *, color: bool = False) -> str:
    lines: list[str] = []
    c = (lambda sev, text: f"{_COLORS[sev]}{text}{_COLORS['reset']}") if color else (lambda sev, text: text)
    by_skill: dict[str, list[Finding]] = {}
    for f in sort_findings(findings):
        by_skill.setdefault(f.skill, []).append(f)
    ordered = [ctx.name for ctx in contexts] + sorted(k for k in by_skill if k not in {ctx.name for ctx in contexts})
    seen: set[str] = set()
    for skill in ordered:
        if skill in seen or skill not in by_skill:
            continue
        seen.add(skill)
        group = by_skill[skill]
        lines.append(c("bold", skill or "(catalog)") + f"  {group[0].file}" if skill else c("bold", "(catalog)"))
        for profile in PROFILES:
            sub = [f for f in group if f.profile == profile]
            if not sub:
                continue
            lines.append(f"  [{profile}]")
            for f in sub:
                where = f"{f.file}:{f.line}" if f.line else (f.file or "-")
                body = f.message[len(f.rule_id) + 2 :] if f.message.startswith(f.rule_id + ": ") else f.message
                lines.append(f"    {c(f.severity, f.severity.upper().ljust(7))}  {f.rule_id}  {where}  {body}  [fix: {f.hint}]")
    counts = _counts(findings)
    per_profile = ", ".join(
        f"{p}: {_counts(f for f in findings if f.profile == p)['errors']}E/{_counts(f for f in findings if f.profile == p)['warnings']}W/{_counts(f for f in findings if f.profile == p)['infos']}I"
        for p in profiles
    )
    lines.append(f"{len(contexts)} skills checked: {counts['errors']} errors, {counts['warnings']} warnings, {counts['infos']} infos ({per_profile})")
    return "\n".join(lines) + "\n"


def _gh_escape(text: str, prop: bool = False) -> str:
    text = text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if prop:
        text = text.replace(":", "%3A").replace(",", "%2C")
    return text


def format_github(findings: Sequence[Finding], contexts: Sequence[SkillContext], profiles: Sequence[str]) -> str:
    text = format_text(findings, contexts, profiles, color=False)
    commands = []
    kinds = {"error": "error", "warning": "warning", "info": "notice"}
    for f in sort_findings(findings):
        props = [f"title={_gh_escape(f.rule_id, True)}"]
        if f.file:
            props.insert(0, f"file={_gh_escape(f.file, True)}")
            if f.line:
                props.insert(1, f"line={f.line}")
        commands.append(f"::{kinds[f.severity]} {','.join(props)}::{_gh_escape(f.message + ' [fix: ' + f.hint + ']')}")
    return text + ("\n".join(commands) + "\n" if commands else "")


def format_json(findings: Sequence[Finding], contexts: Sequence[SkillContext], profiles: Sequence[str], *, failing_level: str, exit_code: int, note: str | None = None) -> str:
    skills = []
    for ctx in contexts:
        own = [f for f in findings if f.skill == ctx.name]
        skills.append({
            "name": ctx.name,
            "path": _display_path(ctx.entry.dir),
            "skill_md": _display_path(ctx.entry.skill_md),
            "profiles": {p: _counts(f for f in own if f.profile == p) for p in profiles},
        })
    summary: dict[str, object] = {
        "skills": len(contexts),
        "profiles": list(profiles),
        **_counts(findings),
        "by_profile": {p: _counts(f for f in findings if f.profile == p) for p in profiles},
        "failing_level": failing_level,
        "exit_code": exit_code,
    }
    if note:
        summary["note"] = note
    doc = {"skills": skills, "findings": [f.as_dict() for f in sort_findings(findings)], "summary": summary}
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def format_summary_markdown(findings: Sequence[Finding], contexts: Sequence[SkillContext], profiles: Sequence[str], *, title: str) -> str:
    out = [f"## {title}", ""]
    for profile in profiles:
        sub = [f for f in findings if f.profile == profile]
        counts = _counts(sub)
        out.append(f"### {profile} - {counts['errors']} errors, {counts['warnings']} warnings, {counts['infos']} infos")
        out.append("")
        out.append("| skill | errors | warnings | infos |")
        out.append("|---|---|---|---|")
        for ctx in contexts:
            own = _counts(f for f in sub if f.skill == ctx.name)
            out.append(f"| `{_display_path(ctx.entry.dir)}` | {own['errors']} | {own['warnings']} | {own['infos']} |")
        catalog = _counts(f for f in sub if f.skill == "")
        if any(catalog.values()):
            out.append(f"| (catalog) | {catalog['errors']} | {catalog['warnings']} | {catalog['infos']} |")
        out.append("")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
# --changed-since
# --------------------------------------------------------------------------- #


def _git(args: Sequence[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def changed_files(ref: str, cwd: Path) -> list[Path]:
    """Files added/modified/renamed since ``git merge-base REF HEAD`` (plus untracked files)."""

    toplevel = _git(["rev-parse", "--show-toplevel"], cwd)
    if toplevel is None:
        raise RuntimeError(f"{cwd} is not inside a git repository")
    root = Path(toplevel.strip())
    out = _git(["diff", "--name-only", "--diff-filter=AMR", "--merge-base", ref], root)
    if out is None:
        base = _git(["merge-base", ref, "HEAD"], root)
        base_ref = base.strip() if base else ref
        out = _git(["diff", "--name-only", "--diff-filter=AMR", base_ref], root)
    if out is None:
        raise RuntimeError(f"git diff against {ref!r} failed (is the ref fetched?)")
    files = [root / line for line in out.splitlines() if line.strip()]
    untracked = _git(["ls-files", "--others", "--exclude-standard"], root)
    if untracked:
        files.extend(root / line for line in untracked.splitlines() if line.strip())
    return files


def _resolve_all(files: Sequence[Path]) -> list[Path]:
    resolved = []
    for f in files:
        try:
            resolved.append(f.resolve())
        except OSError:
            resolved.append(f)
    return resolved


def _touched(directory: Path, resolved: Sequence[Path]) -> bool:
    try:
        target = directory.resolve()
    except OSError:
        target = directory
    return any(target == f or target in f.parents for f in resolved)


def select_changed(contexts: Sequence[SkillContext], files: Sequence[Path]) -> list[SkillContext]:
    resolved = _resolve_all(files)
    return [ctx for ctx in contexts if _touched(ctx.entry.dir, resolved)]


def select_changed_directories(discovery: Discovery, files: Sequence[Path]) -> list[Path]:
    """Discovery-level directories (case variants, orphans, hidden skills) that changed.

    These never become skill contexts, so their findings would otherwise be
    filtered out of a ``--changed-since`` run and a pull request adding one
    would pass green.
    """

    resolved = _resolve_all(files)
    candidates = [d for d, _ in discovery.case_variants] + [p for p, _ in discovery.orphans] + list(discovery.hidden_skills)
    out: list[Path] = []
    for directory in candidates:
        if directory not in out and _touched(directory, resolved):
            out.append(directory)
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _default_paths(repo_root: Path) -> list[Path]:
    return [p for p in (repo_root / "skills", repo_root / "skill-search") if p.is_dir()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_skills.py",
        description="Static SKILL.md validator: spec, claude-code, codex, antigravity and cursor profiles.",
    )
    parser.add_argument("paths", nargs="*", help="skill directories, SKILL.md files or collection directories (default: skills/ and skill-search/)")
    parser.add_argument("--profile", action="append", choices=("all", *PROFILES), help="profile to run (repeatable; default all)")
    parser.add_argument("--changed-since", metavar="REF", help="only skills with added/modified/renamed files since `git merge-base REF HEAD`")
    parser.add_argument("--format", choices=("text", "json", "github"), default="text")
    parser.add_argument("--summary", metavar="FILE", help="append a Markdown report (e.g. $GITHUB_STEP_SUMMARY)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--list", action="store_true", help="print the discovered skills (name<TAB>path) and exit")
    parser.add_argument("--no-color", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    global _REPO_ROOT
    parser = build_parser()
    args = parser.parse_args(argv)
    if yaml is None:
        print("validate_skills.py: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
        return 2
    repo_root = Path(__file__).resolve().parent.parent
    _REPO_ROOT = repo_root
    profiles: list[str] = list(PROFILES) if not args.profile or "all" in args.profile else [p for p in PROFILES if p in args.profile]
    try:
        inputs = [Path(p) for p in args.paths] if args.paths else _default_paths(repo_root)
        if not inputs:
            print(f"validate_skills.py: no skills/ or skill-search/ directory under {repo_root} and no paths given", file=sys.stderr)
            return 2
        discovery = discover_skills(inputs)
    except FileNotFoundError as exc:
        print(f"validate_skills.py: {exc}", file=sys.stderr)
        return 2
    try:
        names = {entry.name for entry in discovery.entries}
        contexts = [load_skill(entry, catalog_names=names) for entry in discovery.entries]
        selected = contexts
        touched_dirs: list[Path] = []
        note: str | None = None
        if args.changed_since:
            files = changed_files(args.changed_since, Path.cwd())
            selected = select_changed(contexts, files)
            touched_dirs = select_changed_directories(discovery, files)
            if not selected and not touched_dirs:
                if args.format == "json":
                    sys.stdout.write(format_json([], [], profiles, failing_level="warning" if args.strict else "error",
                                                 exit_code=0, note="no skills changed"))
                else:
                    print("no skills changed")
                return 0
            names = [ctx.name for ctx in selected] + [d.name for d in touched_dirs]
            note = f"validating {len(names)} changed skill(s): " + ", ".join(names)
        if args.list:
            # Only real skill directories: agentskills/skills-ref cannot validate
            # a directory without a SKILL.md.
            for ctx in selected:
                print(f"{ctx.name}\t{ctx.entry.dir.resolve()}")
            return 0
        findings = run_profiles(contexts, profiles, catalog=True, full_catalog=args.changed_since is None, discovery=discovery)
        if args.changed_since:
            keep = {ctx.name for ctx in selected} | {d.name for d in touched_dirs}
            findings = [f for f in findings if f.skill in keep]
        findings = sort_findings(findings)
        failing_level = "warning" if args.strict else "error"
        failing = [f for f in findings if _SEVERITY_RANK[f.severity] <= _SEVERITY_RANK[failing_level]]
        exit_code = 1 if failing else 0
        if args.format == "json":
            sys.stdout.write(format_json(findings, selected, profiles, failing_level=failing_level, exit_code=exit_code, note=note))
        else:
            if note:
                print(note)
            color = args.format == "text" and not args.no_color and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
            if args.format == "github":
                sys.stdout.write(format_github(findings, selected, profiles))
            else:
                sys.stdout.write(format_text(findings, selected, profiles, color=color))
        if args.summary:
            title = f"Skill compatibility ({', '.join(profiles)}; {len(selected)} skills{'; changed since ' + args.changed_since if args.changed_since else ''})"
            with open(args.summary, "a", encoding="utf-8") as fh:
                fh.write(format_summary_markdown(findings, selected, profiles, title=title))
        return exit_code
    except RuntimeError as exc:
        print(f"validate_skills.py: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - internal errors are reported, not raised
        print(f"validate_skills.py: internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
