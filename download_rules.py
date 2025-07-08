#!/usr/bin/env python3
"""
Download and merge rule sets for proxy configuration
"""

import requests
import os
import time
from collections import defaultdict
from typing import Dict, List, Set

# 规则集URL映射，按功能分组
RULE_GROUPS = {
    'lan': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/lan.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/lan.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/LocalAreaNetwork.list'
    },
    'reject': {
        'sukka_domainset': 'https://ruleset.skk.moe/List/domainset/reject.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/domainset/reject.txt',
        'acl4ssr_ad': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanAD.list'
    },
    'reject_app': {
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanProgramAD.list'
    },
    'ai': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/ai.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/ai.txt'
    },
    'telegram': {
        'sukka_surge_non_ip': 'https://ruleset.skk.moe/List/non_ip/telegram.conf',
        'sukka_surge_ip': 'https://ruleset.skk.moe/List/ip/telegram.conf',
        'sukka_clash_non_ip': 'https://ruleset.skk.moe/Clash/non_ip/telegram.txt',
        'sukka_clash_ip': 'https://ruleset.skk.moe/Clash/ip/telegram.txt'
    },
    'stream': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/stream.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/stream.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ProxyMedia.list'
    },
    'microsoft': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/microsoft.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/microsoft.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Microsoft.list'
    },
    'apple': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/apple_services.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/apple_services.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Apple.list'
    },
    'google_fcm': {
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/GoogleFCM.list'
    },
    'game': {
        'acl4ssr_steam': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Steam.list',
        'acl4ssr_epic': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Epic.list'
    },
    'domestic': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/domestic.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/domestic.txt',
        'acl4ssr_domain': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ChinaDomain.list',
        'acl4ssr_ip': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ChinaCompanyIp.list'
    },
    'global': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/global.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/global.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ProxyLite.list'
    },
    'china_ip': {
        'sukka_surge': 'https://ruleset.skk.moe/List/ip/china_ip.conf',
        'sukka_clash': 'https://ruleset.skk.moe/Clash/ip/china_ip.txt'
    }
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

def normalize_rule(line: str) -> str:
    """Normalize rule format"""
    line = line.strip()
    if not line or line.startswith('#'):
        return ""
    
    # Remove payload suffix for Clash rules
    if ',' in line and (line.startswith('DOMAIN') or line.startswith('IP-CIDR')):
        parts = line.split(',')
        if len(parts) >= 2:
            return f"{parts[0]},{parts[1]}"
    
    return line

def merge_rules(rule_contents: List[str]) -> List[str]:
    """Merge multiple rule contents and deduplicate"""
    rules = set()
    
    for content in rule_contents:
        if not content:
            continue
            
        for line in content.split('\n'):
            normalized = normalize_rule(line)
            if normalized:
                rules.add(normalized)
    
    # Sort rules for consistent output
    return sorted(list(rules))

def create_rule_files():
    """Download and merge rule files"""
    os.makedirs('rules', exist_ok=True)
    
    print("📥 Starting rule download and merge process...")
    
    for group_name, urls in RULE_GROUPS.items():
        print(f"\n🔄 Processing {group_name} rules...")
        
        # Download all rule contents for this group
        rule_contents = []
        for source_name, url in urls.items():
            content = download_file(url)
            if content:
                rule_contents.append(content)
        
        if not rule_contents:
            print(f"  ⚠️  No content downloaded for {group_name}")
            continue
        
        # Merge and deduplicate
        merged_rules = merge_rules(rule_contents)
        
        if not merged_rules:
            print(f"  ⚠️  No valid rules found for {group_name}")
            continue
        
        # Generate header
        header = f"""# {group_name.upper()} Rules
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Sources: {', '.join(urls.keys())}
# Total rules: {len(merged_rules)}

"""
        
        # Create unified rule file
        rule_content = header + '\n'.join(merged_rules)
        
        # Write file
        with open(f'rules/{group_name}.txt', 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        print(f"  ✅ Created {group_name}.txt ({len(merged_rules)} rules)")
    
    print(f"\n🎉 Rule download and merge completed!")
    print(f"📁 Files saved to:")
    print(f"  - rules/ (Universal format, works for both Surge and Clash)")

if __name__ == '__main__':
    create_rule_files()