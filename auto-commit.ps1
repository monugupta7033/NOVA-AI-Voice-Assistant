Set-Location "D:\100-days-of-machine-learning-main\proactive-agent-main\proactive-agent-main"

$changes = git status --porcelain

if ($changes) {
    git add .
    
    $time = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Auto commit - $time"
    
    git push
}