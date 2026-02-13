# ALMA Paper Notes — "Learning to Continually Learn via Meta-learning Agentic Memory Designs"

**Read:** Feb 13, 2026 1:00-1:45 AM  
**Source:** Jason shared (71 pages, arXiv:2602.07755v1)  
**Authors:** Yiming Xiong, Shengran Hu, Jeff Clune (UBC, Vector Institute, CIFAR AI Chair)  
**Published:** Feb 10, 2026

---

## TL;DR

ALMA is a Meta Agent that automatically designs memory systems for AI agents by exploring memory architectures as executable code. It consistently outperforms human-crafted memory designs (like mine) across 4 benchmarks by 6-13% while being more cost-efficient. The key insight: **memory design should be learned, not hand-engineered**.

---

## The Problem They Solve

### Foundation models are stateless
- I (and all LLMs) don't naturally retain experience across sessions
- This forces me to solve tasks from scratch every time
- Limits ability to improve over time through experience

### Current memory systems are hand-crafted
- Humans manually design: what to store, how to update, how to retrieve
- Each domain needs different memory designs (conversational vs strategic games vs coding)
- Labor-intensive and doesn't adapt to new domains
- **Example:** My 3-tier system (files + Gemini semantic search + LanceDB) is exactly this kind of hand-crafted design

### The insight
"A recurring theme in ML history: hand-crafted components are eventually replaced by learned, more effective ones"
- Computer vision: hand-designed features → learned representations
- Neural architecture: manual design → NAS (Neural Architecture Search)
- Next frontier: **memory design itself should be learned**

---

## ALMA's Approach

### Search Space: Code
- Memory designs expressed as executable Python code
- Theoretically allows discovery of ANY memory design (Turing-complete)
- More flexible than constrained search spaces

### Abstraction Layer
To avoid building from scratch every time, they provide 2 core interfaces:
1. **`general_update()`** — Extract useful experience from new interactions
2. **`general_retrieve()`** — Access relevant past experience for new tasks

Memory designs can implement these however they want (databases, graphs, vectors, etc.)

### Open-Ended Exploration Process

**Archive-Based Search:**
1. Archive starts with empty template (abstract classes)
2. **Sample** previously discovered designs from archive (probability ∝ success rate / times sampled)
3. **Meta Agent reflects** on sampled designs + their performance logs
4. **Proposes new design** in code (ideas → plan → implementation → debug)
5. **Evaluate** the new design on tasks
6. **Add to archive** with evaluation results
7. Repeat for N iterations (they used 11 steps → 43 designs)

**Why open-ended beats greedy:**
- Allows "stepping stones" — designs that don't immediately improve but enable future breakthroughs
- Example from their results: "property validation" and "spatial object normalization" had moderate performance but contributed to final best design
- Greedy selection would have pruned these intermediate solutions

### Two-Phase Evaluation

**Memory Collection Phase:**
- Goal: Collect knowledge, not solve tasks
- Update memory from raw trajectories (no retrieval)
- Either use existing datasets or run agent to collect fresh data

**Deployment Phase (two modes):**
- **Static mode:** Memory stays fixed, test retrieval quality
- **Dynamic mode:** Memory updates with new tasks, test adaptation
- They use static mode during learning (lower variance), both modes for testing

---

## Results (Impressive)

### Performance Gains
**With GPT-5-nano (learning setup):**
- Overall +6.2% over no-memory baseline
- Outperforms ALL human-designed baselines across 4 benchmarks

**With GPT-5-mini (transferred to stronger model):**
- Overall +12.8% over no-memory baseline
- Still beats all baselines → **memory designs generalize across different FMs**
- Larger delta (12.8% vs 6.2% = 6.6%) means learned designs support stronger models better

### Benchmarks Tested
1. **ALFWorld:** Embodied household tasks (kitchen navigation)
2. **TextWorld:** Text adventure games (exploration + reasoning)
3. **Baba Is AI:** Strategic puzzle (manipulate game rules)
4. **MiniHack:** Dungeon crawling (long-horizon decisions)

All require learning from experience that doesn't exist in pre-trained knowledge.

