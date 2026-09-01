# Paper 1 Formal Research Proposal

## How Does AI Change Information Acquisition and Opinion Formation in Human Groups?

Version: RP 1.4  
Date: 2026-08-25  
Status: English version of the current formal baseline for the reconstructed research direction

### Version Note

This document fixes the current reconstructed direction of Paper 1. The earlier baseline draft on “Algorithmic Authority and Information Calibration” and the identification review of “Group Information Homogenization” remain archived as historical materials. This document does not revise those earlier files.

This revision makes four changes:

1. The overarching theme is fixed as “How Does AI Change Information Acquisition and Opinion Formation in Human Groups?”;
2. The core research question of Paper 1 is fixed as “How Do Large Language Models Change Group Opinion Distributions?”;
3. The process under study now includes information exposure, information diffusion, whether information enters individual opinion updating, and group opinion evolution;
4. The theoretical framework and construct boundaries are presented in separate sections. Section 5 explains how the theories support the research questions, and Section 6 defines the terms, levels of analysis, and empirical measures.

RP 1.4 does not use “information overlap” as an umbrella term for the three subquestions. Information overlap is used only to measure relations among the factual claims, arguments, or sources received by members. Similarity in wording, active sharing by members, whether members accept information, and the final opinion distribution are measured separately. SQ3 remains conditional, and its primary candidate intervention continues to be **independent random routing across model families or providers**.

---

## 1. Research Theme and Core Research Question

### 1.1 Overarching Theme

> How does AI change information acquisition and opinion formation in human groups?

The overarching theme defines the research domain. Because “AI,” “information acquisition,” and “opinion formation” each encompass multiple technologies, behaviors, and outcomes, a single paper must further delimit the technical object, the process through which it operates, and the group-level outcome.

### 1.2 Core Research Question

> How do large language models change group opinion distributions?

This study focuses on large language models as its technical object. It examines what information members receive from LLMs and other members, which information is subsequently transmitted, how information enters opinion updating, and how the group opinion distribution changes over time. Search frequency, search stopping, perceived information sufficiency, and source trust are outside the current main line of inquiry.

### 1.3 Subquestions

In this paper, group opinion evolution refers to systematic changes in the group opinion distribution over rounds of interaction, including shifts in the group mean, opinion convergence, polarization, clustering, and fragmentation. These are distinct distributional patterns and must be reported separately.

> SQ1: How do large language models change information exposure and information diffusion within groups?

> SQ2: How do changes in information exposure and diffusion affect individual opinion updating and group opinion evolution?

> SQ3: If the above patterns of group opinion evolution are observed, can technical interventions at the LLM layer attenuate them?

The three subquestions form a single process chain:

$$
\text{LLM generation and technical configuration}
\rightarrow
\text{individual information exposure}
\rightarrow
\text{member sharing and network diffusion}
\rightarrow
\text{acceptance weights and opinion updating}
\rightarrow
\text{group opinion evolution}
$$

No single term is used to summarize every stage of this process chain. Surface-level textual similarity belongs to the technical-output layer; information overlap is an indicator of the distribution of information exposure; active sharing is a member behavior; subjective credibility assigned to factual claims and the weight placed on external information belong to the individual-updating layer; and convergence, polarization, and clustering are group-level opinion outcomes.

Information overlap is retained as an auxiliary empirical indicator. It measures the extent to which two or more members receive the same information items. Information items are restricted to coded factual claims, supporting or opposing arguments, and sources. For issue $q$, the set of information items received by member $i$ is denoted by $I_{iq}$. Information overlap in statistical group $g$ is measured as the within-group mean of pairwise Jaccard overlap:

$$
O_{gq}
=
\frac{2}{n_g(n_g-1)}
\sum_{i<j}
\frac{|I_{iq}\cap I_{jq}|}{|I_{iq}\cup I_{jq}|}
$$

$O_{gq}=0$ indicates that members share no information items, whereas $O_{gq}=1$ indicates that members receive identical information items. This indicator does not measure similarity in wording, sharing behavior, subjective credibility, update weights, or opinion convergence.

---

## 2. Research Object and Scope

### 2.1 Technical Object

The research object is limited to large language models that generate natural-language responses. The main experimental conditions are a shared single LLM and independent random routing across model families or providers. The routing configuration is an experimental condition, not a theoretical construct. Neutral prompts constitute the main setting; stance-conditioned prompts are used only for boundary tests.

### 2.2 Unit of Analysis

The primary unit of analysis is a statistical group with an information-diffusion network. Members interact separately with an LLM and may also share information with other members through network ties that are prespecified or empirically calibrated. The group is used to calculate information exposure, diffusion paths, individual opinion trajectories, and the final opinion distribution.

The statistical group does not perform a joint task or make a formal team decision. Although the model may include information transmission and social influence among members, its conclusions cannot be directly generalized to real organizational teams with defined roles, status relations, and shared responsibilities.

### 2.3 Meaning of Opinion

This paper uses `opinion` to refer to an individual’s position on a specific public-policy issue. It can be measured empirically using degree of policy support or a continuous opposition–support scale. This state is neither a factual belief with a verifiable truth value nor a stable general ideology.

The `opinion state` in the ABM is a formal state variable. Whether it represents the policy attitudes of real people must be established through calibration with human data and out-of-sample validation.

### 2.4 Group-Level Outcomes

The group opinion distribution is the distribution of members’ opinion states within the same statistical group. The primary measure is the change in within-group opinion variance. Auxiliary measures include shifts in the mean position, pairwise opinion distance between members, the number of opinion clusters, and distributional bimodality.

Consensus, differentiation, and polarization describe distributional patterns; they do not automatically indicate judgment quality. Political attitudes and policy preferences usually lack a unique ground truth, so the main study does not use accuracy to evaluate whether they are better or worse.

---

## 3. Research Background

LLMs have become interactive gateways through which people obtain explanations, arguments, and policy information. Unlike conventional information retrieval, LLMs directly generate integrated natural-language responses. After receiving these responses, group members may restate, share, or continue to interact around them. LLMs can therefore change information content, member exposure, and subsequent diffusion processes at the same time.

Jiang et al., in *Artificial Hivemind: The Open-Ended Homogeneity of Language Models*, identify both intra-model repetition and inter-model homogeneity in open-ended generation [1]. Their study identifies homogeneity at the level of model output but does not examine how people update their opinions after exposure to such output. Fügener et al., in *Will Humans-in-the-Loop Become Borgs? Merits and Pitfalls of Working with AI*, show that AI assistance may improve individual performance while increasing correlations among members’ choices [2]. Doshi and Hauser further report that generative AI can improve individual creative performance while reducing the diversity of content produced at the group level [3]. Taken together, these studies show that individual-level outcomes and group-level distributions require separate analysis.

Changes in information exposure also do not guarantee changes in political opinions. Nyhan et al. reduced Facebook users’ exposure to like-minded sources but found no measurable changes across eight preregistered political-attitude outcomes [4]. This result requires the present study to identify the information layer separately from the opinion layer. Perra and Rocha’s model includes opinion posting, filtering of personal timelines, and opinion updating based on timeline content; filtering rules and network structure jointly affect local homogeneous clusters, the survival of minority opinions, and the overall opinion distribution [5]. Their study shows why information exposure, member diffusion, and opinion updating must be incorporated into the same dynamic process.

This study draws on the layered treatment of information exposure, information diffusion, selective acceptance, and group opinion evolution in research on information cocoons and algorithmic personalization to construct an ABM of LLM-mediated group information processes. Information cocoons are not the research object, dependent variable, or claimed contribution of this paper.

Research on algorithmic monoculture provides a system-level basis for technical intervention at the LLM layer. Kleinberg and Raghavan define `algorithmic monoculture` as a condition in which multiple decision-makers use the same algorithm and show that this pattern of use can reduce system-level outcomes even when the individual algorithm is highly accurate [13]. The theory concerns the correlation structure created by shared use of the same algorithm. This paper applies it to generative information environments: when members use the same generative model, the arguments, evidence, and errors they receive may become more correlated, and subsequent diffusion may amplify these relations.

Major model providers have already adopted several technologies adjacent to the problem of information diversity. OpenAI adjusts model behavior through requirements for covering multiple viewpoints, evaluations of political bias, and participatory `collective alignment` [14,15]. Anthropic uses Collective Constitutional AI to incorporate public input into a model constitution [16]. Google’s AI co-scientist uses multi-agent modules for Generation, Reflection, Ranking, and Evolution, together with web search and specialized models, to generate candidate hypotheses [17]. Microsoft Foundry Model Router routes requests among multiple models according to quality, cost, and latency [18]. Gemini Grounding can generate one or more search queries and synthesize web sources [19]. These systems address response bias, value input, candidate generation, task matching, and factual grounding, respectively. Existing official evaluations do not examine whether they reduce overlap in the information received by different users. Provider practices establish the practical feasibility of multi-model, multi-agent, and multi-source architectures; they do not directly establish that group-level information diversity has increased.

