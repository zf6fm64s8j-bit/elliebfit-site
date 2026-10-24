#!/usr/bin/env python3
"""Build the allowlisted production artifact locally; never deploys or pushes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from site_inventory import public_files

ROOT = Path(__file__).resolve().parent.parent


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True, help='New directory outside repository')
    args = cli.parse_args()
    out = args.output.resolve()
    if out == ROOT or ROOT in out.parents:
        cli.error('output must be outside repository')
    files = public_files(ROOT)
    for rel in files:
        if rel.endswith('.html'):
            source = (ROOT / rel).read_text()
            for marker in ('abf-local-preview-badge', "Draft for Ellen's Review", 'LAN review preview'):
                if marker in source:
                    raise ValueError('preview marker in production source: ' + rel)
    out.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for rel in sorted(files):
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
        hashes[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    # Validate precisely the files that will be published, not the repository root.
    for script in ('scripts/validate-site.py', 'docs/source/check-seo.py', 'scripts/audit-navigation.py'):
        subprocess.run([sys.executable, str(ROOT / script), '--root', str(out)], check=True)
    receipt = out.parent / (out.name + '.manifest.json')
    receipt.write_text(json.dumps(hashes, indent=2))
    print(json.dumps({'directory': str(out), 'files': len(hashes), 'manifest': str(receipt)}))


if __name__ == '__main__':
    main()
