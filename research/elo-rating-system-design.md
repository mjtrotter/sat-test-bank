# Research: ELO rating system design for adaptive educational math platform targeting competition math students (MATHCOUNTS, AMC 8/10/12, AIME). Specifically need:

1. How to set the ELO scale for a math competition training app — should it mirror real competition ELO ranges (like AoPS's rating system) or use a custom scale? What are the tradeoffs?
2. Best practices for K-factor tuning in educational contexts (not chess) — how should K-factor vary for new students vs established, and how does it interact with Bayesian IRT models?
3. How to handle multi-dimensional ELO — students have separate ratings per skill domain (algebra, geometry, counting, number theory, etc.). How do platforms like AoPS, Brilliant, or Khan Academy handle per-topic ratings?
4. Cold-start problem — calibrating question difficulty WITHOUT historical student data. Specifically: using small language models (sub-1B parameter) to empirically estimate problem difficulty by measuring solve rates across multiple models. Is this approach documented anywhere? What are alternatives (expert tagging, IRT parameter estimation)?
5. Scale range — should ELO go to 2000? 2400? 3000? What do existing math competition rating systems use (Codeforces, AoPS, MATHCOUNTS)?
6. How Glicko-2 or TrueSkill compare to standard ELO for this use case — is the rating deviation (uncertainty) parameter worth the complexity?

Context: Building a native iOS adaptive training app for ~30 gifted middle school students (grades 6-8). Self-hosted inference on AMD MI50 GPUs. The app covers math competition prep (MVP), then expands to SAT and AP Writing. Need the rating system to handle 300-500+ atomic skill nodes across 6 math domains.

**Mode:** pro
**Thread:** https://www.perplexity.ai/search/elo-rating-system-design-for-a-TmlFw7VASkK2aZsak_A.4g
**Date:** 2026-03-28T01:02:17.410760

## Answer

For your use case, I would use a custom internal Elo-like scale, not a literal clone of AoPS or Codeforces. Keep the math-like interpretation internally, but choose anchors, update behavior, and displayed labels around your curriculum and question bank rather than around public contest rankings.
artofproblemsolving
+2

1) Scale design

A custom scale is usually better because your system is optimizing for instructional sequencing and skill diagnosis, not leaderboard prestige. AoPS’s own wiki uses a rough 1–10 difficulty scale tied to contest families, and explicitly says the ratings are approximate, contest-dependent, and meant to emphasize problem-solving over technicality; that is a good sign that a contest-prestige scale is not ideal as your product’s primary internal scale.
artofproblemsolving

Tradeoffs

Mirror a known competitive scale

Pros: easier for advanced students to interpret, familiar anchors, and you can map to AMC/AIME intuitively. Codeforces shows how a public Elo-like scale can create clear tiers such as Newbie through Legendary Grandmaster.
wikipedia

Cons: the absolute numbers become emotionally loaded, harder to tune for educational goals, and the scale may drift if your item bank is not similar to the external benchmark.
wikipedia

Use a custom scale

Pros: you can center the scale on your own item bank, grade band, and expected progression; it is easier to keep stable as you add SAT/AP Writing later.

Cons: users cannot compare it directly with AoPS/Codeforces, so you must provide good labels or percentile-style interpretation.

A practical compromise is: use a hidden internal scale for modeling, and show a friendly public-facing band system like Bronze/Silver/Gold or “AMC 8-ready / AMC 10-ready / AIME-ready.” AoPS’s contest rating pages already group problems by rough contest progression rather than a single universal score, which fits your product better than a prestige Elo number.
artofproblemsolving

2) K-factor tuning

For education, the K-factor should reflect how much you trust the current estimate and how quickly the student can actually change, not just how many games they have played. In the educational literature, Elo-style systems are attractive because they update online and can handle student-item interaction, while Glicko-2 adds an uncertainty/variance component that is useful when students have sparse or irregular practice histories.
eric.ed
+1

Suggested rule of thumb

New students: high K, because early evidence is noisy and you want fast personalization.

Established students: lower K, because their rating should move more slowly unless the evidence is strong.

After long inactivity: temporarily increase update sensitivity again, or use a model with rating deviation/uncertainty.

A good starting heuristic is:

