@echo off
setlocal enabledelayedexpansion

:: Proxy Subscription Converter - Windows 一键运行脚本
:: 自动创建虚拟环境、安装依赖、运行转换

title 代理订阅转换工具

:: 颜色定义 (Windows 10+ 支持)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: 输出函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:: 显示帮助信息
:show_help
echo.
echo 代理订阅转换工具 - Windows 一键运行脚本
echo.
echo 用法:
echo   %~nx0 ^<订阅链接^> [选项]
echo.
echo 参数:
echo   订阅链接        必需，代理订阅链接地址
echo.
echo 选项:
echo   -o, --output    输出文件前缀 (默认: config)
echo   -f, --format    输出格式 surge/clash/both (默认: both)
echo   -h, --help      显示此帮助信息
echo.
echo 示例:
echo   %~nx0 https://example.com/subscription
echo   %~nx0 "https://example.com/subscription" -o my_config
echo   %~nx0 "https://example.com/subscription" -f surge
echo.
goto :eof

:: 检查Python是否安装
:check_python
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :python_found
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto :python_found
)

call :log_error "Python 未安装，请先安装 Python 3.6 或更高版本"
call :log_info "下载地址: https://www.python.org/downloads/"
pause
exit /b 1

:python_found
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
call :log_info "检测到 Python 版本: !PYTHON_VERSION!"

:: 简单版本检查 (检查主版本号)
for /f "tokens=1 delims=." %%i in ("!PYTHON_VERSION!") do set "MAJOR_VERSION=%%i"
if !MAJOR_VERSION! geq 3 (
    call :log_success "Python 版本满足要求"
) else (
    call :log_error "Python 版本过低，需要 3.6 或更高版本"
    pause
    exit /b 1
)
goto :eof

:: 创建虚拟环境
:create_venv
if not exist "venv" (
    call :log_info "创建虚拟环境..."
    %PYTHON_CMD% -m venv venv
    if !errorlevel! neq 0 (
        call :log_error "虚拟环境创建失败"
        pause
        exit /b 1
    )
    call :log_success "虚拟环境创建完成"
) else (
    call :log_info "虚拟环境已存在，跳过创建"
)
goto :eof

:: 激活虚拟环境
:activate_venv
call :log_info "激活虚拟环境..."
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    call :log_success "虚拟环境已激活"
) else (
    call :log_error "无法找到虚拟环境激活脚本"
    pause
    exit /b 1
)
goto :eof

:: 安装依赖
:install_dependencies
call :log_info "检查并安装依赖包..."

:: 升级pip
python -m pip install --upgrade pip --quiet >nul 2>nul

:: 安装依赖
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --quiet >nul 2>nul
    if !errorlevel! neq 0 (
        call :log_error "依赖包安装失败"
        pause
        exit /b 1
    )
    call :log_success "依赖包安装完成"
) else (
    call :log_warning "requirements.txt 文件不存在，手动安装依赖..."
    python -m pip install requests PyYAML --quiet >nul 2>nul
    if !errorlevel! neq 0 (
        call :log_error "依赖包安装失败"
        pause
        exit /b 1
    )
    call :log_success "依赖包安装完成"
)
goto :eof

:: 验证订阅链接
:validate_url
set "url=%~1"
echo !url! | findstr /r "^https\?://" >nul
if !errorlevel! neq 0 (
    call :log_error "订阅链接格式不正确，必须以 http:// 或 https:// 开头"
    exit /b 1
)
exit /b 0

:: 运行转换
:run_conversion
set "subscription_url=%~1"
set "output_prefix=%~2"
set "format=%~3"

call :log_info "开始转换订阅链接..."
call :log_info "订阅地址: !subscription_url!"
call :log_info "输出前缀: !output_prefix!"
call :log_info "输出格式: !format!"
echo.

:: 运行转换脚本
python convert_subscription.py "!subscription_url!" -o "!output_prefix!" -f "!format!"