The literature assembled for this project separately covers LLM-output homogeneity, group diversity in human–AI collaboration, algorithmic information exposure, member diffusion, and opinion dynamics. What remains missing is a layered, validated chain of evidence showing how LLM-generated content enters member exposure and diffusion and then, through the weights members place on that information, forms individual opinion trajectories and group-level distributions. This paper examines that connection.

---

## 4. Theoretical Tension

The theoretical tension is that the same generative system may provide members with similarly directed information and thereby promote opinion convergence, yet it may also generate different information conditional on members’ initial positions and, through selective diffusion and acceptance, promote clustering, polarization, or fragmentation.

SQ3 translates this theoretical tension into a system-level intervention. The inclusion of multiple models, agents, sources, or public value inputs within a system does not guarantee changes in member exposure, diffusion, or opinion evolution. Shared alignment rules, routing objectives, ranking criteria, and aggregation procedures may compress internal differences. Independent random routing across model families or providers must first change the information process before it can attenuate the group-level evolutionary pattern identified in SQ2.

Under common, nonpersonalized prompting, a model’s own generative tendencies may lead different members to receive similar arguments and evidence. Continued exposure to similarly directed information may produce opinion convergence. When users’ initial positions enter the prompt, the model may select arguments consistent with those positions; different initial camps may then update in their respective directions, leaving the group divided or producing more pronounced clustering. Experiments with LLM agents by Chuang et al. show that adding confirmation-bias prompts can produce opinion fragmentation in simulated groups [6].

The effect of LLMs on group opinion distributions therefore cannot be inferred directly from output homogeneity. The study must identify three stages:

1. Whether LLM generation and technical configuration change members’ information exposure;
2. How members diffuse this information and how heavily exposed information is weighted in opinion updating;
3. Whether these changes enter individual opinion updating and group opinion evolution.

This tension places “convergence driven by a shared model prior” and “differentiation driven by user-conditioned generation” at the same level of analysis. Whether a prompt contains the user’s initial position is treated as a prespecified boundary condition, not as a separate research line.

---

## 5. Theoretical Framework

The theoretical framework connects four bodies of literature. LLM generation homogeneity provides the empirical premise at the technical level; group-information research explains how information is distributed and diffused; opinion dynamics explains how members update their positions; and algorithmic monoculture explains why a system-level intervention is needed at the LLM layer. These literatures operate at different levels of analysis and cannot substitute for one another.

### 5.1 Empirical Premise: LLMs May Change the Correlation Structure of Group Information Inputs

Jiang et al. identify both intra-model repetition and inter-model homogeneity in open-ended generation [1]. This finding indicates that, even when members query models separately, the resulting technical outputs may still contain similar arguments, evidence, sources, or errors. Fügener et al. find that AI assistance can improve individual performance while increasing correlations among members’ choices [2]. Doshi and Hauser find that generative AI can improve individual creative performance while reducing the diversity of group-level output [3]. Together, these findings support a starting premise: separate individual use of AI does not guarantee mutually independent information inputs at the group level.

This empirical premise concerns only the relation between technical output and group information inputs. It does not establish that members will believe the content, nor does it establish that a group will ultimately converge, polarize, or experience lower judgment quality. SQ1 must therefore test whether model-output characteristics actually translate into differences in member exposure and information diffusion.

### 5.2 Group Information Processes: Information Distribution, Exposure, and Diffusion Must Be Separated

Stasser and Titus’s work on `shared information` and `unshared information` shows that the number of members who possess an information item affects which information is more likely to enter collective processing during group discussion [11]. Steinel et al. further distinguish what information members possess from whether they reveal, conceal, or misrepresent it [12]. Together, these studies show that the initial distribution of information across members and members’ active sharing of information are separate processes.

Research on algorithmic information environments adds an exposure layer. Nyhan et al. successfully changed the proportion of like-minded sources to which users were exposed but did not observe corresponding changes in preregistered political-attitude measures [4]. This result supports identifying information exposure separately from opinion outcomes. Perra and Rocha place opinion posting, filtering of personal timelines, and timeline-based opinion updating in the same network model. They show that filtering rules and network structure can change local homogeneous clusters, the persistence of minority opinions, and the overall opinion distribution [5]. Their model provides the dynamic structure used in this paper: generated content enters individual exposure and then diffuses through the network.

Research on information cocoons and algorithmic personalization supplies a reference for layering and modeling these processes. This paper draws on its treatment of exposure selection, network diffusion, and opinion evolution. It neither tests whether individuals are in information cocoons nor claims the information-cocoon literature as its theoretical contribution.

### 5.3 Opinion Dynamics: The Same Information Environment Can Produce Different Group Outcomes

Opinion dynamics provides the central theoretical basis for SQ2. The DeGroot model represents opinion updating as a weighted average of others’ opinions; under appropriate connectivity conditions, this updating process can lead to consensus [7]. The Friedkin–Johnsen model retains individuals’ attachment to their initial positions, allowing social influence to coexist with persistent disagreement [8]. The Hegselmann–Krause bounded-confidence model specifies that individuals incorporate only information within a threshold distance from their own opinions, which can generate multiple opinion clusters [9]. These models yield different predictions: common input and broad acceptance favor convergence, whereas attachment to initial positions and bounded acceptance can sustain disagreement or produce clustering.

This paper does not assume in advance that any single update rule is the true mechanism. Human calibration experiments estimate attachment to initial positions, acceptance weights placed on external information, and opinion change, after which candidate rules are compared by their ability to predict held-out issues. In this study, opinion dynamics converts natural-language information generated by LLMs into testable individual opinion trajectories and group-level distributional outcomes. It accommodates competing outcomes, including convergence, persistent disagreement, clustering, and no measurable change.

### 5.4 Algorithmic Monoculture: From a Shared Technical Source to Intervention at the LLM Layer

Kleinberg and Raghavan’s work on `algorithmic monoculture` examines the correlated signals, rankings, or decisions that arise when multiple decision-makers use the same algorithm [13]. Its theoretical value lies in evaluating system-level outcomes when multiple decision-makers share an algorithm, rather than evaluating only the accuracy of an individual algorithm. This paper derives a proposition to be tested: use of the same LLM may increase the correlation of members’ information exposure and error structures, and member diffusion may further amplify this correlation.

This theory identifies an intervention point for SQ3 but does not imply that a multi-model architecture will automatically be effective. Different models may rely on common training data, alignment rules, and retrieval sources and thus still provide similar information. Independent random routing across model families or providers must first change a defined information-exposure or diffusion measure and must subsequently attenuate the same group-opinion outcome identified in SQ2 before the claim of technical mitigation is supported.

### 5.5 Integrated Framework and Research Questions

The four bodies of literature form the following theoretical chain:

$$
\text{LLM generation and technical configuration}
\rightarrow
\text{information exposure}
\rightarrow
\text{member sharing and network diffusion}
\rightarrow
\text{acceptance weights and individual opinion updating}
\rightarrow
\text{group opinion evolution}
$$

SQ1 tests whether technical outputs enter group information processes. SQ2 tests how information exposure and diffusion produce group-level outcomes through different opinion-update rules. SQ3 tests whether technical interventions at the LLM layer can attenuate an identified evolutionary pattern. The framework allows three competing paths: common information inputs combined with broad acceptance may promote convergence; generation conditioned on initial positions, selective sharing, and bounded acceptance may produce clustering or polarization; and changes in the information environment may produce no measurable change in group opinions. The theoretical contribution depends on whether the study can distinguish among these paths.

---

## 6. Construct Boundaries and Empirical Correspondence

This section specifies the terms, levels of analysis, model positions, and empirical measures used in the formal RP. The entries below constrain the interpretation of variables; they do not perform a theoretical-derivation function.

### 6.1 Homogeneity of LLM Output

- Original terms: `intra-model repetition`, `inter-model homogeneity`, and `Artificial Hivemind`.
- Source: Jiang et al. [1].
- Theoretical definition: content similarity across repeated generations from one model or across generations from different models.
- Excludes: homogenization of human opinions, group consensus, and declines in judgment quality.
- Level of analysis: technical-output level.
- Position in the model: antecedent and first-stage outcome.
- Empirical measures: argument overlap, semantic similarity, source overlap, and correlations among stance scores.

### 6.2 Information Exposure

