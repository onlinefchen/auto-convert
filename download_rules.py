#!/usr/bin/env python3
"""
Download Sukka's rule sets directly as recommended - no merging or conversion
"""

import requests
import os
import time
from typing import Dict, List

# Sukka 官方推荐的规则集 URL (仅使用实际存在的规则)
SUKKA_SURGE_RULES = {
    'lan': 'https://ruleset.skk.moe/List/non_ip/lan.conf',
    'reject': 'https://ruleset.skk.moe/List/domainset/reject.conf',
    'reject_app': 'https://ruleset.skk.moe/List/non_ip/reject.conf',
    'ai': 'https://ruleset.skk.moe/List/non_ip/ai.conf',
    'telegram': 'https://ruleset.skk.moe/List/non_ip/telegram.conf',
    'telegram_ip': 'https://ruleset.skk.moe/List/ip/telegram.conf',
    'stream': 'https://ruleset.skk.moe/List/non_ip/stream.conf',
    'microsoft': 'https://ruleset.skk.moe/List/non_ip/microsoft.conf',
    'apple': 'https://ruleset.skk.moe/List/non_ip/apple_services.conf',
    'domestic': 'https://ruleset.skk.moe/List/non_ip/domestic.conf',
    'global': 'https://ruleset.skk.moe/List/non_ip/global.conf',
    'china_ip': 'https://ruleset.skk.moe/List/ip/china_ip.conf'
}

SUKKA_CLASH_RULES = {
    'lan': 'https://ruleset.skk.moe/Clash/non_ip/lan.txt',
    'reject': 'https://ruleset.skk.moe/Clash/domainset/reject.txt',
    'reject_app': 'https://ruleset.skk.moe/Clash/non_ip/reject.txt',
    'ai': 'https://ruleset.skk.moe/Clash/non_ip/ai.txt',
    'telegram': 'https://ruleset.skk.moe/Clash/non_ip/telegram.txt',
    'telegram_ip': 'https://ruleset.skk.moe/Clash/ip/telegram.txt',
    'stream': 'https://ruleset.skk.moe/Clash/non_ip/stream.txt',
    'microsoft': 'https://ruleset.skk.moe/Clash/non_ip/microsoft.txt',
    'apple': 'https://ruleset.skk.moe/Clash/non_ip/apple_services.txt',
    'domestic': 'https://ruleset.skk.moe/Clash/non_ip/domestic.txt',
    'global': 'https://ruleset.skk.moe/Clash/non_ip/global.txt',
    'china_ip': 'https://ruleset.skk.moe/Clash/ip/china_ip.txt'
}

def download_file(url: str, max_retries: int = 3) -> str:
    """Download content from URL with retry"""
    for i in range(max_retries):
        try:
            print(f"  Downloading: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Retry {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  Failed to download: {url}")
                return ""

def create_rule_files():
    """Download Sukka's rule sets directly as recommended"""
    os.makedirs('rules/surge', exist_ok=True)
    os.makedirs('rules/clash', exist_ok=True)
    
    print("📥 Starting Sukka rule sets download (direct, no conversion)...")
    
    # Download Surge rules
    print("\n🔄 Downloading Surge rules...")
    for rule_name, url in SUKKA_SURGE_RULES.items():
        print(f"\n  📋 Downloading {rule_name} for Surge...")
        
        content = download_file(url)
        if not content:
            print(f"    ⚠️  Failed to download {rule_name}")
            continue
        
        # Add simple header
        header = f"""# {rule_name.upper()} Rules (SURGE)
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Source: {url}
# Original Sukka's rule set - no conversion applied

"""
        
        # Write file directly
        with open(f'rules/surge/{rule_name}.txt', 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        rule_count = len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
        print(f"    ✅ Created surge/{rule_name}.txt ({rule_count} rules)")
    
    # Download Clash rules
    print("\n🔄 Downloading Clash rules...")
    for rule_name, url in SUKKA_CLASH_RULES.items():
        print(f"\n  📋 Downloading {rule_name} for Clash...")
        
        content = download_file(url)
        if not content:
            print(f"    ⚠️  Failed to download {rule_name}")
            continue
        
        # Add simple header
        header = f"""# {rule_name.upper()} Rules (CLASH)
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Source: {url}
# Original Sukka's rule set - no conversion applied

"""
        
        # Write file directly
        with open(f'rules/clash/{rule_name}.txt', 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        rule_count = len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
        print(f"    ✅ Created clash/{rule_name}.txt ({rule_count} rules)")
    
    print(f"\n🎉 Sukka rule sets download completed!")
    print(f"📁 Files saved to:")
    print(f"  - rules/surge/ (Direct Sukka Surge rules)")
    print(f"  - rules/clash/ (Direct Sukka Clash rules)")

if __name__ == '__main__':
    create_rule_files()