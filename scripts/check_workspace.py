"""Read-only structural checks and explicit context selection for a file workspace.

This is a small Markdown target checker, not a complete CommonMark parser. It
checks inline/image links and reference-definition destinations outside fenced
and inline code. It does not validate heading fragments, HTML links, semantics,
privacy, compliance, agent behavior, or hostile concurrent filesystem changes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

DEFAULT_WORKSPACE = Path(__file__).resolve().parent.parent / 'example'


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def _without_code(text: str) -> str:
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence):
                fence = None
            lines.append('')
        elif match:
            fence = match[1]
            lines.append('')
        elif line.startswith(('    ', '\t')):
            lines.append('')
        else:
            lines.append(line)
    return re.sub(r'(`+)(.*?)(?<!`)\1(?!`)', '', '\n'.join(lines), flags=re.S)


def _destination(text: str) -> str | None:
    text = text.lstrip()
    if text.startswith('<'):
        closing = text.find('>')
        return text[1:closing] if closing >= 0 else None
    depth = 0
    escaped = False
    end = len(text)
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == chr(92):
            escaped = True
        elif char == '(':
            depth += 1
        elif char == ')':
            if depth == 0:
                end = index
                break
            depth -= 1
        elif char.isspace() and depth == 0:
            end = index
            break
    return text[:end] if depth == 0 else None


def _unescape(value: str) -> str:
    import string
    output = []
    index = 0
    while index < len(value):
        if value[index] == chr(92) and index + 1 < len(value) and value[index + 1] in string.punctuation + ' ':
            index += 1
        output.append(value[index])
        index += 1
    return ''.join(output)


def markdown_destinations(text: str):
    """Yield supported link targets; external targets are classified by the caller."""
    text = _without_code(text)
    for match in re.finditer(re.escape(']('), text):
        destination = _destination(text[match.end():])
        if destination is not None:
            yield _unescape(destination)
    for match in re.finditer(r'^ {0,3}\[[^\]\n]+\]:[ \t]*(.*)$', text, flags=re.M):
        destination = _destination(match[1])
        if destination is not None:
            yield _unescape(destination)


def check_workspace(workspace: Path, route: str | None = None) -> dict:
    root = Path(workspace).resolve()
    report = {'ok': False, 'schema_version': None, 'selected_route': route,
              'routes': [], 'markdown_files_checked': 0, 'context': [],
              'total_context_bytes': 0, 'errors': []}
    seen_errors = set()

    def error(code, path, message):
        item = (code, str(path), message)
        if item not in seen_errors:
            seen_errors.add(item)
            report['errors'].append(dict(zip(('code', 'path', 'message'), item)))

    def safe_path(value, *, base=root, config=False):
        if not isinstance(value, str) or not value.strip() or '\x00' in value:
            error('invalid_path', 'workspace.json' if config else value, 'Path must be a nonempty string.')
            return None
        value = value.replace(chr(92), '/')
        if value.startswith('/') or re.match(r'^[A-Za-z]:', value):
            error('path_escape', value, 'Absolute paths are not allowed.')
            return None
        if config and any(part in ('', '.', '..') for part in value.split('/')):
            error('invalid_path', value, 'Configured paths must use ordinary relative segments.')
            return None
        candidate = Path(os.path.abspath(base / value))
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            error('path_escape', value, 'Path resolves outside the selected workspace.')
            return None
        cursor = root
        for part in relative.parts:
            cursor = cursor / part
            if cursor.is_symlink() or (hasattr(cursor, 'is_junction') and cursor.is_junction()):
                error('symlink', str(cursor.relative_to(root)), 'Symbolic links and junctions are not followed.')
                return None
        return candidate

    def require_file(path):
        if path is None:
            return False
        relative = path.relative_to(root).as_posix()
        checked = safe_path(relative)
        if checked is None:
            return False
        if not checked.is_file():
            error('missing_file', relative, 'Required file is missing or is not a regular file.')
            return False
        return True

    if not root.is_dir():
        error('missing_workspace', '.', 'Workspace directory does not exist.')
        return report
    config_path = safe_path('workspace.json')
    if not require_file(config_path):
        return report
    try:
        document = json.loads(config_path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError):
        error('invalid_schema', 'workspace.json', 'Configuration must be valid UTF-8 JSON with unique keys.')
        return report
    if not isinstance(document, dict) or set(document) != {'schema_version', 'routes'}:
        error('invalid_schema', 'workspace.json', 'Expected only schema_version and routes.')
        return report
    if type(document['schema_version']) is not int or document['schema_version'] != 1:
        error('invalid_schema', 'workspace.json', 'Only integer schema_version 1 is supported.')
        return report
    report['schema_version'] = 1
    routes = document['routes']
    if not isinstance(routes, dict) or not routes:
        error('invalid_schema', 'workspace.json', 'routes must be a nonempty object.')
        return report
    report['routes'] = sorted(routes)
    projects = {}
    references = {}
    for name, definition in routes.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(definition, dict) or set(definition) != {'project', 'references'}:
            error('invalid_schema', 'workspace.json', 'Each named route requires only project and references.')
            continue
        refs = definition['references']
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            error('invalid_schema', 'workspace.json', f'Route {name} references must be a list of paths.')
            continue
        project = safe_path(definition['project'], config=True)
        projects[name] = project
        references[name] = [safe_path(ref, config=True) for ref in refs]
        if project is not None:
            if not project.is_dir():
                error('missing_project', definition['project'], 'Route project directory is missing.')
            for filename in ('AGENTS.md', 'MEMORY.md', 'Handoff.md'):
                require_file(project / filename)
        for ref in references[name]:
            require_file(ref)
    for filename in ('AGENTS.md', 'MEMORY.md'):
        require_file(root / filename)
    if route is not None and route not in routes:
        error('unknown_route', 'workspace.json', 'The selected route is not declared.')

    # Scan Markdown across the workspace, independently of selected context.
    # os.walk does not follow directory links; report and remove them explicitly.
    for directory, folders, files in os.walk(root, followlinks=False):
        directory = Path(directory)
        for folder in list(folders):
            path = directory / folder
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                error('symlink', path.relative_to(root).as_posix(), 'Symbolic links and junctions are not followed.')
                folders.remove(folder)
        for filename in sorted(files):
            path = safe_path((directory / filename).relative_to(root).as_posix())
            if path is None or path.suffix.lower() != '.md':
                continue
            report['markdown_files_checked'] += 1
            try:
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                error('unreadable_file', path.relative_to(root).as_posix(), 'Markdown must be readable UTF-8 text.')
                continue
            for target in markdown_destinations(text):
                if not target or target.startswith('#'):
                    continue
                try:
                    url = urlsplit(target)
                except ValueError:
                    error('invalid_link', path.relative_to(root).as_posix(), 'Malformed link destination.')
                    continue
                if url.scheme or url.netloc:
                    if url.scheme.lower() == 'file' or re.match(r'^[A-Za-z]:', target):
                        error('path_escape', path.relative_to(root).as_posix(), 'Local file links must remain inside the workspace.')
                    continue
                destination = safe_path(unquote(url.path), base=path.parent)
                if destination is not None and not destination.exists():
                    error('broken_link', path.relative_to(root).as_posix(), f'Local link target does not exist: {target}')

    if route in projects and projects[route] is not None:
        project = projects[route]
        chain = [root]
        cursor = root
        for part in project.relative_to(root).parts:
            cursor /= part
            chain.append(cursor)
        chosen = []
        for owner in chain:
            for filename in ('AGENTS.md', 'MEMORY.md'):
                path = safe_path((owner / filename).relative_to(root).as_posix())
                if path is not None and path.is_file():
                    chosen.append(path)
        chosen.append(project / 'Handoff.md')
        chosen.extend(ref for ref in references[route] if ref is not None)
        seen_context = set()
        for path in chosen:
            key = path.relative_to(root).as_posix()
            if key in seen_context or not require_file(path):
                continue
            seen_context.add(key)
            try:
                size = len(path.read_bytes())
            except OSError:
                error('unreadable_file', key, 'Selected context file could not be read.')
                continue
            report['context'].append({'path': key, 'bytes': size})
        report['total_context_bytes'] = sum(item['bytes'] for item in report['context'])
    report['ok'] = not report['errors']
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Read-only workspace structure and explicit-context checker.',
        epilog='No route means structural validation only. Sizes are bytes, not tokens. No network requests or writes. '
               'Checks supported Markdown target existence, not heading fragments or full Markdown syntax. '
               'Cannot establish semantic correctness, privacy, compliance, or automatic agent context loading. '
               'Use a trusted, stationary workspace; this is not a hostile-filesystem sandbox.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE,
                        help='workspace root (default: example beside scripts, independent of current directory)')
    parser.add_argument('--route', help='explicit route key to select context for')
    parser.add_argument('--json', action='store_true', help='emit structured results')
    args = parser.parse_args(argv)
    result = check_workspace(args.workspace, args.route)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print('PASS' if result['ok'] else 'FAIL')
        print(f"Routes: {', '.join(result['routes'])}")
        print(f"Markdown files checked: {result['markdown_files_checked']}")
        print(f"Selected route: {result['selected_route'] or '(none)'}")
        for item in result['context']:
            print(f"  {item['path']} ({item['bytes']} bytes)")
        print(f"Total selected context: {result['total_context_bytes']} bytes")
        for item in result['errors']:
            print(f"  {item['code']}: {item['path']}: {item['message']}")
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