- Original terms: `information exposure` and `exposure to viewpoints`.
- Sources: Nyhan et al. [4]; Perra and Rocha [5].
- Theoretical definition: the content that a user actually sees or receives in an information environment.
- Excludes: whether the user believes the content, whether the user changes policy support, and the final group distribution.
- Level of analysis: individual-input level; relations among members’ inputs can also be compared at the group level.
- Position in the model: after LLM generation and routing configuration, but before member diffusion and opinion updating.
- Empirical measures: factual claims, arguments, sources, and stance information received by each member; at the group level, viewpoint coverage, source composition, repeated exposure, proportion of unique information, and pairwise information overlap among members.

Information overlap is a relational indicator at this layer. Surface-level similarity in wording is measured separately through lexical or character overlap; semantic similarity is measured using validated text representations. Neither measure substitutes for coding factual claims, arguments, and sources.

### 6.3 Information Sharing and Diffusion

- Original terms: `information sharing`, `posting`, and `information diffusion`.
- Sources: Perra and Rocha [5]; Stasser and Titus [11]; Steinel, Utz, and Koning [12].
- Theoretical definition: the process through which members post, restate, or send information they possess to other members and through which that information spreads along a relational network.
- Excludes: information initially received from an LLM, the weight assigned to seen information during opinion updating, and whether final opinions converge.
- Level of analysis: member behavior, network edge, and statistical group.
- Position in the model: the interactive process between information exposure and opinion updating.
- Empirical measures: number and proportion of sharing events, number of recipients, diffusion depth and breadth, proportion of cross-cutting diffusion, and the diffusion path of each information item.

### 6.4 Opinion, Acceptance Weights, and Opinion Dynamics

- Original terms: `opinion`, `opinion dynamics`, `bounded confidence`, and `susceptibility to influence`.
- Sources: DeGroot [7], Friedkin and Johnsen [8], Hegselmann and Krause [9], and Perra and Rocha [5].
- Theoretical definition: `opinion` is an individual’s discrete or continuous position on a specific issue; opinion dynamics describes how this state changes in response to external information and social influence. $\lambda_i$ is the weight of social influence in a member’s overall update, and $w_{ij,t}$ is the relative weight of exposed message $j$ in the social-influence input for that round. Both are model-implementation parameters, not independent theoretical constructs.
- Excludes: whether texts are similar, whether information is shared, the objective truth of factual propositions, stable personality, and general political identity.
- Level of analysis: individual state and individual updating process.
- Position in the model: after information exposure and diffusion, but before formation of the group distribution.
- Empirical measures: pretest, round-by-round, and posttest scores on a policy-support scale; $\lambda_i$ and $w_{ij,t}$ are estimated from opinion changes in human experiments. When materials contain factual propositions with verifiable truth values, the subjective credibility that participants assign to those propositions is measured separately.

### 6.5 Group Opinion Evolution

- Original terms: related research commonly uses `opinion distribution`, `opinion share`, `consensus`, and `polarization` to describe group states [5,9].
- Theoretical definition: the statistical distribution of all members’ opinion states within the same group and changes in that distribution over rounds of interaction.
- Excludes: normative evaluations of the quality of group opinions.
- Level of analysis: statistical group.
- Position in the model: core dependent variable.
- Empirical measures: group mean, within-group variance, mean pairwise distance, number of opinion clusters, bimodality, and changes in these quantities relative to the initial state.

### 6.6 Algorithmic Monoculture and Technical Intervention at the LLM Layer

- Original term: `algorithmic monoculture`.
- Source: Kleinberg and Raghavan [13].
- Theoretical definition: multiple decision-makers use the same algorithm, producing correlated signals, rankings, or decision outcomes.
- Excludes: repeated generation within a single model, any form of model-market concentration, and similarity in performance across all models.
- Level of analysis: the technical system used by the group.
- Position in the model: a system-level antecedent of information exposure and subsequent group evolution, and the intervention point for SQ3.
- Empirical correspondence: in the shared-model condition, all members use the same base LLM. In the technical-intervention condition, each member independently draws an LLM from a prespecified pool spanning model families or providers. The structure of model use is directly determined by experimental assignment.

---

## 7. Competing Expectations for the Research Questions

No directional hypotheses are specified at present. The theory permits three competing outcomes:

1. A shared generative source and repeated exposure cause members to update in similar directions, and group opinions converge;
2. Generation conditioned on initial positions, selective sharing, or bounded acceptance causes different camps to update in their respective directions, producing clustering, polarization, or fragmentation;
3. Information exposure and diffusion change, but the group opinion distribution shows no measurable change.

These outcomes imply different theoretical explanations and cannot be collapsed into a single directional hypothesis before the model and primary outcome are fixed. Formal directional hypotheses will be specified only after pilot studies determine the primary evolutionary measure, the update rule, and the first-stage result of the technical intervention. SQ3 remains conditional: only if SQ2 identifies a stable pattern of group opinion evolution will the study test whether an intervention at the LLM layer attenuates that same pattern.

---

## 8. Research Design

### 8.1 Overall Method

The study uses a hybrid ABM calibrated with human data. The model maintains a common population, network, information environment, state variables, and time steps while incorporating two types of agents in the same system. Rule-based agents operate according to explicit opinion-dynamics equations. LLM agents use individual profiles, current opinions, historical memory, and information received in the current round to generate structured next-period opinions and behaviors. The two types of agents use the same opinion scale and behavioral fields, allowing them to exchange information within the same network and enabling direct comparison of their opinion trajectories. HiSim, developed by Mou et al., provides a direct methodological precedent in which LLM-driven core users and deductive-ABM ordinary users operate together [20].

Here, “hybrid” refers specifically to the coexistence of two implementations of agent behavior within the same ABM. Real human data initialize agent characteristics, calibrate the parameters of rule-based agents, and validate opinion transitions for both types of agents. Population, network, and data source do not themselves define the model as hybrid.

LLMs have two roles in the study, and these roles must remain separate. First, the LLM information source under study provides policy information to the group. Second, LLM agents in the method simulate how some members understand and express natural-language information and update their opinions. The study records the models, prompts, inputs, and outputs used for each role so that the same model does not simultaneously process information, simulate humans, and code outcomes.

The complete process is:

$$
\text{LLM response}
\rightarrow
\text{text coding}
\rightarrow
\text{information exposure}
\rightarrow
\text{sharing and network diffusion}
\rightarrow
\text{acceptance weights and opinion updating}
\rightarrow
\text{group opinion evolution}
$$

The ABM is used to conduct large-scale counterfactual comparisons. Human experiments estimate opinion-update parameters and test whether the model predicts issues not used for calibration. Emergent results from the ABM alone cannot establish causal effects in real populations.

#### 8.1.1 Three Behavioral Functions

Rule-based agents and LLM agents share three behavioral interfaces. Following HiSim’s formal treatment of selection, message, and update functions [20], the three functions define how an agent generates a message, selects its exposure, and updates its opinion in each round:

$$
m_{j,t}=f_{\text{message}}(x_{j,t},z_j,H_{j,t},E_t),
$$

$$
J_{i,t}=f_{\text{selection}}(i,G_t,\{m_{j,t}\},x_{i,t}),
$$

$$
x_{i,t+1}=f_{\text{update}}
\left(x_{i,t},\{m_{j,t}:j\in J_{i,t}\},z_i,H_{i,t}\right).
$$

Here, $x_{i,t}$ denotes the opinion state of agent $i$ in round $t$; $z_i$ denotes individual characteristics supported by human data; $H_{i,t}$ denotes historical memory; $E_t$ denotes the external information environment; $G_t$ denotes the interaction network; and $J_{i,t}$ denotes the information sources that actually enter agent $i$’s exposure set in the current round.

The three functions have the following meanings in the model:

1. The message function $f_{\text{message}}$ determines how an agent converts its current state into a transmissible message. Rule-based agents use prespecified templates or numerical mappings. LLM agents generate natural-language messages from individual profiles, current opinions, and historical records and return structured fields such as stance, arguments, sources, and behavior type.
2. The selection function $f_{\text{selection}}$ determines which candidate messages enter an agent’s actual exposure set. In the main model, both agent types use the same explicit selection rule. Network reachability, recommendation probability, and the information actually encountered by the agent are recorded separately. Fixing the exposure mechanism in this way facilitates identification of differences in message generation and opinion updating.
3. The update function $f_{\text{update}}$ determines an agent’s next-period opinion after receiving information. Rule-based agents use opinion-dynamics equations calibrated with human data. LLM agents read the individual profile, current opinion, historical memory, and exposure bundle and return a next-period opinion on the common scale, a sharing decision, and a generated message. The outputs of LLM agents must be validated against pretest–posttest opinion transitions observed in real people.

