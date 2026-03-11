import os
import io

PY_EXTS = ['.py']
JS_EXTS = ['.js']

skip_dirs = {'.git', '__pycache__'}

modified_files = []

def process_py(path):
    changed = False
    with io.open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            changed = True
            continue
        out.append(line)
    if changed:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.writelines(out)
    return changed

def process_js(path):
    changed = False
    with io.open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    in_block = False
    for line in lines:
        original = line
        if in_block:
            if '*/' in line:
                line = line.split('*/', 1)[1]
                in_block = False
                if line.strip() == '':
                    changed = True
                    continue
            else:
                changed = True
                continue
        if '/*' in line:
            before, rest = line.split('/*', 1)
            if '*/' in rest:
                after = rest.split('*/', 1)[1]
                line = before + after
            else:
                line = before
                in_block = True
                if line.strip() == '':
                    changed = True
                    continue
        stripped = line.lstrip()
        if stripped.startswith('//'):
            changed = True
            continue
        out.append(line)
        if original != line:
            changed = True
    if changed:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.writelines(out)
    return changed

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for fname in files:
        path = os.path.join(root, fname)
        ext = os.path.splitext(fname)[1].lower()
        try:
            if ext in PY_EXTS:
                if process_py(path):
                    modified_files.append(path)
            elif ext in JS_EXTS:
                if process_js(path):
                    modified_files.append(path)
        except Exception as e:
            print(f"Error processing {path}: {e}")

if modified_files:
    print('Modified files:')
    for p in modified_files:
        print(' -', p)
else:
    print('No modifications made.')
