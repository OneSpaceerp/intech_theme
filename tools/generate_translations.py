#!/usr/bin/env python3
"""Build the white-label translation files from the vendor apps' own catalogues.

Every string the vendor apps show that names them is found, renamed, and written to
`intech_theme/translations/<lang>.csv`. Because this app is installed after them, its
translations win, so the renamed strings are what reach the screen -- in every language
the vendor apps ship, English included.

Run it again after upgrading Frappe or ERPNext, so strings added by the new version are
covered too:

    python tools/generate_translations.py --apps ../frappe ../erpnext ../hrms

It needs nothing but the Python standard library and does not need a running bench.
"""

from __future__ import annotations

import argparse
import ast
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Load the text module by path: importing the package would pull in `frappe`.
_spec = importlib.util.spec_from_file_location("it_text", ROOT / "intech_theme" / "utils" / "text.py")
it_text = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(it_text)

# The brand keeps its Latin spelling in every language unless a glossary says otherwise.
BRAND_BY_LANGUAGE: dict[str, str] = {}

# JSON keys whose values are shown to users (DocType, Workspace, Report and fixture files).
VISIBLE_JSON_KEYS = frozenset(
	{
		"label",
		"description",
		"title",
		"name",
		"module",
		"module_name",
		"app_title",
		"item_label",
		"subtitle",
		"intro",
		"success_message",
		"documentation",
		"placeholder",
		"options",
		"content",
		"message",
		"action_label",
		"header",
		"text",
	}
)

SKIP_DIRS = {"node_modules", ".git", "__pycache__", "dist", "tests", "test_records"}


def brand_for(lang: str) -> str:
	return BRAND_BY_LANGUAGE.get(lang.split("-")[0], it_text.DEFAULT_BRAND)


GLOSSARY_DIR = ROOT / "intech_theme" / "translations" / "glossary"


def load_glossary(lang: str) -> dict[str, str]:
	"""Read a language's hand-written glossary: {source: translation}.

	A glossary is the files under `translations/glossary/<lang>/*.tsv`, one entry a line,
	source and translation separated by a tab. It is the reviewed wording for that
	language, and it replaces whatever the vendor apps' own catalogues say.
	"""
	entries: dict[str, str] = {}
	folder = GLOSSARY_DIR / lang
	if not folder.is_dir():
		return entries

	for path in sorted(folder.glob("*.tsv")):
		for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
			# A comment is a line that starts with "#" and has no tab. A source string may
			# itself start with "#" ("# Req'd Items"), and that line has one.
			if not line.strip() or (line.startswith("#") and "\t" not in line):
				continue
			source, tab, translation = line.partition("\t")
			source, translation = source.strip(), translation.strip()
			if not tab or not source or not translation:
				raise ValueError(f"{path.name}:{number}: expected 'source<TAB>translation'")
			if source in entries and entries[source] != translation:
				raise ValueError(f"{path.name}:{number}: {source!r} is translated twice, differently")
			problem = placeholder_mismatch(source, translation)
			if problem:
				raise ValueError(f"{path.name}:{number}: {source!r}: {problem}")
			entries[source] = translation
	return entries


# What a translation has to carry over untouched: format fields, printf fields, HTML tags.
_PLACEHOLDER = re.compile(r"\{[^{}]*\}|%\(\w+\)s|%[sd]|</?[a-zA-Z][^>]*>")


def placeholder_mismatch(source: str, translation: str) -> str:
	"""Say what is wrong if a translation dropped, added or altered a placeholder.

	A missing `{0}` raises an error when the string is formatted, and a missing tag breaks
	the page it is shown on, so a glossary with either is refused outright.
	"""
	wanted = sorted(_PLACEHOLDER.findall(source))
	found = sorted(_PLACEHOLDER.findall(translation))
	if wanted == found:
		return ""
	missing = [item for item in wanted if item not in found]
	extra = [item for item in found if item not in wanted]
	return f"placeholders differ (missing {missing}, unexpected {extra})"


def is_prose(source: str) -> bool:
	"""True if `source` has words of its own besides the vendor's name."""
	remainder = it_text.rebrand(source, "")
	return any(character.isalpha() for character in remainder)


# -- PO parsing ---------------------------------------------------------------


def _unquote(fragment: str) -> str:
	fragment = fragment.strip()
	if not (fragment.startswith('"') and fragment.endswith('"')):
		return ""
	try:
		return ast.literal_eval(fragment)
	except (SyntaxError, ValueError):
		return fragment[1:-1]


