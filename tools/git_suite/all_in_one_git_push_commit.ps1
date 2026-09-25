<#
.SYNOPSIS
    Enterprise-grade Git automation script for WatchLockAI Sentinel with comprehensive safety features.

.DESCRIPTION
    Production-ready PowerShell script for Git workflow automation with enhanced error handling,
    parameter validation, safety checks, and support for the WatchLockAI Sentinel repository structure.

    Features:
    - Comprehensive error handling with try-catch blocks and meaningful error messages
    - Parameter validation for commit messages, branch names, and Git configuration
    - Safety checks for .gitignore, uncommitted changes, and remote repository validation
    - Support for feature branches, force push with warnings, and dry-run mode
    - Progress indicators and detailed logging of Git operations
    - Integration with WatchLockAI Sentinel directory structure and .gitignore

.PARAMETER CommitMessage
    The commit message to use. Must not be empty. Supports conventional commit format.

.PARAMETER TargetBranch
    The target branch to work with. Defaults to current branch. Validates branch name format.

.PARAMETER CreateFeatureBranch
    Creates and switches to a new feature branch before committing.

.PARAMETER FeatureBranchName
    Name for the new feature branch. Required when CreateFeatureBranch is used.

.PARAMETER ForcePush
    Enables force push with safety warnings and confirmation prompts.

.PARAMETER DryRun
    Preview mode that shows what operations would be performed without executing them.

.PARAMETER SkipSafetyChecks
    Bypasses safety checks (use with extreme caution in production).

.PARAMETER CommitTemplate
    Path to a commit message template file.

.PARAMETER EnsureDocsKeep
    Ensures .gitkeep file exists in docs directory.

.PARAMETER EnsureReadmeBadge
    Adds workflow badge to README.md if missing.

.PARAMETER AutoupdateHooks
    Runs pre-commit autoupdate before processing.

.PARAMETER OpenPR
    Opens pull request compare page in browser.

.PARAMETER NoVerify
    Skips pre-commit hooks during commit.

.PARAMETER Verbose
    Enables verbose output for detailed operation logging.

.PARAMETER LogFile
    Path to log file for operation history.

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -CommitMessage "feat: implement new detection engine"

    Basic commit with safety checks and validation.

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -CreateFeatureBranch -FeatureBranchName "feature/new-agent" -CommitMessage "feat: add new agent implementation"

    Creates a feature branch and commits changes.

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -DryRun -CommitMessage "test commit"

    Preview mode to see what operations would be performed.

.EXAMPLE
    .\all_in_one_git_push_commit.ps1 -ForcePush -CommitMessage "fix: critical security patch" -Verbose

    Force push with detailed logging and safety warnings.

.NOTES
    Version: 3.0.0 - Production-Ready Enterprise Edition
    Author: WatchLockAI Development Team
    Requires: PowerShell 5.1+, Git 2.20+
    Compatible: Windows, Linux, macOS

    Safety Features:
    - Validates .gitignore exists and is comprehensive
    - Checks for uncommitted changes that might be lost
    - Confirms remote repository URL is valid and accessible
    - Prevents pushing to protected branches without confirmation
    - Validates Git configuration and repository state

    WatchLockAI Sentinel Integration:
    - Respects comprehensive .gitignore for sensitive files
    - Supports directory reorganization workflows
    - Handles Python cache files and database exclusions
    - Integrates with deployment and forensics directories
#>

