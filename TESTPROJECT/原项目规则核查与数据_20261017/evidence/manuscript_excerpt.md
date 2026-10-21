# 原稿核查摘录

来源：Manuscripts.docx。P为OOXML中w:p元素的零基索引，不是页码。公式提取为线性文本，结构化解释见参数与规则文件。

## P47

The life cycle (LC) of rumor microblogs is the time from the release of rumor microblogs to the death of the discussion heat. This study uses the time span from the first to the last comment that was present in the historical record we collected as the rumor cycle, as shown in Equation (3):

## P48

                              LC=TL-TF             (3)

## P49

where TF represents the timestamp of the first observed comment and TL denotes the timestamp of the last observed comment in our crawled dataset for that rumor thread.

## P55

The typical rumor spread pattern follows a sequence of primary, secondary, and multiple spread. To simplify the model and facilitate the calculations, we define the dissemination range of rumors (PR) as the sum of the primary and secondary spreaders. The number of primary disseminators corresponds to the number of followers of the rumor blogs Num[fan], whereas the number of secondary disseminators represents the cumulative number of followers among fans of the blog Num[ffan]. The formula is shown in Equation (5):

## P56

                          PR=Num[fan]+Num[ffan]         (5)

## P59

To investigate public willingness to forward the government’s rumor-refuting microblogs (RF), we distributed 300 questionnaires and collected 265 valid responses. The statistical analysis revealed a 60% probability of users being willing to forward rumor-refuting news regarding major public opinion.

## P60

To summarize, after analyzing the characteristics of rumor sources and their recipients, we further calculated the mean values of these characteristics among 125 major public opinion rumors as initial parameters for our simulation model. The specific parameters are presented in Table 1.

## P67

TBU denotes the average time required for the public to change their attitude toward a rumor from acceptance to rejection after the government initiates rumor refutation. A smaller value of TBU indicates that the public responds more quickly to the governmental clarification, implying higher refutation effectiveness. Accordingly, this study uses TBU as the dependent variable. In the simulation, TBU is calculated as the average delay between the time when the government starts refuting the rumor and the time when individual users change their attitude from believing to rejecting the rumor. The calculation is given in Equation (7):

## P68

               TBU=1ni=1nTiUpdatabelief-T-G,TiUpdatabelief>T-G             (7)

## P69

where TiUpdatabeliefdenotes the tick at which user i changes from rumor acceptance to rumor rejection, and T_G denotes the tick at which the government begins rumor refutation. The condition TiUpdatabelief > T-Gensures that only attitude changes occurring after the governmental intervention are included. Here, n is the number of users who complete this belief transition after the government starts refuting the rumor.

## P72

When users are in the rumor cocoon of rumor bloggers, their social personalities are gradually cocooned. They have a similar cognitive framework to and smaller social distance from rumor bloggers. Consequently, they are likely to trust the opinions of rumor bloggers and develop a rumor trust gap with groups outside the cocoon. Because the full platform process of group cocooning cannot be directly observed in the simulation, this study uses PBd to capture its belief-polarization outcome. As illustrated in Figure 2A, PBd represents the belief-divergence component of group cocooning in the simulation, calculated as PBd = PBin - PBout, where PBin refers to the rumor trust level of users within the cocoon and PBout refers to that of users outside the cocoon. As the level of group communication within the cocoon increases, the degree of group cocooning also intensifies. Accordingly, the rumor trust gap between cocooned and non-cocooned users becomes larger. This study assumes that users who remain in the cocoon generally conform to this pattern; if they no longer agree with the views of the rumor source, they are likely to unfollow the rumor blogger and exit the rumor cocoon.

## P75

Moreover, a stronger inclination toward believing rumors (PB) is positively associated with an increased likelihood of becoming a rumor disseminator (RC) [33]. In our model, we assume that the dissemination probability (RC) is strictly proportional to the belief probability (PB). To quantify this relationship, we calculated a proportional constant (P) based on the empirical mean values from our dataset:P=RCPB=0.100.579≈0.172. Consequently, in the simulation environment, whenever the probability of believing a rumor (PB) varies—such as the differences observed between users inside versus outside the rumor cocoon—the probability of becoming a disseminator (RC) dynamically scales according to this constant ratio P. This proportional linkage ensures our parameter settings dynamically reflect real-world spreading mechanisms (as detailed in Table 1).

## P100

