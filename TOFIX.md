# TOFIX

Findings from a code scan on 2026-10-04.

## High

- `src/mail_maildir2gmail.py:74` - the dedup database is a `bsddb3.btopen` DB, which only accepts `bytes` keys, but `check_appended`/`mark_appended` (line 77) use `str` filenames, so the first `append()` dies with `TypeError: Bytes or Integer object expected for key, str found` (verified in the repo venv); encode the keys (or switch to stdlib `dbm`, see below).

## Medium

- `src/test_mod.py:93` - `check_deps_in_sync` compares `pyproject.toml` against a `[dependencies].pip` list in `rsconstruct.toml` that no longer exists (pyproject is now the single source of truth, `pyproject.toml:1`), so `src/test.py` always fails with "pyproject.toml is stale: ... extra [every dependency]"; delete the check (and update `src/test.py:8`), and wire `test.py` into the build so it cannot rot again.
- `src/mail_imap_import.py:32` - reads the IMAP password from the plaintext `~/.details.ini`; per the pass(1)-only rule, fetch it with `pass show` at run time (or prompt via `getpass`).
- `src/mail_maildir2gmail.py:139` - Gmail password is taken as a `--password` command-line argument (visible in `ps` and shell history) with the default `"password"`; fetch it from pass(1) or `getpass` instead.
- `src/mail_imap_import.py:73` - the `rmdir` subcommand is declared (with `--toplevel`) but never dispatched (only `import` and `test` are handled at lines 94-99), so `rmdir` silently logs in and out doing nothing; implement it via `IMAP.delete_fullpath` (`src/imap/imap.py:156`) or remove it.
- `src/mail_maildir2gmail.py:62` - `parsedate()` (line 158) raises `ValueError` instead of returning a false value, so the "Skipping ... no date" branch is unreachable and one undated message aborts the run; also its timezone math (lines 162-166, duplicated in `src/imap/imap.py:63`) adds a blanket hour when `time.daylight` is set - use `email.utils.parsedate_to_datetime`/`mktime_tz`.
- `src/system_sys_remove_old_kernels.py:39` - the `apt` usage was replaced by an always-empty `MockCache` (and `cache.commit()` is commented out at line 59), so the script always reports "too few kernels" and can never remove anything; restore the `apt` implementation or delete the script.
- `pyproject.toml:20` - `PyGithub` is declared but no script imports `github`; remove it.
- `pyproject.toml:29` - `bsddb3` is unmaintained upstream (superseded by `berkeleydb`) and forces the `libdb-dev` system dependency (`rsconstruct.toml:34`) just for one script; port `src/mail_maildir2gmail.py` to stdlib `dbm` (as `src/imap/imap.py:29` already does) and drop both.

## Low

- `src/download/generic.py:33` - `progressbar.ProgressBar(maxval=...)` uses the deprecated argument (progressbar2 emits `DeprecationWarning: ... use max_value`); rename it.
- `src/download_netbeans.py:28` - downloads from `http://download.netbeans.org/netbeans/8.0.2/...`, which returns 404 (NetBeans moved to Apache); likewise `src/download_eclipe.py:35` targets a 2018-12 release on a mirror that now 404s, over plain http. Update to current https sources or delete the scripts (`download_eclipe.py` also misspells "eclipse").
- `src/download_ted.py:14` - usage text names the script `ted_download.py`; it is `download_ted.py`.
- `src/keyring_check.py:11` - tells the user to `sudo apt install python3-secretstorage` (and calls itself `check_keyring.py`), but `secretstorage` is a declared dependency installed into the venv; fix the docstring and the ImportError message at line 27.
- `doc/DESIGN.txt:13` - concludes scripts should use `#!/usr/bin/python`, but every script uses `#!/usr/bin/env python` and `src/test_mod.py:25` enforces that; update or delete the doc.
- `doc/TODO.txt:1` - refers to `make install`, but there is no Makefile (installation is `scripts/install.py`, which already skips `__pycache__`); delete the stale item.
- `scripts/install.py:83` - installs every `.py` in `src/` as a command, including the internal helpers `src/test.py` and `src/test_mod.py`, which land in `~/.local/bin` as `test.py`/`test_mod.py`; move them out of `src/` (e.g. into `tests/`) or skip them.
- `pyproject.toml:57` - the mypy `ignore_missing_imports` override lists the repo's own `download.*` package, and imports of local packages carry `# type: ignore` (e.g. `src/download_ted.py:9`, `src/mail_imap_import.py:25`, `src/audio_jack_post_start.py:21`); `mypy_path` already contains `src`, so drop the override and the inline ignores. `mypy_path` also names a nonexistent `python/` dir (`pyproject.toml:50`).
- `README.md:1` - README is only the title; document `scripts/install.py` and what the scripts are.
