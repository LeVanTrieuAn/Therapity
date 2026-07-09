$path = "d:\ThapSangProject\thapsang\frontend\cohort.html"
$content = [System.IO.File]::ReadAllText($path)
$content = [System.Text.RegularExpressions.Regex]::Replace($content, "(?s)<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n.*?\r?\n>>>>>>> [^\r\n]+", "`$1")
[System.IO.File]::WriteAllText($path, $content)
Write-Host "Resolved conflicts in cohort.html"