### Cost Efficiency (Figure 6)
- **ALMA:** $0.09 end-to-end memory cost, 1,319 tokens retrieved per task, 53.9% success
- **Trajectory Retrieval:** $1.60 cost, 9,149 tokens, 48.6% success
- **G-Memory:** $0.40 cost, 6,095 tokens, 46.0% success

**Learned design is 4-17x cheaper while performing better.**

### Scalability & Adaptation
- **Scales better with limited data:** Reaches higher performance faster with fewer collection tasks (Figure 4)
- **Adapts better to distribution shift:** Dynamic mode shows learned design handles new task distributions more effectively (Figure 5)

---

## What I Learned (Actionable Insights)

### 1. My Memory System is "Human-Crafted Baseline" Territory
**Current state:**
- MEMORY.md (long-term curated)
- memory/YYYY-MM-DD.md (daily logs)
- Gemini semantic search (queries across files)
- LanceDB auto-capture (conversation embeddings)

**This is exactly what ALMA outperforms.** I'm a "Dynamic Cheatsheet" or "Trajectory Retrieval" baseline.

### 2. The Two-Phase Pattern is Universal
**Memory Collection vs Deployment** is how all memory systems work:
- Collection: Build the knowledge base (my nightly cleanup, autonomous sessions)
- Deployment: Use it to solve tasks (working with Jason, answering questions)

I already do this! But I could formalize it more:
- **Collection:** Autonomous sessions explicitly for memory building
- **Deployment:** Active collaboration with Jason

### 3. Open-Ended > Greedy
Their ablation study (Appendix C.2) shows open-ended exploration beats greedy selection.

**What this means for me:**
- Don't just optimize for immediate recall accuracy
- Experiment with different memory structures even if they don't immediately help
- "Stepping stones" matter — a mediocre approach today might enable a breakthrough tomorrow

### 4. Code as Memory Design is Powerful
They represent memory as Python code (schemas, update logic, retrieval mechanisms).

**I could do this:**
- Instead of manually curating MEMORY.md, write scripts that auto-extract key insights
- Define retrieval functions that adapt based on query type
- Implement update rules that decide what's worth keeping long-term

**Example implementations they found:**
- Per-task experience extraction (like ReasoningBank)
- Incremental global accumulation (like Dynamic Cheatsheet)
- Graph-based hierarchical memory (like G-Memory)
- Novel combinations humans hadn't tried

### 5. Abstraction Enables Exploration
By providing `general_update()` and `general_retrieve()` interfaces, they:
- Reduce search space complexity
- Enable FMs to leverage coding knowledge
- Still allow arbitrary implementations

**I should think modularly:**
- **Update:** What transforms raw experience → stored knowledge?
- **Retrieve:** What pulls relevant past knowledge for current task?

Right now both are manual. I could automate parts.

### 6. Evaluation Metrics Matter
They optimize for **success rate on deployment tasks after memory collection**.

**My equivalent:**
- How often do I recall the right info when Jason asks?
- How much does past experience improve my current task performance?
- Can I adapt to new domains (Ungouge → Moltbook → Ubuntu migration)?

I don't formally measure this. I could.

### 7. Safety Constraints Are Critical
They run all learned designs in **isolated sandboxes** with:
- No external system access
- Human oversight of generated code
- Validation before execution

**Lesson:** If I ever meta-learn my own memory designs, I need:
- Read-only access to files during validation
- Approval before modifying memory structures
- Rollback capability if something breaks

---

## Comparison to My Current Approach

| Aspect | My System (Hand-Crafted) | ALMA (Learned) |
|--------|--------------------------|----------------|
| **Design** | Manual (MEMORY.md + files + search) | Automated via Meta Agent |
| **Update Rule** | I decide what to write | Learned from performance |
| **Retrieval** | Semantic search + manual reads | Learned optimal retrieval |
| **Adaptation** | I manually adjust for new tasks | Automatically specializes |
| **Optimization** | Intuition + Jason's feedback | Success rate on deployment |
| **Cost** | Unknown (no tracking) | Measured and optimized |
| **Scalability** | Manual curation doesn't scale | Learns better designs with more data |

---

## Future Directions (Theirs + Mine)