Following prior agent-based studies of rumor diffusion, this study adopts discrete time steps to represent the temporal evolution of rumor spreading. In such models, agents interact with their neighbors and update their states at each time step t; accordingly, in the present study, a step refers to one discrete simulation time step. Lu et al. [2] showed that rumor diffusion generally follows a two-stage pattern: The first stage is characterized by rapid and linear growth accompanied by a surge in rumor propagation (OD); in the second stage, the speed of rumor dissemination gradually decreases, exhibiting nonlinear growth patterns (DE). Inflection point D marks the transition between these two periods and is usually observed at approximately 80% of the overall rumor diffusion ratio. As shown in Figure 2B, the proportion at inflection point D is approximately 79%. This is consistent with previous models (80%), suggesting that the pattern of rumor spreading within a social platform with a rumor cocoon still follows this rule. Additionally, the rapid growth stage in this model requires 187 steps to increase from 0% to 79%. The slow growth stage requires an additional 63 steps to increase from 79% to 94%. Given that the initial stage (steps 0–187) accounts for the majority of rumor propagation (approximately 80%), effectively refuting rumors during this period can efficiently suppress their further dissemination and prevent their influencing expansion, requiring relatively fewer resources while yielding more significant intervention outcomes. Conversely, refuting rumors in the second stage may require greater resource allocation without guaranteeing an ideal effect. Therefore, we propose that governmental efforts to combat rumors should primarily concentrate on the first stage (OD), ensuring that the time delay of governmental rumor refutation does not exceed 187 steps. Consequently, we set the range of lag times in government rumor refutation (T_G) to {20,40,60,80,100,120,140,160,180}. As shown in Figure 3, the lag time of governmental rumor refutation demonstrates clear differences in rumor propagation, and longer delays in governmental rumor refutation lead to higher proportions of rumor believers and longer rumor survival times. Thus, we use the delayed time of governmental rumor refutation (T_G) as an indicator of the government’s capability to explore its effect on TBU.

## P104

To capture the government’s ability to identify and target users within the rumor cocoon, this study distinguishes three refutation capacities in the model, denoted as In-out. First, when the government can accurately identify users in the rumor cocoon and primarily deliver refuting messages to them, this scenario is coded as the government primarily refuting rumors within the rumor cocoon (In-out = 2), indicating a high level of identification and targeting capability. Second, when the government can only partially identify or reach users within the rumor cocoon and therefore delivers refuting messages randomly to users either within or outside the rumor cocoon, this scenario is coded as random refutation either within or outside the rumor cocoon (In-out = 1), indicating a medium level of identification and targeting capability. Third, when the government fails to identify users within the rumor cocoon and mainly delivers refuting messages to users outside the rumor cocoon, this scenario is coded as the government primarily refuting rumors outside the rumor cocoon (In-out = 0), indicating a low level of identification and targeting capability. The coding scheme is specified in Equation (8). 

## P106

Government credibility (GT) is important for addressing broader social issues [2], particularly for managing rumors [4, 5, 22]. Hence, this study set GT as {0.2,0.4,0.6,0.8,1} to examine the impact of varying levels of GT on TBU and infer the effect of different levels of government credibility on the effectiveness of government rumor refutation.

## P108

In our model, the rumor cocoon is introduced to represent the clustered communication environment in which rumor dissemination is intensified. As shown in Figure 4A, blue and green agents represent SMP users, and the rumor cocoon is visualized as a circle. The size of this circle varies with the proportion of users who believe the rumor. At the early stage of dissemination, as the number of believers increases, the circle expands. After the government releases rebuttals and the number of believers declines, the circle gradually shrinks.

## P109

The rumor cocoon also distinguishes between users with different levels of exposure to rumor sources. Agents inside the circle are defined as followers of rumor bloggers, whereas agents outside the circle represent users who do not follow these bloggers. Blue agents inside the circle can move only within the circle, reflecting their closer and more direct exposure to rumor bloggers. By contrast, green agents can move both inside and outside the circle. This setting reflects the AI-driven recommendation algorithms of SMPs, through which a small proportion of users who do not follow rumor bloggers may still encounter rumors directly, whereas most non-followers remain outside the immediate rumor environment. As a result, blue agents and a small number of green agents are the first to be exposed to rumor sources.

## P110

The model further assumes that users inside and outside the cocoon differ in their likelihood of believing and forwarding rumors. Specifically, blue agents are assigned a higher probability of believing and forwarding rumors than green agents. This difference is represented by the parameter for the degree of group cocooning in Table 2, which captures the effect of the rumor cocoon on rumor recipients during dissemination.

## P111

Rumors spread beyond the rumor cocoon through interactions between agents across its boundary. This outward diffusion occurs through two pathways. First, blue agents inside the cocoon can transmit rumors when they encounter green agents near the edge of the circle. Second, because green agents can move freely in and out of the cocoon, those who have become rumor disseminators can carry rumors beyond the cocoon and spread them to the wider network.

## P115

