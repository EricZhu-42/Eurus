# Eurus - 利用 SeaTable 中转的 IM 消息推送工具

利用 SeaTable 进行中转，实现内网机器推送 Markdown 消息到手机 APP（支持飞书、钉钉、企业微信）

> In Greek mythology, **Eurus** ( /ˈeu̯.rus/ ) is the god of the east wind, who often *carries messages across the sea*.

## 项目特色

- 内外网机器均可使用，可用于模型训练完成，服务器状态异常等场景向手机 APP 推送信息
- 通过内网 SeaTable 服务器进行内-外网中转，便捷安全，无隐私泄露风险
- 提供基于 Python3 标准库封装的 Python SDK，接入简单，最少仅需 2 行代码即可推送文本通知消息
    ```python
    from eurus import eurus # 载入模块
    
    eurus.send("Hello World", MY_API_TOKEN) # 向默认群组发送信息
    ```
- 支持推送 Markdown 类型消息（包括文本样式、超链接等功能）；支持分组配置不同的推送渠道，便于分类信息

## 平台选择

| 平台     | 配置端 | 频率限制  |
| -------- | ------ | --------- |
| 飞书     | PC     | 100 / min |
| 企业微信 | 移动端 | 20 / min  |
| 钉钉     | PC     | 20 / min  |

部分细节：

- 钉钉建立单人群组需要通过移动端的 “面对面建群” 功能；企业微信需要多人才能建立群组
- 飞书 Markdown 不支持 # 关键词