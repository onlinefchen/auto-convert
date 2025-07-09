class ProxyConverter {
    constructor() {
        // 内存中暂存数据，不持久化
        this.tempData = {
            subscriptionUrl: '',
            githubToken: '',
            outputFormat: 'both'
        };
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('convertForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // 监听输入变化，在内存中暂存
        const subscriptionUrl = document.getElementById('subscriptionUrl');
        const githubToken = document.getElementById('githubToken');
        const outputFormat = document.getElementById('outputFormat');
        
        subscriptionUrl.addEventListener('input', () => {
            this.tempData.subscriptionUrl = subscriptionUrl.value;
        });
        githubToken.addEventListener('input', () => {
            this.tempData.githubToken = githubToken.value;
        });
        outputFormat.addEventListener('change', () => {
            this.tempData.outputFormat = outputFormat.value;
        });
    }

    clearTempData() {
        this.tempData = {
            subscriptionUrl: '',
            githubToken: '',
            outputFormat: 'both'
        };
        document.getElementById('subscriptionUrl').value = '';
        document.getElementById('githubToken').value = '';
        document.getElementById('outputFormat').value = 'both';
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const subscriptionUrl = document.getElementById('subscriptionUrl').value;
        const outputFormat = document.getElementById('outputFormat').value;
        const githubToken = document.getElementById('githubToken').value;

        if (!subscriptionUrl) {
            this.showAlert('请输入订阅链接', 'danger');
            return;
        }

        this.showLoading(true);
        this.hideResults();

        try {
            // 获取订阅内容
            const subscriptionContent = await this.fetchSubscription(subscriptionUrl);
            
            // 解析代理
            const proxies = this.parseProxies(subscriptionContent);
            
            if (proxies.length === 0) {
                throw new Error('未找到有效的代理节点');
            }

            // 生成配置
            const configs = await this.generateConfigs(proxies, outputFormat);
            
            // 如果有 GitHub Token，上传到 Gist
            let gistResults = null;
            if (githubToken) {
                gistResults = await this.uploadToGist(configs, githubToken);
            }

            // 显示结果
            this.showResults(configs, gistResults);
            
        } catch (error) {
            console.error('转换失败:', error);
            this.showAlert(`转换失败: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    async fetchSubscription(url) {
        try {
            // 使用 CORS 代理服务获取订阅内容
            const proxyUrl = `https://cors-anywhere.herokuapp.com/${url}`;
            const response = await fetch(proxyUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.text();
        } catch (error) {
            // 如果代理失败，尝试直接请求
            try {
                const response = await fetch(url);
                return await response.text();
            } catch (directError) {
                throw new Error('无法获取订阅内容，请检查链接是否正确或尝试其他方式');
            }
        }
    }

    parseProxies(content) {
        const proxies = [];
        
        // 尝试 base64 解码
        let decodedContent;
        try {
            decodedContent = atob(content);
        } catch {
            decodedContent = content;
        }
        
        const lines = decodedContent.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
            if (line.startsWith('vmess://')) {
                const proxy = this.parseVmess(line);
                if (proxy) proxies.push(proxy);
            } else if (line.startsWith('ss://')) {
                const proxy = this.parseShadowsocks(line);
                if (proxy) proxies.push(proxy);
            } else if (line.startsWith('trojan://')) {
                const proxy = this.parseTrojan(line);
                if (proxy) proxies.push(proxy);
            }
        }
        
        return proxies;
    }

    parseVmess(vmessUrl) {
        try {
            const vmessData = vmessUrl.substring(8); // 移除 'vmess://'
            const decoded = atob(vmessData);
            const config = JSON.parse(decoded);
            
            return {
                type: 'vmess',
                name: config.ps || 'VMess',
                server: config.add,
                port: parseInt(config.port),
                uuid: config.id,
                alterId: parseInt(config.aid || 0),
                cipher: config.scy || 'auto',
                network: config.net || 'tcp',
                tls: config.tls === 'tls',
                sni: config.sni || config.host || '',
                wsPath: config.path || '',
                wsHost: config.host || ''
            };
        } catch (error) {
            console.warn('VMess 解析失败:', error);
            return null;
        }
    }

    parseShadowsocks(ssUrl) {
        try {
            const ssData = ssUrl.substring(5); // 移除 'ss://'
            let name = 'Shadowsocks';
            let mainPart = ssData;
            
            // 提取名称
            if (ssData.includes('#')) {
                [mainPart, name] = ssData.split('#');
                name = decodeURIComponent(name);
            }
            
            // 解析主要部分
            let method, password, server, port;
            
            if (mainPart.includes('@')) {
                // SIP002 格式
                const [encodedAuth, serverInfo] = mainPart.split('@');
                try {
                    const auth = atob(encodedAuth);
                    [method, password] = auth.split(':', 2);
                } catch {
                    [method, password] = encodedAuth.split(':', 2);
                }
                [server, port] = serverInfo.split(':');
            } else {
                // 传统格式
                const decoded = atob(mainPart);
                const [auth, serverInfo] = decoded.split('@');
                [method, password] = auth.split(':', 2);
                [server, port] = serverInfo.split(':');
            }
            
            return {
                type: 'ss',
                name: name,
                server: server,
                port: parseInt(port),
                cipher: method,
                password: password
            };
        } catch (error) {
            console.warn('Shadowsocks 解析失败:', error);
            return null;
        }
    }

    parseTrojan(trojanUrl) {
        try {
            const trojanData = trojanUrl.substring(9); // 移除 'trojan://'
            let name = 'Trojan';
            let mainPart = trojanData;
            
            if (trojanData.includes('#')) {
                [mainPart, name] = trojanData.split('#');
                name = decodeURIComponent(name);
            }
            
            const [password, serverPort] = mainPart.split('@');
            const [server, port] = serverPort.split(':');
            
            return {
                type: 'trojan',
                name: name,
                server: server,
                port: parseInt(port),
                password: password,
                sni: server
            };
        } catch (error) {
            console.warn('Trojan 解析失败:', error);
            return null;
        }
    }

    async generateConfigs(proxies, format) {
        const configs = {};
        const timestamp = new Date().toLocaleString('zh-CN');
        
        if (format === 'surge' || format === 'both') {
            configs.surge = await this.generateSurgeConfig(proxies, timestamp);
        }
        
        if (format === 'clash' || format === 'both') {
            configs.clash = this.generateClashConfig(proxies, timestamp);
        }
        
        return configs;
    }

    async generateSurgeConfig(proxies, timestamp) {
        const lines = [];
        
        // Header
        lines.push('#!MANAGED-CONFIG interval=43200');
        lines.push(`# Generated at ${timestamp}`);
        lines.push('# Auto Proxy Subscription Converter');
        lines.push('');
        
        // General
        lines.push('[General]');
        lines.push('skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local');
        lines.push('dns-server = 119.29.29.29, 223.5.5.5, system');
        lines.push('loglevel = notify');
        lines.push('internet-test-url = http://www.aliyun.com');
        lines.push('proxy-test-url = http://www.google.com/generate_204');
        lines.push('test-timeout = 5');
        lines.push('ipv6 = false');
        lines.push('');
        
        // Proxies
        lines.push('[Proxy]');
        for (const proxy of proxies) {
            const proxyLine = this.generateSurgeProxy(proxy);
            if (proxyLine) lines.push(proxyLine);
        }
        lines.push('');
        
        // Proxy Groups
        lines.push('[Proxy Group]');
        const proxyNames = proxies.map(p => p.name);
        if (proxyNames.length > 0) {
            lines.push(`🚀 节点选择 = select, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`♻️ 自动选择 = url-test, ${proxyNames.join(', ')}, url=http://www.google.com/generate_204, interval=300`);
            lines.push(`🤖 人工智能 = select, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`📲 电报消息 = select, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`🎥 流媒体 = select, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`Ⓜ️ 微软服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`🍎 苹果服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push('🎯 全球直连 = select, DIRECT, 🚀 节点选择');
            lines.push('🛑 全球拦截 = select, REJECT, DIRECT');
            lines.push('🍃 应用净化 = select, REJECT, DIRECT');
            lines.push('🐟 漏网之鱼 = select, 🚀 节点选择, ♻️ 自动选择, DIRECT');
        }
        lines.push('');
        
        // Rules (按DNS解析行为组织)
        lines.push('[Rule]');
        
        // 本地/局域网地址 (DNS解析: 是/否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/lan.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/lan.conf,🎯 全球直连');
        lines.push('');
        
        // 拦截规则 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/domainset/reject.conf,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/domainset/reject_extra.conf,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/domainset/reject_phishing.conf,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/reject.conf,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/reject_drop.conf,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/reject_no_drop.conf,🍃 应用净化');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/reject.conf,🛑 全球拦截');
        lines.push('');
        
        // AI服务 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/ai.conf,🤖 人工智能');
        lines.push('');
        
        // 电报消息 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/telegram.conf,📲 电报消息');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/telegram.conf,📲 电报消息');
        lines.push('');
        
        // 流媒体 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_us.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_eu.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_jp.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_kr.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_hk.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/stream_tw.conf,🎥 流媒体');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/stream.conf,🎥 流媒体');
        lines.push('');
        
        // 微软服务 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/microsoft.conf,Ⓜ️ 微软服务');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/microsoft_cdn.conf,Ⓜ️ 微软服务');
        lines.push('');
        
        // 苹果服务 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/apple_services.conf,🍎 苹果服务');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/apple_cn.conf,🍎 苹果服务');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/apple_cdn.conf,🍎 苹果服务');
        lines.push('');
        
        // 网易云音乐 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/neteasemusic.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/neteasemusic.conf,🎯 全球直连');
        lines.push('');
        
        // 隐私保护 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/sogouinput.conf,🛑 全球拦截');
        lines.push('');
        
        // CDN优化 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/domainset/cdn.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/cdn.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/cdn.conf,🎯 全球直连');
        lines.push('');
        
        // 下载优化 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/domainset/download.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/download.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/download.conf,🎯 全球直连');
        lines.push('');
        
        // 国内服务 (DNS解析: 否/是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/domestic.conf,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/domestic.conf,🎯 全球直连');
        lines.push('');
        
        // 全球代理 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/global.conf,🚀 节点选择');
        lines.push('');
        
        // 直连服务 (DNS解析: 否)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/non_ip/direct.conf,🎯 全球直连');
        lines.push('');
        
        // 中国IP (DNS解析: 是)
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/surge/ip/china_ip.conf,🎯 全球直连');
        lines.push('');
        
        // 漏网之鱼
        lines.push('FINAL,🐟 漏网之鱼');
        
        return lines.join('\n');
    }

    generateSurgeProxy(proxy) {
        const { type, name, server, port } = proxy;
        
        switch (type) {
            case 'vmess':
                let vmessLine = `${name} = vmess, ${server}, ${port}, username=${proxy.uuid}`;
                if (proxy.tls) {
                    vmessLine += ', tls=true';
                    if (proxy.sni) vmessLine += `, sni=${proxy.sni}`;
                }
                if (proxy.wsPath) {
                    vmessLine += ', ws=true';
                    vmessLine += `, ws-path=${proxy.wsPath}`;
                    if (proxy.wsHost) vmessLine += `, ws-headers=Host:${proxy.wsHost}`;
                }
                return vmessLine;
                
            case 'ss':
                return `${name} = ss, ${server}, ${port}, encrypt-method=${proxy.cipher}, password=${proxy.password}`;
                
            case 'trojan':
                let trojanLine = `${name} = trojan, ${server}, ${port}, password=${proxy.password}`;
                if (proxy.sni) trojanLine += `, sni=${proxy.sni}`;
                return trojanLine;
                
            default:
                return null;
        }
    }

    generateClashConfig(proxies, timestamp) {
        const config = {
            port: 7890,
            'socks-port': 7891,
            'allow-lan': false,
            mode: 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            dns: {
                enable: true,
                nameserver: ['119.29.29.29', '223.5.5.5'],
                fallback: ['8.8.8.8', '1.1.1.1']
            },
            proxies: [],
            'proxy-groups': [],
            rules: []
        };
        
        // Proxies
        for (const proxy of proxies) {
            const clashProxy = this.generateClashProxy(proxy);
            if (clashProxy) config.proxies.push(clashProxy);
        }
        
        // Proxy Groups
        const proxyNames = proxies.map(p => p.name);
        if (proxyNames.length > 0) {
            config['proxy-groups'] = [
                {
                    name: '🚀 节点选择',
                    type: 'select',
                    proxies: ['♻️ 自动选择', ...proxyNames]
                },
                {
                    name: '♻️ 自动选择',
                    type: 'url-test',
                    proxies: proxyNames,
                    url: 'http://www.google.com/generate_204',
                    interval: 300
                },
                {
                    name: '🤖 人工智能',
                    type: 'select',
                    proxies: ['🚀 节点选择', '♻️ 自动选择', ...proxyNames]
                },
                {
                    name: '📲 电报消息',
                    type: 'select',
                    proxies: ['🚀 节点选择', '♻️ 自动选择', ...proxyNames]
                },
                {
                    name: '🎥 流媒体',
                    type: 'select',
                    proxies: ['🚀 节点选择', '♻️ 自动选择', ...proxyNames]
                },
                {
                    name: 'Ⓜ️ 微软服务',
                    type: 'select',
                    proxies: ['DIRECT', '🚀 节点选择', '♻️ 自动选择', ...proxyNames]
                },
                {
                    name: '🍎 苹果服务',
                    type: 'select',
                    proxies: ['DIRECT', '🚀 节点选择', '♻️ 自动选择', ...proxyNames]
                },
                {
                    name: '🎯 全球直连',
                    type: 'select',
                    proxies: ['DIRECT', '🚀 节点选择']
                },
                {
                    name: '🛑 全球拦截',
                    type: 'select',
                    proxies: ['REJECT', 'DIRECT']
                },
                {
                    name: '🍃 应用净化',
                    type: 'select',
                    proxies: ['REJECT', 'DIRECT']
                },
                {
                    name: '🐟 漏网之鱼',
                    type: 'select',
                    proxies: ['🚀 节点选择', '♻️ 自动选择', 'DIRECT']
                }
            ];
        }
        
        // Rule-providers配置(按DNS解析行为组织)
        config['rule-providers'] = {
            // 本地/局域网地址 (DNS解析: 是/否)
            'lan_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/lan.txt',
                path: './rules/lan_ip.yaml',
                interval: 43200
            },
            'lan_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/lan.txt',
                path: './rules/lan_non_ip.yaml',
                interval: 43200
            },
            
            // 拦截规则 (DNS解析: 否/是)
            'reject_domainset': {
                type: 'http',
                behavior: 'domain',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/domainset/reject.txt',
                path: './rules/reject_domainset.yaml',
                interval: 43200
            },
            'reject_extra_domainset': {
                type: 'http',
                behavior: 'domain',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/domainset/reject_extra.txt',
                path: './rules/reject_extra_domainset.yaml',
                interval: 43200
            },
            'reject_phishing_domainset': {
                type: 'http',
                behavior: 'domain',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/domainset/reject_phishing.txt',
                path: './rules/reject_phishing_domainset.yaml',
                interval: 43200
            },
            'reject_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/reject.txt',
                path: './rules/reject_non_ip.yaml',
                interval: 43200
            },
            'reject_drop': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/reject_drop.txt',
                path: './rules/reject_drop.yaml',
                interval: 43200
            },
            'reject_no_drop': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/reject_no_drop.txt',
                path: './rules/reject_no_drop.yaml',
                interval: 43200
            },
            'reject_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/reject.txt',
                path: './rules/reject_ip.yaml',
                interval: 43200
            },
            
            // AI服务 (DNS解析: 否)
            'ai': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/ai.txt',
                path: './rules/ai.yaml',
                interval: 43200
            },
            
            // 电报消息 (DNS解析: 否/是)
            'telegram_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/telegram.txt',
                path: './rules/telegram_non_ip.yaml',
                interval: 43200
            },
            'telegram_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/telegram.txt',
                path: './rules/telegram_ip.yaml',
                interval: 43200
            },
            
            // 流媒体 (DNS解析: 否/是)
            'stream_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream.txt',
                path: './rules/stream_non_ip.yaml',
                interval: 43200
            },
            'stream_us': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_us.txt',
                path: './rules/stream_us.yaml',
                interval: 43200
            },
            'stream_eu': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_eu.txt',
                path: './rules/stream_eu.yaml',
                interval: 43200
            },
            'stream_jp': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_jp.txt',
                path: './rules/stream_jp.yaml',
                interval: 43200
            },
            'stream_kr': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_kr.txt',
                path: './rules/stream_kr.yaml',
                interval: 43200
            },
            'stream_hk': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_hk.txt',
                path: './rules/stream_hk.yaml',
                interval: 43200
            },
            'stream_tw': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/stream_tw.txt',
                path: './rules/stream_tw.yaml',
                interval: 43200
            },
            'stream_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/stream.txt',
                path: './rules/stream_ip.yaml',
                interval: 43200
            },
            
            // 微软服务 (DNS解析: 否)
            'microsoft': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/microsoft.txt',
                path: './rules/microsoft.yaml',
                interval: 43200
            },
            'microsoft_cdn': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/microsoft_cdn.txt',
                path: './rules/microsoft_cdn.yaml',
                interval: 43200
            },
            
            // 苹果服务 (DNS解析: 否)
            'apple_services': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/apple_services.txt',
                path: './rules/apple_services.yaml',
                interval: 43200
            },
            'apple_cn': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/apple_cn.txt',
                path: './rules/apple_cn.yaml',
                interval: 43200
            },
            'apple_cdn': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/apple_cdn.txt',
                path: './rules/apple_cdn.yaml',
                interval: 43200
            },
            
            // 网易云音乐 (DNS解析: 否/是)
            'neteasemusic_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/neteasemusic.txt',
                path: './rules/neteasemusic_non_ip.yaml',
                interval: 43200
            },
            'neteasemusic_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/neteasemusic.txt',
                path: './rules/neteasemusic_ip.yaml',
                interval: 43200
            },
            
            // 隐私保护 (DNS解析: 否)
            'sogouinput': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/sogouinput.txt',
                path: './rules/sogouinput.yaml',
                interval: 43200
            },
            
            // CDN优化 (DNS解析: 否/是)
            'cdn_domainset': {
                type: 'http',
                behavior: 'domain',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/domainset/cdn.txt',
                path: './rules/cdn_domainset.yaml',
                interval: 43200
            },
            'cdn_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/cdn.txt',
                path: './rules/cdn_non_ip.yaml',
                interval: 43200
            },
            'cdn_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/cdn.txt',
                path: './rules/cdn_ip.yaml',
                interval: 43200
            },
            
            // 下载优化 (DNS解析: 否/是)
            'download_domainset': {
                type: 'http',
                behavior: 'domain',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/domainset/download.txt',
                path: './rules/download_domainset.yaml',
                interval: 43200
            },
            'download_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/download.txt',
                path: './rules/download_non_ip.yaml',
                interval: 43200
            },
            'download_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/download.txt',
                path: './rules/download_ip.yaml',
                interval: 43200
            },
            
            // 国内服务 (DNS解析: 否/是)
            'domestic_non_ip': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/domestic.txt',
                path: './rules/domestic_non_ip.yaml',
                interval: 43200
            },
            'domestic_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/domestic.txt',
                path: './rules/domestic_ip.yaml',
                interval: 43200
            },
            
            // 全球代理 (DNS解析: 否)
            'global': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/global.txt',
                path: './rules/global.yaml',
                interval: 43200
            },
            
            // 直连服务 (DNS解析: 否)
            'direct': {
                type: 'http',
                behavior: 'classical',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/non_ip/direct.txt',
                path: './rules/direct.yaml',
                interval: 43200
            },
            
            // 中国IP (DNS解析: 是)
            'china_ip': {
                type: 'http',
                behavior: 'ipcidr',
                url: 'https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/clash/ip/china_ip.txt',
                path: './rules/china_ip.yaml',
                interval: 43200
            }
        };
        
        // Rules (按DNS解析行为优化的完整规则集)
        config.rules = [
            // 本地/局域网地址 (DNS解析: 是/否)
            'RULE-SET,lan_ip,🎯 全球直连',
            'RULE-SET,lan_non_ip,🎯 全球直连',
            
            // 拦截规则 (DNS解析: 否/是)
            'RULE-SET,reject_domainset,🛑 全球拦截',
            'RULE-SET,reject_extra_domainset,🛑 全球拦截',
            'RULE-SET,reject_phishing_domainset,🛑 全球拦截',
            'RULE-SET,reject_non_ip,🛑 全球拦截',
            'RULE-SET,reject_drop,🛑 全球拦截',
            'RULE-SET,reject_no_drop,🍃 应用净化',
            'RULE-SET,reject_ip,🛑 全球拦截',
            
            // AI服务 (DNS解析: 否)
            'RULE-SET,ai,🤖 人工智能',
            
            // 电报消息 (DNS解析: 否/是)
            'RULE-SET,telegram_non_ip,📲 电报消息',
            'RULE-SET,telegram_ip,📲 电报消息',
            
            // 流媒体 (DNS解析: 否/是)
            'RULE-SET,stream_non_ip,🎥 流媒体',
            'RULE-SET,stream_us,🎥 流媒体',
            'RULE-SET,stream_eu,🎥 流媒体',
            'RULE-SET,stream_jp,🎥 流媒体',
            'RULE-SET,stream_kr,🎥 流媒体',
            'RULE-SET,stream_hk,🎥 流媒体',
            'RULE-SET,stream_tw,🎥 流媒体',
            'RULE-SET,stream_ip,🎥 流媒体',
            
            // 微软服务 (DNS解析: 否)
            'RULE-SET,microsoft,Ⓜ️ 微软服务',
            'RULE-SET,microsoft_cdn,Ⓜ️ 微软服务',
            
            // 苹果服务 (DNS解析: 否)
            'RULE-SET,apple_services,🍎 苹果服务',
            'RULE-SET,apple_cn,🍎 苹果服务',
            'RULE-SET,apple_cdn,🍎 苹果服务',
            
            // 网易云音乐 (DNS解析: 否/是)
            'RULE-SET,neteasemusic_non_ip,🎯 全球直连',
            'RULE-SET,neteasemusic_ip,🎯 全球直连',
            
            // 隐私保护 (DNS解析: 否)
            'RULE-SET,sogouinput,🛑 全球拦截',
            
            // CDN优化 (DNS解析: 否/是)
            'RULE-SET,cdn_domainset,🎯 全球直连',
            'RULE-SET,cdn_non_ip,🎯 全球直连',
            'RULE-SET,cdn_ip,🎯 全球直连',
            
            // 下载优化 (DNS解析: 否/是)
            'RULE-SET,download_domainset,🎯 全球直连',
            'RULE-SET,download_non_ip,🎯 全球直连',
            'RULE-SET,download_ip,🎯 全球直连',
            
            // 国内服务 (DNS解析: 否/是)
            'RULE-SET,domestic_non_ip,🎯 全球直连',
            'RULE-SET,domestic_ip,🎯 全球直连',
            
            // 全球代理 (DNS解析: 否)
            'RULE-SET,global,🚀 节点选择',
            
            // 直连服务 (DNS解析: 否)
            'RULE-SET,direct,🎯 全球直连',
            
            // 中国IP (DNS解析: 是)
            'RULE-SET,china_ip,🎯 全球直连',
            
            // 漏网之鱼
            'MATCH,🐟 漏网之鱼'
        ];
        
        return JSON.stringify(config, null, 2);
    }

    generateClashProxy(proxy) {
        const { type, name, server, port } = proxy;
        
        switch (type) {
            case 'vmess':
                const vmessProxy = {
                    name,
                    type: 'vmess',
                    server,
                    port,
                    uuid: proxy.uuid,
                    alterId: proxy.alterId,
                    cipher: proxy.cipher
                };
                
                if (proxy.tls) {
                    vmessProxy.tls = true;
                    if (proxy.sni) vmessProxy.servername = proxy.sni;
                }
                
                if (proxy.network === 'ws') {
                    vmessProxy.network = 'ws';
                    vmessProxy['ws-opts'] = {};
                    if (proxy.wsPath) vmessProxy['ws-opts'].path = proxy.wsPath;
                    if (proxy.wsHost) vmessProxy['ws-opts'].headers = { Host: proxy.wsHost };
                }
                
                return vmessProxy;
                
            case 'ss':
                return {
                    name,
                    type: 'ss',
                    server,
                    port,
                    cipher: proxy.cipher,
                    password: proxy.password
                };
                
            case 'trojan':
                const trojanProxy = {
                    name,
                    type: 'trojan',
                    server,
                    port,
                    password: proxy.password
                };
                
                if (proxy.sni) trojanProxy.sni = proxy.sni;
                return trojanProxy;
                
            default:
                return null;
        }
    }

    async uploadToGist(configs, token) {
        try {
            const files = {};
            
            if (configs.surge) {
                files['config.surge.conf'] = { content: configs.surge };
            }
            
            if (configs.clash) {
                files['config.clash.yaml'] = { content: configs.clash };
            }
            
            const gistData = {
                description: `Proxy Config - Generated at ${new Date().toLocaleString('zh-CN')}`,
                public: false,
                files: files
            };
            
            const response = await fetch('https://api.github.com/gists', {
                method: 'POST',
                headers: {
                    'Authorization': `token ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gistData)
            });
            
            if (!response.ok) {
                throw new Error(`GitHub API 错误: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Gist 上传失败:', error);
            throw new Error(`Gist 上传失败: ${error.message}`);
        }
    }

    showResults(configs, gistResults) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        
        Object.keys(configs).forEach(format => {
            const resultCard = document.createElement('div');
            resultCard.className = 'result-card';
            
            const title = format === 'surge' ? 'Surge 配置' : 'Clash 配置';
            const icon = format === 'surge' ? 'fas fa-mobile-alt' : 'fas fa-bolt';
            
            let content = `
                <h3><i class="${icon}"></i> ${title}</h3>
                <div class="link-box">
                    <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
                    <pre style="margin: 0; white-space: pre-wrap;">${configs[format]}</pre>
                </div>
            `;
            
            // 如果有 Gist 结果，显示链接和二维码
            if (gistResults && gistResults.files) {
                const fileName = format === 'surge' ? 'config.surge.conf' : 'config.clash.yaml';
                const fileData = gistResults.files[fileName];
                
                if (fileData) {
                    const rawUrl = fileData.raw_url;
                    
                    content += `
                        <div style="margin-top: 20px;">
                            <h4><i class="fas fa-link"></i> Gist 直链</h4>
                            <div class="link-box">
                                <button class="copy-btn" onclick="copyToClipboard(this, '${rawUrl}')">复制链接</button>
                                <code>${rawUrl}</code>
                            </div>
                            
                            <div class="qr-code" id="qr-${format}">
                                <h4><i class="fas fa-qrcode"></i> 扫码导入</h4>
                            </div>
                        </div>
                    `;
                    
                    // 延迟生成二维码，确保 DOM 已渲染
                    setTimeout(() => this.generateQRCode(`qr-${format}`, rawUrl), 100);
                }
            }
            
            resultCard.innerHTML = content;
            resultsDiv.appendChild(resultCard);
        });
        
        if (gistResults) {
            const gistCard = document.createElement('div');
            gistCard.className = 'result-card';
            gistCard.innerHTML = `
                <h3><i class="fab fa-github"></i> GitHub Gist</h3>
                <div class="link-box">
                    <button class="copy-btn" onclick="copyToClipboard(this, '${gistResults.html_url}')">复制链接</button>
                    <code>${gistResults.html_url}</code>
                </div>
                <p style="margin-top: 10px; color: #666;">
                    <i class="fas fa-lock"></i> 这是私有 Gist，只有知道链接的人才能访问
                </p>
            `;
            resultsDiv.appendChild(gistCard);
        }
        
        resultsDiv.style.display = 'block';
    }

    generateQRCode(containerId, text) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        try {
            // 使用 qrcode.js 生成二维码
            const qr = qrcode(0, 'M');
            qr.addData(text);
            qr.make();
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const moduleCount = qr.getModuleCount();
            const cellSize = 4;
            const margin = 20;
            
            canvas.width = canvas.height = moduleCount * cellSize + margin * 2;
            
            // 背景
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 二维码
            ctx.fillStyle = '#000000';
            for (let row = 0; row < moduleCount; row++) {
                for (let col = 0; col < moduleCount; col++) {
                    if (qr.isDark(row, col)) {
                        ctx.fillRect(
                            col * cellSize + margin,
                            row * cellSize + margin,
                            cellSize,
                            cellSize
                        );
                    }
                }
            }
            
            container.appendChild(canvas);
            
        } catch (error) {
            console.error('二维码生成失败:', error);
            container.innerHTML += '<p style="color: #666;">二维码生成失败</p>';
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const button = document.getElementById('convertBtn');
        
        if (show) {
            loading.style.display = 'block';
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 转换中...';
        } else {
            loading.style.display = 'none';
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-magic"></i> 开始转换';
        }
    }

    hideResults() {
        const results = document.getElementById('results');
        results.style.display = 'none';
    }

    showAlert(message, type = 'info') {
        // 移除现有的 alert
        const existingAlert = document.querySelector('.alert');
        if (existingAlert && existingAlert.parentNode === document.querySelector('.main-card')) {
            existingAlert.remove();
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        
        const mainCard = document.querySelector('.main-card');
        mainCard.appendChild(alert);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// 复制功能
function copyToClipboard(button, customText = null) {
    let textToCopy;
    
    if (customText) {
        textToCopy = customText;
    } else {
        const linkBox = button.parentNode;
        const textElement = linkBox.querySelector('pre, code');
        textToCopy = textElement.textContent;
    }
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = button.textContent;
        button.textContent = '已复制!';
        button.style.background = '#28a745';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '#6c757d';
        }, 2000);
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制');
    });
}

// 全局变量用于存储 ProxyConverter 实例
let proxyConverterInstance;

// 清除暂存数据的全局函数
function clearTempData() {
    if (proxyConverterInstance) {
        proxyConverterInstance.clearTempData();
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    proxyConverterInstance = new ProxyConverter();
});