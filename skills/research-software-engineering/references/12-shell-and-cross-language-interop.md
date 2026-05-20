# Shell + cross-language interop discipline

Loaded on demand from the `research-software-engineering` skill when
the project involves shell scripts (alone or as orchestration around
Python / Julia / C++ / Fortran / MATLAB / etc.) -- and especially
when those shell scripts read or write structured data (YAML / JSON
/ TOML) produced by another language's standard library.

This reference collects 6 rules surfaced by the `argo-anywhere`
project's `notes/agent_feedback.md` between 2026-05-13 and 2026-05-15
during real-project shipping of a bash-script-collection codebase.
Each rule is a real defect or near-defect that bit the project + cost
real iteration time. The rules are domain-bounded (shell + cross-
language interop specifically); they complement -- they do not
replace -- references 01 (numerical correctness) + 02 (testing for
numerical code).

---

## 12.1 YAML / JSON quoting on the bash / Python interop boundary

When bash parses YAML or JSON produced by Python's `yaml.safe_dump` /
`json.dumps`, **the quoting depends on the value's type**:

- `yaml.safe_dump(default_flow_style=False)` emits plain ASCII strings
  unquoted: `user: aattia` (no quotes around `aattia`).
- Numbers, booleans, null are always unquoted.
- Strings that look like numbers / booleans / contain special
  characters are quoted: `user: "true"`, `user: "123"`, `user: "a: b"`.

**The trap**: bash parsers written assuming the value is always
quoted (e.g. `awk -F'"' '/^user:/ {print $2}'`) silently return EMPTY
when the value is unquoted -- because the line has zero `"`
characters, so `awk -F'"'` sees only 1 field.

### Concrete example

```yaml
# config.yaml produced by yaml.safe_dump(default_flow_style=False):
user: aattia
verbose: true
secret_key: "abc-123"
```

```bash
# WRONG: silently returns empty for `user`, works for `secret_key`.
user=$(awk -F'"' '/^user:/ {print $2}' config.yaml)
echo "$user"  # (empty)
```

### The rule

For bash parsers of YAML / JSON produced by Python or any language
with type-aware quoting:

1. **Never assume quoting**. Use a quoting-agnostic parser (`yq` for
   YAML, `jq` for JSON) when one is available.
2. **If you must use awk / sed / cut**, anchor on the colon-space
   separator + trim quotes / whitespace explicitly:
   ```bash
   user=$(awk -F': *' '/^user:/ {gsub(/[" ]/, "", $2); print $2}' config.yaml)
   ```
3. **Verify the parser against both quoted and unquoted input** during
   testing (per rule 12.4 below).
4. **When generating bash-readable config from Python**, force
   quoting: `yaml.safe_dump({...}, default_flow_style=False,
   default_style='"')` -- emits all strings double-quoted, making
   `awk -F'"'` parsers safe. Document the requirement in the
   producer's docstring.

### Origin

argo-anywhere 2026-05-14 -- bit 2 sites in the script before being
caught. Both were single-line `awk -F'"'` parsers reading a config
produced by `yaml.safe_dump` (which omitted quotes from plain ASCII
identifiers).

---

## 12.2 `setdefault` for security-defaulted keys preserves the wrong default on upgraders

When the security-relevant default of a config key changes between
versions (e.g. `verbose: True` -> `verbose: False`), the obvious
upgrade-time pattern `config.setdefault('verbose', False)` does the
WRONG thing:

- For NEW users (clean install): correct -- they get `False`.
- For UPGRADING users whose config has the OLD value `verbose: True`
  set explicitly: correct -- they keep `True`.
- For UPGRADING users whose config has the OLD value `verbose: True`
  inherited from the OLD default (i.e. they never set it explicitly):
  WRONG -- `setdefault` is a no-op (the key already exists with
  `True`), so the OLD-default value is preserved as if the user had
  opted in to it.

The trap: **from the config file alone you CANNOT distinguish "user
explicitly opted in" from "previous version defaulted them in"**.

### The rule

For any key whose default has security relevance (verbose logging,
network access, telemetry, file-write permissions, etc.):

1. **Overwrite, do NOT setdefault**, at the boundary where the new
   default takes effect:
   ```python
   config['verbose'] = False  # NEW default; overrides any inherited value
   ```
2. **Provide an explicit opt-in channel elsewhere** so users who
   genuinely want the old behaviour can re-enable it -- typically a
   CLI flag (`--verbose`) or a new config key with a different name
   (`force_verbose: True`) that didn't exist in the old version.
3. **Document the upgrade-path implication** in the version's
   CHANGELOG / RELEASE NOTES: "the default for `verbose` changed
   from True to False; if you previously relied on `verbose: True`,
   you must now set it explicitly via the `--verbose` flag or the
   `force_verbose: True` config key. We cannot distinguish your
   prior explicit-opt-in from the prior version's default, so we
   defaulted everyone to the safer new value."

### Origin

