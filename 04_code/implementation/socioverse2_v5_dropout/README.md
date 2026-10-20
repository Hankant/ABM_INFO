# V5 技术失败退出分支

用户授权变更：从V5已完成tick21的状态继续，重试耗尽的LLM用户永久技术下线。原V5代码及结果不覆盖。此分支不是原V5的无修改续跑，也不能把退出解释为真实主动下线。

## 运行
在持有Key的PowerShell执行 Start-Dropout-From-Tick22.ps1 一次。以后中断使用本目录 Resume-MiniMax-Simulation.ps1。继承父运行预算、失败记录、缓存和完整21轮断点；总请求上限12200不重置。使用V4虚拟环境与MiniMax配置，代码为本目录。

## 退出边界
- 同一请求超时/连接错误重试耗尽（当前两次；历史同签名至少两次也有效），或JSON/证据格式最多4次耗尽，触发技术退出。
- 鉴权、额度、预算、未知HTTP错误、未决请求及程序逻辑异常仍全局停止，不自动删除用户。
- 退出不产生信念或行动；保留原信念、记忆、已发布帖子和网络关系。之后不接收新内容、不评论、不转发。旧帖子仍能被其他用户看到。
- 每轮仍保存582条身份记录，退出者后续为空行动。remaining_agents为未技术退出人数，不等于本轮真正阅读人数。退出仅在整轮提交后生效，断点回放会重建。
- 此规则可能把服务端故障造成的失败也计入退出，剩余人数不能作为真实用户留存率。

## 日志与指标
运行结果写入06_experiments/results/socioverse2_v5_dropout，审计写入06_experiments/logs/socioverse2_v5_dropout。
- request-events.jsonl：UTC时间、agent、tick、请求签名和编号、决策开始、发送、收到响应头、收到完整响应、校验通过/失败、缓存复用。SDK请求钩子不代表已到达服务端。
- request-N.json：原始提示词、返回全文、参数、耗时、用量、错误类型；新增底层异常类型链和timeout_phase。不保存认证头、Key和异常原文。旧请求无法补出当时缺失的细节。
- dropout-T-Agent.json：拟退出原因；必须配合checkpoint确认提交，不能单独当作已退出证据。
- checkpoints：每轮完整行动与哈希，decision_status=technical_dropout为退出提交记录。
- reports/technical_dropout.json：最新完成轮次、剩余总人数、剩余LLM人数、退出者ID/轮次/原因。
- trajectory/metrics_history.json：remaining_agents、remaining_llm、remaining_rule、technical_dropout_count与未退出人群的四类信念人数。原all_*包含退出用户保留的旧信念。
- provenance.json：输入、代码哈希、父运行与第22轮生效的规则变更。

## 验证
原有37项测试加退出提交/幂等/回放/指标、额度不退出、HTTP阶段日志不泄露认证信息测试。离线40轮为工程验证，不是实际LLM实验结果。

## 文件权限错误修复

运行023241-331705在tick22 A0361请求发出前出现PermissionError，前一请求435已正常收到HTTP200并校验通过。旧诊断没有filename，无法确定具体失败文件或占用进程，不将其归因为agent问题。

新增JSON读取/原子替换的有界PermissionError重试，最多6次、总等待3秒；仍失败保留全局停止。补充文件名、errno/winerror、无局部变量的堆栈位置诊断。未改变研究规则、未修改原始回答或预算。Continue-After-IO-Repair.ps1仅对该父运行及指定代码哈希执行修复迁移；其后正常Resume。真实续跑尚未由助手启动。
