#!/usr/bin/env python3
"""
Download and process rule sets for Surge and Clash separately
"""

import requests
import os
import time
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

def normalize_rule_surge(line: str) -> str:
    """Normalize rule format to Surge compatible format"""
    line = line.strip()
    if not line or line.startswith('#'):
        return ""
    
    # Handle IP-CIDR format (naked IP ranges)
    if '/' in line and not line.startswith('DOMAIN') and not line.startswith('IP-CIDR'):
        return f"IP-CIDR,{line}"
    
    # Handle domain wildcard format (+.domain.com or .domain.com)
    if line.startswith('+.'):
        domain = line[2:]
        return f"DOMAIN-SUFFIX,{domain}"
    elif line.startswith('.') and not line.startswith('..') and '.' in line[1:]:
        domain = line[1:]
        return f"DOMAIN-SUFFIX,{domain}"
    
    # Handle standard rule formats
    if ',' in line:
        parts = line.split(',')
        rule_type = parts[0]
        rule_value = parts[1]
        
        # Skip unsupported rule types for Surge
        if rule_type in ['DOMAIN-WILDCARD', 'USER-AGENT']:
            return ""
        
        if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'GEOIP', 'DOMAIN-REGEX']:
            return f"{rule_type},{rule_value}"
    
    # Handle naked domain
    if '.' in line and not line.startswith('.') and not line.startswith('+'):
        return f"DOMAIN,{line}"
    
    # Handle special cases like ".data"
    if line.startswith('.') and line.count('.') == 1:
        return f"DOMAIN,{line}"
    
    return line

def normalize_rule_clash(line: str) -> str:
    """Normalize rule format to Clash compatible format"""
    line = line.strip()
    if not line or line.startswith('#'):
        return ""
    
    # Handle IP-CIDR format (naked IP ranges)
    if '/' in line and not line.startswith('DOMAIN') and not line.startswith('IP-CIDR'):
        return f"IP-CIDR,{line}"
    
    # Handle domain wildcard format (+.domain.com or .domain.com)
    if line.startswith('+.'):
        domain = line[2:]
        return f"DOMAIN-SUFFIX,{domain}"
    elif line.startswith('.') and not line.startswith('..') and '.' in line[1:]:
        domain = line[1:]
        return f"DOMAIN-SUFFIX,{domain}"
    
    # Handle standard rule formats
    if ',' in line:
        parts = line.split(',')
        rule_type = parts[0]
        rule_value = parts[1]
        
        if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'GEOIP', 'DOMAIN-REGEX', 'DOMAIN-WILDCARD', 'USER-AGENT']:
            return f"{rule_type},{rule_value}"
    
    # Handle naked domain
    if '.' in line and not line.startswith('.') and not line.startswith('+'):
        return f"DOMAIN,{line}"
    
    # Handle special cases like ".data"
    if line.startswith('.') and line.count('.') == 1:
        return f"DOMAIN,{line}"
    
    return line

def process_rules_for_format(rule_contents: List[str], format_type: str) -> List[str]:
    """Process rules for specific format"""
    normalize_func = normalize_rule_surge if format_type == 'surge' else normalize_rule_clash
    rules = set()
    
    for content in rule_contents:
        if not content:
            continue
            
        for line in content.split('\n'):
            normalized = normalize_func(line)
            if normalized:
                rules.add(normalized)
    
    return sorted(list(rules))

def create_rule_files():
    """Download and process rule files for both formats"""
    os.makedirs('rules/surge', exist_ok=True)
    os.makedirs('rules/clash', exist_ok=True)
    
    print("📥 Starting rule download and processing...")
    
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
        
        # Process for both formats
        for format_type in ['surge', 'clash']:
            processed_rules = process_rules_for_format(rule_contents, format_type)
            
            if not processed_rules:
                print(f"  ⚠️  No valid {format_type} rules found for {group_name}")
                continue
            
            # Generate header
            header = f"""# {group_name.upper()} Rules ({format_type.upper()})
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Sources: {', '.join(urls.keys())}
# Total rules: {len(processed_rules)}

"""
            
            # Create rule file
            rule_content = header + '\n'.join(processed_rules)
            
            # Write file
            with open(f'rules/{format_type}/{group_name}.txt', 'w', encoding='utf-8') as f:
                f.write(rule_content)
            
            print(f"  ✅ Created {format_type}/{group_name}.txt ({len(processed_rules)} rules)")
    
    print(f"\n🎉 Rule processing completed!")
    print(f"📁 Files saved to:")
    print(f"  - rules/surge/ (Surge format)")
    print(f"  - rules/clash/ (Clash format)")

if __name__ == '__main__':
    create_rule_files()