argo-anywhere 2026-05-14 -- caught during a code-review pass; the
project was about to ship a v2.0 where `verbose` defaulted from True
to False (because verbose logging was leaking sensitive content to
syslog). The `setdefault` would have silently kept upgrading users
on the old behaviour.

---

## 12.3 Error-message recovery hints must themselves be tested

When an error message says "to recover, run X", the recovery
command must actually recover. Hints that don't work are worse than
no hint, because the user trusts them.

### Concrete example

argo-anywhere's session-cleanup error message said:

> `argo-proxy is still running. To stop it, run: screen -S argovproxy -X quit`

But when `argo-proxy` had detached from its `screen` wrapper (e.g.
because the wrapper crashed but the child kept running), `screen -X
quit` returned exit 0 and did NOTHING. The user followed the hint,
saw no error, assumed the cleanup worked, and continued. The next
session collided with the still-running child.

### The rule

For any error-message recovery hint:

1. **Test the recovery command on the SAME error condition** the
   message is about. Don't test it on a clean state where the
   command happens to succeed for a different reason.
2. **Include the verification step** in the hint:
   > "To stop it: `screen -S argovproxy -X quit && sleep 1 && pgrep -af argo-proxy`. If `pgrep` returns anything, the detached child needs `kill -9 <pid>` directly."
3. **If the recovery isn't always-applicable**, name the condition
   explicitly:
   > "If argo-proxy is running INSIDE its screen wrapper: `screen -S
   > argovproxy -X quit`. If it's detached (the screen wrapper
   > crashed): `pkill -f argo-proxy`."
4. **Don't suggest commands that print "nothing to do" because the
   recovery already ran**. The user will doubt the original
   diagnosis. Either suppress the redundant invocation OR explain
   why the command's "nothing to do" output means success.

### Origin

argo-anywhere 2026-05-14 -- the misleading hint caused a real
session collision before the rule was added to project conventions.

---

## 12.4 Test stimulus must actually exercise the assertion site

A test that sets up state X, runs command Y, and asserts on output Z
**silently fails as a test** when command Y doesn't actually read
state X. The assertion may pass (Y produces Z regardless of X) or
fail (Y never produced Z because the code path that would have was
never entered) -- either way, you've tested nothing.

### Concrete example

argo-anywhere had a test 2b: "if `~/.argo-anywhere/config.yaml`
declares `verbose: True`, then the `status` subcommand should emit
debug output to stderr". The test ran `argo-anywhere status` and
asserted on stderr containing "DEBUG:". The test PASSED. But
`status` was a thin subcommand that NEVER read the config; the debug
output it emitted came from the unrelated initialisation log. The
real assertion site (`ssh_attempt_pre()`, which DID read the verbose
config) was never reached.

### The rule

For every test, ensure the stimulus actually exercises the assertion
site. Three-step check:

1. **Identify the code site whose behaviour the test asserts on**
   (the "assertion site"): which function, which branch, which file.
2. **Verify the stimulus reaches the assertion site**: trace the
   call graph from the test's command invocation. If the stimulus
   command doesn't call the assertion-site function (or doesn't
   call the branch you're asserting on), the test is invalid.
3. **Confirm by breaking the assertion-site code temporarily** (per
   the universal "confirm the test fails when it should" rule from
   reference 02): if you negate the assertion-site condition and
   the test STILL passes, the stimulus isn't reaching the site.

### When this rule fires most

- Multi-command CLIs where many subcommands share initialisation but
  only some exercise a given feature.
- Library APIs where a high-level call internally dispatches to many
  paths, only one of which exercises the feature under test.
- Integration tests where a test setup runs through many layers
  before reaching the assertion site; one layer may short-circuit on
  cached / default behaviour.

### Origin

argo-anywhere 2026-05-15 -- 2 instances in the test suite (tests 2b
and 5b) before the rule was added; both were silently invalid
("passing") tests.

---

## 12.5 Shell-script unit-test mechanics: pipe-eats-exit-code; awk function-body extraction fragility

Two specific shell-testing gotchas that bit argo-anywhere:

### 12.5a Pipe eats upstream exit code

```bash
# WRONG: $? is always the exit code of `tail`, not the upstream command.
some_command_that_should_fail | tail -20
if [ $? -ne 0 ]; then echo "FAIL"; fi   # never fires
```

### The fix

Use one of:

- **`PIPESTATUS`** (bash, ksh):
  ```bash
  some_command_that_should_fail | tail -20
  if [ ${PIPESTATUS[0]} -ne 0 ]; then echo "FAIL"; fi
  ```
- **`set -o pipefail`** (bash):
  ```bash
  set -o pipefail
  some_command_that_should_fail | tail -20
  if [ $? -ne 0 ]; then echo "FAIL"; fi
  ```
- **Avoid the pipe** when only the exit code matters:
  ```bash
  local output
  output=$(some_command_that_should_fail 2>&1)
  if [ $? -ne 0 ]; then echo "FAIL"; fi
  echo "$output" | tail -20
  ```

### 12.5b `awk` function-body extraction fragility

A common shell-script unit-testing pattern: extract a function's body
with `awk` to source it in isolation:

```bash
# WRONG when the function body contains heredocs with `}` lines.
awk '/^my_func\(\) \{/,/^}$/' lib.sh > /tmp/my_func.sh
```

If `my_func`'s body includes a heredoc whose content has a `}` at the
start of a line (e.g. JSON or a code template), the extraction stops
prematurely.

### The fix: three alternatives

1. **Source the entire library + call the function** (preferred when
   the library is hermetic):
   ```bash
   . lib.sh
   my_func arg1 arg2
   ```
2. **Use `declare -f` to extract the function definition** (bash
   built-in, knows the actual function boundary):
   ```bash
   . lib.sh
   declare -f my_func > /tmp/my_func.sh
   ```
3. **Use a parser that understands shell syntax** (`shfmt`,
   `tree-sitter-bash`) when extraction must run without sourcing
   the library.

### Origin

argo-anywhere 2026-05-15 -- the `awk` extraction broke on a function
whose body included a heredoc with a `}` line of embedded Python
code. Caught when the extracted function failed to run; the agent
spent ~20 minutes debugging before recognising the extraction
itself was wrong.

---

## 12.6 Exit-summary "what to do next" hints must be scope-keyed, not action-keyed

When a long-running command exits (Ctrl+C, error, normal completion
with side effects), the user's mental model is **"what state is
still around?"** (scope question), not **"what verbs do I know?"**
(action question). An exit message that lists actions by name forces
the user to reverse-engineer scope.

### Concrete example

```text
# WRONG (action-keyed):
argo-anywhere exited. To recover, run one of:
  argo-anywhere status
  argo-anywhere clean
  argo-anywhere reset --tunnel-only
  argo-anywhere kill-screens