The integration of LLMs and the ABM therefore occurs at the implementation layer of the agent behavioral functions. The opinion-update function is the primary point of integration for opinion evolution; the message function handles natural-language expression and transmission; and the selection function remains explicit and controllable in the main model. The state variables, network structure, and update sequence form the common ABM environment in which both types of agents operate.

### 8.2 Policy Issues

The initial plan uses approximately 24 public-policy issues spanning the economy, environment, education, public health, immigration, and technology regulation. Each issue uses a continuous support scale and records initial opinions. The final number of issues will be determined by a simulation-based power analysis that treats the issue as the unit of generalization.

A single political issue cannot support general conclusions about group opinion formation. A large number of random seeds estimates only simulation error; it does not substitute for multiple issues.

### 8.3 LLM Information Layer

The main configurations are:

1. Shared model: group members use the same base LLM;
2. Independent random routing: at the start of each issue, each member is independently assigned a base LLM drawn from a prespecified model pool, and subsequent interactions on that issue remain with the assigned model; the pool must include different model families or providers;
3. Human-information baseline: members receive materials from a quality-matched, human-curated information repository.

Routing probabilities are prespecified and are not adjusted according to the user’s initial opinion, prompt content, question difficulty, cost, or model-predicted response quality. This restriction prevents the endogenous model selection found in commercial routers. Candidate models must first be calibrated for mean information quality. Formal comparisons should approximately match the quantity of information, text length, factual accuracy, mean stance direction, and readability at the member level.

Models, prompts, sampling parameters, output length, number of interaction rounds, and temporal version must be fully recorded. A common neutral prompt is the main setting. Prompts that include users’ initial positions are used for boundary tests and cannot be pooled with the main setting. High-temperature sampling, AI personas, and multi-agent debate within a single model are not the primary technical interventions for SQ3, because these configurations may change only wording, predefined stances, or internal reasoning processes without changing member exposure, diffusion, or opinion evolution.

### 8.4 Text-Measurement Layer

Each response is coded for:

- Direction and strength of stance;
- Distinguishable factual claims;
- Supporting and opposing arguments;
- Cited or mentioned information sources;
- Semantic representation.

At the text layer, the study separately measures surface similarity in wording, semantic similarity, overlap in factual claims and arguments, source overlap, stance direction, and error correlation. Lexical or character overlap measures surface wording; human-validated semantic representations measure semantic similarity; and information-item coding identifies factual claims, arguments, and sources. Information overlap is only one measure at the text and information-exposure layers. It does not measure information diffusion, subjective credibility, acceptance weights, or opinion outcomes. Automated coders must be validated on human-annotated samples, with classification accuracy, coding agreement, and rules for resolving disagreements reported.

The same generative model cannot simultaneously generate responses, perform final text coding, and update human opinions.

### 8.5 Information-Exposure Layer

Initial agent exposure is determined by LLM responses. Subsequent exposure comes from both LLMs and content shared by other members in the network. In each round, the model records the information actually received by each agent, its source, arrival time, and diffusion path. At the group level, it reports viewpoint coverage, source composition, repeated exposure, proportion of unique information, pairwise information overlap among members, and cross-cutting exposure.

Process identification for SQ2 uses a fixed response library and the same initial group, with counterfactual runs that separately change information allocation and network-diffusion rules. Conditions must match information quantity, text length, factual accuracy, the balance of supporting and opposing arguments, mean stance direction, and readability. If these attributes cannot be matched, no causal interpretation is assigned to a single information process.

### 8.6 Information-Diffusion Layer

Each agent may share information it has encountered with its network neighbors. The model records sharing behavior, recipients, diffusion depth, and diffusion breadth in every round. The probability of sharing and its relations with opinion distance, information source, or content attributes must be determined from human behavioral data, existing data, or prespecified sensitivity ranges. Demographic characteristics and LLM-generated personality descriptions cannot substitute directly for actual sharing behavior.

The diffusion network may use an empirical network, a prespecified network structure, or robustness comparisons across multiple structures. Network structure is an input condition; actual sharing events and diffusion paths are process variables.

### 8.7 Acceptance Weights and Opinion Updating

Each agent has an initial opinion. Whether social-influence weights and acceptable opinion distances enter the agent state is determined jointly by human calibration data and candidate update models. The candidate primary structure for rule-based agents is a Friedkin–Johnsen update that retains the initial opinion; a bounded-confidence model tests whether selective acceptance produces different outcomes. The final primary update rule will be selected according to predictive performance on held-out human observations.

The baseline update for a rule-based agent can be written as:

$$
x_{i,t+1}
=
(1-\lambda_i)x_{i,0}
+
\lambda_i
\sum_{j\in J_{i,t}}
w_{ij,t}s_{j,t},
\qquad
\sum_jw_{ij,t}=1.
$$

Here, $x_{i,0}$ is the member’s initial opinion; $s_{j,t}$ is the coded stance of message $j$; $\lambda_i\in[0,1]$ is the weight of social influence in the update; $1-\lambda_i$ is the member’s attachment to the initial opinion; and $w_{ij,t}$ is the weight of exposed message $j$ in member $i$’s update. The classical Friedkin–Johnsen model uses others’ opinions as social-influence inputs [8]. This project connects the coded stances of natural-language messages to the same structure, so this equation is a candidate implementation of the text–state interface.

The bounded-confidence test further specifies $w_{ij,t}=0$ when $|s_{j,t}-x_{i,t}|>\varepsilon_i$. $\varepsilon_i$ denotes the acceptable opinion distance and corresponds to the confidence bound in the Hegselmann–Krause model [9].

LLM agents do not directly apply the numerical equation above. They receive an individual profile, current opinion, historical memory, and the current exposure bundle and return, in a prespecified format, a next-period opinion, whether to share, the target or scope of sharing, and a generated message. The next-period opinion must use the same scale as the rule-based agents. The model also retains the original natural-language rationale so that consistency between the numerical state and the publicly expressed position can be checked. LLM output represents only the state transition of a simulated agent and cannot be interpreted directly as the internal thought process of a real person.

The distributions of $\lambda_i$, $w_{ij,t}$, and $\varepsilon_i$ must come from estimates based on human experiments, existing panel data, or explicit sensitivity ranges. Opinion-transition direction, magnitude, and sharing behavior of LLM agents must likewise be tested on held-out human observations. When research materials include verifiable factual propositions, the subjective credibility assigned by members to those propositions must also be measured; policy support cannot substitute for factual belief. Demographic characteristics and personality descriptions cannot directly substitute for actual opinion-transition data.

### 8.8 Calibration with Human Data

The calibration experiment records participants’ initial positions on multiple policy issues, randomly presents coded information materials, and then measures opinion change. The experiment estimates:

- Individual differences in opinion inertia;
- How the distance between information and an initial position affects the magnitude of updating;
- Whether members share information they encounter and with whom;
- How repeated exposure and member restatement affect acceptance weights;
- Differences in updating across issues in response to the same information;
- The joint distribution of parameters.

Some issues are used to estimate the parameters of rule-based agents and to construct verifiable individual profiles for LLM-agent prompts. Held-out issues are used to test separately whether rule-based and LLM agents can predict the direction and magnitude of opinion change, sharing behavior, and group-level distributions in human samples. Fit in population initialization cannot substitute for validation of opinion updating. Sample size will be determined through a simulation-based power analysis using the group design, expected intragroup correlation, and the smallest effect of interest; it is not fixed arbitrarily at the RP stage.

### 8.9 Group Construction and Simulation Runs

Each statistical group consists of rule-based agents and LLM agents with heterogeneous initial opinions and an information-diffusion network. The proportion and sampling rules for LLM agents will be fixed after pilot studies and included in the sensitivity analysis. The same initial group and network are used in paired runs across conditions with common random numbers to reduce irrelevant Monte Carlo variation. Run logs separately preserve raw LLM responses, text coding, information exposure, sharing paths, rule-agent update parameters, structured LLM-agent outputs, agent states, and group outcomes so that every layer remains auditable.

The simulation should report entities, state variables, processes, scheduling, initialization, input data, and submodels according to the ODD protocol [10].

### 8.10 Model Validation

Model validation follows a layered procedure. Program verification, parameter calibration, empirical validation, and sensitivity analysis address different questions and cannot be replaced by superficial similarity in final group-level curves. Empirical validation of an ABM requires an explicit correspondence among theory, model structure, and real-world data [21]. Multi-level pattern comparison reduces the problem of observationally equivalent explanations produced by fitting a single outcome [22].

#### 8.10.1 Program Verification

