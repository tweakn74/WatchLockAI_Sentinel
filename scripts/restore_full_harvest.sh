#!/bin/bash
# Full Harvest v7.1 Restoration Script (Bash)
# Verifies and extracts both source-only and everything packages

set -euo pipefail

# Default values
TARGET_DIR="WatchLockAI_Sentinel_Restored"
DIST_DIR="./dist"
SOURCE_ONLY=false
EVERYTHING=false
VERIFY=true

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -t, --target DIR     Target directory (default: $TARGET_DIR)"
    echo "  -d, --dist DIR       Distribution directory (default: $DIST_DIR)"
    echo "  -s, --source-only    Restore only source package"
    echo "  -e, --everything     Restore only everything package"
    echo "  --no-verify          Skip SHA256 verification"
    echo "  -h, --help           Show this help message"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            TARGET_DIR="$2"
            shift 2
            ;;
        -d|--dist)
            DIST_DIR="$2"
            shift 2
            ;;
        -s|--source-only)
            SOURCE_ONLY=true
            shift
            ;;
        -e|--everything)
            EVERYTHING=true
            shift
            ;;
        --no-verify)
            VERIFY=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

echo -e "${CYAN}[U+1F527] Full Harvest v7.1 Restoration Script${NC}"
echo -e "${CYAN}=============================================${NC}"

# Function to calculate SHA256
calculate_sha256() {
    local file="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$file" | cut -d' ' -f1
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$file" | cut -d' ' -f1
    else
        echo "[FAIL] No SHA256 utility found (sha256sum or shasum required)" >&2
        return 1
    fi
}

# Function to verify SHA256SUMS
verify_sha256sums() {
    local dist_path="$1"
    local sha256sums_file="$dist_path/SHA256SUMS"
    
    if [[ ! -f "$sha256sums_file" ]]; then
        echo -e "${RED}[FAIL] SHA256SUMS file not found: $sha256sums_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}[SEARCH] Verifying SHA256SUMS...${NC}"
    local all_valid=true
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^([a-f0-9]{64})[[:space:]]+(.+)$ ]]; then
            local expected_hash="${BASH_REMATCH[1]}"
            local file_name="${BASH_REMATCH[2]}"
            local file_path="$dist_path/$file_name"
            
            if [[ -f "$file_path" ]]; then
                local actual_hash
                actual_hash=$(calculate_sha256 "$file_path")
                if [[ "$actual_hash" == "$expected_hash" ]]; then
                    echo -e "  ${GREEN}[PASS] $file_name${NC}"
                else
                    echo -e "  ${RED}[FAIL] $file_name (hash mismatch)${NC}"
                    all_valid=false
                fi
            else
                echo -e "  ${RED}[FAIL] $file_name (file not found)${NC}"
                all_valid=false
            fi
        fi
    done < "$sha256sums_file"
    
    [[ "$all_valid" == true ]]
}

# Function to reassemble parts (if any exist)
reassemble_split_archive() {
    local base_name="$1"
    local dist_path="$2"
    local parts_index_file="$dist_path/${base_name}.parts.json"
    
    if [[ ! -f "$parts_index_file" ]]; then
        # No parts to reassemble
        return 0
    fi
    
    echo -e "${YELLOW}[U+1F527] Reassembling split archive: $base_name${NC}"
    
    # Extract original filename from JSON (simple parsing)
    local original_file
    original_file=$(grep -o '"original_file": "[^"]*"' "$parts_index_file" | cut -d'"' -f4)
    local output_file="$dist_path/$original_file"
    
    # Remove existing file if it exists
    [[ -f "$output_file" ]] && rm -f "$output_file"
    
    # Get part filenames (simple JSON parsing)
    local part_files
    part_files=$(grep -o '"filename": "[^"]*"' "$parts_index_file" | cut -d'"' -f4)
    
    local part_num=1
    for part_file in $part_files; do
        local part_path="$dist_path/$part_file"
        if [[ ! -f "$part_path" ]]; then
            echo -e "  ${RED}[FAIL] Part not found: $part_file${NC}"
            return 1
        fi
        
        # Append to output file
        cat "$part_path" >> "$output_file"
        echo -e "  ${GREEN}[PASS] Part $part_num: $part_file${NC}"
        ((part_num++))
    done
    
    local total_size
    total_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
    echo -e "  ${GREEN}[PASS] Reassembled: $base_name ($total_size bytes)${NC}"
    return 0
}