if !errorlevel! equ 0 (
    echo.
    call :log_success "转换完成！"
    echo.
    call :log_info "生成的文件:"
    
    if "!format!"=="surge" (
        if exist "!output_prefix!.surge.conf" (
            echo   📱 Surge 配置: !output_prefix!.surge.conf
        )
    ) else if "!format!"=="clash" (
        if exist "!output_prefix!.clash.yaml" (
            echo   ⚡ Clash 配置: !output_prefix!.clash.yaml
        )
    ) else (
        if exist "!output_prefix!.surge.conf" (
            echo   📱 Surge 配置: !output_prefix!.surge.conf
        )
        if exist "!output_prefix!.clash.yaml" (
            echo   ⚡ Clash 配置: !output_prefix!.clash.yaml
        )
    )
    
    echo.
    call :log_info "配置特性:"
    echo   ✅ 支持 VMess、Shadowsocks、Trojan 协议
    echo   ✅ 智能分组 (AI、流媒体、游戏等)
    echo   ✅ 广告拦截和应用净化
    echo   ✅ 自动规则更新
    echo   ✅ 每个分组可选择所有节点
    echo.
    call :log_success "请将生成的配置文件导入到对应的客户端中使用"
    
) else (
    call :log_error "转换失败，请检查订阅链接是否正确"
    pause
    exit /b 1
)
goto :eof

:: 主函数
:main
:: 解析命令行参数
set "SUBSCRIPTION_URL="
set "OUTPUT_PREFIX=config"
set "FORMAT=both"

:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="-h" goto :show_help_exit
if "%~1"=="--help" goto :show_help_exit
if "%~1"=="-o" (
    set "OUTPUT_PREFIX=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set "OUTPUT_PREFIX=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-f" (
    set "FORMAT=%~2"
    if not "!FORMAT!"=="surge" if not "!FORMAT!"=="clash" if not "!FORMAT!"=="both" (
        call :log_error "格式参数只能是 surge、clash 或 both"
        pause
        exit /b 1
    )
    shift
    shift
    goto :parse_args
)
if "%~1"=="--format" (
    set "FORMAT=%~2"
    if not "!FORMAT!"=="surge" if not "!FORMAT!"=="clash" if not "!FORMAT!"=="both" (
        call :log_error "格式参数只能是 surge、clash 或 both"
        pause
        exit /b 1
    )
    shift
    shift
    goto :parse_args
)
if "%~1" neq "" (
    if "!SUBSCRIPTION_URL!"=="" (
        set "SUBSCRIPTION_URL=%~1"
        shift
        goto :parse_args
    ) else (
        call :log_error "多余的参数: %~1"
        call :show_help
        pause
        exit /b 1
    )
)

:show_help_exit
call :show_help
pause
exit /b 0

:args_done
:: 检查必需参数
if "!SUBSCRIPTION_URL!"=="" (
    call :log_error "缺少订阅链接参数"
    call :show_help
    pause
    exit /b 1
)

:: 验证订阅链接
call :validate_url "!SUBSCRIPTION_URL!"
if !errorlevel! neq 0 (
    pause
    exit /b 1
)

:: 显示欢迎信息
echo.
echo ==========================================
echo 🚀 代理订阅转换工具 v1.0
echo ==========================================
echo.

:: 检查转换脚本是否存在
if not exist "convert_subscription.py" (
    call :log_error "转换脚本 convert_subscription.py 不存在"
    call :log_info "请确保在正确的目录中运行此脚本"
    pause
    exit /b 1
)

:: 执行步骤
call :check_python
call :create_venv
call :activate_venv
call :install_dependencies
call :run_conversion "!SUBSCRIPTION_URL!" "!OUTPUT_PREFIX!" "!FORMAT!"

echo.
call :log_success "🎉 所有操作完成！"
echo.
echo 按任意键退出...
pause >nul
goto :eof

:: 运行主函数
call :main %*