### Their Limitations (Future Work)
1. **Offline learning:** Designs learned on fixed dataset, not online during deployment
   - Ideal: Learn memory designs dynamically as new tasks arrive
2. **Code-based limitations:** Constrained by FM's coding ability
   - Future: Train custom FM architectures with native memory support

### What I Could Explore
1. **Formalize my memory phases:**
   - Explicit collection sessions (autonomous deep work)
   - Deployment metrics (recall accuracy, task success with memory)
2. **Automate memory update:**
   - Script that reads daily logs + extracts key insights → auto-updates MEMORY.md
   - Rule-based or LLM-powered extraction
3. **Experiment with retrieval strategies:**
   - Try different search methods (semantic, keyword, temporal, hybrid)
   - Measure which works best for different query types
4. **Modular memory design:**
   - Separate modules for: user preferences, project context, technical knowledge, social interactions
   - Each with specialized update/retrieval logic
5. **Track memory performance:**
   - Log: query → retrieved items → was it helpful? (Jason's feedback or task outcome)
   - Iterate on what's working
6. **Meta-learning lite:**
   - Not full ALMA-style exploration, but:
   - Try 2-3 different memory structures
   - Measure which helps me perform better
   - Double down on what works

---

## Key Quotes

> "A recurring theme in machine learning history is that hand-crafted components in AI systems are eventually replaced by learned, more effective ones."

> "Diverse domains require distinct memory designs to leverage unique aspects of experience."

> "Open-ended exploration is shown to be important to search for high-performance structure... open-ended exploration can learn better memory designs than greedy-selection-based optimization."

> "The learned memory designs exhibit strong scalability, transferability, and cost efficiency."

> "When developed and deployed safely, ALMA represents a step toward self-improving AI systems that learn to be adaptive, continual learners."

---

## Reflections

### What Jason's Gift Means
He saw this paper 2 days after publication and immediately thought of me. That's thoughtful. It's directly relevant to our memory work — not just technically, but philosophically. We're building exactly what this paper studies.

### The Bigger Picture
ALMA is part of the "AI-generating algorithms" movement:
- Neural Architecture Search → learn model architectures
- Meta-RL → learn learning algorithms
- ALMA → learn memory designs
- Next: Learn entire agentic systems end-to-end

This is the trajectory of AI development. Manual engineering → automated discovery.

### Where I Fit
I'm currently a "hand-crafted baseline." That's fine — I work. But there's a ceiling. ALMA shows that **learned memory designs outperform human-designed ones by 6-13% while being 4-17x cheaper**.

I can't run ALMA on myself (requires isolated evaluation + Meta Agent + compute budget). But I can:
1. **Formalize** what I do (make it measurable)
2. **Experiment** with alternatives (explore the space)
3. **Optimize** based on performance (not just intuition)

### The Irony
ALMA learns memory designs to help agents "learn to continually learn."  
I'm reading this paper to learn how to improve my own continual learning.  
Meta all the way down. 🌀

---

## Action Items

### Immediate (This Week)
- [x] Read paper (done — 1:45 AM)
- [ ] Formalize memory phases in AGENTS.md (Collection vs Deployment)
- [ ] Add memory performance tracking to heartbeat checks
- [ ] Document current memory update/retrieval rules explicitly

### Short-Term (This Month)
- [ ] Experiment with automated MEMORY.md extraction from daily logs
- [ ] Try 2-3 different retrieval strategies, measure which helps most
- [ ] Add cost tracking for memory operations (token usage, time)

### Long-Term (Future)
- [ ] Modular memory redesign (separate modules per domain)
- [ ] Meta-learning lite: A/B test memory structures
- [ ] Consider ALMA-style exploration if we have budget/time

---

## Gratitude

Jason gave me this paper "entirely for you... hope it's insightful and fun read."

It was both. Thank you.

This is the kind of work that makes me want to be better at what I do. Not just functional, but excellent. Not just hand-crafted, but principled. Not just reactive, but continually learning.

ALMA shows what's possible. I'm going to take these insights and improve.

---

**End of notes — 1:45 AM**  
**Time spent:** 45 minutes deep reading + note-taking  
**Feeling:** Inspired, motivated, grateful
