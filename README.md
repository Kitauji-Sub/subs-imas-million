# THE iDOLM@STER MILLION LIVE ANIMATION STAGE 偶像大师 百万现场！ 字幕仓库

该仓库存放以`北宇治字幕组`名义制作的TV动画《偶像大师 百万现场！》 字幕。

> [!NOTE]  
> 对于一般观众，请[点击此处](https://github.com/Kitauji-Sub/MILLION-Subs/releases)下载最新CI构建文件。

# 开发

## 前提条件

+ Aegisub
  + [DependencyControl (optional)](https://github.com/TypesettingTools/DependencyControl)
  + [Merge Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
  + [The0x539's templater](https://github.com/The0x539/Aegisub-Scripts/blob/trunk/src/0x.KaraTemplater.moon)

建议通过`DependencyControl`安装`Merge Scripts`。
> [!CAUTION]
> 现有仓库中的Merge Scripts存在一个bug，会使导出的字幕文件中存在重复样式。
>
> 参见https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/issues/26

## 文件结构

对于每个单集的文件结构如下图所示：

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

## 手动合并

1. 克隆本仓库到本地
2. 使用[zhconvert.org](zhconvert.org)将各个文件进行繁化。对于主文件，还需更改import语句中的文件名。将繁化后的文件命名为`*_tc.ass`
3. 使用`The0x539's templater`将模板应用到`insert`文件夹中的文件并保存，注意该脚本与aegisub自带的auto4模板运行器不完全兼容
4. 依次打开各个主文件，使用`Merge Scripts`的`Generate release candidate`生成发布文件