# Function to extract archive and count contents
extract_harvest_archive() {
    local archive_path="$1"
    local destination_path="$2"
    local package_type="$3"
    
    echo -e "${YELLOW}[PKG] Extracting $package_type package...${NC}"
    echo -e "  ${GRAY}Source: $archive_path${NC}"
    echo -e "  ${GRAY}Target: $destination_path${NC}"
    
    if [[ ! -f "$archive_path" ]]; then
        echo -e "  ${RED}[FAIL] Archive not found: $archive_path${NC}"
        return 1
    fi
    
    # Create destination directory
    [[ -d "$destination_path" ]] && rm -rf "$destination_path"
    mkdir -p "$destination_path"
    
    # Extract archive
    if unzip -q "$archive_path" -d "$destination_path"; then
        # Count extracted files and calculate total size
        local file_count
        local total_bytes
        file_count=$(find "$destination_path" -type f | wc -l)
        total_bytes=$(find "$destination_path" -type f -exec stat -f%z {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || \
                     find "$destination_path" -type f -exec stat -c%s {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
        
        echo -e "  ${GREEN}[PASS] Extracted $file_count files ($total_bytes bytes)${NC}"
        echo "$file_count:$total_bytes"
        return 0
    else
        echo -e "  ${RED}[FAIL] Extraction failed${NC}"
        return 1
    fi
}

# Main restoration logic
main() {
    # Resolve paths
    DIST_DIR=$(realpath "$DIST_DIR")
    echo -e "${GRAY}[U+1F4C1] Distribution directory: $DIST_DIR${NC}"
    
    if [[ ! -d "$DIST_DIR" ]]; then
        echo -e "${RED}[FAIL] Distribution directory not found: $DIST_DIR${NC}"
        exit 1
    fi
    
    # Verify SHA256SUMS if requested
    if [[ "$VERIFY" == true ]]; then
        if ! verify_sha256sums "$DIST_DIR"; then
            echo -e "${RED}[FAIL] SHA256 verification failed!${NC}"
            exit 1
        fi
        echo -e "${GREEN}[PASS] SHA256 verification passed!${NC}"
    fi
    
    # Determine which packages to restore
    local restore_source=false
    local restore_everything=false
    
    if [[ "$SOURCE_ONLY" == true ]]; then
        restore_source=true
    elif [[ "$EVERYTHING" == true ]]; then
        restore_everything=true
    else
        # Default: restore both
        restore_source=true
        restore_everything=true
    fi
    
    local total_file_count=0
    local total_bytes=0
    
    # Restore source-only package
    if [[ "$restore_source" == true ]]; then
        local source_archive="$DIST_DIR/source_only_v7_1.zip"
        local source_target="${TARGET_DIR}_source_only"
        
        # Check for split archive parts
        reassemble_split_archive "source_only_v7_1.zip" "$DIST_DIR" || exit 1
        
        local result
        result=$(extract_harvest_archive "$source_archive" "$source_target" "source-only")
        if [[ $? -eq 0 ]]; then
            local file_count=${result%:*}
            local bytes=${result#*:}
            total_file_count=$((total_file_count + file_count))
            total_bytes=$((total_bytes + bytes))
        else
            echo -e "${RED}[FAIL] Source-only extraction failed${NC}"
            exit 1
        fi
    fi
    
    # Restore everything package
    if [[ "$restore_everything" == true ]]; then
        local everything_archive="$DIST_DIR/everything_v7_1.zip"
        local everything_target="${TARGET_DIR}_everything"
        
        # Check for split archive parts
        reassemble_split_archive "everything_v7_1.zip" "$DIST_DIR" || exit 1
        
        local result
        result=$(extract_harvest_archive "$everything_archive" "$everything_target" "everything")
        if [[ $? -eq 0 ]]; then
            local file_count=${result%:*}
            local bytes=${result#*:}
            total_file_count=$((total_file_count + file_count))
            total_bytes=$((total_bytes + bytes))
        else
            echo -e "${RED}[FAIL] Everything extraction failed${NC}"
            exit 1
        fi
    fi
    
    # Success summary
    echo ""
    echo -e "${CYAN}=============================================${NC}"
    echo -e "${GREEN}[PASS] RESTORATION COMPLETE${NC}"
    printf "   Files restored: %'d\n" "$total_file_count"
    printf "   Total bytes: %'d\n" "$total_bytes"
    echo -e "   Target directories created"
    [[ "$restore_source" == true ]] && echo -e "     ${GRAY}- ${TARGET_DIR}_source_only${NC}"
    [[ "$restore_everything" == true ]] && echo -e "     ${GRAY}- ${TARGET_DIR}_everything${NC}"
    echo -e "${GREEN}[U+1F7E2] OK - Full Harvest v7.1 restoration successful!${NC}"
    echo -e "${CYAN}=============================================${NC}"
    
    exit 0
}

# Run main function
main "$@"