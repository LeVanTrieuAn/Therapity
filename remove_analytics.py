import glob
import re

files = glob.glob('frontend/*.html')

# Pattern 1: multi-line href="/analytics" (like in tasks, diary, coach, aoa, analytics)
pattern1 = re.compile(r'\s*<a class="[^"]*"\s*href="/analytics">\s*<span class="material-symbols-outlined"[^>]*>analytics</span>\s*<span class="font-body-md text-\[16px\]" data-i18n="nav\.analytics">Analytics</span>\s*</a>', re.DOTALL)

# Pattern 2: single-line `<a ... href="/analytics">` (like in cohort)
pattern2 = re.compile(r'\s*<a class="[^"]*" href="/analytics">\s*<span class="material-symbols-outlined">analytics</span>\s*<span class="font-body-md text-\[16px\]" data-i18n="nav\.analytics">Analytics</span>\s*</a>', re.DOTALL)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content, count1 = pattern1.subn('', content)
    new_content, count2 = pattern2.subn('', new_content)
    
    if count1 > 0 or count2 > 0:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Removed analytics from {f}')