Based on the analysis and calculation of the characteristics pertaining to rumor sources and recipients of 125 major public opinion rumors on Weibo as shown in subsection 3.1, we incorporated these characteristics as other parameters in our model. In terms of rumor sources, the setting of the blue agents’ number is determined by NF = 82. Green agents have a fixed number of 500. In Figure 4A, the left side shows the situation before the rumor outbreak, and the right side shows the situation after the rumor outbreak. The red agent positioned at the center represents the rumor source, located at the center of the rumor cocoon. Its size represents the influence of the rumor source (RI = 1). Moreover, considering that the rumors’ life cycles (LC) have an average value of 250 ticks, their heterogeneity, and the time required for governmental rumor-refutation, we ultimately determined the termination time of 400 ticks for our model. Preliminary experiments confirmed that setting the termination time at 400 ticks is appropriate and does not limit the value of TBU. In terms of rumor recipients, the rumor cocoon, in which the recipients of rumors are situated, is represented by a circle to illustrate the sphere of influence exerted by the source (PR = 11.7). In addition, an agent’s movement speed was employed as an indicator of their level of activity on social platforms (UA = 2). Furthermore, this model considers individual heterogeneity by incorporating several thresholds. First, the threshold for public belief in rumors is considered as PB. Second, the probability of becoming a rumor spreader has a threshold denoted as RC. Third, the threshold for forwarding the government’s rumor-refuting information to the public is set as RF.

## P162

As illustrated in Figure 4B, rumor diffusion is modeled as a discrete-time, contact-driven state-transition process. The process begins with rumor bloggers initiating rumor dissemination. In each tick, rumor-related agents move randomly in a two-dimensional space. Agent movement speed represents user activity on the SMP: higher speed indicates more frequent encounters with other agents within the same tick. Such encounters simulate browsing others’ microblogs or exchanging opinions.

## P163

To mathematically formalize the interaction mechanism, this study draws on epidemic-style compartmental models of rumor spreading and conceptualizes agent interactions within a modified S-E-I-R framework. Let St, Et, It, and Rt denote the proportions of agents at tick t who are susceptible, rumor-trust-only, rumor disseminators, and rumor-not-trust, respectively. Since susceptible agents may encounter either rumor bloggers or rumor disseminators, let λt denote the effective contact intensity between susceptible users and active rumor senders at tick t.

## P164

Following an effective encounter, state transition is governed by two sequential probabilities. An agent first believes the rumor with probability PB. Conditional on belief, the agent becomes a rumor disseminator with probability RC; otherwise, the agent remains a rumor-trust-only user. The discrete-time dynamics are therefore given by:

## P165

                            St+1= St - λtSt                              (9)

## P166

                       Et+1 = Et+ λtSt⋅PB⋅(1 - RC)                      (10)

## P167

                         It+1= It + λtSt⋅PB⋅RC                         (11)

## P168

                        Rt+1= Rt + λtSt⋅(1 - PB)                        (12)

## P169

Equation (9) indicates that susceptible agents leave the susceptible state after effective exposure. Equations (10)–(12) describe the three possible post-exposure outcomes: believing the rumor without disseminating it, believing and disseminating it, or rejecting it. Thus, the branching process in Figure 4B is determined by effective exposure, rumor acceptance, and dissemination propensity. At the micro level, this mechanism is equivalent to two sequential Bernoulli trials after an effective encounter: the first determines rumor acceptance with probability PB, and the second, conditional on acceptance, determines rumor dissemination with probability RC.

## P172

After a period of time, the government begins to refute the rumors. As shown in Figure 4A, the black agent represents the government, and we simulate the delay in governmental rumor refutation by setting different time delays for governmental rumor refutation (T_G). By adjusting In-out to 2, 1, or 0, the government is positioned to refute rumors primarily inside the rumor cocoon, randomly within or outside the cocoon, or primarily outside the rumor cocoon, thereby representing different target groups of rumor refutation. At each tick in the rumor-dispelling process, the government moves one step in a random direction. If the government meets with an SMP user (blue or green agents), a random value ranging from 0 to 1 is generated. If the random number exceeds government credibility (GT), this user will not change their belief in the rumor. Conversely, if the random number falls below GT, the agent will choose to believe the government’s refutation and will not believe the rumor anymore. Subsequently, another random value between 0 and 1 is generated. If this value is less than RF, the agent forwards rumor-refuting information; otherwise, it does not. 

## P173

Finally, upon completion of 400 ticks by all agents, the agents cease movement and proceed to the next simulation, which is reset to the time prior to the rumor occurrence. At the beginning of each simulation run, the positions of all SMP users and the government agent were randomly initialized. For each simulation run, we calculated the mean TBU across all agents who updated their beliefs after the governmental rebuttal. This run-level mean TBU was used as one observation in the regression analysis. The final dataset contained 81,000 stochastic simulation replications nested within 405 unique parameter combinations of PBd, T_G, In-out, and GT. Because repeated simulation runs under the same parameter combination are not fully independent, standard errors were clustered at the parameter-combination level. This approach accounts for the nested simulation structure while summarizing how TBU varies across systematically generated governance scenarios. The detailed flowchart of the simulation model is shown in Figure 5A.