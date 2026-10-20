# 模型参数与程序执行顺序

当前代码对应最近确认的设计：使用582名独立模拟用户，真实账号资料作为画像；T_G扩展为10、20、30、40、50。所有随机网络、群体划分和心理属性均是实验设定。已导入75个有正文事件，另50个保留画像并列入待补清单。

## 从哪里改参数

编辑 `config/research.json` 后，运行时加 `--config config/research.json`。改变行为配置后必须使用新的输出目录；代码会阻止不同配置混入同一轨迹。某些固定规则由校验器锁定，若要改变规则，需要同步修改 `src/rumor_sim/core.py`、校验器及相关测试。

| 设置 | 当前值与作用 | 配置位置 |
| --- | --- | --- |
| 圈内用户 | 82；关注SOURCE，身份为实验分配 | population.n_inside |
| 圈外用户 | 500；不直接关注SOURCE | population.n_outside |
| 其他账号 | SOURCE发布源帖；GOV只在政策轮发布纠正 | core.py |
| 真实画像 | 粉丝数、关注数、累计发博数；不足582份时重复抽取模板 | 各事件 profiles.jsonl |
| 同组关注 | 每人随机关注8名同组用户 | network.same_group_follows |
| 跨组关注 | 每人随机关注2名另一组用户 | network.cross_group_follows |
| 政府关注 | 初始均不关注GOV | network.pre_follow_government |
| 活跃概率 | 0.1、0.2、0.3；圈内27/28/27人，圈外167/166/167人 | population.activity_levels / counts |
| 原有政府信任 | 0.25、0.5、0.75；按上述人数独立打乱赋值 | population.trust_levels |
| 日常分享习惯 | rare、sometimes、often；按上述人数独立打乱 | population.sharing_styles |
| 纠正分享倾向 | 圈内49人、圈外300人愿意分享；其余倾向仅阅读 | population.willing_inside / willing_outside |
| 初始群体差异d_seed | 0、0.2、0.4；构造首次曝光前的倾向，不强迫模型接受 | grid.d_seed |
| 总体初始倾向均值 | μ=0.579；圈内μ+(500/582)d，圈外μ−(82/582)d | prior.overall_mean |
| 组内个体差异 | 每组一半在该组均值上加0.05，一半减0.05 | prior.within_group_offset |
| 关注信息槽位 | 活跃者最多阅读1条所关注账号的可读帖子 | feed.following_slots |
| 推荐 | 活跃者以0.1概率打开推荐槽位，最多1条非关注账号可读帖子 | feed.recommendation_probability |
| 时效权重 | 2^(−帖龄/5)，越新越易被抽中 | feed.recency_half_life_rounds |
| 帖子寿命 | 帖龄小于40轮才可读；0轮源帖在第1轮可见 | feed.post_ttl_rounds |
| 重复阅读 | 同一post_id最多3次，重复间隔至少5轮 | feed.max_reads_per_post / repeat_gap_rounds |
| 转发约束 | 同一根内容每名Agent最多转发1次 | feed.max_reposts_per_content |
| 评论与转发可见性 | 本轮新建的用户帖子从下一轮起可读 | feed.new_user_post_delay |
| 记忆 | 最近5个实际决策轮的阅读与行动，未曝光轮不添造记忆 | feed.memory_decision_rounds |
| 信念 | LLM给出0–100整数；≥60接受、≤40拒绝，其余不确定；尚未曝光为unaware | belief |
| T_G：自变量 | 10、20、30、40、50轮 | grid.government_round |
| In-out：自变量 | inside、random、outside；分别从圈内、全体、圈外抽取 | grid.targeting |
| 直接投送预算 | 每个政策40名独立用户，仅T_G轮投送；不活跃也读到 | policy.direct_unique_users |
| GT：自变量 | 0.2、0.6、1.0；提示来源过去10条已核验内容中2/6/10条准确，属于虚拟实验线索 | grid.credibility |
| PBd：基线调节变量 | 第5轮实际接受比例之差：圈内接受人数/82−圈外接受人数/500 | time.pb_checkpoint_round |
| TBU：因变量 | T_G−1轮接受者，在T_G至T_G+30首次变为拒绝的轮数差 | time.followup_max_elapsed |
| 总运行长度 | 每条完整轨迹80轮 | time.last_round |
| 随机种子 | 1、2、3；控制环境及分配，不能保证远程模型输出完全确定 | grid.seeds |
| LLM | deepseek-v4-flash，经用户指定第三方端点调用 | llm.model / base_url |
| 采样 | temperature=0.7，top_p=0.8，最多384个输出token | llm |
| 输出失败 | 每个决策最多初次加2次重试；401/403立即停止；绝不换成Mock继续真实实验 | llm.max_retries |

