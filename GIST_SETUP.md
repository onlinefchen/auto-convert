# 📱 GitHub Gist 二维码功能设置指南

## 🔧 准备工作

### 1. 获取 GitHub 个人访问令牌 (Token)

1. 登录 GitHub，访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写 Token 信息：
   - **Note**: 填写用途，如 "Proxy Config Gist"
   - **Expiration**: 选择过期时间（建议 30 天或自定义）
   - **Scopes**: ✅ 勾选 **gist** 权限（只需要这一个）
4. 点击 "Generate token"
5. **⚠️ 复制并保存 token（只显示一次）**

### 2. 安装额外依赖

```bash
# 激活虚拟环境（如果还没激活）
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装二维码相关依赖
pip install qrcode[pil] PyGithub
```

## 🚀 使用方法

### 方法1: 命令行参数
```bash
# 基本用法
./convert.sh <订阅链接> --upload --github-token YOUR_TOKEN

# 完整示例
./convert.sh https://your-subscription-url --upload --github-token ghp_xxxxxxxxxxxx
```

### 方法2: 环境变量（推荐）
```bash
# 设置环境变量
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# 使用时不需要指定token
./convert.sh <订阅链接> --upload
```

## 📱 功能说明

使用 `--upload` 参数后，脚本会：

1. ✅ **生成配置文件** - 正常的 Surge/Clash 配置
2. ✅ **上传到私有 Gist** - 只有知道链接的人才能访问
3. ✅ **生成二维码** - 保存到 `qr_codes/` 目录
4. ✅ **显示直链** - 可以直接在浏览器中访问

## 📁 输出文件

```
项目目录/
├── config.surge.conf        # Surge 配置文件
├── config.clash.yaml        # Clash 配置文件
└── qr_codes/                 # 二维码目录
    ├── config.surge_qr.png   # Surge 配置二维码
    └── config.clash_qr.png   # Clash 配置二维码
```

## 📱 使用二维码

1. 用手机扫描对应的二维码
2. 或者复制控制台显示的直链
3. 在 Surge/Clash 中添加配置订阅
4. 使用扫描的链接作为订阅地址

## 🔒 安全说明

- ✅ **私有 Gist**: 只有知道链接的人才能访问
- ✅ **无公开暴露**: 不会出现在你的公开 Gist 列表
- ✅ **可删除**: 可以随时在 GitHub 上删除 Gist
- ⚠️ **链接保密**: 不要在公开场所分享二维码或链接

## ❌ 故障排除

### Token 权限错误
```
❌ GitHub 认证失败: Bad credentials
```
**解决方法**: 检查 token 是否正确，确保勾选了 `gist` 权限

### 依赖库缺失
```
❌ 缺少依赖库，请安装: pip install qrcode[pil] PyGithub
```
**解决方法**: 在虚拟环境中安装依赖

### 网络连接问题
```
❌ 上传失败: Connection timeout
```
**解决方法**: 检查网络连接，或稍后重试

## 🎯 高级用法

### 直接使用 gist_uploader.py
```bash
# 单独上传文件
python gist_uploader.py config.surge.conf config.clash.yaml

# 指定描述
python gist_uploader.py config.surge.conf --description "My Proxy Config"

# 使用不同的二维码目录
python gist_uploader.py config.surge.conf --qr-dir my_qr_codes
```

## 💡 使用建议

1. **定期更新**: 订阅内容变化时重新生成
2. **及时删除**: 不需要时删除旧的 Gist
3. **备份 Token**: 保存好 GitHub Token
4. **检查权限**: 确保 Token 只有必要的权限