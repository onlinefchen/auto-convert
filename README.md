# Proxy Subscription Converter

🚀 一键将代理订阅链接转换为 Surge 和 Clash 配置文件的 Python 工具

## ✨ 功能特性

- **多协议支持**: VMess、Shadowsocks、Trojan
- **智能分组**: AI服务、流媒体、游戏、微软、苹果等专用分组
- **高质量规则**: 集成 Sukka 和 ACL4SSR 规则集
- **一键运行**: 自动环境配置，零配置使用
- **跨平台**: 支持 Windows、macOS、Linux

## 🚀 快速开始

### 一键运行（推荐）

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

### 示例

1. 一键生成 Surge 和 Clash 配置：
```bash
./convert.sh https://sub.example.com/link/xxx
```

2. 仅生成 Surge 配置：
```bash
./convert.sh https://sub.example.com/link/xxx -f surge
```

3. 自定义输出文件名：
```bash
./convert.sh https://sub.example.com/link/xxx -o myconfig
```

4. 显示帮助信息：
```bash
./convert.sh --help
```

## 输出文件

- Surge 配置：`<output>.surge.conf`
- Clash 配置：`<output>.clash.yaml`

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