Program verification tests whether the code correctly implements the declared model. The three behavioral functions are unit-tested separately: whether the message function returns the specified format, whether the selection function constructs $J_{i,t}$ according to the network and exposure rules, and whether the update function produces the next-period state prescribed by the equation or output protocol for a given input. The model is also tested under extreme conditions, including no messages, identical messages, opposing messages, and disconnected networks, and for reproducibility given fixed model versions, inputs, and random seeds. Program verification establishes implementation correctness; it provides no evidence of empirical validity.

#### 8.10.2 Empirical Validation of the Three Functions

The message function is compared with texts produced by real participants under the same profile, issue, and information conditions. Comparisons cover stance direction, factual claims, arguments, sources, expressions of uncertainty, and sharing behavior. Automated text coding must first be validated on human-annotated samples.

The selection function uses human information-selection or sharing data to estimate the probability that a message enters the actual exposure set. Its predictions of reading, ignoring, and sharing behavior are tested on held-out participants or held-out issues. Network reachability and actual selection are recorded separately.

The update function is validated using data with the structure “initial opinion–controlled information exposure–posttest opinion.” The same held-out observations are supplied separately to the rule-based agent, the LLM agent, and an opinion-invariance baseline. The comparison covers the direction of opinion change, error in update magnitude, the final opinion distribution, and sharing behavior. Data used for parameter estimation or prompt construction cannot be reused for out-of-sample validation.

#### 8.10.3 Incremental Test of the Hybrid Architecture

A rule-only ABM, the hybrid ABM, and simple baseline models are compared under the same initial population, network, information materials, and random conditions. The central question is whether adding LLM agents improves prediction of message expression, opinion change, sharing behavior, and group distributions for held-out issues and participants. If the hybrid ABM does not deliver stable out-of-sample improvement, the methodological conclusion is restricted to opinion-dynamics results that can be explained by the rule-only ABM, and LLM agents receive no additional methodological value.

#### 8.10.4 Validation of Group-Level Patterns

When small-scale, multi-round data on real group interaction are available, real and simulated groups are compared under the same initial opinion distribution, network, information materials, and number of interaction rounds. Comparison measures include the mean and variance of opinions, opinion clusters, degree of bimodality, cross-cutting exposure, diffusion depth and breadth, and round-by-round opinion trajectories. Multiple micro- and macro-level patterns jointly serve as validation targets, avoiding a fit to only one aggregate mean [22].

If real group trajectories are unavailable, the paper can claim only that the three functions have been calibrated or validated at the individual level. Long-run group results must then be defined as empirically constrained model emergence and counterfactual simulation. They cannot be described as quantitative predictions of long-run opinion evolution in real societies.

#### 8.10.5 Functional Ablation and Sensitivity Analysis

Functional ablation holds the message, selection, or update function fixed in turn while changing the remaining functions to determine whether group outcomes arise from information generation, information selection, or opinion updating. Sensitivity analysis varies the proportion of LLM agents, network structure, update sequence, candidate opinion-dynamics rule, model version, sampling parameters, prompting method, and random seed. Results that hold under only one configuration must be interpreted within that configuration.

The ODD protocol is used to report the model’s purpose, entities and state variables, process schedule, design concepts, initialization, external inputs, and submodels in full [10]. It improves model transparency and reproducibility. Empirical validity still comes from calibration with human data, out-of-sample prediction, and comparison of group-level patterns described above.

---

## 9. Variables and Empirical Correspondence

| Position | Variable | Level of analysis | Empirical measure |
| --- | --- | --- | --- |
| Independent variable | LLM routing configuration | Technical system | Shared single LLM, independent random routing across model families or providers, human-information baseline |
| Technical output | Characteristics of LLM responses | Response/model | Surface similarity in wording, semantic similarity, overlap in factual claims and arguments, source overlap, stance direction, error correlation |
| Intermediate stage 1 | Information exposure | Individual and statistical group | Information received by each member, source composition, repeated exposure, viewpoint coverage, proportion of unique information, pairwise information overlap among members |
| Intermediate stage 2 | Information sharing and diffusion | Member/network edge/statistical group | Sharing proportion, number of recipients, diffusion depth and breadth, proportion of cross-cutting diffusion, diffusion paths |
| Intermediate stage 3 | Social-influence weight $\lambda_i$ and message weight $w_{ij,t}$ | Individual/message | Estimated from opinion changes in human experiments; subjective credibility is measured separately in factual-proposition tasks |
| Dynamic state | Individual opinion | Individual | Policy-support scale and round-by-round change |
| Core outcome | Group opinion evolution | Statistical group × round | Group mean, within-group variance, pairwise distance, opinion clusters, bimodality, and changes in these quantities |
| Boundary condition | Whether the prompt includes the initial position | Technical input | Neutral prompt, stance-conditioned prompt |

---

## 10. Identification and Statistical Analysis

### 10.1 Identification of SQ1

SQ1 first compares the human-information baseline with the shared-LLM condition to test whether the LLM changes the outputs of the message and selection functions. Model parameters must be distinguished from simulation outputs: coefficients such as $\beta$ and $\gamma$ are parameters used to implement functions; message overlap, diffusion depth, and group distributions are observed outcomes generated after the functions are iterated.

#### 10.1.1 Parameterized Output of the Message Function

The message generated by agent $j$ in round $t$ is represented as:

$$
m_{j,t}
=
\left(
s_{j,t},
\mathbf q_{j,t},
\mathbf r_{j,t}
\right),
$$

where $s_{j,t}\in[-1,1]$ denotes the stance position of the message, $\mathbf q_{j,t}\in\{0,1\}^{K}$ indicates whether the message contains factual claim or argument $k$, and $\mathbf r_{j,t}\in\{0,1\}^{L}$ indicates whether the message uses information source $l$. The message function is written as:

$$
m_{j,t}
=
f_{\text{message}}
(x_{j,t},z_j,H_{j,t}).
$$

SQ1 compares $E(s_{j,t})$, $Var(s_{j,t})$, $P(q_{j,t,k}=1)$, and $P(r_{j,t,l}=1)$ across information conditions. Group-level message overlap at the factual-claim layer is defined as:

$$
C^{M}_{g,t}
=
\frac{2}{n(n-1)}
\sum_{i<j}
\frac{|Q_{i,t}\cap Q_{j,t}|}
{|Q_{i,t}\cup Q_{j,t}|},
$$

where $Q_{i,t}$ denotes the set of factual claims contained in the messages received by member $i$ in that round. $C^{M}_{g,t}$ is a project-specific measure constructed from Jaccard overlap; it is not an independent theoretical construct. Semantic similarity is used as a robustness measure and cannot substitute for coding factual claims, arguments, and sources. The primary comparison at the message-function layer is:

$$
C^{M}_{\text{shared LLM}}
-
C^{M}_{\text{human information}}.
$$

#### 10.1.2 Parameterized Implementation of the Selection Function

The selection function determines whether a candidate message enters member $i$’s actual exposure set:

$$
J_{i,t}
=
f_{\text{selection}}
(N_i,x_{i,t},\{m_{j,t}\}).
$$

Here, $N_i$ denotes the message sources that member $i$ could encounter through the network. A candidate implementation is:

$$
P(m_{j,t}\in J_{i,t})
=
\operatorname{logit}^{-1}
\left[
\beta_0
+
\beta_d|s_{j,t}-x_{i,t}|
+
\beta_rR_{i,j,t}
+
\beta_nA_{ij}
\right].
$$

Here, $\beta_0$ is the baseline probability of exposure; $\beta_d$ captures how distance between the message and the current opinion affects the probability of selection; $R_{i,j,t}$ is the number of prior exposures to the source or information; $\beta_r$ captures how repeated exposure affects reselection; $A_{ij}$ indicates whether member $i$ and source $j$ are connected in the network; and $\beta_n$ captures how network connectivity affects information selection. This equation is a candidate project-specific implementation for estimating selection behavior, not a fixed equation from an established theory. Its coefficients must be estimated from information-selection data collected from real people.

Overlap in actual exposure among members is defined as:

$$
C^{E}_{g,t}
=
\frac{2}{n(n-1)}
\sum_{i<j}
\frac{|J_{i,t}\cap J_{j,t}|}
{|J_{i,t}\cup J_{j,t}|}.
$$

The cumulative number of repeated exposures of member $i$ to information item $k$ through round $t$ is defined as:

$$
R_{i,k,t}
=
\sum_{\tau=1}^{t}
\mathbb I(q_k\in J_{i,\tau}).
$$

The selection-function layer therefore compares $C^{E}_{\text{shared LLM}}-C^{E}_{\text{human information}}$ and $\beta_d^{\text{shared LLM}}-\beta_d^{\text{human information}}$. The first comparison tests whether members actually receive more similar information; the second tests whether the LLM condition changes the extent to which members select information according to opinion distance.

#### 10.1.3 Parameterized Implementation of Sharing and Diffusion