def read_po(path: Path):
	"""Yield (context, msgid, msgstr) for each usable entry of a .po / .pot file.

	Plural entries, obsolete entries and fuzzy matches are skipped: a fuzzy translation is
	a guess, and the vendor's own loader ignores it too.
	"""
	entry: dict[str, str] = {}
	field = None
	fuzzy = False
	plural = False

	def flush():
		nonlocal entry, fuzzy, plural
		msgid = entry.get("msgid")
		if msgid and not plural:
			yield entry.get("msgctxt") or "", msgid, "" if fuzzy else entry.get("msgstr", "")
		entry, fuzzy, plural = {}, False, False

	with path.open(encoding="utf-8") as handle:
		for raw in handle:
			line = raw.strip()
			if not line:
				yield from flush()
				field = None
				continue
			if line.startswith("#~"):
				continue
			if line.startswith("#,"):
				fuzzy = fuzzy or "fuzzy" in line
				continue
			if line.startswith("#"):
				continue
			if line.startswith("msgid_plural") or line.startswith("msgstr["):
				plural = True
				field = None
				continue
			matched = False
			for key in ("msgctxt", "msgid", "msgstr"):
				if line.startswith(key + " "):
					field = key
					entry[key] = _unquote(line[len(key) :])
					matched = True
					break
			if not matched and line.startswith('"') and field:
				entry[field] = entry.get(field, "") + _unquote(line)
		yield from flush()


# -- Source scanning ----------------------------------------------------------


def find_json_strings(app_package: Path) -> set[str]:
	"""Vendor-named strings in an app's JSON definitions that the catalogues may not hold."""
	found: set[str] = set()

	def walk(node):
		if isinstance(node, dict):
			for key, value in node.items():
				if isinstance(value, str):
					if key in VISIBLE_JSON_KEYS:
						consider(value)
				else:
					walk(value)
		elif isinstance(node, list):
			for item in node:
				walk(item)

	def consider(value: str):
		# Select options and the like arrive as newline-separated lists.
		for part in value.split("\n") if len(value) < 400 else [value]:
			part = part.strip()
			if part and len(part) <= 300 and it_text.has_vendor_name(part) and "<" not in part:
				found.add(part)

	for path in app_package.rglob("*.json"):
		if SKIP_DIRS.intersection(path.parts):
			continue
		try:
			walk(json.loads(path.read_text(encoding="utf-8")))
		except (ValueError, OSError, UnicodeDecodeError):
			continue
	return found


def find_hook_strings(app_package: Path) -> set[str]:
	"""`app_title` and friends from hooks.py, which reach the screen but not the catalogue."""
	found: set[str] = set()
	hooks = app_package / "hooks.py"
	if not hooks.exists():
		return found
	try:
		tree = ast.parse(hooks.read_text(encoding="utf-8"))
	except SyntaxError:
		return found
	for node in ast.walk(tree):
		if isinstance(node, ast.Constant) and isinstance(node.value, str):
			value = node.value.strip()
			if value and len(value) <= 200 and "\n" not in value and it_text.has_vendor_name(value):
				found.add(value)
	return found


# `_("...")` in Python and Jinja, `__("...")` in JavaScript, with either quote. The catalogue
# (main.pot) is regenerated by the vendor only now and then, so a string added since - the
# desktop's "Frappe Support" row is one - reaches the screen without ever being in it.
_CODE_STRING = re.compile(
	r"""(?<![A-Za-z0-9_.])__?\(\s*(?P<q>["'`])(?P<text>(?:\\.|(?!(?P=q)).)*?)(?P=q)\s*[,)]"""
)
CODE_SUFFIXES = {".py", ".js", ".html", ".vue"}


def find_code_strings(app_package: Path) -> set[str]:
	"""Vendor-named literals passed to the translation functions in an app's source."""
	found: set[str] = set()
	for path in app_package.rglob("*"):
		if path.suffix not in CODE_SUFFIXES or SKIP_DIRS.intersection(path.parts):
			continue
		if ".bundle." in path.name and path.parent.name == "dist":
			continue
		try:
			text = path.read_text(encoding="utf-8")
		except (OSError, UnicodeDecodeError):
			continue
		if "Frappe" not in text and "ERPNext" not in text:
			continue
		for match in _CODE_STRING.finditer(text):
			value = match.group("text")
			if match.group("q") == "`" and "${" in value:
				continue  # a template literal with interpolation is not a fixed string
			value = value.replace("\\'", "'").replace('\\"', '"')
			if value and len(value) <= 300 and "\\n" not in value and it_text.has_vendor_name(value):
				found.add(value)
	return found