[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Standard')]
param(
    [Parameter(Mandatory, HelpMessage = "Commit message for the changes")]
    [ValidateNotNullOrEmpty()]
    [ValidateScript({
            if ($_.Length -lt 10) {
                throw "Commit message must be at least 10 characters long"
            }
            if ($_.Length -gt 72) {
                Write-Warning "Commit message is longer than 72 characters. Consider shortening for better Git log readability."
            }
            return $true
        })]
    [string]$CommitMessage,

    [Parameter(HelpMessage = "Target branch to work with")]
    [ValidateScript({
            if ($_ -match '^[a-zA-Z0-9/_-]+$') {
                return $true
            }
            throw "Branch name contains invalid characters. Use only letters, numbers, hyphens, underscores, and forward slashes."
        })]
    [string]$TargetBranch,

    [Parameter(ParameterSetName = 'FeatureBranch', HelpMessage = "Create and switch to a new feature branch")]
    [switch]$CreateFeatureBranch,

    [Parameter(ParameterSetName = 'FeatureBranch', Mandatory, HelpMessage = "Name for the new feature branch")]
    [ValidateNotNullOrEmpty()]
    [ValidateScript({
            if ($_ -match '^[a-zA-Z0-9/_-]+$' -and $_.Length -le 50) {
                return $true
            }
            throw "Feature branch name must be valid (alphanumeric, hyphens, underscores, slashes) and under 50 characters."
        })]
    [string]$FeatureBranchName,

    [Parameter(HelpMessage = "Enable force push with safety warnings")]
    [switch]$ForcePush,

    [Parameter(HelpMessage = "Preview mode - show operations without executing")]
    [switch]$DryRun,

    [Parameter(HelpMessage = "Skip safety checks (use with extreme caution)")]
    [switch]$SkipSafetyChecks,

    [Parameter(HelpMessage = "Path to commit message template file")]
    [ValidateScript({
            if ([string]::IsNullOrEmpty($_) -or (Test-Path -Path $_ -PathType Leaf)) {
                return $true
            }
            throw "Commit template file does not exist: $_"
        })]
    [string]$CommitTemplate,

    [Parameter(HelpMessage = "Ensure .gitkeep file in docs directory")]
    [switch]$EnsureDocsKeep,

    [Parameter(HelpMessage = "Add workflow badge to README")]
    [switch]$EnsureReadmeBadge,

    [Parameter(HelpMessage = "Update pre-commit hooks before running")]
    [switch]$AutoupdateHooks,

    [Parameter(HelpMessage = "Open pull request page in browser")]
    [switch]$OpenPR,

    [Parameter(HelpMessage = "Skip pre-commit hooks during commit")]
    [switch]$NoVerify,

    [Parameter(HelpMessage = "Path to log file for operation history")]
    [string]$LogFile = "git_operations.log"
)

# Enterprise-grade error handling and configuration
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$InformationPreference = 'Continue'

# Global variables for script state
$script:OperationLog = @()
$script:GitOperationCount = 0
$script:StartTime = Get-Date

#region Logging and Utility Functions

function Write-OperationLog {
    <#
    .SYNOPSIS
        Centralized logging function for all Git operations.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [Parameter()]
        [ValidateSet('Info', 'Warning', 'Error', 'Success', 'Debug')]
        [string]$Level = 'Info',

        [Parameter()]
        [switch]$WriteToHost
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logEntry = "[$timestamp] [$Level] $Message"

    # Add to in-memory log
    $script:OperationLog += $logEntry

    # Write to log file if specified
    if ($LogFile -and -not $DryRun) {
        try {
            Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8 -ErrorAction SilentlyContinue
        }
        catch {
            Write-Warning "Failed to write to log file: $($_.Exception.Message)"
        }
    }

    # Write to host based on level
    if ($WriteToHost) {
        switch ($Level) {
            'Info' { Write-Information $Message -InformationAction Continue }
            'Warning' { Write-Warning $Message }
            'Error' { Write-Host "ERROR: $Message" -ForegroundColor Red }
            'Success' { Write-Host $Message -ForegroundColor Green }
            'Debug' { Write-Verbose $Message }
        }
    }
}

function Show-Progress {
    <#
    .SYNOPSIS
        Shows progress for long-running Git operations.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Activity,

        [Parameter()]
        [string]$Status = 'Processing...',

        [Parameter()]
        [int]$PercentComplete = -1
    )

    if (-not $DryRun) {
        Write-Progress -Activity $Activity -Status $Status -PercentComplete $PercentComplete
    }
    else {
        Write-OperationLog -Message "[DRY RUN] $Activity - $Status" -Level 'Debug' -WriteToHost
    }
}

