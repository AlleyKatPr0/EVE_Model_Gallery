# -*- coding: utf-8 -*-
import zipfile
import sqlite3
import json
from pathlib import Path
from typing import Dict, Set, Optional, List, Tuple
import shutil
import hashlib
import re

class EVEDataInitializer:
    def __init__(self):
        self.sde_path = Path("sde")
        self.output_path = Path("docs") / "statics"
        self.icons_path = self.output_path / "icons"
        self.temp_icons_path = Path("icons_temp")
        self.models_path = Path("docs") / "models"
        self.extra_models_path = Path("docs") / "extra_models"
        
        # Clear output directory
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        
        # Create necessary directories
        self.output_path.mkdir(exist_ok=True)
        self.icons_path.mkdir(exist_ok=True, parents=True)
        
    def extract_zip_files(self):
        """Extract zip files from sde directory"""
        print("Extracting files...")
        
        # Extract icon files to temp directory
        icons_zip_path = self.sde_path / "icons.zip"
        if icons_zip_path.exists():
            if self.temp_icons_path.exists():
                shutil.rmtree(self.temp_icons_path)
            self.temp_icons_path.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(icons_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_icons_path)
            print(f"Icon files extracted")
        else:
            print(f"Warning: Icon file not found {icons_zip_path}")
        
        # Extract SDE files (database files in sde/db/)
        sde_zip_path = self.sde_path / "sde.zip"
        if sde_zip_path.exists():
            with zipfile.ZipFile(sde_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.sde_path)
            print(f"SDE files extracted")
        else:
            print(f"Warning: SDE file not found {sde_zip_path}")
    
    def connect_database(self, db_name: str) -> Optional[sqlite3.Connection]:
        """Connect to SQLite database"""
        db_file = self.sde_path / "db" / f"item_db_{db_name}.sqlite"
        if not db_file.exists():
            print(f"Error: Database file not found {db_file}")
            return None
            
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            print(f"{db_name.upper()} database connected successfully")
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    def load_data(self, conn: sqlite3.Connection, lang: str, extra_type_ids: list = None) -> Dict:
        """Load data for specified language (query categoryID 6 and 65, plus extra item IDs)"""
        print(f"Loading {lang.upper()} data...")
        
        if extra_type_ids is None:
            extra_type_ids = []
        
        # Build unified query template
        base_query = """
            SELECT 
                t.type_id,
                t.en_name,
                t.zh_name,
                t.categoryID,
                t.groupID,
                t.icon_filename,
                c.name as category_name,
                c.icon_filename AS category_icon_name,
                g.name as group_name,
                g.icon_filename AS group_icon_name
            FROM types t
            LEFT JOIN categories c ON t.categoryID = c.category_id
            LEFT JOIN groups g ON t.groupID = g.group_id
            WHERE {where_clause}
        """
        
        # Build WHERE clause and parameters
        if extra_type_ids:
            placeholders = ','.join(['?'] * len(extra_type_ids))
            where_clause = f"(t.categoryID IN (6, 65) AND t.published = 1) OR t.type_id IN ({placeholders})"
            cursor = conn.execute(base_query.format(where_clause=where_clause), extra_type_ids)
        else:
            where_clause = "t.categoryID IN (6, 65) AND t.published = 1"
            cursor = conn.execute(base_query.format(where_clause=where_clause))
        categories = {}
        groups = {}
        types = {}
        icon_names = set()
        
        # Select name field based on language
        name_field = 'zh_name' if lang == 'zh' else 'en_name'
        
        for row in cursor:
            type_id = row['type_id']
            category_id = row['categoryID']
            group_id = row['groupID']
            
            # Collect type info (save both Chinese and English names)
            types[type_id] = {
                'id': type_id,
                'name': row[name_field] or row['en_name'],
                'name_en': row['en_name'] or '',
                'name_zh': row['zh_name'] or '',
                'categoryID': category_id,
                'groupID': group_id,
                'icon_name': row['icon_filename']
            }
            # Collect type icon names
            if row['icon_filename']:
                icon_names.add(row['icon_filename'])
            
            # Collect category info
            if category_id and category_id not in categories:
                categories[category_id] = {
                    'id': category_id,
                    'name': row['category_name'] or '',
                    'icon_name': row['category_icon_name']
                }
                if row['category_icon_name']:
                    icon_names.add(row['category_icon_name'])
            
            # Collect group info
            if group_id and group_id not in groups:
                groups[group_id] = {
                    'id': group_id,
                    'name': row['group_name'] or '',
                    'categoryID': category_id,
                    'icon_name': row['group_icon_name']
                }
                if row['group_icon_name']:
                    icon_names.add(row['group_icon_name'])
        
        # Output stats for extra item IDs if present
        if extra_type_ids:
            extra_found = [tid for tid in extra_type_ids if tid in types]
            if extra_found:
                print(f"  Found {len(extra_found)} items from extra IDs: {extra_found}")
            missing = [tid for tid in extra_type_ids if tid not in types]
            if missing:
                print(f"  Warning: {len(missing)} items not found from extra IDs: {missing}")
        
        print(f"  Loaded {len(types)} types, {len(categories)} categories, {len(groups)} groups")
        
        return {
            'categories': categories,
            'groups': groups,
            'types': types,
            'icon_names': icon_names
        }
    
    def _ensure_category_exists(self, category_map: Dict, category_id: int, categories: Dict) -> None:
        """Ensure category exists in map, create if not"""
        if category_id not in category_map:
            category_info = categories.get(category_id, {})
            category_map[category_id] = {
                'id': category_id,
                'name': category_info.get('name', f'Category {category_id}'),
                'icon_name': category_info.get('icon_name'),
                'groups': {}
            }
    
    def _ensure_group_exists(self, category_map: Dict, category_id: int, group_id: int, groups: Dict) -> None:
        """Ensure group exists in category, create if not"""
        if group_id not in category_map[category_id]['groups']:
            group_info = groups.get(group_id, {})
            category_map[category_id]['groups'][group_id] = {
                'id': group_id,
                'name': group_info.get('name', f'Group {group_id}'),
                'icon_name': group_info.get('icon_name'),
                'types': [],
                'is_t3_cruiser': (group_id == 963)
            }
    
    def build_category_tree(self, data: Dict, model_map: Dict[int, str] = None, all_file_info: List[Dict] = None) -> list:
        """Build category -> group -> type tree structure, with 4th layer variants for group 963"""
        categories = data['categories']
        groups = data['groups']
        types = data['types']
        
        if model_map is None:
            model_map = {}
        if all_file_info is None:
            all_file_info = []
        
        # Build variant list for each typeid (for group 963)
        typeid_variants = {}
        for file_info in all_file_info:
            typeid = file_info['typeid']
            if typeid not in typeid_variants:
                typeid_variants[typeid] = []
            typeid_variants[typeid].append({
                'variant': file_info.get('variant'),
                'model_path': file_info['relative_path'],
                'filename': file_info.get('filename', '')
            })
        
        # Build tree structure
        category_map = {}
        
        # Initialize all category nodes
        for category_id, category_info in categories.items():
            category_map[category_id] = {
                'id': category_id,
                'name': category_info['name'],
                'icon_name': category_info.get('icon_name'),
                'groups': {}
            }
        
        # Add groups to categories
        for group_id, group_info in groups.items():
            category_id = group_info.get('categoryID')
            if category_id:
                # Use helper method to ensure category exists
                self._ensure_category_exists(category_map, category_id, categories)
                # Add group to category
                category_map[category_id]['groups'][group_id] = {
                    'id': group_id,
                    'name': group_info['name'],
                    'icon_name': group_info.get('icon_name'),
                    'types': [],
                    'is_t3_cruiser': (group_id == 963)  # Mark T3 cruisers
                }
        
        # Add types to groups
        for type_id, type_info in types.items():
            category_id = type_info.get('categoryID')
            group_id = type_info.get('groupID')
            
            if category_id and group_id:
                # Use helper methods to ensure category and group exist
                self._ensure_category_exists(category_map, category_id, categories)
                self._ensure_group_exists(category_map, category_id, group_id, groups)
                
                # Check if this is group 963 (T3 cruiser)
                is_t3_cruiser = (group_id == 963)
                
                if is_t3_cruiser and type_id in typeid_variants:
                    # For T3 cruisers, build variant list
                    variants_list = []
                    default_model_path = None
                    
                    for variant_info in typeid_variants[type_id]:
                        variant_code = variant_info['variant']
                        # Build variant name
                        if variant_code:
                            variant_name = f"{type_info['name']}（{variant_code}）"
                            variant_name_en = f"{type_info.get('name_en', '')} ({variant_code})"
                            variant_name_zh = f"{type_info.get('name_zh', '')}（{variant_code}）"
                        else:
                            variant_name = type_info['name']
                            variant_name_en = type_info.get('name_en', '')
                            variant_name_zh = type_info.get('name_zh', '')
                            # Find file without variant value, use as default model
                            default_model_path = variant_info['model_path']
                        
                        variants_list.append({
                            'variant_code': variant_code or '',
                            'name': variant_name,
                            'name_en': variant_name_en,
                            'name_zh': variant_name_zh,
                            'model_path': variant_info['model_path']
                        })
                    
                    # Sort by variant code
                    variants_list.sort(key=lambda x: x['variant_code'])
                    
                    # If no default model without variant found, use first variant
                    if not default_model_path and variants_list:
                        default_model_path = variants_list[0]['model_path']
                    
                    # Add type with variants
                    category_map[category_id]['groups'][group_id]['types'].append({
                        'id': type_id,
                        'name': type_info['name'],
                        'name_en': type_info.get('name_en', ''),
                        'name_zh': type_info.get('name_zh', ''),
                        'icon_name': type_info.get('icon_name'),
                        'has_variants': True,
                        'model_path': default_model_path or '',
                        'variants': variants_list
                    })
                else:
                    # For regular items, use original logic
                    model_path = model_map.get(type_id, '')
                    
                    category_map[category_id]['groups'][group_id]['types'].append({
                        'id': type_id,
                        'name': type_info['name'],
                        'name_en': type_info.get('name_en', ''),
                        'name_zh': type_info.get('name_zh', ''),
                        'icon_name': type_info.get('icon_name'),
                        'has_variants': False,
                        'model_path': model_path
                    })
        
        # Convert to list and sort (sort by name)
        result = []
        for category in category_map.values():
            category['groups'] = list(category['groups'].values())
            category['groups'].sort(key=lambda x: x['name'])
            for group in category['groups']:
                group['types'].sort(key=lambda x: x['name'])
            result.append(category)
        
        result.sort(key=lambda x: x['name'])
        return result
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to avoid excessive memory use for large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"  Warning: Failed to calculate file hash {file_path}: {e}")
            return ""
    
    def extract_variant_info(self, filename: str) -> Optional[str]:
        """
        Extract variant info from filename (for group 963 T3 cruisers)
        Example: 29984_Tengu2312_caldaribase_lite.glb -> 2312
        Returns 4-digit string, None if not found
        """
        parts = filename.split('_')
        if len(parts) >= 2:
            # Extract second segment
            second_part = parts[1]
            # Try to extract last 4 digits
            match = re.search(r'(\d{4})$', second_part)
            if match:
                return match.group(1)
        return None
    
    def _get_model_files(self, path: Path) -> List[Path]:
        """Get all supported model files in specified directory"""
        if not path.exists():
            return []
        model_extensions = {'.glb', '.gltf'}
        return [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in model_extensions]
    
    def scan_models(self) -> Tuple[Dict[int, str], List[Dict]]:
        """Scan models directory, extract model file info, return model mapping and file info list (with hashes)"""
        print("Scanning model files...")
        
        model_map = {}
        file_info_list = []  # Store file info: typeid, path, hash, variant
        
        if not self.models_path.exists():
            print(f"  Warning: Models directory not found {self.models_path}")
            return model_map, file_info_list
        
        # Use shared method to get all model files
        model_files = self._get_model_files(self.models_path)
        
        print(f"  Found {len(model_files)} model files, calculating hashes...")
        
        # Scan all model files and calculate hashes
        for idx, model_file in enumerate(model_files, 1):
            if idx % 50 == 0 or idx == len(model_files):
                print(f"    Progress: {idx}/{len(model_files)} ({idx*100//len(model_files)}%)")
            
            # Split filename by underscore, take first part as ID
            filename_without_ext = model_file.stem
            parts = filename_without_ext.split('_')
            model_id_str = parts[0]
            
            try:
                model_id = int(model_id_str)
            except ValueError:
                print(f"  Warning: Cannot parse model ID: {model_file.name} (extracted ID: {model_id_str})")
                continue
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(model_file)
            if not file_hash:
                continue
            
            # Extract variant info (for group 963)
            variant = self.extract_variant_info(filename_without_ext)
            
            # Record model path (relative to docs directory)
            model_path = f"./models/{model_file.name}"
            
            # Record file info (with variant info)
            file_info_list.append({
                'typeid': model_id,
                'path': model_file,
                'relative_path': model_path,
                'hash': file_hash,
                'variant': variant,
                'filename': model_file.name
            })
            
            # For non-variant cases, keep simple mapping
            if model_id not in model_map:
                model_map[model_id] = model_path
        
        print(f"  Scanned {len(file_info_list)} model files (including variants)")
        return model_map, file_info_list
    
    def scan_extra_models(self) -> Tuple[Dict[int, str], List[Dict]]:
        """Scan extra_models directory, extract extra item IDs and file mapping, return model mapping and file info list (with hashes)"""
        print("Scanning extra models directory...")
        
        extra_models_map = {}
        file_info_list = []  # Store file info: typeid, path, hash, variant
        
        if not self.extra_models_path.exists():
            print(f"  Info: Extra models directory not found {self.extra_models_path}, skipping")
            return extra_models_map, file_info_list
        
        # Use shared method to get all model files
        model_files = self._get_model_files(self.extra_models_path)
        
        print(f"  Found {len(model_files)} model files, calculating hashes...")
        
        # Scan all model files and calculate hashes
        for idx, model_file in enumerate(model_files, 1):
            if idx % 50 == 0 or idx == len(model_files):
                print(f"    Progress: {idx}/{len(model_files)} ({idx*100//len(model_files)}%)")
            
            # Split filename by underscore, take first part as ID
            filename_without_ext = model_file.stem
            parts = filename_without_ext.split('_')
            model_id_str = parts[0]
            
            try:
                model_id = int(model_id_str)
            except ValueError:
                print(f"  Warning: Cannot parse extra model ID: {model_file.name} (extracted ID: {model_id_str})")
                continue
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(model_file)
            if not file_hash:
                continue
            
            # Extract variant info (for group 963)
            variant = self.extract_variant_info(filename_without_ext)
            
            # Record file path (relative to docs directory)
            file_path = f"./extra_models/{model_file.name}"
            
            # Record file info (with variant info)
            file_info_list.append({
                'typeid': model_id,
                'path': model_file,
                'relative_path': file_path,
                'hash': file_hash,
                'variant': variant,
                'filename': model_file.name
            })
            
            # For non-variant cases, keep simple mapping
            if model_id not in extra_models_map:
                extra_models_map[model_id] = file_path
        
        print(f"  Extracted {len(file_info_list)} model files from extra models directory (including variants)")
        return extra_models_map, file_info_list
    
    def check_duplicate_files(self, model_file_info: List[Dict], extra_file_info: List[Dict]):
        """Check if models and extra_models directories have files with identical names"""
        model_filenames = {info['filename']: info['relative_path'] for info in model_file_info}
        extra_filenames = {info['filename']: info['relative_path'] for info in extra_file_info}
        
        duplicate_files = set(model_filenames.keys()) & set(extra_filenames.keys())
        
        if duplicate_files:
            error_msg = f"\nError: Found {len(duplicate_files)} duplicate filenames existing in both models and extra_models directories:\n"
            for dup_file in sorted(duplicate_files):
                error_msg += f"  File {dup_file}:\n"
                error_msg += f"    - models directory: {model_filenames[dup_file]}\n"
                error_msg += f"    - extra_models directory: {extra_filenames[dup_file]}\n"
            error_msg += "\nPlease remove the file from one of the directories to ensure each filename appears in only one directory.\n"
            raise ValueError(error_msg)
    
    def deduplicate_model_mapping(self, file_info_list: List[Dict]) -> Dict[int, str]:
        """
        Reuse model files based on file hash, for files with same hash, point all typeids to file with smallest typeid
        Files with variant markers (variant not None) don't participate in deduplication, keep all variants
        No files are deleted, only mapping relationships updated to enable reuse
        Returns: Deduplicated model mapping (all typeids with same hash point to kept file)
        """
        print("Detecting duplicate files and building reuse mapping...")
        
        if not file_info_list:
            return {}
        
        # Separate variant files and normal files
        variant_files = [f for f in file_info_list if f.get('variant') is not None]
        normal_files = [f for f in file_info_list if f.get('variant') is None]
        
        print(f"  Variant files: {len(variant_files)} (not deduplicated)")
        print(f"  Normal files: {len(normal_files)} (deduplicated)")
        
        # Build result mapping
        result_map = {}
        
        # Variant files kept directly, not deduplicated
        for file_info in variant_files:
            typeid = file_info['typeid']
            # For variant files, use filename as part of key to ensure uniqueness
            # But in actual mapping, we need to keep full path info
            result_map[typeid] = file_info['relative_path']
        
        # Group normal files by hash value
        hash_groups: Dict[str, List[Dict]] = {}
        for file_info in normal_files:
            file_hash = file_info['hash']
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(file_info)
        
        # Find duplicate hashes (group with files > 1)
        duplicate_groups = {h: files for h, files in hash_groups.items() if len(files) > 1}
        
        reused_count = 0
        
        # Process each duplicate group
        for file_hash, files in duplicate_groups.items():
            # Sort by typeid, keep smallest as reuse target
            files_sorted = sorted(files, key=lambda x: x['typeid'])
            keep_file = files_sorted[0]
            reuse_files = files_sorted[1:]
            
            # Keep file's own mapping
            result_map[keep_file['typeid']] = keep_file['relative_path']
            
            # Point all duplicate file typeids to kept file
            for reuse_file in reuse_files:
                result_map[reuse_file['typeid']] = keep_file['relative_path']
                reused_count += 1
            
            # Output detailed info
            print(f"    Hash {file_hash[:16]}...:")
            print(f"      Reuse target: {keep_file['path'].name} (typeid: {keep_file['typeid']})")
            for reuse_file in reuse_files:
                print(f"        Reuse: {reuse_file['path'].name} (typeid: {reuse_file['typeid']}) -> points to {keep_file['path'].name}")
        
        # Process non-duplicate normal files (use their own paths directly)
        for file_hash, files in hash_groups.items():
            if file_hash not in duplicate_groups:
                for file_info in files:
                    result_map[file_info['typeid']] = file_info['relative_path']
        
        if duplicate_groups:
            print(f"  Reuse complete: {len(duplicate_groups)} duplicate file groups, {reused_count} typeids reusing existing files")
        else:
            print("  No duplicate files found, no reuse needed")
        
        print(f"  Mapping relationships: {len(result_map)} entries (including {len(variant_files)} variant files)")
        
        return result_map
    
    def extract_icons(self, icon_names: Set[str]):
        """Extract required icon files to static/icons directory"""
        print(f"Extracting {len(icon_names)} icon files...")
        
        extracted_count = 0
        for icon_name in icon_names:
            if not icon_name:
                continue
            
            icon_name_normalized = icon_name.replace('\\', '/')
            source_file = self.temp_icons_path / icon_name_normalized
            
            # Try to find using filename only
            if not source_file.exists():
                icon_filename = Path(icon_name_normalized).name
                source_file_flat = self.temp_icons_path / icon_filename
                if source_file_flat.exists():
                    source_file = source_file_flat
                    icon_name_normalized = icon_filename
            
            dest_file = self.icons_path / icon_name_normalized
            
            if source_file.exists():
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                extracted_count += 1
        
        print(f"  Extracted {extracted_count} icon files")
    
    def save_index(self, category_tree: list, lang: str):
        """Save index file"""
        output_file = self.output_path / f"resources_index_{lang}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_tree, f, ensure_ascii=False, indent=2)
        print(f"  {lang.upper()} index saved: {output_file}")
    
    def save_available_models(self, model_map: Dict[int, str]):
        """Save list of item IDs with models"""
        available_ids = sorted(model_map.keys())
        output_data = {"available": available_ids}
        output_file = self.output_path / "available_models.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"  Available model ID list saved: {output_file} (total {len(available_ids)})")
    
    def cleanup(self):
        """Clean up temporary files"""
        print("Cleaning up temporary files...")
        
        if self.temp_icons_path.exists():
            shutil.rmtree(self.temp_icons_path)
        
        print("  Cleanup complete")
    
    def run(self):
        """Run complete initialization process"""
        print("Starting EVE data initialization...")
        print("=" * 50)
        
        try:
            # 1. Extract files
            self.extract_zip_files()
            
            # 2. Connect to databases
            conn_zh = self.connect_database("zh")
            conn_en = self.connect_database("en")
            
            if not conn_zh or not conn_en:
                print("Error: Chinese and English databases required")
                return
            
            try:
                # 3. Scan model files (with hash calculation)
                model_map, model_file_info = self.scan_models()
                
                # 4. Scan extra models directory, extract extra item IDs (with hash calculation)
                extra_models_map, extra_file_info = self.scan_extra_models()
                
                # 5. Check if two directories have duplicate filenames
                self.check_duplicate_files(model_file_info, extra_file_info)
                
                # 6. Merge file info lists, perform hash deduplication
                all_file_info = model_file_info + extra_file_info
                
                # 7. Build reuse mapping based on hash values (don't delete files, only update mapping)
                combined_model_map = self.deduplicate_model_mapping(all_file_info)
                
                # 9. Extract extra item ID list for data loading (using deduplicated mapping)
                extra_type_ids = [tid for tid in extra_models_map.keys() if tid in combined_model_map]
                
                # 10. Load Chinese data
                data_zh = self.load_data(conn_zh, 'zh', extra_type_ids)
                tree_zh = self.build_category_tree(data_zh, combined_model_map, all_file_info)
                
                # 11. Load English data
                data_en = self.load_data(conn_en, 'en', extra_type_ids)
                tree_en = self.build_category_tree(data_en, combined_model_map, all_file_info)
                
                # 12. Extract icons (merge Chinese and English icon requirements)
                all_icons = data_zh['icon_names'] | data_en['icon_names']
                self.extract_icons(all_icons)
                
                # 13. Save index files
                print("Saving index files...")
                self.save_index(tree_zh, 'cn')
                self.save_index(tree_en, 'en')
                
                # 14. Save list of item IDs with models (includes models from both directories, deduplicated)
                print("Saving available models list...")
                self.save_available_models(combined_model_map)
                
            finally:
                conn_zh.close()
                conn_en.close()
                print("Database connections closed")
            
            # 7. Clean up temporary files
            self.cleanup()
            
            print("\nInitialization complete!")
            print("=" * 50)
                
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    initializer = EVEDataInitializer()
    initializer.run()
