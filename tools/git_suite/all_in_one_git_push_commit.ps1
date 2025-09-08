<#
.SYNOPSIS
    all_in_one_git_push_commit.ps1 is an Enterprise-grade Git automation script with pre-commit integration.

.DESCRIPTION
    PowerShell-native implementation of complete Git workflow automation.
    Designed by Jeffrey Snover's architectural principles for maximum reliability.

.PARAMETER CommitMessage
    The commit message to use. Defaults to "chore: sync commit".

.PARAMETER RefactorBranch
    The refactor branch to rebase and push. Defaults to "daz/refactor-20250825-1853".

.PARAMETER EnsureDocsKeep
    Ensures .gitkeep file exists in blueprint/docs_in directory.

.PARAMETER EnsureReadmeBadge
    Adds workflow badge to README.md if missing.

.PARAMETER AutoupdateHooks
    Runs pre-commit autoupdate before processing.

.PARAMETER OpenPR
    Opens pull request compare page in browser.

.PARAMETER NoVerify
    Skips pre-commit hooks during commit.

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -CommitMessage "feat: new feature"

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -AutoupdateHooks -OpenPR

.NOTES
    Version: 2.0.0 - Jeffrey Snover Architecture
    Requires: PowerShell 5.1+, Git, Pre-commit (optional)
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(HelpMessage = "Commit message for the changes")]
    [ValidateNotNullOrEmpty()]
    [string]$CommitMessage = "chore: sync commit",

    [Parameter(HelpMessage = "Refactor branch to rebase and push")]
    [ValidateNotNullOrEmpty()]
    [string]$RefactorBranch = "daz/refactor-20250825-1853",

    [Parameter(HelpMessage = "Ensure .gitkeep file in docs directory")]
    [switch]$EnsureDocsKeep,

    [Parameter(HelpMessage = "Add workflow badge to README")]
    [switch]$EnsureReadmeBadge,

    [Parameter(HelpMessage = "Update pre-commit hooks before running")]
    [switch]$AutoupdateHooks,

    [Parameter(HelpMessage = "Open pull request page in browser")]
    [switch]$OpenPR,

    [Parameter(HelpMessage = "Skip pre-commit hooks during commit")]
    [switch]$NoVerify
)

# Jeffrey Snover's Principle: Consistent error handling
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

#region Jeffrey Snover's Enterprise-Grade Functions

function Invoke-GitCommand {
    <#
    .SYNOPSIS
        PowerShell-native Git command execution with proper error handling.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string]$Command,

        [Parameter()]
        [string[]]$Arguments = @(),

        [Parameter()]
        [switch]$IgnoreError,

        [Parameter()]
        [switch]$PassThru
    )

    $gitArgs = @($Command) + $Arguments
    Write-Verbose "Executing: git $($gitArgs -join ' ')"

    try {
        if ($PassThru) {
            $result = & git @gitArgs 2>&1
            if ($LASTEXITCODE -ne 0 -and -not $IgnoreError) {
                throw "Git command failed (Exit Code: $LASTEXITCODE): git $($gitArgs -join ' ')"
            }
            return $result
        }
        else {
            & git @gitArgs
            if ($LASTEXITCODE -ne 0 -and -not $IgnoreError) {
                throw "Git command failed (Exit Code: $LASTEXITCODE): git $($gitArgs -join ' ')"
            }
        }
    }
    catch {
        if (-not $IgnoreError) {
            Write-Error "Git operation failed: $($_.Exception.Message)" -ErrorAction Stop
        }
        Write-Warning "Git command failed but continuing: $($_.Exception.Message)"
    }
}

function Add-GitPathsIfExist {
    <#
    .SYNOPSIS
        Adds file paths to Git staging area if they exist.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Paths
    )

    foreach ($path in $Paths) {
        if (Test-Path -Path $path -PathType Leaf) {
            Write-Verbose "Adding existing file: $path"
            Invoke-GitCommand -Command 'add' -Arguments @($path)
        }
        else {
            Write-Verbose "Skipping non-existent file: $path"
        }
    }
}

