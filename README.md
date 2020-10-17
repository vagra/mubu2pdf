# mubu2pdf
Convert mubu.com outline html to pdf, with up to 108 heading levels. 

## 简介
这个 Python 脚本用来把幕布（mubu.com）导出的 html 文件，转换为 PDF 文档。

这不是一般的 PDF 文档，而是支持多达 108 级标题的 PDF 文档。

![PDF 阅读效果](https://github.com/vagra/mubu2pdf/raw/main/images/pdf.jpg)

推荐使用 [PDF-XChange Viewer](https://www.tracker-software.com/product/pdf-xchange-viewer) 来阅读生成的 PDF ，它的书签栏可以支持无限级的标题，体验很不错，而且免费。

## 示例文件
本工具实际上就一个 parse_html.py ，和 css 目录下两个 css 文件，其它的都是文档和示例文件。
mubu, html, pdf 三个目录下带了几个示例文件，大家可以看效果。
```
mubu/   # 幕布导出的原始 html 文件
html/   # 转换生成的判定了各级标题和正文的 html 文件
pdf/    # 最终生成的 pdf 文件
```

## 安装

这个工具主要使用了两个 Python 库，需要使用 pip 预先安装：

1. [lxml](https://github.com/lxml/lxml)

2. [weasyprint](https://github.com/Kozea/WeasyPrint)

特别是 weasyprint 这个库安装比较麻烦，请自己去官网搜索 [安装文档](https://weasyprint.readthedocs.io/en/stable/install.html) 。
我自己简单写了个 weasyprint 在 Windows 上的的安装过程在本文最后，可参看。

## 使用方法

1. 从幕布（mubu.com）把你的大纲文件导出为 html ，放到 mubu/ 目录下；

2. 然后执行脚本： 

```
python parse_html.py
```

它就会自动查找 mubu/ 目录下所有的 html 文件，把它们统统转换为 pdf ，放置在 pdf/ 目录下。
html/ 目录用来放置生成的中间文件。

由于查找要转换的 html 文件时只会在 pdf/ 目录下搜索，不会搜索它的子目录，所以已经转换过的 html 文件你可以移动到 pdf/ 的子目录比方说 pdf/pass/ 下面，这样以后批量转换时就不会再转换它们了。

## 为什么要做这个工具？

幕布本身有一些导出功能，按理说最容易读取、格式最清晰的，是 opml 格式，但是幕布导出的 opml 格式文档阉割得太厉害，加粗、彩色等等的格式都没有，这些格式因为可以辅助判断一个节点是不是标题，所以非常重要，但幕布导出的 opml 里没有。

幕布还可以导出 html ，这个信息保留全面，所以我写了这个工具，用来解析幕布导出的 html 文件，判断哪些节点是标题，哪些节点是内容，生成一个新的 html 文件，再转换为支持 108 级标题的 pdf 。

这样的好处不但是容易判断哪些是标题，它还可以保留幕布原文档中的大部分格式，加粗、彩色字体都可以保留。

## 如何判断一个节点是标题还是正文？
```
MUST_COLOR = True       # 是否必须有颜色才是标题
MUST_BOLD = False       # 是否必须加粗才是标题
MUST_DIGITAL = True     # 是否必须以数字开头才是标题（前两位有数字都算）
MUST_STEM = False       # 是否必须以天干地支开头才是标题
```
parse_html.py 中有上面四个设置，是可以自己随意修改的。
比方说，你的文档中，凡是天干地支开头，并且带颜色的，就是标题，其它是正文，那么，你就把 `MUST_COLOR` 和 `MUST_STEM` 设置为 `True` ，表示这两个是必须条件，另两项设置为 `False`。

另外还有个隐藏的判断，就是幕布还能给节点添加一到三级标题，那么在这个工具的判断中，凡是加了标题格式的节点，无条件判断为标题。

另外，这个标题的判断，是从外层往内层，一旦一个节点被判断为正文，那么它的下面就算还有一些缩进，就算符合前面的判断条件，它也不会被判定为标题，而是作为有缩进层次的正文部分来处理。

## 如何修改字体、行距、PDF 设置边距、页码等等？
这个，只要修改 css/ 目录下的两个 css 文件，你可以为所欲为。

## 这个工具有什么缺点？
缺点就是，从幕布中导出 html 文件之前，必须展开幕布中的所有节点。如果一个节点没有展开，它就不会被幕布输出到 html 。

相比之下导出 opml 虽然不支持粗体和颜色等格式，但可以输出整个大纲的节点树。

## weasyprint 安装过程

这个教程只针对 64 位 Windows ，而且要安装 64 位的 python 3.x 。
其它系统可以参看官方文档。

1. 没有 Python 的话到这里下载 Windows x86-64 executable installer ：

https://www.python.org/downloads/windows/

如果你的系统只是 64 位 Windows 7 ，你只能下载 Python 3.8.x 以下的版本， Python 3.9 以上不支持 Windows 7 。
下载后安装，安装过程中注意勾选`把 Python 加入系统变量`，它默认就是选中的。

2. 装好后，看看你的 python 的版本是 32 位还是 64 位的：
```
python --version --version
```

3. 到这里下载 gtk3-runtime-x.x.x-x-x-x-ts-win64.exe ：

https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

下载后安装，一路 Next 即可。

然后打开命令行窗口执行如下步骤：

4. pip 默认的国外镜像速度太慢，执行如下指令设置 pip 使用清华大学镜像：
```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

5. 执行如下指令升级你的 pip：
```
python -m pip install --upgrade pip setuptools
```

6. 执行如下指令以安装 lxml：
```
python -m pip install lxml 
```

7. 执行如下指令以安装 weasyprint：
```
python -m pip install WeasyPrint
```
它会自动安装各项依赖库。

8. 但是它忘了安装 cssselect ，所以要手动安装：
```
python -m pip install cssselect
```

9. 好了，现在关闭命令行窗口（以更新环境变量），再重新打开，就可以执行如下指令来转换 html 为 pdf 文档了：
```
weasyprint html路径.html 输出pdf路径.pdf
```
这个能正常执行的话，就是安装成功了。

## 特别鸣谢

[weasyprint](https://github.com/Kozea/WeasyPrint)

这个 html 转 pdf 的库做得太好了！它支持 css 3.0 的大部分特性，而其它大部分同类工具仅支持 css 2.0 。
这意味着它可以有许多魔幻的玩法，怎么玩？就是设置 css 文件就可以。通过修改 css 文件，你可以给 pdf 加页码、带页码的目录、页眉页脚显示章节标题、等等等等。

同类工具中，收费的，Prince 很不错，免费开源的，目前就我所知， weasyprint 是最好的！
