# Proxy Subscription Converter

🚀 一键将代理订阅链接转换为 Surge 和 Clash 配置文件的 Python 工具

## ✨ 功能特性

- **多协议支持**: VMess、Shadowsocks、Trojan
- **智能分组**: AI服务、流媒体、游戏、微软、苹果等专用分组
- **高质量规则**: 集成 Sukka 和 ACL4SSR 规则集
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

## 📁 输出文件

- Surge 配置：`<output>.surge.conf`
- Clash 配置：`<output>.clash.yaml`
- 二维码图片：`qr_codes/<配置名>_qr.png`

## 📋 智能分组

生成的配置包含以下专用分组，每个分组可选择所有节点：

- 🤖 **人工智能** - ChatGPT、Claude、Gemini 等 AI 服务
- 📲 **电报消息** - Telegram 专用
- 🎥 **流媒体** - Netflix、YouTube、Disney+ 等
- 🎮 **游戏平台** - Steam、Epic Games 等
- Ⓜ️ **微软服务** - Microsoft 全家桶
- 🍎 **苹果服务** - iCloud、App Store 等
- 📢 **谷歌FCM** - 推送通知服务

## 🛡️ 规则特性

- **广告拦截**: 自动屏蔽广告和跟踪
- **应用净化**: 净化应用内广告
- **智能分流**: 国内直连，国外代理
- **自动更新**: 规则集每日自动更新

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

- [Sukka](https://github.com/SukkaW/Surge) - 高质量规则集
- [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) - 分流规则