A candidate implementation of sharing behavior is:

$$
P(Y_{i,j,t}^{\text{share}}=1)
=
\operatorname{logit}^{-1}
\left[
\gamma_0
+
\gamma_d|s_{j,t}-x_{i,t}|
+
\gamma_rR_{i,j,t}
+
\gamma_sS_j
\right],
$$

where $\gamma_0$ is the baseline probability of sharing, $\gamma_d$ captures the effect of opinion distance on sharing, $\gamma_r$ captures the effect of repeated exposure on sharing, $S_j$ denotes the category of the information source, and $\gamma_s$ captures the effect of source category on sharing. This equation is also a candidate implementation. Its parameters must come from human sharing data or prespecified sensitivity ranges.

Diffusion depth, diffusion breadth, and the proportion of cross-cutting diffusion are process outcomes generated when the sharing function is iterated through the network. SQ1 ultimately tests:

$$
\text{LLM information condition}
\rightarrow
\left(
C^{M},C^{E},\beta_d,\gamma_d,\gamma_r
\right)
\rightarrow
\text{diffusion paths}.
$$

The analysis model must include issue effects and account for dependencies created when the same response, member, and network recur across rounds. Response content, actual exposure, and network diffusion must be reported separately; a change at one layer cannot substitute for measurement at another.

### 10.2 Identification of SQ2

SQ2 uses a fixed message library, the same initial groups, and the same networks. It directly manipulates exposure commonality in the selection function and diffusion intensity in the sharing function and then observes the output of the opinion-update function. Information exposure and diffusion must be changed exogenously; the analysis cannot rely only on correlations among process differences that arise naturally in SQ1.

#### 10.2.1 Exposure Commonality and Diffusion Intensity

The first experimental control is exposure commonality $c$:

$$
c\in\{c_{\text{low}},c_{\text{high}}\}.
$$

The $c_{\text{high}}$ condition assigns more of the same factual claims and arguments to members, whereas the $c_{\text{low}}$ condition assigns more distinct information. The two conditions approximately match information quantity, text length, factual accuracy, mean stance direction, the balance of supporting and opposing arguments, and readability. The realized $C^{E}_{g,t}$ is used to test the success of the manipulation. $c$ is an experimental control defined for this study, not a new theoretical construct.

The second experimental control is diffusion intensity $\pi$:

$$
\pi\in\{0,\hat\pi_{\text{human}}\},
$$

where $\pi=0$ means that members cannot continue to share information and $\pi=\hat\pi_{\text{human}}$ means that members diffuse information according to sharing probabilities estimated from human data. This produces the following two-dimensional simulation experiment:

|  | $\pi=0$ | $\pi=\hat\pi_{\text{human}}$ |
| --- | --- | --- |
| $c=c_{\text{high}}$ | High common exposure, no diffusion | High common exposure, diffusion enabled |
| $c=c_{\text{low}}$ | Low common exposure, no diffusion | Low common exposure, diffusion enabled |

This comparison separately identifies the effects of exposure commonality, member diffusion, and their interaction on individual opinion change and group opinion distributions.

#### 10.2.2 Acceptance of Social Influence in the Friedkin–Johnsen Structure

Rule-based agents may use a Friedkin–Johnsen structure that retains the initial opinion:

$$
x_{i,t+1}
=
(1-\lambda_i)x_{i,0}
+
\lambda_i
\sum_{j\in J_{i,t}}
w_{ij,t}s_{j,t},
\qquad
\sum_jw_{ij,t}=1.
$$

Here, $x_{i,0}$ is the member’s initial opinion; $\lambda_i\in[0,1]$ is the weight of social influence in the update; $1-\lambda_i$ denotes the member’s attachment to the initial opinion; and $w_{ij,t}$ is the weight of message $j$ in member $i$’s update. The classical Friedkin–Johnsen model uses others’ opinions as social-influence inputs [8]. The equation above uses the coded message stance $s_{j,t}$ and is the project’s implementation of a text–state interface; it cannot be presented as the complete original equation from Friedkin and Johnsen.

SQ2 first compares:

$$
\Delta x_i(c_{\text{high}},\pi)
-
\Delta x_i(c_{\text{low}},\pi),
$$

and then tests how this difference varies with $\lambda_i$. This comparison asks whether the effect of common exposure occurs primarily among members who place greater weight on social influence.

#### 10.2.3 Acceptable Opinion Distance in the Bounded-Confidence Model

The bounded-confidence model further specifies:

$$
w_{ij,t}=0
\quad\text{if}\quad
|s_{j,t}-x_{i,t}|>\varepsilon_i,
$$

where $\varepsilon_i$ denotes member $i$’s acceptable opinion distance. This parameter corresponds to the confidence bound in the Hegselmann–Krause bounded-confidence model [9]. SQ2 compares:

$$
Y(c_{\text{high}},\varepsilon_{\text{large}})
-
Y(c_{\text{low}},\varepsilon_{\text{large}})
$$

and:

$$
Y(c_{\text{high}},\varepsilon_{\text{small}})
-
Y(c_{\text{low}},\varepsilon_{\text{small}}),
$$

where $Y$ denotes a prespecified measure of the group opinion distribution. When $\varepsilon_i$ is large, members can incorporate information from a wider range of positions. When $\varepsilon_i$ is small, information beyond the threshold does not enter the update. Different combinations of common exposure, messages conditioned on initial positions, and acceptable opinion distance can produce convergence, persistent disagreement, or multiple opinion clusters.

The main parameter comparison for rule-based agents is therefore:

$$
\boxed{
c
\times
\pi
\times
\lambda
\times
\varepsilon
\rightarrow
\text{individual opinion change and group distribution}
}.
$$

Here, $c$ is the exposure commonality controlled by the selection function, $\pi$ is the diffusion intensity controlled by the sharing function, $\lambda$ is the social-influence weight in the Friedkin–Johnsen structure, and $\varepsilon$ is the acceptable opinion distance in the bounded-confidence model.

#### 10.2.4 Comparable Behavioral Response of LLM Agents

LLM agents do not have native $\lambda_i$ or $\varepsilon_i$ parameters. For LLM agents, the study directly records:

$$
\Delta x^{\text{LLM}}_{i,t}
=
x^{\text{LLM}}_{i,t+1}
-
x^{\text{LLM}}_{i,t},
$$

and estimates their behavioral response using the same exposure and diffusion manipulations:

$$
\Delta x^{\text{LLM}}_{i,t}
=
\theta_0
+
\theta_1(\bar s_{i,t}-x_{i,t})
+
\theta_2c
+
\theta_3\pi
+
\theta_4c(\bar s_{i,t}-x_{i,t})
+
u_{i,t}.
$$

$\theta_1$ describes the empirical relation between changes in the LLM agent’s state and message–opinion distance. It is a reduced-form description of LLM output and is not interpreted as a psychological parameter that literally exists inside the LLM. The direction and magnitude of state transitions are compared separately among human participants, LLM agents, and rule-based agents under the same information manipulations. $\theta_1^{\text{human}}$, $\theta_1^{\text{LLM}}$, and $\lambda_i$ in the rule-based model have different definitions and cannot be subjected directly to a parameter-equality test.

The core causal comparison for SQ2 is as follows: holding message content, information quality, and initial groups constant, change exposure commonality $c$ and diffusion intensity $\pi$ to test their effects on individual opinion updating, and then examine whether those effects vary with social-influence weight $\lambda$ and acceptable opinion distance $\varepsilon$. The primary outcomes are changes from the initial state in the group mean, within-group variance, opinion clusters, and bimodality. Differences in group outcomes can be attributed to the manipulated stage only when other processes and average member-level information attributes are approximately matched.

### 10.3 Identification of SQ3

SQ3 is tested only after SQ2 identifies a stable pattern of group opinion evolution. The primary technical intervention is independent random routing across model families or providers, and the core comparison is between a condition in which all members use the same LLM and one in which this routing scheme is used. The technical intervention must first change at least one defined information process and then attenuate the same group-level evolutionary measure used in SQ2. A change only in model labels, surface wording, or backend architecture does not constitute effective mitigation.

Commercial model routers select models according to quality, cost, latency, or question difficulty, making the routing outcome endogenous to input characteristics. Such routers establish the practical feasibility of multi-model architectures but cannot directly supply the causal comparison required for SQ3. The formal study uses independent random routing with prespecified probabilities.

### 10.4 Unit of Generalization and Uncertainty

The primary statistical unit is the “statistical group × issue.” Issues should enter hierarchical models or resampling procedures as a dimension of generalization. Random seeds estimate Monte Carlo uncertainty; they are not independent empirical observations.

The analysis also reports:

