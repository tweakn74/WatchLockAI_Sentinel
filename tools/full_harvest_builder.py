#!/usr/bin/env python3
"""
Full Harvest & Packaging v7.1 Builder
Deterministic, reproducible archive creation with comprehensive verification
"""
import os
import sys
import json
import hashlib
import zipfile
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple
import math

# Deterministic timestamp from environment
DETERMINISTIC_TIMESTAMP = int(os.environ.get('SOURCE_DATE_EPOCH', '1700000000'))

class FullHarvestBuilder:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.exclude_patterns = {
            '__pycache__', '*.pyc', '.git', '.DS_Store', 
            '*.tmp', '*.temp', '.pytest_cache', '.mypy_cache'
        }
        self.source_files: List[Path] = []
        self.everything_files: List[Path] = []
        self.file_manifest: Dict[str, Dict] = {}
        
    def should_exclude(self, path: Path) -> bool:
        """Determine if a file/directory should be excluded"""
        path_str = str(path)
        path_name = path.name
        
        # Exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if path_name.endswith(pattern[1:]):
                    return True
            elif pattern in path_str or pattern == path_name:
                return True
                
        # Exclude hidden files/dirs starting with .
        if path_name.startswith('.') and path_name not in ['.gitignore']:
            return True
            
        return False
        
    def enumerate_files(self) -> Tuple[List[Path], List[Path]]:
        """Build stable, sorted file lists for source-only and everything packages"""
        print(f"📁 Enumerating files from: {self.root_path}")
        
        all_files = []
        source_only_files = []
        
        # Walk the directory tree
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
            
            # Process files
            for file_name in files:
                file_path = root_path / file_name
                if self.should_exclude(file_path):
                    continue
                    
                # Get relative path for consistent sorting
                rel_path = file_path.relative_to(self.root_path)
                all_files.append(rel_path)
                
                # For source-only, exclude dist/** except new harvest files
                if not (str(rel_path).startswith('dist/') and 
                       not any(x in str(rel_path) for x in ['source_only_v7_1', 'everything_v7_1', 'FULL_HARVEST', 'SHA256SUMS'])):
                    source_only_files.append(rel_path)
                    
        # Sort deterministically by path string
        all_files.sort(key=str)
        source_only_files.sort(key=str)
        
        print(f"📊 Enumerated {len(source_only_files)} source-only files, {len(all_files)} total files")
        return source_only_files, all_files
        
    def calculate_file_hash(self, file_path: Path) -> Tuple[str, int]:
        """Calculate SHA256 hash and size for a file"""
        hasher = hashlib.sha256()
        size = 0
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
                size += len(chunk)
                
        return hasher.hexdigest(), size
        
    def build_manifest(self, file_list: List[Path]) -> Dict:
        """Build comprehensive file manifest with hashes and metadata"""
        manifest = {
            'timestamp_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            'deterministic_epoch': DETERMINISTIC_TIMESTAMP,
            'total_files': len(file_list),
            'files': {}
        }
        
        total_size = 0
        for rel_path in file_list:
            full_path = self.root_path / rel_path
            try:
                sha256, size = self.calculate_file_hash(full_path)
                manifest['files'][str(rel_path)] = {
                    'size': size,
                    'sha256': sha256
                }
                total_size += size
            except Exception as e:
                print(f"⚠️  Error processing {rel_path}: {e}")
                
        manifest['total_size_bytes'] = total_size
        manifest['total_size_mb'] = round(total_size / 1024 / 1024, 2)
        return manifest
        
    def create_deterministic_zip(self, file_list: List[Path], output_path: Path, description: str) -> str:
        """Create deterministic ZIP archive with sorted entries"""
        print(f"📦 Creating {description}: {output_path}")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for rel_path in file_list:
                full_path = self.root_path / rel_path
                if full_path.exists():
                    # Use forward slashes in ZIP entries
                    arc_name = str(rel_path).replace('\\', '/')
                    
                    # Set deterministic timestamp
                    zinfo = zipfile.ZipInfo(filename=arc_name)
                    zinfo.date_time = time.gmtime(DETERMINISTIC_TIMESTAMP)[:6]
                    
                    with open(full_path, 'rb') as src:
                        zf.writestr(zinfo, src.read())
                        
        # Calculate final archive hash
        sha256, size = self.calculate_file_hash(output_path)
        print(f"✅ {description} complete: {size:,} bytes, SHA256={sha256[:16]}...")
        return sha256
        
    def split_large_zip(self, zip_path: Path, max_size_gb: float = 1.0) -> Dict:
        """Split large ZIP into parts if needed"""
        max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
        zip_size = zip_path.stat().st_size
        
        if zip_size <= max_size_bytes:
            print(f"📏 {zip_path.name} ({zip_size:,} bytes) is within size limit")
            return {'parts': 0, 'index': None}
            
        print(f"✂️  Splitting {zip_path.name} ({zip_size:,} bytes) into ≤{max_size_gb}GB parts")
        
        parts_info = {
            'original_file': str(zip_path.name),
            'original_size': zip_size,
            'part_size_limit': max_size_bytes,
            'parts': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        }
        
        part_num = 1
        with open(zip_path, 'rb') as src:
            while True:
                part_path = zip_path.with_suffix(f'{zip_path.suffix}.part{part_num:03d}')
                chunk = src.read(max_size_bytes)
                if not chunk:
                    break
                    
                with open(part_path, 'wb') as part_file:
                    part_file.write(chunk)
                    
                sha256, size = self.calculate_file_hash(part_path)
                parts_info['parts'].append({
                    'part_number': part_num,
                    'filename': part_path.name,
                    'size': size,
                    'sha256': sha256
                })
                
                print(f"  📦 Part {part_num}: {part_path.name} ({size:,} bytes)")
                part_num += 1
                
        # Write parts index
        index_path = zip_path.with_suffix(f'{zip_path.suffix}.parts.json')
        with open(index_path, 'w') as f:
            json.dump(parts_info, f, indent=2)
            
        parts_info['total_parts'] = len(parts_info['parts'])
        print(f"✅ Split into {parts_info['total_parts']} parts, index: {index_path.name}")
        return {'parts': parts_info['total_parts'], 'index': str(index_path.name)}