```

The user has to guess: which command matches the state I'm in? Worse,
a suggested action may print "nothing to do" because the action just
ran -- making the user doubt the original diagnosis.

```text
# RIGHT (scope-keyed):
argo-anywhere exited. The following state is still active:
  - SSH tunnel on localhost:5000 (started at 14:23)
  - argo-proxy process (PID 12345)
  - screen session 'argovproxy'

To clean up any of these, see `argo-anywhere clean --help`. To inspect
without changing state, run `argo-anywhere status`.
```

### The rule

For every exit-summary / error message that includes "what to do
next" hints:

1. **Lead with scope**: enumerate the state that's still around (PID,
   port, file, directory, lock, etc.) -- ideally with timestamps or
   sizes so the user knows what's recent and what's stale.
2. **Defer actions**: point at a help command or docs page that
   maps scope to action. Don't pre-suggest actions until the user
   has the scope picture.
3. **Make the inspection command no-op-safe**: a command named
   `status` should never change state. The user should be able to
   run it from the exit summary without worrying it will make things
   worse.

### Cross-reference

This rule also lives (in a more general doc-authoring framing) in
`human-facing-doc-authoring/SKILL.md`'s "Error message authoring"
guidance. The version here is specific to shell-script CLIs that
emit exit summaries; the version there generalises to any human-
facing error message.

### Origin

argo-anywhere 2026-05-15 -- the action-keyed exit summary caused
users to run `clean` when they meant `status`, occasionally killing
sessions they wanted to inspect.

---

## When to load this reference

Load this reference at the start of a session that involves:

- Writing or reviewing bash / shell scripts that orchestrate
  Python / Julia / C++ / Fortran / MATLAB code.
- Parsing structured config (YAML / JSON / TOML) in shell.
- Writing or debugging shell-script unit tests.
- Authoring error messages or exit summaries for any CLI tool.
- Upgrading a project across a major version that changes
  security-relevant defaults.

Do NOT load this reference for:

- Pure Python / Julia / C++ work with no shell orchestration.
- Numerical-correctness work (load reference 01 instead).
- Test-design work that isn't shell-script-specific (load reference
  02 instead).

## See also

- `research-software-engineering/references/02-testing-for-numerical-code.md`
  -- the universal "confirm the test fails when it should" rule
  underpins rule 12.4 here.
- `research-software-engineering/references/11-ai-assisted-coding-rules.md`
  -- Bridgeford 2025 R6 (the "paper tests" anti-pattern) is the
  numerical-code analogue of rule 12.4 (the shell-script
  test-stimulus rule).
- `human-facing-doc-authoring/SKILL.md` -- error-message authoring
  discipline (rule 12.6's broader cousin) lives there.

---

*Created 2026-05-17 by A. Attia. Distilled from 6 distinct findings
(F-03 through F-08) in the argo-anywhere project's
`notes/agent_feedback.md`, 2026-05-13 to 2026-05-15. Each rule
corresponds to a real defect or near-defect the agent caught (or
missed) during real-project work. The rules are
domain-bounded -- shell-script orchestration of cross-language
research codebases -- and complement, not replace, references 01
and 02.*