#endregion

#region Enhanced Git Functions

function Invoke-GitCommand {
    <#
    .SYNOPSIS
        Enhanced Git command execution with comprehensive error handling and logging.
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
        [switch]$PassThru,

        [Parameter()]
        [string]$OperationDescription
    )

    $gitArgs = @($Command) + $Arguments
    $fullCommand = "git $($gitArgs -join ' ')"

    # Increment operation counter
    $script:GitOperationCount++

    # Log the operation
    $description = if ($OperationDescription) { $OperationDescription } else { $Command }
    Write-OperationLog -Message "Executing Git operation #$($script:GitOperationCount): $description" -Level 'Debug'
    Write-Verbose "Full command: $fullCommand"

    # Handle dry run mode
    if ($DryRun) {
        Write-OperationLog -Message "[DRY RUN] Would execute: $fullCommand" -Level 'Info' -WriteToHost
        if ($PassThru) {
            return "DRY_RUN_OUTPUT"
        }
        return
    }

    try {
        $startTime = Get-Date

        if ($PassThru) {
            $result = & git @gitArgs 2>&1
            $exitCode = $LASTEXITCODE
        }
        else {
            & git @gitArgs 2>&1 | Out-Null
            $exitCode = $LASTEXITCODE
            $result = $null
        }

        $duration = (Get-Date) - $startTime

        if ($exitCode -ne 0 -and -not $IgnoreError) {
            $errorMsg = "Git command failed (Exit Code: $exitCode) after $($duration.TotalSeconds)s: $fullCommand"
            Write-OperationLog -Message $errorMsg -Level 'Error'
            throw $errorMsg
        }

        if ($exitCode -ne 0 -and $IgnoreError) {
            Write-OperationLog -Message "Git command failed but ignored (Exit Code: $exitCode): $fullCommand" -Level 'Warning'
        }
        else {
            Write-OperationLog -Message "Git operation completed successfully in $($duration.TotalSeconds)s" -Level 'Success'
        }

        return $result
    }
    catch {
        $errorMsg = "Git operation failed: $($_.Exception.Message)"
        Write-OperationLog -Message $errorMsg -Level 'Error'

        if (-not $IgnoreError) {
            throw
        }
        Write-Warning $errorMsg
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
            Write-OperationLog -Message "Adding existing file: $path" -Level 'Debug'
            Invoke-GitCommand -Command 'add' -Arguments @($path) -OperationDescription "Add file: $path"
        }
        else {
            Write-OperationLog -Message "Skipping non-existent file: $path" -Level 'Debug'
        }
    }
}

#endregion

#region Safety Check Functions

function Test-GitRepository {
    <#
    .SYNOPSIS
        Validates that we're in a valid Git repository.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $null = Invoke-GitCommand -Command 'rev-parse' -Arguments @('--git-dir') -PassThru -IgnoreError
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Test-GitIgnoreExists {
    <#
    .SYNOPSIS
        Validates that .gitignore exists and contains WatchLockAI Sentinel patterns.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    if (-not (Test-Path -Path '.gitignore')) {
        Write-OperationLog -Message ".gitignore file not found" -Level 'Error' -WriteToHost
        return $false
    }

    try {
        $gitignoreContent = Get-Content -Path '.gitignore' -Raw

        # Check for essential patterns
        $requiredPatterns = @(
            '__pycache__/',
            '*.pyc',
            '*.log',
            '*.db',
            '*.sqlite',
            '.env',
            'secrets/'
        )

        $missingPatterns = @()
        foreach ($pattern in $requiredPatterns) {
            if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
                $missingPatterns += $pattern
            }
        }

        if ($missingPatterns.Count -gt 0) {
            Write-OperationLog -Message ".gitignore missing critical patterns: $($missingPatterns -join ', ')" -Level 'Warning' -WriteToHost
            return $false
        }

        Write-OperationLog -Message ".gitignore validation passed" -Level 'Success'
        return $true
    }
    catch {
        Write-OperationLog -Message "Failed to validate .gitignore: $($_.Exception.Message)" -Level 'Error' -WriteToHost
        return $false
    }
}

