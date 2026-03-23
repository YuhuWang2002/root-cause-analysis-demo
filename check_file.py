with open('/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/web/ontology_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
print(f'Total lines: {len(lines)}')
print('\nLast 10 lines:')
for i, line in enumerate(lines[-10:], len(lines)-9):
    print(f'Line {i}: {repr(line)}')
    print(f'  Length: {len(line)}')
    print(f'  First 10 chars: {[ord(c) for c in line[:10]]}')
    print(f'  Last 10 chars: {[ord(c) for c in line[-10:]]}')
    print()