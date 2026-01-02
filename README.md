## Syncf - 优雅的文件同步打包工具
<div align="center" style="
    background: #1e1e1e;
    padding: 2rem 1rem;
    border-radius: 8px;
    margin: 2rem 0;
    border: 1px solid #444;
    font-family: 'Courier New', Consolas, Monaco, monospace;
    text-align: center;
    position: relative;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
">

<!-- 终端标题栏 -->
<div style="
    background: #2d2d2d;
    padding: 0.5rem 1rem;
    border-radius: 6px 6px 0 0;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.5rem;
">
    <span style="
        width: 12px;
        height: 12px;
        background: #ff5f56;
        border-radius: 50%;
        display: inline-block;
    "></span>
    <span style="
        width: 12px;
        height: 12px;
        background: #ffbd2e;
        border-radius: 50%;
        display: inline-block;
    "></span>
    <span style="
        width: 12px;
        height: 12px;
        background: #27ca3f;
        border-radius: 50%;
        display: inline-block;
    "></span>
    <span style="
        color: #888;
        font-size: 0.8em;
        margin-left: 1rem;
    ">syncf — bash</span>
</div>

<pre style="
    margin: 3rem 0 1.5rem 0;
    padding: 0;
    font-size: 0.9em;
    line-height: 1.2;
    color: #7ee787;
    background: transparent;
    border: none;
    font-weight: bold;
">
         ::::::::::  ##::    ::## ##::   ::##  :::::::::: :::::::::::: 
        ::::::::::::  ##::  ::##  ###::  ::## :::::::::::: :::::::::::: 
        ::::::         ########   ####:: ::## ::::::       ::::::       
         ::::::::::     ######    ## ::####:: ::::::       ::::::::::   
             :::::::     ####     ##  ::###:: ::::::       ::::::::::   
        ::::::::::::     ####     ##   ::##:: :::::::::::: ::::::       
         ::::::::::      ####     ##    ::##   :::::::::: ::::::       
</pre>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</p>

<p align="center">
  <strong>一个优雅的命令行工具，用于智能打包和管理文件集合</strong>
</p>

## ✨ 特性亮点

- 🎯 **智能文件选择** - 使用 `.gitignore` 风格的规则匹配文件
- 📦 **优雅的打包管理** - 交互式界面选择历史包文件
- 🎨 **美观的终端界面** - 使用 Rich 库提供彩色输出和进度条
- ⚡ **高性能** - 支持增量打包和大文件处理
- 🔄 **双向操作** - 打包和解包都支持详细模式
- 🧹 **自动清理** - 一键清理所有包文件
- 📁 **组织有序** - 自动创建和管理包文件目录

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd syncf

# 或使用虚拟环境
python -m venv .venv
source .venv/bin/activate
python ./src/syncf.py

or

./bin/syncf

```

### 基本使用

```bash
# 查看帮助
syncf -h

# 使用文件列表打包
syncf -z filelist myproject

# 解包最新文件
syncf -u

# 列出所有包
syncf -l

# 清理所有包
syncf -c
```

## 📁 项目结构

```
syncf/
├── src/
│   ├── syncf.py          # 主功能模块
│   └── __main__.py       # 可执行入口
├── bin/
│   └── syncf             # 可执行脚本
├── .files/               # 包文件存储目录（自动创建）
└── README.md            # 本文档
```

## 📋 详细功能

### 1. 智能打包 (`-z`)

使用类 `.gitignore` 语法选择文件：

```bash
# filelist.txt 示例
src/**/*.py          # 包含所有 Python 文件
!src/test_*.py       # 排除测试文件
docs/**/*            # 包含文档目录
*.log                # 排除日志文件
```

```bash
# 打包文件
syncf -z filelist.txt project_backup

# 详细信息模式
syncf -z filelist.txt project_backup -v
```

**输出示例：**
```
✓ Package complete: .files/project_backup_20241231_235959.tar.gz
Packed 42 files, total size: 15.23 MB
```

### 2. 交互式解包 (`-u`)

优雅的交互界面选择要解包的文件：

```bash
syncf -u
```

**界面展示：**
```
📦 找到 5 个包文件:

[?] 请选择文件 (共 5 个): (使用方向键)
❯ [1] project_backup_20241231_235959.tar.gz (15.23 MB, 今天 23:59)
  [2] docs_20241230_120000.tar.gz (2.45 MB, 昨天 12:00)
  [3] src_20241229_090000.tar.gz (8.76 MB, 12-29 09:00)
  [退出] 返回