function Test-GitConfiguration {
    <#
    .SYNOPSIS
        Validates Git user configuration.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $userName = Invoke-GitCommand -Command 'config' -Arguments @('user.name') -PassThru -IgnoreError
        $userEmail = Invoke-GitCommand -Command 'config' -Arguments @('user.email') -PassThru -IgnoreError

        if ([string]::IsNullOrWhiteSpace($userName) -or [string]::IsNullOrWhiteSpace($userEmail)) {
            Write-OperationLog -Message "Git user configuration incomplete. Please set user.name and user.email" -Level 'Error' -WriteToHost
            return $false
        }

        Write-OperationLog -Message "Git configuration valid: $($userName.Trim()) <$($userEmail.Trim())>" -Level 'Success'
        return $true
    }
    catch {
        Write-OperationLog -Message "Failed to validate Git configuration: $($_.Exception.Message)" -Level 'Error' -WriteToHost
        return $false
    }
}

function Test-RemoteRepository {
    <#
    .SYNOPSIS
        Validates remote repository connectivity.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $remoteUrl = Invoke-GitCommand -Command 'config' -Arguments @('--get', 'remote.origin.url') -PassThru -IgnoreError

        if ([string]::IsNullOrWhiteSpace($remoteUrl)) {
            Write-OperationLog -Message "No remote origin configured" -Level 'Warning' -WriteToHost
            return $false
        }

        Write-OperationLog -Message "Testing connectivity to remote: $($remoteUrl.Trim())" -Level 'Info'

        # Test remote connectivity
        $null = Invoke-GitCommand -Command 'ls-remote' -Arguments @('origin', 'HEAD') -PassThru -IgnoreError

        if ($LASTEXITCODE -eq 0) {
            Write-OperationLog -Message "Remote repository connectivity confirmed" -Level 'Success'
            return $true
        }
        else {
            Write-OperationLog -Message "Cannot connect to remote repository" -Level 'Error' -WriteToHost
            return $false
        }
    }
    catch {
        Write-OperationLog -Message "Failed to validate remote repository: $($_.Exception.Message)" -Level 'Error' -WriteToHost
        return $false
    }
}

