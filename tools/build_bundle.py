#!/usr/bin/env python3
"""Test and package matching backend services without installing or starting them."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile

ROOT: Path = Path(__file__).resolve().parents[1]


def run(command: list[str], directory: Path) -> None:
    print(' '.join(command), flush=True)
    subprocess.run(command, cwd=directory, check=True)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=4)
    args: argparse.Namespace = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    hosts: dict[str, str] = {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}
    host: str = hosts[platform.system()]
    architecture: str = 'x64'
    if platform.machine().lower() in ('arm64', 'aarch64'):
        architecture = 'arm64'
    target: str = host + '-' + architecture
    revision_output: str = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True)
    revision: str = revision_output.strip()
    build: Path = ROOT / '.build' / target
    bundle: Path = build / 'bundle'
    bundle.mkdir(parents=True, exist_ok=True)
    engine: Path = ROOT / 'engine'
    orchestrator: Path = ROOT / 'orchestrator'
    os.environ['GOMAXPROCS'] = str(args.jobs)
    run(['go', 'test', '-p', str(args.jobs), './...'], engine)
    run(['go', 'vet', './...'], engine)
    run(['cargo', '+stable', 'fmt', '--check'], orchestrator)
    run(['cargo', '+stable', 'run', '--locked', '--bin', 'orchestrator-fixtures', '--', '--check'], orchestrator)
    run(['cargo', '+stable', 'test', '--locked', '--jobs', str(args.jobs)], orchestrator)
    run(['cargo', '+stable', 'clippy', '--locked', '--all-targets', '--all-features',
         '--jobs', str(args.jobs), '--', '-D', 'warnings'], orchestrator)
    suffix: str = ''
    if host == 'windows':
        suffix = '.exe'
    run(['go', 'build', '-trimpath', '-o', str(bundle / ('fileman-engine' + suffix)),
         './cmd/fileman-engine'], engine)
    run(['cargo', '+stable', 'build', '--locked', '--release', '--bin', 'orchestrator',
         '--jobs', str(args.jobs)], orchestrator)
    shutil.copy2(orchestrator / 'target/release' / ('orchestrator' + suffix), bundle)
    shutil.copy2(ROOT / 'LICENSE', bundle)
    files: dict[str, str] = {}
    name: str
    for name in ['fileman-engine' + suffix, 'orchestrator' + suffix, 'LICENSE']:
        data: bytes = (bundle / name).read_bytes()
        files[name] = hashlib.sha256(data).hexdigest()
    manifest: dict[str, object] = {
        'schema': 1, 'repository': 'falseywinchnet/backend', 'revision': revision,
        'platform': target, 'files': files,
        'validation': 'go test/vet; cargo fmt/test/clippy; locked release build',
        'limits': 'Not installed or activated; no platform capability promotion'}
    (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive: Path = build / ('backend-' + target + '.tar.gz')
    with tarfile.open(archive, 'w:gz') as stream:
        stream.add(bundle, arcname='backend')
    digest: str = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.gz.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