function Get-GitRepositorySlug {
    <#
    .SYNOPSIS
        Extracts GitHub repository slug from remote origin URL.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    try {
        $remoteUrl = Invoke-GitCommand -Command 'config' -Arguments @('--get', 'remote.origin.url') -PassThru -IgnoreError
        if ([string]::IsNullOrWhiteSpace($remoteUrl)) {
            Write-Warning "No remote origin URL found"
            return ''
        }

        $url = $remoteUrl.Trim()
        if ($url -match 'github\.com[:/](.+?)(?:\.git)?$') {
            return $Matches[1]
        }

        Write-Warning "URL does not match GitHub pattern: $url"
        return ''
    }
    catch {
        Write-Warning "Failed to get repository slug: $($_.Exception.Message)"
        return ''
    }
}

function Set-ReadmeWorkflowBadge {
    <#
    .SYNOPSIS
        Adds GitHub Actions workflow badge to README.md if missing.
    #>
    [CmdletBinding()]
    param()

    $readmePath = 'README.md'
    if (-not (Test-Path -Path $readmePath)) {
        Write-Verbose "README.md not found, skipping badge addition"
        return
    }

    $repositorySlug = Get-GitRepositorySlug
    if ([string]::IsNullOrWhiteSpace($repositorySlug)) {
        Write-Warning "Cannot determine repository slug, skipping badge"
        return
    }

    $badgeMarkdown = "![Manifest Census & Diff](https://github.com/$repositorySlug/actions/workflows/manifest-ci.yml/badge.svg)"

    try {
        $readmeContent = Get-Content -Path $readmePath -Raw -ErrorAction Stop
        $escapedBadge = [regex]::Escape($badgeMarkdown)

        if ($readmeContent -notmatch $escapedBadge) {
            $updatedContent = "$readmeContent`n`n$badgeMarkdown`n"
            Set-Content -Path $readmePath -Value $updatedContent -Encoding UTF8 -ErrorAction Stop
            Write-Information "Added workflow badge to README.md" -InformationAction Continue
            Invoke-GitCommand -Command 'add' -Arguments @($readmePath)
        }
        else {
            Write-Verbose "Workflow badge already exists in README.md"
        }
    }
    catch {
        Write-Error "Failed to update README.md: $($_.Exception.Message)" -ErrorAction Continue
    }
}

function Set-DocumentationKeepFile {
    <#
    .SYNOPSIS
        Ensures .gitkeep file exists in documentation directory.
    #>
    [CmdletBinding()]
    param()

    $docsDirectory = 'blueprint/docs_in'
    $keepFilePath = Join-Path -Path $docsDirectory -ChildPath '.gitkeep'

    try {
        if (-not (Test-Path -Path $docsDirectory)) {
            Write-Verbose "Creating documentation directory: $docsDirectory"
            $null = New-Item -ItemType Directory -Path $docsDirectory -Force
        }

        if (-not (Test-Path -Path $keepFilePath)) {
            Write-Verbose "Creating .gitkeep file: $keepFilePath"
            Set-Content -Path $keepFilePath -Value '' -Encoding UTF8 -ErrorAction Stop
            Write-Information "Created $keepFilePath" -InformationAction Continue
            Invoke-GitCommand -Command 'add' -Arguments @($keepFilePath)
        }
        else {
            Write-Verbose ".gitkeep file already exists: $keepFilePath"
        }
    }
    catch {
        Write-Error "Failed to create documentation keep file: $($_.Exception.Message)" -ErrorAction Continue
    }
}

