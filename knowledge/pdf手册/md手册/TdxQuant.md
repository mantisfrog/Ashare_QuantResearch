# TdxQuant 简介

TdxQuant是由深圳市财富趋势科技股份有限公司研发的专业量化投研平台，专注于为国内量化投资者提供从策略研究到投资决策的全流程解决方案。平台以高效、简洁为核心设计理念，致力于降低量化交易门槛，提升策略开发与执行的效率。

依托通达信近三十余年在金融科技领域的深厚积累，TdxQuant集成了完备的实时和历史行情数据、金融数据库及稳定的交易系统基础设施，为策略的研发、回测、验证和执行提供了坚实可靠的技术支持。

平台采用分层化、模块化的服务体系，可灵活适配从高校学生、独立研究者、个人投资者到专业机构等不同用户的需求，实现从策略构思到交易落地的无缝衔接。

# TdxQuant 服务介绍

TdxQuant 是一套基于通达信金融终端构建的 Python 量化策略运行框架。该框架通过 API 接口形式，为策略交易提供所需的行情数据获取与交易指令执行功能。

# 运行环境要求

TdxQuant 支持 64 位 Python 3.7、3.8、3.9、3.10、3.11、3.12、3.13、3.14等版本，系统会自动适配当前 Python 版本，建议使用3.13版本。

请注意：运行 TdxQuant 程序前，需预先启动支持TQ策略功能的 通达信金融终端、量化模拟版或专业研究版等版本。

# 核心运行逻辑

TdxQuant 以 tqcenter 行情模块为核心，专注于为量化交易者提供高效、直接的数据服务，主要包含以下内容：

行情数据：实时与历史的快照、K 线、分笔（Tick）数据  
基本面数据：除权除息、基本财务、专业财务、股票交易数据、市场数据等  
新股和合约等信息：标的基础信息、可转债、新股申购等  
分类数据：市场类型、行业分类、自定义板块等

# 核心应用场景

TdxQuant提供覆盖量化投研全流程的核心功能模块，主要应用场景包括：

# 1. 策略研发与历史回测

平台提供“即用型”标准化数据。所有历史与实时数据均在服务端完成清洗、对齐，并预加载至客户端。支持用户快速获取指定时间维度的历史数据，并进行策略信号计算与回测分析。既提供复权因子，也提供各种类型的复权后的数据。

# 2. 实时监控与信号预警

支持实时行情数据订阅，用户可基于自定义的指标与因子模型进行在线计算。当预设条件触发时，系统通过信号接口实时推送预警信息至客户端，助力研究者及时捕捉市场动态与交易机会。

# 3. 交易模拟与实盘执行

平台构建了完整的策略交易闭环，提供模拟交易、券商实盘等两种执行环境：

模拟交易：在仿真市场环境中，使用实时行情数据对策略进行持续跟踪与验证，评估其实际表现，全程无资金风险。  
实盘交易：通过稳定的交易总线，安全对接券商报盘系统，实现策略信号的自动化、高可靠性下单与交易管理。

# 量化交易的核心价值

# 1. 利用历史数据高效验证策略，提升研究效率数百倍

在验证交易策略时，历史回测是评估其有效性的关键环节，但传统人工方式难以处理海量数据与复杂计算。量化交易可在几分钟内完成一次全面回测，快速获得统计验证结果，极大提升了策略研发的迭代效率。

# 2. 实时捕捉基于概率的获胜机会

量化交易借助计算机强大的数据处理能力，能够从海量市场信息中发掘人工难以察觉的规律与机会。面对全市场数千只股票的实时波动，量化系统可同时监控多重条件，避免机会错失。它能够综合考量选股、择时、资产配置与风险管理，构建并执行具有较大概率的投资组合，追求收益最大化。

# 3. 实现科学、客观的投资决策

与传统主观投资不同，量化交易将投资理念、经验甚至市场直觉转化为严谨的数学模型。通过系统化的信号生成与执行机制，有效克服人性中的情绪偏差，使投资决策过程更具纪律性、可重复性与可优化性。

# 量化交易的工具挑战

工欲善其事，必先利其器。 对于个人投资者而言，独立搭建一套完整的量化交易体系，复杂繁琐，涉及数据、系统、策略等多层面的巨大投入。

# 一、需要准确、全面的金融数据基础

量化交易依赖于高质量的历史与实时数据，包括行情、财务、宏观及基本面数据等。构建和维护这样一个数据仓库，不仅需要持续的数据采购、清洗、更新与运维成本，还需在数据存储、访问速度与系统稳定性方面进行深入的技术投入。

# 需要易用、可靠的量化交易系统

一个成熟的量化平台需要支持多样的策略开发语言、具备高速的回测与模拟引擎、提供科学的策略评估体系，并为实盘交易提供全方位的保障。过往，研究者往往需要兼具复杂的金融数据知识与工程构建能力。如今，TdxQuant让您只需专注于策略逻辑本身，其余复杂工作交给平台。

# TdxQuant的核心优势

TdxQuant是一款集金融数据与策略投研工具于一体的量化平台，结构清晰，简洁易上手，数据获取快捷，算法资源丰富。我们的目标是为投资者提供"开箱即用"的完整解决方案。

# 1. 全方位保障策略安全与自主

支持策略在本地IDE环境中开发与运行，保障代码安全与私密性  
分离式模块化架构，策略的编码和调试更加自由和灵活

# 2. 大幅降低量化交易门槛

提供高质量、高精度、快速接入的金融元数据  
支持多种策略类型的便捷编写、回测、模拟与实盘

# 3. 助力构建专业量化成长路径

全程助力用户从入门到精通，成为专业的量化投资者

#版本更新说明

# ?? 更新日志

# ?? 2026-03-27 更新说明 --仅上线内测版和金融终端(量化模拟)版

新增函数：获取股票所属板块get\_relation  
新增函数：调用客户端功能接口exec\_to\_tdx  
新增函数：撤单cancel\_order\_stock  
新增函数：账户资产查询query\_stock\_asset  
更新函数：交易类账户函数逻辑更新  
更新函数：order\_stock对于模拟账户自动下单  
更新函数：order\_stock新增信用交易：担保品买入、担保品卖出，融资买入，融券卖出  
更新函数：get\_stock\_list\_in\_sector访问空的自定义板块会返回空集而不是报错  
问题修复：修复了get\_market\_data、refresh\_kline等函数无法处理期权的问题  
其他更新：期货期权类型支持，新增相关宏定义（常量枚举）

# ?? 2026-03-20 更新说明 --仅上线内测版和金融终端(量化模拟)版

新增函数：获取资金账户句柄stock\_account  
新增函数：查询账户委托信息query\_stock\_orders  
新增函数：查询账户持仓信息query\_stock\_positions  
新增函数：交易执行函数order\_stock  
更新函数：get\_stock\_list\_in\_sector新增block\_type=2，可取对应期货代码  
更新函数：get\_more\_info新增字段QHMainYYMM  
更新函数：get\_stock\_list新增参数92: 国内期货主力合约  
更新函数：get\_cb\_info改名为get\_kzz\_info

# ?? 2026-03-06 更新说明

新增函数：获取跟踪指数的ETF信息get\_trackzs\_etf\_info  
更新函数：refresh\_cache新增参数 'ZS' 表示沪深京指数  
更新函数：get\_stock\_list新增参数91 跟踪指数的ETF信息  
其他修正：未识别的市场后缀由默认的SZ改为OT  
其他修正：修复get\_market\_data某些情况下会报NoneType的bug

# ?? 2026-02-28 更新说明

问题修复：修复了formula\_process\_mul\_zb等入参retrun\_count拼写错误问题  
更新函数：get\_more\_info，get\_cb\_info，get\_market\_snapshot加上了字段筛选功能  
更新函数：get\_more\_info等支持更多行情数据项，输出顺序进行归整  
其他修正：tqcenter几处细节修改

# ?? 2026-02-12 更新说明

更新函数：send\_user\_block可以添加股票进自选股，自选股简称为ZXG  
其他更新：批量调用公式内部优化提速  
其他更新：新增港股指数（.HI）  
其他更新：解决多个客户端同时运行时的TQ冲突的问题

# ?? 2026-02-07 更新说明

新增函数：批量调用选股公式formula\_process\_mul\_xg  
新增函数：批量调用指标公式formula\_process\_mul\_zb  
更新函数：get\_stock\_list、 get\_sector\_list、 get\_stock\_list\_in\_sector新增参数list\_type，可以选择返回股票名称

更新函数：download\_file新增下载：最近舆情、综合信息文件  
更新函数：get\_stock\_info新增部分数据字段输出

# ?? 2026-01-31 更新说明

新增功能：支持调用通达信公式进行计算  
新增函数：格式化K线数据formula\_format\_data  
新增函数：向通达信公式系统设置数据formula\_set\_data  
新增函数：向通达信公式系统设置数据信息formula\_set\_data\_info  
新增函数：获取公式中的设置数据formula\_get\_data  
新增函数：调用通达信技术指标公式formula\_zb  
新增函数：调用通达信条件选股公式formula\_xg  
新增函数：调用通达信专家系统公式formula\_exp  
新增函数：获取股票更多信息get\_more\_info  
新增函数：获取每天的股本数据get\_gb\_info  
问题修复：修复了部分市场数据返回时小数位数不对导致的精度问题。  
问题修复：修复了获取Python3.9以及之前版本依赖库错误问题。

更新函数：刷新行情缓存refresh\_cache，新增参数force和market，可指定强制刷新或指定市场刷新

其他更新：新增中证指数（.CSI），中金所期货（.CFF），宏观数据（.HG）等市场后缀识别和数据获取

其他更新：获取非指定日期的股票交易数据，板块交易数据等数据时增加了对应日期返回。

# ?? 2026-01-17 正式发布

安装Python及开发环境 →

# 安装Python及VSCode等开发环境

# 1.安装 Python 环境

安装Python：建议使用Python3.7及以上版本

# 1.1 下载地址：Python官网

特别提示：安装时候务必勾选Add Python to PATH（将Python添加到环境变量）

# 2.安装IDE 建议VSCode、PyCharm或Trae

# 2.1 下载地址：Visual Studio Code官网

# 2.2 安装 Python 插件（Extensions）

VSCode安装好后，在VSCode终端-扩展-输入下文，分别添加相关扩展：

简体中文  
python

![](images/e14c59e38c7c48fe39f4b40082136bb3d9d5e77c95a75ee09bb7ba2e623dd030.jpg)

<details>
<summary>text_image</summary>

文件(E)
编辑(E)
选择(S)
查看(V)
转到(G)
运行(B)
扩展: 商店
CHINESE
Chinese (Simplified) (简体中文) L...
中文(简体)
Microsoft
Chinese (Traditional...
4.4M ★5
中文(繁體)
Microsoft
安装
Cline Chinese
157K ★5
Cline中文汉化版，Cline是一款在您...
HybridTalentComputing
安装
ESLint Chinese Rules
eslint中文规则提示插件
maggie
安装
</details>

![](images/a66f42761ca69b75002ee1912380157e1ec36af1c74d74f829da7ed83fd4858a.jpg)

<details>
<summary>text_image</summary>

PYTHON
Python Debugger
Python Debugger extension using ...
Microsoft
isort
Import organization support for Py...
Microsoft
Python
Python language support with exte...
Microsoft
Pylance
A performant, feature-rich languag...
Microsoft
Python Environments
Provides a unified python environm...
Microsoft
Python Indent
Correct Python indentation
Kevin Rose
安装
</details>

# 2.3 选择Python解释器：选择python3.13安装路径的exe

使用 Ctrl+Shift+P 快捷键打开 command palette 窗口  
输入关键字 python select 并找到 Python: Select Interpreter 一项， 点击该项并在随后弹出的 Python 解释器列表中选择目标解释器：

![](images/4fb22584dd8fcd269ea7f89866b77c4fba94e571fc18575e3f38b2db4315e72c.jpg)

<details>
<summary>text_image</summary>

文件(F) 编辑(E) 选择(S) 查看(V) 转到(G) 运行(R) 终端(T) 帮助(H)
扩展: 满改
Python
Python Debugger 473ms
Python Debugger extension using ...
Microsoft
isort 187ms
Import organization support for Py...
Microsoft
Python 1915ms
Python language support with exte...
Microsoft
Pylance 1520ms
A performant, feature-rich languag...
Microsoft
Python Environments 1095ms
Provides a unified python environm...
Microsoft
Python Indent 16.2M ★4
Correct Python indentation
Kevin Rose 安装
Python for VSCode 6.4M ★2
Python language extension for vcscn...
Thomas Haakon Townsend 安装
Python Extension ... 12.8M ★4.5
Popular Visual Studio Code extensi...
Don Jayamanne 安装
Python Environme... 12.8M ★4
View and manage Python environm...
Don Jayamanne 安装
autoDocstring - Py... 15.2M ★5
Generates python docstrings auto...
Nile Werner 安装
Python Preview 2.7M ★4.5
Provide Preview for Python Execut...
dongli 安装
Python Extended 1.9M ★4
Python Extended is a vscde snipp...
Taiwo Kareem 安装
Python Path 1.7M ★4.5
Python imports utils.
Python: 选择解析器 最近使用
Python: Select Interpreter
首选项: 打开键盘快捷方式 Ctrl + K Ctrl + S
Preferences: Open Keyboard Shortcuts
"将内联聊天移全面做聊天"的重置选择 其他条令
Reset Choice for 'Move inline Chat to Panel Chat'
"文件操作需要预览"的重置选项
Reset choice for 'File operation needs preview'
帮助: 报告问题...
Help: Report Issue...
帮助: 报告性能问题...
Help: Report Performance Issue...
帮助: 查看许可证
Help: View License
帮助: 订阅 VS Code 新闻邮件
Help: Signup for the VS Code Newsletter
帮助: 辅助功能入门
Help: Get Started with Accessibility Features
帮助: 启上浏览
打开聊天 Ctrl + Alt + I
显示所有命令 Ctrl + Shift + P
开始调试 FS
问题 输出 调试控制台 筛编 试口
PS D:\new_tdx_test\PYPlugins\user>
</details>

# 2.4 在VSCode终端-扩展-分别输入下文，常用库建议安装：

pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple   
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple   
pip install backtrader -i https://pypi.tuna.tsinghua.edu.cn/simple

![](images/91786a6b1c6e220ca798ff821b5f9b1e94efcb38bb2a65fc262ff060a38b23ff.jpg)

<details>
<summary>text_image</summary>

USER
>_pycache_
>_idea
taxdata_test.py
tqcenter.py
打开聊天	Ctrl + Alt + I
显示所有命令	Ctrl + Shift + P
开始调试	FS
问题	输出	调试控制台	终端	端口
PS D:\new_tdx_test\PyPlugins\user> plp install numpy -1 https://pypl.tuna.tsinghua.edu.cn/simple
大写
> 时间线
</details>

在 VSCode 中打开要调试的文件（如 tdxdemo.py）  
在代码行号左侧单击，出现红点即表示断点已设置。  
选择调试配置：点击左侧活动栏的“运行和调试”图标（或按 Ctrl+Shift+D),选择并启动调试配置（调试器类型选择 “PythonDebugger” ）  
自动生成配置：完成以上步骤后，VSCode会自动在项目根目录创建一个 .vscode 文件夹，并在里面生成 launch.json 文件.同时，调试下拉菜单就会出现，默认选中了“Python 文件”这个配置。  
启动调试：按 F5 或点击绿色的“开始调试”按钮。

![](images/38718bea8d0e8657126e98803fc3ef56df56d3384b28282f1bab155347d45dbf.jpg)

<details>
<summary>text_image</summary>

选择项目目录
2.选择策略文件
3.打上断点
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
code
函数的使用程序，将函数的使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，使用程序执行。如果在该函数中，则从以下顺序依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次依次次序操作
</details>

显示选择调试配置-“ Python文件 ”，调试打开的 Python 文件。

![](images/9698afc2844f2d0bc0fa683f7d4bb8b64f670fe123466c1ab0f297cc9b4ff0b6.jpg)

<details>
<summary>text_image</summary>

