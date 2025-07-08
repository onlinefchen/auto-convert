#!/usr/bin/env python3
"""
Subscription Link to Surge/Clash Configuration Converter
Converts proxy subscription links to Surge and Clash configuration files
"""

import base64
import json
import re
import sys
import urllib.parse
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import argparse


class ProxyParser:
    """Parse different proxy protocols"""
    
    @staticmethod
    def decode_subscription(content: str) -> List[str]:
        """Decode base64 encoded subscription content"""
        try:
            # Try to decode as base64
            decoded = base64.b64decode(content).decode('utf-8')
            return [line.strip() for line in decoded.split('\n') if line.strip()]
        except:
            # If not base64, assume it's plain text
            return [line.strip() for line in content.split('\n') if line.strip()]
    
    @staticmethod
    def parse_vmess(vmess_url: str) -> Optional[Dict]:
        """Parse vmess:// URL"""
        try:
            if not vmess_url.startswith('vmess://'):
                return None
            
            # Remove vmess:// prefix and decode base64
            vmess_data = vmess_url[8:]
            decoded = base64.b64decode(vmess_data).decode('utf-8')
            config = json.loads(decoded)
            
            return {
                'type': 'vmess',
                'name': config.get('ps', 'VMess'),
                'server': config.get('add', ''),
                'port': int(config.get('port', 443)),
                'uuid': config.get('id', ''),
                'alterId': int(config.get('aid', 0)),
                'cipher': config.get('scy', 'auto'),
                'network': config.get('net', 'tcp'),
                'tls': config.get('tls', '') == 'tls',
                'sni': config.get('sni', config.get('host', '')),
                'ws_path': config.get('path', ''),
                'ws_host': config.get('host', '')
            }
        except Exception as e:
            print(f"Error parsing vmess URL: {e}")
            return None
    
    @staticmethod
    def parse_ss(ss_url: str) -> Optional[Dict]:
        """Parse ss:// URL"""
        try:
            if not ss_url.startswith('ss://'):
                return None
            
            # Remove ss:// prefix
            ss_data = ss_url[5:]
            
            # Check if it contains @ (SIP002 format)
            if '@' in ss_data:
                # SIP002 format: ss://base64(method:password)@server:port#tag
                parts = ss_data.split('@')
                if len(parts) != 2:
                    return None
                
                # Decode method and password
                try:
                    method_password = base64.b64decode(parts[0]).decode('utf-8')
                except:
                    method_password = parts[0]
                
                method, password = method_password.split(':', 1)
                
                # Parse server info
                server_info = parts[1]
                if '#' in server_info:
                    server_port, name = server_info.split('#', 1)
                    name = urllib.parse.unquote(name)
                else:
                    server_port = server_info
                    name = 'Shadowsocks'
                
                server, port = server_port.split(':', 1)
                
            else:
                # Legacy format: ss://base64(method:password@server:port)#tag
                if '#' in ss_data:
                    encoded, name = ss_data.split('#', 1)
                    name = urllib.parse.unquote(name)
                else:
                    encoded = ss_data
                    name = 'Shadowsocks'
                
                decoded = base64.b64decode(encoded).decode('utf-8')
                method_password, server_port = decoded.split('@', 1)
                method, password = method_password.split(':', 1)
                server, port = server_port.split(':', 1)
            
            return {
                'type': 'ss',
                'name': name,
                'server': server,
                'port': int(port),
                'cipher': method,
                'password': password
            }
        except Exception as e:
            print(f"Error parsing ss URL: {e}")
            return None
    
    @staticmethod
    def parse_trojan(trojan_url: str) -> Optional[Dict]:
        """Parse trojan:// URL"""
        try:
            if not trojan_url.startswith('trojan://'):
                return None
            
            # Remove trojan:// prefix
            trojan_data = trojan_url[9:]
            
            # Format: trojan://password@server:port#name
            if '#' in trojan_data:
                main_part, name = trojan_data.split('#', 1)
                name = urllib.parse.unquote(name)
            else:
                main_part = trojan_data
                name = 'Trojan'
            
            password, server_port = main_part.split('@', 1)
            server, port = server_port.split(':', 1)
            
            return {
                'type': 'trojan',
                'name': name,
                'server': server,
                'port': int(port),
                'password': password,
                'sni': server  # Default SNI to server
            }
        except Exception as e:
            print(f"Error parsing trojan URL: {e}")
            return None