function Initialize-PythonVirtualEnvironment {
    <#
    .SYNOPSIS
        Detects and activates Python virtual environment using PowerShell best practices.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $virtualEnvPaths = @(
        '.venv\Scripts\Activate.ps1',
        'venv\Scripts\Activate.ps1',
        '.\.venv\Scripts\Activate.ps1'
    )

    foreach ($venvPath in $virtualEnvPaths) {
        if (Test-Path -Path $venvPath) {
            Write-Verbose "Found virtual environment activation script: $venvPath"
            try {
                # Jeffrey Snover's Principle: Proper PowerShell script execution
                . $venvPath
                Write-Information "Successfully activated virtual environment: $venvPath" -InformationAction Continue
                return $true
            }
            catch {
                Write-Warning "Failed to activate virtual environment $venvPath`: $($_.Exception.Message)"
            }
        }
    }

    Write-Verbose "No virtual environment found or activated"
    return $false
}

function Invoke-PreCommitHooks {
    <#
    .SYNOPSIS
        Executes pre-commit hooks with enterprise-grade error handling.
    #>
    [CmdletBinding()]
    param()

    Write-Information "Initializing pre-commit hook execution..." -InformationAction Continue

    # Activate virtual environment if available
    $venvActivated = Initialize-PythonVirtualEnvironment
    if ($venvActivated) {
        Write-Verbose "Virtual environment activated for pre-commit execution"
    }

    try {
        # Check if pre-commit is available
        $preCommitAvailable = Get-Command -Name 'pre-commit' -ErrorAction SilentlyContinue
        if (-not $preCommitAvailable) {
            Write-Warning "Pre-commit not found in PATH, skipping hook execution"
            return
        }

        Write-Information "Executing pre-commit hooks on all files..." -InformationAction Continue
        & pre-commit run --all-files

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Pre-commit hooks reported issues (Exit Code: $LASTEXITCODE) - continuing with commit process"
        }
        else {
            Write-Information "Pre-commit hooks completed successfully" -InformationAction Continue
        }
    }
    catch {
        Write-Warning "Pre-commit execution failed: $($_.Exception.Message) - continuing with commit process"
    }
}

#endregion

#region Main Execution Logic

# Jeffrey Snover's Principle: Clear execution flow
Write-Information "Starting Git automation workflow..." -InformationAction Continue

if ($EnsureReadmeBadge) {
    Set-ReadmeWorkflowBadge
}

if ($EnsureDocsKeep) {
    Set-DocumentationKeepFile
}

# Add standard configuration files if they exist
Add-GitPathsIfExist -Paths @('.gitattributes', '.pre-commit-config.yaml', 'tools/hook_block_docs.py')

# Handle pre-commit hook updates
if ($AutoupdateHooks) {
    try {
        Write-Information "Updating pre-commit hooks..." -InformationAction Continue
        & pre-commit autoupdate
        if ($LASTEXITCODE -eq 0) {
            Add-GitPathsIfExist -Paths @('.pre-commit-config.yaml')
            Write-Information "Pre-commit hooks updated successfully" -InformationAction Continue
        }
        else {
            Write-Warning "Pre-commit autoupdate failed (Exit Code: $LASTEXITCODE)"
        }
    }
    catch {
        Write-Warning "Pre-commit autoupdate failed: $($_.Exception.Message)"
    }
}

# Execute pre-commit hooks using Jeffrey Snover's architecture
Invoke-PreCommitHooks

# Stage all changes using PowerShell-native Git commands
Write-Information "Staging all changes..." -InformationAction Continue
Invoke-GitCommand -Command 'add' -Arguments @('-A')

# Jeffrey Snover's Principle: Intelligent commit logic
Write-Information "Preparing commit operation..." -InformationAction Continue