# -- Output -------------------------------------------------------------------


def write_csv(path: Path, rows: dict[tuple[str, str], str]):
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8", newline="") as handle:
		writer = csv.writer(handle, lineterminator="\n")
		for (source, context), translated in sorted(rows.items()):
			# The framework's loader turns a literal backslash-n back into a newline.
			writer.writerow(
				[source.replace("\n", "\\n"), translated.replace("\n", "\\n"), context]
				if context
				else [source.replace("\n", "\\n"), translated.replace("\n", "\\n")]
			)


def main(argv=None) -> int:
	parser = argparse.ArgumentParser(
		description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument(
		"--apps",
		nargs="+",
		required=True,
		type=Path,
		help="paths to the vendor app repositories, e.g. ../frappe ../erpnext",
	)
	parser.add_argument("--out", type=Path, default=ROOT / "intech_theme" / "translations")
	args = parser.parse_args(argv)

	# (source, context) -> source, for every vendor-named string in any catalogue or file
	sources: dict[tuple[str, str], str] = {}
	# lang -> (source, context) -> the vendor's own translation
	translated: dict[str, dict[tuple[str, str], str]] = {}
	# source -> every context the vendor catalogues file it under
	contexts: dict[str, set[str]] = {}

	for repo in args.apps:
		package = repo / repo.name
		if not package.is_dir():
			print(f"error: {package} is not an app package", file=sys.stderr)
			return 1

		locale = package / "locale"
		pot = locale / "main.pot"
		if pot.exists():
			for context, msgid, _ in read_po(pot):
				contexts.setdefault(msgid, set()).add(context)
				if it_text.has_vendor_name(msgid):
					sources[(msgid, context)] = msgid

		for po in sorted(locale.glob("*.po")):
			lang = po.stem.replace("_", "-")
			table = translated.setdefault(lang, {})
			for context, msgid, msgstr in read_po(po):
				if not msgstr:
					continue
				# Keep an entry if either side names the vendor: some translations add the
				# name where the source has none, and those must be renamed as well.
				if it_text.has_vendor_name(msgid) or it_text.has_vendor_name(msgstr):
					table[(msgid, context)] = msgstr
					if it_text.has_vendor_name(msgid):
						sources[(msgid, context)] = msgid

		for value in find_json_strings(package) | find_hook_strings(package) | find_code_strings(package):
			sources.setdefault((value, ""), value)

	if not sources:
		print("error: no vendor-named strings found; check the --apps paths", file=sys.stderr)
		return 1

	languages = sorted({"en", *translated})
	total = 0
	glossary_total = 0
	for lang in languages:
		brand = brand_for(lang)
		table = translated.get(lang, {})
		rows: dict[tuple[str, str], str] = {}

		for key in set(sources) | set(table):
			source = key[0]
			base = table.get(key) or source
			# An untranslated sentence stays English, so it keeps the English brand name:
			# an Arabic name dropped into an English sentence reads as a mistake. A string
			# that is nothing but the product name is the exception -- that is the name.
			use_local = key in table or not is_prose(source)
			renamed = it_text.rebrand(
				base, brand if use_local else it_text.DEFAULT_BRAND, loose=key in table and lang != "en"
			)
			# Nothing to say if the result is what the framework would show anyway.
			if renamed == source and key not in table:
				continue
			if renamed == base and not it_text.has_vendor_name(source):
				continue
			rows[key] = renamed

		# The glossary has the last word. The framework looks a string up under its
		# context first and falls back to the bare string, so an entry is written for
		# the bare string and for every context the vendor files it under: otherwise
		# the vendor's contextual translation would still win wherever one exists.
		glossary = load_glossary(lang)
		for source, translation in glossary.items():
			for context in {"", *contexts.get(source, ())}:
				rows[(source, context)] = translation
		glossary_total += len(glossary)

		write_csv(args.out / f"{lang}.csv", rows)
		total += len(rows)

	print(
		f"{len(sources)} vendor-named strings, {glossary_total} glossary entries, "
		f"{len(languages)} languages, {total} rows -> {args.out}"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
