Set-Location "D:\100-days-of-machine-learning-main\proactive-agent-main\proactive-agent-main"

$changes = git status --porcelain

if ($changes) {
    git add .
    git commit -m "Update NOVA project"
    git push
}