```

### 3. 包文件列表 (`-l`)

查看所有可用的包文件：

```bash
syncf -l
```

### 4. 清理操作 (`-c`)

安全清理所有包文件：

```bash
syncf -c
```

**确认提示：**
```
[?] 确认删除 5 个包文件 (总计 28.44 MB)? (y/N)
```

## ⚙️ 配置文件

### 包存储位置

包文件默认存储在 `.files/` 目录中，位置根据运行方式自动确定：

- **开发模式**: 项目根目录的 `.files/`
- **打包后**: 可执行文件所在目录的 `.files/`

## 🎨 界面特色

### 彩色输出
- ✅ 绿色: 成功操作
- ⚠️ 黄色: 警告信息
- ❌ 红色: 错误信息
- 🔵 蓝色: 详细信息
- 🟠 橙色: 跳过文件

### 进度显示
```bash
Packing... ████████████████████ 100% 00:00:12
```

### 时间格式
- `今天 14:30` - 当天文件
- `昨天 10:15` - 前一天文件  
- `12-31 23:59` - 同年其他日期
- `2023-12-31` - 跨年文件

## 📊 文件信息

每个包文件包含：
- 📁 文件名（带时间戳）
- 📏 文件大小（自动格式化）
- 🕐 修改时间（友好格式）
- 🔢 文件数量统计
- ⚠️ 跳过文件列表（如有）

## 🔧 技术栈

- **Python 3.6+** - 核心语言
- **Rich** - 终端美化输出
- **Inquirer** - 交互式命令行界面
- **PathSpec** - `.gitignore` 风格路径匹配
- **argparse** - 命令行参数解析
- **tarfile** - 标准压缩库

## 🐳 构建发布

### 单文件可执行

```bash
# 安装构建工具
pip install pyinstaller

# 构建
pyinstaller --onefile src/cli.py --name syncf

# 输出在 dist/syncf
```

### 安装到系统

```bash
# 开发安装
pip install -e .

# 全局安装
sudo cp dist/syncf /usr/local/bin/
```

## 📝 使用示例

### 场景1: 项目备份

```bash
# 创建备份规则
cat > .syncignore << 'EOF'
# 备份源代码
src/**/*.py
src/**/*.pyx
src/**/*.c

# 备份配置文件
*.ini
*.yaml
*.json

# 排除开发文件
*.log
__pycache__/
*.pyc
*.pyo
EOF

# 执行备份
syncf -z .syncignore myproject -v
```

### 场景2: 文档打包

```bash
# 文档打包规则
cat > docs.list << 'EOF'
docs/**/*.md
docs/**/*.rst
docs/images/**
!docs/_build/
EOF

syncf -z docs.list documentation
```

### 场景3: 恢复特定版本

```bash
# 查看可用版本
syncf -l

# 交互式选择恢复
syncf -u
```

## ⚠️ 注意事项

1. **文件规则**: 支持完整的 `.gitignore` 语法
2. **路径处理**: 使用相对当前目录的路径
3. **权限保留**: 解包时保持文件权限
4. **大文件支持**: 自动处理大文件压缩
5. **错误处理**: 详细的错误信息和恢复建议

## 🔄 更新日志

### v1.0.0 (当前)
- ✅ 基础打包/解包功能
- ✅ 交互式文件选择
- ✅ 进度显示和彩色输出
- ✅ 智能文件规则匹配
- ✅ 批量清理功能
- ✅ 跨平台支持


## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👤 作者

**Astor Jiang** - 优雅的工具创造者

- 📧 Email: astor.jiang@outlook.com
- 💼 GitHub: [@astor](https://github.com/CallMeMinxJ)

## 🙏 致谢

感谢以下开源项目的支持：
- [Rich](https://github.com/Textualize/rich) - 美丽的终端输出
- [Inquirer](https://github.com/magmax/python-inquirer) - 交互式 CLI
- [PathSpec](https://github.com/cpburnz/python-path-specification) - 路径模式匹配

---

<p align="center">
  <em>用优雅的方式管理您的文件集合</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Made with Python">
  <img src="https://img.shields.io/badge/CLI-Tool-4EAA25.svg?style=flat&logo=gnu-bash&logoColor=white" alt="CLI Tool">
</p> syncf