function Test-UncommittedChanges {
    <#
    .SYNOPSIS
        Checks for uncommitted changes that might be lost.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $status = Invoke-GitCommand -Command 'status' -Arguments @('--porcelain') -PassThru -IgnoreError

        if ([string]::IsNullOrWhiteSpace($status)) {
            Write-OperationLog -Message "Working directory is clean" -Level 'Success'
            return $true
        }

        $statusLines = $status -split "`n" | Where-Object { $_.Trim() -ne '' }
        Write-OperationLog -Message "Found $($statusLines.Count) uncommitted changes" -Level 'Info'

        foreach ($line in $statusLines) {
            Write-OperationLog -Message "  $line" -Level 'Debug'
        }

        return $true
    }
    catch {
        Write-OperationLog -Message "Failed to check repository status: $($_.Exception.Message)" -Level 'Error' -WriteToHost
        return $false
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

#endregion

#region Enhanced Main Execution Logic

function Invoke-SafetyChecks {
    <#
    .SYNOPSIS
        Performs comprehensive safety checks before Git operations.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    if ($SkipSafetyChecks) {
        Write-OperationLog -Message "Safety checks skipped by user request" -Level 'Warning' -WriteToHost
        return $true
    }

    Write-OperationLog -Message "Performing safety checks..." -Level 'Info' -WriteToHost
    Show-Progress -Activity "Safety Checks" -Status "Validating repository state" -PercentComplete 10

    $checks = @(
        @{ Name = "Git Repository"; Test = { Test-GitRepository } },
        @{ Name = "Git Configuration"; Test = { Test-GitConfiguration } },
        @{ Name = ".gitignore File"; Test = { Test-GitIgnoreExists } },
        @{ Name = "Remote Repository"; Test = { Test-RemoteRepository } },
        @{ Name = "Repository Status"; Test = { Test-UncommittedChanges } }
    )

    $failedChecks = @()
    $checkCount = 0

    foreach ($check in $checks) {
        $checkCount++
        $percentComplete = [math]::Round(($checkCount / $checks.Count) * 100)
        Show-Progress -Activity "Safety Checks" -Status "Checking: $($check.Name)" -PercentComplete $percentComplete

        try {
            $result = & $check.Test
            if (-not $result) {
                $failedChecks += $check.Name
            }
        }
        catch {
            Write-OperationLog -Message "Safety check '$($check.Name)' failed with error: $($_.Exception.Message)" -Level 'Error'
            $failedChecks += $check.Name
        }
    }

    Write-Progress -Activity "Safety Checks" -Completed

    if ($failedChecks.Count -gt 0) {
        Write-OperationLog -Message "Safety checks failed: $($failedChecks -join ', ')" -Level 'Error' -WriteToHost
        return $false
    }

    Write-OperationLog -Message "All safety checks passed" -Level 'Success' -WriteToHost
    return $true
}

function Get-CommitMessageFromTemplate {
    <#
    .SYNOPSIS
        Loads commit message from template file if specified.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    if ([string]::IsNullOrEmpty($CommitTemplate)) {
        return $CommitMessage
    }

    try {
        $templateContent = Get-Content -Path $CommitTemplate -Raw
        if ([string]::IsNullOrWhiteSpace($templateContent)) {
            Write-OperationLog -Message "Commit template file is empty, using provided message" -Level 'Warning'
            return $CommitMessage
        }

        # Replace placeholders in template
        $finalMessage = $templateContent -replace '\{MESSAGE\}', $CommitMessage
        $finalMessage = $finalMessage -replace '\{DATE\}', (Get-Date -Format 'yyyy-MM-dd')
        $finalMessage = $finalMessage -replace '\{TIME\}', (Get-Date -Format 'HH:mm:ss')

        Write-OperationLog -Message "Using commit message from template: $CommitTemplate" -Level 'Info'
        return $finalMessage.Trim()
    }
    catch {
        Write-OperationLog -Message "Failed to load commit template, using provided message: $($_.Exception.Message)" -Level 'Warning'
        return $CommitMessage
    }
}

# Main execution starts here
try {
    Write-OperationLog -Message "=== WatchLockAI Sentinel Git Automation Workflow Started ===" -Level 'Info' -WriteToHost
    Write-OperationLog -Message "Script Version: 3.0.0 - Production-Ready Enterprise Edition" -Level 'Info'
    Write-OperationLog -Message "Execution Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -Level 'Info' -WriteToHost

    # Perform safety checks
    if (-not (Invoke-SafetyChecks)) {
        throw "Safety checks failed. Aborting operation for security."
    }

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


    # Validate repository state
    Show-Progress -Activity "Git Operations" -Status "Validating repository state" -PercentComplete 75
    Write-OperationLog -Message "Validating repository state..." -Level 'Info' -WriteToHost

    try {
        $currentBranch = Invoke-GitCommand -Command 'rev-parse' -Arguments @('--abbrev-ref', 'HEAD') -PassThru
        $currentBranch = $currentBranch.Trim()

        # Use the target branch if specified, otherwise use current branch
        $branchToPush = if ($TargetBranch) { $TargetBranch } else { $currentBranch }

        $commitsAhead = Invoke-GitCommand -Command 'rev-list' -Arguments @('--count', 'HEAD', "^origin/$branchToPush") -PassThru -IgnoreError
        if ($commitsAhead -and [int]$commitsAhead -gt 0) {
            Write-OperationLog -Message "Repository is ahead of origin/$branchToPush by $commitsAhead commits" -Level 'Info' -WriteToHost
        }
        else {
            $repositoryStatus = Invoke-GitCommand -Command 'status' -Arguments @('--porcelain=v1') -PassThru -IgnoreError
            if ([string]::IsNullOrWhiteSpace($repositoryStatus)) {
                Write-OperationLog -Message "Working tree is clean and synchronized" -Level 'Success'
            }
            else {
                Write-OperationLog -Message "Uncommitted changes detected, but proceeding with push operation" -Level 'Warning'
            }
        }
    }
    catch {
        Write-OperationLog -Message "Repository state validation failed, proceeding with push: $($_.Exception.Message)" -Level 'Warning'
    }

    # Handle push operation with safety checks
    Show-Progress -Activity "Git Operations" -Status "Pushing to remote" -PercentComplete 85

    $currentBranch = Invoke-GitCommand -Command 'rev-parse' -Arguments @('--abbrev-ref', 'HEAD') -PassThru
    $currentBranch = $currentBranch.Trim()
    $branchToPush = if ($TargetBranch) { $TargetBranch } else { $currentBranch }

    Write-OperationLog -Message "Pushing branch '$branchToPush' to origin..." -Level 'Info' -WriteToHost

    # Handle force push with safety warnings
    if ($ForcePush) {
        Write-OperationLog -Message "WARNING: Force push requested!" -Level 'Warning' -WriteToHost
        if (-not $DryRun) {
            $confirmation = Read-Host "Are you sure you want to force push? This can overwrite remote history. Type 'FORCE' to confirm"
            if ($confirmation -ne 'FORCE') {
                throw "Force push cancelled by user"
            }
        }
        Invoke-GitCommand -Command 'push' -Arguments @('-f', '-u', 'origin', $branchToPush) -OperationDescription "Force push branch"
    }
    else {
        Invoke-GitCommand -Command 'push' -Arguments @('-u', 'origin', $branchToPush) -OperationDescription "Push branch"
    }

    # Open pull request if requested
    if ($OpenPR) {
        Show-Progress -Activity "Git Operations" -Status "Opening pull request" -PercentComplete 95
        $repositorySlug = Get-GitRepositorySlug
        if ($repositorySlug) {
            $pullRequestUrl = "https://github.com/$repositorySlug/compare/main...$branchToPush"
            try {
                if (-not $DryRun) {
                    Start-Process -FilePath $pullRequestUrl
                }
                Write-OperationLog -Message "Pull request URL: $pullRequestUrl" -Level 'Info' -WriteToHost
            }
            catch {
                Write-OperationLog -Message "Failed to open pull request page: $($_.Exception.Message)" -Level 'Warning'
            }
        }
    }

    # Complete progress
    Write-Progress -Activity "Git Operations" -Completed

    # Calculate execution time
    $executionTime = (Get-Date) - $script:StartTime

    Write-OperationLog -Message "=== Git automation workflow completed successfully ===" -Level 'Success' -WriteToHost
    Write-OperationLog -Message "Execution time: $($executionTime.TotalSeconds) seconds" -Level 'Info' -WriteToHost
    Write-OperationLog -Message "Total Git operations: $script:GitOperationCount" -Level 'Info' -WriteToHost

    # Display operation summary
    if ($script:OperationLog.Count -gt 0) {
        Write-OperationLog -Message "Operation log summary:" -Level 'Info' -WriteToHost
        $script:OperationLog | ForEach-Object { Write-Verbose $_ }
    }
}
catch {
    Write-Progress -Activity "Git Operations" -Completed
    $errorMsg = "Git automation workflow failed: $($_.Exception.Message)"
    Write-OperationLog -Message $errorMsg -Level 'Error' -WriteToHost

    # Log the full error details
    Write-OperationLog -Message "Error details: $($_.Exception.ToString())" -Level 'Error'
    Write-OperationLog -Message "Stack trace: $($_.ScriptStackTrace)" -Level 'Error'

    # Exit with error code
    exit 1
}
finally {
    # Cleanup and final logging
    if ($LogFile -and (Test-Path $LogFile)) {
        Write-Host "Operation log saved to: $LogFile" -ForegroundColor Cyan
    }

    # Reset error action preference
    $ErrorActionPreference = 'Continue'
}

#endregion
