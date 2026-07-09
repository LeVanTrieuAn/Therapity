import os

file_path = r"d:\ThapSangProject\thapsang\frontend\cohort.html"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the start of the MAIN APP section
start_idx = -1
for i, line in enumerate(lines):
    if "<!-- MAIN APP" in line:
        start_idx = i - 1 # Include the previous line (<!-- ====... )
        break

if start_idx == -1:
    print("Could not find MAIN APP section")
    exit(1)

# Modify sidebar
for i in range(start_idx):
    if 'data-i18n="nav.cohort"' in lines[i] or 'data-i18n="nav.roadmap"' in lines[i]:
        # Need to replace the icon and text
        if 'groups' in lines[i-1]:
            pass # Keep groups icon as per original sidebar if we want, but the image shows people (groups icon)
        
        # Change text
        lines[i] = lines[i].replace('Cohort', 'Personal Roadmap').replace('nav.cohort', 'nav.roadmap')

new_main_content = """<!-- ======================================================================= -->
<!-- MAIN APP                                                                 -->
<!-- ======================================================================= -->
<main class="flex-grow flex flex-col items-center justify-start pt-24 p-6 mt-16 animate-page-fade w-full h-[calc(100vh-64px)] overflow-y-auto" x-data="roadmapApp()">
    
    <div class="flex flex-col items-center justify-center w-full max-w-2xl text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#fbbf24]/20 bg-[#fbbf24]/10 mb-6">
            <span class="w-2 h-2 rounded-full bg-[#fbbf24]"></span>
            <span class="text-[10px] text-[#d0c6ab] font-bold tracking-widest uppercase">AI STANDBY MODE • UNALLOCATED</span>
        </div>

        <!-- Headers -->
        <h2 class="text-[32px] font-bold text-[#162061] dark:text-white tracking-tight mb-2">AI Personal Roadmap Allocation</h2>
        <p class="text-sm text-[#4a5568] dark:text-[#d0c6ab] flex items-center justify-center gap-2 mb-10">
            <span class="material-symbols-outlined text-[16px]">calendar_month</span>
            <span>Status: Personal roadmap is empty (null)</span>
        </p>

        <!-- Card -->
        <div class="glass-panel w-full p-10 rounded-[24px] flex flex-col items-center relative overflow-hidden bg-white dark:bg-[#161b22]/75 border border-gray-200 dark:border-gray-700/50 shadow-sm">
            <!-- decorative background -->
            <div class="absolute bottom-[-50px] right-[-50px] w-64 h-64 bg-[#fbbf24] opacity-[0.05] ] rounded-full pointer-events-none"></div>

            <div class="w-16 h-16 rounded-full bg-white dark:bg-[#fbbf24]/10 border border-[#fbbf24]/30 shadow-sm flex items-center justify-center mb-6">
                <span class="material-symbols-outlined text-[#fbbf24] text-3xl">psychology</span>
            </div>

            <h3 class="text-xl font-bold text-[#162061] dark:text-white mb-4">Reflect More with Socratic Coach</h3>
            <p class="text-sm text-[#4a5568] dark:text-[#d0c6ab] max-w-lg mb-8 leading-relaxed">
                Every Socratic exchange feeds the cognitive engine to pinpoint psychological barriers, identify biases, and build a highly customized PDCA development roadmap tailored just for you.
            </p>

            <div class="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto z-10">
                <a href="/coach" class="w-full sm:w-auto px-6 py-3 rounded-xl border border-[#fbbf24] text-[#fbbf24] bg-white dark:bg-transparent font-bold text-sm hover:bg-[#fbbf24]/10 transition-colors flex items-center justify-center gap-2 shadow-sm">
                    <span class="material-symbols-outlined text-[18px]">forum</span>
                    Go to Socratic Coach
                </a>
                <button @click="triggerAllocator()" class="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-[#fbbf24] to-[#f59e0b] text-[#0a0a0a] font-bold text-sm hover:shadow-[0_0_20px_rgba(255,225,109,0.4)] hover:scale-[1.02] transition-all flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">bolt</span>
                    Trigger AI Personal Allocator
                </button>
            </div>
        </div>
    </div>
</main>
</div>

<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('roadmapApp', () => ({
        lang: localStorage.getItem('thapsang_lang') || 'vi',
        init() {
            window.addEventListener('language-changed', (e) => {
                this.lang = e.detail;
            });
        },
        triggerAllocator() {
            showGlobalToast(this.lang === 'en' ? 'AI Allocator triggered! Generating roadmap...' : 'Đã kích hoạt AI Allocator! Đang tạo lộ trình...', 'info');
            setTimeout(() => {
                showGlobalToast(this.lang === 'en' ? 'Insufficient data. Please reflect more with Coach.' : 'Dữ liệu chưa đủ. Vui lòng thảo luận thêm với Coach.', 'error');
            }, 2500);
        }
    }));
});
</script>
</body>
</html>
"""

# Write the result back
with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines[:start_idx])
    f.write(new_main_content)

print("Successfully updated cohort.html")
