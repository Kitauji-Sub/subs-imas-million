# THE iDOLM@STER MILLION LIVE ANIMATION STAGE 偶像大师 百万现场！ 字幕仓库

![menu_logo](https://github.com/Kitauji-Sub/subs-imas-million/assets/46473171/23b114ef-15e0-48ef-b1b8-a26224eb6402)

该仓库存放以`北宇治字幕组`名义制作的TV动画《偶像大师 百万现场！》 字幕。

## 下载字幕

> [!NOTE]
> 由于项目结构原因，字幕文件并非即取即用，故在此提供预构建文件方便观众取用。

|分支|说明|下载|
|-|-|:-:|
|`latest`|`main`持续集成的分支，拥有最新改动，部分显示可能会不正常|[点此下载](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/latest)|
|`tv`|适配网络放送版TV播放源（例如CR）的稳定分支|[点此下载](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/tv-0.1-fix)|
|`bd`|适配BD源的稳定分支|[点此下载](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/bd-1.1)|
|`movie`|专为剧场先行上映的三幕制作的字幕|[点此下载](https://github.com/Kitauji-Sub/subs-imas-million/releases/tag/movie-1.1.2)|

## 开发

### 环境需求

+ Aegisub
  + [DependencyControl (optional)](https://github.com/TypesettingTools/DependencyControl)
  + [Merge Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
  + [The0x539's templater](https://github.com/The0x539/Aegisub-Scripts/blob/trunk/src/0x.KaraTemplater.moon)
+ Python 3.x
  + SubDigest

建议通过`DependencyControl`安装`Merge Scripts`。
> [!CAUTION]
> 现有仓库中的Merge Scripts存在一个bug，会使导出的字幕文件中存在重复样式。
>
> 参见https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/issues/26

### 目录结构

对于每个单集的目录结构如下图所示：

```
epxx → 主目录
├── insert
│   ├── insert0x.ass
│   └── insert0x_tc.ass
├── screen
│   ├── screen.ass
│   └── screen_tc.ass
├── staff
│   ├── stf_kitauji.ass
│   └── stf_lolihouse.ass
├── epxx_sc.ass
└── epxx_tc.ass
```

> [!NOTE]  
> 由于现在由自动化流程自动生成繁体化文件，故_tc.ass已不起作用。

`insert`下的文件应该仅包含插入曲部分，其它文件也以此类推。`epxx_sc.ass`为主文件，包含`import`语句。其它文件应使用 `Merge Scripts` 经由`import`语句导入到主文件中，最后导出发布文件。

### 手动合并

1. 克隆本仓库到本地
2. 使用[zhconvert.org](zhconvert.org)将各个文件进行繁化。对于主文件，还需更改import语句中的文件名。将繁化后的文件命名为`*_tc.ass`
3. 使用`The0x539's templater`将模板应用到`insert`文件夹中的文件并保存，注意该脚本与aegisub自带的auto4模板运行器不完全兼容
4. 依次打开各个主文件，使用`Merge Scripts`的`Generate release candidate`生成发布文件
