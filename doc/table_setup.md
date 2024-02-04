# SeaTable 配置流程

通过表格导出的 API_TOKEN 鉴权，避免在机器存储个人账号密码的隐私风险

## 配置 Table

首先创建 Table 表格，并导出表格的 API Token

1. 下载表格模板 (10 KB)
2. 登录 SeaTable 网页版，点击 我的表格 → 添加表格 → 从文件导入，选择刚刚下载的表格模板，等待导入完成。可以按个人喜好修改表格的名字
3. 点击刚刚表格右侧的三个小点（更多操作）→ 高级 → API Token → 随意输入 APP 名称，权限为 “可读写” → 提交，此时会显示表格的 API Token。请记录下 API Token，最终 Python 代码调用时会使用到

## 管理 Webhook

刚刚创建的表格，其有两个子表，名称分别为 "Mapping" 与 "Buffer"，其中 "Mapping" 储存的是消息的分类规则，其共有两列，分别为群组名 Name 与 Webhook 地址 Webhook。

例如，假设 Mapping 表的内容为：

| Name    | Webhook |
| ------- | ------- |
| DEFAULT | URL_0   |
| Group_1 | URL_1   |

Eurus 发送消息时，可以选择提供群组名参数 `group`，其具体规则为：

1. 若 `group` 与某一行匹配成功**（大小写不敏感）**，则将消息发送给该行 Webhook 对应的群组

   > 例如：调用 `eurus.send(text, group="Group_1")` 时，将向 URL_1 对应的群组发送内容为 `text` 的信息

2. 若 `group` 为空（默认为空），或 `group` 与任一行均不匹配，则默认将消息发送至第一行 Webhook 对应的群组

   > 例如：调用 `eurus.send(text)`  或 `eurus.send(text, group="Group_2")`，均会将消息发送给 URL_0 对应的群组

请根据需求自行配置群组。"Mapping" 表的行可以自由添加。

配置完成后（**请至少配置第一行的默认 Webhook**），可以进入 "Buffer" 子表，并在某一行的 "Content" 列随意输入一些文字。如果配置正确，你会看到刚刚输入的内容会在几秒后自动消失，同时消息会被推送到默认 Webhook 对应的群组。