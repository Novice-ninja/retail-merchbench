# Retail MerchBench Positioning Matrix

| Work | Domain | Task Type | Evaluation Object | Scoring Method | What It Teaches | Retail MerchBench Difference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| March 2026 retail-operations agent benchmark | Retail operations / supermarket simulation | Long-horizon autonomous decisions | LLM agent strategy and execution | Operational stability and efficiency in simulated environments | Whether agents can maintain strategy under stochastic demand | Retail MerchBench isolates merchant judgment and model-routing fit before adding long-horizon simulation. |
| tau-bench | Retail and airline customer service | Multi-turn tool-agent-user interactions | Tool-using conversational agents | End-state database correctness and pass^k reliability | Whether agents follow policies and use tools consistently | Retail MerchBench evaluates planning decisions, not customer-service workflows. |
| tau2-bench | Telecom support | Dual-control agent/user environment | Conversational agents coordinating with user actions | Task success and ablations by reasoning/coordination | How shared-state user control affects agents | Retail MerchBench is static and segment-scored; it does not evaluate shared-state tool use. |
| WebShop | E-commerce | Simulated product search and purchase | Shopping agents | Task success in web environment | Grounded language agents struggle with shopping navigation | Retail MerchBench is internal merchant-side planning, not consumer shopping. |
| ShoppingBench | E-commerce | Complex shopping intents | Shopping agents in product sandbox | Success rate over intent-grounded tasks | Modern agents still struggle with realistic shopping goals | Retail MerchBench focuses on buy, allocation, pricing, promotion, and operational judgment. |
| ShoppingComp | Open-world shopping | Retrieval, report generation, safety | Shopping agents | Accuracy, report quality, safety checks | Shopping recommendations can fail under constraints and safety requirements | Retail MerchBench translates risk-aware decision making to retail planning economics. |
| WebMall | Multi-shop e-commerce | Comparison shopping across shops | Web agents | Completion rate, F1, efficiency | Multi-shop shopping creates longer trajectories and heterogeneous data | Retail MerchBench does not evaluate consumer cross-shop search. |
| HELM | General language models | Broad scenario and metric coverage | Language models | Multi-metric standardized evaluation | Transparent benchmark reporting matters | MerchBench should adopt multi-metric reporting and prompt/response disclosure |
| LiveBench | General language models | Frequently updated reasoning/coding/data tasks | Language models | Objective scoring and rolling updates | Static public benchmarks contaminate quickly | MerchBench should version scenarios and consider a private/rotating split |
| MT-Bench / Chatbot Arena | Chat assistants | Multi-turn open-ended responses | Chat models and LLM judges | LLM-as-judge with human agreement analysis | LLM judges can scale evaluation but need bias checks | Retail MerchBench uses automated scoring as a routing prior and reserves final claims for human calibration. |
| M5 Forecasting | Retail/Walmart | Hierarchical demand forecasting | Forecasting models | Forecast accuracy metrics | Forecasting can be benchmarked rigorously with real data | Retail MerchBench is about planning judgment after or around forecasts. |
| Dominick's Dataset | Grocery retail | Sales, pricing, promotions | Econometric/retail models | Research-specific quantitative analysis | Promotions, pricing, and scanner data shape retail decisions | Retail MerchBench uses these concepts for task realism, but it is not a forecasting dataset. |

## Positioning Summary

Retail MerchBench should be framed as a **judgment and model-routing benchmark** rather than a forecasting, shopping-agent, customer-service-agent, or full retail-simulation benchmark.

The core claim is that a planner's value often comes from deciding whether the data and question are valid before doing the math. This makes static judgment scenarios academically defensible because they isolate the decision-quality layer that agent benchmarks often mix with tools, memory, environment design, and web navigation.

## Recommended Public Language

Use:

> Retail MerchBench evaluates whether LLMs can approximate experienced merchandise-planning judgment: filtering weak evidence, reframing bad questions, respecting constraints, calibrating uncertainty, and anticipating economic consequences.

Avoid:

> Retail MerchBench predicts retail demand.

Avoid:

> Retail MerchBench is a full retail operating simulator.

Avoid:

> Retail MerchBench evaluates online shopping agents.
