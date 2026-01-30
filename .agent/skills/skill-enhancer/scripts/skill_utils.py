#!/usr/bin/env python3
import os
import sys
import re

class VanillaYamlParser:
    """
    Zero-Dependency YAML Parser for strict subset of YAML.
    Supports:
    - Key-Value pairs (key: value)
    - Lists (- item)
    - Basic Nesting (2-3 levels)
    - Quoted strings ("foo", 'bar')
    - Comments (#)
    """
    def parse(self, content):
        lines = content.splitlines()
        root = {}
        stack = [(root, -1)]  # (container, indent_level)
        last_key = None 
        
        for line in lines:
            raw_line = line.rstrip()
            stripped = raw_line.lstrip()
            
            # Skip empty or comments
            if not stripped or stripped.startswith('#'):
                continue
                
            indent = len(raw_line) - len(stripped)
            line_content = stripped.split('#')[0].strip()
            
            # Hierarchy management
            while len(stack) > 1 and indent <= stack[-1][1]:
                stack.pop()
            
            current_container, _ = stack[-1]

            # Case 1: List Item "- value" or "- key: value"
            if line_content.startswith('- '):
                value = line_content[2:].strip()
                processed_val = self._parse_value(value)
                
                # Check for "Empty Dict -> List" conversion
                if isinstance(current_container, dict) and len(current_container) == 0:
                    if len(stack) > 1:
                        parent, _ = stack[-2]
                        target_k = None
                        if isinstance(parent, dict):
                            for k, v in parent.items():
                                if v is current_container:
                                    target_k = k
                                    break
                        
                        if target_k:
                            # Swap dict for list
                            new_list = []
                            parent[target_k] = new_list
                            
                            # Capture old indent (of the dict/key) from stack before popping
                            _, old_indent = stack[-1]
                            stack.pop()
                            # Use old_indent so list container logic works for siblings
                            stack.append((new_list, old_indent))
                            current_container = new_list
                
                if isinstance(current_container, list):
                    current_container.append(processed_val)
                    if isinstance(processed_val, dict):
                         stack.append((processed_val, indent))
                
                # Fallback: If we popped the list container, append to parent
                elif isinstance(current_container, dict) and last_key:
                    if last_key not in current_container or not isinstance(current_container[last_key], list):
                        current_container[last_key] = []
                    
                    if isinstance(processed_val, dict) and hasattr(processed_val, 'items'):
                         # Support "- key: val" style
                         # processed_val is already dict from _parse_value
                         current_container[last_key].append(processed_val)
                         # Push with current indent so keys inside match scope
                         stack.append((processed_val, indent))
                    else:
                        current_container[last_key].append(processed_val)
                continue

            # Case 2: Key-Value "key: value" or Parent "key:"
            if ':' in line_content:
                key_part, val_part = line_content.split(':', 1)
                key = key_part.strip()
                val = val_part.strip()
                
                if not val:
                    new_container = {} 
                    current_container[key] = new_container
                    last_key = key
                    stack.append((new_container, indent))
                else:
                    current_container[key] = self._parse_value(val)
                    last_key = key
                continue

        return root

    def _parse_value(self, val_str):
        val_str = val_str.strip()
        
        # Check for inline dict "key: val" (for list items)
        # Only support simple keys to avoid false positives with text containing colons
        if ':' in val_str and not (val_str.startswith('"') or val_str.startswith("'")):
            k, v = val_str.split(':', 1)
            k = k.strip()
            # Simple heuristic: valid key shouldn't have brackets or extensive spaces
            # If k has spaces but is short, might be ok? 
            # Safest: prevent keys with [], (), or multiple words unless strictly needed.
            if re.match(r'^[\w\-\.]+$', k): 
                 return {k: self._parse_value(v)}
            
        # Quotes
        if (val_str.startswith('"') and val_str.endswith('"')) or \
           (val_str.startswith("'") and val_str.endswith("'")):
            return val_str[1:-1]
            
        # Booleans / Nulls
        if not isinstance(val_str, str):
            return val_str

        val_lower = val_str.lower()
        if val_lower == 'true': return True
        if val_lower == 'false': return False
        if val_lower == 'null': return None
        
        # Numbers
        if val_str.isdigit(): return int(val_str)
        try:
            return float(val_str)
        except ValueError:
            pass
            
        return val_str

def load_config(project_root="."):
    """
    Loads configuration by merging:
    1. Bundled Defaults (skill_standards_default.yaml)
    2. Project Overlay (.agent/rules/skill_standards.yaml)
    """
    parser = VanillaYamlParser()
    config = {}
    
    # 1. Load Defaults
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "skill_standards_default.yaml")
    
    if os.path.exists(default_path):
        try:
            with open(default_path, 'r') as f:
                config = parser.parse(f.read())
        except Exception as e:
            print(f"Warning: Failed to load bundled defaults: {e}")
    
    # 2. Load Project Overlay
    project_config_path = os.path.join(project_root, ".agent", "rules", "skill_standards.yaml")
    if os.path.exists(project_config_path):
        try:
            with open(project_config_path, 'r') as f:
                overlay = parser.parse(f.read())
                _deep_merge(config, overlay)
        except Exception as e:
            print(f"Warning: Failed to load project config at {project_config_path}: {e}")
            
    return config

def _deep_merge(base, overlay):
    """Recursive merge of dicts."""
    for k, v in overlay.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v

if __name__ == "__main__":
    cfg = load_config()
    import json
    print(json.dumps(cfg, indent=2))
