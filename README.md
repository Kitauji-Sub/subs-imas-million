# THE iDOLM@STER MILLION LIVE ANIMATION STAGE 偶像大师 百万现场！ 字幕仓库

![menu_logo](https://github.com/Kitauji-Sub/subs-imas-million/assets/46473171/23b114ef-15e0-48ef-b1b8-a26224eb6402)

[![preview status](https://github.com/Kitauji-Sub/subs-imas-million/actions/workflows/preview.yml/badge.svg?branch=main)](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/latest) ![tv tags](https://img.shields.io/github/v/tag/Kitauji-Sub/subs-imas-million?filter=tv-*&label=tv) ![bd tags](https://img.shields.io/github/v/tag/Kitauji-Sub/subs-imas-million?filter=bd-*&label=bd) ![movie tags](https://img.shields.io/github/v/tag/Kitauji-Sub/subs-imas-million?filter=movie-*&label=movie)

该仓库存放以`北宇治字幕组`名义制作的 TV 动画《偶像大师 百万现场！》字幕。

## 下载字幕

> [!NOTE]
> 仓库内字幕按工程文件组织，面向观众的可直接播放版本统一通过 Releases 提供。

| 标签 | 说明 | 下载 |
| :-: | - | :-: |
| `latest` | `main` 分支滚动预发布，版本号形如 `latest-YYYYMMDDHHMM-<sha>` | [点此下载](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/latest) |
| `tv` | 适配网络放送版 TV 播放源的稳定分支，版本号形如 `tv-x.y.z` | [点此查看](https://github.com/Kitauji-Sub/subs-imas-million/releases?q=tv-) |
| `bd` | 适配 BD 源的稳定分支，版本号形如 `bd-x.y.z` | [点此查看](https://github.com/Kitauji-Sub/subs-imas-million/releases?q=bd-) |
| `movie` | 剧场先行上映三幕对应的稳定分支，版本号形如 `movie-x.y.z` | [点此查看](https://github.com/Kitauji-Sub/subs-imas-million/releases?q=movie-) |

## 开发

### 环境需求

- Aegisub
- [Merge Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
- [The0x539's templater](https://github.com/The0x539/Aegisub-Scripts/blob/trunk/src/0x.KaraTemplater.moon)
- Python 3.x
- [assdiff3](https://github.com/TypesettingTools/assdiff3)（推荐，用于 `*.ass` 三方合并）

> [!CAUTION]
> 现有 `Merge Scripts` 上游版本存在重复样式问题，自动化构建使用的是 FichteForks 的修复分支。
>
> 参见 https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/issues/26

> [!NOTE]
> 仓库已经通过 `.gitattributes` 声明了 `*.ass merge=assdiff3`。安装 `assdiff3` 后，还需要按其仓库说明把它注册为 Git merge driver。

### 目录结构

TV 单集目录结构如下：

```text
epxx
├── insert
│   └── insert01.ass
├── screen
│   └── screen.ass
├── staff
│   ├── stf_kitauji.ass
│   └── stf_lolihouse.ass
└── epxx_sc.ass
```

- `epxx_sc.ass` 为主文件，包含 `import` / `import-shifted` 语句
- `insert`、`screen`、`staff` 分别只放对应子模块内容
- `*_tc.ass` 由构建脚本自动生成，不再作为手工维护入口
- 新单集可从 `ep.template/` 复制起步

### 本地构建

1. 克隆仓库
2. 安装 Python 依赖：

```bash
pip install --user git+https://github.com/FichteForks/Myaamori-Aegisub-Scripts.git@pr/fix-style-deduplication#subdirectory=scripts/sub-digest
pip install requests urllib3
```

3. 下载 [aegisub-cli.zip](https://github.com/scrpr/aegisub-cli/releases/download/disable_unique_path/aegisub-cli.zip) 到仓库根目录并解压为 `aegisub-cli/`。
4. 安装 `Fonts/` 下字体；在非 Windows 环境运行构建时，还需要可用的 `wine`
5. 运行构建：

```bash
python build.py --line preview --version local-dev
```

稳定分支本地构建示例：

```bash
python build.py --line tv --version tv-0.1.2
python build.py --line bd --version bd-1.2.1
python build.py --line movie --version movie-1.2.1
```

输出位于 `build/output/`


## 声明

![site image](https://zhconvert.org/build/assets/images/logo_h36.1306fa53.png)

本仓库字幕在繁体中文化流程中，使用了繁化姬（[zhconvert.org](https://zhconvert.org/)）提供的 API 服务。

繁化姬 API 仅供个人学习研究使用，商业用途请参考[繁化姬说明文件](https://docs.zhconvert.org/commercial/)
