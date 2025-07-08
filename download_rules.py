#!/usr/bin/env python3
"""
Download and process rule sets for Surge and Clash with format-specific sources
"""

import requests
import os
import time
from typing import Dict, List, Set

# Surge 专用规则源 (优先使用原生 Surge 格式)
SURGE_RULE_SOURCES = {
    'lan': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/lan.conf'
    },
    'reject': {
        'sukka_domainset': 'https://ruleset.skk.moe/List/domainset/reject.conf'
    },
    'reject_app': {
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanProgramAD.list'
    },
    'ai': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/ai.conf'
    },
    'telegram': {
        'sukka_surge_non_ip': 'https://ruleset.skk.moe/List/non_ip/telegram.conf',
        'sukka_surge_ip': 'https://ruleset.skk.moe/List/ip/telegram.conf'
    },
    'stream': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/stream.conf'
    },
    'microsoft': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/microsoft.conf'
    },
    'apple': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/apple_services.conf'
    },
    'google_fcm': {
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/GoogleFCM.list'
    },
    'game': {
        'acl4ssr_steam': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Steam.list',
        'acl4ssr_epic': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Epic.list'
    },
    'domestic': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/domestic.conf'
    },
    'global': {
        'sukka_surge': 'https://ruleset.skk.moe/List/non_ip/global.conf'
    },
    'china_ip': {
        'sukka_surge': 'https://ruleset.skk.moe/List/ip/china_ip.conf'
    }
}

# Clash 专用规则源 (使用 Clash 格式源，获得更好的覆盖)
CLASH_RULE_SOURCES = {
    'lan': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/lan.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/LocalAreaNetwork.list'
    },
    'reject': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/domainset/reject.txt',
        'acl4ssr_ad': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanAD.list'
    },
    'reject_app': {
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanProgramAD.list'
    },
    'ai': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/ai.txt'
    },
    'telegram': {
        'sukka_clash_non_ip': 'https://ruleset.skk.moe/Clash/non_ip/telegram.txt',
        'sukka_clash_ip': 'https://ruleset.skk.moe/Clash/ip/telegram.txt'
    },
    'stream': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/stream.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ProxyMedia.list'
    },
    'microsoft': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/microsoft.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Microsoft.list'
    },
    'apple': {
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
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/domestic.txt',
        'acl4ssr_domain': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ChinaDomain.list',
        'acl4ssr_ip': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ChinaCompanyIp.list'
    },
    'global': {
        'sukka_clash': 'https://ruleset.skk.moe/Clash/non_ip/global.txt',
        'acl4ssr': 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/ProxyLite.list'
    },
    'china_ip': {
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
        rule_value = parts[1] if len(parts) > 1 else ""
        
        # Skip unsupported rule types for Surge
        if rule_type in ['DOMAIN-WILDCARD', 'USER-AGENT']:
            return ""
        
        if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'GEOIP', 'DOMAIN-REGEX', 'PROCESS-NAME']:
            return f"{rule_type},{rule_value}"
    
    # Handle naked domain
    if '.' in line and not line.startswith('.') and not line.startswith('+') and not line.startswith('DOMAIN'):
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
        rule_value = parts[1] if len(parts) > 1 else ""
        
        # Clash supports all rule types
        if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'GEOIP', 'DOMAIN-REGEX', 'DOMAIN-WILDCARD', 'USER-AGENT', 'PROCESS-NAME']:
            return f"{rule_type},{rule_value}"
    
    # Handle naked domain
    if '.' in line and not line.startswith('.') and not line.startswith('+') and not line.startswith('DOMAIN'):
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
    """Download and process rule files for both formats with format-specific sources"""
    os.makedirs('rules/surge', exist_ok=True)
    os.makedirs('rules/clash', exist_ok=True)
    
    print("📥 Starting format-specific rule download and processing...")
    
    # Process Surge rules
    print("\n🔄 Processing Surge rules...")
    for group_name, urls in SURGE_RULE_SOURCES.items():
        print(f"\n  📋 Processing {group_name} rules for Surge...")
        
        # Download Surge-specific sources
        rule_contents = []
        for source_name, url in urls.items():
            content = download_file(url)
            if content:
                rule_contents.append(content)
        
        if not rule_contents:
            print(f"    ⚠️  No content downloaded for {group_name}")
            continue
        
        # Process rules for Surge
        processed_rules = process_rules_for_format(rule_contents, 'surge')
        
        if not processed_rules:
            print(f"    ⚠️  No valid Surge rules found for {group_name}")
            continue
        
        # Generate header
        header = f"""# {group_name.upper()} Rules (SURGE)
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Sources: {', '.join(urls.keys())}
# Total rules: {len(processed_rules)}

"""
        
        # Create rule file
        rule_content = header + '\n'.join(processed_rules)
        
        # Write file
        with open(f'rules/surge/{group_name}.txt', 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        print(f"    ✅ Created surge/{group_name}.txt ({len(processed_rules)} rules)")
    
    # Process Clash rules
    print("\n🔄 Processing Clash rules...")
    for group_name, urls in CLASH_RULE_SOURCES.items():
        print(f"\n  📋 Processing {group_name} rules for Clash...")
        
        # Download Clash-specific sources
        rule_contents = []
        for source_name, url in urls.items():
            content = download_file(url)
            if content:
                rule_contents.append(content)
        
        if not rule_contents:
            print(f"    ⚠️  No content downloaded for {group_name}")
            continue
        
        # Process rules for Clash
        processed_rules = process_rules_for_format(rule_contents, 'clash')
        
        if not processed_rules:
            print(f"    ⚠️  No valid Clash rules found for {group_name}")
            continue
        
        # Generate header
        header = f"""# {group_name.upper()} Rules (CLASH)
# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
# Sources: {', '.join(urls.keys())}
# Total rules: {len(processed_rules)}

"""
        
        # Create rule file
        rule_content = header + '\n'.join(processed_rules)
        
        # Write file
        with open(f'rules/clash/{group_name}.txt', 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        print(f"    ✅ Created clash/{group_name}.txt ({len(processed_rules)} rules)")
    
    print(f"\n🎉 Format-specific rule processing completed!")
    print(f"📁 Files saved to:")
    print(f"  - rules/surge/ (Surge-optimized sources)")
    print(f"  - rules/clash/ (Clash-optimized sources)")

if __name__ == '__main__':
    create_rule_files()