GT仅改变可见的来源线索，模型需要结合原有信任、当前内容和记忆自行决定信念与行动。d_seed与实际PBd是两个量，输出中分别保留，不能混称为测得的群体差异。程序不向Agent提前透露现实主张真假或预期研究结论。

## 每轮的完整交互

1. 初始化582个独立用户、真实公开画像、实验属性和有向关注网络。信念尚未形成，记忆为空。SOURCE在第0轮发布源帖。
2. 进入第t轮后，冻结上一轮末状态。按各用户活跃概率确定是否浏览。根据关注关系、推荐概率、帖龄、重复阅读限制形成信息流。
3. 如果t等于T_G，生成固定纠正帖，从指定群体抽取40名不同用户，加入其额外投送槽位。每个用户最多合并阅读1条关注帖、1条推荐帖、1条政府直接投送帖。
4. 仅对实际看到至少一条帖子的用户调用LLM；没有曝光的用户保留原信念和状态。LLM输入包括该用户画像、实验属性、此前信念、最近5次决策记忆、当轮实际可见帖子和允许转发的帖子ID。
5. LLM只返回6个字段：belief_score、action、target_post_id、public_stance、comment、reason。动作是silent、comment或repost；不能指向未见过的帖子。
6. 校验输出，不合格时按预算修复；任何最终失败使本轮不提交。所有Agent都基于同一冻结状态决策，不会看到同一轮尚未结束时其他人的回答。
7. 全部决策有效后统一提交信念和行动。评论、转发成为新帖子并继承根内容；政府帖的后续传播携带相同纠正正文和来源线索。下一轮才可被别人读到。
8. 更新真实阅读记录、记忆、统计量。第5轮记录并冻结PBd；政策分支在T_G−1轮确定风险集，随后记录首次拒绝时间。每轮原子保存快照、曝光、帖子和决策审计。
9. 所有分支运行到80轮，导出逐人TBU、总体摘要和完整时间轨迹。未在窗口内拒绝者标记event=0、duration=30，不能记成观测到TBU为30。

## 父轨迹和配对政策

每个事件、d_seed、seed组合先跑一条无纠正父轨迹到80轮，保留所有轮末快照。T_G=10/20/30/40/50的分支分别复制父轨迹第9/19/29/39/49轮末状态。相同T_G和定向策略下，不同GT使用同一组40名收件人，保持投送对象可比。各政策分支后续模型回答单独缓存，不相互复用。

每事件9条父轨迹，405条政策轨迹。CSV包含各分支对应的完整父轨迹前缀及政策后缀；完整582人轨迹的states.csv应有46,560行。

## 开始运行的顺序

1. 解压代码包，双击 `开始离线验证.cmd`。先检查61项测试，再运行一个582人、80轮的离线示例。它使用Mock决策，结果不能写作真实LLM研究发现。
2. 检查 `data/imported/ready_events.json` 中的事件输入和 `missing_source_text.csv`。当前政府纠正是明确标注的实验脚本，无真实官方证据文件。
3. 双击 `开始API测试.cmd`，隐藏输入ZetaTechs密钥。该工具每次发出最多1次新请求，输出真实状态；新平台已以 `deepseek-v4-flash` 成功返回合法决策。旧平台403已归档，不能据此判断新平台状态。
4. 接口成功后，按README命令运行一个真实事件，显式选择 `--provider http --max-api-requests 20`。额度不足时停止；不要把未完成轨迹解释为完整实验。
5. 查看provider审计、快照和exports；需要继续时使用相同命令和输出目录，并由研究者明确提高累计请求上限。更换模型、配置或文本则新建输出目录。
6. 确认单事件行为后，再使用 `grid --event-list data/imported/ready_events.json`。先执行estimate了解轨迹规模；交付程序没有擅自执行75事件的完整收费实验。
