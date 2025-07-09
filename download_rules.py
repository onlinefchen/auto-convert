#!/usr/bin/env python3
"""
Download Sukka's rule sets organized by DNS resolution behavior
Following the ref-list philosophy: domainset, non_ip, and ip categories
"""

import requests
import os
import time
from typing import Dict, List

# Sukka rule sets organized by DNS resolution behavior
# Based on complete analysis of ref-list directory structure

# SURGE RULES - Organized by DNS resolution behavior
SUKKA_SURGE_RULES = {
    # domainset - Pure domain rules (no DNS resolution)
    'domainset': {
        'cdn': 'https://ruleset.skk.moe/List/domainset/cdn.conf',
        'download': 'https://ruleset.skk.moe/List/domainset/download.conf',
        'reject': 'https://ruleset.skk.moe/List/domainset/reject.conf',
        'reject_extra': 'https://ruleset.skk.moe/List/domainset/reject_extra.conf',
        'reject_phishing': 'https://ruleset.skk.moe/List/domainset/reject_phishing.conf',
    },
    
    # non_ip - Rules that don't trigger DNS resolution
    'non_ip': {
        # Network infrastructure
        'lan': 'https://ruleset.skk.moe/List/non_ip/lan.conf',
        'download': 'https://ruleset.skk.moe/List/non_ip/download.conf',
        'cdn': 'https://ruleset.skk.moe/List/non_ip/cdn.conf',
        
        # Region-based
        'direct': 'https://ruleset.skk.moe/List/non_ip/direct.conf',
        'global': 'https://ruleset.skk.moe/List/non_ip/global.conf',
        'domestic': 'https://ruleset.skk.moe/List/non_ip/domestic.conf',
        
        # Service providers
        'apple_services': 'https://ruleset.skk.moe/List/non_ip/apple_services.conf',
        'apple_cn': 'https://ruleset.skk.moe/List/non_ip/apple_cn.conf',
        'microsoft': 'https://ruleset.skk.moe/List/non_ip/microsoft.conf',
        'microsoft_cdn': 'https://ruleset.skk.moe/List/non_ip/microsoft_cdn.conf',
        
        # AI services
        'ai': 'https://ruleset.skk.moe/List/non_ip/ai.conf',
        
        # Communication services
        'telegram': 'https://ruleset.skk.moe/List/non_ip/telegram.conf',
        
        # Streaming services (regional variants)
        'stream': 'https://ruleset.skk.moe/List/non_ip/stream.conf',
        'stream_us': 'https://ruleset.skk.moe/List/non_ip/stream_us.conf',
        'stream_eu': 'https://ruleset.skk.moe/List/non_ip/stream_eu.conf',
        'stream_jp': 'https://ruleset.skk.moe/List/non_ip/stream_jp.conf',
        'stream_kr': 'https://ruleset.skk.moe/List/non_ip/stream_kr.conf',
        'stream_hk': 'https://ruleset.skk.moe/List/non_ip/stream_hk.conf',
        'stream_tw': 'https://ruleset.skk.moe/List/non_ip/stream_tw.conf',
        
        # Other services
        'neteasemusic': 'https://ruleset.skk.moe/List/non_ip/neteasemusic.conf',
        
        # Privacy protection
        'sogouinput': 'https://ruleset.skk.moe/List/non_ip/sogouinput.conf',
        
        # Reject categories
        'reject': 'https://ruleset.skk.moe/List/non_ip/reject.conf',
        'reject_drop': 'https://ruleset.skk.moe/List/non_ip/reject-drop.conf',
        'reject_no_drop': 'https://ruleset.skk.moe/List/non_ip/reject-no-drop.conf',
    },
    
    # ip - Rules that trigger DNS resolution
    'ip': {
        # Region-based IP rules
        'china_ip': 'https://ruleset.skk.moe/List/ip/china_ip.conf',
        'domestic': 'https://ruleset.skk.moe/List/ip/domestic.conf',
        
        # Service-based IP rules
        'telegram': 'https://ruleset.skk.moe/List/ip/telegram.conf',
        'stream': 'https://ruleset.skk.moe/List/ip/stream.conf',
        'neteasemusic': 'https://ruleset.skk.moe/List/ip/neteasemusic.conf',
        
        # Infrastructure IP rules
        'lan': 'https://ruleset.skk.moe/List/ip/lan.conf',
        'cdn': 'https://ruleset.skk.moe/List/ip/cdn.conf',
        'download': 'https://ruleset.skk.moe/List/ip/download.conf',
        
        # Reject IP rules
        'reject': 'https://ruleset.skk.moe/List/ip/reject.conf',
    }
}