New student: K in the rough range of 24–48

Established student: K in the rough range of 8–24

Very stable, high-confidence student: K as low as 4–12

That said, in education the cleaner pattern is often to let uncertainty drive the update, which is exactly where Glicko-2 or Bayesian IRT helps. Park’s K-12 math work explicitly adapts Glicko-2 for student ability and item difficulty in a learning setting, and notes that the method models change over time and can handle stratified content.
eric.ed

How it interacts with Bayesian IRT

If you already plan to use Bayesian IRT, do not treat Elo and IRT as competing black boxes. A common architecture is:

Elo/Glicko for fast online updates

Bayesian IRT for periodic recalibration, calibration of item parameters, and uncertainty-aware reporting

If you have Bayesian priors and posterior variances, those can directly inform K: high posterior uncertainty 
→
→ larger K, low posterior uncertainty 
→
→ smaller K. That makes the system more principled than a fixed K across all users. The literature on multivariate Glicko and multidimensional Elo in adaptive learning supports this general direction.
acm
+2

3) Multi-dimensional ratings

For 300–500 atomic nodes across algebra, geometry, counting, and number theory, I would use separate domain ratings plus a global latent rating, not a single flat Elo. The educational literature shows that multidimensional Elo variants exist precisely because the unidimensional assumption breaks down when items measure more than one skill.
educationaldatamining
+2

Best-practice structure

Global ability rating: overall problem-solving strength.

Domain ratings: algebra, geometry, number theory, counting, etc.

Prerequisite/cluster ratings: optional subskills like modular arithmetic, angle chasing, invariants, combinatorics counts.

A simple and effective implementation is:

Each problem tags 1–3 skills.

The student gets one update distributed across those skills, weighted by tag strength.

The global rating is a weighted aggregate of domain ratings.

This is closer to how adaptive educational systems actually behave than a single monolithic Elo. Research on multivariate Elo-based learner models found that extra parameters can help both adaptive behavior and insight for students and instructors, and a 2025 EDM paper found multidimensional Elo extensions outperform unidimensional Elo when the underlying data are multidimensional.
eric.ed
+1

How AoPS, Brilliant, Khan differ

AoPS: publicly emphasizes contest/problem difficulty grouping more than per-student skill vectors; its wiki uses rough contest-aligned difficulty levels and interpolation across contest families.
artofproblemsolving

Khan Academy: uses mastery levels like Not Started, Attempted, Familiar, Proficient, and Mastered rather than a visible Elo rating, which is better for teaching prerequisites and progress than for fine-grained skill competition.
khanacademy
+1

Brilliant: publicly emphasizes interactive STEM problem-solving and progress tracking, but I did not find a documented public multi-dimensional Elo system for per-topic ratings in the sources I checked.
brighterly

4) Cold start and difficulty calibration

Yes, there is now documented work on using language models to estimate item difficulty, but the evidence is stronger for hybrid prediction pipelines than for “let a small model solve it and infer difficulty from solve rate” as a standalone gold standard. A 2025 study on item difficulty modeling found that direct LLM estimates can correlate with true difficulty, but feature-based LLM pipelines were stronger and more stable.
arxiv

What the literature suggests

Direct LLM judgment: prompt a model to rate item difficulty.

Feature-based LLM pipeline: extract interpretable features, then train a regressor.

Simulation / solve-rate estimation: use model attempts or simulated responses, then fit an IRT model.

The 2026 paper on question difficulty using LLM student responses explicitly frames simulated responses plus IRT as a way to estimate difficulty when real field testing is expensive. That is the closest match to your idea of measuring solve rates across multiple models, and it is more defensible if you treat it as a prior initializer rather than final truth.
arxiv

Is sub-1B multi-model solve-rate estimation documented?

I did not find a paper specifically saying “use multiple sub-1B language models to empirically estimate math problem difficulty for an educational platform.” What is documented is:

LLM-based item difficulty prediction
arxiv

LLM/student simulation plus IRT calibration
arxiv

small/large model use for difficulty modeling in educational assessment contexts
pmc.ncbi.nlm.nih
+1

Better alternatives for cold start

Expert tagging: fastest and most reliable at the start.