class ConfigGenerator:
    """Generate Surge and Clash configuration files"""
    
    def __init__(self, proxies: List[Dict]):
        self.proxies = proxies
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_surge(self) -> str:
        """Generate Surge configuration"""
        lines = []
        
        # Header
        lines.append('#!MANAGED-CONFIG interval=43200')
        lines.append(f'# Generated at {self.timestamp}')
        lines.append('# Auto Proxy Subscription Converter')
        lines.append('')
        
        # General settings
        lines.append('[General]')
        lines.append('skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local')
        lines.append('dns-server = 119.29.29.29, 223.5.5.5, system')
        lines.append('loglevel = notify')
        lines.append('internet-test-url = http://www.aliyun.com')
        lines.append('proxy-test-url = http://www.google.com/generate_204')
        lines.append('test-timeout = 5')
        lines.append('ipv6 = false')
        lines.append('')
        
        # Proxy section
        lines.append('[Proxy]')
        for proxy in self.proxies:
            proxy_line = self._generate_surge_proxy(proxy)
            if proxy_line:
                lines.append(proxy_line)
        lines.append('')
        
        # Proxy Group
        lines.append('[Proxy Group]')
        proxy_names = [p['name'] for p in self.proxies if self._is_valid_proxy(p)]
        
        if proxy_names:
            # 主要策略组
            lines.append(f'🚀 节点选择 = select, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'♻️ 自动选择 = url-test, {", ".join(proxy_names)}, url=http://www.google.com/generate_204, interval=300')
            
            # 服务策略组 - 每个都可以选择所有节点
            lines.append(f'🤖 人工智能 = select, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'📲 电报消息 = select, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'🎥 流媒体 = select, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'🎮 游戏平台 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'Ⓜ️ 微软服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'🍎 苹果服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            lines.append(f'📢 谷歌FCM = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, {", ".join(proxy_names)}')
            
            # 基础策略组
            lines.append('🎯 全球直连 = select, DIRECT, 🚀 节点选择')
            lines.append('🛑 全球拦截 = select, REJECT, DIRECT')
            lines.append('🍃 应用净化 = select, REJECT, DIRECT')
            lines.append('🐟 漏网之鱼 = select, 🚀 节点选择, ♻️ 自动选择, DIRECT')
        lines.append('')
        
        # Rules
        base_url = 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules'
        
        lines.append('[Rule]')
        lines.append('# 本地/局域网地址')
        lines.append(f'RULE-SET,{base_url}/lan.txt,🎯 全球直连')
        
        lines.append('# 拦截规则')
        lines.append(f'RULE-SET,{base_url}/reject.txt,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/reject_app.txt,🍃 应用净化')
        
        lines.append('# AI服务')
        lines.append(f'RULE-SET,{base_url}/ai.txt,🤖 人工智能')
        
        lines.append('# 电报')
        lines.append(f'RULE-SET,{base_url}/telegram.txt,📲 电报消息')
        
        lines.append('# 流媒体')
        lines.append(f'RULE-SET,{base_url}/stream.txt,🎥 流媒体')
        
        lines.append('# 微软')
        lines.append(f'RULE-SET,{base_url}/microsoft.txt,Ⓜ️ 微软服务')
        
        lines.append('# 苹果')
        lines.append(f'RULE-SET,{base_url}/apple.txt,🍎 苹果服务')
        
        lines.append('# 谷歌FCM')
        lines.append(f'RULE-SET,{base_url}/google_fcm.txt,📢 谷歌FCM')
        
        lines.append('# 游戏平台')
        lines.append(f'RULE-SET,{base_url}/game.txt,🎮 游戏平台')
        
        lines.append('# 国内域名')
        lines.append(f'RULE-SET,{base_url}/domestic.txt,🎯 全球直连')
        
        lines.append('# 全球加速')
        lines.append(f'RULE-SET,{base_url}/global.txt,🚀 节点选择')
        
        lines.append('# 中国IP')
        lines.append(f'RULE-SET,{base_url}/china_ip.txt,🎯 全球直连')
        
        lines.append('# Final')
        lines.append('FINAL,🐟 漏网之鱼')
        
        return '\n'.join(lines)
    
    def generate_clash(self) -> str:
        """Generate Clash configuration"""
        config = {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True,
                'nameserver': [
                    '119.29.29.29',
                    '223.5.5.5'
                ],
                'fallback': [
                    '8.8.8.8',
                    '1.1.1.1'
                ]
            }
        }
        
        # Proxies
        config['proxies'] = []
        for proxy in self.proxies:
            clash_proxy = self._generate_clash_proxy(proxy)
            if clash_proxy:
                config['proxies'].append(clash_proxy)
        
        # Proxy groups
        proxy_names = [p['name'] for p in self.proxies if self._is_valid_proxy(p)]
        
        config['proxy-groups'] = []
        
        if proxy_names:
            # 主要策略组
            config['proxy-groups'].extend([
                {
                    'name': '🚀 节点选择',
                    'type': 'select',
                    'proxies': ['♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '♻️ 自动选择',
                    'type': 'url-test',
                    'proxies': proxy_names,
                    'url': 'http://www.google.com/generate_204',
                    'interval': 300
                }
            ])
            
            # 服务策略组 - 每个都可以选择所有节点
            config['proxy-groups'].extend([
                {
                    'name': '🤖 人工智能',
                    'type': 'select',
                    'proxies': ['🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '📲 电报消息',
                    'type': 'select',
                    'proxies': ['🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '🎥 流媒体',
                    'type': 'select',
                    'proxies': ['🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '🎮 游戏平台',
                    'type': 'select',
                    'proxies': ['DIRECT', '🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': 'Ⓜ️ 微软服务',
                    'type': 'select',
                    'proxies': ['DIRECT', '🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '🍎 苹果服务',
                    'type': 'select',
                    'proxies': ['DIRECT', '🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '📢 谷歌FCM',
                    'type': 'select',
                    'proxies': ['DIRECT', '🚀 节点选择', '♻️ 自动选择'] + proxy_names
                },
                {
                    'name': '🎯 全球直连',
                    'type': 'select',
                    'proxies': ['DIRECT', '🚀 节点选择']
                },
                {
                    'name': '🛑 全球拦截',
                    'type': 'select',
                    'proxies': ['REJECT', 'DIRECT']
                },
                {
                    'name': '🍃 应用净化',
                    'type': 'select',
                    'proxies': ['REJECT', 'DIRECT']
                },
                {
                    'name': '🐟 漏网之鱼',
                    'type': 'select',
                    'proxies': ['🚀 节点选择', '♻️ 自动选择', 'DIRECT']
                }
            ])
        
        # Rule providers
        base_url = 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules'
        
        config['rule-providers'] = {
            'lan': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/lan.txt',
                'path': './ruleset/lan.yaml',
                'interval': 86400
            },
            'reject': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/reject.txt',
                'path': './ruleset/reject.yaml',
                'interval': 86400
            },
            'reject_app': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/reject_app.txt',
                'path': './ruleset/reject_app.yaml',
                'interval': 86400
            },
            'ai': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/ai.txt',
                'path': './ruleset/ai.yaml',
                'interval': 86400
            },
            'telegram': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/telegram.txt',
                'path': './ruleset/telegram.yaml',
                'interval': 86400
            },
            'stream': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/stream.txt',
                'path': './ruleset/stream.yaml',
                'interval': 86400
            },
            'microsoft': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/microsoft.txt',
                'path': './ruleset/microsoft.yaml',
                'interval': 86400
            },
            'apple': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/apple.txt',
                'path': './ruleset/apple.yaml',
                'interval': 86400
            },
            'google_fcm': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/google_fcm.txt',
                'path': './ruleset/google_fcm.yaml',
                'interval': 86400
            },
            'game': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/game.txt',
                'path': './ruleset/game.yaml',
                'interval': 86400
            },
            'global': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/global.txt',
                'path': './ruleset/global.yaml',
                'interval': 86400
            },
            'domestic': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/domestic.txt',
                'path': './ruleset/domestic.yaml',
                'interval': 86400
            },
            'china_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/china_ip.txt',
                'path': './ruleset/china_ip.yaml',
                'interval': 86400
            }
        }
        
        # Rules
        config['rules'] = [
            # 本地/局域网地址
            'RULE-SET,lan,🎯 全球直连',
            
            # 拦截规则
            'RULE-SET,reject,🛑 全球拦截',
            'RULE-SET,reject_app,🍃 应用净化',
            
            # AI服务
            'RULE-SET,ai,🤖 人工智能',
            
            # 电报
            'RULE-SET,telegram,📲 电报消息',
            
            # 流媒体
            'RULE-SET,stream,🎥 流媒体',
            
            # 微软
            'RULE-SET,microsoft,Ⓜ️ 微软服务',
            
            # 苹果
            'RULE-SET,apple,🍎 苹果服务',
            
            # 谷歌FCM
            'RULE-SET,google_fcm,📢 谷歌FCM',
            
            # 游戏平台
            'RULE-SET,game,🎮 游戏平台',
            
            # 国内域名
            'RULE-SET,domestic,🎯 全球直连',
            
            # 全球加速
            'RULE-SET,global,🚀 节点选择',
            
            # 中国IP
            'RULE-SET,china_ip,🎯 全球直连',
            
            # LAN IP
            'IP-CIDR,192.168.0.0/16,🎯 全球直连',
            'IP-CIDR,10.0.0.0/8,🎯 全球直连',
            'IP-CIDR,172.16.0.0/12,🎯 全球直连',
            'IP-CIDR,127.0.0.0/8,🎯 全球直连',
            
            # Final
            'MATCH,🐟 漏网之鱼'
        ]
        
        import yaml
        return yaml.dump(config, allow_unicode=True, sort_keys=False)
    
    def _is_valid_proxy(self, proxy: Dict) -> bool:
        """Check if proxy configuration is valid"""
        required_fields = {
            'vmess': ['server', 'port', 'uuid'],
            'ss': ['server', 'port', 'cipher', 'password'],
            'trojan': ['server', 'port', 'password']
        }
        
        proxy_type = proxy.get('type')
        if proxy_type not in required_fields:
            return False
        
        for field in required_fields[proxy_type]:
            if not proxy.get(field):
                return False
        
        return True
    
    def _generate_surge_proxy(self, proxy: Dict) -> Optional[str]:
        """Generate Surge proxy line"""
        if not self._is_valid_proxy(proxy):
            return None
        
        name = proxy['name']
        proxy_type = proxy['type']
        
        if proxy_type == 'vmess':
            # Surge format: name = vmess, server, port, username=uuid
            parts = [
                f'{name} = vmess',
                proxy['server'],
                str(proxy['port']),
                f'username={proxy["uuid"]}'
            ]
            
            if proxy.get('tls'):
                parts.append('tls=true')
                if proxy.get('sni'):
                    parts.append(f'sni={proxy["sni"]}')
            
            if proxy.get('ws_path'):
                parts.append(f'ws=true')
                parts.append(f'ws-path={proxy["ws_path"]}')
                if proxy.get('ws_host'):
                    parts.append(f'ws-headers=Host:{proxy["ws_host"]}')
            
            return ', '.join(parts)
        
        elif proxy_type == 'ss':
            # Surge format: name = ss, server, port, encrypt-method=cipher, password=password
            return f'{name} = ss, {proxy["server"]}, {proxy["port"]}, encrypt-method={proxy["cipher"]}, password={proxy["password"]}'
        
        elif proxy_type == 'trojan':
            # Surge format: name = trojan, server, port, password=password
            parts = [
                f'{name} = trojan',
                proxy['server'],
                str(proxy['port']),
                f'password={proxy["password"]}'
            ]
            
            if proxy.get('sni'):
                parts.append(f'sni={proxy["sni"]}')
            
            return ', '.join(parts)
        
        return None
    
    def _generate_clash_proxy(self, proxy: Dict) -> Optional[Dict]:
        """Generate Clash proxy configuration"""
        if not self._is_valid_proxy(proxy):
            return None
        
        proxy_type = proxy['type']
        
        if proxy_type == 'vmess':
            clash_proxy = {
                'name': proxy['name'],
                'type': 'vmess',
                'server': proxy['server'],
                'port': proxy['port'],
                'uuid': proxy['uuid'],
                'alterId': proxy.get('alterId', 0),
                'cipher': proxy.get('cipher', 'auto')
            }
            
            if proxy.get('tls'):
                clash_proxy['tls'] = True
                if proxy.get('sni'):
                    clash_proxy['servername'] = proxy['sni']
            
            if proxy.get('network') == 'ws':
                clash_proxy['network'] = 'ws'
                clash_proxy['ws-opts'] = {}
                if proxy.get('ws_path'):
                    clash_proxy['ws-opts']['path'] = proxy['ws_path']
                if proxy.get('ws_host'):
                    clash_proxy['ws-opts']['headers'] = {'Host': proxy['ws_host']}
            
            return clash_proxy
        
        elif proxy_type == 'ss':
            return {
                'name': proxy['name'],
                'type': 'ss',
                'server': proxy['server'],
                'port': proxy['port'],
                'cipher': proxy['cipher'],
                'password': proxy['password']
            }
        
        elif proxy_type == 'trojan':
            clash_proxy = {
                'name': proxy['name'],
                'type': 'trojan',
                'server': proxy['server'],
                'port': proxy['port'],
                'password': proxy['password']
            }
            
            if proxy.get('sni'):
                clash_proxy['sni'] = proxy['sni']
            
            return clash_proxy
        
        return None