# CLASH RULES - Same organization
SUKKA_CLASH_RULES = {
    # domainset - Pure domain rules (no DNS resolution)
    'domainset': {
        'cdn': 'https://ruleset.skk.moe/Clash/domainset/cdn.txt',
        'download': 'https://ruleset.skk.moe/Clash/domainset/download.txt',
        'reject': 'https://ruleset.skk.moe/Clash/domainset/reject.txt',
        'reject_extra': 'https://ruleset.skk.moe/Clash/domainset/reject_extra.txt',
        'reject_phishing': 'https://ruleset.skk.moe/Clash/domainset/reject_phishing.txt',
    },
    
    # non_ip - Rules that don't trigger DNS resolution
    'non_ip': {
        # Network infrastructure
        'lan': 'https://ruleset.skk.moe/Clash/non_ip/lan.txt',
        'download': 'https://ruleset.skk.moe/Clash/non_ip/download.txt',
        'cdn': 'https://ruleset.skk.moe/Clash/non_ip/cdn.txt',
        
        # Region-based
        'direct': 'https://ruleset.skk.moe/Clash/non_ip/direct.txt',
        'global': 'https://ruleset.skk.moe/Clash/non_ip/global.txt',
        'domestic': 'https://ruleset.skk.moe/Clash/non_ip/domestic.txt',
        
        # Service providers
        'apple_services': 'https://ruleset.skk.moe/Clash/non_ip/apple_services.txt',
        'apple_cn': 'https://ruleset.skk.moe/Clash/non_ip/apple_cn.txt',
        'microsoft': 'https://ruleset.skk.moe/Clash/non_ip/microsoft.txt',
        'microsoft_cdn': 'https://ruleset.skk.moe/Clash/non_ip/microsoft_cdn.txt',
        
        # AI services
        'ai': 'https://ruleset.skk.moe/Clash/non_ip/ai.txt',
        
        # Communication services
        'telegram': 'https://ruleset.skk.moe/Clash/non_ip/telegram.txt',
        
        # Streaming services (regional variants)
        'stream': 'https://ruleset.skk.moe/Clash/non_ip/stream.txt',
        'stream_us': 'https://ruleset.skk.moe/Clash/non_ip/stream_us.txt',
        'stream_eu': 'https://ruleset.skk.moe/Clash/non_ip/stream_eu.txt',
        'stream_jp': 'https://ruleset.skk.moe/Clash/non_ip/stream_jp.txt',
        'stream_kr': 'https://ruleset.skk.moe/Clash/non_ip/stream_kr.txt',
        'stream_hk': 'https://ruleset.skk.moe/Clash/non_ip/stream_hk.txt',
        'stream_tw': 'https://ruleset.skk.moe/Clash/non_ip/stream_tw.txt',
        
        # Other services
        'neteasemusic': 'https://ruleset.skk.moe/Clash/non_ip/neteasemusic.txt',
        
        # Privacy protection
        'sogouinput': 'https://ruleset.skk.moe/Clash/non_ip/sogouinput.txt',
        
        # Reject categories
        'reject': 'https://ruleset.skk.moe/Clash/non_ip/reject.txt',
        'reject_drop': 'https://ruleset.skk.moe/Clash/non_ip/reject-drop.txt',
        'reject_no_drop': 'https://ruleset.skk.moe/Clash/non_ip/reject-no-drop.txt',
    },
    
    # ip - Rules that trigger DNS resolution
    'ip': {
        # Region-based IP rules
        'china_ip': 'https://ruleset.skk.moe/Clash/ip/china_ip.txt',
        'domestic': 'https://ruleset.skk.moe/Clash/ip/domestic.txt',
        
        # Service-based IP rules
        'telegram': 'https://ruleset.skk.moe/Clash/ip/telegram.txt',
        'stream': 'https://ruleset.skk.moe/Clash/ip/stream.txt',
        'neteasemusic': 'https://ruleset.skk.moe/Clash/ip/neteasemusic.txt',
        
        # Infrastructure IP rules
        'lan': 'https://ruleset.skk.moe/Clash/ip/lan.txt',
        'cdn': 'https://ruleset.skk.moe/Clash/ip/cdn.txt',
        'download': 'https://ruleset.skk.moe/Clash/ip/download.txt',
        
        # Reject IP rules
        'reject': 'https://ruleset.skk.moe/Clash/ip/reject.txt',
    }
}

def process_rule_content(content: str) -> str:
    """Process rule content to fix formatting issues"""
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        # Comment out Sukka's signature line to avoid syntax errors
        if 'th1s_rule5et_1s_m4d3_by_5ukk4w_ruleset.skk.moe' in line:
            processed_lines.append('# ' + line)
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def ensure_directories():
    """Ensure all required directories exist"""
    for format_type in ['surge', 'clash']:
        for category in ['domainset', 'non_ip', 'ip']:
            os.makedirs(f'rules/{format_type}/{category}', exist_ok=True)

