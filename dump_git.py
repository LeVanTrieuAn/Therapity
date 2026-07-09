import subprocess

def get_git_file(ref, path):
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, cwd=r"d:\ThapSangProject\thapsang")
    return result.stdout

head_content = get_git_file("HEAD", "frontend/cohort.html")
merge_head_content = get_git_file("MERGE_HEAD", "frontend/cohort.html")

with open(r"d:\ThapSangProject\thapsang\frontend\cohort_head.html", "w", encoding="utf-8") as f:
    f.write(head_content)

with open(r"d:\ThapSangProject\thapsang\frontend\cohort_merge_head.html", "w", encoding="utf-8") as f:
    f.write(merge_head_content)

print("Dumped HEAD and MERGE_HEAD")