$stagedFiles = Invoke-GitCommand -Command 'diff' -Arguments @('--cached', '--name-only') -PassThru -IgnoreError
if ([string]::IsNullOrWhiteSpace($stagedFiles)) {
    Write-Information "No changes staged for commit - repository is up to date" -InformationAction Continue
}
else {
    Write-Information "Committing staged changes..." -InformationAction Continue

    # Build commit arguments
    $commitArgs = @('commit', '-m', $CommitMessage)
    if ($NoVerify) {
        $commitArgs += '--no-verify'
    }

    try {
        Invoke-GitCommand -Command $commitArgs[0] -Arguments $commitArgs[1..($commitArgs.Length - 1)]
        Write-Information "Commit completed successfully" -InformationAction Continue
    }
    catch {
        # Handle case where pre-commit hooks modified files
        Write-Warning "Initial commit failed, re-staging and retrying: $($_.Exception.Message)"

        Invoke-GitCommand -Command 'add' -Arguments @('-A')
        $restagedFiles = Invoke-GitCommand -Command 'diff' -Arguments @('--cached', '--name-only') -PassThru -IgnoreError

        if ([string]::IsNullOrWhiteSpace($restagedFiles)) {
            Write-Information "Pre-commit hooks left no changes to commit" -InformationAction Continue
        }
        else {
            try {
                Invoke-GitCommand -Command $commitArgs[0] -Arguments $commitArgs[1..($commitArgs.Length - 1)]
                Write-Information "Retry commit completed successfully" -InformationAction Continue
            }
            catch {
                Write-Error "Commit failed after retry. Please inspect the repository state manually." -ErrorAction Stop
            }
        }
    }
}


# Validate repository state using PowerShell-native commands
Write-Information "Validating repository state..." -InformationAction Continue

try {
    $commitsAhead = Invoke-GitCommand -Command 'rev-list' -Arguments @('--count', 'HEAD', '^origin/main') -PassThru -IgnoreError
    if ($commitsAhead -and [int]$commitsAhead -gt 0) {
        Write-Information "Repository is ahead of origin/main by $commitsAhead commits" -InformationAction Continue
    }
    else {
        $repositoryStatus = Invoke-GitCommand -Command 'status' -Arguments @('--porcelain=v1') -PassThru -IgnoreError
        if ([string]::IsNullOrWhiteSpace($repositoryStatus)) {
            Write-Information "Working tree is clean and synchronized" -InformationAction Continue
        }
        else {
            Write-Warning "Uncommitted changes detected, but proceeding with push operation"
        }
    }
}
catch {
    Write-Verbose "Repository state validation failed, proceeding with push: $($_.Exception.Message)"
}

# Push current branch using PowerShell-native Git commands
$currentBranch = Invoke-GitCommand -Command 'rev-parse' -Arguments @('--abbrev-ref', 'HEAD') -PassThru
$currentBranch = $currentBranch.Trim()

Write-Information "Pushing current branch '$currentBranch' to origin..." -InformationAction Continue
Invoke-GitCommand -Command 'push' -Arguments @('-u', 'origin', $currentBranch)

# Handle refactor branch operations
Write-Information "Processing refactor branch operations..." -InformationAction Continue
Invoke-GitCommand -Command 'fetch' -Arguments @('origin')

$refactorBranchExists = Invoke-GitCommand -Command 'show-ref' -Arguments @('--verify', "refs/heads/$RefactorBranch") -PassThru -IgnoreError
if ($refactorBranchExists) {
    Write-Information "Processing refactor branch: $RefactorBranch" -InformationAction Continue

    Invoke-GitCommand -Command 'checkout' -Arguments @($RefactorBranch)
    Invoke-GitCommand -Command 'rebase' -Arguments @('origin/main') -IgnoreError
    Invoke-GitCommand -Command 'push' -Arguments @('-f', '--set-upstream', 'origin', $RefactorBranch)
    Invoke-GitCommand -Command 'checkout' -Arguments @($currentBranch)
}
else {
    Write-Verbose "Refactor branch '$RefactorBranch' does not exist locally"
}

# Open pull request if requested
if ($OpenPR) {
    $repositorySlug = Get-GitRepositorySlug
    if ($repositorySlug) {
        $pullRequestUrl = "https://github.com/$repositorySlug/compare/main...$RefactorBranch"
        try {
            Start-Process -FilePath $pullRequestUrl
            Write-Information "Opened pull request compare page: $pullRequestUrl" -InformationAction Continue
        }
        catch {
            Write-Warning "Failed to open pull request page: $($_.Exception.Message)"
        }
    }
}

Write-Information "Git automation workflow completed successfully" -InformationAction Continue

#endregion
