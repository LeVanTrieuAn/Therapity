import glob
import re

files = glob.glob('frontend/*.html')

pattern = re.compile(r'<div[^>]*class=\"w-10 h-10 rounded-full[^\"]*flex items-center justify-center shrink-0 overflow-hidden[^\"]*\">\s*<template x-if=\"user\.avatar\">\s*<img :src=\"user\.avatar\" class=\"w-full h-full object-cover\">\s*</template>\s*<template x-if=\"!user\.avatar\">\s*<span\s+class=\"material-symbols-outlined[^\"]*\">person</span>\s*</template>\s*</div>', re.DOTALL)

replacement = '''<div
                    class="w-[50px] h-[50px] rounded-[18px] bg-transparent border-[1.5px] border-[#fbbf24] flex items-center justify-center shrink-0 overflow-hidden transition-colors shadow-[0_0_15px_rgba(251,191,36,0.15)] hover:bg-[#fbbf24]/10">
                    <template x-if="user.avatar">
                        <img :src="user.avatar" class="w-full h-full object-cover">
                    </template>
                    <template x-if="!user.avatar">
                        <span
                            class="material-symbols-outlined text-[#fbbf24] text-[30px]" style="font-variation-settings: 'wght' 300;">person</span>
                    </template>
                </div>'''

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content, count = pattern.subn(replacement, content)
    if count > 0:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Updated {f} ({count} matches)')