def get_rule_stats(content: str) -> dict:
    """Get statistics about the rules"""
    lines = content.split('\n')
    total_lines = len(lines)
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    rule_lines = len([line for line in lines if line.strip() and not line.startswith('#')])
    
    return {
        'total_lines': total_lines,
        'comment_lines': comment_lines,
        'rule_lines': rule_lines
    }

def download_file(url: str, max_retries: int = 3) -> str:
    """Download content from URL with retry"""
    for i in range(max_retries):
        try:
            print(f"    Downloading: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"    Retry {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                print(f"    Failed to download: {url}")
                return ""

def create_rule_files():
    """Download Sukka's rule sets organized by DNS resolution behavior"""
    
    # Create directory structure following ref-list philosophy
    ensure_directories()
    
    print("📥 Starting Sukka rule sets download (organized by DNS resolution behavior)...")
    print(f"📅 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Source: https://ruleset.skk.moe/")
    print(f"📊 Total rule-sets: {len(SUKKA_SURGE_RULES['domainset']) + len(SUKKA_SURGE_RULES['non_ip']) + len(SUKKA_SURGE_RULES['ip'])}")
    
    # Download Surge rules
    print("\n🔄 Downloading Surge rules...")
    total_surge_rules = 0
    failed_surge = []
    
    for category, rules in SUKKA_SURGE_RULES.items():
        print(f"\n  📂 Category: {category} (Surge)")
        for rule_name, url in rules.items():
            print(f"\n    📋 Downloading {rule_name}...")
            
            content = download_file(url)
            if not content:
                print(f"      ⚠️  Failed to download {rule_name}")
                failed_surge.append(f"{category}/{rule_name}")
                continue
            
            # Process content to fix formatting issues
            content = process_rule_content(content)
            
            # Add header with category information
            header = f"""# {rule_name.upper()} Rules (SURGE)
# Category: {category}
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Source: {url}
# DNS Resolution: {'Yes' if category == 'ip' else 'No'}

"""
            
            # Write file in category subdirectory
            filepath = f'rules/surge/{category}/{rule_name}.conf'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + content)
            
            stats = get_rule_stats(content)
            total_surge_rules += stats['rule_lines']
            print(f"      ✅ Created {filepath} ({stats['rule_lines']} rules, {stats['total_lines']} total lines)")
    
    # Download Clash rules
    print("\n🔄 Downloading Clash rules...")
    total_clash_rules = 0
    failed_clash = []
    
    for category, rules in SUKKA_CLASH_RULES.items():
        print(f"\n  📂 Category: {category} (Clash)")
        for rule_name, url in rules.items():
            print(f"\n    📋 Downloading {rule_name}...")
            
            content = download_file(url)
            if not content:
                print(f"      ⚠️  Failed to download {rule_name}")
                failed_clash.append(f"{category}/{rule_name}")
                continue
            
            # Process content to fix formatting issues
            content = process_rule_content(content)
            
            # Add header with category information
            header = f"""# {rule_name.upper()} Rules (CLASH)
# Category: {category}
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Source: {url}
# DNS Resolution: {'Yes' if category == 'ip' else 'No'}

"""
            
            # Write file in category subdirectory
            filepath = f'rules/clash/{category}/{rule_name}.txt'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + content)
            
            stats = get_rule_stats(content)
            total_clash_rules += stats['rule_lines']
            print(f"      ✅ Created {filepath} ({stats['rule_lines']} rules, {stats['total_lines']} total lines)")
    
    print(f"\n🎉 Rule sets download completed!")
    print(f"📊 Statistics:")
    print(f"  - Surge rules: {total_surge_rules} total")
    print(f"  - Clash rules: {total_clash_rules} total")
    print(f"📁 Files organized by DNS resolution behavior:")
    print(f"  - rules/surge/domainset/ (pure domain rules)")
    print(f"  - rules/surge/non_ip/ (no DNS resolution)")
    print(f"  - rules/surge/ip/ (triggers DNS resolution)")
    print(f"  - rules/clash/domainset/ (pure domain rules)")
    print(f"  - rules/clash/non_ip/ (no DNS resolution)")
    print(f"  - rules/clash/ip/ (triggers DNS resolution)")
    
    if failed_surge or failed_clash:
        print(f"\n⚠️  Failed downloads:")
        if failed_surge:
            print(f"  Surge: {', '.join(failed_surge)}")
        if failed_clash:
            print(f"  Clash: {', '.join(failed_clash)}")

if __name__ == '__main__':
    create_rule_files()