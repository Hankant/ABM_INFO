$ErrorActionPreference = 'Stop'

$SourceRoot = 'E:\Info_AI'
$DestinationRoot = 'G:\ABM_INFO'
$Paper1Root = Join-Path $SourceRoot '主Agent\文章项目\01_算法权威与信息校准'
$Records = [System.Collections.Generic.List[object]]::new()

function Copy-One {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$RelativeDestination
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        Write-Warning "Missing source: $Source"
        return
    }
    $destination = Join-Path $DestinationRoot $RelativeDestination
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $destination -Force
    $item = Get-Item -LiteralPath $destination
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash
    $Records.Add([pscustomobject]@{
        destination = $RelativeDestination
        source = $Source
        bytes = $item.Length
        sha256 = $hash
    })
}

function Copy-CleanTree {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDirectory,
        [Parameter(Mandatory = $true)][string]$RelativeDestination,
        [string[]]$ExcludedDirectories = @(),
        [string[]]$ExcludedExtensions = @()
    )
    $sourceBase = (Resolve-Path -LiteralPath $SourceDirectory).Path.TrimEnd('\')
    Get-ChildItem -LiteralPath $sourceBase -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($sourceBase.Length + 1)
        $parts = $relative -split '[\\/]'
        if (@($parts | Where-Object { $ExcludedDirectories -contains $_ }).Count -gt 0) { return }
        if ($ExcludedExtensions -contains $_.Extension.ToLowerInvariant()) { return }
        if ($_.Name.StartsWith('~$')) { return }
        Copy-One -Source $_.FullName -RelativeDestination (Join-Path $RelativeDestination $relative)
    }
}

