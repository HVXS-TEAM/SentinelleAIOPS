# recette_6actes.ps1 — enchaîne les 6 actes de démo BTS via l'API et vérifie les effets.
$API = 'http://localhost:8000/api/v1'
$t = (Invoke-RestMethod -Uri "$API/auth/login" -Method POST -Body @{username='tech'; password='TechPass2026!'})
$h = @{Authorization = "Bearer $($t.access_token)"}

function Step($n, $label) { Write-Host "`n=== ACTE $n : $label ===" -ForegroundColor Cyan }

# Acte 1 — Reset (état nominal)
Step 1 'Reset (etat nominal)'
$r = Invoke-RestMethod -Uri "$API/simulation/reset" -Method POST -Headers $h
Write-Host "purgés: $($r.elements_purges | ConvertTo-Json -Compress)"
Write-Host "scores: $($r.scores_sante_restaures | ConvertTo-Json -Compress)"

# Acte 2 — Bruteforce SSH (Sécurité)
Step 2 'Injecter Brute-force SSH'
$r = Invoke-RestMethod -Uri "$API/simulation/inject-bruteforce" -Method POST -Headers $h
Write-Host ($r | ConvertTo-Json -Depth 4 -Compress)

# Acte 3 — Vérif sécurité via API
Start-Sleep -Seconds 3
$ev = Invoke-RestMethod -Uri "$API/securite/events?limit=50" -Headers $h
$crit = @($ev | Where-Object { $_.severite -eq 'critique' })
Write-Host "événements sécurité: $(@($ev).Count), dont critiques: $($crit.Count)"

# Acte 4 — Stress disque (Supervision / TTF)
Step 3 'Simuler Saturation Disque'
$r = Invoke-RestMethod -Uri "$API/simulation/stress-disk" -Method POST -Headers $h
Write-Host ($r | ConvertTo-Json -Depth 4 -Compress)

# Acte 5 — Vérif prédictions TTF
Start-Sleep -Seconds 3
$pred = Invoke-RestMethod -Uri "$API/supervision/predictions" -Headers $h
$urg = @($pred | Where-Object { $_.ttf_estime -le 48 })
Write-Host "prédictions: $(@($pred).Count), dont TTF<=48h (urgentes): $($urg.Count)"

# Acte 6 — Faille CIS (NetDevOps)
Step 4 'Injecter Faille CIS Cisco'
$r = Invoke-RestMethod -Uri "$API/simulation/cis-flaw" -Method POST -Headers $h
Write-Host "non-conformités: $(@($r.non_conformites).Count), health SW-CORE-01: $($r.health_score_equipement)"

# Acte 5 — Rapport PDF (binaire : écriture directe sur disque, sans parsing en mémoire)
Step 5 'Générer Rapport PDF'
Invoke-WebRequest -Uri "$API/admin/generate-pdf-report" -Headers $h -TimeoutSec 60 -OutFile rec3_report.pdf
if (Test-Path rec3_report.pdf) {
    $ko = [math]::Round((Get-Item rec3_report.pdf).Length/1KB,1)
    $magic = [System.IO.File]::ReadAllBytes("$PWD/rec3_report.pdf")[0..3] | ForEach-Object { $_.ToString('X2') }
    Write-Host "PDF généré: $ko Ko | magic: $($magic -join ' ') (%PDF attendu: 25 50 44 46)"
}

# Acte 8 — Reset final
Step 6 'Réinitialiser Démo'
$r = Invoke-RestMethod -Uri "$API/simulation/reset" -Method POST -Headers $h
Write-Host "scores après reset: $($r.scores_sante_restaures | ConvertTo-Json -Compress)"

Write-Host "`nRECETTE 6 ACTES TERMINEE" -ForegroundColor Green