def fetch_subscription(url: str) -> str:
    """Fetch subscription content from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert proxy subscription to Surge/Clash configuration')
    parser.add_argument('subscription_url', help='Subscription URL')
    parser.add_argument('-o', '--output', default='config', help='Output file prefix (default: config)')
    parser.add_argument('-f', '--format', choices=['surge', 'clash', 'both'], default='both', 
                        help='Output format (default: both)')
    
    args = parser.parse_args()
    
    # Fetch subscription
    print(f"Fetching subscription from {args.subscription_url}...")
    content = fetch_subscription(args.subscription_url)
    
    # Parse proxies
    parser = ProxyParser()
    proxy_urls = parser.decode_subscription(content)
    
    proxies = []
    for url in proxy_urls:
        if url.startswith('vmess://'):
            proxy = parser.parse_vmess(url)
        elif url.startswith('ss://'):
            proxy = parser.parse_ss(url)
        elif url.startswith('trojan://'):
            proxy = parser.parse_trojan(url)
        else:
            continue
        
        if proxy:
            proxies.append(proxy)
    
    print(f"Parsed {len(proxies)} proxies")
    
    if not proxies:
        print("No valid proxies found!")
        sys.exit(1)
    
    # Generate configurations
    generator = ConfigGenerator(proxies)
    
    if args.format in ['surge', 'both']:
        surge_config = generator.generate_surge()
        surge_file = f"{args.output}.surge.conf"
        with open(surge_file, 'w', encoding='utf-8') as f:
            f.write(surge_config)
        print(f"Surge configuration saved to {surge_file}")
    
    if args.format in ['clash', 'both']:
        # Install PyYAML if not available
        try:
            import yaml
        except ImportError:
            print("Installing PyYAML...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyyaml'])
            import yaml
        
        clash_config = generator.generate_clash()
        clash_file = f"{args.output}.clash.yaml"
        with open(clash_file, 'w', encoding='utf-8') as f:
            f.write(clash_config)
        print(f"Clash configuration saved to {clash_file}")
    
    print("Conversion completed!")


if __name__ == '__main__':
    main()