- Heterogeneity across issues;
- Sensitivity to model and prompt versions;
- Uncertainty in parameters calibrated from human data;
- Robustness across different opinion-update rules;
- Out-of-sample prediction error on held-out issues.

---

## 11. Tests of AI Specificity

A shared human-curated brief is a necessary alternative-source check. If quality-matched shared human information produces the same information exposure, sharing, acceptance, and opinion evolution through the same diffusion network, the paper can support only a general effect of common information input. An AI-specific claim additionally requires at least one of the following:

1. Content relations or repeated exposure produced through separate LLM interactions are consistently different from those produced by human information or search information;
2. User-conditioned generation and members’ follow-up queries produce dynamic diffusion and differentiation that fixed human materials cannot readily reproduce;
3. Independent random routing across model families or providers consistently changes the information process and attenuates an identified pattern of group opinion evolution.

If none of these conditions holds, the LLM can be treated only as an applied setting for a common-information-input mechanism, and the paper cannot claim an independent theoretical effect of AI.

---

## 12. Validity and Reproducibility

### 12.1 Construct Validity

- Validate the extraction of arguments, stances, and sources through human coding;
- Separate textual relations, information exposure, sharing behavior, factual beliefs, acceptance weights, and policy opinions;
- Do not use text similarity as a substitute for opinion change.

### 12.2 Internal Validity

- Conduct paired counterfactual runs using the same response library, initial groups, and networks;
- Match member-level information quantity, accuracy, mean stance, and readability;
- Change information allocation, diffusion processes, and acceptance rules separately;
- Prespecify neutral prompts and stance-conditioned prompts;
- Control model versions, sampling settings, and issue order.

### 12.3 External Validity

- Use multiple policy domains;
- Calibrate rule-based agents with opinion changes observed in real people and validate state transitions of LLM agents;
- Constrain diffusion parameters using human sharing behavior or explicit sensitivity ranges;
- Test predictions on held-out issues;
- Limit conclusions about statistical groups to settings with information-diffusion networks but without formal team tasks.

### 12.4 Reproducibility

- Preserve complete prompts, model versions, sampling parameters, and timestamps;
- Fix random seeds and record failed calls;
- Release text-coding protocols, rules for constructing the response library, network and diffusion rules, implementation details for the three behavioral functions, and the ABM code;
- Report the model according to the ODD protocol [10].

---

## 13. Research Gap

The literature assembled for this project has separately established four points: open-ended LLM output may be homogeneous [1]; AI assistance may change the correlation or diversity of human group output [2,3]; algorithmic information exposure, member posting, and network structure can be incorporated into opinion-dynamics models [5]; and LLM agents can simulate opinion updating and group opinion evolution [6].

Existing evidence has not jointly identified:

1. How characteristics of LLM output translate into members’ actual information exposure;
2. How member sharing and network diffusion change the coverage and repeated exposure of LLM-generated information;
3. How heavily exposed information is weighted in individual opinion updating and how it subsequently produces group opinion evolution;
4. How a shared generative source and user-conditioned generation account for different outcomes, including convergence, clustering, polarization, and no effect;
5. Whether independent random routing across model families or providers can change the information process and attenuate an identified pattern of group opinion evolution;
6. Whether large-scale ABM results generated by rule-based and LLM agents can obtain parameter calibration and out-of-sample support from the sharing behavior and opinion changes of real people.

---

## 14. Expected Theoretical and Methodological Contributions

### 14.1 From Individual Human–AI Interaction to Group Opinion Formation

Existing research on human–AI collaboration shows that AI can improve individual performance while increasing correlations among different members’ judgments or reducing the diversity of group-level output [2,3]. These findings indicate that positive individual-level effects may not correspond to the resulting group-level distribution.

This paper further explains how such group outcomes arise. When members interact separately with LLMs, model-generated information enters their information exposure, passes through active sharing and network diffusion, and then affects other members’ opinion updating. Individually occurring member–LLM interactions may therefore change the statistical distributions of both information and opinions across the group.

The first expected contribution to research on human–LLM interaction is a micro-to-macro explanation linking individual interactions to group opinion distributions:

$$
\text{individual–LLM interaction}
\rightarrow
\text{group information distribution}
\rightarrow
\text{member sharing and network diffusion}
\rightarrow
\text{group opinion distribution}.
$$

This explanation extends the outcome of inquiry from individual performance, individual attitudes, or one-time adoption to multiple members, repeated interaction, and group opinion evolution.

### 14.2 Incorporating Natural-Language Information Processes into Opinion Dynamics

Classical opinion-dynamics models primarily use numerical opinion states and social-influence weights to explain consensus, persistent disagreement, and opinion clustering [7–9]. In these models, social influence is usually represented by the positions of others and the weights assigned to them; the specific arguments, evidence, and sources being transmitted are often compressed into numerical inputs.

The introduction of LLMs adds a natural-language information layer that can vary independently within the opinion-formation process. The same opinion position can be expressed through different arguments, and different members may receive similar or different information from the same model. The paper therefore separates message generation, information selection, and opinion updating:

$$
f_{\text{message}}
\rightarrow
f_{\text{selection}}
\rightarrow
f_{\text{update}}.
$$

This decomposition distinguishes three explanations: group opinions may become closer because the model generated similar information, because members encountered and diffused similar information, or because members applied similar update weights to information. The paper thereby incorporates natural-language messages and their diffusion into a model of opinion evolution and tests how information content is translated into individual opinion trajectories and group-level distributions.

### 14.3 Explaining Why LLMs May Produce Both Convergence and Differentiation

Research on LLM-output homogeneity supports a prediction of group convergence: different members who use the same model with common prompts may receive similar arguments, evidence, and sources [1]. Research on algorithmic personalization and bounded confidence supports a competing prediction: when a model generates directionally consistent information conditional on a user’s initial position and members accept only content close to their own positions, different camps may update in their respective directions [5,9].

This paper places both predictions in the same opinion-dynamics framework and tests two boundary conditions. The first is whether generation depends on a user’s initial position: common neutral prompts are more likely to produce similar information, whereas stance-conditioned prompts are more likely to produce directionally different information. The second is the distance over which members accept opinions: a larger acceptable distance facilitates influence across positions, whereas a smaller acceptable distance helps opinion clusters persist.

Different combinations of shared generative tendencies, user-conditioned generation, information selection, and opinion-update rules can produce convergence, persistent disagreement, clustering, or no measurable change. The paper thus offers a unified conditional explanation for the homogenization and differentiation that may both occur in human–LLM interaction.

### 14.4 Extending the Explanatory Scope of ABMs to Natural-Language Information Processes

In this paper, the ABM is a modeling method and a generative explanatory strategy. Traditional opinion-dynamics ABMs use explicit state variables, network structures, and update equations to explain how individual interactions generate consensus, persistent disagreement, or opinion clustering. These models have strong rule transparency but usually compress the content transmitted among members into numerical opinions. They can show an opinion changing from $x_{i,t}$ to $x_{i,t+1}$, but they have more difficulty specifying which arguments a member encountered, which sources supported them, and which messages entered opinion updating through diffusion.

The hybrid ABM retains explicit network structures and opinion-update rules while adding natural-language messages and records of their diffusion:

$$
\text{natural-language messages}
\rightarrow
\text{actual exposure sets}
\rightarrow
\text{sharing paths}
\rightarrow
\text{numerical opinion updating}.
$$

Rule-based agents and LLM agents share three functional interfaces: message, selection, and update. The model preserves the natural-language messages generated by agents, the stances and factual claims contained in those messages, the information actually encountered by members, the sharing and diffusion paths, and agents’ round-by-round opinion states. The study can therefore trace group-level opinion outcomes through their information pathways and distinguish similarity in message generation, similarity in actual exposure, selective diffusion, and similarity in opinion-update rules.

This method extends the explanatory scope of ABMs in generative-AI settings. Traditional ABMs provide controllable micro-level rules and macro-level emergent structures, whereas LLM agents add natural-language information generation and expression. Their combination gives group-level outcomes both numerical state records and inspectable records of language processes.

This methodological contribution has two boundaries. First, readable natural-language output does not make the LLM’s internal generative process transparent. Second, language records require validation through human coding, and the hybrid ABM must be compared with a rule-only ABM on held-out participants and issues. Its additional explanatory value is supported only if the hybrid model provides information pathways unavailable to the rule-only model or improves out-of-sample predictive performance.

### 14.5 Conditional Technical and Governance Implications

Algorithmic monoculture continues to provide the theoretical basis for SQ3 [13], but it is not claimed as a separate primary theoretical contribution. If a shared LLM changes group opinion distributions through information exposure and diffusion, the paper further tests whether independent random routing across model families or providers attenuates that pattern.

