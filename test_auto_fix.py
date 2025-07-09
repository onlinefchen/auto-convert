#!/usr/bin/env python3
"""
Test script to verify automatic signature line fixing
"""

import os
import glob

def test_signature_fix():
    """Test that all signature lines are completely removed"""
    issues_found = []
    
    # Find all rule files
    rule_files = []
    rule_files.extend(glob.glob('rules/surge/**/*.conf', recursive=True))
    rule_files.extend(glob.glob('rules/clash/**/*.txt', recursive=True))
    
    print(f"🔍 Checking {len(rule_files)} rule files...")
    
    for file_path in rule_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Check for any signature lines (should be completely removed)
            if 'th1s_rule5et_1s_m4d3_by_5ukk4w_ruleset.skk.moe' in line:
                issues_found.append({
                    'file': file_path,
                    'line': line_num,
                    'content': line.strip()
                })
    
    if issues_found:
        print(f"❌ Found {len(issues_found)} signature lines that should be removed:")
        for issue in issues_found:
            print(f"  📁 {issue['file']}:{issue['line']} - {issue['content']}")
        return False
    else:
        print("✅ All signature lines have been completely removed!")
        return True

def get_rule_stats():
    """Get statistics about rule files"""
    surge_files = glob.glob('rules/surge/**/*.conf', recursive=True)
    clash_files = glob.glob('rules/clash/**/*.txt', recursive=True)
    
    print(f"\n📊 Rule Statistics:")
    print(f"  - Surge files: {len(surge_files)}")
    print(f"  - Clash files: {len(clash_files)}")
    print(f"  - Total files: {len(surge_files) + len(clash_files)}")
    
    # Count by category
    for format_type in ['surge', 'clash']:
        print(f"\n  📂 {format_type.upper()} breakdown:")
        for category in ['domainset', 'non_ip', 'ip']:
            pattern = f'rules/{format_type}/{category}/*'
            files = glob.glob(pattern)
            print(f"    - {category}: {len(files)} files")

if __name__ == '__main__':
    print("🧪 Testing Rule File Integrity")
    print("=" * 40)
    
    # Test signature fix
    signature_ok = test_signature_fix()
    
    # Get statistics
    get_rule_stats()
    
    # Final result
    print("\n" + "=" * 40)
    if signature_ok:
        print("✅ All tests passed! Rules are ready for production.")
    else:
        print("❌ Issues found! Please check the output above.")
        exit(1)