$currentFiles = @(
    @{ Source = (Join-Path $SourceRoot 'LaTeX\Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN.tex'); Destination = '00_current_baseline\Paper1_Formal_RP_EN.tex' },
    @{ Source = (Join-Path $SourceRoot 'output\pdf\Paper1_RP_Revised_2026-08-30.pdf'); Destination = '00_current_baseline\Paper1_latest_available_PDF_2026-08-30.pdf' },
    @{ Source = (Join-Path $Paper1Root 'Paper1_AI群体信息获取与意见形成_正式RP_2026-08-24.md'); Destination = '00_current_baseline\Paper1_Formal_RP_CN_2026-08-24.md' },
    @{ Source = (Join-Path $Paper1Root 'Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN_2026-08-25.md'); Destination = '00_current_baseline\Paper1_Formal_RP_EN_2026-08-25.md' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_revision_2026-08-30\Paper1_content_changes.md'); Destination = '00_current_baseline\Paper1_content_changes_2026-08-30.md' }
)
foreach ($entry in $currentFiles) { Copy-One -Source $entry.Source -RelativeDestination $entry.Destination }

$currentNotes = @(
    'README.md',
    'Paper1_AI群体信息获取与意见形成_参考文献维护总表_2026-08-17.md',
    'Paper1_HiSim混合ABM方法拆解_2026-08-25.md',
    'Paper1_群体信息同质化_重构方案_2026-07-28.md',
    'Paper1_群体信息同质化_最小识别审查_2026-07-28.md'
)
foreach ($name in $currentNotes) {
    Copy-One -Source (Join-Path $Paper1Root $name) -RelativeDestination (Join-Path '01_research_notes\current_direction' $name)
}

$historicalNotes = @(
    '当前第一章_算法权威与信息校准_基准稿.md',
    '文献批判靶子_自动化偏差与信息校准_2026-07-05.md',
    '文献批判靶子_自动化偏差与信息校准_2026-07-05.png',
    'Literature_Targets_Automation_Bias_and_Information_Calibration_2026-07-05.md',
    'Literature_Targets_Automation_Bias_and_Information_Calibration_2026-07-05.png',
    'Paper1_理论框架_排序丰富版_2026-07-25.md',
    'Paper1_群体智慧方向_研究计划存档_2026-07-31.md',
    'Paper1_群体智慧方向_主问题锁定与行动约束_2026-07-31.md'
)
foreach ($name in $historicalNotes) {
    Copy-One -Source (Join-Path $Paper1Root $name) -RelativeDestination (Join-Path '99_historical_directions' $name)
}

$literatureNotes = @(
    'belief_attitude_opinion_construct_evidence_2026-08-01.md',
    'group_information_homogeneity_llm_abm_literature_2026-07-29.md',
    'paper1_hybrid_llm_abm_metadata_and_deepseek_prompt_2026-08-25.md',
    'verified_links.md',
    'to_collect.md',
    'pdf_archive_checklist.md',
    'README.md'
)
foreach ($name in $literatureNotes) {
    Copy-One -Source (Join-Path $SourceRoot "defense_project\reference_materials\$name") -RelativeDestination (Join-Path '02_literature\notes_and_indexes' $name)
}
Copy-One -Source (Join-Path $SourceRoot 'defense_project\latex\references.bib') -RelativeDestination '02_literature\bibliography\shared_references_full.bib'
if (Test-Path -LiteralPath (Join-Path $SourceRoot 'references_new.bib')) {
    Copy-One -Source (Join-Path $SourceRoot 'references_new.bib') -RelativeDestination '02_literature\bibliography\references_new_full.bib'
}

$paperCategories = @(
    'collective_intelligence_homogeneity',
    'llm_social_simulation',
    'opinion_dynamics_abm',
    'simulation_validation',
    'recommender_genai'
)
foreach ($category in $paperCategories) {
    $sourceCategory = Join-Path $SourceRoot "defense_project\reference_materials\papers_originals\$category"
    if (Test-Path -LiteralPath $sourceCategory) {
        Copy-CleanTree -SourceDirectory $sourceCategory -RelativeDestination (Join-Path '02_literature\papers' $category)
    }
}

Copy-One -Source 'C:\Users\69596\Downloads\2024.findings-acl.285.pdf' -RelativeDestination '02_literature\user_supplied_originals\MouEtAl2024_HiSim_2024.findings-acl.285.pdf'

$presentationFiles = @(
    @{ Source = 'F:\第一章节 AI如何改变人类群体的信息获取与信念形成.pptx'; Destination = '03_presentations\original_user_deck\第一章节_AI如何改变人类群体的信息获取与信念形成.pptx' },
    @{ Source = (Join-Path $SourceRoot 'Paper1_LLM_Group_Opinion_EN_20260826.pptx'); Destination = '03_presentations\english_decks\Paper1_LLM_Group_Opinion_EN_20260826.pptx' },
    @{ Source = (Join-Path $SourceRoot 'Paper1_LLM_Group_Opinion_EN_20260827_plain_language.pptx'); Destination = '03_presentations\english_decks\Paper1_LLM_Group_Opinion_EN_20260827_plain_language.pptx' },
    @{ Source = (Join-Path $SourceRoot 'Paper1_LLM_Group_Opinion_EN_20260827_search_comparison_fixed.pptx'); Destination = '03_presentations\english_decks\Paper1_LLM_Group_Opinion_EN_20260827_search_comparison_fixed.pptx' },
    @{ Source = (Join-Path $SourceRoot '主Agent\答辩材料\Paper1_群体信息与意见形成_第5页理论框架极简版_2026-08-24.pptx'); Destination = '03_presentations\focused_slides\Paper1_群体信息与意见形成_第5页理论框架极简版_2026-08-24.pptx' }
)
foreach ($entry in $presentationFiles) { Copy-One -Source $entry.Source -RelativeDestination $entry.Destination }

Get-ChildItem -LiteralPath $Paper1Root -File | Where-Object {
    $_.Extension -in @('.pptx', '.ndjson') -and -not $_.Name.StartsWith('~$')
} | ForEach-Object {
    Copy-One -Source $_.FullName -RelativeDestination (Join-Path '03_presentations\theory_framework_archive' $_.Name)
}

Get-ChildItem -LiteralPath (Join-Path $SourceRoot '主Agent\答辩材料') -File | Where-Object {
    $_.Name -like 'Intro_Paper1_Paper2_Paper3_Combined_MainDeck_v*.pptx' -or
    $_.Name -eq 'Paper1_Paper2_Paper3_Combined_MainDeck_v01.pptx'
} | ForEach-Object {
    Copy-One -Source $_.FullName -RelativeDestination (Join-Path '03_presentations\combined_defense_archive' $_.Name)
}

$dashboardCopy = @{
    SourceDirectory = (Join-Path $Paper1Root 'paper1-reconstruction-dashboard')
    RelativeDestination = '04_code\paper1-reconstruction-dashboard'
    ExcludedDirectories = @('.git', 'node_modules', '.vinext', '.wrangler', 'build', 'dist', '__pycache__')
    ExcludedExtensions = @('.pyc')
}
Copy-CleanTree @dashboardCopy

$hiSimCopy = @{
    SourceDirectory = (Join-Path $SourceRoot 'tmp\HiSim_source_audit')
    RelativeDestination = '04_code\third_party_reference\HiSim_source_audit'
    ExcludedDirectories = @('.git', 'build', 'dist', 'HiSim.egg-info', '__pycache__')
    ExcludedExtensions = @('.pyc')
}
Copy-CleanTree @hiSimCopy

Copy-One -Source (Join-Path $SourceRoot 'tmp\extract_hisim_pdf.py') -RelativeDestination '04_code\research_helpers\extract_hisim_pdf.py'
Copy-One -Source (Join-Path $SourceRoot 'tmp\MouEtAl2024HiSim_pages.txt') -RelativeDestination '04_code\research_helpers\MouEtAl2024HiSim_pages.txt'

$revisionFiles = @(
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_audit_2026-08-30\Paper1_research_alignment_review.md'); Destination = '05_reviews_and_revision_history\Paper1_research_alignment_review_2026-08-30.md' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_audit_2026-08-30\Paper1_language_scan.json'); Destination = '05_reviews_and_revision_history\Paper1_language_scan_audit.json' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_revision_2026-08-30\Paper1_revision.diff'); Destination = '05_reviews_and_revision_history\Paper1_revision_2026-08-30.diff' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_revision_2026-08-30\Paper1_language_scan.json'); Destination = '05_reviews_and_revision_history\Paper1_language_scan_revision.json' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_revision_2026-08-30\before\Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN.tex'); Destination = '05_reviews_and_revision_history\snapshots\before_content_revision.tex' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_revision_2026-08-30\after_content\Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN.tex'); Destination = '05_reviews_and_revision_history\snapshots\after_content_revision.tex' },
    @{ Source = (Join-Path $SourceRoot 'outputs\RP_concise_revision_2026-08-30\before\Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN.tex'); Destination = '05_reviews_and_revision_history\snapshots\before_conservative_language_revision.tex' },
    @{ Source = (Join-Path $SourceRoot 'output\pdf\Paper1_AI_Group_Information_Acquisition_and_Opinion_Formation_Formal_RP_EN.pdf'); Destination = '05_reviews_and_revision_history\older_exports\Paper1_Formal_RP_EN_2026-08-28.pdf' }
)
foreach ($entry in $revisionFiles) { Copy-One -Source $entry.Source -RelativeDestination $entry.Destination }

$manifestPath = Join-Path $DestinationRoot 'SOURCE_MANIFEST.csv'
$Records | Sort-Object destination | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding utf8

$inventoryPath = Join-Path $DestinationRoot 'PROJECT_INVENTORY.csv'
Get-ChildItem -LiteralPath $DestinationRoot -Recurse -File | Where-Object {
    $_.FullName -ne $inventoryPath
} | ForEach-Object {
    [pscustomobject]@{
        path = $_.FullName.Substring($DestinationRoot.Length + 1)
        bytes = $_.Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
    }
} | Sort-Object path | Export-Csv -LiteralPath $inventoryPath -NoTypeInformation -Encoding utf8

$summary = Get-ChildItem -LiteralPath $DestinationRoot -Recurse -File | Measure-Object Length -Sum
Write-Output ("Copied project files: {0}" -f $summary.Count)
Write-Output ("Total bytes: {0}" -f $summary.Sum)
Write-Output ("Source manifest: {0}" -f $manifestPath)
Write-Output ("Project inventory: {0}" -f $inventoryPath)