This test asks whether reducing a group’s dependence on a single model source changes the information that members actually receive and diffuse and subsequently changes group opinion evolution. The technical intervention must first change a defined information process and, while approximately matching mean information quality, attenuate the same group-level outcome used in SQ2. Only if both conditions are met can the study derive a corresponding system-design recommendation.

Research on information cocoons and algorithmic personalization provides modeling references for information exposure, network diffusion, selective acceptance, and opinion dynamics. The paper does not claim “the discovery of a new information cocoon” as a theoretical contribution.

All contributions above are expected contributions subject to empirical testing. The formal paper will retain, narrow, or remove each claim according to the actual results of SQ1–SQ3.

---

## 15. Falsification and Scope-Reduction Rules

The current theoretical claims must be narrowed if any of the following results occurs:

1. Different LLM configurations change only surface wording and do not change factual claims, arguments, sources, stances, or members’ actual exposure, leaving SQ1 without a substantive first stage;
2. Information exposure changes, but member sharing, acceptance weights, and opinion updating do not, so the LLM effect remains confined to the information-input layer;
3. Sharing and diffusion change, but the group mean, variance, clustering, and bimodality do not, so the group-evolution pathway in SQ2 is unsupported;
4. Counterfactual conditions for exposure, diffusion, or acceptance cannot match member-level information attributes, preventing causal identification of the corresponding process;
5. Independent random routing changes no defined information process or fails to attenuate the same group-evolution measure used in SQ2, rendering the current technical intervention for SQ3 ineffective;
6. The primary results appear only among agents for which the LLM itself decides sharing or opinion updating and cannot be reproduced through human calibration or on held-out issues;
7. The results depend on a single issue, model, prompt, network, or opinion-update equation;
8. A shared human-curated brief fully reproduces the effect through the same diffusion network, and the LLM has no distinctive effect arising from dynamic generation, diffusion, or technical intervention.

Result 1 restricts the study to textual differences. Results 2–4 undermine the explanation from information processes to group opinion evolution. Result 5 rejects the current technical intervention. Result 8 retains a general common-information-input explanation while removing the claim of an AI-specific theoretical effect.

---

## 16. Fixed Elements and Matters Yet to Be Determined

### 16.1 Fixed Elements

- Overarching theme: How does AI change information acquisition and opinion formation in human groups?
- Core research question: How do large language models change group opinion distributions?
- The three subquestions;
- The conditional structure of SQ3: technical mitigation is tested only after an evolutionary pattern is observed;
- Independent random routing across model families or providers as the primary candidate intervention for SQ3;
- Statistical groups with information-diffusion networks as the unit of analysis;
- Separation of information exposure, information diffusion, social-influence weights, message weights, individual opinion updating, and group opinion evolution;
- Information overlap as only an auxiliary indicator at the information-exposure layer;
- Research on information cocoons and algorithmic personalization as theoretical and modeling references only;
- The requirement that the ABM be calibrated with human data;
- Shared human information as a test of AI specificity.

### 16.2 To Be Determined Through Pilot Studies and Power Analysis

- Number of agents per group;
- Final number of issues and interaction rounds;
- Base LLMs and versions to be used;
- Text encoder and scale of human annotation;
- Sample size for the human calibration experiment;
- Distribution of opinion-update parameters;
- Parameters governing sharing behavior and the diffusion network;
- Whether the Friedkin–Johnsen structure outperforms other candidate update rules on held-out issues, and the applicable range of the bounded-confidence parameter $\varepsilon$;
- Primary measure of group opinion evolution and the smallest effect of interest;
- Formal directional hypotheses.

These are methodological parameters and must not be allowed to retroactively change the core research question.

---

## References

[1] Jiang, L., Chai, Y., Li, M., et al. (2025). Artificial Hivemind: The Open-Ended Homogeneity of Language Models. Advances in Neural Information Processing Systems. https://openreview.net/forum?id=saDOrrnNTz

[2] Fügener, A., Grahl, J., Gupta, A., & Ketter, W. (2021). Will Humans-in-the-Loop Become Borgs? Merits and Pitfalls of Working with AI. MIS Quarterly, 45(3), 1527–1556. https://doi.org/10.25300/MISQ/2021/16553

[3] Doshi, A. R., & Hauser, O. P. (2024). Generative AI Enhances Individual Creativity but Reduces the Collective Diversity of Novel Content. Science Advances, 10(28). https://doi.org/10.1126/sciadv.adn5290

[4] Nyhan, B., Settle, J., Thorson, E., et al. (2023). Like-Minded Sources on Facebook Are Prevalent but Not Polarizing. Nature, 620, 137–144. https://doi.org/10.1038/s41586-023-06297-w

[5] Perra, N., & Rocha, L. E. C. (2019). Modelling Opinion Dynamics in the Age of Algorithmic Personalisation. Scientific Reports, 9, 7261. https://doi.org/10.1038/s41598-019-43830-2

[6] Chuang, Y.-S., Goyal, A., Harlalka, N., et al. (2024). Simulating Opinion Dynamics with Networks of LLM-Based Agents. Findings of the Association for Computational Linguistics: NAACL 2024, 3326–3346. https://aclanthology.org/2024.findings-naacl.211/

[7] DeGroot, M. H. (1974). Reaching a Consensus. Journal of the American Statistical Association, 69(345), 118–121. https://doi.org/10.1080/01621459.1974.10480137

[8] Friedkin, N. E., & Johnsen, E. C. (1990). Social Influence and Opinions. Journal of Mathematical Sociology, 15(3–4), 193–206. https://doi.org/10.1080/0022250X.1990.9990069

[9] Hegselmann, R., & Krause, U. (2002). Opinion Dynamics and Bounded Confidence Models, Analysis, and Simulation. Journal of Artificial Societies and Social Simulation, 5(3). https://www.jasss.org/5/3/2.html

[10] Grimm, V., Railsback, S. F., Vincenot, C. E., et al. (2020). The ODD Protocol for Describing Agent-Based and Other Simulation Models: A Second Update to Improve Clarity, Replication, and Structural Realism. Journal of Artificial Societies and Social Simulation, 23(2). https://doi.org/10.18564/jasss.4259

[11] Stasser, G., & Titus, W. (1985). Pooling of Unshared Information in Group Decision Making: Biased Information Sampling During Discussion. Journal of Personality and Social Psychology, 48(6), 1467–1478. https://doi.org/10.1037/0022-3514.48.6.1467

[12] Steinel, W., Utz, S., & Koning, L. (2010). The Good, the Bad and the Ugly Thing to Do When Sharing Information: Revealing, Concealing and Lying Depend on Social Motivation, Distribution and Importance of Information. Organizational Behavior and Human Decision Processes, 113(2), 85–96. https://doi.org/10.1016/j.obhdp.2010.07.001

[13] Kleinberg, J., & Raghavan, M. (2021). Algorithmic Monoculture and Social Welfare. Proceedings of the National Academy of Sciences, 118(22), e2018340118. https://doi.org/10.1073/pnas.2018340118

[14] OpenAI. (2025). Defining and Evaluating Political Bias in LLMs. https://openai.com/index/defining-and-evaluating-political-bias-in-llms/

[15] OpenAI. (2025). Collective Alignment: Public Input on Our Model Spec. https://openai.com/index/collective-alignment-aug-2025-updates/

[16] Anthropic. (2023). Collective Constitutional AI: Aligning a Language Model with Public Input. https://www.anthropic.com/news/collective-constitutional-ai-aligning-a-language-model-with-public-input

[17] Gottweis, J., & Natarajan, V. (2025). Accelerating Scientific Breakthroughs with an AI Co-Scientist. Google Research. https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/

[18] Microsoft. (2026). How Model Router Works in Microsoft Foundry. Microsoft Learn. https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router-how-it-works

[19] Google. (2026). Grounding with Google Search. Google AI for Developers. https://ai.google.dev/gemini-api/docs/google-search

[20] Mou, X., Wei, Z., & Huang, X. (2024). Unveiling the Truth and Facilitating Change: Towards Agent-based Large-scale Social Movement Simulation. Findings of the Association for Computational Linguistics: ACL 2024, 4789–4809. https://doi.org/10.18653/v1/2024.findings-acl.285

[21] Windrum, P., Fagiolo, G., & Moneta, A. (2007). Empirical Validation of Agent-Based Models: Alternatives and Prospects. Journal of Artificial Societies and Social Simulation, 10(2), 8. https://www.jasss.org/10/2/8.html

[22] Grimm, V., Revilla, E., Berger, U., et al. (2005). Pattern-Oriented Modeling of Agent-Based Complex Systems: Lessons from Ecology. Science, 310(5750), 987–991. https://doi.org/10.1126/science.1116681