localhost
# print(market_snapshot)
# print(market_snapshot)
#
import 可转清基础数据
#
cb_info = tq.get_cb_info(stock_code = '123049.52')
print(cb_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipo_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc_info(ipc_type=2, ipc_date=1)
print(ipc_info)
#
ipc_info = tq.get_ipc info stock_code='688318.SH', field_list=0]
print(fc) fdc = ('Activecapital': '25611.65', 'BelongHS300': 0', 'BelongHS61': 1', 'BelongHasXQ2': 0', 'BelongRZQ': 1', 'DelayMin': 0', 'EndImer': 0', 'ErrorId': 0', 'F2': ['578', '600', '780', '900', '900']
# field_list可以将选返回字段。默认返回全部字段 比如 field_list['Fn193', 'Fn194']
# report_type 可选 'report_time' 按截止日期 'announce_time' 按公告日期 进行筛选
# fd = tq.get_financial_data(
# stock_list['688318.SH'],
# field_list['Fn193', 'Fn194', 'Fn195', 'Fn196', 'Fn197'],
# start_time='20250181',
# end_time='',
# report_type='announce_time')
# print(fd)
#
fd
# fd = tq.get_financial_data_by_date(
# stock_list['688318.SH'],
# field_list['Fn193', 'Fn194', 'Fn195', 'Fn196', 'Fn197'],
# year=0,
# mmd=0)
# print(fd)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
##
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://www.hk/
#http://wksyj: '0.06', '0.06', '0.06'
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# http://www.hk/
# # 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
$ \uwave{\text{if}} $ (if) {
    if (if) {
        if (if) {
            if (if) {
                if (if) {
                    if (if) {
                     if (if) {
                      if (if) {
                        if (if) {
                            if (if) {
                             if (if) {
                          if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if) {
                            if (if)n(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)
    # If(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(If)(Of(If)(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of(Of<nl>
<fcel>// / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /<nl>
<fcel>// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// ://<nl>
<fcel>// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// :// : //<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/<nl>
<fcel>/# 1.运行到断点处
3.点击调试控制台
4.查看输出结果
3.输入python语句，可以查看变量
</details>

# 3.用户py的文件位置

在策略管理器界面，点击[文件位置]。

用户的py文件一般在客户端PYPlugins下面的user目录下面。py运行过程的生成的文件一般在PYPlugins下面的data和file目录下。

# 1. 安装通达信终端

# 1.1 下载地址

内测版下载入口： 通达信金融终端内测版

量化模拟下载入口： 金融终端(量化模拟)

正式版下载入口： 通达信金融终端64位版、通达信专业研究版

# 1.2 登录通达信金融终端

![](images/d2f7adb9050c45449b9bea0582ea7fbebb02da519b6df09d51f6d20900a92b2c.jpg)

<details>
<summary>text_image</summary>

系统 功能 深度 报价 分析 扩展市场行情 特灵交易 资讯 工具 帮助 安易策略 发现 市场 问小达 TO策略已开启 CC
行情级别 制新竞价 资金能动力 资金博弈 DCE排名 SUP统计
代码 名称(19) 涨幅% 现价 涨跌 买价 卖价 总量 现量 涨速% 换手% 今开 最高 最低 昨收 市盈动向 总金额 量比 细分行业 地区 振幅% 均价 内盘 外盘 内外比 温价% 买量 卖量 ?
300548 长芯博创 R -4.34 147.96 -6.72 147.95 147.96 196692 7 0.03 7.30 155.09 157.66 146.33 154.68 129.43 29.8亿 1.42 网络搭配及塔塔 浙江 7.32 150.36 118019 78673 1.50 0.00 4 3
603118 共通股份 R 0.17 11.54 0.02 11.53 11.54 67522 5 0.09 0.86 11.56 11.67 11.49 11.52 78.97 7800万 0.95 通信终端及配件 深圳 1.56 11.56 34504 33018 1.05 0.00 213 323
300627 华测导航 R 1.12 33.28 0.37 33.25 33.28 116666 28 -0.17 1.80 32.90 33.46 32.78 32.91 39.85 3.87亿 1.22 其他通信设备 上海 2.07 33.15 47845 68821 0.70 0.00 22 22
000586 汇源通信 -0.35 14.25 -0.05 14.24 14.25 46184 2 -0.13 2.39 14.30 14.46 14.08 14.30 140.04 6567万 1.04 光纤光线 四川 2.66 14.22 25105 21079 1.19 0.00 77 37
002161 远望谷 R 0.98 7.24 0.07 7.24 7.25 63342 6 -0.13 0.87 7.17 7.30 7.15 7.17 27.76 4436万 1.22 其他通讯设备 浏圳 2.09 7.23 27914 33428 0.84 0.00 597 97
002491 遥昂互联 R -1.53 6.45 -0.10 6.45
002194 武汉凡谷 R 1.71 13.08 0.22 13.08 运行 断开连接 全部启动 全部断开 宽客论坛 建议使用Python3.1和VSCode 启动外部编辑器 新增策略 修改策略 删除策略
300183 松软载波 R -0.14 14.73 -0.02 14.72 策略名称 文件名称 状态 开始时间 停止时间 数据调用数 文易调用数 输出信息数 策略名称
300211 *ST亿通 R -0.73 8.26 0.06 8.26 外部 tdxdata_test.py 停止 11:03:26 11:03:26 (1/75B) 0
300615 航天科技 R -0.22 13.48 -0.03 13.47
300711 广哈通信 R -1.88 -22.78 -0.42 -22.78
600487 空通光电 R -4.86 -25.62 -1.31 -25.61
600522 中天科技 R -2.97 -18.65 -0.57 -18.64
600775 南京熊猫 R -0.25 -12.08 -0.03 -12.08
601869 长飞光纤 S -5.19 -123.73 -6.77 -123.72
603042 华脉科技 R -1.59 -17.91 -0.28 -17.90
688080 映翰通 K -0.24 -58.78 --0.12 -58.78
688143 长盈通 K -2.90 -48.22 -1.36 -48.21
688292 浩瀚深度 K -0.18 -27.00 --0.05 -27.00
[1:0:2:5] 外部略升连接！
[1:0:3:18] 外部开始运行！
[1:0:3:18] 外部断开连接！
[1:0:3:26] 外部开始运行！
[1:0:3:26] 外部断开连接！
保存 重置 文件位置 分类 ▲主力资金 ▲即时决策 ▲回款 ▲动态形状 ▲A股 ▲北证 ▲时代 ▲科创 ▲B股 ▲基金 ▲债券 ▲REITs ▲新三板 ▲版状指数 ▲港关联动 ▲自送 ▲版状 ▲自定 ▲港票 ▲期货现货 ▲期权 ▲基金理财 ▲环境行情 ▲其它 ▲
</details>

中国百强城市价值丰》发布：城市音争超精音赛转向效室音赛 指勤“除名”，业德牛速与股车尚离，红日翡业临条重困情 市场监督管理总局等两部门：变更个人信息出境认证依据提准 港脱医荷2025：TD共情认购火爆政策新规强力助d，普及版新用户专享月卡20元

总成交11139亿高级行情\_上海双线9

![](images/a9c12fc1e989b96ad28ef99b5940356b360d26e46dad22d7aebeeb3953f5edbf.jpg)

# 1.3 系统-盘后数据下载

进行日线和分钟线等数据下载

![](images/4b33221955c54b7c4060bb94967284130ed8f393cd92df2621eabb1133ec9121.jpg)

<details>
<summary>text_image</summary>

盘后数据下载
沪深京日线* 沪深京分钟线 沪深京分时图 扩展市场行情日线 扩展市场行情分钟线
✓ 日线,实时行情和日线统计数据
2025-12-19 ~ 2025-12-25
□ 下载所有AB股类品种的日线数据
下载数据覆盖本地原有数据。本地选股、报表分析、日线以上周期本地复权等需要使用这些数据。网络慢时请酌情下载，选择较少品种和较短时间段。
交易日在15:45后才能下载到当天沪深京数据，其它市场行情数据请在相应市场收盘以后下载。
日线以上周期数据通过下载日线数据生成，5倍数的分钟线数据通过5分钟线生成，其它分钟线数据通过1分钟线生成。
较长日线段没有下载时,可点击此处获取日线完整包
品种代码 品种名称
$ 600000 浦发银行
$ 000001 平安银行
添加品种 移出品种 清空品种
下载完毕.
开始下载 关闭
</details>

# 2. 使用VSCode集成环境

# 2.1 使用VSCode运行py

# 2.1.1 打开py文件

在 VS Code 中点击打开一个本地文件夹，“文件”->"打开文件夹"。

![](images/461d72e45b24433b163c1e75e37fcfe2436c12b1696771c9f0617452947edecb.jpg)

<details>
<summary>text_image</summary>

文件(E) 编辑(E) 选择(S) 查看(V) 搜索
欢迎
Visual Studio Code
编辑进化
启动
新建文件...
打开文件...
打开文件夹...
连接到...
生成新工作区...
最近
user D:\new_tdx_test\PYPlugins
pytest E:\投研产品-量化交易
PythonTest D\
launcher C:\Users\DELL\vscode\extensions\ms-python.python-2022.10.1...
case D:\PythonTest
演练
开始使用 VS Code
自定义编辑器、了解基础知识并开始编码
了解基础知识
Python 开发入门 已更新
Jupyter 笔记本入门 已更新
启动时显示欢迎页
</details>

# 2.1.2 运行py文件

![](images/f8bc6ae7468d24df848b62e4d877d8ba797baaf114bc9c8d37b6247bb176d28a.jpg)

<details>
<summary>text_image</summary>

USER
> _pycache_
> idea
txdata_test.py
tqcenter.py
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
... 
获取x线数据 获取x线数据需要先在客户端中下载对应盘后数据。调用会触发客户端刷新数据。移时过长请耐心等待
field_list可以被选返回字段。默认返回全部字段 比如 field_list-["Open", "Close"] 既是只取开盘价和收盘价
count可以设置每只股票取的数据量
暂时不支持获取分笔数据
开高低收单位为元，成交量单位为手，成交额单位为万元
df = tq.get_market_data(
    field_list-["close"],
    stock_list-codes,
    start_time-starttime,
    end_time-endtime,
    # count>30,
    dividend_type-dividend_type,
    period=period,
    # fill_data=True
)
print(df)
帮助分析分配数据
问题 输出 调试控制台 维编 端口
PS D:\new_tdx_test\PYPlugins\user> & D:\Python\Python31\python.exe d:/new_tdx_test/PYPlugins/user/tdxdata_test.py
TDX数据接口自动初始化成功，使用路径：d:\new_tdx_test\PYPlugins\user/tdxdata_test.py
{'close': 000001.5Z}
2025-12-19  11.62
2025-12-22  11.52
2025-12-23  11.56
2025-12-24  11.54
2025-12-25  11.60)
PS D:\new_tdx_test\PYPlugins\user>
</details>

注意：客户端安装目录下面的 .../PYPlugins/user 文件夹中的 tqcenter.py 是最主要的TQData支撑文件，请勿修改或删除，否则需要重新下载。

# 2.2 使用VSCode编辑新文件

# 2.2.1 新建py文件

在打开的文件夹中鼠标右键创建新的".py" python 文件，文件名例如tdxdemo.py。

![](images/33e1b432f22686a7e7b9f48f3ec4506a515b1d7391ac4f028b34a5d5cfd59e8c.jpg)

<details>
<summary>text_image</summary>

pytest - Visual Studio Code
EXPLORER
PYTEST
New File
New Folder
Reveal in File Explorer	Shift+Alt+R
Open in Integrated Terminal
Add Folder to Workspace...
Open Folder Settings
Remove Folder from Workspace
Find in Folder...	Shift+Alt+F
Paste	Ctrl+V
Copy Path	Shift+Alt+C
Copy Relative Path	Ctrl+K	Ctrl+Shift+C
创建python文件
Show All Commands	Ctrl + Shift + P
Go to File	Ctrl + P
Find in Files	Ctrl + Shift + F
Start Debugging	F5
Toggle Terminal	Ctrl + 
OUTLINE
</details>

# 2.2.2 编辑py文件

<table><tr><td>1</td><td></td><td>py</td></tr><tr><td>2</td><td colspan="2"># 使用tqcenter的API函数查看平安银行日线数据示例</td></tr><tr><td>3</td><td colspan="2">from tqcenter import tq</td></tr></table>

```python
cq Troilize(____), 所有策略连接通过给客户端都必须调用此函数进行仿矩阵

#获取平安银行日线前复权收盘数据
df = tq.get_market_data(
    field_list = ['Close'],
    stock_list = ["000001.SZ"],
    start_time = '20251219',
    end_time = '20251225',
    dividend_type='front',
    period='1d',
)
print(df) 
```

运行结果如图：  
![](images/cf4c8b1ed5f0e10a558263dc24094f3be0d72e123d9550e4b6d98b369ab18938.jpg)

<details>
<summary>text_image</summary>

文件(F) 编辑(E) 选择(S) 查看(V) 转到(G) 运行(R) 终锁(L) 帮助(H)
资源管理器
USER
    >_pycache_
    >_idea
    txddata_test.py
    txddemo.py
    tqcenter.py
    tdxdema_test.py
    tdxdemo.py
    tdxdemo.py > _
1 from tqcenter import tq
2 
3 #初始化
4 tq.initialize(_file_) #所有策略连接通达信客户端必须调用此函数进行初始化
5 
6 #获取平安银行日线前复权收盘数据
7 df = tq.get_market_data(
8    fifoId_list = ['Close'],
9    stock_list = ["000001.SZ"],
10    start_time = '20251219',
11    end_time = '20251225',
12    dividend_type='front',
13    period='1d',
14 )
15 print(df)
16 
17
问题 输出 网试验制台 终错 端口
PS D:\new_tdx_test\PPPlugins\user> & D:\Python\Python313\python.exe d:/new_tdx_test/PPPlugins/user/tdxdemo.py
TDX数据接口自动初始化成功，使用路径：di:\new_tdx_test\PPPlugins\user\tdxdemo.py
{"Close": 000001.SZ"
2025-12-19  11.62
2025-12-22  11.52
2025-12-23  11.56
2025-12-24  11.54
2025-12-25  11.50)
PS D:\new_tdx_test\PPPlugins\user>
</details>

← 安装Python及开发环境

快速开始第一个策略 →

# 步骤分解

一个完整选股入自定义板块策略只需要两步:

# 第一步：客户端新增自定义板块

![](images/b2862750d7109d8217d2a5c5ab04c1063c1ab23593a88a42813b450e560ecea4.jpg)

<details>
<summary>text_image</summary>

系统
功能
深度
报价
分析
扩展市场行情
特灵交易
资讯
工具
帮助
交易策略
发现
市场
问小话
TO策略已开启
自选股
行情报价
财报竞价
资金超动力
资金博弈
DOE排名
SUP统计
代码
名称
涨幅%
现价
涨跌
买价
卖价
总量
现量
涨跌%
换手%
今开
最高
最低
昨收
市盈(动)
总金额
量比
细分行业
地区
振幅%
均价
内盘
外盘
内外比
溢价%
买量
卖量 ?
1 999999 上证指数
0.51 3961.15 20.20
- - 3.94亿
- - 0.04 0.83 3937.72 3964.07 3936.08 3940.95 16.83 6671亿 0.95
0.71 3979.02
- - - 0.00 -
自定义板块设置
自定义板块管理 自定义板块显示设置
自选股股
临时条件股
新建板块
删除板块
板块改名
前移 后移
最前 最后
自选起迁移
LZXG(11)
新板块
板块名称: 涨幅选股
板块简称: ZFXG
(板块简称用于键盘精灵选板块和磁盘文件
(为了便于同步板块, 板块简称不要使用汉字)
确定 取消
保存板块[推荐]
添加品种
移出 清空
前移 后移
最新 最后
板块内排序√
导出板块
导入板块√
确定 取消
自选类别 自选公告 自选研报 每日个股精选
分类▲主力资金■即时決算■动态新状▲A股■北证■财针■科创■B股■基金▲债券▲REITs ▲新三板 ▲板块指数 ▲进关联动 ▲自选 ▲板块 ▲自定 ▲重组 ▲期货现货 ▲缩股 ▲基金理财 ▲环球行情 ▲其它▲□
普通股数 近一个自然人超15.9亿元, 电网设备ETF (150326) 午后拉升, 规模创历史奠基 通由深泽等获在国内新增法应证 昊志电机20nm封板!今日, 机器人板块循环购起准备章?
海通证券: 总城互联促进进口模型与应用产业发展 维持计算机行业“推荐”评级 11亿元 封关后 普及增强版 线线宝网悉先机 打板必备
TQ借助管理器 X 3% 6671亿 深证13544.05 57.63 0.43% 9673亿 北证1461.22 15.67 1.08% 162.6亿 前业3241.92 12.34 0.38% 4520亿 科创1351.44 -0.69 -0.05% 384.7亿 沪深4645.52 11.46 0.25% 3268亿 总成交 16506亿 高级行情 上海双线9
</details>

# 第二步：在VSCode里面运行以下python代码

实现运行函数：在这个策略里, 我们会根据运行结果做出相应操作:

```python
# 策略说明：如果运行时间点价格高出昨收5%，则进入涨幅选股板块，否则清空该板块
import pandas as pd
import numpy as np
from datetime import datetime
from tqcenter import tq

# 初始化tq
tq.initialize(__file__)
# 1. 基础配置
batch_codes = tq.get_stock_list_in_sector('通达信88')    # 目标板块
start_time = "20251025"    # 数据起始日期
target_end = datetime.now().strftime("%Y%m%d")    # 数据结束日期（当前日期）
target_gain = 5.0    # 目标涨幅（%），可修改
target_block_name = 'ZFXG'    # 目标自定义板块简称

# 2. 获取并整理收盘价数据
df_real = tq.get_market_data(
    field_list=['Close'],
    stock_list=batch_codes,
    start_time=start_time,
    end_time=target_end, 
```

```python
# 转换为「日期×股票代码」的收盘价宽表
close_df = tq.price_df(df_real, 'Close', column_names=batch_codes)

# 3. 核心：计算当日相较于昨日的涨幅（%）
# 昨日收盘价（向下平移1行）
prev_close = close_df.shift(1)
# 计算涨幅：（当日收盘价 - 昨日收盘价）/ 昨日收盘价 × 100%
daily_gain = (close_df - prev_close) / prev_close * 100

# 4. 筛选符合条件的股票（最新交易日涨幅超target_gain%）
latest_date = daily_gain.index[-1]    # 最新交易日
latest_daily_gain = daily_gain.loc[Latest_date] # 每只股票最新交易日的涨幅
# 筛选条件：涨幅 > target_gain%（排除NaN，避免数据异常）
target_stocks = latest_daily_gain[Latest_daily_gain > target_gain].sort_values(ascending=False)
target_stocks_list = target_stocks.index.tolist()    # 提取符合条件的股票代码列表

# 5. 结果输出与自定义板块操作（可按需注释）
print(f"\n=== 筛选结果（当日涨幅>{target_gain}%) ===")
if not target_stocks.empty:
    # ==================== 模块1：打印筛选结果 ====================
    print("【模块1：打印筛选结果】")
    print(f"符合条件的股票共 {len(target_stocks)} 只：")
    print(f"{股票代码':<12} {'昨日收盘价':<12} {'当日收盘价':<12} {'当日涨幅':<10}")
    print("-" * 50)
    for stock_code, gain in target_stocks.items():
    prev_price = prev_close.loc[Latest_date, stock_code]
    curr_price = close_df.loc[Latest_date, stock_code]
    print(f"{stock_code:<12} {prev_price:<12.2f} {curr_price:<12.2f} {gain:<.2f}%")
    print("-" * 50)

    # ==================== 模块2：添加至自定义板块 ====================
    try:
    print("【模块2：自定义板块操作】")
    tq.send_user_block(block_code=target_block_name, stocks=target_stocks_list, show=True)
    print(f" ✓ 已成功将股票添加至自定义板块「{target_block_name}」")
except Exception as e:
    print(f" ✗ 添加自定义板块失败：{e}")
print("-" * 50)

else:
    # ==================== 模块1：打印空结果 ====================
    print("【模块1：打印筛选结果】")
    print(f"暂无当日涨幅>{target_gain}%的股票")
print("-" * 50)

    # ==================== 模块2：清空自定义选板块 ====================
    try:
    print("【模块2：自定义板块操作】")
    tq.send_user_block(block_code=target_block_name, stocks=[],show=True)
    print(f" ✓ 已清空自定义板块「{target_block_name}」")
except Exception as e:
    print(f" ✗ 清空自定义板块失败：{e}")
print("-" * 50) 
```

# 结果示例

VSCode端

![](images/50446929fe3e56756bd67bf4c278a3c6183b7875aecff5511bbd6dcf29e8225b.jpg)

<details>
<summary>text_image</summary>

资源清理机制已注册
TDX数据接口自动初始化成功，使用路径：d:\new_tdx_test\PYPlugins\user\涨幅选股.py
=== 筛选结果（当日涨幅＞5.0%） ===
【模块1：打印筛选结果】
符合条件的股票共 4 只：
股票代码	昨日收盘价	当日收盘价	当日涨幅
300274.SZ	167.88	183.58	9.35	%
300699.SZ	32.16	35.01	8.86	%
603993.SH	18.70	19.94	6.63	%
601899.SH	32.03	33.69	5.18	%
【模块2：自选板块操作】
✓ 已成功将股票添加至自选板块「ZFXG」
TDX数据连接已自动关闭
PS D:\new_tdx_test\PYPlugins\user>
</details>

通达信终端

<table><tr><td>行情报价</td><td>封板竞价</td><td>资金能动力</td><td>资金博弈</td><td>DC排名</td><td>SUP统计</td><td colspan="14"></td><td>行情筛选</td><td>分类过滤</td><td>组合分析</td><td>自选管理</td><td>多星网列</td><td>综合排名</td><td>定制版面</td><td></td></tr><tr><td>代码</td><td>名称(4)</td><td>涨幅%</td><td>现价</td><td>涨跌</td><td>买价</td><td>卖价</td><td>总量</td><td>现量</td><td>涨速%</td><td>换手%</td><td>今开</td><td>最高</td><td>最低</td><td>昨收</td><td>市盈动加</td><td>总金额</td><td>量比</td><td>细分行业</td><td>地区</td><td>振幅%</td><td>均价</td><td>内盘</td><td>外盘</td><td>内外比</td><td>溢价%</td><td>买量</td><td>卖量?</td></tr><tr><td>300274</td><td>阳光电源</td><td>R 9.66</td><td>184.09</td><td>16.21</td><td>184.09</td><td>184.12</td><td>820288</td><td>230</td><td>0.82</td><td>5.16</td><td>169.88</td><td>184.12</td><td>168.85</td><td>167.88</td><td>24.09</td><td>145.7亿</td><td>3.98</td><td>光伏逆变器</td><td>安徽</td><td>9.10</td><td>177.56</td><td>303389</td><td>516899</td><td>0.59</td><td>0.00</td><td>2</td><td>142</td></tr><tr><td>300699</td><td>光威复材</td><td>R 8.86</td><td>35.01</td><td>2.85</td><td>35.00</td><td>35.01</td><td>749792</td><td>244</td><td>-0.13</td><td>9.13</td><td>33.33</td><td>36.66</td><td>33.13</td><td>32.16</td><td>52.62</td><td>26.1亿</td><td>7.07</td><td>碳纤维</td><td>山东</td><td>10.98</td><td>34,78</td><td>291898</td><td>457893</td><td>0.64</td><td>0.00</td><td>7440</td><td>338</td></tr><tr><td>603993</td><td>洛阳钼业</td><td>R 6.50</td><td>19.93</td><td>1.23</td><td>19.93</td><td>19.94</td><td>158.9万</td><td>132</td><td>-0.19</td><td>0.91</td><td>19.04</td><td>19.99</td><td>18.98</td><td>18.70</td><td>22.39</td><td>30.9亿</td><td>2.07</td><td>钨钼</td><td>河南</td><td>5.40</td><td>19,47</td><td>548906</td><td>104.0万</td><td>0.53</td><td>0.00</td><td>5</td><td>95</td></tr><tr><td>601899</td><td>紫金矿业</td><td>R 5.12</td><td>33.67</td><td>1.64</td><td>33.66</td><td>33.68</td><td>165.6万</td><td>436</td><td>0.03</td><td>0.80</td><td>32.60</td><td>33.77</td><td>32.55</td><td>32.03</td><td>17.73</td><td>54.8亿</td><td>2.01</td><td>铜</td><td>福建</td><td>3.81</td><td>33,10</td><td>591167</td><td>106.5万</td><td>0.56</td><td>0.00</td><td>226</td><td>19</td></tr></table>

分类

# 初始化initialize

initialize(\_\_file\_\_) #所有策略连接通达信客户端都必须调用此函数进行初始化

py

# 调用方法:

```python
from tqcenter import tq
tq.initialize(__file__) 
```

py

# 注意事项:

1."initialize"不可修改。  
2.该函数用于初始化，任何一个策略都必须有该函数。

← 快速开始第一个策略

订阅行情subscribe\_hq →

# 订阅行情subscribe\_hq

# 订阅股票实时更新

```python
1 subscribe_hq(stock_list: List[str] = [],callback = None): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>订阅的证券代码</td></tr><tr><td>callback</td><td>Y</td><td>str</td><td>回调函数</td></tr></table>

订阅股票更新 传入回调函数，订阅的股票有更新时，系统会调用回调函数，最多订阅100条  
回调函数格式定义为on\_data(datas) datas格式为 {"Code":"XXXXXX.XX","ErrorId":"0"}

# 接口使用

```python
from tqcenter import tq

tq.initialize(__file Dynamic)

# 回调函数 功能为收到更新后请求最新的report数据
def my_callback_func(data_str):
    print("Callback received data:", data_str)
    code_json = json.loads(data_str)
    print(f"codes = {code_json.get('Code')}")
    report_ptr = tq.get_report_data(code_json.get('Code'))
    print(report_ptr)
    return None

sub_hq = tq.subscribe_hq(stock_list=['688318.SH'], callback=my_callback_func)
print(sub_hq)

# 收到更新时策略需要正在运行
#while True:
# time.sleep(1) 
```

py

# 数据样本

```json
{
    "Error": "订阅688318.SH更新成功.",
    "ErrorId": "0",
    "run_id": "1"
} 
```

# 取消订阅更新unsubscribe\_hq

# 取消订阅股票实时更新

```python
1 unsubscribe_hq(stock_list: List[str] = []): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码</td></tr></table>

订阅股票更新 传入回调函数，订阅的股票有更新时，系统会调用回调函数，最多订阅100条  
回调函数格式定义为on\_data(datas) datas格式为 {"Code":"XXXXXX.XX","ErrorId":"0"}

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
un_sub_ptr = tq. unsubscribe_hq(stock_list=['688318.SH'])
print(un_sub_ptr) 
```

py

# 数据样本

```json
{
    "Error": "取消全部订阅更新失败.",
    "ErrorId": "0",
    "run_id": "1"
} 
```

获得订阅列表get\_subscribe\_hq\_stock\_list

获得当前策略订阅的股票列表  
```python
1 get_subscribe_hq_stock_list(): py 
```

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
sub_list = tq.get_subscribe_hq_stock_list()
print(sub_list) 
```

数据样本  
```txt
1 ['600519.SH'] 
```

← 取消订阅更新unsubscribe\_hq

刷新行情缓存refresh\_cache →

# 刷新行情缓存(最新snapshot和K线数据)refresh\_cache

刷新行情缓存(最新snapshot和K线数据)。如果不调用，首次取snapshot和K线时系统会自动刷新一次行情

```python
def refresh_cache(market: str = 'AG',
    force: bool = False): 
```

py

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>force</td><td>Y</td><td>bool</td><td>是否强制刷新</td></tr><tr><td>market</td><td>Y</td><td>str</td><td>指定刷新的市场</td></tr></table>

force为false时距离上次刷新不足10分钟则不会刷新，为true时强制刷新。  
market赋值： 'AG'表示A股，'HK'表示港股，'US'表示美股，'QH'表示国内期货，'QQ'表示股票期权，'NQ'表示新三板，'ZZ'表示中证和国证指数，'OF'表示基金净值，'ZS' 表示沪深京指数，'OJ' 表示期货期权。

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
refresh_cache = tq.refresh_cache()
print(refresh_cache) 
```

py

# 数据样本

使用后会在客户端弹出刷新数据的加载界面，加载完成后才会有返回

```json
{
    "Error" : "Refresh Cache Success.",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 刷新历史K线缓存refresh\_kline

根据股票和周期刷新历史K线缓存，如果本地没有下载完整的日线等数据，则可以调用这个函数定向下载某些品种某些周期的历史K线数据

```python
1 refresh_kline(stock_list: List[str] = [], period: str = '') 
```

py

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表,证券代码格式为6位数+市场后缀(.SH/.SZ/.BJ等)</td></tr><tr><td>period</td><td>Y</td><td>str</td><td>周期1d为日线、1m为一分钟线、5m为五分钟线,只支持这三种,其它周期的数据均由这三种数据生成</td></tr></table>

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
refresh_kline = tq.refresh_kline(stock_list=['688318.SH'],period='1d')
print(refresh_kline) 
```

py

# 数据样本

注：如果在盘中交易时间段下载1m和5m分钟线，只能下载到截止上个交易日的数据使用后会在客户端弹出刷新数据的加载界面，加载完成后才会有返回

```json
{
    "Error" : "refresh kline cache success.",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 发送消息到通达信客户端send\_message

# 发送消息给通达信客户端的TQ策略界面

```txt
1 send_message(msg_str: str) -> Dict: 
```

```txt
py 
```

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>msg_str</td><td>Y</td><td>str</td><td>消息字符串</td></tr></table>

传入的字符串使用 | 可以让客户端将其分为两条（插入 \n 也可以分行显示）

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
msg_str = "这是第一行. | 这是第二行."
tq.send_message(msg_str)
```

```txt
py 
```

← 获取交易日列表get\_trading\_dates

发送预警信号到客户端send\_warn →

# 发送预警信号send\_warn

往客户端发送指定股票的预警信号  
```python
send_warn(stock_list: List[str] = [],
time_list: List[str] = [],
price_list: List[str] = [],
close_list: List[str] = [],
volum_list: List[str] = [],
bs_flag_list: List[str] = [],
warn_type_list: List[str] = [],
reason_list: List[str] = [],
count: int = 1) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>time_list</td><td>Y</td><td>List[str]</td><td>时间列表</td></tr><tr><td>price_list</td><td>N</td><td>List[str]</td><td>现价列表</td></tr><tr><td>close_list</td><td>N</td><td>List[str]</td><td>收盘价列表</td></tr><tr><td>volum_list</td><td>N</td><td>List[str]</td><td>成交额列表</td></tr><tr><td>bs_flag_list</td><td>N</td><td>List[str]</td><td>买卖标志:0买1卖2未知</td></tr><tr><td>warn_type_list</td><td>N</td><td>List[str]</td><td>预警类型:0常规预警(目前仅支持)</td></tr><tr><td>reason_list</td><td>N</td><td>List[str]</td><td>预警原因</td></tr><tr><td>count</td><td>N</td><td>int</td><td>有效数据个数</td></tr></table>

price\_list、close\_list、volum\_list、bs\_flag\_list、warn\_type\_list 均要求为纯数字字符串List  
bs\_flag\_list 0买1卖2未知，长度小于count的会自动补为2。  
reason\_list每个元素有效长度为25个汉字（50个英文）|  
count限定入参中每个list中的有效数据个数，即每个list前count个数据会传给客户端  
stock\_list与其他list的元素数据是一一对应的，即stock\_list的第一个元素对应的预警信息是其他list的第一个元素，同一只股票的多个预警信息，则在stock\_list中加入多次该股票

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
warn_res = tq.send_warn(stock_list = ['688318.SH', '688318.SH', '600519.SH'],
time_list = ['20251215141115', '20251215142100', '20251215143101'],
price_list = ['123.45', '133.45', '1823.45'],
close_list = ['122.50', '132.50', '1822.50'],
volum_list = ['1000', '2000', '15000'],
bs_flag_list = ['0'],
warn_type_list = ['0'],
reason_list = ['价格突破预警线', '收盘价突破预警线', '成交量突破预警线'], 
```

# 数据样本

```javascript
1 {'Error': '发送预警信号成功.', 'ErrorId': '0', 'run_id': '1'} 
```

← 发送消息到TQ策略界面send\_message

发送文件到客户端send\_file →

# 发送文件到客户端send\_file

往通达信客户端发送文件名，可由TQ策略数据浏览中打开

```txt
1 send_file(file: str) -> Dict: 
```

py

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>file</td><td>Y</td><td>str</td><td>文件路径</td></tr></table>

文件放于 .\PYPlugins\file\ 文件夹中时，file可仅传入文件名  
文件放于其他位置时，file需要传入绝对路径  
目前支持的文件类型：txt，pdf，html

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
file = "test.txt"
tq.send_file(file) 
```

← 发送预警信号到客户端send\_warn

发送回测数据send\_bt\_data →

# 发送回测数据send\_bt\_data

往客户端发送指定股票的回测数据  
```python
1 send_bt_data(stock_code: str = '', 
2 time_list: List[str] = [], 
3 data_list: List[List[str]] = [], 
4 count: int = 1) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>List[str]</td><td>证券代码</td></tr><tr><td>time_list</td><td>Y</td><td>List[str]</td><td>时间列表</td></tr><tr><td>data_list</td><td>N</td><td>List[List[str]]</td><td>回测数据列表</td></tr><tr><td>count</td><td>N</td><td>int</td><td>有效数据个数</td></tr></table>

data\_list为二维List，每个子元素对应time\_list的一个元素时间点，且每个子元素最多有16个有效纯数字字符串，即data\_list每个子List的前16个数据为一个时间点的有效数据  
count限定入参中每个list中的有效数据个数，即每个list前count个数据会传给客户端

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
bt_data = tq.send_bt_data(stock_code = '688318.SH',
    time_list = ['20251215141115'],
    data_list = [['11']], 
    count = 1)
print(bt_data) 
```

数据样本  
```javascript
1 {'Error': '发送回测结果成功.', 'ErrorId': '0', 'run_id': '1'} 
```

# 下载特定数据文件download\_file

10大股东数据文件、ETF申赎清单文件、最近舆情信息文件、股票综合信息文件

```python
download_file(stock_code: str = '',
down_time:str = '',
down_type:int = 1): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>List[str]</td><td>证券代码</td></tr><tr><td>down_time</td><td>Y</td><td>List[str]</td><td>指定日期</td></tr><tr><td>down_type</td><td>Y</td><td>List[str]</td><td>指定下载类型</td></tr></table>

down\_type=1时，下载10大股东数据文件，down\_time为指定日期  
down\_type=2时，下载ETF申赎清单文件，down\_time为指定日期  
down\_type=3时，下载最近舆情信息文件，其余两项无效  
down\_type=4时，下载股票综合信息文件，其余两项无效  
下载的文件保存在 .\PYPlugins\data 文件夹  
down\_type=1时，下载的文件中含指定日期所在年度的所有10大股东数据和流通股东数据

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
# 下载10大股东数据
down_ptr_10 = tq.download_file(stock_code='688318.SH', down_time='20241231', down_type=1)
print(down_ptr_10)
# 下载ETF申赎数据
down_ptr_etf = tq.download_file(stock_code='159109.SH', down_time='20260227', down_type=2)
print(dowm_ptr_etf) 
```

py

数据样本  
```json
{
    "ErrorId": "0",
    "Msg": "下载十大股东数据[2025]成功。",
    "run_id": "1"
}
{
    "ErrorId": "0",
    "Msg": "下载ETF申述清单[20250101]成功。",
    "run_id": "1" 
```

← 缓存历史K线refresh\_kline

获取交易日列表get\_trading\_dates →

# 获取交易日列表get\_trading\_dates

根据指定时间段获取交易日列表  
```python
get_trading_dates(market: str,
    start_time: str,
    end_time: str,
    count:int = -1) -> List: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>market</td><td>Y</td><td>str</td><td>市场代码(暂固定为SH)</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始日期</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束日期</td></tr><tr><td>count</td><td>N</td><td>int</td><td>返回最近的count个交易日</td></tr></table>

需要现在客户端下载上证指数（999999）的盘后数据 目前仅支持A股  
count > 0时，限制返回从结束日期往前最近的count个在限定时间段中的交易日

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
    trade_dates = tq.get_trading_dates(market = 'SH', start_time = '20220101', end_time = '', count = 10);
    print(trade_dates) 
```

数据样本  
```json
1 ['20251211', '20251212', '20251215', '20251216', '20251217', '20251218', '20251219', '20251222', '20251223', '20251224'] 
```

# 导出多组数据到通达信客户端 print\_to\_tdx

将计算数据导出到通达信客户端展示  
```python
print_to_tdx(df_list: list[pd.DataFrame] = [],
sp_name: str = "", 
xml_filename: str = "", 
jsn_filenames: list[str] = None,
vertical: int = None,
horizontal: int = None,
height: list[str | float] = None,
table_names: list[str] = None) -> None: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>df_list</td><td>Y</td><td>list[pd.DataFrame]</td><td>多组数据的DataFrame列表,每组table对应1个DataFrame;每个DataFrame非空且第一列为日期(datetime64[ns]或字符串类型),后续列为指标/因子名称;列表长度需等于组数</td></tr><tr><td>sp_name</td><td>N</td><td>str</td><td>生成.sp文件的名称前缀,为空时默认生成python.sp</td></tr><tr><td>xml_filename</td><td>N</td><td>str</td><td>生成的xml文件名(需包含.xml后缀),为空会影响通达信面板配置关联,建议必填</td></tr><tr><td>jsn_filenames</td><td>Y</td><td>list[str]</td><td>每组数据对应的.jsn文件名列表,列表非空且长度需等于组数(与df_list一致),文件名建议包含.jsn后缀</td></tr><tr><td>vertical</td><td>N</td><td>int</td><td>纵向排列的table组数(≥1),与horizontal二选一,horizontal优先级更高</td></tr><tr><td>horizontal</td><td>N</td><td>int</td><td>横向排列的table组数(≥1),优先级高于vertical,未指定时默认使用vertical或1组</td></tr><tr><td>height</td><td>N</td><td>list[str | float]</td><td>自定义每组gridctrl高度列表,长度需等于组数;元素为数值/字符串(高度占比),未指定时自动计算(1/组数,最后一组高度为0)</td></tr><tr><td>table_names</td><td>N</td><td>list[str]</td><td>每组展示面板的标题列表,长度需等于组数;元素为空时自动使用对应jsn_filenames的前缀作为标题</td></tr></table>

df\_list、jsn\_filenames长度必须与vertical/horizontal指定的组数完全一致，否则会抛出ValueError异常  
height参数值为高度占比（如0.3/"0.3"），表示该面板占整体展示区域的比例，仅支持0-1之间的数值  
未指定vertical/horizontal时，默认按1组纵向排列展示，自动计算面板高度

# 调用客户端功能

客户端根据入参执行指定功能  
```python
def exec_to_tdx(url:str = ''): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>url</td><td>Y</td><td>str</td><td>功能调用串或网址</td></tr></table>

若是功能串，请以 http://www.treeid 开头

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
exec_res1 = tq.exec_to_tdx(url='http://www.treeid/MAINQH')
exec_res2 = tq.exec_to_tdx(url='http://www.treeid/dlghttp://www.tdx.com.cn')
print(exec_res2) 
```

数据样本  
```javascript
1 {'ErrorId': '0', 'Msg': 'http://www.treeid/dlghttp://www.tdx.com.cn', 'run_id': '1'} 
```

# 获取K线行情get\_market\_data

根据股票，获取历史行情  
```python
get_market_data(field_list: List[str] = [],
    stock_list: List[str] = [],
    period: str = '',
    start_time: str = '',
    end_time: str = '',
    count: int = -1,
    dividend_type: Optional[str] = None,
    fill_data: bool = True) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>field_list</td><td>N</td><td>List[str]</td><td>字段筛选,传空则返回全部</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>period</td><td>Y</td><td>str</td><td>周期</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间</td></tr><tr><td>count</td><td>N</td><td>int</td><td>返回数据个数(每只股票)</td></tr><tr><td>dividend_type</td><td>N</td><td>str</td><td>复权类型:none不复权、front前复权、back后复权</td></tr><tr><td>fill_data</td><td>N</td><td>bool</td><td>是否向后填充空缺数据</td></tr></table>

count<=0时，即返回start\_time和end\_time之间的全部数据

# 返回数据

返回dict { field1 : value1, field2 : value2, ... }   
field1, field2, ... ：数据字段  
value1, value2, ... ：pd.DataFrame 数据集，index为stock\_list，columns为time\_list  
各字段对应的DataFrame维度相同、索引相同  
只有dividend\_type传入为none时，会返回有效的前复权因子ForwardFactor  
后复权数据与取的数据个数有关，只在返回的数据中进行后复权  
一次最多返回24000条数据，要获取完整分钟线需要多次分批获取  
返回复权数据时，若该组数据时间内未发生权息变动，则复权价与未复权价相同，

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>Date</td><td>Y</td><td>str</td><td>日期</td></tr><tr><td>Time</td><td>Y</td><td>str</td><td>时间</td></tr><tr><td>Open</td><td>Y</td><td>str</td><td>开盘价</td></tr><tr><td>High</td><td>Y</td><td>str</td><td>最高价</td></tr><tr><td>Low</td><td>Y</td><td>str</td><td>最低价</td></tr><tr><td>Close</td><td>Y</td><td>str</td><td>收盘价</td></tr><tr><td>Volume</td><td>Y</td><td>str</td><td>成交量</td></tr><tr><td>Amount</td><td>Y</td><td>str</td><td>成交额</td></tr><tr><td>ForwardFactor</td><td>Y</td><td>str</td><td>前复权因子,当dividend_type=none时候返回有效值</td></tr><tr><td>VolInStock</td><td>N</td><td>str</td><td>持仓量</td></tr></table>

期货数据时Amount为0，非期货数据时VolInStock为0

# 接口使用

获取688318.SH从2025-12-20到今为止最新一条日K线的不复权数据

```python
from tqcenter import tq
tq.initialize(__file__)
df = tq.get_market_data(
    field_list=[],
    stock_list=['688318.SH'],
    start_time='20251220',
    end_time='',
    count=1,
    dividend_type='none',
    period='1d',
    fill_data=True
)
print(df) 
```

# 数据样本

```txt
{'Amount': 688318.SH
2025-12-24 29394.81,
'Low': 688318.SH
2025-12-24 128.0,
'Date': 688318.SH
2025-12-24 20251224.0,
'Volume': 688318.SH
2025-12-24 2257325.0,
'Close': 688318.SH
2025-12-24 131.58,
'Open': 688318.SH
2025-12-24 128.01,
'Time': 688318.SH
2025-12-24 0.0,
'High': 688318.SH
2025-12-24 131.87,
'ForwardFactor': 688318.SH
2025-12-24 1.0} 
```

# 获取快照数据get\_market\_snapshot

# 根据股票，获取最新行情数据

```python
def get_market_snapshot(stock_code: str, field_list: List = []) -> Dict: 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>证券代码</td></tr><tr><td>field_list</td><td>N</td><td>List[str]</td><td>字段筛选,传空则返回全部</td></tr></table>

# 返回数据

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>ItemNum</td><td>Y</td><td>str</td><td>快照笔数</td></tr><tr><td>LastClose</td><td>Y</td><td>str</td><td>前收盘价</td></tr><tr><td>Open</td><td>Y</td><td>str</td><td>开盘价</td></tr><tr><td>Max</td><td>Y</td><td>str</td><td>最高价</td></tr><tr><td>Min</td><td>Y</td><td>str</td><td>最低价</td></tr><tr><td>Now</td><td>Y</td><td>str</td><td>现价</td></tr><tr><td>Volume</td><td>Y</td><td>str</td><td>总手</td></tr><tr><td>NowVol</td><td>Y</td><td>str</td><td>现手</td></tr><tr><td>Amount</td><td>Y</td><td>str</td><td>总成交金额</td></tr><tr><td>Inside</td><td>Y</td><td>str</td><td>内盘 板块指数时为跌停家数</td></tr><tr><td>Outside</td><td>Y</td><td>str</td><td>外盘 板块指数时为涨停家数</td></tr><tr><td>TickDiff</td><td>Y</td><td>str</td><td>笔涨跌</td></tr><tr><td>InOutFlag</td><td>Y</td><td>str</td><td>内外盘标志 0:Buy 1:Sell 2:Unknown</td></tr><tr><td>Jjz</td><td>Y</td><td>str</td><td>基金净值</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Buyp</td><td>Y</td><td>List[str]</td><td>五个买价</td></tr><tr><td>Buyv</td><td>Y</td><td>List[str]</td><td>对应的五个买盘量</td></tr><tr><td>Sellp</td><td>Y</td><td>List[str]</td><td>五个卖价</td></tr><tr><td>Sellv</td><td>Y</td><td>List[str]</td><td>对应的五个卖盘量</td></tr><tr><td>UpHome</td><td>Y</td><td>str</td><td>上涨家数 对于指数有效</td></tr><tr><td>DownHome</td><td>Y</td><td>str</td><td>卜跌家数 对于指数有效</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Before5MinNow</td><td>Y</td><td>str</td><td>5分钟前价格</td></tr><tr><td>Average</td><td>Y</td><td>str</td><td>均价</td></tr><tr><td>XsFlag</td><td>Y</td><td>str</td><td>小数位数</td></tr><tr><td>Zangsu</td><td>Y</td><td>str</td><td>涨速</td></tr><tr><td>ZAFPre3</td><td>Y</td><td>str</td><td>3日涨幅</td></tr></table>

# 接口使用

获取688318.SH从2025-12-20到今为止最新一条日K线的不复权数据

```python
from tqcenter import tq
tq.initialize(__file__)
market_snapshot = tq.get_market_snapshot(stock_code = '688260.SH', field_list=[])
print(market_snapshot) 
```

# 数据样本

```json
{'ItemNum': '3342',
'LastClose': '34.21',
'Open': '33.78',
'Max': '36.49',
'Min': '32.50',
'Now': '35.06',
'Volume': '122881',
'NowVol': '1449',
'Amount': '43068.48',
'Inside': '60373',
'Outside': '62509',
'TickDiff': '0.00',
'InOutFlag': '2',
'Jjjz': '0.00',
'Buyp': ['35.05', '35.04', '35.02', '35.01', '35.00'],
'Buyv': ['154', '9', '49', '136', '154'],
'Sellp': ['35.06', '35.07', '35.08', '35.09', '35.10'],
'Sellv': ['4', '31', '139', '4', '4'],
'UpHome': '0',
'DownHome': '0',
'Before5MinNow': '35.15',
'Average': '35.05',
'XsFlag': '2',
'Zangsu': '-0.25',
'ZAFPre3': '-1.83',
'ErrorId': '0'} 
```

# 获取证券基本信息get\_stock\_info

根据股票，获取股票基础的财务数据  
```erlang
get_stock_info(cls,
    stock_code:str,
    field_list: List = []) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>证券代码</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr></table>

返回数据

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>Name</td><td>Y</td><td>str</td><td>证券名称</td></tr><tr><td>Unit</td><td>Y</td><td>str</td><td>交易单位</td></tr><tr><td>VolBase</td><td>Y</td><td>str</td><td>量比的基量</td></tr><tr><td>MinPrice</td><td>Y</td><td>str</td><td>最小价格变动</td></tr><tr><td>XsFlag</td><td>Y</td><td>str</td><td>价格小数位数</td></tr><tr><td>Fz[8]</td><td>Y</td><td>List[str]</td><td>开收市时间(4段)</td></tr><tr><td>DelayMin</td><td>Y</td><td>str</td><td>延时分钟数</td></tr><tr><td>QHVolBaseRate</td><td>Y</td><td>str</td><td>期货期权的每手乘数</td></tr><tr><td>HKVolBaseRate</td><td>Y</td><td>str</td><td>港股/日股/新加坡股 每手股数</td></tr><tr><td>BelongHS300</td><td>Y</td><td>str</td><td>是否属于沪深300</td></tr><tr><td>BelongHasKQZ</td><td>Y</td><td>str</td><td>是否含可转债</td></tr><tr><td>BelongRZRQ</td><td>Y</td><td>str</td><td>是否是融资融券标的</td></tr><tr><td>BelongHSGT</td><td>Y</td><td>str</td><td>是否属于沪深股通</td></tr><tr><td>IsHKGP</td><td>Y</td><td>str</td><td>是否是港股</td></tr><tr><td>IsQH</td><td>Y</td><td>str</td><td>是否是期货</td></tr><tr><td>IsQQ</td><td>Y</td><td>str</td><td>是否是期权</td></tr><tr><td>IsSTGP</td><td>Y</td><td>str</td><td>是否是ST股票</td></tr><tr><td>IsQuitGP</td><td>Y</td><td>str</td><td>是否是退市整理板股票</td></tr><tr><td>TodayDRFlag</td><td>Y</td><td>str</td><td>当天是否有除权除息(沪深京)</td></tr><tr><td>HSStockKind</td><td>Y</td><td>str</td><td>沪深京品种类型 0:指数,1:A股王板,2:北证A股,3:创业板,4:科创板,5:B股,6:债券,7:基金,8:权证,9:其它,10:非沪深京品种</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>ActiveCapital</td><td>Y</td><td>str</td><td>流通股本(万股)</td></tr><tr><td>J_zgb</td><td>Y</td><td>str</td><td>总股本(万股)</td></tr><tr><td>J_bg</td><td>Y</td><td>str</td><td>B股(万股)</td></tr><tr><td>J_hg</td><td>Y</td><td>str</td><td>H股(万股)</td></tr><tr><td>J_zzc</td><td>Y</td><td>str</td><td>总资产(万元)</td></tr><tr><td>J_ldzc</td><td>Y</td><td>str</td><td>流动资产(万元)</td></tr><tr><td>J_gdzc</td><td>Y</td><td>str</td><td>固定资产(万元)</td></tr><tr><td>J_wxzc</td><td>Y</td><td>str</td><td>无形资产(万元)</td></tr><tr><td>J_ldfz</td><td>Y</td><td>str</td><td>流动负债(万元)</td></tr><tr><td>J_cqfz</td><td>Y</td><td>str</td><td>少数股东权益(万元)</td></tr><tr><td>J_zbgjj</td><td>Y</td><td>str</td><td>资本公积金(万元)</td></tr><tr><td>J_jzc</td><td>Y</td><td>str</td><td>股东权益/净资产(万元)</td></tr><tr><td>J_yysy</td><td>Y</td><td>str</td><td>营业收入(万元)</td></tr><tr><td>J_yycb</td><td>Y</td><td>str</td><td>营业成本(万元)</td></tr><tr><td>J_yszk</td><td>Y</td><td>str</td><td>应收账款(万元)</td></tr><tr><td>J_yyly</td><td>Y</td><td>str</td><td>营业利润(万元)</td></tr><tr><td>J_tzsy</td><td>Y</td><td>str</td><td>投资收益(万元)</td></tr><tr><td>J_jyxjl</td><td>Y</td><td>str</td><td>经营现金净流量(万元)</td></tr><tr><td>J_zxjl</td><td>Y</td><td>str</td><td>总现金净流量(万元)</td></tr><tr><td>J_ch</td><td>Y</td><td>str</td><td>存货(万元)</td></tr><tr><td>J_lyze</td><td>Y</td><td>str</td><td>利润总额(万元)</td></tr><tr><td>J_shly</td><td>Y</td><td>str</td><td>税后利润(万元)</td></tr><tr><td>J_jly</td><td>Y</td><td>str</td><td>净利润(万元)</td></tr><tr><td>J_wfply</td><td>Y</td><td>str</td><td>未分配利益(万元)</td></tr><tr><td>J_jyl</td><td>Y</td><td>str</td><td>净资产收益率</td></tr><tr><td>J_mgwfp</td><td>Y</td><td>str</td><td>每股未分配</td></tr><tr><td>J_mgsy</td><td>Y</td><td>str</td><td>每股收益(折算为全年)</td></tr><tr><td>J_mgsy2</td><td>Y</td><td>str</td><td>季报每股收益(财报中提供的每股收益)</td></tr><tr><td>J_mggjj</td><td>Y</td><td>str</td><td>每股公积金</td></tr><tr><td>J_mgjzc</td><td>Y</td><td>str</td><td>每股净资产</td></tr><tr><td>J_mgjzc2</td><td>Y</td><td>str</td><td>季报每股净资产(财报中提供的每股收益)</td></tr><tr><td>J_gdqyb</td><td>Y</td><td>str</td><td>股东权益比</td></tr><tr><td>J_gdrs</td><td>Y</td><td>str</td><td>股东人数</td></tr><tr><td>J_HalfYearFlag</td><td>Y</td><td>str</td><td>报告期月份(3,6,9,12)</td></tr><tr><td>J_start</td><td>Y</td><td>str</td><td>上市日期</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>tdx_dycode</td><td>Y</td><td>str</td><td>通达信地域代码</td></tr><tr><td>tdx_dyname</td><td>Y</td><td>str</td><td>通达信地域</td></tr><tr><td>rs_hycode_sim</td><td>Y</td><td>str</td><td>通达信行业代码</td></tr><tr><td>rs_hyname</td><td>Y</td><td>str</td><td>通达信行业</td></tr><tr><td>blockzscore</td><td>Y</td><td>str</td><td>所属的行业板块指数代码</td></tr><tr><td>underly_setcode</td><td>Y</td><td>str</td><td>标的市场代码(比如:当前ETF跟踪的指数市场)</td></tr><tr><td>underly_code</td><td>Y</td><td>str</td><td>标的代码(比如:当前ETF跟踪的指数代码)</td></tr></table>

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
fdc = tq.get_stock_info(stock_code='688318.SH', field_list=[])
print(fdc) 
```

py

# 数据样本

```javascript
{'Name': '财富趋势',
'Unit': '100',
'VolBase': '102.22',
'MinPrice': '0.01',
'XsFlag': '2',
'Fz': ['570', '690', '780', '900', '900', '900', '900', '900'],
'DelayMin': '0',
'QHVolBaseRate': '0',
'HKVolBaseRate': '0',
'BelongHS300': '0',
'BelongHasKQZ': '0',
'BelongRZRQ': '1',
'BelongHSGT': '1',
'IsHKGP': '0',
'IsQH': '0',
'IsQQ': '0',
'IsSTGP': '0',
'IsQuitGP': '0',
'TodayDRFlag': '0',
'HSStockKind': '4',
'ActiveCapital': '25611.94',
'J_zgb': '25611.94',
'J_bg': '0.00',
'J_hg': '0.00',
'J_zzc': '389036.97',
'J_ldzc': '235598.84', 
```

```javascript
'J_cqfz': '73.15',
'J_zbgjj': '157998.02',
'J_jzc': '370454.03',
'J_yysy': '19827.85',
'J_yycb': '4258.70',
'J_yszk': '2726.99',
'J_yyly': '20836.07',
'J_tzsy': '5091.96',
'J_jyxjl': '5432.08',
'J_zxjl': '9779.30',
'J_ch': '61.84',
'J_lyze': '20829.85',
'J_shly': '18421.45',
'J_jly': '18421.34',
'J_wfply': '175521.63',
'J_jyl': '4.97',
'J_mgwfp': '6.85',
'J_mgsy': '0.96',
'J_mgsy2': '0.00',
'J_mggjj': '6.17',
'J_mgjzc': '14.46',
'J_mgjzc2': '14.46',
'J_gdqyb': '0.95',
'J_gdrs': '24154.00',
'J_HalfYearFlag': '9',
'J_start': '20200427',
'tdx_dycode': '18',
'tdx_dynam': '深圳板块',
'rs_hycode_sim': 'X4202',
'rs_hynam': '软件服务',
'blockzscode': '881355',
'underly_setcode': '0',
'underly_code': '',
'ErrorId': '0'} 
```

# 获取股票更多信息get\_more\_info

# 获取指定股票更细节的信息

```python
def get_more_info(stock_code:str = '',
    field_list: List = []): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>股票代码</td></tr><tr><td>field_list</td><td>N</td><td>List[str]</td><td>字段筛选,传空则返回全部</td></tr></table>

# 返回数据

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>MainBusiness</td><td>Y</td><td>str</td><td>主营构成</td></tr><tr><td>SafeValue</td><td>Y</td><td>str</td><td>安全分</td></tr><tr><td>ShineValue</td><td>Y</td><td>str</td><td>亮点数</td></tr><tr><td>ShapeValue</td><td>Y</td><td>str</td><td>短期形态+中期形态+长期形态 编号</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>TPFlag</td><td>Y</td><td>str</td><td>停牌标识</td></tr><tr><td>ZTPrice</td><td>Y</td><td>str</td><td>涨停价</td></tr><tr><td>DTPrice</td><td>Y</td><td>str</td><td>跌停价</td></tr><tr><td>HqDate</td><td>Y</td><td>str</td><td>行情日期</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>fHSL</td><td>Y</td><td>str</td><td>换手率</td></tr><tr><td>fLianB</td><td>Y</td><td>str</td><td>量比</td></tr><tr><td>Wtb</td><td>Y</td><td>str</td><td>委比</td></tr><tr><td>Zsz</td><td>Y</td><td>str</td><td>总市值(亿)</td></tr><tr><td>Ltsz</td><td>Y</td><td>str</td><td>流通市值(亿)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>vzangsu</td><td>Y</td><td>str</td><td>量涨速</td></tr><tr><td>Fzhsl</td><td>Y</td><td>str</td><td>分钟换手率</td></tr><tr><td>FzAmo</td><td>Y</td><td>str</td><td>2分钟金额(万元)</td></tr><tr><td>VOpenZAF</td><td>Y</td><td>str</td><td>抢筹涨幅</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>ZAF</td><td>Y</td><td>str</td><td>涨幅</td></tr><tr><td>ZAFYesterday</td><td>Y</td><td>str</td><td>昨日涨幅</td></tr><tr><td>ZAFPre2D</td><td>Y</td><td>str</td><td>前天涨幅</td></tr><tr><td>ZAFPre5</td><td>Y</td><td>str</td><td>5日涨幅</td></tr><tr><td>ZAFPre10</td><td>Y</td><td>str</td><td>10日涨幅</td></tr><tr><td>ZAFPre20</td><td>Y</td><td>str</td><td>20日涨幅</td></tr><tr><td>ZAFPre30</td><td>Y</td><td>str</td><td>30日涨幅</td></tr><tr><td>ZAFPre60</td><td>Y</td><td>str</td><td>60日涨幅</td></tr><tr><td>ZAFYear</td><td>Y</td><td>str</td><td>年初至今涨幅</td></tr><tr><td>ZAFPreMyMonth</td><td>Y</td><td>str</td><td>涨幅(本月来)</td></tr><tr><td>ZAFPreOneYear</td><td>Y</td><td>str</td><td>涨幅(一年来)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Zjl</td><td>Y</td><td>str</td><td>主买净额(万元)</td></tr><tr><td>Zjl_HB</td><td>Y</td><td>str</td><td>主力净流入(万元)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>TotalBVol</td><td>Y</td><td>str</td><td>总买量</td></tr><tr><td>TotalSVol</td><td>Y</td><td>str</td><td>总卖量</td></tr><tr><td>BCancel</td><td>Y</td><td>str</td><td>总撤买量</td></tr><tr><td>SCancel</td><td>Y</td><td>str</td><td>总撤卖量</td></tr><tr><td>L2TicNum</td><td>Y</td><td>str</td><td>L2逐笔成交数</td></tr><tr><td>L2OrderNum</td><td>Y</td><td>str</td><td>L2逐笔委托数</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>FCAmo</td><td>Y</td><td>str</td><td>封单额(万元)</td></tr><tr><td>FCb</td><td>Y</td><td>str</td><td>封成比</td></tr><tr><td>OpenAmo</td><td>Y</td><td>str</td><td>开盘金额(万元)(A股和板块指数有效)</td></tr><tr><td>OpenZTBuy</td><td>Y</td><td>str</td><td>竞价涨停买入金额(万元)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>OpenAmoPre1</td><td>Y</td><td>str</td><td>昨开盘金额(万元)</td></tr><tr><td>OpenVolPre1</td><td>Y</td><td>str</td><td>昨开盘量</td></tr><tr><td>CJJEPre1</td><td>Y</td><td>str</td><td>昨成交额(万元)</td></tr><tr><td>CJJEPre3</td><td>Y</td><td>str</td><td>3日成交额(万元)</td></tr><tr><td>FDEPre1</td><td>Y</td><td>str</td><td>昨封单额(万元)</td></tr><tr><td>FDEPre2</td><td>Y</td><td>str</td><td>前封单额(万元)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>ZTGPNum</td><td>Y</td><td>str</td><td>板块指数的涨停家数</td></tr><tr><td>LastStartZT</td><td>Y</td><td>str</td><td>几天</td></tr><tr><td>LastZTHzNum</td><td>Y</td><td>str</td><td>儿板</td></tr><tr><td>EverZTCount</td><td>Y</td><td>str</td><td>连板天</td></tr><tr><td>ConZAFDateNum</td><td>Y</td><td>str</td><td>连涨天数</td></tr><tr><td>YearZTDay</td><td>Y</td><td>str</td><td>年涨停天数</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>MA5Value</td><td>Y</td><td>str</td><td>5日均价</td></tr><tr><td>HisHigh</td><td>Y</td><td>str</td><td>52周最高</td></tr><tr><td>HisLow</td><td>Y</td><td>str</td><td>52周最低</td></tr><tr><td>IPO_Price</td><td>Y</td><td>str</td><td>发行价</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>More_YJL</td><td>Y</td><td>str</td><td>ETF,LOF溢价率</td></tr><tr><td>BetaValue</td><td>Y</td><td>str</td><td>贝塔系数</td></tr><tr><td>DynaPE</td><td>Y</td><td>str</td><td>动态市盈率</td></tr><tr><td>MorePE</td><td>Y</td><td>str</td><td>市盈率(港股:动,其他扩展:静)</td></tr><tr><td>StaticPE_TTM</td><td>Y</td><td>str</td><td>市盈率(TTM)</td></tr><tr><td>DYRatio</td><td>Y</td><td>str</td><td>股息率</td></tr><tr><td>PB_MRQ</td><td>Y</td><td>str</td><td>市净率(MRQ)</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>IsT0Fund</td><td>Y</td><td>str</td><td>是否是T+0基金</td></tr><tr><td>IsZCZGP</td><td>Y</td><td>str</td><td>是否是注册制A股</td></tr><tr><td>IsKzz</td><td>Y</td><td>str</td><td>是否是可转债</td></tr><tr><td>Kzz_HSCode</td><td>Y</td><td>str</td><td>可转债对应的正股代码</td></tr><tr><td>QHMainYYMM</td><td>Y</td><td>str</td><td>主力合约关联的月份(期货),主力和次主力</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>FreeLtgb</td><td>Y</td><td>str</td><td>自由流通股本(万)</td></tr><tr><td>Yield</td><td>Y</td><td>str</td><td>应计利息(债券),占款天数(回购)</td></tr><tr><td>KfEarnMoney</td><td>Y</td><td>str</td><td>扣非净利润(万元)</td></tr><tr><td>RDInputFee</td><td>Y</td><td>str</td><td>研发费用(万元)</td></tr><tr><td>CashZJ</td><td>Y</td><td>str</td><td>货币资金(万元)</td></tr><tr><td>PreReceiveZJ</td><td>Y</td><td>str</td><td>合同负债(万元)</td></tr><tr><td>OtherQYJzc</td><td>Y</td><td>str</td><td>其它权益工具(万元)</td></tr><tr><td>StaffNum</td><td>Y</td><td>str</td><td>员工人数</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>RecentGGJYDate</td><td>Y</td><td>str</td><td>最近北上大额交易日</td></tr><tr><td>RecentHGDate</td><td>Y</td><td>str</td><td>最近回购预案日</td></tr><tr><td>RecentIncentDate</td><td>Y</td><td>str</td><td>最近股权激励预案日</td></tr><tr><td>NoticeDate_Recent</td><td>Y</td><td>str</td><td>最近业绩预告日</td></tr><tr><td>RecentReleaseDate</td><td>Y</td><td>str</td><td>最近解禁日</td></tr><tr><td>RecentDZDate</td><td>Y</td><td>str</td><td>最近定增日</td></tr><tr><td>ReportDate</td><td>Y</td><td>str</td><td>最近财报公告日期</td></tr><tr><td>ZTDate_Recent</td><td>Y</td><td>str</td><td>近2年最近涨停板日期</td></tr><tr><td>DTDate_Recent</td><td>Y</td><td>str</td><td>近2年最近跌停板日期</td></tr><tr><td>TopDate_Recent</td><td>Y</td><td>str</td><td>近2年最近龙虎榜日期</td></tr><tr><td>StopJYDate_Recent</td><td>Y</td><td>str</td><td>最近停牌日期</td></tr></table>

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
more_info = tq.get_more_info(stock_code = '688318.SH', field_list=[])
print(more_info) 
```

数据样本  
```javascript
{'MainBusiness': '软件服务收入',
'SafeValue': '98',
'ShineValue': '3',
'ShapeValue': '101308',
'TPFlag': '0',
'ZTPrice': '151.62',
'DTPrice': '101.08',
'HqDate': '20260227',
'fHSL': '0.86',
'fLianB': '0.89',
'Wtb': '-0.66',
'Zsz': '326.91',
'Ltsz': '326.91',
'vzangsu': '2.17',
'Fzhsl': '0.12',
'FzAmo': '514.92',
'VOpenZAF': '0.00',
'ZAF': '1.02',
'ZAFYesterday': '-1.21',
'ZAFPre2D': '1.99',
'ZAFPre5': '-1.56',
'ZAFPre10': '-3.44',
'ZAFPre20': '-10.76',
'ZAFPre30': '-10.13',
'ZAFPre60': '-1.59',
'ZAFYear': '-3.54',
'ZAFPreMyMonth': '-5.23',
'ZAFPreOneYear': '10.27',
'Zjl': '0.00',
'Zjl_HB': '0.00',
'TotalBVol': '1295.00', 
```

```txt
35 'L2TicNum': '6880',
36 'L2OrderNum': '29448',
37 'FCAmo': '0.00',
38 'FCb': '0.00',
39 'OpenAmo': '1069400.00',
40 'OpenFDE': '0.00',
41 'OpenAmoPre1': '77.93',
42 'OpenVolPre1': '61.00',
43 'CJJEPre1': '26056.68',
44 'CJJEPre3': '89751.03',
45 'FDEPre1': '0.00',
46 'FDEPre2': '0.00',
47 'ZTGPNum': '0',
48 'LastStartZT': '0',
49 'LastZTHzNum': '0',
50 'EverZTCount': '0',
51 'ConZAFDateNum': '1',
52 'YearZTDay': '0',
53 'MA5Value': '126.56',
54 'HisHigh': '180.86',
55 'HisLow': '83.41',
56 'IPO_Price': '107.41',
57 'More_YJL': '0.00',
58 'BetaValue': '2.31',
59 'DynaPE': '133.10',
60 'MorePE': '107.56',
61 'StaticPE_TTM': '94.99',
62 'DYRatio': '0.28',
63 'PB_MRQ': '8.82',
64 'IsTOFund': '0',
65 'IsZCZGP': '1',
66 'IsKzz': '0',
67 'Kzz_HSCode': '0',
68 'FreeLtgb': '7935.14',
69 'Yield': '106.94',
70 'KfEarnMoney': '9778.22',
71 'RDInputFee': '5894.58',
72 'CashZJ': '60954.52',
73 'PreReceiveZJ': '11281.48',
74 'OtherQYJzc': '0.00',
75 'StaffNum': '446',
76 'RecentGGJYDate': '0',
77 'RecentHGDate': '0',
78 'RecentIncentDate': '0',
79 'NoticeDate_Recent': '0',
80 'RecentReleaseDate': '20230427',
81 'RecentDZDate': '0',
82 'ReportDate': '20251031',
83 'ZTDate_Recent': '20241008',
84 'DTDate_Recent': '0',
85 'TopDate_Recent': '20250625',
86 'StopJYDate_Recent': '0'} 
```

# 获取分红配送数据get\_divid\_factors

根据股票，获取指定时间段内的分红配送数据  
```erlang
get_divid_factors(stock_code: str,
    start_time: str,
    end_time: str) -> pd.DataFrame: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>证券代码</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间</td></tr></table>

返回数据

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>Type</td><td>Y</td><td>str</td><td>类型 1:除权除息 11:扩缩股 15:重新调整</td></tr><tr><td>Bonus</td><td>Y</td><td>str</td><td>红利</td></tr><tr><td>AlloPrice</td><td>Y</td><td>str</td><td>配股价</td></tr><tr><td>ShareBonus</td><td>Y</td><td>str</td><td>送股/扩缩股比例</td></tr><tr><td>Allotment</td><td>Y</td><td>str</td><td>配股</td></tr></table>

# 接口使用

获取688318.SH全部分红配送数据  
```python
from tqcenter import tq
tq.initialize(__file__)
divid_factors = tq.get_divid_factors(
    stock_code='688318.SH',
    start_time='',
    end_time='')
print(divid_factors) 
```

数据样本  
```csv
1
2
3
4
5
1
2
Date
Type Bonus AllotPrice ShareBonus Allotment
2020-09-29 1 6.0 0.0 0.0 0.0
2021-05-27 1 10.0 0.0 0.0 0.0
2022-06-20 1 14.0 0.0 4.0 0.0
2023-06-13 1 5.0 0.0 4.0 0.0 
```

← 获取股票更多信息get\_more\_info

获取股票所属板块get\_relation →

# 获取股票所属板块

# 获取指定股票所属板块信息

1

```python
def get_relation(stock_code:str = ''): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>股票代码</td></tr></table>

# 返回数据

<table><tr><td>数据</td><td>默认返回</td><td>数据类型</td><td>数据说明</td></tr><tr><td>BlockCode</td><td>Y</td><td>str</td><td>板块代码</td></tr><tr><td>BlockName</td><td>Y</td><td>str</td><td>板块名称</td></tr><tr><td>BlockType</td><td>Y</td><td>str</td><td>板块类型</td></tr><tr><td>GPNume</td><td>Y</td><td>str</td><td>成份股数量</td></tr></table>

没有板块代码的板块的BlockCode字段返回"0"

# 接口使用

1
2
3
4
5
6

```python
from tqcenter import tq
from tqcenter import tqconst
tq.initialize(__file__)
gp_block_res = tq.get_relation(stock_code='688318.SH')
print(gp_block_res) 
```

py

# 数据样本

```json
[{'BlockCode': '881355.SH', 'BlockName': '软件服务', 'BlockType': '行业', 'GPNume': '234'}, {'BlockCode': '880218.SH', 'BlockName': '深圳板块', 'BlockType': '地区', 'GPNume': '427'}, {'BlockCode': '880592.SH', 'BlockName': '互联金融', 'BlockType': '概念', 'GPNume': '211'}, {'BlockCode': '880722.SH', 'BlockName': '华为鸿蒙', 'BlockType': '概念', 'GPNume': '262'}, {'BlockCode': '880916.SH', 'BlockName': '国产软件', 'BlockType': '概念', 'GPNume': '266'}, {'BlockCode': '880948.SH', 'BlockName': '人工智能', 'BlockType': '概念', 'GPNume': '1049'}, {'BlockCode': '880956.SH', 'BlockName': '腾讯概念', 'BlockType': '概念', 'GPNume': '295'}, {'BlockName': '沪股通标的', 'BlockType': '风格', 'GPNume': '1763'}, {'BlockName': '融资融券', 'BlockType': '风格', 'GPNume': '4354'}, {'BlockCode': '880805.SH', 'BlockName': '保险重仓', 'BlockType': '风格', 'GPNume': '200'}, {'BlockCode': '880878.SH', 'BlockName': '百元股', 'BlockType': '风格', 'GPNume': '220'}, {'BlockName': '中证500', 'BlockType': '指数', 'GPNume': '500'}, {'BlockName': '中证800', 'BlockType': '指数', 'GPNume': '800'}, {'BlockName': '上证380', 'BlockType': '指数', 'GPNume': '380'}, {'BlockName': '金融科技', 'BlockType': '指数', 'GPNume': '59'}, 
```

← 获取分红配送数据get\_divid\_factors

获取新股申购信息get\_ipo\_info →

# 获取新股申购信息get\_ipo\_info

# 获取今天及未来的新股或新发债申购信息

```python
1 get_ipo_info(ipo_type:int = 0,
2 ipo_date:int = 0): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>ipo_type</td><td>Y</td><td>str</td><td>自定义板块简称</td></tr><tr><td>ipo_date</td><td>Y</td><td>int</td><td>自定义板块名称</td></tr></table>

ipo\_type=0 表示获取新股申购信息  
ipo\_type=1 表示获取新发债信息  
ipo\_type=2 表示获取新股和新发债信息  
ipo\_date=0 表示只获取今天信息  
ipo\_date=1 表示获取今天及以后信息

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
ipo_info = tq.get_ipo_info(ipo_type=2, ipo_date=1)
print(ipo_info) 
```

py

# 数据样本

```json
[{'MaxSG': '0.00', 'PE_Issue': '0.00', 'SGCode': '371036', 'SGDate': '20251226', 'SGPrice': '100.00', 'code': '301036', 'name': '双乐转债', 'setcode': '0'}, {'MaxSG': '0.00', 'PE_Issue': '0.00', 'SGCode': '718676', 'SGDate': '20251225', 'SGPrice': '100.00', 'code': '688676', 'name': '金05转债', 'setcode': '1'}] 
```

# 获取每天的股本数据get\_gb\_info

获取指定股票的股本数据  
```python
def get_gb_info(stock_code:str = '', date_list: List[str] = [], count: int = 1): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>股票代码</td></tr><tr><td>date_list</td><td>Y</td><td>List[str]</td><td>日期数组</td></tr><tr><td>count</td><td>Y</td><td>int</td><td>日期有效个数</td></tr></table>

. date\_list传入的日期须从小到大排序  
date\_list有效数据个数须不小于count，且不能小于1

输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>Date</td><td>double</td><td></td><td>日期</td></tr><tr><td>Zgb</td><td>double</td><td></td><td>总股本</td></tr><tr><td>Ltgb</td><td>double</td><td></td><td>流通股本</td></tr></table>

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
gb_info = tq.get_gb_info(stock_code = '688318.SH', date_list=['20250101', '20250601'], count=2)
print(gb_info) 
```

数据样本  
```json
[{'Date': 20250101, 'Zgb': 182942480.0, 'Ltgb': 182942480.0},
{'Date': 20250601, 'Zgb': 182942480.0, 'Ltgb': 182942480.0}] 
```

# 获取专业财务数据get\_financial\_data

根据股票，获取指定时间段内的专业财务数据，与基础财务数据不同，需要先在客户端中下载专业财务数据

```python
get_financial_data(stock_list: List[str] = [],
    field_list: List[str] = [],
    start_time: str = '',
    end_time: str = '',
    report_type: str = 'report_time') -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表例如 [ &quot;600519.SH&quot; ]</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空,字段名须与系统定义一致(如 FN193 )</td></tr><tr><td>start_time</td><td>Y</td><td>str</td><td>起始时间,格式 YYYYMMDD ,如 &#x27;20250101&#x27;</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间,格式 YYYYMMDD ,为空表示无结束限制</td></tr><tr><td>report_type</td><td>N</td><td>bool</td><td>按截止日期还是公告日期筛选,可选值:&#x27;announce_time&#x27;(按公告日期筛选)或 &#x27;tag_time&#x27;(按报告期筛选)</td></tr></table>

输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>announce_time</td><td>int</td><td></td><td>公告日期</td></tr><tr><td>tag_time</td><td>int</td><td></td><td>报告期</td></tr><tr><td>FN1</td><td>double</td><td></td><td>基本每股收益</td></tr><tr><td>FN2</td><td>double</td><td></td><td>扣除非经常性损益每股收益</td></tr><tr><td>FN3</td><td>double</td><td></td><td>每股未分配利润</td></tr><tr><td>FN4</td><td>double</td><td></td><td>每股净资产</td></tr><tr><td>FN5</td><td>double</td><td></td><td>每股资本公积金</td></tr><tr><td>FN6</td><td>double</td><td></td><td>净资产收益率</td></tr><tr><td>FN7</td><td>double</td><td></td><td>每股经营现金流量</td></tr><tr><td>FN8</td><td>double</td><td></td><td>货币资金</td></tr><tr><td>FN9</td><td>double</td><td></td><td>交易性金融资产</td></tr><tr><td>FN10</td><td>double</td><td></td><td>应收票据</td></tr><tr><td>FN11</td><td>double</td><td></td><td>应收账款</td></tr><tr><td>FN12</td><td>double</td><td></td><td>预付款项</td></tr><tr><td>FN13</td><td>double</td><td></td><td>其他应收款</td></tr><tr><td>FN14</td><td>double</td><td></td><td>应收关联公司款</td></tr><tr><td>FN15</td><td>double</td><td></td><td>应收利息</td></tr><tr><td>FN16</td><td>double</td><td></td><td>应收股利</td></tr><tr><td>FN17</td><td>double</td><td></td><td>存货</td></tr><tr><td>FN18</td><td>double</td><td></td><td>其中:消耗性生物资产</td></tr><tr><td>FN19</td><td>double</td><td></td><td>一年内到期的非流动资产</td></tr><tr><td>FN20</td><td>double</td><td></td><td>其他流动资产</td></tr><tr><td>FN21</td><td>double</td><td></td><td>流动资产合计</td></tr><tr><td>FN22</td><td>double</td><td></td><td>可供出售金融资产</td></tr><tr><td>FN23</td><td>double</td><td></td><td>持有至到期投资</td></tr><tr><td>FN24</td><td>double</td><td></td><td>长期应收款</td></tr><tr><td>FN25</td><td>double</td><td></td><td>长期股权投资</td></tr><tr><td>FN26</td><td>double</td><td></td><td>投资性房地产</td></tr><tr><td>FN27</td><td>double</td><td></td><td>固定资产</td></tr><tr><td>FN28</td><td>double</td><td></td><td>在建工程</td></tr><tr><td>FN29</td><td>double</td><td></td><td>工程物资</td></tr><tr><td>FN30</td><td>double</td><td></td><td>固定资产清理</td></tr><tr><td>FN31</td><td>double</td><td></td><td>生产性生物资产</td></tr><tr><td>FN32</td><td>double</td><td></td><td>油气资产</td></tr><tr><td>FN33</td><td>double</td><td></td><td>无形资产</td></tr><tr><td>FN34</td><td>double</td><td></td><td>开发支出</td></tr><tr><td>FN35</td><td>double</td><td></td><td>商誉</td></tr><tr><td>FN36</td><td>double</td><td></td><td>长期待摊费用</td></tr><tr><td>FN37</td><td>double</td><td></td><td>递延所得税资产</td></tr><tr><td>FN38</td><td>double</td><td></td><td>其他非流动资产</td></tr><tr><td>FN39</td><td>double</td><td></td><td>非流动资产合计</td></tr><tr><td>FN40</td><td>double</td><td></td><td>资产总计</td></tr><tr><td>FN41</td><td>double</td><td></td><td>短期借款</td></tr><tr><td>FN42</td><td>double</td><td></td><td>交易性金融负债</td></tr><tr><td>FN43</td><td>double</td><td></td><td>应付票据</td></tr><tr><td>FN44</td><td>double</td><td></td><td>应付账款</td></tr><tr><td>FN45</td><td>double</td><td></td><td>预收款项</td></tr><tr><td>FN46</td><td>double</td><td></td><td>应付职工薪酬</td></tr><tr><td>FN47</td><td>double</td><td></td><td>应交税费</td></tr><tr><td>FN48</td><td>double</td><td></td><td>应付利息</td></tr><tr><td>FN49</td><td>double</td><td></td><td>应付股利</td></tr><tr><td>FN50</td><td>double</td><td></td><td>其他应付款</td></tr><tr><td>FN51</td><td>double</td><td></td><td>应付关联公司款</td></tr><tr><td>FN52</td><td>double</td><td></td><td>一年内到期的非流动负债</td></tr><tr><td>FN53</td><td>double</td><td></td><td>其他流动负债</td></tr><tr><td>FN54</td><td>double</td><td></td><td>流动负债合计</td></tr><tr><td>FN55</td><td>double</td><td></td><td>长期借款</td></tr><tr><td>FN56</td><td>double</td><td></td><td>应付债券</td></tr><tr><td>FN57</td><td>double</td><td></td><td>长期应付款</td></tr><tr><td>FN58</td><td>double</td><td></td><td>专项应付款</td></tr><tr><td>FN59</td><td>double</td><td></td><td>预计负债(非流动负债)</td></tr><tr><td>FN60</td><td>double</td><td></td><td>递延所得税负债</td></tr><tr><td>FN61</td><td>double</td><td></td><td>其他非流动负债</td></tr><tr><td>FN62</td><td>double</td><td></td><td>非流动负债合计</td></tr><tr><td>FN63</td><td>double</td><td></td><td>负债合计</td></tr><tr><td>FN64</td><td>double</td><td></td><td>实收资本(或股本)</td></tr><tr><td>FN65</td><td>double</td><td></td><td>资本公积</td></tr><tr><td>FN66</td><td>double</td><td></td><td>盈余公积</td></tr><tr><td>FN67</td><td>double</td><td></td><td>减:库存股</td></tr><tr><td>FN68</td><td>double</td><td></td><td>未分配利润</td></tr><tr><td>FN69</td><td>double</td><td></td><td>少数股东权益</td></tr><tr><td>FN70</td><td>double</td><td></td><td>外币报表折算价差</td></tr><tr><td>FN71</td><td>double</td><td></td><td>非正常经营项目收益调整</td></tr><tr><td>FN72</td><td>double</td><td></td><td>所有者权益(或股东权益)合计</td></tr><tr><td>FN73</td><td>double</td><td></td><td>负债和所有者(或股东权益)合计</td></tr><tr><td>FN98</td><td>double</td><td></td><td>销售商品、提供劳务收到的现金</td></tr><tr><td>FN99</td><td>double</td><td></td><td>收到的税费返还</td></tr><tr><td>FN100</td><td>double</td><td></td><td>收到其他与经营活动有关的现金</td></tr><tr><td>FN101</td><td>double</td><td></td><td>经营活动现金流入小计</td></tr><tr><td>FN102</td><td>double</td><td></td><td>购买商品、接受劳务支付的现金</td></tr><tr><td>FN103</td><td>double</td><td></td><td>支付给职工以及为职工支付的现金</td></tr><tr><td>FN104</td><td>double</td><td></td><td>支付的各项税费</td></tr><tr><td>FN105</td><td>double</td><td></td><td>支付其他与经营活动有关的现金</td></tr><tr><td>FN106</td><td>double</td><td></td><td>经营活动现金流出小计</td></tr><tr><td>FN107</td><td>double</td><td></td><td>经营活动产生的现金流量净额</td></tr><tr><td>FN108</td><td>double</td><td></td><td>收回投资收到的现金</td></tr><tr><td>FN109</td><td>double</td><td></td><td>取得投资收益收到的现金</td></tr><tr><td>FN110</td><td>double</td><td></td><td>处置固定资产、无形资产和其他长期资产收回的现金净额</td></tr><tr><td>FN111</td><td>double</td><td></td><td>处置子公司及其他营业单位收到的现金净额</td></tr><tr><td>FN112</td><td>double</td><td></td><td>收到其他与投资活动有关的现金</td></tr><tr><td>FN113</td><td>double</td><td></td><td>投资活动现金流入小计</td></tr><tr><td>FN114</td><td>double</td><td></td><td>购建固定资产、无形资产和其他长期资产支付的现金</td></tr><tr><td>FN115</td><td>double</td><td></td><td>投资支付的现金</td></tr><tr><td>FN116</td><td>double</td><td></td><td>取得子公司及其他营业单位支付的现金净额</td></tr><tr><td>FN117</td><td>double</td><td></td><td>支付其他与投资活动有关的现金</td></tr><tr><td>FN118</td><td>double</td><td></td><td>投资活动现金流出小计</td></tr><tr><td>FN119</td><td>double</td><td></td><td>投资活动产生的现金流量净额</td></tr><tr><td>FN120</td><td>double</td><td></td><td>吸收投资收到的现金</td></tr><tr><td>FN121</td><td>double</td><td></td><td>取得借款收到的现金</td></tr><tr><td>FN122</td><td>double</td><td></td><td>收到其他与筹资活动有关的现金</td></tr><tr><td>FN123</td><td>double</td><td></td><td>筹资活动现金流入小计</td></tr><tr><td>FN124</td><td>double</td><td></td><td>偿还债务支付的现金</td></tr><tr><td>FN125</td><td>double</td><td></td><td>分配股利、利润或偿付利息支付的现金</td></tr><tr><td>FN126</td><td>double</td><td></td><td>支付其他与筹资活动有关的现金</td></tr><tr><td>FN127</td><td>double</td><td></td><td>筹资活动现金流出小计</td></tr><tr><td>FN128</td><td>double</td><td></td><td>筹资活动产生的现金流量净额</td></tr><tr><td>FN129</td><td>double</td><td></td><td>四、汇率变动对现金的影响</td></tr><tr><td>FN130</td><td>double</td><td></td><td>四(2)、其他原因对现金的影响</td></tr><tr><td>FN131</td><td>double</td><td></td><td>五、现金及现金等价物净增加额</td></tr><tr><td>FN132</td><td>double</td><td></td><td>期初现金及现金等价物余额</td></tr><tr><td>FN133</td><td>double</td><td></td><td>期末现金及现金等价物余额</td></tr><tr><td>FN134</td><td>double</td><td></td><td>净利润</td></tr><tr><td>FN135</td><td>double</td><td></td><td>加:资产减值准备</td></tr><tr><td>FN136</td><td>double</td><td></td><td>固定资产折旧、油气资产折耗、生产性生物资产折旧</td></tr><tr><td>FN137</td><td>double</td><td></td><td>无形资产摊销</td></tr><tr><td>FN138</td><td>double</td><td></td><td>长期待摊费用摊销</td></tr><tr><td>FN139</td><td>double</td><td></td><td>处置固定资产、无形资产和其他长期资产的损失</td></tr><tr><td>FN140</td><td>double</td><td></td><td>固定资产报废损失</td></tr><tr><td>FN141</td><td>double</td><td></td><td>公允价值变动损失</td></tr><tr><td>FN142</td><td>double</td><td></td><td>财务费用</td></tr><tr><td>FN143</td><td>double</td><td></td><td>投资损失</td></tr><tr><td>FN144</td><td>double</td><td></td><td>递延所得税资产减少</td></tr><tr><td>FN145</td><td>double</td><td></td><td>递延所得税负债增加</td></tr><tr><td>FN146</td><td>double</td><td></td><td>存货的减少</td></tr><tr><td>FN147</td><td>double</td><td></td><td>经营性应收项目的减少</td></tr><tr><td>FN148</td><td>double</td><td></td><td>经营性应付项目的增加</td></tr><tr><td>FN149</td><td>double</td><td></td><td>其他</td></tr><tr><td>FN150</td><td>double</td><td></td><td>经营活动产生的现金流量净额2</td></tr><tr><td>FN151</td><td>double</td><td></td><td>债务转为资本</td></tr><tr><td>FN152</td><td>double</td><td></td><td>一年内到期的可转换公司债券</td></tr><tr><td>FN153</td><td>double</td><td></td><td>融资租入固定资产</td></tr><tr><td>FN154</td><td>double</td><td></td><td>现金的期末余额</td></tr><tr><td>FN155</td><td>double</td><td></td><td>减:现金的期初余额</td></tr><tr><td>FN156</td><td>double</td><td></td><td>加:现金等价物的期末余额</td></tr><tr><td>FN157</td><td>double</td><td></td><td>减:现金等价物的期初余额</td></tr><tr><td>FN158</td><td>double</td><td></td><td>现金及现金等价物净增加额</td></tr><tr><td>FN159</td><td>double</td><td></td><td>流动比率(非金融类指标)</td></tr><tr><td>FN160</td><td>double</td><td></td><td>速动比率(非金融类指标)</td></tr><tr><td>FN161</td><td>double</td><td></td><td>现金比率(%)(非金融类指标)</td></tr><tr><td>FN162</td><td>double</td><td></td><td>利息保障倍数(非金融类指标)</td></tr><tr><td>FN163</td><td>double</td><td></td><td>非流动负债比率(%)(非金融类指标)</td></tr><tr><td>FN164</td><td>double</td><td></td><td>流动负债比率(%)(非金融类指标)</td></tr><tr><td>FN166</td><td>double</td><td></td><td>有形资产净值债务率(%)</td></tr><tr><td>FN167</td><td>double</td><td></td><td>权益乘数(%)</td></tr><tr><td>FN168</td><td>double</td><td></td><td>股东的权益/负债合计(%)</td></tr><tr><td>FN169</td><td>double</td><td></td><td>有形资产/负债合计(%)</td></tr><tr><td>FN170</td><td>double</td><td></td><td>经营活动产生的现金流量净额/负债合计(%)(非金融类指标)</td></tr><tr><td>FN171</td><td>double</td><td></td><td>EBITDA/负债合计(%)(非金融类指标)</td></tr><tr><td>FN172</td><td>double</td><td></td><td>应收帐款周转率(非金融类指标)</td></tr><tr><td>FN173</td><td>double</td><td></td><td>存货周转率(非金融类指标)</td></tr><tr><td>FN174</td><td>double</td><td></td><td>运营资金周转率(非金融类指标)</td></tr><tr><td>FN175</td><td>double</td><td></td><td>总资产周转率(非金融类指标)</td></tr><tr><td>FN176</td><td>double</td><td></td><td>固定资产周转率(非金融类指标)</td></tr><tr><td>FN177</td><td>double</td><td></td><td>应收帐款周转天数(非金融类指标)</td></tr><tr><td>FN178</td><td>double</td><td></td><td>存货周转天数(非金融类指标)</td></tr><tr><td>FN179</td><td>double</td><td></td><td>流动资产周转率(非金融类指标)</td></tr><tr><td>FN180</td><td>double</td><td></td><td>流动资产周转天数(非金融类指标)</td></tr><tr><td>FN181</td><td>double</td><td></td><td>总资产周转天数(非金融类指标)</td></tr><tr><td>FN182</td><td>double</td><td></td><td>股东权益周转率(非金融类指标)</td></tr><tr><td>FN183</td><td>double</td><td></td><td>营业收入增长率(%)</td></tr><tr><td>FN184</td><td>double</td><td></td><td>净利润增长率(%)</td></tr><tr><td>FN185</td><td>double</td><td></td><td>净资产增长率(%)</td></tr><tr><td>FN186</td><td>double</td><td></td><td>固定资产增长率(%)</td></tr><tr><td>FN187</td><td>double</td><td></td><td>总资产增长率(%)</td></tr><tr><td>FN188</td><td>double</td><td></td><td>投资收益增长率(%)</td></tr><tr><td>FN189</td><td>double</td><td></td><td>营业利润增长率(%)</td></tr><tr><td>FN190</td><td>double</td><td></td><td>扣非每股收益同比(%)</td></tr><tr><td>FN191</td><td>double</td><td></td><td>扣非净利润同比(%)</td></tr><tr><td>FN192</td><td>double</td><td></td><td>暂无</td></tr><tr><td>FN193</td><td>double</td><td></td><td>成本费用利润率(%)</td></tr><tr><td>FN194</td><td>double</td><td></td><td>营业利润率(非金融类指标)</td></tr><tr><td>FN195</td><td>double</td><td></td><td>营业税金率(非金融类指标)</td></tr><tr><td>FN196</td><td>double</td><td></td><td>营业成本率(非金融类指标)</td></tr><tr><td>FN197</td><td>double</td><td></td><td>净资产收益率</td></tr><tr><td>FN198</td><td>double</td><td></td><td>投资收益率</td></tr><tr><td>FN199</td><td>double</td><td></td><td>销售净利率(%)</td></tr><tr><td>FN200</td><td>double</td><td></td><td>总资产净利率</td></tr><tr><td>FN201</td><td>double</td><td></td><td>净利润率(非金融类指标)</td></tr><tr><td>FN202</td><td>double</td><td></td><td>销售毛利率(%)(非金融类指标)</td></tr><tr><td>FN203</td><td>double</td><td></td><td>三费比重(非金融类指标)</td></tr><tr><td>FN204</td><td>double</td><td></td><td>管理费用率(非金融类指标)</td></tr><tr><td>FN205</td><td>double</td><td></td><td>财务费用率(非金融类指标)</td></tr><tr><td>FN206</td><td>double</td><td></td><td>扣除非经常性损益后的净利润</td></tr><tr><td>FN207</td><td>double</td><td></td><td>息税前利润(EBIT)</td></tr><tr><td>FN208</td><td>double</td><td></td><td>息税折旧摊销前利润(EBITDA)</td></tr><tr><td>FN209</td><td>double</td><td></td><td>EBITDA/营业总收入(%)(非金融类指标)</td></tr><tr><td>FN210</td><td>double</td><td></td><td>资产负债率(%)</td></tr><tr><td>FN211</td><td>double</td><td></td><td>流动资产比率(非金融类指标)</td></tr><tr><td>FN212</td><td>double</td><td></td><td>货币资金比率(非金融类指标)</td></tr><tr><td>FN213</td><td>double</td><td></td><td>存货比率(非金融类指标)</td></tr><tr><td>FN214</td><td>double</td><td></td><td>固定资产比率</td></tr><tr><td>FN215</td><td>double</td><td></td><td>负债结构比(非金融类指标)</td></tr><tr><td>FN216</td><td>double</td><td></td><td>归属于母公司股东权益/全部投入资本(%)</td></tr><tr><td>FN217</td><td>double</td><td></td><td>股东的权益/带息债务(%)</td></tr><tr><td>FN218</td><td>double</td><td></td><td>有形资产/净债务(%)</td></tr><tr><td>FN219</td><td>double</td><td></td><td>每股经营性现金流(元)</td></tr><tr><td>FN220</td><td>double</td><td></td><td>营业收入现金含量(%)(非金融类指标)</td></tr><tr><td>FN221</td><td>double</td><td></td><td>经营活动产生的现金流量净额/经营活动净收益(%)</td></tr><tr><td>FN222</td><td>double</td><td></td><td>销售商品提供劳务收到的现金/营业收入(%)</td></tr><tr><td>FN223</td><td>double</td><td></td><td>经营活动产生的现金流量净额/营业收入</td></tr><tr><td>FN224</td><td>double</td><td></td><td>资本支出/折旧和摊销</td></tr><tr><td>FN225</td><td>double</td><td></td><td>每股现金流量净额(元)</td></tr><tr><td>FN226</td><td>double</td><td></td><td>经营净现金比率(短期债务)(非金融类指标)</td></tr><tr><td>FN227</td><td>double</td><td></td><td>经营净现金比率(全部债务)</td></tr><tr><td>FN228</td><td>double</td><td></td><td>经营活动现金净流量与净利润比率</td></tr><tr><td>FN229</td><td>double</td><td></td><td>全部资产现金回收率</td></tr><tr><td>FN230</td><td>double</td><td></td><td>营业收入</td></tr><tr><td>FN231</td><td>double</td><td></td><td>营业利润</td></tr><tr><td>FN232</td><td>double</td><td></td><td>归属于母公司所有者的净利润</td></tr><tr><td>FN233</td><td>double</td><td></td><td>扣除非经常性损益后的净利润</td></tr><tr><td>FN234</td><td>double</td><td></td><td>经营活动产生的现金流量净额</td></tr><tr><td>FN235</td><td>double</td><td></td><td>投资活动产生的现金流量净额</td></tr><tr><td>FN236</td><td>double</td><td></td><td>筹资活动产生的现金流量净额</td></tr><tr><td>FN237</td><td>double</td><td></td><td>现金及现金等价物净增加额</td></tr><tr><td>FN238</td><td>double</td><td></td><td>总股本</td></tr><tr><td>FN239</td><td>double</td><td></td><td>已上市流通A股</td></tr><tr><td>FN240</td><td>double</td><td></td><td>已上市流通B股</td></tr><tr><td>FN241</td><td>double</td><td></td><td>已上市流通H股</td></tr><tr><td>FN242</td><td>double</td><td></td><td>股东人数(户)</td></tr><tr><td>FN243</td><td>double</td><td></td><td>第一大股东的持股数量</td></tr><tr><td>FN244</td><td>double</td><td></td><td>十大流通股东持股数量合计(股)</td></tr><tr><td>FN245</td><td>double</td><td></td><td>十大股东持股数量合计(股)</td></tr><tr><td>FN246</td><td>double</td><td></td><td>机构总量(家)</td></tr><tr><td>FN247</td><td>double</td><td></td><td>机构持股总量(股)</td></tr><tr><td>FN248</td><td>double</td><td></td><td>QFII机构数</td></tr><tr><td>FN249</td><td>double</td><td></td><td>QFII持股量</td></tr><tr><td>FN250</td><td>double</td><td></td><td>券商机构数</td></tr><tr><td>FN251</td><td>double</td><td></td><td>券商持股量</td></tr><tr><td>FN252</td><td>double</td><td></td><td>保险机构数</td></tr><tr><td>FN253</td><td>double</td><td></td><td>保险持股量</td></tr><tr><td>FN254</td><td>double</td><td></td><td>基金机构数</td></tr><tr><td>FN255</td><td>double</td><td></td><td>基金持股量</td></tr><tr><td>FN256</td><td>double</td><td></td><td>社保机构数</td></tr><tr><td>FN257</td><td>double</td><td></td><td>社保持股量</td></tr><tr><td>FN258</td><td>double</td><td></td><td>私募机构数</td></tr><tr><td>FN259</td><td>double</td><td></td><td>私募持股量</td></tr><tr><td>FN260</td><td>double</td><td></td><td>财务公司机构数</td></tr><tr><td>FN261</td><td>double</td><td></td><td>财务公司持股量</td></tr><tr><td>FN262</td><td>double</td><td></td><td>年金机构数</td></tr><tr><td>FN263</td><td>double</td><td></td><td>年金持股量</td></tr><tr><td>FN264</td><td>double</td><td></td><td>十大流通股东持有的流通A股合计(股)[注:2019半年报之前,季度报告中,若股东持股除了流通A股、还有流通B股或流通H股,指标264取的是包含流通B股或流通H股的流通股数]</td></tr><tr><td>FN265</td><td>double</td><td></td><td>第一大流通股东持股量(股)</td></tr><tr><td>FN266</td><td>double</td><td></td><td>自由流通股(股)[注:1.自由流通股=已流通A股-持股5%以上股东的流通A股(一致行动人算一起);2.指标按报告期展示,新股在上市日的下个报告期才有数据]</td></tr><tr><td>FN267</td><td>double</td><td></td><td>受限流通A股(股)</td></tr><tr><td>FN268</td><td>double</td><td></td><td>一般风险准备(金融类)</td></tr><tr><td>FN269</td><td>double</td><td></td><td>其他综合收益(利润表)</td></tr><tr><td>FN270</td><td>double</td><td></td><td>综合收益总额(利润表)</td></tr><tr><td>FN271</td><td>double</td><td></td><td>归属于母公司股东权益(资产负债表)</td></tr><tr><td>FN272</td><td>double</td><td></td><td>银行机构数(家)(机构持股)</td></tr><tr><td>FN273</td><td>double</td><td></td><td>银行持股量(股)(机构持股)</td></tr><tr><td>FN274</td><td>double</td><td></td><td>一般法人机构数(家)(机构持股)</td></tr><tr><td>FN275</td><td>double</td><td></td><td>一般法人持股量(股)(机构持股)</td></tr><tr><td>FN276</td><td>double</td><td></td><td>近一年净利润(元)</td></tr><tr><td>FN277</td><td>double</td><td></td><td>信托机构数(家)(机构持股)</td></tr><tr><td>FN278</td><td>double</td><td></td><td>信托持股量(股)(机构持股)</td></tr><tr><td>FN279</td><td>double</td><td></td><td>特殊法人机构数(家)(机构持股)</td></tr><tr><td>FN280</td><td>double</td><td></td><td>特殊法人持股量(股)(机构持股)</td></tr><tr><td>FN281</td><td>double</td><td></td><td>加权净资产收益率(每股指标)</td></tr><tr><td>FN282</td><td>double</td><td></td><td>扣非每股收益(单季度财务指标)</td></tr><tr><td>FN283</td><td>double</td><td></td><td>最近一年营业收入(万元)</td></tr><tr><td>FN284</td><td>double</td><td></td><td>国家队持股数量(万股)[注:本指标统计包含汇金公司、证金公司、外汇管理局旗下投资平台、国家队基金、国开、养老金以及中科汇通等国家队机构持股数量]</td></tr><tr><td>FN285</td><td>double</td><td></td><td>业绩预告-本期归母净利润同比增幅下限%[注:指标285至294展示未来一个报告期的数据。例,3月31日至6月29日这段时间内展示的是中报的数据;如果最新的财务报告后面有多个报告期的业绩预告/快报,只能展示最新的财务报告后面的一个报告期的业绩预告/快报]</td></tr><tr><td>FN286</td><td>double</td><td></td><td>业绩预告-本期归母净利润同比增幅上限%</td></tr><tr><td>FN287</td><td>double</td><td></td><td>业绩快报-归母净利润</td></tr><tr><td>FN288</td><td>double</td><td></td><td>业绩快报-扣非净利润</td></tr><tr><td>FN289</td><td>double</td><td></td><td>业绩快报-总资产</td></tr><tr><td>FN290</td><td>double</td><td></td><td>业绩快报-净资产</td></tr><tr><td>FN291</td><td>double</td><td></td><td>业绩快报-每股收益</td></tr><tr><td>FN292</td><td>double</td><td></td><td>业绩快报-摊薄净资产收益率</td></tr><tr><td>FN293</td><td>double</td><td></td><td>业绩快报-加权净资产收益率</td></tr><tr><td>FN294</td><td>double</td><td></td><td>业绩快报-每股净资产</td></tr><tr><td>FN295</td><td>double</td><td></td><td>应付票据及应付账款(资产负债表)</td></tr><tr><td>FN296</td><td>double</td><td></td><td>应收票据及应收账款(资产负债表)</td></tr><tr><td>FN297</td><td>double</td><td></td><td>递延收益(资产负债表-非流动负债)</td></tr><tr><td>FN298</td><td>double</td><td></td><td>其他综合收益(资产负债表)</td></tr><tr><td>FN299</td><td>double</td><td></td><td>其他权益工具(资产负债表)</td></tr><tr><td>FN300</td><td>double</td><td></td><td>其他收益(利润表)</td></tr><tr><td>FN301</td><td>double</td><td></td><td>资产处置收益(利润表)</td></tr><tr><td>FN302</td><td>double</td><td></td><td>持续经营净利润(利润表)</td></tr><tr><td>FN303</td><td>double</td><td></td><td>终止经营净利润(利润表)</td></tr><tr><td>FN304</td><td>double</td><td></td><td>研发费用(利润表)</td></tr><tr><td>FN305</td><td>double</td><td></td><td>其中:利息费用(利润表-财务费用)</td></tr><tr><td>FN306</td><td>double</td><td></td><td>其中:利息收入(利润表-财务费用)</td></tr><tr><td>FN307</td><td>double</td><td></td><td>近一年经营活动现金流净额</td></tr><tr><td>FN308</td><td>double</td><td></td><td>近一年归母净利润(万元)</td></tr><tr><td>FN309</td><td>double</td><td></td><td>近一年扣非净利润(万元)</td></tr><tr><td>FN310</td><td>double</td><td></td><td>近一年现金净流量(万元)</td></tr><tr><td>FN311</td><td>double</td><td></td><td>基本每股收益(单季度)</td></tr><tr><td>FN312</td><td>double</td><td></td><td>营业总收入(单季度)(万元)</td></tr><tr><td>FN313</td><td>double</td><td></td><td>业绩预告公告日期[注:本指标展示未来一个报告期的数据。例,3月31日至6月29日这段时间内展示的是中报的数据;如果最新的财务报告后面有多个报告期的业绩预告/快报,只能展示最新的财务报告后面的一个报告期的业绩预告/快报的数据;公告日期格式为YYMMDD,例:190101代表2019年1月1日]</td></tr><tr><td>FN314</td><td>double</td><td></td><td>财报公告日期[注:日期格式为YYMMDD,例:190101代表2019年1月1日]</td></tr><tr><td>FN315</td><td>double</td><td></td><td>业绩快报公告日期[注:本指标展示未来一个报告期的数据。例,3月31日至6月29日这段时间内展示的是中报的数据;如果最新的财务报告后面有多个报告期的业绩预告/快报,只能展示最新的财务报告后面的一个报告期的业绩预告/快报的数据;公告日期格式为YYMMDD,例:190101代表2019年1月1日]</td></tr><tr><td>FN316</td><td>double</td><td></td><td>近一年投资活动现金流净额(万元)</td></tr><tr><td>FN317</td><td>double</td><td></td><td>业绩预告-本期归母净利润下限(万元)[注:指标317至318展示未来一个报告期的数据。例,3月31日至6月29日这段时间内展示的是中报的数据;如果最新的财务报告后面有多个报告期的业绩预告/快报,只能展示最新的财务报告后面的一个报告期的业绩预告/快报]</td></tr><tr><td>FN318</td><td>double</td><td></td><td>业绩预告-本期归母净利润上限(万元)</td></tr><tr><td>FN319</td><td>double</td><td></td><td>营业总收入TTM(万元)</td></tr><tr><td>FN320</td><td>double</td><td></td><td>员工总数(人)</td></tr><tr><td>FN321</td><td>double</td><td></td><td>每股企业自由现金流</td></tr><tr><td>FN322</td><td>double</td><td></td><td>每股股东自由现金流</td></tr><tr><td>FN323</td><td>double</td><td></td><td>近一年营业利润(万元)</td></tr><tr><td>FN324</td><td>double</td><td></td><td>净利润(单季度)(万元)</td></tr><tr><td>FN325</td><td>double</td><td></td><td>北上资金数(家)(机构持股)</td></tr><tr><td>FN326</td><td>double</td><td></td><td>北上资金持股量(股)(机构持股)</td></tr><tr><td>FN327</td><td>double</td><td></td><td>有息负债率</td></tr><tr><td>FN328</td><td>double</td><td></td><td>营业成本(单季度)(万元)</td></tr><tr><td>FN329</td><td>double</td><td></td><td>投入资本回报率(ROIC)(获利能力分析)</td></tr><tr><td>FN330</td><td>double</td><td></td><td>业绩快报-营业收入(本期)</td></tr><tr><td>FN331</td><td>double</td><td></td><td>业绩快报-营业收入(上期)</td></tr><tr><td>FN332</td><td>double</td><td></td><td>业绩快报-营业利润(本期)</td></tr><tr><td>FN333</td><td>double</td><td></td><td>业绩快报-营业利润(上期)</td></tr><tr><td>FN334</td><td>double</td><td></td><td>业绩快报-利润总额(本期)</td></tr><tr><td>FN335</td><td>double</td><td></td><td>业绩快报-利润总额(上期)</td></tr><tr><td>FN336</td><td>double</td><td></td><td>审计意见[注:0-未审计,1-无保留意见,2-带强调事项段的无保留意见,3-保留意见,4-无法表示意见,5-否定意见及其他]</td></tr><tr><td>FN337</td><td>double</td><td></td><td>股利支付率(%)</td></tr><tr><td>FN338</td><td>double</td><td></td><td>近一年营业成本-非金融类(万元)</td></tr><tr><td>FN339</td><td>double</td><td></td><td>近一年营业成本-金融类(万元)</td></tr><tr><td>FN340</td><td>double</td><td></td><td>业绩预告-本期扣非后净利润下限(万元)</td></tr><tr><td>FN341</td><td>double</td><td></td><td>业绩预告-本期扣非后净利润上限(万元)</td></tr><tr><td>FN342</td><td>double</td><td></td><td>业绩预告-本期扣非后净利润同比增长下限(%)</td></tr><tr><td>FN343</td><td>double</td><td></td><td>业绩预告-本期扣非后净利润同比增长上限(%)</td></tr><tr><td>FN344</td><td>double</td><td></td><td>业绩预告-预告基本每股收益下限(元)</td></tr><tr><td>FN345</td><td>double</td><td></td><td>业绩预告-预告基本每股收益上限(元)</td></tr><tr><td>FN346</td><td>double</td><td></td><td>业绩预告-预告基本每股收益同比增长下限(%)</td></tr><tr><td>FN347</td><td>double</td><td></td><td>业绩预告-预告基本每股收益同比增长上限(%)</td></tr><tr><td>FN348</td><td>double</td><td></td><td>业绩预告-预告扣非后基本每股收益下限(元)</td></tr><tr><td>FN349</td><td>double</td><td></td><td>业绩预告-预告扣非后基本每股收益上限(元)</td></tr><tr><td>FN350</td><td>double</td><td></td><td>业绩预告-预告扣非后基本每股收益同比增长下限(%)</td></tr><tr><td>FN351</td><td>double</td><td></td><td>业绩预告-预告扣非后基本每股收益同比增长上限(%)</td></tr><tr><td>FN352</td><td>double</td><td></td><td>业绩预告-预告营业收入下限(万元)</td></tr><tr><td>FN353</td><td>double</td><td></td><td>业绩预告-预告营业收入上限(万元)</td></tr><tr><td>FN354</td><td>double</td><td></td><td>业绩预告-预告营业收入同比增长下限(%)</td></tr><tr><td>FN355</td><td>double</td><td></td><td>业绩预告-预告营业收入同比增长上限(%)</td></tr><tr><td>FN356</td><td>double</td><td></td><td>业绩预告-预告扣除后营业收入下限(万元)</td></tr><tr><td>FN357</td><td>double</td><td></td><td>业绩预告-预告扣除后营业收入上限(万元)</td></tr><tr><td>FN358</td><td>double</td><td></td><td>主营业务收入(内销)(万元)</td></tr><tr><td>FN359</td><td>double</td><td></td><td>主营业务收入(外销)(万元)</td></tr><tr><td>FN360</td><td>double</td><td></td><td>资管计划机构数(家)</td></tr><tr><td>FN361</td><td>double</td><td></td><td>资管计划持股量(股)</td></tr><tr><td>FN362</td><td>double</td><td></td><td>财务总评分</td></tr><tr><td>FN401</td><td>double</td><td></td><td>专项储备(万元)</td></tr><tr><td>FN402</td><td>double</td><td></td><td>结算备付金(万元)</td></tr><tr><td>FN403</td><td>double</td><td></td><td>拆出资金(万元)</td></tr><tr><td>FN404</td><td>double</td><td></td><td>发放贷款及垫款(万元)(流动资产科目)</td></tr><tr><td>FN405</td><td>double</td><td></td><td>衍生金融资产(万元)</td></tr><tr><td>FN406</td><td>double</td><td></td><td>应收保费(万元)</td></tr><tr><td>FN407</td><td>double</td><td></td><td>应收分保账款(万元)</td></tr><tr><td>FN408</td><td>double</td><td></td><td>应收分保合同准备金(万元)</td></tr><tr><td>FN409</td><td>double</td><td></td><td>买入返售金融资产(万元)</td></tr><tr><td>FN410</td><td>double</td><td></td><td>划分为持有待售的资产(万元)</td></tr><tr><td>FN411</td><td>double</td><td></td><td>发放贷款及垫款(万元)(非流动资产科目)</td></tr><tr><td>FN412</td><td>double</td><td></td><td>向中央银行借款(万元)</td></tr><tr><td>FN413</td><td>double</td><td></td><td>吸收存款及同业存放(万元)</td></tr><tr><td>FN414</td><td>double</td><td></td><td>拆入资金(万元)</td></tr><tr><td>FN415</td><td>double</td><td></td><td>衍生金融负债(万元)</td></tr><tr><td>FN416</td><td>double</td><td></td><td>卖出回购金融资产款(万元)</td></tr><tr><td>FN417</td><td>double</td><td></td><td>应付手续费及佣金(万元)</td></tr><tr><td>FN418</td><td>double</td><td></td><td>应付分保账款(万元)</td></tr><tr><td>FN419</td><td>double</td><td></td><td>保险合同准备金(万元)</td></tr><tr><td>FN420</td><td>double</td><td></td><td>代理买卖证券款(万元)</td></tr><tr><td>FN421</td><td>double</td><td></td><td>代理承销证券款(万元)</td></tr><tr><td>FN422</td><td>double</td><td></td><td>划分为持有待售的负债(万元)</td></tr><tr><td>FN423</td><td>double</td><td></td><td>预计负债(万元)(流动负债)</td></tr><tr><td>FN424</td><td>double</td><td></td><td>递延收益(万元)(流动负债科目,公告此科目的股票较少,大部分公司没有此数据)</td></tr><tr><td>FN425</td><td>double</td><td></td><td>其中:优先股(万元)(非流动负债科目)</td></tr><tr><td>FN426</td><td>double</td><td></td><td>永续债(万元)(非流动负债科目)</td></tr><tr><td>FN427</td><td>double</td><td></td><td>长期应付职工薪酬(万元)</td></tr><tr><td>FN428</td><td>double</td><td></td><td>其中:优先股(万元)(所有者权益科目)</td></tr><tr><td>FN429</td><td>double</td><td></td><td>永续债(万元)(所有者权益科目)</td></tr><tr><td>FN430</td><td>double</td><td></td><td>债权投资(万元)</td></tr><tr><td>FN431</td><td>double</td><td></td><td>其他债权投资(万元)</td></tr><tr><td>FN432</td><td>double</td><td></td><td>其他权益工具投资(万元)</td></tr><tr><td>FN433</td><td>double</td><td></td><td>其他非流动金融资产(万元)</td></tr><tr><td>FN434</td><td>double</td><td></td><td>合同负债(万元)</td></tr><tr><td>FN435</td><td>double</td><td></td><td>合同资产(万元)</td></tr><tr><td>FN436</td><td>double</td><td></td><td>其他资产(万元)</td></tr><tr><td>FN437</td><td>double</td><td></td><td>应收款项融资(万元)</td></tr><tr><td>FN438</td><td>double</td><td></td><td>使用权资产(万元)</td></tr><tr><td>FN439</td><td>double</td><td></td><td>租赁负债(万元)</td></tr><tr><td>FN440</td><td>double</td><td></td><td>发放贷款及垫款(万元)[注:金融类科目]</td></tr><tr><td>FN441</td><td>double</td><td></td><td>应收款项(万元)[注:证券类指标]</td></tr><tr><td>FN442</td><td>double</td><td></td><td>存出保证金(万元)[注:证券类指标]</td></tr><tr><td>FN443</td><td>double</td><td></td><td>现金及存放中央银行款项(万元)[注:金融类科目]</td></tr><tr><td>FN444</td><td>double</td><td></td><td>贵金属(万元)[注:金融类科目]</td></tr><tr><td>FN445</td><td>double</td><td></td><td>以公允价值计量且其变动计入当期损益的金融资产(万元)[注:金融类科目]</td></tr><tr><td>FN446</td><td>double</td><td></td><td>代理业务资产(万元)[注:金融类科目]</td></tr><tr><td>FN447</td><td>double</td><td></td><td>应收款项类投资(万元)[注:金融类科目]</td></tr><tr><td>FN448</td><td>double</td><td></td><td>同业及其它金融机构存放款项(万元)[注:金融类科目]</td></tr><tr><td>FN449</td><td>double</td><td></td><td>以公允价值计量且其变动计入当期损益的金融负债(万元)[注:金融类科目]</td></tr><tr><td>FN450</td><td>double</td><td></td><td>吸收存款(万元)[注:金融类科目]</td></tr><tr><td>FN451</td><td>double</td><td></td><td>代理业务负债(万元)[注:金融类科目]</td></tr><tr><td>FN452</td><td>double</td><td></td><td>其他负债(万元)[注:金融类科目]</td></tr><tr><td>FN453</td><td>double</td><td></td><td>发放贷款及垫款(万元)[注:金融类科目]</td></tr><tr><td>FN501</td><td>double</td><td></td><td>稀释每股收益(元)</td></tr><tr><td>FN502</td><td>double</td><td></td><td>营业总收入(万元)</td></tr><tr><td>FN503</td><td>double</td><td></td><td>汇兑收益(万元)</td></tr><tr><td>FN504</td><td>double</td><td></td><td>其中:归属于母公司综合收益(万元)</td></tr><tr><td>FN505</td><td>double</td><td></td><td>其中:归属于少数股东综合收益(万元)</td></tr><tr><td>FN506</td><td>double</td><td></td><td>利息收入(万元)</td></tr><tr><td>FN507</td><td>double</td><td></td><td>已赚保费(万元)</td></tr><tr><td>FN508</td><td>double</td><td></td><td>手续费及佣金收入(万元)</td></tr><tr><td>FN509</td><td>double</td><td></td><td>利息支出(万元)</td></tr><tr><td>FN510</td><td>double</td><td></td><td>手续费及佣金支出(万元)</td></tr><tr><td>FN511</td><td>double</td><td></td><td>退保金(万元)</td></tr><tr><td>FN512</td><td>double</td><td></td><td>赔付支出净额(万元)</td></tr><tr><td>FN513</td><td>double</td><td></td><td>提取保险合同准备金净额(万元)</td></tr><tr><td>FN514</td><td>double</td><td></td><td>保单红利支出(万元)</td></tr><tr><td>FN515</td><td>double</td><td></td><td>分保费用(万元)</td></tr><tr><td>FN516</td><td>double</td><td></td><td>其中:非流动资产处置利得(万元)</td></tr><tr><td>FN517</td><td>double</td><td></td><td>信用减值损失(万元)</td></tr><tr><td>FN518</td><td>double</td><td></td><td>净敞口套期收益(万元)</td></tr><tr><td>FN519</td><td>double</td><td></td><td>营业总成本(万元)</td></tr><tr><td>FN520</td><td>double</td><td></td><td>信用减值损失(万元、2019格式)</td></tr><tr><td>FN521</td><td>double</td><td></td><td>资产减值损失(万元、2019格式)</td></tr><tr><td>FN522</td><td>double</td><td></td><td>其他业务收入(万元) [注:金融类科目]</td></tr><tr><td>FN523</td><td>double</td><td></td><td>业务及管理费(万元) [注:金融类科目]</td></tr><tr><td>FN524</td><td>double</td><td></td><td>其他业务成本(万元) [注:金融类科目]</td></tr><tr><td>FN561</td><td>double</td><td></td><td>加:其他原因对现金的影响2(万元)(现金的期末余额科目)</td></tr><tr><td>FN562</td><td>double</td><td></td><td>客户存款和同业存放款项净增加额(万元)</td></tr><tr><td>FN563</td><td>double</td><td></td><td>向中央银行借款净增加额(万元)</td></tr><tr><td>FN564</td><td>double</td><td></td><td>向其他金融机构拆入资金净增加额(万元)</td></tr><tr><td>FN565</td><td>double</td><td></td><td>收到原保险合同保费取得的现金(万元)</td></tr><tr><td>FN566</td><td>double</td><td></td><td>收到再保险业务现金净额(万元)</td></tr><tr><td>FN567</td><td>double</td><td></td><td>保户储金及投资款净增加额(万元)</td></tr><tr><td>FN568</td><td>double</td><td></td><td>处置以公允价值计量且其变动计入当期损益的金融资产净增加额(万元)</td></tr><tr><td>FN569</td><td>double</td><td></td><td>收取利息、手续费及佣金的现金(万元)</td></tr><tr><td>FN570</td><td>double</td><td></td><td>拆入资金净增加额(万元)</td></tr><tr><td>FN571</td><td>double</td><td></td><td>回购业务资金净增加额(万元)</td></tr><tr><td>FN572</td><td>double</td><td></td><td>客户贷款及垫款净增加额(万元)</td></tr><tr><td>FN573</td><td>double</td><td></td><td>存放中央银行相同业款项净增加额(万元)</td></tr><tr><td>FN574</td><td>double</td><td></td><td>支付原保险合同赔付款项的现金(万元)</td></tr><tr><td>FN575</td><td>double</td><td></td><td>支付利息、手续费及佣金的现金(万元)</td></tr><tr><td>FN576</td><td>double</td><td></td><td>支付保单红利的现金(万元)</td></tr><tr><td>FN577</td><td>double</td><td></td><td>其中:子公司吸收少数股东投资收到的现金(万元)</td></tr><tr><td>FN578</td><td>double</td><td></td><td>其中:子公司支付给少数股东的股利、利润(万元)</td></tr><tr><td>FN579</td><td>double</td><td></td><td>投资性房地产的折旧及摊销(万元)</td></tr><tr><td>FN580</td><td>double</td><td></td><td>信用减值损失(万元)</td></tr><tr><td>FN581</td><td>double</td><td></td><td>使用权资产折旧(万元)</td></tr><tr><td>FN582</td><td>double</td><td></td><td>收取利息和手续费净增加额(万元)[注:金融类科目]</td></tr><tr><td>FN583</td><td>double</td><td></td><td>支付手续费的现金(万元)[注:金融类科目]</td></tr><tr><td>FN584</td><td>double</td><td></td><td>发行债券支付的现金(万元)[注:金融类科目]</td></tr></table>

# 返回值说明

返回类型： dict ，键为股票代码（如 '600519.SH' ），值为 pandas.DataFrame。  
DataFrame 列：

用户请求的财务字段（如 FN193 , FN194 … 大写）。

announce\_time ：公告日期，格式 YYYYMMDD。  
tag\_time ：报告期截止日期，格式 YYYYMMDD

行：按时间顺序排列的财务数据记录。

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
    fd = tq.get_financial_data(
    stock_list=['688318.SH'],
    field_list=['Fn193','Fn194','Fn195','Fn196','Fn197'],
    start_time='20250101',
    end_time='',
    report_type='announce_time')
print(fd) 
```

数据样本  
```txt
1 {'600519.SH': FN193 FN194 FN195 FN196 FN197 announce_time tag_time
2 0 164.82 70.03 15.76 8.07 36.99 20250403 20241231
3 1 193.43 73.19 14.16 8.03 10.39 20250430 20250331
4 2 166.69 70.22 15.60 8.70 19.02 20250813 20250630
5 3 162.47 69.67 16.07 8.71 25.14 20251030 20250930} 
```

← 获取每天的股本数据get\_gb\_info

获取指定日期财务数据get\_financial\_data\_by\_date →

# 获取指定日期专业财务数据get\_financial\_data\_by\_date

根据股票，获取指定日期的专业财务数据，与基础财务数据不同，需要先在客户端中下载专业财务数据

```python
get_financial_data_by_date(stock_list: List[str] = [],
    field_list: List[str] = [],
    year: int = 0,
    mmdd: int = 0) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空(如 FN193 )</td></tr><tr><td>year</td><td>Y</td><td>int</td><td>指定年份</td></tr><tr><td>mmdd</td><td>Y</td><td>int</td><td>指定月日</td></tr></table>

如果year和mmdd都为0,表示最新的财报;  
如果year为0,mmdd为小于300的数字,表示最近一期向前推mmdd期的数据,如果是331,630,930,1231这些,表示最近一期的对应季报的数据;  
如果mmdd为0,year为一数字,表示最近一期向前推year年的同期数据;  
季报分界点为:0331,0630,0930,1231   
需要先在客户端中下载财务数据包

# 输出数据

同get\_financial\_data一样。

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
    fd = tq.get_financial_data_by_date(
    stock_list=['688318.SH'],
    field_list=['Fn193', 'Fn194', 'Fn195', 'Fn196', 'Fn197'],
    year=0,
    mmdd=0)
print(fd) 
```

数据样本  
```txt
{'600519.SH':  
{'FN193': '162.47',  
'FN194': '69.67',  
'FN195': '16.07', 
```

← 获取专业财务数据get\_financial\_data

获取股票交易数据get\_gpjy\_value →

# 获取股票交易数据get\_gpjy\_value

根据股票，获取指定时间段内的股票交易数据，需要先在客户端中下载股票数据包

```python
get_gpjy_value(stock_list: List[str] = [], field_list: List[str] = [], start_time: str = '', end_time: str = '') -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间</td></tr></table>

输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>GP01</td><td>double</td><td></td><td>股东人数 股东户数(户)</td></tr><tr><td>GP02</td><td>double</td><td></td><td>龙虎榜 买入总计(万元) 卖出总计(万元)[注:该指标展示20230717日之后的数据]</td></tr><tr><td>GP03</td><td>double</td><td></td><td>融资融券1 融资余额(万元) 融券余量(股)</td></tr><tr><td>GP04</td><td>double</td><td></td><td>大宗交易 成交均价(元) 成交额(万元)</td></tr><tr><td>GP05</td><td>double</td><td></td><td>增减持1 成交均价(元) 变动股数(股)</td></tr><tr><td>GP06</td><td>double</td><td></td><td>陆股通持股量 持股数量(股)[注:该指标展示20170317日之后的数据]</td></tr><tr><td>GP07</td><td>double</td><td></td><td>陆股通市场成交净额 陆股通市场净买入(万元)[注:官方只公布了每日的前十名数据]</td></tr><tr><td>GP08</td><td>double</td><td></td><td>龙虎榜机构(卖方)数据 卖方机构个数 机构卖出金额(万元)</td></tr><tr><td>GP09</td><td>double</td><td></td><td>龙虎榜机构(买方)数据 买方机构个数 机构买入金额(万元)</td></tr><tr><td>GP10</td><td>double</td><td></td><td>近3月机构调研情况 近3月机构调研次数 近3月调研机构数量</td></tr><tr><td>GP11</td><td>double</td><td></td><td>融资融券2 融资买入额(万元) 融资偿还额(万元)</td></tr><tr><td>GP12</td><td>double</td><td></td><td>融资融券3 融券卖出量(股) 融券偿还量(股)</td></tr><tr><td>GP13</td><td>double</td><td></td><td>融资融券4 融资净买入(万元) 融券净卖出(股)</td></tr><tr><td>GP14</td><td>double</td><td></td><td>涨停数据 涨停金额(即板上成交,万元) 开板次数[注:该指标展示20180319日之后的数据]</td></tr><tr><td>GP15</td><td>double</td><td></td><td>涨跌停 涨跌停状态 封单金额(万元)[注:涨停取2,曾涨停取1,跌停取-2,曾跌停取-1;跌停和曾跌停时,封单金额取负值 该指标展示20160926日之后的数据]</td></tr><tr><td>GP16</td><td>double</td><td></td><td>总市值 总市值(万元)</td></tr><tr><td>GP17</td><td>double</td><td></td><td>龙虎榜营业部数据 买入金额(万元) 卖出金额(万元)</td></tr><tr><td>GP18</td><td>double</td><td></td><td>龙虎榜沪深股通数据 买入金额(万元) 卖出金额(万元)</td></tr><tr><td>GP19</td><td>double</td><td></td><td>每周股票质押数量 无限售股份质押数(万) 有限售股份质押数(万)[注:该指标展示20180316日之后的数据]</td></tr><tr><td>GP20</td><td>double</td><td></td><td>每周股票质押比例 质押比例(%)[注:该指标展示20180316日之后的数据]</td></tr><tr><td>GP21</td><td>double</td><td></td><td>股息率 股息率(%)</td></tr><tr><td>GP22</td><td>double</td><td></td><td>涨跌停 封成比 封流比[注:该指标展示20180319日之后的数据]</td></tr><tr><td>GP23</td><td>double</td><td></td><td>拟增减持 拟增持数量(万股) 拟减持数量(万股)</td></tr><tr><td>GP24</td><td>double</td><td></td><td>涨停 首次涨停时间 涨停最大封单额(万) [注:首次涨停时间展示20160301之后的数据,涨停最大封单额展示20200730之后的数据]</td></tr><tr><td>GP25</td><td>double</td><td></td><td>盘前盘后成交量 开盘成交量(手) 盘后固定成交量(手) [注:盘后固定成交量只包含科创板和创业板]</td></tr><tr><td>GP26</td><td>double</td><td></td><td>拟增减持金额 拟增持金额(万元) 拟减持金额(万元)</td></tr><tr><td>GP27</td><td>double</td><td></td><td>人气排名 市场人气排名 行业人气排名 [注:行业排名为通达信二级研究行业排名]</td></tr><tr><td>GP28</td><td>double</td><td></td><td>股票回购 回购均价(元) 回购数量(万股)</td></tr><tr><td>GP29</td><td>double</td><td></td><td>证券信息 是否复牌日 是否更名日 [注:是否复牌日说明:0-不是复牌日,n(n&gt;0)-停牌n个交易日之后的复牌日;是否更名日说明:0-未更名,1-常规更名,2-加ST,3-加*ST,4-摘帽,5-其他]</td></tr><tr><td>GP30</td><td>double</td><td></td><td>分红送转 派息金额(万元) 送转数量(股) [注:对应展示日期为除权除息日]</td></tr><tr><td>GP31</td><td>double</td><td></td><td>转融券 期初余量(股) 期末余量(股)</td></tr><tr><td>GP32</td><td>double</td><td></td><td>转融券 融出数量(股) 融出市值(元)</td></tr><tr><td>GP33</td><td>double</td><td></td><td>跌停数据 跌停金额(万元) 开板次数 [注:该指标展示20180319日之后的数据,暂无跌停金额数据]</td></tr><tr><td>GP34</td><td>double</td><td></td><td>跌停 首次跌停时间 跌停最大封单额(万) [注:首次跌停时间展示20160301之后的数据,跌停最大封单额展示20200730之后的数据]</td></tr><tr><td>GP35</td><td>double</td><td></td><td>增减持2 增持数量(股) 减持数量(股)</td></tr><tr><td>GP36</td><td>double</td><td></td><td>竞价涨停买 买入金额(万元) [注:该指标展示20241101日之后的数据]</td></tr><tr><td>GP37</td><td>double</td><td></td><td>龙虎榜2 上榜类型连续交易日(天) [注:该指标展示上榜类型中指代的连续交易日类型]</td></tr><tr><td>GP38</td><td>double</td><td></td><td>涨停相关1 近1年涨停次数 近1年溢价5%次数</td></tr><tr><td>GP39</td><td>double</td><td></td><td>涨停相关2 近1年首板封板率(%) 近1年次日红盘率(%)</td></tr><tr><td>GP40</td><td>double</td><td></td><td>涨停相关3 近1年连板率(%) 最后涨停时间</td></tr><tr><td>GP41</td><td>double</td><td></td><td>股权登记日 配股股权登记日</td></tr><tr><td>GP42</td><td>double</td><td></td><td>龙虎榜专业机构买卖净额 买方成交净额(万元) 卖方成交净额(万元)</td></tr><tr><td>GP43</td><td>double</td><td></td><td>配股实施 配股价格(元) 配股数量(万股)</td></tr><tr><td>GP44</td><td>double</td><td></td><td>股票评分 综合评分</td></tr><tr><td>GP45</td><td>double</td><td></td><td>评级系数 评级系数</td></tr></table>

GP46

double

拟询价转让 拟转让股数(万股) 拟转让占总股本(%)

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
gp_val = tq.get_gpjy_value(
    stock_list=['688318.SH'],
    field_list=['GP1', 'GP2', 'GP3', 'GP4', 'GP5'],
    start_time='20250101',
    end_time='20250102')
print(gp_val) 
```

数据样本  
```json
1 {'688318.SH': {'GP3': [{ 'Date': '20250102', 'Value': ['141405.89', '11113.00']}]} 
```

← 获取指定日期财务数据get\_financial\_data\_by\_date

获取指定日期股票交易数据get\_gpjy\_value\_by\_date →

# 获取指定日期股票交易数据get\_gpjy\_value\_by\_date

根据股票，获取指定时间段内的股票交易数据，需要先在客户端中下载股票数据包

```python
def get_gpjy_value_by_date(stock_list: List[str] = [],
    field_list: List[str] = [],
    year: int = 0,
    mmdd: int = 0) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>year</td><td>Y</td><td>int</td><td>指定年份</td></tr><tr><td>mmdd</td><td>Y</td><td>int</td><td>指定月日</td></tr></table>

如果year为0,mmdd为0,表示最新数据,mmdd为1,2,3...,表示倒数第2,3,4...个数据。  
需要先在客户端中下载股票数据包

# 输出数据

同get\_gpjy\_value一样。

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
gp_one = tq.get_gpjy_value_by_date(
    stock_list=['688318.SH'],
    field_list=['GP1', 'GP2', 'GP3', 'GP4', 'GP5'],
    year=0, mmdd=0)
print(gp_one) 
```

数据样本  
```txt
1 {'688318.SH': {'GP1': ['24154.00', '0.00'], 'GP2': ['20574.12', '18728.85'], 'GP3': ['140464.83', '55043.00'], 'GP4': ['169.80', '5943.00'], 'GP5': ['103.00', '-7000.00']}} 
```

# 获取板块交易数据get\_bkjy\_value

根据板块代码，获取指定时间段内的板块交易数据，需要先在客户端中下载股票数据包

```python
get_bkjy_value(stock_list: List[str] = [],
    field_list: List[str] = [],
    start_time: str = '',
    end_time: str = '') -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间</td></tr></table>

输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>BK5</td><td>double</td><td></td><td>市盈率TTM 整体法 算术平均</td></tr><tr><td>BK6</td><td>double</td><td></td><td>市净率MRQ 整体法 算术平均</td></tr><tr><td>BK7</td><td>double</td><td></td><td>市销率TTM 整体法 算术平均</td></tr><tr><td>BK8</td><td>double</td><td></td><td>市现率TTM 整体法 算术平均</td></tr><tr><td>BK9</td><td>double</td><td></td><td>涨跌数 上涨家数 下跌家数</td></tr><tr><td>BK10</td><td>double</td><td></td><td>板块总市值(亿元) 整体法 算术平均</td></tr><tr><td>BK11</td><td>double</td><td></td><td>板块流通市值(亿元) 整体法 算术平均</td></tr><tr><td>BK12</td><td>double</td><td></td><td>涨停数 涨停家数 曾涨停家数[注:该指标展示20160926日之后的数据]</td></tr><tr><td>BK13</td><td>double</td><td></td><td>跌停数 跌停家数 曾跌停家数[注:该指标展示20160926日之后的数据]</td></tr><tr><td>BK14</td><td>double</td><td></td><td>涨停数据 市场高度(不含ST股和未开板新股) 2板及以上涨停个数(不含ST股和未开板新股)[注:该指标展示20180319日之后的数据]</td></tr><tr><td>BK15</td><td>double</td><td></td><td>融资融券 沪深京融资余额(万元) 沪深京融券余额(万元)</td></tr><tr><td>BK16</td><td>double</td><td></td><td>陆股通资金流入 沪股通流入金额(亿元) 深股通流入金额(亿元) [注:该指标展示20170320日之后的数据]</td></tr><tr><td>BK17</td><td>double</td><td></td><td>开盘成交数 开盘成交额(万元) 开盘成交量(万股)</td></tr><tr><td>BK18</td><td>double</td><td></td><td>板块股息率(%) 算数平均 整体法</td></tr><tr><td>BK19</td><td>double</td><td></td><td>板块自由流通市值(亿元) 整体法 算术平均</td></tr></table>

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
    bk_data = tq.get_bkjy_value(stock_list=['880660.SH'),
    field_list=['BK5', 'BK6', 'BK7', 'BK8', 'BK9'],
    start_time='20250101',
    end_time='20250102')
print(bk_data) 
```

数据样本  
```txt
{'880660.SH': {'BK5': [{ 'Date': '20250102', 'Value': ['55.28', '55.50']}], 'BK6': [{ 'Date': '20250102', 'Value': ['4.62', '3.79']}], 'BK7': [{ 'Date': '20250102', 'Value': ['5.25', '8.22']}], 'BK8': [{ 'Date': '20250102', 'Value': ['46.52', '312.41']}], 'BK9': [{ 'Date': '20250102', 'Value': ['0.00', '35.00']}, {'Date': '20260130', 'Value': ['10.00', '25.00']]}]} 
```

← 获取指定日期股票交易数据get\_gpjy\_value\_by\_date

获取指定日期板块交易数据get\_bkjy\_value\_by\_date →

# 获取指定日期板块交易数据get\_bkjy\_value\_by\_date

根据板块代码，获取指定日期的板块交易数据，需要先在客户端中下载股票数据包

```python
get_bkjy_value_by_date(stock_list: List[str] = [],
    field_list: List[str] = [],
    year: int = 0,
    mmdd: int = 0) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>year</td><td>Y</td><td>int</td><td>指定年份</td></tr><tr><td>mmdd</td><td>Y</td><td>int</td><td>指定月日</td></tr></table>

如果year为0,mmdd为0,表示最新数据,mmdd为1,2,3...,表示倒数第2,3,4...个数据。  
需要先在客户端中下载股票数据包

# 输出数据

同get\_bkjy\_value一样。

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
bk_one = tq.get_bkjy_value_by_date(stock_list=['880660.SH'], field_list=['BK9', 'BK10', 'BK11', 'BK12', 'BK13'], year=0, mmdd=0)
print(bk_one) 
```

数据样本  
```txt
1 {'880660.SH': {'BK10': ['6705.83', '191.60'], 'BK11': ['6183.65', '176.68'], 'BK12': ['0.00', '0.00'], 'BK13': ['0.00', '0.00'], 'BK9': ['3.00', '31.00']}} 
```

# 获取市场交易数据

获取指定时间段内的市场交易数据，需要先在客户端中下载股票数据包

```python
get_scjy_value(field_list: List[str] = [],
    start_time: str = '',
    end_time: str = '') -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>start_time</td><td>N</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>N</td><td>str</td><td>结束时间</td></tr></table>

输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>SC01</td><td>double</td><td></td><td>融资融券 沪深京融资余额(万元) 沪深京融券余额(万元)</td></tr><tr><td>SC02</td><td>double</td><td></td><td>陆股通资金流入 沪股通流入金额(亿元) 深股通流入金额(亿元)[注:沪股通限制展示2000条数据,深股通展示自20161205以后的数据]</td></tr><tr><td>SC03</td><td>double</td><td></td><td>沪深京涨停股个数 涨停股个数 曾涨停股个数 [注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC04</td><td>double</td><td></td><td>沪深京跌停股个数 跌停股个数 曾跌停股个数 [注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC05</td><td>double</td><td></td><td>上证50股指期货 净持仓(手)[注:该指标展示20171009日之后的数据]</td></tr><tr><td>SC06</td><td>double</td><td></td><td>沪深300股指期货 净持仓(手) [注:该指标展示20171009日之后的数据]</td></tr><tr><td>SC07</td><td>double</td><td></td><td>中证500股指期货 净持仓(手) [注:该指标展示20171009日之后的数据]</td></tr><tr><td>SC08</td><td>double</td><td></td><td>ETF基金规模份额数据 ETF基金规模(亿份) ETF净申赎(亿份)</td></tr><tr><td>SC09</td><td>double</td><td></td><td>沪月新开A股账户 沪月新开A股账户(万户)</td></tr><tr><td>SC10</td><td>double</td><td></td><td>增减持统计 增持额(万元) 减持额(万元)[注:部分公司公告滞后,造成每天查看的数据可能会不一样]</td></tr><tr><td>SC11</td><td>double</td><td></td><td>大宗交易 溢价的大宗交易额(万元) 折价的大宗交易额(万元)</td></tr><tr><td>SC12</td><td>double</td><td></td><td>限售解禁 限售解禁计划额(亿元) 限售解禁股份实际上市金额(亿元)[注:该指标展示201802月之后的数据;部分股票的解禁日期延后,造成不同日期提取的某天的计划额可能不同]</td></tr><tr><td>SC13</td><td>double</td><td></td><td>分红 市场总分红额(亿元)[注:除权派息日的A股市场总分红额]</td></tr><tr><td>SC14</td><td>double</td><td></td><td>募资 市场总募资额(亿元)[注:发行日期/除权日期的首发、配股和增发的总募资额]</td></tr><tr><td>SC15</td><td>double</td><td></td><td>打板资金 封板成功资金(亿元) 封板失败资金(亿元) [注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC16</td><td>double</td><td></td><td>龙虎榜 买入总金额(亿元) 卖出总金额(亿元)</td></tr><tr><td>SC17</td><td>double</td><td></td><td>龙虎榜机构数据 买入金额(亿元) 卖出金额(亿元)</td></tr><tr><td>SC18</td><td>double</td><td></td><td>龙虎榜营业部数据 买入金额(亿元) 卖出金额(亿元)</td></tr><tr><td>SC19</td><td>double</td><td></td><td>龙虎榜沪深股通数据 买入金额(亿元) 卖出金额(亿元)</td></tr><tr><td>SC20</td><td>double</td><td></td><td>陆股通净买入 沪股通净买入额(亿元) 深股通净买入额(亿元)</td></tr><tr><td>SC21</td><td>double</td><td></td><td>每周无限售质押率 深市质押率(%) 沪市质押率(%)[注:该指标展示20180128日之后的数据]</td></tr><tr><td>SC22</td><td>double</td><td></td><td>每周有限售质押率 深市质押率(%) 沪市质押率(%)[注:该指标展示20180128日之后的数据]</td></tr><tr><td>SC23</td><td>double</td><td></td><td>连板家数 连板股个数(包含ST和未开板新股) 连板股个数(不含ST股和未开板新股)[注:该指标展示20180319日之后的数据]</td></tr><tr><td>SC24</td><td>double</td><td></td><td>沪深京涨跌停股个数 涨停股个数(不含ST股和未开板新股) 跌停股个数 (不含ST股)[注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC25</td><td>double</td><td></td><td>融资融券 沪深京融资买入额 (万元) 沪深京融券卖出量 (万股)</td></tr><tr><td>SC26</td><td>double</td><td></td><td>每周市场质押比 每周市场质押比例 (%) [注:该指标展示20180316日之后的数据]</td></tr><tr><td>SC27</td><td>double</td><td></td><td>央行公开市场净投放 央行公开市场净投放 (亿元)</td></tr><tr><td>SC28</td><td>double</td><td></td><td>历史A股新高新低数 历史新高A股股票个数 历史新低A股股票个数(上市满一年的股票)</td></tr><tr><td>SC29</td><td>double</td><td></td><td>120天A股新高新低数 120天新高A股股票个数 120天新低A股股票个数(上市满一年的股票)</td></tr><tr><td>SC30</td><td>double</td><td></td><td>涨停数据 市场高度(不含ST股和未开板新股) 2板以上涨停个数(不含ST股和未开板新股)[注:该指标展示20180319日之后的数据]</td></tr><tr><td>SC31</td><td>double</td><td></td><td>涨跌家数 涨家数 (剔除停牌) 跌家数 (剔除停牌)</td></tr><tr><td>SC32</td><td>double</td><td></td><td>20天A股新高新低数 20天新高A股股票个数 20天新低A股股票个数(上市满一年的股票)</td></tr><tr><td>SC33</td><td>double</td><td></td><td>市场总封单金额 涨停封单金额 (亿元) 跌停封单金额 (亿元)[注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC34</td><td>double</td><td></td><td>涨跌股成交量 上涨股成交量(万手) 下跌股成交量(万手)</td></tr><tr><td>SC35</td><td>double</td><td></td><td>涨停数据 换手板家数 回封率(%) [注:两个指标都剔除了未开板新股,换手板家数展示20190605日之后的数据,回封率展示20180927日之后的数据]</td></tr><tr><td>SC36</td><td>double</td><td></td><td>曾涨跌停股个数 曾涨停股个数(剔除ST股和未开板新股) 曾跌停股个数(剔除ST股)[注:该指标展示20160926日之后的数据]</td></tr><tr><td>SC37</td><td>double</td><td></td><td>转融券 融出市值(亿元) 期末余额(亿元)</td></tr><tr><td>SC38</td><td>double</td><td></td><td>ETF基金规模金额数据 ETF基金规模(亿元) ETF净申赎(亿元)</td></tr><tr><td>SC39</td><td>double</td><td></td><td>涨跌5%家数 涨幅大于等于5%家数 跌幅大于等于5%家数</td></tr><tr><td>SC40</td><td>double</td><td></td><td>陆股通成交 陆股通成交总额(亿元) 陆股通成交总笔(万笔)</td></tr><tr><td>SC41</td><td>double</td><td></td><td>中证1000股指期货 净持仓(手)[注:该指标展示20220722日之后的数据]</td></tr><tr><td>SC42</td><td>double</td><td></td><td>沪深股通成交金额 沪股通成交总额(亿元) 深股通成交总额(亿元)</td></tr></table>

接口使用

<table><tr><td>1</td><td>from tqcenter import tq</td><td>py</td></tr><tr><td>2</td><td></td><td></td></tr><tr><td>3</td><td>tq.initialize(__file__)</td><td></td></tr></table>

```txt
print(sc_val) 
```

数据样本  
```json
{'SC1': [{ 'Date': '20250102', 'Value': ['184712288.00', '999820.06']}], 'SC2': [{ 'Date': '20250102', 'Value': ['0.00', '0.00']}], 'SC3': [{ 'Date': '20250102', 'Value': ['67.00', '49.00']}], 'SC4': [{ 'Date': '20250102', 'Value': ['32.00', '30.00']}], 'SC5': [{ 'Date': '20250102', 'Value': [-21204.00', '0.00']]}} 
```

← 获取指定日期板块交易数据get\_bkjy\_value\_by\_date

获取指定日期市场交易数据get\_scjy\_value\_by\_date →

# 获取指定日期市场交易数据get\_scjy\_value\_by\_date

获取指定时间的市场交易数据，需要先在客户端中下载股票数据包  
```python
get_scjy_value_by_date(field_list: List[str] = [],
year: int = 0,
mmdd: int = 0) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空</td></tr><tr><td>year</td><td>Y</td><td>int</td><td>指定年份</td></tr><tr><td>mmdd</td><td>Y</td><td>int</td><td>指定月日</td></tr></table>

如果year为0,mmdd为0,表示最新数据,mmdd为1,2,3...,表示倒数第2,3,4...个数据。  
需要先在客户端中下载股票数据包

# 输出数据

同get\_scjy\_value一样。

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
    sc_one = tq.get_scjy_value_by_date(field_list=['SC6', 'SC7', 'SC8', 'SC9', 'SC10'], year=0, mmdd=0)
    print(sc_one) 
```

数据样本  
```txt
1 {'SC10': ['0.00', '181415.13'], 'SC6': [-30479.00', '0.00'], 'SC7': [-26449.00', '0.00'], 'SC8': ['31752.86', '84.22'], 'SC9': ['993000.00', '2900.00']} 
```

# 获取股票的单个财务数据get\_gp\_one\_data

# 根据证券代码，获取股票的单个数据

```python
get_gp_one_data(stock_list: List[str] = [],
    field_list: List[str] = []) -> Dict: 
```

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>证券代码列表</td></tr><tr><td>field_list</td><td>Y</td><td>List[str]</td><td>字段筛选,不能为空(如 G047 表示是第47号个股数据最新业绩预告 本期扣非净利润预计同比增减幅上限%)这个值,GO为gp one的首字母大写</td></tr></table>

# 输出数据

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>GO1</td><td>double</td><td></td><td>发行价(元)</td></tr><tr><td>GO2</td><td>double</td><td></td><td>总发行数量(万股)</td></tr><tr><td>GO3</td><td>double</td><td></td><td>一致预期目标价(元)[注:一致预期值均为近半年内各家机构预测数值的平均值]</td></tr><tr><td>GO4</td><td>double</td><td></td><td>一致预期T年度</td></tr><tr><td>GO5</td><td>double</td><td></td><td>一致预期T年每股收益</td></tr><tr><td>GO6</td><td>double</td><td></td><td>一致预期T+1年每股收益</td></tr><tr><td>GO7</td><td>double</td><td></td><td>一致预期T+2年每股收益</td></tr><tr><td>GO8</td><td>double</td><td></td><td>一致预期T年净利润(万元)</td></tr><tr><td>GO9</td><td>double</td><td></td><td>一致预期T+1年净利润(万元)</td></tr><tr><td>GO10</td><td>double</td><td></td><td>一致预期T+2年净利润(万元)</td></tr><tr><td>GO11</td><td>double</td><td></td><td>一致预期T年营业收入(万元)</td></tr><tr><td>GO12</td><td>double</td><td></td><td>一致预期T+1年营业收入(万元)</td></tr><tr><td>GO13</td><td>double</td><td></td><td>一致预期T+2年营业收入(万元)</td></tr><tr><td>GO14</td><td>double</td><td></td><td>一致预期T年营业利润(万元)</td></tr><tr><td>GO15</td><td>double</td><td></td><td>一致预期T+1年营业利润(万元)</td></tr><tr><td>GO16</td><td>double</td><td></td><td>一致预期T+2年营业利润(万元)</td></tr><tr><td>GO17</td><td>double</td><td></td><td>一致预期T年每股净资产(元)</td></tr><tr><td>GO18</td><td>double</td><td></td><td>一致预期T+1年每股净资产(元)</td></tr><tr><td>GO19</td><td>double</td><td></td><td>一致预期T+2年每股净资产(元)</td></tr><tr><td>GO20</td><td>double</td><td></td><td>一致预期T年净资产收益率(%)</td></tr><tr><td>GO21</td><td>double</td><td></td><td>一致预期T+1年净资产收益率(%)</td></tr><tr><td>GO22</td><td>double</td><td></td><td>一致预期T+2年净资产收益率(%)</td></tr><tr><td>GO23</td><td>double</td><td></td><td>一致预期T年PE</td></tr><tr><td>GO24</td><td>double</td><td></td><td>一致预期T+1年PE</td></tr><tr><td>GO25</td><td>double</td><td></td><td>一致预期T+2年PE</td></tr><tr><td>GO26</td><td>double</td><td></td><td>最新解禁日(YYMMDD格式)</td></tr><tr><td>GO27</td><td>double</td><td></td><td>最新解禁数量(万股)</td></tr><tr><td>GO28</td><td>double</td><td></td><td>下一报告期的预约披露时间</td></tr><tr><td>GO29</td><td>double</td><td></td><td>最新持股机构家数</td></tr><tr><td>GO30</td><td>double</td><td></td><td>最新机构持股总量(万股)</td></tr><tr><td>GO31</td><td>double</td><td></td><td>最新持股基金家数</td></tr><tr><td>GO32</td><td>double</td><td></td><td>最新基金持股量(万股)</td></tr><tr><td>GO33</td><td>double</td><td></td><td>最新总股本(万股)</td></tr><tr><td>GO34</td><td>double</td><td></td><td>最新实际流通A股(万股)</td></tr><tr><td>GO35</td><td>double</td><td></td><td>最新业绩预告 报告期(YYMMDD格式)</td></tr><tr><td>GO36</td><td>double</td><td></td><td>最新业绩预告 本期归母净利润下限(万元)</td></tr><tr><td>GO37</td><td>double</td><td></td><td>最新业绩预告 本期归母净利润上限(万元)</td></tr><tr><td>GO38</td><td>double</td><td></td><td>最新业绩预告 本期归母净利润预计同比增减幅下限%</td></tr><tr><td>GO39</td><td>double</td><td></td><td>最新业绩预告 本期归母净利润预计同比增减幅上限%</td></tr><tr><td>GO40</td><td>double</td><td></td><td>最新业绩快报 报告期</td></tr><tr><td>GO41</td><td>double</td><td></td><td>最新业绩快报 归母净利润(万元)</td></tr><tr><td>GO42</td><td>double</td><td></td><td>分红募资 派现总额(万元)</td></tr><tr><td>GO43</td><td>double</td><td></td><td>分红募资 募资总额(万元)</td></tr><tr><td>GO44</td><td>double</td><td></td><td>最新业绩预告 本期扣非净利润下限(万元)</td></tr><tr><td>GO45</td><td>double</td><td></td><td>最新业绩预告 本期扣非净利润上限(万元)</td></tr><tr><td>GO46</td><td>double</td><td></td><td>最新业绩预告 本期扣非净利润预计同比增减幅下限%</td></tr><tr><td>GO47</td><td>double</td><td></td><td>最新业绩预告 本期扣非净利润预计同比增减幅上限%</td></tr></table>

接口使用

<table><tr><td>1</td><td>from tqcenter import tq</td><td>py</td></tr><tr><td>2</td><td></td><td></td></tr><tr><td>3</td><td>tq.initialize(__file__)</td><td></td></tr></table>

print(go)6

# 数据样本

```json
1 { '688318.SH': { 'G01': '107.41', 'G02': '1667.00', 'G03': '0.00', 'G04': '2025.00', 'G05': '1.74'} } 
```

← 获取指定日期市场交易数据get\_scjy\_value\_by\_date

获取系统分类成份股get\_stock\_list →

# 获取A股板块代码列表get\_sector\_list

# 获取A股全部板块代码列表

```txt
def get_sector_list(list_type: int = 0) -> List: 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>list_type</td><td>Y</td><td>int</td><td>返回数据类型</td></tr></table>

list\_type = 0 只返回代码，list\_type = 1 返回代码和名称

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
block_list = tq.get_sector_list()
print(block_list)
block_list2 = tq.get_sector_list(list_type = 1)
print(block_list2) 
```

py

注：此接口相当于 get\_stock\_list('10')

# 数据样本

```json
['880081.SH', '880082.SH', '880201.SH', '880202.SH', '880203.SH', '880204.SH', '880205.SH', '880206.SH', '880207.SH', '880208.SH', ...]
[{'Code': '880081.SH', 'Name': '轮动趋势'}, {'Code': '880082.SH', 'Name': '板块趋势'}, {'Code': '880201.SH', 'Name': '黑龙江'}, {'Code': '880202.SH', 'Name': '新疆板块'}, {'Code': '880203.SH', 'Name': '吉林板块'}, {'Code': '880204.SH', 'Name': '甘肃板块'}, {'Code': '880205.SH', 'Name': '辽宁板块'}, {'Code': '880206.SH', 'Name': '青海板块'}, {'Code': '880207.SH', 'Name': '北京板块'}, ...}] 
```

# 获取系统分类成份股get\_stock\_list

根据入参返回指定证券代码列表  
```python
def get_stock_list(market = None,
    list_type: int = 0) -> List: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>market</td><td>Y</td><td>str</td><td>指定代码</td></tr><tr><td>list_type</td><td>Y</td><td>int</td><td>返回数据类型</td></tr></table>

list\_type = 0 只返回代码，list\_type = 1 返回代码和名称

```txt
1 默认为全部A股
2 0:自选股 1:持仓股
3 5:所有A股 6:上证指数成份股 7:上证主板 8:深证主板 9:重点指数
4 10:所有板块指数 11:缺省行业板块 12:概念板块 13:风格板块 14:地区板块 15:缺省行业分类+概念板块 16:研究行业一级 1
5 7:研究行业二级 18:研究行业三级
6 21:含H股 22:含可转债 23:沪深300 24:中证500 25:中证1000 26:国证2000 27:中证2000 28:中证A500
7 30:REITs 31:ETF基金 32:可转债 33:LOF基金 34:所有可交易基金 35:所有沪深基金 36:T+0基金
8 49:金融类企业 50:沪深A股 51:创业板 52:科创板 53:北交所
9 101:国内期货 102:港股 103:美股
10 91:ETF追踪的指数
92:国内期货主力合约
```

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
stock_list = tq.get_stock_list('16')
print(stock_list)

stock_list2 = tq.get_stock_list('16', list_type=1)
print(stock_list2) 
```

数据样本  
```txt
[ '881001.SH', '881006.SH', '881015.SH', '881061.SH', '881070.SH', '881090.SH', '881105.SH', '881129.SH', '881150.SH', '881166.SH', '881183.SH', '881199.SH', '881211.SH', '881230.SH', '881260.SH', '881286.SH', '881292.SH', '881318.SH', '881337.SH', '881351.SH', '881368.SH', '881385.SH', '881393.SH', '881405.SH', '881417.SH', '881426.SH', '881441.SH', '881458.SH', '881469.SH', '881477.SH']
[{'Code': '881001.SH', 'Name': '煤炭'}, {'Code': '881006.SH', 'Name': '石油'}, {'Code': '881015.SH', 'Name': '化工'}, {'Code': '881061.SH', 'Name': '钢铁'}, {'Code': '881070.SH', 'Name': '有色'}, {'Code': '881090.SH', 'Name': '建材'}, {'Code': '881105.SH', 'Name': '农林牧渔'}, {'Code': '881129.SH', 'Name': '食品饮料'}, {'Code': '881150.SH', 'Name': '纺织服饰'}, {'Code': '881166.SH', 'Name': '轻工制造'}, {'Code': '881183.SH', 'Name': '家电'}, {'Code': '881199.SH', 'Name': '商贸'}, {'Code': '881211.SH', 'Name': '汽车'}, {'Code': '881230. 
```

```javascript
Name: 通信}, {Code: '881931.SH', Name: 计算机}, {Code: '881906.SH', Name: [传媒]}, {Code': '881385.SH', 'Name': '银行'}, {'Code': '881393.SH', 'Name': '非银金融'}, {'Code': '881405.SH', 'Name': '建筑'}, {'Code': '881417.SH', 'Name': '房地产'}, {'Code': '881426.SH', 'Name': '社会服务'}, {'Code': '881441.SH', 'Name': '交通运输'}, {'Code': '881458.SH', 'Name': '公用事业'}, {'Code': '881469.SH', 'Name': '环保'}, {'Code': '881477.SH', 'Name': '综合'}]} 
```

← 获取股票的单个数据(非序列)get\_gp\_one\_data

获取A股板块代码列表get\_sector\_list →

# 获取板块成份股get\_stock\_list\_in\_sector

根据板块代码获取其成份股列表  
```python
def get_stock_list_in_sector(block_code: str,
    block_type: int = 0,
    list_type: int = 0) -> List: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>block_code</td><td>Y</td><td>str</td><td>板块代码</td></tr><tr><td>block_type</td><td>N</td><td>str</td><td>板块类型</td></tr><tr><td>list_type</td><td>Y</td><td>int</td><td>返回数据类型</td></tr></table>

. 获取A股成份股时支持板块名称或板块代码两种方式传入  
block\_type=0 表示传入板块指数代码或板块指数名称（默认）  
block\_type=1 表示传入自定义板块简称 需要是客户端中预先定义好自定义板块的简称 如果是ZXG表示是自选股；TJG表示是临时条件股  
list\_type = 0 只返回代码，list\_type = 1 返回代码和名称

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
#通过板块代码获取成份股
block_stocks = tq.get_stock_list_in_sector('880081.SH')
print(block_stocks)
print(len(block_stocks))

#通过板块名获取成份股
block_stocks = tq.get_stock_list_in_sector('钛金属')
print(block_stocks)
print(len(block_stocks))

block_stocks2 = tq.get_stock_list_in_sector('钛金属', list_type=1)
print(block_stocks2)

#获取自定义板块成份股
block_stocks = tq.get_stock_list_in_sector('CSBK', block_type = 1)
print(block_stocks)
print(len(block_stocks)) 
```

数据样本  
```txt
[ '159922.SZ', '510500.SH', '512500.SH' ]
3
[ '000545.SZ', '000629.SZ', '000635.SZ', '000688.SZ', '000709.SZ', '000962.SZ', '002136.SZ', '002140.SZ', '002145.SZ', '002149.SZ', '002167.SZ', '002386.SZ', '002601.SZ', '002978.SZ', '300402.SZ', '300891.SZ', '6004 
```

```json
[ 'Code': '000549.SZ', 'Name': '金庸钛业'}, [ 'Code': '000029.SZ', 'Name': '钒钛股份'}, [ 'Code': '000039.SZ', 'Name': '英力特'}, { 'Code': '000688.SZ', 'Name': '国城矿业'}, { 'Code': '000709.SZ', 'Name': '河钢股份'}, { 'Code': '000962.SZ', 'Name': '东方钽业'}, { 'Code': '002136.SZ', 'Name': '安纳达'}, { 'Code': '002140.SZ', 'Name': '东华科技'}, { 'Code': '002145.SZ', 'Name': '钛能化学'}, { 'Code': '002149.SZ', 'Name': '西部材料'}, { 'Code': '002167.SZ', 'Name': '东方锆业'}, { 'Code': '002386.SZ', 'Name': '天原股份'}, { 'Code': '002601.SZ', 'Name': '龙佰集团'}, { 'Code': '002978.SZ', 'Name': '安宁股份'}, { 'Code': '300402.SZ', 'Name': '宝色股份'}, { 'Code': '300891.SZ', 'Name': '惠云钛业'}, { 'Code': '600456.SH', 'Name': '宝钛股份'}, { 'Code': '600727.SH', 'Name': '鲁北化工'}, { 'Code': '603067.SH', 'Name': '振华股份'}, { 'Code': '603389.SH', 'Name': '*ST亚振'}, { 'Code': '603826.SH', 'Name': '坤彩科技'}, { 'Code': '688122.SH', 'Name': '西部超导'}, { 'Code': '688750.SH', 'Name': '金天钛业'}, { 'Code': '920068.BJ', 'Name': '天工股份'}] ['600000.SH', '600004.SH', '600006.SH', '600007.SH', '600008.SH', '600009.SH', '600010.SH'] 
```

# 注意

get\_stock\_list\_in\_sector 入参的板块只能是自定义板块或者15板块指数

不支持系统 全部A股 沪深A股等板块

← 获取A股板块代码列表get\_sector\_list

获取自定义板块列表get\_user\_sector →

# 获取自定义板块列表get\_user\_sector

获取自定义板块代码列表  
```erlang
1 get_user_sector(cls) -> List: py 
```

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
user_list = tq.get_user_sector()
print(user_list)
print(len(user_list)) 
```

数据样本  
```txt
1 [{ 'Code': 'CSBK', 'Name': '测试板块'}, {'Code': 'CSBK2', 'Name': '测试板块2'}] 
```

← 获取板块成份股get\_stock\_list\_in\_sector

添加自定义板块成份股send\_user\_block →

# 创建自定义板块

在通达信客户端中创建自定义板块  
```python
create_sector(block_code:str = '', block_name:str = ''): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>block_code</td><td>Y</td><td>str</td><td>自定义板块简称</td></tr><tr><td>block_name</td><td>Y</td><td>str</td><td>自定义板块名称</td></tr></table>

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
create_ptr = tq.create_sector(block_code='CSBK2', block_name='测试板块2')
print(create_ptr) 
```

数据样本  
```json
{
    "Error" : "创建CSBK2板块成功",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 删除自定义板块

删除通达信客户端中的自定义板块  
```python
1 delete_sector(block_code:str = ''): py 
```

输入参数  
```txt
参数 是否必选 参数类型 参数说明
block_code Y str 自定义板块简称
```

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
delete_ptr = tq.delete_sector(block_code='CSBK')
print(delete_ptr) 
```

数据样本  
```json
{
    "Error" : "删除CSBK板块成功",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 创建自定义板块

重命名通达信客户端中的自定义板块  
```python
rename_sector(block_code:str = '', block_name:str = ''): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>block_code</td><td>Y</td><td>str</td><td>自定义板块简称</td></tr><tr><td>block_name</td><td>Y</td><td>str</td><td>重命名后的自定义板块名称</td></tr></table>

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
rename_ptr = tq.rename_sector(block_code='CSBK', block_name='测试板块重命名')
print(rename_ptr) 
```

数据样本  
```json
{
    "Error" : "重命名CSBK板块成功",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 添加自定义板块成份股

往指定自定义板块中添加成份股  
```python
send_user_block(block_code: str = '',
stocks: List[str] = [],
show: bool = False) -> Dict: 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>block_code</td><td>Y</td><td>str</td><td>自定义板块简称</td></tr><tr><td>stocks</td><td>Y</td><td>List[str]</td><td>添加的自选股</td></tr><tr><td>show</td><td>N</td><td>str</td><td>客户端是否切换至对应板块界面</td></tr></table>

block\_code 为客户端已有的自定义板块简称，如果不存在则无效果，空则为添加到临时条件股  
block\_code存在，传入空列表则表示清空该板块所有股票，否则为添加新股票  
自选股的block\_code为ZXG

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
zxg_result = tq.send_user_block(block_code='CSBK', stocks=["600000.SH", "600004.SH", "000001.SZ", "000002.SZ"]) 
```

数据样本  
```txt
1 {'Error': 'Add User Block Completed', 'ErrorId': '0', 'run_id': '1'} 
```

# 清空自定义板块成份股

清空指定通达信客户端自定义板块的成份股  
```python
1 clear_sector(block_code:str = ''): py 
```

输入参数  
```txt
参数 是否必选 参数类型 参数说明
block_code Y str 自定义板块简称
```

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
clear_ptr = tq.clear_sector(block_code='CSBK')
print(clear_ptr) 
```

数据样本  
```json
{
    "Error" : "清空CSBK板块成功",
    "ErrorId" : "0",
    "run_id" : "1"
} 
```

# 获取跟踪指数的ETF信息get\_trackzs\_etf\_info

# 根据指数代码获取跟踪它的ETF的信息

1

```python
def get_trackzs_etf_info(zs_code: str = ''): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>zs_code</td><td>Y</td><td>str</td><td>指数代码</td></tr></table>

# 输出数据

<table><tr><td>名称</td><td>类型</td><td>说明</td></tr><tr><td>Code</td><td>str</td><td>证券代码</td></tr><tr><td>Name</td><td>str</td><td>证券名称</td></tr><tr><td>NowPrice</td><td>str</td><td>现价</td></tr><tr><td>PreClose</td><td>str</td><td>昨收</td></tr><tr><td>IOPV</td><td>str</td><td>净值</td></tr><tr><td>Zgb</td><td>str</td><td>净额(万份)</td></tr><tr><td>Sz</td><td>str</td><td>规模(亿元)</td></tr></table>

# 接口使用

```python
from tqcenter import tq
tq.initialize(__file__)
trackzs_etf_info = tq.get_trackzs_etf_info(zs_code='950162.CSI')
print(trackzs_etf_info) 
```

py

# 数据样本

```txt
[{'Code': '589210.SH', 'Name': '科创芯片设计ETF', 'NowPrice': '1.208', 'PreClose': '1.192', 'IOPV': '1.2071', 'Zgb': '7646.90', 'Sz': '0.92'}, {'Code': '589070.SH', 'Name': '科创芯片设计ETF', 'NowPrice': '0.954', 'PreClose': '0.942', 'IOPV': '0.9547', 'Zgb': '65129.30', 'Sz': '6.21'}, {'Code': '588780.SH', 'Name': ' 科创芯片设计ETF', 'NowPrice': '0.875', 'PreClose': '0.866', 'IOPV': '0.8756', 'Zgb': '106790.20', 'Sz': '9.34'}, {'Code': '589170.SH', 'Name': '科创芯片设计ETF', 'NowPrice': '0.969', 'PreClose': '0.956', 'IOPV': '0.9685', 'Zgb': '37890.90', 'Sz': '3.67'}, {'Code': '589250.SH', 'Name': '芯设计PY', 'NowPrice': '0.000', 'PreClose': '0.000', 'IOPV': '0.0000', 'Zgb': '0.00', 'Sz': '0.00'}, {'Code': '589030.SH', 'Name': '科创芯片设计ETF', 'NowPrice': '1.013', 'PreClose': '1.000', 'IOPV': '1.0130', 
```

← 重命名自定义板块rename\_sector

可转债信息get\_kzz\_info →

# 获取可转债信息get\_kzz\_info

# 根据可转债代码获取可转债信息

```python
def get_kzz_info(stock_code:str = '', field_list: List[str] = []): 
```

py

# 输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>可转债代码</td></tr><tr><td>field_list</td><td>N</td><td>List[str]</td><td>字段筛选,传空则返回全部</td></tr></table>

# 输出数据

<table><tr><td>名称</td><td>类型</td><td>说明</td></tr><tr><td>SetCode</td><td>str</td><td>证券市场</td></tr><tr><td>KZZCode</td><td>str</td><td>可转债代码</td></tr><tr><td>HSCode</td><td>str</td><td>正股代码</td></tr><tr><td>ZGPrice</td><td>str</td><td>转股价格</td></tr><tr><td>CurRate</td><td>str</td><td>当期利率</td></tr><tr><td>RestScope</td><td>str</td><td>剩余规模(万)</td></tr><tr><td>PutBack</td><td>str</td><td>回售触发价</td></tr><tr><td>ForceRedeem</td><td>str</td><td>强赎触发价</td></tr><tr><td>ZGDate</td><td>str</td><td>转股日</td></tr><tr><td>EndPrice</td><td>str</td><td>到期价</td></tr><tr><td>EndDate</td><td>str</td><td>到期日期</td></tr><tr><td>ZGRate</td><td>str</td><td>转股比率%</td></tr><tr><td>RealValue</td><td>str</td><td>纯债价值</td></tr><tr><td>ExpireYield</td><td>str</td><td>到期收益率%</td></tr><tr><td>KZZScore</td><td>str</td><td>可转债评级</td></tr><tr><td>HSScore</td><td>str</td><td>主体评级</td></tr><tr><td>RedeemDate</td><td>str</td><td>赎回登记日期</td></tr><tr><td>RedeemPrice</td><td>str</td><td>赎回价格</td></tr><tr><td>PutDate</td><td>str</td><td>回售申报起始日期</td></tr><tr><td>PutPrice</td><td>str</td><td>回售价格</td></tr><tr><td>ZGCode</td><td>str</td><td>转股代码</td></tr><tr><td></td><td></td><td></td></tr><tr><td>AGPrice</td><td>str</td><td>正股当前价格</td></tr><tr><td>KZZPrice</td><td>str</td><td>可转债当前价格</td></tr><tr><td>KZZYj</td><td>str</td><td>溢价率</td></tr><tr><td>ZGValue</td><td>str</td><td>转股价值</td></tr></table>

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
kzz_info = tq.get_kzz_info(stock_code = '123039.SZ')
print(kzz_info) 
```

数据样本  
```txt
{'CurRate': '2.80',
'EndDate': '20251226',
'EndPrice': '115.00',
'ExpireYield': '0.00',
'ForceRedeem': '37.90',
'HSCode': '300577',
'HSScore': 'A+', 
'KZZCode': '123039',
'KZZScore': 'A+', 
'PutBack': '20.41',
'PutDate': '0',
'PutPrice': '0.00',
'RealValue': '0.00',
'RedeemDate': '0',
'RedeemPrice': '0.00',
'RestScope': '22044.02',
'ZGCode': '123039',
'ZGDate': '20200702',
'ZGPrice': '29.15',
'ZGRate': '1.15',
'setcode': '0'} 
```

# 格式化K线数据formula\_format\_data

格式化get\_market\_data获取的K线数据  
```python
def formula_format_data(data_dict: Dict = {}): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>data_dict</td><td>Y</td><td>Dict</td><td>get_market_data获取格式的K线Dict</td></tr></table>

get\_market\_data获取的K线数据不能直接用于设置公式参数，须先调用formula\_format\_data进行格式化  
formula\_format\_data返回值为List[Dict]，其中Dict的Key须有["Amount", "Volume", "Close", "Open", "High", "Low"]，用户可以 直接提供符合条件的List提供给tdx\_formula\_set\_data。

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
test_md = tq.get_market_data(stock_list=['688318.SH'], count=5, period='1d')
format_md = tq.formula_format_data(test_md)
print(format_md) 
```

数据样本  
```json
{'688318.SH': [
    {'Date': '2026-01-20 00:00:00', 'Amount': 33930.29, 'Volume': 2345401.0, 'Close': 144.4, 'Open': 146.5, 'High': 146.98, 'Low': 142.65},
    {'Date': '2026-01-21 00:00:00', 'Amount': 35841.09, 'Volume': 2472760.0, 'Close': 144.77, 'Open': 144.49, 'High': 146.5, 'Low': 143.1},
    {'Date': '2026-01-22 00:00:00', 'Amount': 41598.79, 'Volume': 2878793.0, 'Close': 143.03, 'Open': 145.0, 'High': 147.0, 'Low': 142.5},
    {'Date': '2026-01-23 00:00:00', 'Amount': 47131.04, 'Volume': 3256538.0, 'Close': 144.39, 'Open': 142.58, 'High': 146.88, 'Low': 142.58},
    {'Date': '2026-01-26 00:00:00', 'Amount': 54141.73, 'Volume': 3761141.0, 'Close': 141.84, 'Open': 143.7, 'High': 146.77, 'Low': 141.8}] 
```

# 向通达信公式设置数据formula\_set\_data

在调用公式前须先设置公式参数，此接口与formula\_set\_data\_info作用一样，会互相覆盖

```python
def formula_set_data(stock_code: str = '',
    stock_period: str = '1d',
    stock_data: List = [],
    count: int = 1,
    dividend_type: int = 0): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>股票代码</td></tr><tr><td>stock_period</td><td>Y</td><td>str</td><td>K线周期</td></tr><tr><td>stock_data</td><td>Y</td><td>List</td><td>指定格式的K线数据</td></tr><tr><td>count</td><td>Y</td><td>int</td><td>选取的K线数量</td></tr><tr><td>dividend_type</td><td>Y</td><td>int</td><td>复权类型</td></tr></table>

需要先在下载对应的盘后数据  
dividend\_type的取值为：0不复权 1前复权 2后复权  
count为设定stock\_data中生效的K线数据，即stock\_data中有效数据不能小于count  
count须大于0，且最大不超过24000  
. 设置的数据在断开连接前一直生效，后设置的数据会覆盖前面设置的数据

# 接口使用

```python
from tqcenter import tq
    tq.initialize(__file__)
    test_md = tq.get_market_data(stock_list=['688318.SH'], count=5, period='1d')
    format_md = tq.tdx_formula_format_data(test_md)
    formula_set_k = tq.formula_set_data(stock_code='688318.SH', stock_period='1d', stock_data=format_md['688318.SH'], count=len(format_md['688318.SH'])) print(formula_set_k) 
```

# 数据样本

```txt
1 {'ErrorId': '0', 'Msg': '向通达信公式系统设置数据成功！', 'run_id': '1'}
```

# 向通达信公式设置数据信息formula\_set\_data\_info

在调用公式前须先设置公式参数，此接口与formula\_set\_data作用一样，会互相覆盖  
```python
def formula_set_data_info(stock_code: str = '',
    stock_period: str = '1d',
    start_time: str = '',
    end_time: str = '',
    count: int = -1,
    dividend_type: int = 0): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>stock_code</td><td>Y</td><td>str</td><td>股票代码</td></tr><tr><td>stock_period</td><td>Y</td><td>str</td><td>K线周期</td></tr><tr><td>start_time</td><td>Y</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>Y</td><td>str</td><td>结束时间</td></tr><tr><td>count</td><td>Y</td><td>int</td><td>截取K线数量</td></tr><tr><td>dividend_type</td><td>Y</td><td>int</td><td>复权类型</td></tr></table>

需要先在下载对应的盘后数据  
dividend\_type的取值为：0不复权 1前复权 2后复权  
count为截取最新交易日开始往前的n条K线，当count参数不为0时，start\_time和end\_time失效  
count=-1时，获取所有数据，count=-2时，使用无序列数据  
当count为0时，start\_time和end\_time生效，指定K线为对应时间段内  
count最大值为24000，count为-1时为获取对应股票全部K线  
设置的数据在断开连接前一直生效，后设置的数据会覆盖前面设置的数据

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
formula_set_res = tq formula_set_data_info(stock_code='688318.SH', stock_period='1d', count=100, dividend_type=1)
print(formula_set_res) 
```

数据样本  
```javascript
1 {'ErrorId': '0', 'Msg': '向通达信公式系统设置数据信息成功！', 'run_id': '1'}
```

← 向通达信公式设置数据formula\_set\_data

获取公式中的设置数据formula\_get\_data →

# 获取公式中的设置数据formula\_get\_data

获取目前公式设置中的K线数据，使用前须先调用formula\_set\_data或formula\_set\_data\_info设置公式数据

```txt
1 def formula_get_data(cls): 
```

```txt
py 
```

需要先在下载对应的盘后数据

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
formula_set_res = tq formula_set_data_info(stock_code='688318.SH', stock_period='1d', count=5, dividend_type=1)
formula_kline = tq formula_get_data()
print(formula_kline) 
```

数据样本  
```jsonl
{'Code': '688318.SH', 'Data': [
{'Amount': 339302880.0, 'Close': 144.4, 'Date': '2026-01-20 00:00:00', 'High': 146.98, 'Low': 142.65, 'Open': 146.5, 'Volume': 2345401.0},
{'Amount': 358410880.0, 'Close': 144.77, 'Date': '2026-01-21 00:00:00', 'High': 146.5, 'Low': 143.1, 'Open': 144.49, 'Volume': 2472760.0},
{'Amount': 415987840.0, 'Close': 143.03, 'Date': '2026-01-22 00:00:00', 'High': 147.0, 'Low': 142.5, 'Open': 145.0, 'Volume': 2878793.0},
{'Amount': 471310432.0, 'Close': 144.39, 'Date': '2026-01-23 00:00:00', 'High': 146.88, 'Low': 142.58, 'Open': 142.58, 'Volume': 3256538.0},
{'Amount': 541417344.0, 'Close': 141.84, 'Date': '2026-01-26 00:00:00', 'High': 146.77, 'Low': 141.8, 'Open': 143.7, 'Volume': 3761141.0}], 'ErrorId': '0'} 
```

# 调用通达信公式进行计算formula\_zb/xg/exp

调用通达信三种类型的公式  
```python
#调用技术指标公式
def formula_zb(formula_name: str = '',
    formula_arg: str = '',
    xsflag: int = -1):
#调用条件选股公式
def formula_xg(formula_name: str = '',
    formula_arg: str ='av):
#调用专家系统公式
def formula_exp(formula_name: str = '',
    formula_arg: str ='av): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>formula_name</td><td>Y</td><td>str</td><td>公式名称</td></tr><tr><td>formula_arg</td><td>Y</td><td>str</td><td>公式参数</td></tr><tr><td>xsflag</td><td>Y</td><td>int</td><td>数据精度</td></tr></table>

需要先在下载对应的盘后数据  
目前支持调用技术指标公式、条件选股公式和专家系统公式，调用公式时请注意对应不同的调用接口和公式名  
formula\_arg格式为"arg1,arg2,arg3,arg4,arg5"，arg须为纯数字字符串，最多支持16个。  
xsflag小于0时返回默认精度，最大可返回8位小数。

接口使用  
```python
from tqcenter import tq
    tq.initialize(__file__)
formula_set_res = tq.formula_set_data_info(stock_code='688318.SH', stock_period='1d', count=20, dividend_type=1)
#技术指标公式MACD
formula_zb = tq.formula_zb(formula_name='MACD', formula_arg='12, 26, 9')
print(formula_zb)
#条件选股公式UPN
formula_xg = tq.formula_xg(formula_name='UPN', formula_arg='3')
print(formula_xg)
#专家系统公式CCI
formula_exp = tq.formula_zb(formula_name='CCI', formula_arg='12')
print(formula_exp) 
```

数据样本  
```txt
1 {'Data': {'DEA': [0.0, 0.01, -0.01, 0.03, 0.29, 0.63, 0.93, 1.25, 1.77, 2.27, 2.72, 3.08, 3.4, 3.57, 3.62, 3.58, 3.46, 3.3, 3.09, 2.83], 'DIF': [0.0, 0.05, -0.07, 0.19, 1.33, 1.96, 2.16, 2.52, 3.84, 4.25, 4.55, 4.5 
```

```jsonl
{ 'Data': {0.3 : [None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}, 'ErrorId': '0'}
{'Data': {'ENTERLONG': [None, None, None, None, None, None, None, None, None, None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'EXITLONG': [None, None, None, None, None, None, None, None, None, None, None, None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'ErrorId': '0'} 
```

← 获取公式中的设置数据formula\_get\_data

批量调用通达信公式formula\_process\_mul\_xg/zb →

# 批量调用通达信公式formula\_process\_mul\_xg/zb

批量调用通达信公式无需使用formula\_set\_data和formula\_set\_data\_info提前设置，formula\_set\_data和formula\_set\_data\_info的设置也对批量调用不生效

```python
#批量调用选股公式
def formula_process_mul_xg(formula_name: str = '',
    formula_arg: str = '',
    return_count: int = 1,
    return_date:bool = False,
    stock_list: List[str] = [],
    stock_period: str = '1d',
    start_time: str = '',
    end_time: str = '',
    count: int = 0,
    dividend_type: int = 0):
#批量调用指标公式
def formula_process_mul_zb(formula_name: str = '',
    formula_arg: str = '',
    xsflag: int = -1,
    return_count: int = 1,
    return_date:bool = False,
    stock_list: List[str] = [],
    stock_period: str = '1d',
    start_time: str = '',
    end_time: str = '',
    count: int = 0,
    dividend_type: int = 0): 
```

输入参数

<table><tr><td>参数</td><td>是否必选</td><td>参数类型</td><td>参数说明</td></tr><tr><td>formula_name</td><td>Y</td><td>str</td><td>公式名称</td></tr><tr><td>formula_arg</td><td>Y</td><td>str</td><td>公式参数</td></tr><tr><td>xsflag</td><td>Y</td><td>int</td><td>数据精度</td></tr><tr><td>retrun_count</td><td>Y</td><td>int</td><td>设置每个返回值的返回数</td></tr><tr><td>formula_arg</td><td>Y</td><td>bool</td><td>设置是否返回日期</td></tr><tr><td>stock_list</td><td>Y</td><td>List[str]</td><td>股票代码列表</td></tr><tr><td>stock_period</td><td>Y</td><td>str</td><td>K线周期</td></tr><tr><td>start_time</td><td>Y</td><td>str</td><td>起始时间</td></tr><tr><td>end_time</td><td>Y</td><td>str</td><td>结束时间</td></tr><tr><td>count</td><td>Y</td><td>int</td><td>截取K线数量</td></tr><tr><td>dividend_type</td><td>Y</td><td>int</td><td>复权类型</td></tr></table>

需要先在下载对应的盘后数据  
dividend\_type的取值为：0不复权 1前复权 2后复权

当count为0时，start\_time和end\_time生效，指定K线为对应时间段内  
count最大值为24000，count为-1时为获取对应股票全部K线  
正常每个返回值的数据个数应该与count相同，但是return\_count可以限制返回个数，去掉用不到的数据，以此提高能够返回的有效数据量；对于选股和多股指标排行场景，一般只需要返回最后一个数据进行判断股票是否选中或显示最后一个指标数据，return\_count为1就可以。  
xsflag小于0时返回默认精度，最大可返回8位小数。

接口使用  
```python
from tqcenter import tq
tq.initialize(__file__)
#批量调用UPN 选股公式
mul_xg_res = tq.formula_process_mul_xg(
    formula_name='UPN',
    formula_arg='3',
    return_count=3,
    return_date=True,
    stock_list=['688318.SH','600519.SH','000001.SZ'],
    stock_period='1d',
    count=5,
    dividend_type=1)
print(mul_xg_res)

#批量调用CYX 指标公式
mul_zb_res = tq.formula_process_mul_zb(
    formula_name='CYX',
    formula_arg='12',
    return_count=3,
    return_date=True,
    stock_list=['688318.SH','600519.SH','000001.SZ'],
    stock_period='1d',
    count=5,
    dividend_type=1)
print(mul_zb_res) 
```

数据样本  
```txt
{'000001.SZ': {'UP3': [{ 'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '0'}, {'Date': '20260205', 'Value': '0'}]},
'600519.SH': {'UP3': [{ 'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '1'}, {'Date': '20260205', 'Value': '1'}]},
'688318.SH': {'UP3': [{ 'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '0'}, {'Date': '20260205', 'Value': '0'}]}, 'ErrorId': '0'}}
{'000001.SZ': {'NOTEXT1': [{ 'Date': '20260203', 'Value': '11.06'}, {'Date': '20260204', 'Value': '11.08'}, {'Date': '20260205', 'Value': '11.11'}], 'NOTEXT2': [{ 'Date': '20260203', 'Value': '10.85'}, {'Date': '20260204', 'Value': '10.91'}, {'Date': '20260205', 'Value': '10.96'}], 'OUTPUT1': ['全国性银行 深圳板块 跨境支付C IPS ']},
'600519.SH': {'NOTEXT1': [{ 'Date': '20260203', 'Value': '1494.05'}, {'Date': '20260204', 'Value': '1529.5 3'}, {'Date': '20260205', 'Value': '1565.00'}], 'NOTEXT2': [{ 'Date': '20260203', 'Value': '1446.08'}, {'Date': '20260204', 'Value': '1480.54'}, {'Date': '20260205', 'Value': '1515.00'}], 'OUTPUT1': ['酿酒 贵州板块 通达信88 白酒概念 ']},
'688318.SH': {'NOTEXT1': [{ 'Date': '20260203', 'Value': '136.60'}, {'Date': '20260204', 'Value': '135.30'}, 
```

← 调用通达信公式进行计算formula\_zb/xg/exp

获取资金账户句柄stock\_account →

市场类型

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>.SZ</td><td>int</td><td>0</td><td>深圳交易所</td></tr><tr><td>.SH</td><td>int</td><td>1</td><td>上海交易所</td></tr><tr><td>.BJ</td><td>int</td><td>2</td><td>北京交易所</td></tr><tr><td>.NQ</td><td>int</td><td>44</td><td>新三板</td></tr><tr><td>.SHO</td><td>int</td><td>8</td><td>上海个股期权</td></tr><tr><td>.SZO</td><td>int</td><td>9</td><td>深圳个股期权</td></tr><tr><td>.HK</td><td>int</td><td>31</td><td>香港交易所</td></tr><tr><td>.US</td><td>int</td><td>74</td><td>美国股票</td></tr><tr><td>.CSI</td><td>int</td><td>62</td><td>中证指数</td></tr><tr><td>.CNI</td><td>int</td><td>102</td><td>国证指数</td></tr><tr><td>.HG</td><td>int</td><td>38</td><td>国内宏观指标</td></tr><tr><td>.CFF</td><td>int</td><td>47</td><td>中金期货</td></tr><tr><td>.CZC</td><td>int</td><td>28</td><td>郑州期货</td></tr><tr><td>.DCE</td><td>int</td><td>29</td><td>大连期货</td></tr><tr><td>.SHF</td><td>int</td><td>30</td><td>上海期货</td></tr><tr><td>.GFE</td><td>int</td><td>66</td><td>广州期货</td></tr><tr><td>.INE</td><td>int</td><td>30</td><td>上海能源</td></tr><tr><td>.HI</td><td>int</td><td>27</td><td>港股指数</td></tr><tr><td>.OF</td><td>int</td><td>33</td><td>开放式基金净值</td></tr><tr><td>.CFFO</td><td>int</td><td>7</td><td>中金所期权</td></tr><tr><td>.CZCO</td><td>int</td><td>4</td><td>郑州期货期权</td></tr><tr><td>.DCEO</td><td>int</td><td>5</td><td>大连期货期权</td></tr><tr><td>.SHFO</td><td>int</td><td>6</td><td>上海期货期权</td></tr><tr><td>.GFEO</td><td>int</td><td>67</td><td>广州期货期权</td></tr></table>

dividend\_type复权类型

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>type</td><td>str</td><td>none</td><td>不复权</td></tr><tr><td>type</td><td>str</td><td>front</td><td>前复权</td></tr><tr><td>type</td><td>str</td><td>back</td><td>后复权</td></tr></table>

period周期入参类型

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>period</td><td>str</td><td>1m</td><td>1分钟</td></tr><tr><td>period</td><td>str</td><td>5m</td><td>5分钟</td></tr><tr><td>period</td><td>str</td><td>15m</td><td>15分钟</td></tr><tr><td>period</td><td>str</td><td>30m</td><td>30分钟</td></tr><tr><td>period</td><td>str</td><td>1h</td><td>60分钟(1小时)</td></tr><tr><td>period</td><td>str</td><td>1d</td><td>1天</td></tr><tr><td>period</td><td>str</td><td>1w</td><td>1周</td></tr><tr><td>period</td><td>str</td><td>1mon</td><td>1月</td></tr><tr><td>period</td><td>str</td><td>1q</td><td>1季</td></tr><tr><td>period</td><td>str</td><td>1y</td><td>1年</td></tr><tr><td>period</td><td>str</td><td>tick</td><td>分笔</td></tr></table>

order\_type类型

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>STOCK_BUY</td><td>int</td><td>0</td><td>买</td></tr><tr><td>STOCK_SELL</td><td>int</td><td>1</td><td>卖</td></tr><tr><td>CREDIT_BUY</td><td>int</td><td>0</td><td>担保品买入</td></tr><tr><td>CREDIT_SELL</td><td>int</td><td>1</td><td>担保品卖出</td></tr><tr><td>CREDIT_FIN_BUY</td><td>int</td><td>69</td><td>融资买入</td></tr><tr><td>CREDIT_SLO_SELL</td><td>int</td><td>70</td><td>融券卖出</td></tr></table>

price\_type类型

<table><tr><td>名称</td><td>类型</td><td>数值</td><td>说明</td></tr><tr><td>PRICE_MY</td><td>int</td><td>0</td><td>自填价</td></tr><tr><td>PRICE_SJ</td><td>int</td><td>1</td><td>市价</td></tr><tr><td>PRICE_ZTJ</td><td>int</td><td>2</td><td>涨停价/笼子上限</td></tr><tr><td>PRICE_DTJ</td><td>int</td><td>3</td><td>跌停价/笼子下限</td></tr></table>

<table><tr><td>WTSTATUS_NULL</td><td>int</td><td>0</td><td>无效单</td></tr><tr><td>WTSTATUS_NOCJ</td><td>int</td><td>1</td><td>未成交</td></tr><tr><td>WTSTATUS_PARTCJ</td><td>int</td><td>2</td><td>部分成交</td></tr><tr><td>WTSTATUS_ALLCJ</td><td>int</td><td>3</td><td>全部成交</td></tr><tr><td>WTSTATUS_BCBC</td><td>int</td><td>4</td><td>部分成交部分撤单</td></tr><tr><td>WTSTATUS_ALLCD</td><td>int</td><td>5</td><td>全部撤单</td></tr></table>

← 撤单cancel\_order\_stock

回测及模拟交易 →

# 什么是量化交易

量化交易是指利用计算机科技并采用一定的数学模型去实现投资理念、实现投资策略的过程。简单的说，量化交易主要是做这样的事：

一个简单的投资想法 => 可执行的交易策略 => 可执行的代码程序 => 检验交易策略效果 => 实盘交易验证改进

# Step 1：从一个简单的投资想法开始

投资想法即我们认为可能会盈利的投资方法、理念，比如熊市时期银行股是潜力股、复制基金经理的增强指数、金叉买入死叉卖出等等。这些想法通常以网络、书本和讲座等为载体，来源于投顾、同行以及自己的经验总结等等。

以一个简单的投资想法为例：

1 如果遇到股价金叉，则买入  
2 如果遇到股价死叉，则卖出

py

# Step 2：完善这个想法，形成明确的可执行的交易策略

简单的投资想法通常比较模糊，我们需要将其细化成明确的可执行的策略，目的是为了能得到确定的信号进行交易操作。

一个可执行的交易策略至少需要明确以下几点:

1. Security：确定投资品种或范围   
2. Condition：确定触发买/卖的具体条件  
3. Quantity：确定买卖的数量/金额等

明确的可执行的交易策略的判断基准：根据交易策略的描述，不同的人在相同情形下，都能做出相同的交易操作。

上述关于金叉死叉的投资想法，显然它是不够明确的（可度量/可计算）。所以我们进一步细化：

1 监测沪深300指数的所有成分股的收盘价  
2 如果收盘价上穿收盘价的5日简单移动平均，则用全部可用资金买入该股票  
3 如果收盘价的5日简单移动平均上穿收盘价，则卖出该股票所有持仓

现在，我们基本已经把之前的想法细化成了明确的可执行的交易策略。当然，可能还有些地方不够明确或者参数需要改动，这些可以随时想到随时修正，不必一次做到完美。

# 现在，我们想知道这样操作究竟会不会赚钱？

# Step 3：编写一段代码，把交易策略转成可执行的代码程序

为了验证这个策略是否赚钱，我们需要把明确后的交易策略通过编程转成程序，计算机能根据历史数据/实时数据执行该策略产生模拟交易，或者根据实时数据执行该策略产生实盘交易。

把上述策略翻译成计算机可以识别的代码语言，即类似这样的代码：

1   
import pandas as pd2   
3 import vectorbt as vbt   
4 from tqcenter import tq

py

```python
# 解决 'panda's future warning
pd.set_option('future.no_silent_downcasting', True)

# ---- 核心配置（用户可直接修改这里）----
target_start = '20240930'  # 【目标回测开始时间】（真正想回测的起始日）
target_end = '20250930'  # 【目标回测结束时间】
stock_code_list = ['688318.SH']    # 股票代码
window = 5    # MA指标周期（如MA5、MA10、MA20，改这里自动适配历史数据）
# ----

start_time = (pd.to_datetime(target_start) - pd.Timedelta(days=window + 10)).strftime('%Y%m%d')

# 1.获取价格数据
df_real = tq.get_market_data(
    field_list=['Close', 'Open'],
    stock_list=stock_code_list,
    start_time=start_time,
    end_time=target_end,
    dividend_type='front',
    period='1d',
    fill_data=True
)
close_df = tq.price_df(df_real, 'Close', column_names=stock_code_list)
open_df = tq.price_df(df_real, 'Open', column_names=stock_code_list)

# 2.买卖信号计算与生成
ma5_dynamic = vbt.MA.run(close_df, window=window).ma
ma5_dynamic.columns = close_df.columns

entries_raw = close_df.vbt.crossed_above(ma5_dynamic)
exits_raw = close_df.vbt.crossed_below(ma5_dynamic)

# 信号移位+1
entries_df = entries_raw.shift(1).fillna(False).astype(bool)
exits_df = exits_raw.shift(1).fillna(False).astype(bool)

# 3.执行回测
portfolio = vbt.Portfolio.from_signals(
    close=close_df,    # 净值计算用未复权收盘价
    entries=entries_df,    # 延迟后的买入信号
    exits=exits_df,    # 延迟后的卖出信号
    price=open_df,    # 含滑点的成交价格
    init_cash=100000,    # 初始资金10万元
    fees=0.0003,    # 手续费0.03%（双边）
    freq='D',    # 日线频率
    size_granularity=100    # A股最小交易单位100股
)

# 4.输出回测结果
print(f"\n====投资组合回测表现====")
print(portfolio.stats())
print(f"\n====投资组合回测记录====")
print(portfolio.trades.records_readable) 
```

这样一来，刚才细化好的策略转成了代码，计算机就能理解并执行了。

# Step 4：回测或者模拟交易，检验策略效果

基本的检验策略方法有回测和模拟交易两种方法。核心区别是：回测是用历史数据模拟执行策略，模拟交易是用未来的实际数据模拟执行策略。。

\*\*回测是让计算机能根据一段时间区间内的历史的数据来模拟执行该策略，根据结果评价并改进策略。\*\*如果结果不好，则需要分析原因并改进。如果结果不错，则可以考虑用模拟交易进一步验证。

\*\*模拟交易是让计算机能根据未来的实际数据模拟执行该策略一段时间区间，根据结果评价并改进策略。\*\*如果策略在回测与模拟交易的表现都非常好，我们可以考虑进行完全真金白银的实盘交易。

# 回测举例说明：

1. 策略环境：设定初始虚拟资产100万元；选择一段历史时间区间：20100101到20200101；把该时间区间的各种数据如收盘股价行情等发给计算机。  
2. 策略执行：计算机利用这些数据模仿历史真实的市场，执行我们编写的策略程序。  
3. 策略评估：计算机会出具一份报告，根据这个报告我们知道，在20100101期初的100万元，按照我们的策略交易到期末20200101，会怎样？一般包括盈亏情况，下单情况，持仓变化，以及一些统计指标等，根据此评估交易策略的好坏。

# 模拟交易举例说明：

1. 策略环境：设定初始的虚拟资产比如100万元，选择开始执行模拟交易的时间点，比如下周一。那么从下周一开始，股市开始交易，真实的行情数据就会实时地发送到计算机。  
2. 策略执行：计算机利用真实的数据模仿真实的市场，执行你的策略代码输出买卖队列，模拟系统会记录每一笔买卖记录。  
3. 策略评估：我们可以得到一份实时更新的策略评估报告，这报告类似于回测得到的报告，不同的是会根据实际行情变化更新；同样我们能据此评估交易策略的好坏。

# Step 5：实盘执行交易策略，并持续优化改进策略

实盘交易就是让计算机能根据实际行情，用真实资金账号来自动下单交易。注意，这时不再是用虚拟资产进行模拟交易，实盘交易账户上的盈亏都是真金白银。

实盘交易一般也会给出一份类似模拟交易的投资分析报告，通过实时观察策略的实盘表现、根据投资理念的变化、市场状况的变化及时修正、改善和优化策略，使之保持持续盈利能力。

# 执行选股策略并加入客户端自定义板块

第一步：执行选股策略  
```python
import pandas as pd
import numpy as np
from datetime import datetime
from tqcenter import tq

# 初始化tq
tq.initialize(__file Dynamic)

# 1. 基础配置（可修改项）
batch_codes = tq.get_stock_list_in_sector('通达信88')    # 目标板块
start_time = "20251025"    # 数据起始日期
target_end = datetime.now().strftime("%Y%m%d")    # 数据结束日期（当前日期）
N = 3    # 目标连续上涨天数
block_code = 'LZXG'    # 自定义板块简称（必选）
block_name = '连涨选股'    # 自定义板块名称（必选）

# 2. 获取并整理收盘价数据
df_real = tq.get_market_data(
    field_list=['Close'], 
    stock_list=batch_codes,
    start_time=start_time,
    end_time=target_end,
    dividend_type='front',    # 前复权
    period='1d',    # 日线
    fill_data=True    # 填充缺失数据
)

# 转换为「日期×股票代码」的收盘价宽表
close_df = tq.price_df(df_real, 'Close', column_names=batch_codes)

# 3. 标记每日是否上涨（核心判断逻辑）
is_up = close_df > close_df.shift(1)    # True=当日上涨，False=当日非上涨

# 4. 核心：计算连续上涨天数
# 步骤1：上涨日标记为1，非上涨日标记为NaN
up_mask = np.where(is_up, 1, np.nan)
up_mask_df = pd.DataFrame(up_mask, index=close_df.index, columns=close_df.columns)

# 步骤2：前向填充 → 连续上涨阶段的非上涨日（NaN）会被1填充
filled_df = up_mask_df.ffill()

# 步骤3：累计非NaN值的数量（初步计数）
consec_up_days = filled_df.notna().cumsum()

# 步骤4：非上涨日重置计数（关键步骤，实现“连续”效果）
reset_counts = consec_up_days.where(~is_up).ffill().fillna(0)
consec_up_days = (consec_up_days - reset_counts).astype(int)

# 5. 筛选符合条件的股票（连续上涨≥N天）
latest_date = consec_up_days.index[-1]    # 最新交易日
latest_consec_up = consec_up_days.loc[Latest_date]    # 每只股票最新的连续上涨天数
target_stocks = latest_consec_up[Latest_consec_up >= N].sort_values(ascending=False)
target_stocks_list = target_stocks.index.tolist()    # 提取符合条件的股票代码列表 
```

```python
# 第一步：创建自定义板块
try:
    tq.create_sector(block_code=block_code, block_name=block_name)
    print(f"✓ 已成功创建自定义板块「{block_name}（{block_code})」")
except Exception as e:
    # 板块已存在时可能报错，此处捕获异常不中断流程
    print(f"☐ 自定义板块创建提示：{e}（若提示已存在，可忽略此信息）")

# 第二步：处理板块成份股（添加/清空）
if not target_stocks.empty:
    # 打印筛选结果
    print(f"符合条件的股票共 {len(target_stocks)} 只：")
    for stock_code, days in target_stocks.items():
    print(f"{stock_code}: 连续上涨 {days} 天")

    # 发送至自定义板块
    try:
    tq.send_user_block(block_code=block_code, stocks=target_stocks_list)
    print(f"\n✓ 已成功将股票添加至自定义板块「{block_name}（{block_code})」")
except Exception as e:
    print(f"\n✗ 添加自定义板块失败：{e}")

    # 发送提示消息至TQ策略管理器
    msg = f"MSG, 筛选结果：{start_time}至{target_end}, 连续上涨≥{N}天的股票共{len(target_stocks)}只，已添加至「{block_name}（{block_code})」"
    try:
    tq.send_message(msg)
    print("✓ 提示消息发送成功")
except Exception as e:
    print(f"✗ 消息发送失败：{e}")

else:
    # 无符合条件股票时清空板块
    print("暂无符合条件的股票")
    try:
    tq.send_user_block(block_code=block_code, stocks=[])
    print(f"✓ 已清空自定义板块「{block_name}（{block_code})」")
except Exception as e:
    print(f"✗ 清空自定义板块失败：{e}")

    # 发送空结果提示
    msg = f"MSG, 筛选结果：{start_time}至{target_end}, 连续上涨≥{N}天的股票共0只，已清空「{block_name}（{block_code})」"
    try:
    tq.send_message(msg)
except Exception as e:
    print(f"✗ 消息发送失败：{e}") 
```

第二步：客户端查看执行效果

![](images/c4fe1613a470881c98023974e319f24dbf18617c28e2f0997576eceacbd3d941.jpg)

<details>
<summary>bar</summary>

| Category | Value |
|---|---|
| 炼金矿业 | 601899 |
| 焦金矿业 (中国) | 5.12 |
| 焦金矿业 (北京) | 33.67 |
| 焦金矿业 (天津) | 1.64 |
| 焦金矿业 (重庆) | 33.66 |
| 焦金矿业 (上海) | 33.68 |
| 焦金矿业 (广州) | 165.6万 |
| 焦金矿业 (武汉) | 436 |
| 焦金矿业 (安徽) | 0.03 |
| 焦金矿业 (河北) | 0.80 |
| 焦金矿业 (浙江) | 32.60 |
| 焦金矿业 (四川) | 33.77 |
| 焦金矿业 (吉林) | 32.55 |
| 焦金矿业 (甘肃) | 32.03 |
| 焦金矿业 (河南) | 17.73 |
| 焦金矿业 (福建) | 54.8亿 |
| 焦金矿业 (广东) | 2.01 |
| 焦金矿业 (安徽) | 铜 |
| 焦金矿业 (湖北) | 福建 |
| 焦金矿业 (甘肃) | 3.81 |
| 焦金矿业 (云南) | 33.10 |
| 焦金矿业 (河北) | 591167 |
| 焦金矿业 (上海) | 106.5万 |
| 焦金矿业 (天津) | 0.56 |
| 焦金矿业 (河北) | 0.00 |
| 焦金矿业 (福建) | 226 |
| 焦金矿业 (广东) | 19 |
</details>

分类主力资 上证3975.7816.16041%4894亿深证13659.9818.57.95%7186亿北证1470732770.88%5.6亿创业3262112.77070%327亿科创1353.6 科创 板块 4.550.34%251.3亿沪深4672.6830.140.65%2550亿总成交12195亿高级行情深圳双线3

← 回测及模拟交易

订阅行情涨幅突破实时预警 →

# 订阅行情涨幅突破实时预计

第一步：设置预警条件，并发送预警结果到客户端  
```python
#订阅板块成分股行情，涨幅突破实时预警，首次突破后取消该证券行情订阅监控
import json
import time
import signal
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from tqcenter import tq

# ---- 全局配置 ----
# 板块配置：支持多个板块/自定义板块
SECTOR_NAMES = ['通达信88']  # 可扩展为其他板块名称或代码
PRICE_RISE_THRESHOLD = 5.0  # 涨幅阈值>5%
ANTI_SHAKE_SECONDS = 10    # 防抖间隔
BATCH_SUBSCRIBE_SIZE = 50    # 分批订阅大小（避免单次订阅过多）

# 全局变量
SUBSCRIBE_CODES = []    # 动态获取的监控股票列表
last_warn_time = defaultdict(int)
EXIT_FLAG = False
TRIGGERED_STOCKS = set()    # 记录已首次触发预警的股票（避免重复监控/推送）

# ---- 信号处理函数 ----
def signal_handler(signum, frame):
    """处理Ctrl+C (SIGINT) 信号"""
    global EXIT_FLAG
    print(f"\n\n[{datetime.now().strftime('%H:%M:%S')} 接收到退出信号（Ctrl+C），开始清理资源..")
    EXIT_FLAG = True
    # 强制取消订阅+关闭TDX
    try:
    unsubscribe_stocks()
    except Exception as e:
    print(f"取消订阅失败：{e}")

    print("资源清理完成，程序退出！")
    sys.exit(0)

# ---- 工具函数（新增） ----
def get_valid_stock_codes(sector_names):
    """
    从指定板块获取有效股票代码列表
    :param sector_names: 板块名称列表
    :return: 去重后的有效股票代码列表
    """
    valid_codes = set()  # 用集合去重
    for sector in sector_names:
    try:
    # 获取板块股票列表（TDX初始化后调用）
    sector_codes = tq.get_stock_list_in_sector(sector)
    if not sector_codes:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 警告：板块{sector}未获取到股票列表")
    continue
```

```python
if code and instance(code, set) and (code:endwith(1:%H)% of code:endwith(1:%2)):
    valid_codes.add(code)
    else:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 过滤无效代码：{code}")

except Exception as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取板块{sector}股票列表失败：{e}")
    import traceback
    traceback.print_exc()

# 转为列表并排序
valid_codes_list = sorted(list(valid_codes))
print(f"[{datetime.now().strftime('%H:%M:%S')}] 从板块{sector_names}获取到有效股票{len(valid_codes_list)}
只：{valid_codes_list[:10]}...") # 只打印前10个
return valid_codes_list

def batch_subscribe(stocks, batch_size):
    """
    分批订阅股票（避免单次订阅过多）
    :param stocks: 股票列表
    :param batch_size: 每批订阅数量
    :return: 整体订阅结果 (True/False)
    """

    total_success = True
    for i in range(0, len(stocks), batch_size):
    batch = stocks[i:i+batch_size]
    try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 订阅第{i//batch_size + 1}批股票（{len(batch)}只）：{batch[:5]}...")
    sub_res = tq.subscribe_hq(stock_list=batch, callback=price_rise_callback)
    if not sub_res:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅失败：{sub_res}")
    total_success = False
    else:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅成功：{sub_res}")
    except Exception as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅异常：{e}")
    total_success = False
    return total_success

def unsubscribe_single_stock(stock_code):
    """
    取消单只股票的订阅（首次触发后不再监控）
    :param stock_code: 股票代码
    :return: 取消结果 (True/False)
    """

    try:
    un_sub_res = tq unsubscribe_hq(stock_list=[stock_code])
    if un_sub_res:
    # 从全局订阅列表中移除
    if stock_code in SUBSCRIBE_CODES:
    SUBSCRIBE_CODES.remove(stock_code)
    return True
    return False
    except Exception as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 取消{stock_code}订阅失败：{e}")
    return False

# ---- 核心回调函数 ----
def price_rise_callback(data_str): 
```

```python
# 前置过滤：无效数据/非监控股票/已触发过的股票（直接返回，不输出日志）
if (code_json.get('ErrorId') != "0" or not code) or \
  (code not in SUBSCRIBE_CODES) or \
  (code in TRIGGERED_STOCKS):
    return

# 获取最新行情数据
report_ptr = tq.get_full_tick(code)

latest_price = 0.0
pre_close = 0.0

if report_ptr:
    latest_price = round(float(report_ptr['Now']), 2)
    pre_close = round(float(report_ptr['LastClose']), 2)

    if pre_close <= 0 and latest_price > 0:
    pre_close = latest_price - 0.01

# 过滤最新价/昨收价无效的情况
if latest_price <= 0 or pre_close <= 0:
    return

# 计算涨幅
rise_rate = round(((latest_price - pre_close) / pre_close) * 100, 2) if pre_close > 0 else 0.0

# 仅处理满足涨幅阈值+防抖的情况
if rise_rate > PRICE_RISE_THRESHOLD:
    current_time = int(time.time())
    if current_time - last_warn_time[code] < ANTI_SHAKE_SECONDS:
    return

    # 标记为已触发，后续不再处理
    TRIGGERED_STOCKS.add(code)
    last_warn_time[code] = current_time

    # 取消该股票的订阅（不再监控）
    unsubscribe_single_stock(code)

    # 发送预警
    warn_time = datetime.now().strftime("%Y%m%d%H%M%S")
    reason = (
    f"涨幅突破"
    )

    try:
    # 成交量用实际值，无则填0
    volume = report_ptr.get('Volume', '0') if report_ptr else '0'
    warn_res = tq.send_warn(
    stock_list=[code],
    time_list=[warn_time],
    price_list=[str(latest_price)],
    close_list=[str(pre_close)],
    volum_list=[volume],
    bs_flag_list=['0'],
    warn_type_list=['3'],
    reason_list=[reason],
    count=1 
```

```python
print(f"[{datetime.now().strftime('%H:%M:%S')} ] 拨署发送结束：[Bar1-35] )
    print(f"[{datetime.now().strftime('%H:%M:%S')} ] 已取消{code}订阅，后续不再监控")
except Exception as e:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')} ] {code} 发送预警失败：{e}")

except Exception as e:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')} ] 回调函数执行异常：{e}")
    import traceback
    traceback.print_exc()

return None

# ---- 订阅/取消订阅函数----
def subscribe_stocks():
    """订阅股票（分批订阅+容错）"""
    if not SUBSCRIBE_CODES:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')} ] 无有效股票可订阅，跳过订阅流程")
    return False

print(f"\n开始批量订阅股票（总计{len(SUBSCRIBE_CODES)}只）")
sub_result = batch_subscribe(SUBSCRIBE_CODES, BATCH_SUBSCRIBE_SIZE)
print(f"批量订阅最终结果：{'成功' if sub_result else '部分/全部失败'}")
return sub_result

def unsubscribe_stocks():
    """取消订阅（分批取消）"""
    if not SUBSCRIBE_CODES:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')} ] 无已订阅股票，跳过取消订阅流程")
    return False

print(f"\n开始批量取消订阅股票（总计{len(SUBSCRIBE_CODES)}只）")
total_success = True
for i in range(0, len(SUBSCRIBE_CODES), BATCH_SUBSCRIBE_SIZE):
    batch = SUBSCRIBE_CODES[i:i+BATCH_SUBSCRIBE_SIZE]
    try:
    print(f"取消第{i//BATCH_SUBSCRIBE_SIZE + 1}批订阅：{batch[:5]}...")
    un_sub_ptr = tq. unsubscribe_hq(stock_list=batch)
    if not un_sub_ptr:
    print(f"第{i//BATCH_SUBSCRIBE_SIZE + 1}批取消失败：{un_sub_ptr}")
    total_success = False
    except Exception as e:
    print(f"第{i//BATCH_SUBSCRIBE_SIZE + 1}批取消异常：{e}")
    total_success = False
print(f"批量取消订阅最终结果：{'成功' if total_success else '部分/全部失败'}")
return total_success

# ---- 主程序 ----
if __name__ == "__main__":
    # 注册SIGINT信号处理（优先于默认的KeyboardInterrupt）
signal.signal(signal.SIGINT, signal_handler)

# 1. 初始化TDX（仅执行1次，无重试）
try:
    tq.initialize(__file____)
    print(f"程序启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"TDX初始化成功")
except Exception as e:
    print(f"TDX初始化失败：{e}")
    exit(1) 
```

```python
print("未获取到任何有效股票代码，程序退出")
exit(1)

# 3. 订阅股票
subscribe_stocks()

# 4. 运行提示
print(f"\n=== 涨幅监控启动 ===")
print(f"监控板块：{SECTOR_NAMES}")
print(f"监控股票总数：{len(SUBSCRIBE_CODES)}")
print(f"涨幅阈值：>{PRICE_RISE_THRESHOLD}%")
print(f"防抖间隔：{ANTI_SHAKE_SECONDS}秒")
print(f"分批订阅大小：{BATCH_SUBSCRIBE_SIZE}只/批")
print("按 Ctrl+C 退出程序...\n")

# 5. 通过全局标记控制退出
try:
    while not EXIT_FLAG:
    time.sleep(0.1)
except Exception as e:
    print(f"主循环异常：{e}")
    # 兜底清理
    unsubscribe_stocks()
```

# 第二步：打开通达信金融终端查看运行结果

# 通达信金融终端

<table><tr><td>代码</td><td>名称</td><td>涨幅%</td><td>现价</td><td>涨跌</td><td>买价</td><td>卖价</td><td>总量</td><td>现量</td><td>涨速%</td><td>换手%</td><td>今开</td><td>最高</td><td>最低</td><td>昨收</td><td>市盈动</td><td>总金额</td><td>量比</td><td>细分行业</td><td>地区</td><td>振幅%</td><td>均价</td><td>内盘</td><td>外盘</td><td>内外比</td><td>溢价%</td><td>买量</td><td>卖量?</td></tr><tr><td>300699</td><td>光威复材</td><td>8.02</td><td>34.74</td><td>2.58</td><td>34.74</td><td>34.75</td><td>872417</td><td>47</td><td>-0.31</td><td>10.62</td><td>33.33</td><td>36.66</td><td>33.13</td><td>32.16</td><td>52.21</td><td>38.3亿</td><td>5.36</td><td>碳纤维</td><td>山东</td><td>10.98</td><td>34.77</td><td>356066</td><td>516351</td><td>0.69</td><td>0.00</td><td>44</td><td>1</td></tr><tr><td>300274</td><td>阳光电源</td><td>7.28</td><td>180.10</td><td>12.22</td><td>180.10</td><td>180.13</td><td>100.3万</td><td>235</td><td>-0.51</td><td>6.31</td><td>169.88</td><td>185.18</td><td>168.85</td><td>167.88</td><td>23.57</td><td>178.8亿</td><td>3.16</td><td>光伏逆变器</td><td>安徽</td><td>9.73</td><td>178.37</td><td>400881</td><td>602491</td><td>0.66</td><td>0.00</td><td>6</td><td>8</td></tr><tr><td>603993</td><td>洛阳钼业</td><td>5.45</td><td>19.72</td><td>1.02</td><td>19.71</td><td>19.72</td><td>201.7万</td><td>120</td><td>0.05</td><td>1.15</td><td>19.04</td><td>19.99</td><td>18.98</td><td>18.70</td><td>22.16</td><td>39.3亿</td><td>1.71</td><td>铬钼</td><td></td><td>5.40</td><td>19.54</td><td>776394</td><td>123.7万</td><td>0.63</td><td>0.00</td><td>302</td><td>7</td></tr><tr><td>601899</td><td>紫金矿业</td><td>4.78</td><td>33.56</td><td>1.53</td><td>33.55</td><td>33.56</td><td>215.7万</td><td>64</td><td>0.06</td><td>1.05</td><td>32.60</td><td>33.77</td><td>32.55</td><td>32.03</td><td>17.68</td><td>71.6亿</td><td>1.70</td><td>铜</td><td></td><td>3.01</td><td>33.20</td><td>834416</td><td>132.3万</td><td>0.63</td><td>0.00</td><td>146</td><td>48</td></tr><tr><td>605090</td><td>九丰能源</td><td>3.04</td><td>41.98</td><td>1.24</td><td>41.97</td><td>41.98</td><td>434120</td><td>40</td><td>0.00</td><td>6.26</td><td>40.75</td><td>43.95</td><td>40.75</td><td>40.74</td><td>17.64</td><td>18.5亿</td><td>1.99</td><td>燃气</td><td></td><td>7.85</td><td>42.56</td><td>202554</td><td>231566</td><td>0.87</td><td>0.00</td><td>155</td><td></td></tr></table>

上证3962.42 2  
国

# 计算调仓信号并快速买卖

第一步：计算信号并发送预警，以  
```python
from datetime import datetime, timedelta
from tqcenter import tq as tdxdata
import vectorbt as vbt
import pandas as pd

# 初始化
tdxdata.initialize(__file__)
run_time = datetime.now()
run_time_str = run_time.strftime("%Y-%m-%d %H:%M:%S")
# 预警时间戳（格式：YYYYMMDDHHMMSS）
warn_time = run_time.strftime("%Y%m%d%H%M%S")

# =================--------- 1. 配置参数 =================---------
N = 5 # 均线周期
batch_codes = tdxdata.get_stock_list_in_sector('通达信88')
end_date = run_time.strftime("%Y%m%d")
start_date = (run_time - timedelta(days=2 * N + 20)).strftime("%Y%m%d")

# =================--------- 2. 获取并处理数据 =================---------
# 获取日线Close数据（保留完整索引用于日期筛选）
df_real = tdxdata.get_market_data(
    field_list=['Close'],
    stock_list=batch_codes,
    start_time=start_date,
    end_time=end_date,
    dividend_type='front',
    period='1d',
    fill_data=True
)
close_df = tdxdata.price_df(df_real, 'Close', column_names=batch_codes)

# 计算均线+生成信号
ma = vbt.MA.run(close_df, window=N).ma
ma.columns = close_df.columns
entries = close_df.vbt.crossed_above(ma) # 上穿（买入）
exits = close_df.vbt.crossed_below(ma) # 下穿（卖出）
latest_date = close_df.index[-1] # 今日日期（DataFrame最后一行）
# 获取上一个工作日日期
prev_date = close_df.index[-2] if len(close_df.index) >= 2 else latest_date

# =================--------- 3. 筛选最新买卖信号 =================---------
buy_signals = {}
sell_signals = {}

# 遍历股票筛选信号
for code in batch_codes:
    # 确保股票有足够的交易数据
    if code not in close_df.columns:
    continue

    # 今日收盘价
today_close = close_df.loc[Latest_date, code]
# 上一个工作日收盘价 
```

```python
# 关入信号：最新日期Close上穿均线
if entries.loc[Latest_date, code]:
    buy_signals[code] = {
    'today_close': round(today_close, 2),    # 今日close
    'prev_close': round(prev_close, 2),    # 上一个工作日close
    'ma_price': round(ma.loc[Latest_date, code], 2)
    }
# 卖出信号：最新日期Close下穿均线
if exits.loc[Latest_date, code]:
    sell_signals[code] = {
    'today_close': round(today_close, 2),    # 今日close
    'prev_close': round(prev_close, 2),    # 上一个工作日close
    'ma_price': round(ma.loc[Latest_date, code], 2)
    }
# =================== 4. 生成并发送MSG ===================
def send_msg(content):
    msg = f"MSG,{content}"
    print(msg)
    try:
    tdxdata.send_message(msg)
    except Exception as e:
    print(f"发送失败：{e}")
# 统计行
stat_line = (
    f"运行时间：{run_time_str}, 均线周期：{N}天, "
    f"买入信号数：{len(buy_signals)} 只，卖出信号数：{len(sell_signals)} 只"
)

print("\n== MSG格式 (TQ策略管理器显示区域) ===")
send_msg(stat_line)

# 处理买入信号
if buy_signals:
    send_msg(f"=== 买入信号 (Close上穿{N}日均线) ===")
    for idx, (code, info) in enumerate(buy_signals.items(), 1):
    line = f"{idx}. {code}: 买入信号，今日Close:{info['today_close']}，昨日Close:{info['prev_close']}"
    send_msg(line)

# 处理卖出信号
if sell_signals:
    send_msg(f"=== 卖出信号 (Close下穿{N}日均线) ===")
    for idx, (code, info) in enumerate(sell_signals.items(), 1):
    line = f"{idx}. {code}: 卖出信号，今日Close:{info['today_close']}，昨日Close:{info['prev_close']}"
    send_msg(line)

# 无信号的情况
if not buy_signals and not sell_signals:
    send_msg(f"运行时间：{run_time_str}, 均线周期：{N}天，无买入或卖出信号")

# =================== 5. 调用send_warn接口发送预警 ===================
def send_trade_warn():
    """发送买卖信号对应的预警（精简版，仅保留核心逻辑）"""
    # 合并所有信号用于发送预警
    all_signals = []
    if buy_signals:
    all_signals.extend([(code, info, '买入') for code, info in buy_signals.items()])
    if sell_signals:
    all_signals.extend([(code, info, '卖出') for code, info in sell_signals.items())]) 
```

```python
print(“n无预警信息需要发送”)
return
# 构造预警参数列表
codes = []
time_list = []
price_list = []    # 今日close
close_list = []    # 上一个工作日close
volum_list = []
bs_flag_list = []
warn_type_list = []
reason_list = []

for code, info, trade_type in all_signals:
    codes.append(code)
    time_list.append(warn_time)
    price_list.append(str(info['today_close']))    # 替换为今日close
    close_list.append(str(info['prev_close']))    # 替换为上一个工作日close
    volum_list.append('0')
    bs_flag_list.append('0' if trade_type == '买入' else '1')
    warn_type_list.append('1')
    reason_list.append(f"{trade_type}信号")

# 调用预警接口
try:
    warn_res = tdxdata.send_warn(
    stock_list=codes,
    time_list=time_list,
    price_list=price_list,
    close_list=close_list,
    volum_list=volum_list,
    bs_flag_list=bs_flag_list,
    warn_type_list=warn_type_list,
    reason_list=reason_list,
    count=len(codes)
    )
    print(f"\n预警发送完成，共发送 {len(codes)} 条预警，接口返回：{warn_res}")
except Exception as e:
    print(f"\n预警发送失败：{e}")

# 执行预警发送
send_trade_warn()

print("\n所有消息发送完成！")
tdxdata.close() 
```

第二步:双击TQ策略信号，快速打开闪电买卖，根据输出的买/卖信号打开买/卖界面

![](images/2624bb2930d63f52d9d8b7481438e5bdaf08835995448dee1a353a5edf978b31.jpg)

<details>
<summary>text_image</summary>

运行
断开连接
全部启动
全部断开
宽客论坛
Python编程建议用VSCode或PyCharm
启动外部编辑器
... 
新增策略
修改策略
删除策略
策略名称
文件名称
状态
开始时间
停止时间
数据调用数
交易调用数
输出信息数
策略名称
编程语言
Python
Outside
均线买卖信号_send_w...
停止
09:08:45
09:08:46
89(76.1K)
0
11
TQ策略信号 条数:7
纽威股份 09:08 51.71 0.00% 卖出信号
豪威集团 09:08 126.92 0.00% 卖出信号
东方财富 09:08 23.35 0.00% 卖出信号
豪迈科技 09:08 83.96 0.00% 卖出信号
陕西煤业 09:08 21.68 0.00% 卖入信号
小商品城 09:08 16.29 0.00% 卖入信号
分众传媒 09:08 7.19 0.00% 其入信号
操作v 打开 设置
仅显示当前选中策略的消息
买1.闪电买入
当前用户 模拟操盘(普)-86 113**42
股东代码 深A B0001350442
证券代码 002027 分众传媒 刷
报价方式 限价委托
买入价格 7.19 未锁 元
最大可买 300 全部 股
买入数量 0 股
可买量 1/2 1/3 1/4 1/5 ?
B->S 买入 +
预估金额:0.00(0股)
策略信号 策略数据 保存 重置 文件位置
</details>

← 订阅行情涨幅突破实时预警

结合VBT回测示例 →

VBT简单回测并输出图形  
```python
# 注意：
# 1/目前调用的vectorbt三方库函数vbt.Portfolio.from_signals不支持分红送股等权益变动，该demo仅做示例。

import pandas as pd
import vectorbt as vbt    #VSCODE-终端安装1. pip install vectorbt -i https://pypi.tuna.tsinghua.edu.cn/simple
e    安装2.pip install plotly 用于打印html交互式图形
from tqcenter import tq
from datetime import datetime

tq.initialize(__file__)
# 解决 pandas future warning
pd.set_option('future.no_silent_downcasting', True)
pd.set_option('display.float_format', lambda x: f"{x:.10f}".rstrip('0').rstrip('.') if '.' in f"{x:.10f}" else f"{x}")

# =================-------- 核心配置（用户可直接修改这里）
target_start = '20250701'    # 【目标回测开始时间】（真正想回测的起始日）
target_end = '20251231'    # 【目标回测结束时间】
stock_code_list = ['688318.SH']    # 股票代码
window = 5    # MA指标周期（如MA5、MA10、MA20，改这里自动适配历史数据）
# =================----------------
start_time = (pd.to_datetime(target_start) - pd.Timedelta(days=window + 10)).strftime('%Y%m%d')

# 1.获取价格数据
df_real = tq.get_market_data(
    field_list=['Close', 'Open'],
    stock_list=stock_code_list,
    start_time=start_time,
    end_time=target_end,
    dividend_type='front',
    period='1d',
    fill_data=True
)
close_df = tq.price_df(df_real, 'Close', column_names=stock_code_list)
open_df = tq.price_df(df_real, 'Open', column_names=stock_code_list)

# 2.买卖信号计算与生成
ma5_dynamic = vbt.MA.run(close_df, window=window).ma.ffill()
ma5_dynamic.columns = close_df.columns

entries_df = close_df.vbt.crossed_above(ma5_dynamic).shift(1).fillna(False).astype(bool)
exits_df = close_df.vbt.crossed_below(ma5_dynamic).shift(1).fillna(False).astype(bool)

print(f"\n信号生成统计：")
print(f"买入信号总数：{entries_df.sum().sum()}")
print(f"卖出信号总数：{exits_df.sum().sum()}")

# 3.执行回测
portfolio = vbt.Portfolio.from_signals(
    close=close_df,    # 净值计算用未复权收盘价
    entries=entries_df,    # 延迟后的买入信号
    exits=exits_df,    # 延迟后的卖出信号
    price=open_df,    # 含滑点的成交价格
    init_cash=100000,    # 初始资金10万元 
```

```python
size_grundarity=100 - # A股最小交易单位100股
60 )
61
62 # ====== vbt绘图 ======
63 portfolio[stock_code_list[0]].plot().show()
64
65 # 4. 输出回测结果
66 print(f"\n" + "="*60)
67 print(f"投资组合回测表现")
68 print("=*60)
69 stats_df = portfolio.stats()
70 print(stats_df)
71
72 print(f"\n" + "="*60)
73 print(f"投资组合回测记录")
74 print("=*60)
trades_df_original = portfolio.trades.records_readable.copy()
print(trades_df_original.to_string()) 
```

← 计算调仓信号并快速买卖

20260122公众号文章 →

# Q：运行的python文件可不可以随便放，不一定在PYPlugins\user目录下？

A： 可以。在import tqcenter前添加通达信安装目录\PYPlugins\user这个绝对路径。

<table><tr><td>1</td><td rowspan="2">import sys
sys.path.append(&#x27;C:/new_tdx64/PYPlugins/user&#x27;)</td></tr><tr><td>2</td></tr><tr><td>3</td><td>from tqcenter import tq</td></tr><tr><td>4</td><td>tq.initialize(__file__)</td></tr></table>

# Q：无法内部执行策略之如何把python路径添加到PATH中

A： 内部执行python策略时，会寻找用户设定的默认python解释器执行python策略，所以必须在操作系统<高级系统设置>--->环境变量设置里，配置python路径。

![](images/a8eecd4eff8296548fa0ecce1bc805f78251c336358b0ad678928e7ab1c0340a.jpg)

<details>
<summary>text_image</summary>

环境变量
HP 的用户变量(U)
变量	值
include	C:\Program Files (x86)\Microsoft Visual Studio\VC98\atl\inclu...
lib	C:\Program Files (x86)\Microsoft Visual Studio\VC98\mfc\lib;...
MSDevDir	C:\Program Files (x86)\Microsoft Visual Studio\Common\MS...
OneDrive	C:\Users\HP\OneDrive
Path	C:\Users\HP\AppData\Local\Programs\Python\Python313\Scr...
PyCharm	D:\MayZeeyar\MyApp\PyCharm 2025.2.1.1\bin
TEMP	C:\Users\HP\AppData\Local\Temp
新建(N)...	编辑(E)...	删除(D)
系统变量(S)
变量	值
NUMBER_OF_PROCESSORS	12
OS	Windows_NT
Path	E:\VMWare\VM17\bin\C:\Windows\system32\C:\Windows\C:...
PATHEXT	.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC
PROCESSOR_ARCHITECT...	AMD64
PROCESSOR_IDENTIFIER	Intel64 Family 6 Model 151 Stepping 5, GenuineIntel
PROCESSOR_LEVEL	6
新建(W)...	编辑(I)...	删除(L)
确定	取消
</details>

如图所示，环境变量中分为用户变量和系统变量，都有PATH，在这两个中添加python路径都可生效，但是用户变量的优先级高于系统变量，所以图中仅在用户变量中的PATH中添加python路径。

![](images/8e1b5c73853a60c1a1f9ed41a49c2ae923e55e25a7d66706147e7143a7b4487c.jpg)

<details>
<summary>text_image</summary>

C:\Users\HP\AppData\Local\Programs\Python\Python313\Script...
C:\Users\HP\AppData\Local\Programs\Python\Python313\
C:\Users\HP\AppData\Local\Programs\Python\Python39\Scripts\
C:\Users\HP\AppData\Local\Programs\Python\Python39\
C:\Users\HP\AppData\Local\activestate\cache\bin\
C:\Users\HP\AppData\Local\ActiveState\StateToo\release\bin\
C:\Users\HP\AppData\Local\Programs\-Python\-Python312\Sc...
C:\Users\HP\AppData\Local\Programs\-Python\-Python312\
C:\Users\HP\AppData\Local\Programs\-Python\Launcher\
C:\Program Files (x86)\Microsoft Visual Studio\Common\Tools\
C:\Program Files (x86)\Microsoft Visual Studio\Common\MSDe...
C:\Program Files (x86)\Microsoft Visual Studio\Common\Tools\
C:\Program Files (x86)\Microsoft Visual Studio\VC98\bin
%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\
E:\VSCode\VSCode-win32-x64-1.33.1\bin\
%PyCharm%
D:\MayZeeyar\Tools\CMake3.18.4\bin\
%USERPROFILE%\dotnet\tools
新建(N)
编辑(E)
浏览(B)...
删除(D)
上移(U)
下移(O)
编辑文本(T)...
确定	取消
</details>

图中可见，PATH中可以配置多个版本的python，但是最后生效为最上面的，每个版本的python需要配置两个路径。

# Q：出现类似以下的报错怎么办？

1

```txt
FileNotFoundException: Could not find module 'F:\tdx\new_tdx_600\PYPlugins\TPythonClient.dll' (or one of its dependencies). Try using the full path with constructor syntax. 
```

A： 这通常是TPythClient.dll缺少依赖库导致的，请检查TPythClient.dll同目录下（../PYPlugins/）是否有tdxrpcx64.dll，通常是杀毒软件误杀此dll导致，需要重装或给予白名单确保tdxrpcx64.dll不会被杀毒软件误杀。

# Q：外部运行的py文件报已经存在运行的，怎么处理？

A： 请在TQ策略管理器找到这个正在运行的已经运行出错的OutSide策略，点删除策略删除它。

# Q：菜单一直显示“正在开启TQ策略..”

A： 是否有以下这个提示？如果有，请允许访问。

![](images/83e84ace2fc12abe1ba5af0a1951296537471143438943c1e5d77559f717a307.jpg)

# Windows Defender防火墙已经阻止此应用的部分功能

WindowsDefender防火墙已阻止所有公用网络和专用网络上的通达信应用程序的某些功能。

![](images/1932c86615668b1fed4da003d0b515c938476af8a9af11f3b963d8d5ded3e8ad.jpg)

名称(N): 通达信应用程序

发布者(P): （通达信）深圳市财富趋势科技股份有限公司

路径(H): F:\tdx\new\_tdx\_cfv\_mock\tdxwd.exe

允许通达信应用程序在这些网络上通信：

专用网络，例如家庭或工作网络(R)

公用网络，例如机场和咖啡店中的网络(不推荐，由于公用网络通常安全性很小或者根本不安全）U

允许应用通过防火墙有何风险？

允许访问(A)

取消

# Q：获取的数据count=5，返回的指标值怎么前面的是none？

'ZF':[None,'-0.18','1.20','0.64']

A： formula\_set\_res = tq.formula\_set\_data\_info(stock\_code=stock,stock\_period='1d', count=4,dividend\_type=1)这里的count=4是获取最近4根k线的数据用于计算指标，所以最近4根k的数据

ZF:(C-REF(C,1))/REF(C,1)\*100;这个式子的只能计算出 最后4根k的涨幅值。

所以在获取指标值时注意获取k线数目要覆盖到最大参数值，否则计算结果会为空。

# Q：为什么同一个选股公式，用formula\_process\_mul\_xg选股的结果比客户端条件选股中得到的结果少？

A： 请确认formula\_process\_mul\_xg中的count参数是否合理？数据个数要满足公式计算中的数据要求。客户端的条件选股中使用了所有的本地数据。

# Q：如何选出分钟内主力净额排名靠前的股票？

A： 可以用一定时间间隔获取主力净额输出值，然后用这次值减上次值的差额排序筛选全市场找出来。

{ZLJE 自定义指标}

超B:=L2\_AMO(0,0)/10000.0;

大B:=L2\_AMO(1,0)/10000.0;

中B:=L2\_AMO(2,0)/10000.0;

小B:=L2\_AMO(3,0)/10000.0;

超S:=L2\_AMO(0,1)/10000.0;

大S:=L2\_AMO(1,1)/10000.0;

中S:=L2\_AMO(2,1)/10000.0;

小S:=L2\_AMO(3,1)/10000.0;

主力净额:(超B+大B)-(超S+大S),NODRAW;

实现示例完整代码

import sys1

import time2

from tqcenter import tq

tq.initialize('0303zlje.py')   
# 先获取A股全部股票  
```python
all_stocks = tq.get_stock_list(market='5')[:100]
# all_stocks=['300911.SZ', '600635.SH', '000890.SZ', '603155.SH', '301448.SZ', '600010.SH', '600011.SH', '600012.SH', '600013.SH', '600014.SH']
print("正在处理，请等待...")
start_date = '20240601'
end_date = '20240630' 
```  
# 开始计时

start\_time = time.time()   
```ini
macd_stocks = []
pre_mul_zb_result = {}
mul_zb_result = {}
curr_val = 0
countjs = 1
pre_val=0
ce_val=0 
```  
# 添加最大循环次数限制，防止无限循环  
max\_iterations = 10 # 设置最大迭代次数

```python
while countjs <= max_iterations:
    # 保存之前的值
    pre_mul_zb_result = mul_zb_result.copy()  # 使用copy()避免引用问题
```

# 获取新的值  
```python
mul_zb_result = tq.formula_process_mul_zb(
    formula_name='ZLJE',
    formula_arg='',
    xsflag=6,
    return_count=2,
    return_date=True,
    stock_list=all_stocks,
    stock_period='1d',
    count=-1,
    start_time=start_date,
    end_time=end_date,
    dividend_type=1
) 
```

```txt
print("当前结果:", mul_zb_result)
print("前一结果:", pre_mul_zb_result)
countjs += 1 
```

# 检查是否有有效的数据  
```python
if mul_zb_result and countjs >= 2:    # 至少需要两次才能比较
    diff_list = []
    for key in mul_zb_result:
    if key != "ErrorId":
    # 安全检查
    if (key in mul_zb_result and
    '主力净额' in mul_zb_result[key] and
    len(mul_zb_result[key]['主力净额']) >= 1 and
    key in pre_mul_zb_result and
    '主力净额' in pre_mul_zb_result[key] and 
```

```python
curl_val = mul_zb_result[key]['主力净额'][-1]['Value']
pre_val = pre_mul_zb_result[key]['主力净额'][-1]['Value']
ce_val = float(curr_val) - float(pre_val)
diff_list.append((key, ce_val))

print(f"股票 {key}: 当前值={curr_val}, 前值={pre_val}, 差值={ce_val}")
# 按差值从大到小排序，输出前5名
if diff_list:
    diff_list.sort(key=lambda x: x[1], reverse=True)
    print("主力净额变化前5名:")
    for i, (code, diff) in enumerate(diff_list[:5], 1):
    print(f"{i}. {code}: {diff:.2f}")
else:
    print("无有效差值数据")

# 等待一段时间再下一次循环
time.sleep(180)

print("处理完成") 
```

← 20260302公众号文章