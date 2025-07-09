# Proxy Subscription Converter

🚀 一键将代理订阅链接转换为 Surge 和 Clash 配置文件的 Python 工具

[![Update Rules](https://github.com/onlinefchen/auto-convert/actions/workflows/update-rules.yml/badge.svg)](https://github.com/onlinefchen/auto-convert/actions/workflows/update-rules.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rules](https://img.shields.io/badge/rules-78_files-green.svg)](https://github.com/onlinefchen/auto-convert/tree/main/rules)
[![Sukka](https://img.shields.io/badge/powered_by-Sukka's_Ruleset-orange.svg)](https://ruleset.skk.moe/)

## ✨ 功能特性

- **多协议支持**: VMess、Shadowsocks、Trojan
- **智能分组**: AI服务、流媒体、微软、苹果等专用分组
- **高质量规则**: 基于 Sukka 理念的 DNS 解析优化规则集
- **性能优化**: 三层规则分类，减少DNS查询提升速度
- **一键运行**: 自动环境配置，零配置使用
- **二维码生成**: 上传到私有 GitHub Gist，扫码即用
- **跨平台**: 支持 Windows、macOS、Linux

## 🚀 快速开始

### 🌐 在线工具（推荐）

访问：**https://onlinefchen.github.io/auto-convert**

- 无需下载，直接在浏览器使用
- 实时转换，即时生成二维码
- 数据本地处理，隐私安全

### 📱 一键运行

```bash
# macOS/Linux
./convert.sh <订阅链接>

# Windows
convert.bat <订阅链接>
```

### 手动安装

```bash
# 1. 安装 Python 3.6+
# 2. 安装依赖
pip install requests pyyaml

# 3. 运行转换
python convert_subscription.py <订阅链接>
```

## 使用方法

### 🚀 一键运行（推荐）

#### macOS/Linux:
```bash
./convert.sh <订阅链接>
```

#### Windows:
```cmd
convert.bat <订阅链接>
```

一键脚本会自动：
- 检查Python环境
- 创建虚拟环境
- 安装依赖包
- 运行转换

### 手动运行

如果你想手动控制每个步骤：

1. 创建虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行转换：
```bash
python convert_subscription.py <订阅链接>
```

### 命令行参数

- `subscription_url`: 必需，订阅链接地址
- `-o, --output`: 输出文件前缀（默认：config）
- `-f, --format`: 输出格式，可选 surge/clash/both（默认：both）
- `--upload`: 上传到私有 GitHub Gist 并生成二维码
- `--github-token`: GitHub 个人访问令牌

### 示例

1. 一键生成 Surge 和 Clash 配置：
```bash
./convert.sh https://sub.example.com/link/xxx
```

2. 生成配置并上传到 GitHub Gist（扫码即用）：
```bash
./convert.sh https://sub.example.com/link/xxx --upload --github-token YOUR_TOKEN
```

3. 仅生成 Surge 配置：
```bash
./convert.sh https://sub.example.com/link/xxx -f surge
```

4. 自定义输出文件名：
```bash
./convert.sh https://sub.example.com/link/xxx -o myconfig
```

5. 显示帮助信息：
```bash
./convert.sh --help
```

## 📱 二维码功能

使用 `--upload` 参数可以将配置文件上传到私有 GitHub Gist 并生成二维码：

```bash
./convert.sh <订阅链接> --upload --github-token YOUR_TOKEN
```

**功能特点**：
- 🔒 **私有 Gist**: 只有知道链接的人才能访问
- 📱 **二维码生成**: 扫码即可导入配置
- 🗂️ **自动整理**: 二维码保存到 `qr_codes/` 目录
- 🔗 **直链访问**: 可直接复制链接使用

### 🔧 GitHub Token 获取方法

1. **访问 GitHub Settings**：https://github.com/settings/tokens
2. **创建新 Token**：
   - 点击 "Generate new token" → "Generate new token (classic)"
   - Note: 填写 `Proxy Config Gist Upload`
   - Expiration: 选择 `30 days` 或 `90 days`
   - Scopes: ✅ **只勾选 `gist`** (其他都不选)
3. **生成并保存**：
   - 点击 "Generate token"
   - ⚠️ **立即复制 token**（格式：`ghp_xxxxxxxxxxxx`）
   - 妥善保存，离开页面后就看不到了

### 💻 在线前端工具

访问我们的在线工具：**https://onlinefchen.github.io/auto-convert**

- 🌐 **网页界面**：无需下载，直接在浏览器使用
- 📱 **实时生成**：输入订阅链接即时转换
- 🔒 **数据不保存**：所有处理都在客户端，不保存任何数据
- 📲 **二维码显示**：直接显示可扫描的二维码

详细设置教程请查看：[GIST_SETUP.md](GIST_SETUP.md)

## 🛡️ 隐私保护与数据安全

### 🔒 数据存储与隐私保护

我们高度重视用户的隐私和数据安全，采用不同的策略来保护您的敏感信息：

#### 💻 Python 本地版本
- **完全本地处理**：所有数据处理都在您的本地机器上进行
- **不发送到服务器**：订阅链接和配置文件不会发送到任何第三方服务器
- **临时文件处理**：
  - 下载的订阅内容仅在内存中处理
  - 生成的配置文件保存在本地目录
  - 使用完成后可随时删除
- **GitHub Gist 上传**（可选）：
  - 仅在用户明确使用 `--upload` 参数时上传
  - 上传到用户自己的私有 GitHub Gist
  - 用户完全控制数据的访问权限

#### 🌐 网页版本 (JavaScript)
- **客户端处理**：所有转换都在用户的浏览器中进行
- **不保存到本地**：
  - 订阅链接和 GitHub Token 仅在页面内存中暂存
  - 页面刷新或关闭后数据自动清除
  - 不使用 localStorage 或任何持久化存储
- **数据传输**：
  - 仅在获取订阅内容时访问用户提供的订阅链接
  - 如果用户提供 GitHub Token，仅用于上传配置到用户的私有 Gist
  - 不会将任何数据发送到我们的服务器

#### 🔐 安全措施
- **HTTPS 加密**：所有网络请求都通过 HTTPS 进行
- **无日志记录**：不记录用户的订阅链接或访问日志
- **开源透明**：所有代码公开，用户可以审查和验证
- **最小权限原则**：GitHub Token 仅需要 `gist` 权限

#### ⚠️ 用户须知
- **GitHub Token 安全**：
  - 仅授予 `gist` 权限，不要给予其他权限
  - 定期更新 Token，建议设置较短的过期时间
  - 如果不需要 Gist 功能，可以不提供 Token
- **订阅链接保护**：
  - 确保订阅链接来自可信的提供商
  - 不要在公共场所使用订阅链接
  - 定期更新订阅链接

### 📱 数据流向示意

```
Python 版本：
订阅链接 → 本地内存 → 配置文件 → 本地磁盘
                  ↓ (可选)
               GitHub Gist

JavaScript 版本：
订阅链接 → 浏览器内存 → 配置显示 → 内存清除
                    ↓ (可选)
                 GitHub Gist
```

## 📁 输出文件

- Surge 配置：`<output>.surge.conf`
- Clash 配置：`<output>.clash.yaml`
- 二维码图片：`qr_codes/<配置名>_qr.png`

## 📋 智能分组

生成的配置包含以下专用分组，每个分组可选择所有节点：

- 🤖 **人工智能** - ChatGPT、Claude、Gemini 等 AI 服务
- 📲 **电报消息** - Telegram 专用优化
- 🎥 **流媒体** - Netflix、YouTube、Disney+ 等全球流媒体
  - 🇺🇸 美国流媒体 - Netflix US、Hulu 等
  - 🇪🇺 欧洲流媒体 - 欧洲本地服务
  - 🇯🇵 日本流媒体 - AbemaTV、TVer 等
  - 🇰🇷 韩国流媒体 - 韩国本地服务
  - 🇭🇰 香港流媒体 - 香港本地服务
  - 🇹🇼 台湾流媒体 - 台湾本地服务
- Ⓜ️ **微软服务** - Microsoft 全家桶及 CDN 优化
- 🍎 **苹果服务** - iCloud、App Store 等完整生态
- 🛑 **全球拦截** - 广告、跟踪、钓鱼网站拦截
- 🍃 **应用净化** - 应用内广告轻量拦截
- 🎯 **全球直连** - 国内服务、CDN、下载优化

## 🛡️ 规则特性

### 📊 基于 Sukka 理念的 DNS 解析优化

本项目采用 [Sukka](https://github.com/SukkaW/Surge) 的三层规则分类理念，按DNS解析行为组织规则，优化代理性能：

#### 🎯 三层规则分类

1. **domainset/** - 纯域名规则（DNS解析：否）
   - 不触发DNS解析，最快匹配
   - 适用于明确域名的拦截和分流

2. **non_ip/** - 非IP规则（DNS解析：否）
   - 域名和正则表达式规则
   - 不触发DNS解析，性能优异

3. **ip/** - IP规则（DNS解析：是）
   - 需要DNS解析的IP段规则
   - 精确匹配，但会触发DNS查询

#### 🚀 性能优化

- **规则顺序优化**: 按DNS解析成本排序，优先匹配无需解析的规则
- **完整规则覆盖**: 包含所有39个Sukka规则集，无遗漏
- **智能分组**: 根据服务类型和DNS解析行为合理分组
- **格式分离**: Surge和Clash规则完全分离，避免混用

#### 📋 规则分组详情

- **🛑 全球拦截** (7个规则) - 广告、跟踪、钓鱼网站拦截
- **🍃 应用净化** (1个规则) - 应用内广告净化
- **🎯 全球直连** (14个规则) - 国内服务、CDN、下载优化
- **🚀 节点选择** (2个规则) - 国外代理服务、GitHub访问
- **🤖 人工智能** (1个规则) - AI服务专用
- **📲 电报消息** (2个规则) - Telegram专用
- **🎥 流媒体** (8个规则) - 各地区流媒体服务
- **Ⓜ️ 微软服务** (2个规则) - Microsoft全家桶
- **🍎 苹果服务** (3个规则) - Apple生态服务

#### 🔧 DNS污染防护

针对DNS劫持和污染问题，本项目提供双重防护：

**🛡️ 主要防护 - DoH (DNS over HTTPS)：**
- **加密DNS查询**：使用HTTPS加密DNS请求，防止中间人攻击
- **绕过ISP劫持**：避开路由器和ISP的DNS劫持
- **多重备份**：阿里云DoH + 腾讯云DoH + Cloudflare DoH
- **自动降级**：DoH失败时自动降级到传统DNS

**🎯 备用防护 - GitHub规则集：**
- **优先级规则**：GitHub域名规则优先于LAN规则
- **代理访问**：GitHub相关域名直接通过代理访问
- **完整覆盖**：包含所有GitHub相关域名作为双重保险

**📊 DNS服务器配置：**
```
dns-server = https://223.5.5.5/dns-query,    # 阿里云DoH
             https://119.29.29.29/dns-query,  # 腾讯云DoH  
             https://1.1.1.1/dns-query,      # Cloudflare DoH
             system                          # 系统DNS备用
```

#### 📈 技术特点

- **自动更新**: 规则集每日自动更新（GitHub Actions）
- **DNS解析优化**: 减少不必要的DNS查询
- **行为分析**: 基于流量特征智能分流
- **兼容性**: 支持最新的Surge和Clash特性
- **质量保证**: 自动修复格式问题，确保规则语法正确

#### 🤖 自动化更新

本项目使用GitHub Actions实现全自动规则更新：

- **⏰ 定时更新**: 每日北京时间 08:00 自动更新
- **📥 智能下载**: 自动获取最新的Sukka规则集
- **🔧 自动修复**: 自动处理格式问题和语法错误
- **📦 自动发布**: 更新后自动创建Release版本
- **🔍 变更检测**: 仅在规则有变化时才提交更新

#### 🛠️ 规则维护

手动更新规则（开发者）：
```bash
# 下载最新规则
python3 download_rules.py

# 测试规则完整性
python3 test_auto_fix.py
```

## 📄 输出文件

- `config.surge.conf` - Surge 配置文件
- `config.clash.yaml` - Clash 配置文件

## 🔧 支持格式

| 协议 | 格式示例 |
|------|----------|
| VMess | `vmess://base64编码配置` |
| Shadowsocks | `ss://base64(method:password)@server:port#name` |
| Trojan | `trojan://password@server:port#name` |

## 📝 许可证

MIT License

## 🙏 致谢

- [Sukka](https://github.com/SukkaW/Surge) - 高质量规则集及DNS解析优化理念
- [Sukka's Ruleset](https://ruleset.skk.moe/) - 完整的39个规则集数据源
- [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) - 分流规则参考

## 📊 规则统计

本项目包含完整的 39 个 Sukka 规则集：

### domainset/ (5个规则)
- cdn, download, reject, reject_extra, reject_phishing

### non_ip/ (25个规则)  
- ai, apple_cdn, apple_cn, apple_services, cdn, direct, domestic, download, global, lan, microsoft, microsoft_cdn, neteasemusic, reject, reject_drop, reject_no_drop, sogouinput, stream, stream_eu, stream_hk, stream_jp, stream_kr, stream_tw, stream_us, telegram

### ip/ (9个规则)
- cdn, china_ip, domestic, download, lan, neteasemusic, reject, stream, telegram

**总计: 39个规则文件 × 2种格式 = 78个规则文件**