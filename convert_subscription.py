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
        lines.append('# GitHub服务 (DNS解析: 否) - 优先处理避免DNS污染')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/github.conf,🚀 节点选择')
        lines.append('')
        
        lines.append('# 本地/局域网地址 (DNS解析: 是/否)')
        lines.append(f'RULE-SET,{base_url}/surge/ip/lan.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/lan.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 拦截规则 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/domainset/reject.conf,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/surge/domainset/reject_extra.conf,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/surge/domainset/reject_phishing.conf,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/reject.conf,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/reject_drop.conf,🛑 全球拦截')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/reject_no_drop.conf,🍃 应用净化')
        lines.append(f'RULE-SET,{base_url}/surge/ip/reject.conf,🛑 全球拦截')
        lines.append('')
        
        lines.append('# AI服务 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/ai.conf,🤖 人工智能')
        lines.append('')
        
        lines.append('# 电报消息 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/telegram.conf,📲 电报消息')
        lines.append(f'RULE-SET,{base_url}/surge/ip/telegram.conf,📲 电报消息')
        lines.append('')
        
        lines.append('# 流媒体 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_us.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_eu.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_jp.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_kr.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_hk.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/stream_tw.conf,🎥 流媒体')
        lines.append(f'RULE-SET,{base_url}/surge/ip/stream.conf,🎥 流媒体')
        lines.append('')
        
        lines.append('# 微软服务 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/microsoft.conf,Ⓜ️ 微软服务')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/microsoft_cdn.conf,Ⓜ️ 微软服务')
        lines.append('')
        
        lines.append('# 苹果服务 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/apple_services.conf,🍎 苹果服务')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/apple_cn.conf,🍎 苹果服务')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/apple_cdn.conf,🍎 苹果服务')
        lines.append('')
        
        lines.append('# 网易云音乐 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/neteasemusic.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/ip/neteasemusic.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 隐私保护 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/sogouinput.conf,🛑 全球拦截')
        lines.append('')
        
        lines.append('# CDN优化 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/domainset/cdn.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/cdn.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/ip/cdn.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 下载优化 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/domainset/download.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/download.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/ip/download.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 国内服务 (DNS解析: 否/是)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/domestic.conf,🎯 全球直连')
        lines.append(f'RULE-SET,{base_url}/surge/ip/domestic.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 全球代理 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/global.conf,🚀 节点选择')
        lines.append('')
        
        lines.append('# 直连服务 (DNS解析: 否)')
        lines.append(f'RULE-SET,{base_url}/surge/non_ip/direct.conf,🎯 全球直连')
        lines.append('')
        
        lines.append('# 中国IP (DNS解析: 是)')
        lines.append(f'RULE-SET,{base_url}/surge/ip/china_ip.conf,🎯 全球直连')
        lines.append('')
        
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
            # GitHub服务 (non_ip) - 避免DNS污染
            'github': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/github.txt',
                'path': './ruleset/github.yaml',
                'interval': 86400
            },
            
            # 局域网规则 (non_ip/ip)
            'lan_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/lan.txt',
                'path': './ruleset/lan_ip.yaml',
                'interval': 86400
            },
            'lan_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/lan.txt',
                'path': './ruleset/lan_non_ip.yaml',
                'interval': 86400
            },
            
            # 拦截规则 (domainset/non_ip/ip)
            'reject_domainset': {
                'type': 'http',
                'behavior': 'domain',
                'url': f'{base_url}/clash/domainset/reject.txt',
                'path': './ruleset/reject_domainset.yaml',
                'interval': 86400
            },
            'reject_extra': {
                'type': 'http',
                'behavior': 'domain',
                'url': f'{base_url}/clash/domainset/reject_extra.txt',
                'path': './ruleset/reject_extra.yaml',
                'interval': 86400
            },
            'reject_phishing': {
                'type': 'http',
                'behavior': 'domain',
                'url': f'{base_url}/clash/domainset/reject_phishing.txt',
                'path': './ruleset/reject_phishing.yaml',
                'interval': 86400
            },
            'reject_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/reject.txt',
                'path': './ruleset/reject_non_ip.yaml',
                'interval': 86400
            },
            'reject_drop': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/reject_drop.txt',
                'path': './ruleset/reject_drop.yaml',
                'interval': 86400
            },
            'reject_no_drop': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/reject_no_drop.txt',
                'path': './ruleset/reject_no_drop.yaml',
                'interval': 86400
            },
            'reject_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/reject.txt',
                'path': './ruleset/reject_ip.yaml',
                'interval': 86400
            },
            
            # AI服务
            'ai': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/ai.txt',
                'path': './ruleset/ai.yaml',
                'interval': 86400
            },
            
            # 电报消息
            'telegram_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/telegram.txt',
                'path': './ruleset/telegram_non_ip.yaml',
                'interval': 86400
            },
            'telegram_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/telegram.txt',
                'path': './ruleset/telegram_ip.yaml',
                'interval': 86400
            },
            
            # 流媒体服务
            'stream_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream.txt',
                'path': './ruleset/stream_non_ip.yaml',
                'interval': 86400
            },
            'stream_us': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_us.txt',
                'path': './ruleset/stream_us.yaml',
                'interval': 86400
            },
            'stream_eu': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_eu.txt',
                'path': './ruleset/stream_eu.yaml',
                'interval': 86400
            },
            'stream_jp': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_jp.txt',
                'path': './ruleset/stream_jp.yaml',
                'interval': 86400
            },
            'stream_kr': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_kr.txt',
                'path': './ruleset/stream_kr.yaml',
                'interval': 86400
            },
            'stream_hk': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_hk.txt',
                'path': './ruleset/stream_hk.yaml',
                'interval': 86400
            },
            'stream_tw': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/stream_tw.txt',
                'path': './ruleset/stream_tw.yaml',
                'interval': 86400
            },
            'stream_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/stream.txt',
                'path': './ruleset/stream_ip.yaml',
                'interval': 86400
            },
            
            # 微软服务
            'microsoft_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/microsoft.txt',
                'path': './ruleset/microsoft_non_ip.yaml',
                'interval': 86400
            },
            'microsoft_cdn': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/microsoft_cdn.txt',
                'path': './ruleset/microsoft_cdn.yaml',
                'interval': 86400
            },
            
            # 苹果服务
            'apple_services': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/apple_services.txt',
                'path': './ruleset/apple_services.yaml',
                'interval': 86400
            },
            'apple_cn': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/apple_cn.txt',
                'path': './ruleset/apple_cn.yaml',
                'interval': 86400
            },
            'apple_cdn': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/apple_cdn.txt',
                'path': './ruleset/apple_cdn.yaml',
                'interval': 86400
            },
            
            # 网易云音乐
            'neteasemusic_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/neteasemusic.txt',
                'path': './ruleset/neteasemusic_non_ip.yaml',
                'interval': 86400
            },
            'neteasemusic_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/neteasemusic.txt',
                'path': './ruleset/neteasemusic_ip.yaml',
                'interval': 86400
            },
            
            # 隐私保护
            'sogouinput': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/sogouinput.txt',
                'path': './ruleset/sogouinput.yaml',
                'interval': 86400
            },
            
            # CDN优化
            'cdn_domainset': {
                'type': 'http',
                'behavior': 'domain',
                'url': f'{base_url}/clash/domainset/cdn.txt',
                'path': './ruleset/cdn_domainset.yaml',
                'interval': 86400
            },
            'cdn_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/cdn.txt',
                'path': './ruleset/cdn_non_ip.yaml',
                'interval': 86400
            },
            'cdn_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/cdn.txt',
                'path': './ruleset/cdn_ip.yaml',
                'interval': 86400
            },
            
            # 下载优化
            'download_domainset': {
                'type': 'http',
                'behavior': 'domain',
                'url': f'{base_url}/clash/domainset/download.txt',
                'path': './ruleset/download_domainset.yaml',
                'interval': 86400
            },
            'download_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/download.txt',
                'path': './ruleset/download_non_ip.yaml',
                'interval': 86400
            },
            'download_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/download.txt',
                'path': './ruleset/download_ip.yaml',
                'interval': 86400
            },
            
            # 国内服务
            'domestic_non_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/domestic.txt',
                'path': './ruleset/domestic_non_ip.yaml',
                'interval': 86400
            },
            'domestic_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/domestic.txt',
                'path': './ruleset/domestic_ip.yaml',
                'interval': 86400
            },
            
            # 全球代理
            'global': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/global.txt',
                'path': './ruleset/global.yaml',
                'interval': 86400
            },
            
            # 直连服务
            'direct': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/non_ip/direct.txt',
                'path': './ruleset/direct.yaml',
                'interval': 86400
            },
            
            # 中国IP
            'china_ip': {
                'type': 'http',
                'behavior': 'classical',
                'url': f'{base_url}/clash/ip/china_ip.txt',
                'path': './ruleset/china_ip.yaml',
                'interval': 86400
            }
        }
        
        # Rules
        config['rules'] = [
            # GitHub服务 (优先处理避免DNS污染)
            'RULE-SET,github,🚀 节点选择',
            
            # 局域网规则
            'RULE-SET,lan_ip,🎯 全球直连',
            'RULE-SET,lan_non_ip,🎯 全球直连',
            
            # 拦截规则 (按DNS解析性能优化排序)
            'RULE-SET,reject_domainset,🛑 全球拦截',
            'RULE-SET,reject_extra,🛑 全球拦截',
            'RULE-SET,reject_phishing,🛑 全球拦截',
            'RULE-SET,reject_non_ip,🛑 全球拦截',
            'RULE-SET,reject_drop,🛑 全球拦截',
            'RULE-SET,reject_no_drop,🍃 应用净化',
            'RULE-SET,reject_ip,🛑 全球拦截',
            
            # AI服务
            'RULE-SET,ai,🤖 人工智能',
            
            # 电报消息
            'RULE-SET,telegram_non_ip,📲 电报消息',
            'RULE-SET,telegram_ip,📲 电报消息',
            
            # 流媒体服务
            'RULE-SET,stream_non_ip,🎥 流媒体',
            'RULE-SET,stream_us,🎥 流媒体',
            'RULE-SET,stream_eu,🎥 流媒体',
            'RULE-SET,stream_jp,🎥 流媒体',
            'RULE-SET,stream_kr,🎥 流媒体',
            'RULE-SET,stream_hk,🎥 流媒体',
            'RULE-SET,stream_tw,🎥 流媒体',
            'RULE-SET,stream_ip,🎥 流媒体',
            
            # 微软服务
            'RULE-SET,microsoft_non_ip,Ⓜ️ 微软服务',
            'RULE-SET,microsoft_cdn,Ⓜ️ 微软服务',
            
            # 苹果服务
            'RULE-SET,apple_services,🍎 苹果服务',
            'RULE-SET,apple_cn,🍎 苹果服务',
            'RULE-SET,apple_cdn,🍎 苹果服务',
            
            # 网易云音乐
            'RULE-SET,neteasemusic_non_ip,🎯 全球直连',
            'RULE-SET,neteasemusic_ip,🎯 全球直连',
            
            # 隐私保护
            'RULE-SET,sogouinput,🛑 全球拦截',
            
            # CDN优化
            'RULE-SET,cdn_domainset,🎯 全球直连',
            'RULE-SET,cdn_non_ip,🎯 全球直连',
            'RULE-SET,cdn_ip,🎯 全球直连',
            
            # 下载优化
            'RULE-SET,download_domainset,🎯 全球直连',
            'RULE-SET,download_non_ip,🎯 全球直连',
            'RULE-SET,download_ip,🎯 全球直连',
            
            # 国内服务
            'RULE-SET,domestic_non_ip,🎯 全球直连',
            'RULE-SET,domestic_ip,🎯 全球直连',
            
            # 全球代理
            'RULE-SET,global,🚀 节点选择',
            
            # 直连服务
            'RULE-SET,direct,🎯 全球直连',
            
            # 中国IP
            'RULE-SET,china_ip,🎯 全球直连',
            
            # 私有IP段
            'IP-CIDR,192.168.0.0/16,🎯 全球直连',
            'IP-CIDR,10.0.0.0/8,🎯 全球直连',
            'IP-CIDR,172.16.0.0/12,🎯 全球直连',
            'IP-CIDR,127.0.0.0/8,🎯 全球直连',
            
            # 最终规则
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
    parser.add_argument('--upload', action='store_true', help='Upload to private GitHub Gist and generate QR codes')
    parser.add_argument('--github-token', help='GitHub personal access token for Gist upload')
    
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
    
    # Upload to Gist if requested
    if args.upload:
        generated_files = []
        if args.format in ['surge', 'both']:
            generated_files.append(surge_file)
        if args.format in ['clash', 'both']:
            generated_files.append(clash_file)
        
        try:
            from gist_uploader import GistUploader
            uploader = GistUploader(args.github_token)
            
            print("\n📤 上传配置文件到私有 GitHub Gist...")
            gist = uploader.upload_files(
                files=generated_files,
                description=f"Proxy Config - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                public=False
            )
            
            if gist:
                raw_urls = uploader.get_raw_urls(gist)
                uploader.generate_qr_codes(raw_urls)
                
                print("\n🎉 上传成功!")
                print("📱 扫描二维码即可导入配置!")
                print(f"🔗 Gist 地址: {gist.html_url}")
                print("🔒 这是私有 Gist，只有知道链接的人才能访问")
            
        except ImportError:
            print("\n❌ 缺少依赖库，请安装:")
            print("pip install qrcode[pil] PyGithub")
        except Exception as e:
            print(f"\n❌ 上传失败: {e}")


if __name__ == '__main__':
    main()