Content-based heuristics: problem length, number of steps, theorem load, diagram complexity, and prerequisite depth.

Bootstrap IRT: start with expert priors, then update from student responses.

LLM-assisted triage: use models to rank or cluster items, then verify with experts.

For your small cohort of 30 students, I would strongly recommend expert calibration first, then let the model learn online. Pure solve-rate calibration from small models is interesting, but it is not yet a mature replacement for human or IRT-based initialization.
arxiv
+1

5) Scale range

For your app, I would not force the scale to 2000, 2400, or 3000 unless you need a public leaderboard vibe. Those numbers are mostly presentation choices; what matters is whether the scale has enough resolution and whether the mean and variance are stable. Codeforces uses a public Elo-like ladder that reaches 3000+ for Legendary Grandmaster, while AoPS uses a much coarser 1–10 contest difficulty scale for problems.
wikipedia
+1

Practical recommendation

Use:

Internal model scale centered around something like 1500 or 0

Displayed user scale mapped to grades or mastery bands

For example:

0–1000: early middle-school fundamentals.

1000–1600: AMC 8/10 core.

1600–2200: AMC 10/12 stretch.

2200+: AIME and above.

That gives you room without pretending to be Codeforces. If you later need more precision, you can expand the numeric range without changing the model semantics.

6) Glicko-2 vs TrueSkill vs Elo

For this product, plain Elo is the easiest MVP, but Glicko-2 is probably the best next step if you want uncertainty-aware personalization without full Bayesian complexity. Educational work has already adapted Glicko-2 to K-12 math learning settings, and TrueSkill has also been studied for student ability estimation in educational environments, with evidence that it can perform comparably to IRT and may be more robust in small-sample settings.
unt
+1

Decision guide
Method	Best for	Pros	Cons
Elo	Simple MVP	Easy to implement, fast updates	No uncertainty term, can be brittle with sparse data
Glicko-2	Adaptive learning with sparse/inactive users	Adds rating deviation, handles uncertainty and time gaps	More complex than Elo
TrueSkill	Multivariate/sparse inference	Natural uncertainty modeling, handles team-like latent updates well	More engineering complexity; less standard in edtech
Bayesian IRT	Calibration and reporting	Strong measurement grounding, interpretable item/student parameters	Heavier implementation, usually batch-oriented
Is uncertainty worth it?

Yes, for your setting it probably is. You have:

only ~30 students initially,

irregular practice,

300–500 item nodes,

and likely rapid growth in content domains.

That is exactly the kind of environment where uncertainty matters, because the system should know when it does not know. Glicko-2 and TrueSkill help with that, while plain Elo does not.
unt
+2

Recommended architecture

For your MVP, I would build this:

Item bank

Expert-tag each item with 1–3 domains and prerequisite nodes.

Give each item a starting difficulty prior from experts plus LLM-assisted heuristics.

Student model

Maintain a global ability rating.

Maintain domain ratings for the 6 math domains.

Optionally maintain a confidence/uncertainty value per rating.

Update engine

Start with Glicko-2 or a simplified Glicko-like system.

Use a higher update rate for new students.

Decay confidence with inactivity.

Offline calibration

Periodically fit a Bayesian IRT model to student response logs.

Use that to re-anchor item difficulty and validate your online ratings.

UI

Show mastery bands and topic readiness.

Hide the raw numeric rating unless you have a strong reason to expose it.

If you want, I can turn this into a concrete rating-system spec with:

exact formulas,

recommended initial priors,

a K-factor schedule,

domain-tag update rules,

and a data schema for your iOS backend.

(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'9e3413af8c9edacd',t:'MTc3NDY3NDA4Ni4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();

## Sources

1. [artofproblemsolving](https://artofproblemsolving.com/wiki/index.php/AoPS_Wiki:Competition_ratings)
2. [wikipedia](https://en.wikipedia.org/wiki/Codeforces)
3. [eric.ed](https://files.eric.ed.gov/fulltext/ED615621.pdf)
4. [brighterly](https://brighterly.com/blog/brilliant-vs-khan-academy/)
5. [arxiv](https://arxiv.org/pdf/2504.08804.pdf)
6. [arxiv](https://arxiv.org/html/2601.09953v1)
