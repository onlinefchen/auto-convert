class ProxyConverter {
    constructor() {
        this.initializeEventListeners();
        this.loadSavedData();
    }

    initializeEventListeners() {
        const form = document.getElementById('convertForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // 监听输入变化，自动保存
        const subscriptionUrl = document.getElementById('subscriptionUrl');
        const githubToken = document.getElementById('githubToken');
        const outputFormat = document.getElementById('outputFormat');
        
        subscriptionUrl.addEventListener('input', () => this.saveData());
        githubToken.addEventListener('input', () => this.saveData());
        outputFormat.addEventListener('change', () => this.saveData());
    }

    loadSavedData() {
        try {
            const savedData = localStorage.getItem('proxyConverterData');
            if (savedData) {
                const data = JSON.parse(savedData);
                
                if (data.subscriptionUrl) {
                    document.getElementById('subscriptionUrl').value = data.subscriptionUrl;
                }
                if (data.githubToken) {
                    document.getElementById('githubToken').value = data.githubToken;
                }
                if (data.outputFormat) {
                    document.getElementById('outputFormat').value = data.outputFormat;
                }
            }
        } catch (error) {
            console.warn('加载保存的数据失败:', error);
        }
    }

    saveData() {
        try {
            const data = {
                subscriptionUrl: document.getElementById('subscriptionUrl').value,
                githubToken: document.getElementById('githubToken').value,
                outputFormat: document.getElementById('outputFormat').value
            };
            localStorage.setItem('proxyConverterData', JSON.stringify(data));
        } catch (error) {
            console.warn('保存数据失败:', error);
        }
    }

    clearSavedData() {
        try {
            localStorage.removeItem('proxyConverterData');
            document.getElementById('subscriptionUrl').value = '';
            document.getElementById('githubToken').value = '';
            document.getElementById('outputFormat').value = 'both';
        } catch (error) {
            console.warn('清除保存的数据失败:', error);
        }
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
            lines.push(`🎮 游戏平台 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`Ⓜ️ 微软服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`🍎 苹果服务 = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push(`📢 谷歌FCM = select, DIRECT, 🚀 节点选择, ♻️ 自动选择, ${proxyNames.join(', ')}`);
            lines.push('🎯 全球直连 = select, DIRECT, 🚀 节点选择');
            lines.push('🛑 全球拦截 = select, REJECT, DIRECT');
            lines.push('🍃 应用净化 = select, REJECT, DIRECT');
            lines.push('🐟 漏网之鱼 = select, 🚀 节点选择, ♻️ 自动选择, DIRECT');
        }
        lines.push('');
        
        // Rules (使用完整规则集)
        lines.push('[Rule]');
        
        // 本地/局域网地址
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/lan.txt,🎯 全球直连');
        // 拦截规则
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/reject.txt,🛑 全球拦截');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/reject_app.txt,🍃 应用净化');
        // AI服务
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/ai.txt,🤖 人工智能');
        // 电报消息
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/telegram.txt,📲 电报消息');
        // 流媒体
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/stream.txt,🎥 流媒体');
        // 游戏平台
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/game.txt,🎮 游戏平台');
        // 微软服务
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/microsoft.txt,Ⓜ️ 微软服务');
        // 苹果服务
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/apple.txt,🍎 苹果服务');
        // 谷歌FCM
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/google_fcm.txt,📢 谷歌FCM');
        // 全球代理
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/global.txt,🚀 节点选择');
        // 中国直连
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/domestic.txt,🎯 全球直连');
        lines.push('RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/china_ip.txt,🎯 全球直连');
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
                    name: '🎮 游戏平台',
                    type: 'select',
                    proxies: ['DIRECT', '🚀 节点选择', '♻️ 自动选择', ...proxyNames]
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
                    name: '📢 谷歌FCM',
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
        
        // Rules (使用完整规则集)
        config.rules = [
            // 本地/局域网地址
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/lan.txt,🎯 全球直连',
            // 拦截规则
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/reject.txt,🛑 全球拦截',
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/reject_app.txt,🍃 应用净化',
            // AI服务
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/ai.txt,🤖 人工智能',
            // 电报消息
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/telegram.txt,📲 电报消息',
            // 流媒体
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/stream.txt,🎥 流媒体',
            // 游戏平台
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/game.txt,🎮 游戏平台',
            // 微软服务
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/microsoft.txt,Ⓜ️ 微软服务',
            // 苹果服务
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/apple.txt,🍎 苹果服务',
            // 谷歌FCM
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/google_fcm.txt,📢 谷歌FCM',
            // 全球代理
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/global.txt,🚀 节点选择',
            // 中国直连
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/domestic.txt,🎯 全球直连',
            'RULE-SET,https://raw.githubusercontent.com/onlinefchen/auto-convert/main/rules/china_ip.txt,🎯 全球直连',
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
                    <pre style="margin: 0; white-space: pre-wrap;">${configs[format].substring(0, 500)}${configs[format].length > 500 ? '\n...(内容已截断)' : ''}</pre>
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

// 清除保存数据的全局函数
function clearSavedData() {
    if (proxyConverterInstance) {
        proxyConverterInstance.clearSavedData();
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    proxyConverterInstance = new ProxyConverter();
});