if __name__ == "__main__":
    builder = FullHarvestBuilder()
    
    print("🚀 Full Harvest & Packaging v7.1 Builder")
    print("=" * 50)
    
    # Step 1: Enumerate files
    source_files, everything_files = builder.enumerate_files()
    
    # Step 2: Build manifests  
    print("\n📋 Building file manifests...")
    source_manifest = builder.build_manifest(source_files)
    everything_manifest = builder.build_manifest(everything_files)
    
    # Create output directory
    dist_path = builder.root_path / "dist"
    dist_path.mkdir(exist_ok=True)
    
    print(f"\n📦 Creating archives in: {dist_path}")
    
    # Step 3: Create source-only package
    source_zip_path = dist_path / "source_only_v7_1.zip"
    source_hash = builder.create_deterministic_zip(source_files, source_zip_path, "source-only package")
    
    # Step 4: Create everything package  
    everything_zip_path = dist_path / "everything_v7_1.zip"
    everything_hash = builder.create_deterministic_zip(everything_files, everything_zip_path, "everything package")
    
    # Step 5: Handle large file splitting
    split_info = builder.split_large_zip(everything_zip_path)
    
    # Step 6: Generate comprehensive manifest
    full_manifest = {
        'harvest_version': 'v7.1',
        'build_timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        'deterministic_epoch': DETERMINISTIC_TIMESTAMP,
        'source_package': {
            'filename': source_zip_path.name,
            'sha256': source_hash,
            'size': source_zip_path.stat().st_size,
            'files_count': len(source_files)
        },
        'everything_package': {
            'filename': everything_zip_path.name,
            'sha256': everything_hash,
            'size': everything_zip_path.stat().st_size,
            'files_count': len(everything_files),
            'split_info': split_info
        },
        'file_manifests': {
            'source_only': source_manifest,
            'everything': everything_manifest
        }
    }
    
    # Write full manifest
    manifest_path = dist_path / "FULL_HARVEST_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(full_manifest, f, indent=2)
        
    print(f"\n✅ Full harvest packaging complete!")
    print(f"📄 Manifest: {manifest_path}")
    print(f"📦 Source package: {source_zip_path.name} ({source_zip_path.stat().st_size:,} bytes)")
    print(f"📦 Everything package: {everything_zip_path.name} ({everything_zip_path.stat().st_size:,} bytes)")
    if split_info['parts'] > 0:
        print(f"✂️  Split into {split_info['parts']} parts")
        
    # Export file lists for other tools
    builder.source_files = source_files
    builder.everything_files = everything_files
    builder.file_manifest = full_manifest
    
    print("\n🎯 Ready for verification and proof generation!")