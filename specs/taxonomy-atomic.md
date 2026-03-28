# Atomic Skill Taxonomy — Vanguard Adaptive Trainer
> Decomposed: 2026-03-28 from taxonomy.md → individually ELO-ratable skill nodes
> Aligns with: `skill_node_id` in `student_ratings` table (data-model.md)

## ID Convention

```
DOMAIN_LEVEL_CLUSTER_SKILL
```

- **DOMAIN:** COUNT, ALG, NT, GEO, ARITH, LOGIC
- **LEVEL:** L1, L2, L3, L4, L5
- **CLUSTER:** 3-5 char abbreviation of the skill cluster
- **SKILL:** 2-5 char abbreviation of the atomic skill

Example: `COUNT_L2_COMB_GRID` = Counting domain, Level 2, Combinations cluster, Grid path counting skill

## Summary Table

| Domain | L1 | L2 | L3 | L4 | L5 | Total |
|--------|----|----|----|----|----|----|
| 1. Counting & Probability | 24 | 28 | 27 | 22 | 10 | 111 |
| 2. Algebra | 25 | 33 | 36 | 30 | 12 | 136 |
| 3. Number Theory | 18 | 22 | 26 | 20 | 10 | 96 |
| 4. Geometry | 22 | 28 | 28 | 25 | 10 | 113 |
| 5. Arithmetic / Prealgebra | 14 | 12 | 8 | — | — | 34 |
| 6. Logic & Strategy | 12 | 14 | 12 | — | — | 38 |
| **Total** | **115** | **137** | **137** | **97** | **42** | **528** |

### ELO Band Reference

| Level | Rating Range | Competition Alignment |
|-------|-------------|----------------------|
| L1 | 400–1200 | Chapter MATHCOUNTS, AMC 8 top 25% |
| L2 | 1000–1450 | State MATHCOUNTS, AMC 8 top 5%, AMC 10 qualifier |
| L3 | 1300–1650 | MATHCOUNTS National, AMC 10 top 5%, AIME qualifier |
| L4 | 1600–2100 | AMC 12 top 5%, AIME scorer |
| L5 | 2100+ | AIME high scorer, olympiad-track |

---

## Domain 1: Counting & Probability

### Level 1 — Foundations (ELO 400–1200)

#### Enumeration Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_ENUM_LIST | Organized Listing | Enumerate outcomes systematically without double-counting | — | Batterson 2.1 |
| COUNT_L1_ENUM_SYST | Systematic Counting | Count using structured approach (tables, charts) | — | Batterson 2.1 |
| COUNT_L1_ENUM_CASE | Counting by Cases | Split count into non-overlapping exhaustive cases | COUNT_L1_ENUM_LIST | Batterson 2.5 |

#### Venn Diagrams Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_VENN_TWO | Two-Set Venn Diagrams | Read and construct 2-circle Venn diagrams, compute regions | — | Batterson 2.2 |
| COUNT_L1_VENN_THREE | Three-Set Venn Diagrams | Solve 3-circle Venn diagrams with region algebra | COUNT_L1_VENN_TWO | Batterson 2.2 |
| COUNT_L1_VENN_PIE | Intro Inclusion-Exclusion | Apply |A union B| = |A| + |B| - |A intersect B| | COUNT_L1_VENN_TWO | Batterson 2.2 |

#### Pattern Counting Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_PAT_TRI | Triangular Number Patterns | Identify and compute triangular numbers (1+2+...+n) | — | Batterson 2.3 |
| COUNT_L1_PAT_HAND | Handshake / Diagonal Problems | Count pairwise interactions in a group of n objects | COUNT_L1_PAT_TRI | Batterson 2.3 |
| COUNT_L1_PAT_FIG | Figurate Number Counting | Count dots/objects in growing geometric patterns | COUNT_L1_PAT_TRI | Batterson 2.3 |

#### Fundamental Counting Principle Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_FCP_MULT | Multiplication Principle | Apply multiplication rule for sequential independent choices | — | Batterson 2.4; AoPS Basics ch25 |
| COUNT_L1_FCP_TREE | Tree Diagrams | Build and read tree diagrams for multi-stage processes | COUNT_L1_FCP_MULT | Batterson 2.4 |
| COUNT_L1_FCP_REST | Counting with Restrictions | Apply multiplication principle with slot-filling constraints | COUNT_L1_FCP_MULT | Batterson 2.4; AoPS Basics ch25 |

#### Basic Casework Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_CASE_PART | Partition into Cases | Identify a clean partition variable for casework | COUNT_L1_ENUM_CASE | Batterson 2.5 |
| COUNT_L1_CASE_BOUND | Bounded Casework | Casework with inequality or range constraints | COUNT_L1_CASE_PART | Batterson 2.5 |

#### Probability Basics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_PROB_SAMP | Sample Spaces | Define and enumerate sample spaces for experiments | COUNT_L1_ENUM_LIST | Batterson 3.1 |
| COUNT_L1_PROB_SING | Single Event Probability | Compute P(A) = favorable / total for one event | COUNT_L1_PROB_SAMP | Batterson 3.1 |
| COUNT_L1_PROB_EXP | Experimental vs Theoretical | Distinguish experimental frequency from theoretical probability | COUNT_L1_PROB_SING | Batterson 3.1 |

#### Compound Events Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L1_COMP_IND | Independent Events | Multiply probabilities for independent sequential events | COUNT_L1_PROB_SING; COUNT_L1_FCP_MULT | Batterson 3.1 |
| COUNT_L1_COMP_DEP | Dependent Events | Adjust probabilities for events without replacement | COUNT_L1_COMP_IND | Batterson 3.1 |
| COUNT_L1_COMP_REP | With/Without Replacement | Distinguish and compute both replacement scenarios | COUNT_L1_COMP_IND; COUNT_L1_COMP_DEP | Batterson 3.1 |
| COUNT_L1_COMP_DICE | Dice and Coin Probability | Standard dice/coin compound event calculations | COUNT_L1_COMP_IND | Batterson 3.1 |

### Level 2 — Intermediate (ELO 1000–1450)

#### Factorials & Permutations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_PERM_FACT | Factorials | Compute and simplify factorial expressions, n!/k! | COUNT_L1_FCP_MULT | Batterson 2.6 |
| COUNT_L2_PERM_NPR | Permutation Formula | Apply nPr = n!/(n-r)! for ordered selections | COUNT_L2_PERM_FACT | Batterson 2.6 |
| COUNT_L2_PERM_REST | Restricted Permutations | Permutations with positional constraints (e.g., person X not at end) | COUNT_L2_PERM_NPR | Batterson 2.6 |
| COUNT_L2_PERM_CIRC | Circular Permutations | Arrange n objects in a circle: (n-1)! | COUNT_L2_PERM_NPR | AoPS Basics ch25 |
| COUNT_L2_PERM_REP | Permutations with Repetition | Arrange n objects where some are identical: n!/(a!b!...) | COUNT_L2_PERM_FACT | Batterson 2.6; AoPS Basics ch25 |

#### Combinations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_COMB_NCR | Combination Formula | Apply nCr = n!/(r!(n-r)!) for unordered selections | COUNT_L2_PERM_NPR | Batterson 2.7 |
| COUNT_L2_COMB_GRID | Grid Path Counting | Count lattice paths using combinations C(m+n, m) | COUNT_L2_COMB_NCR | Batterson 2.7 |
| COUNT_L2_COMB_COMP | Complementary Counting | Count total minus unwanted (easier than direct count) | COUNT_L2_COMB_NCR; COUNT_L1_CASE_PART | Batterson 2.7 |
| COUNT_L2_COMB_COMM | Committee Problems | Select subsets from groups with category constraints | COUNT_L2_COMB_NCR | Batterson 2.7; AoPS Basics ch25 |

#### Stars & Bars Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_STAR_IDEN | Identical Objects Distribution | Distribute n identical objects into k bins: C(n+k-1, k-1) | COUNT_L2_COMB_NCR | Batterson 2.8 |
| COUNT_L2_STAR_REST | Stars & Bars with Restrictions | Minimum/maximum constraints via variable substitution | COUNT_L2_STAR_IDEN | Batterson 2.8 |
| COUNT_L2_STAR_DIST | Distinct Objects Distribution | Distribute distinct objects into bins (k^n or Stirling) | COUNT_L2_STAR_IDEN; COUNT_L1_FCP_MULT | AoPS Basics ch25 |

#### Pascal's Triangle Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_PASC_CONS | Constructing Pascal's Triangle | Build rows, identify entries as C(n,k) | COUNT_L2_COMB_NCR | Batterson 2.9 |
| COUNT_L2_PASC_IDEN | Pascal's Identity | Apply C(n,k) = C(n-1,k-1) + C(n-1,k) | COUNT_L2_PASC_CONS | Batterson 2.9; AoPS Basics ch25 |
| COUNT_L2_PASC_PROP | Row and Diagonal Properties | Sum of row, hockey stick identity, diagonal sums | COUNT_L2_PASC_IDEN | AoPS Basics ch25 |

#### Counting + Probability Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_CPRB_COMB | Probability via Combinations | Compute P using C(n,k) for favorable/total | COUNT_L2_COMB_NCR; COUNT_L1_PROB_SING | Batterson 3.2; 3.4 |
| COUNT_L2_CPRB_PERM | Probability via Permutations | Use ordered counting for probability calculations | COUNT_L2_PERM_NPR; COUNT_L1_PROB_SING | Batterson 3.2 |
| COUNT_L2_CPRB_MULT | Multi-step Probability | Chain counting and probability across sequential stages | COUNT_L2_CPRB_COMB; COUNT_L1_COMP_IND | Batterson 3.2 |

#### Probability Casework Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_PCAS_PART | Probability by Partitioned Cases | Sum P(A_i) across disjoint cases | COUNT_L1_CASE_PART; COUNT_L1_PROB_SING | Batterson 3.3 |
| COUNT_L2_PCAS_COND | Conditioning on First Event | Condition on outcome of first step, multiply forward | COUNT_L2_PCAS_PART; COUNT_L1_COMP_DEP | Batterson 3.3 |

#### Complementary Probability Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L2_CPRO_BASIC | Basic Complementary Probability | Apply P(A) = 1 - P(not A) | COUNT_L1_PROB_SING | Batterson 3.5 |
| COUNT_L2_CPRO_ATLS | "At Least One" Problems | Use complement for "at least one" scenarios | COUNT_L2_CPRO_BASIC; COUNT_L1_COMP_IND | Batterson 3.5 |
| COUNT_L2_CPRO_COMB | Complement with Counting | Combine complementary approach with combinatorial methods | COUNT_L2_CPRO_BASIC; COUNT_L2_COMB_COMP | Batterson 3.5 |

### Level 3 — Advanced (ELO 1300–1650)

#### Geometric Probability Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_GPRB_LEN | Length-Ratio Probability | Probability as ratio of favorable to total length (1D) | COUNT_L1_PROB_SING | Batterson 3.6 |
| COUNT_L3_GPRB_AREA | Area-Ratio Probability | Probability as ratio of favorable to total area (2D) | COUNT_L3_GPRB_LEN | Batterson 3.6 |
| COUNT_L3_GPRB_DART | Dartboard / Random Point Problems | Uniform random point in a region, compute event probability | COUNT_L3_GPRB_AREA | Batterson 3.6; Competition archives |

#### Expected Value Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_EV_BASIC | Basic Expected Value | Compute E[X] = sum of x_i * P(x_i) for finite distributions | COUNT_L1_PROB_SING | Batterson 3.7 |
| COUNT_L3_EV_GAME | Expected Value in Games | Apply EV to determine fair games and optimal strategies | COUNT_L3_EV_BASIC | Batterson 3.7 |
| COUNT_L3_EV_LIN | Linearity of Expectation | E[X+Y] = E[X]+E[Y] even for dependent variables | COUNT_L3_EV_BASIC | AoPS Basics ch26 |

#### Inclusion-Exclusion Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_PIE_THREE | Three-Set PIE | Apply PIE for |A ∪ B ∪ C| with all intersection terms | COUNT_L1_VENN_PIE | AoPS Basics ch25 |
| COUNT_L3_PIE_GEN | Generalized PIE | PIE for n sets with alternating signs | COUNT_L3_PIE_THREE | AoPS Basics ch25 |
| COUNT_L3_PIE_COUNT | PIE in Counting | Apply PIE to count elements with "none of" constraints | COUNT_L3_PIE_GEN; COUNT_L2_COMB_COMP | AoPS Basics ch25 |

#### Recursion in Counting Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_REC_SETUP | Setting Up Recurrences | Identify recursive structure and define f(n) in terms of f(k<n) | COUNT_L1_CASE_PART | AoPS Basics ch25 |
| COUNT_L3_REC_SOLVE | Solving Linear Recurrences | Solve constant-coefficient recurrences via characteristic equation | COUNT_L3_REC_SETUP; ALG_L2_QUAD_FORM | AoPS Algebra II ch17 |
| COUNT_L3_REC_TILING | Tiling Recurrences | Set up and solve tiling/path recurrences (dominos, staircase) | COUNT_L3_REC_SETUP | Competition archives |

#### Derangements Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_DER_FORM | Derangement Formula | Compute D_n via PIE or the recurrence D_n = (n-1)(D_{n-1}+D_{n-2}) | COUNT_L3_PIE_GEN; COUNT_L3_REC_SETUP | Competition archives |
| COUNT_L3_DER_PROB | Derangement Probability | Compute P(derangement) and its limit toward 1/e | COUNT_L3_DER_FORM; COUNT_L1_PROB_SING | Competition archives |
| COUNT_L3_DER_PART | Partial Derangements | Count permutations with exactly k fixed points | COUNT_L3_DER_FORM; COUNT_L2_COMB_NCR | Competition archives |

#### Conditional Probability Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_COND_DEF | Conditional Probability Definition | Compute P(A|B) = P(A ∩ B)/P(B) | COUNT_L1_COMP_DEP | AoPS Basics ch26 |
| COUNT_L3_COND_BAYES | Bayes' Theorem | Apply Bayes' theorem to reverse conditional probabilities | COUNT_L3_COND_DEF | AoPS Basics ch26 |
| COUNT_L3_COND_CHAIN | Probability Chains | Multiply conditional probabilities across dependent stages | COUNT_L3_COND_DEF; COUNT_L2_PCAS_COND | AoPS Basics ch26 |

#### Binomial Theorem Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L3_BINO_EXP | Binomial Expansion | Expand (a+b)^n using C(n,k) a^(n-k) b^k | COUNT_L2_COMB_NCR | AoPS Basics ch25; Gelfand Algebra §31 |
| COUNT_L3_BINO_TERM | Specific Term Extraction | Find the coefficient of x^k in a binomial expansion | COUNT_L3_BINO_EXP | AoPS Basics ch25 |
| COUNT_L3_BINO_IDEN | Binomial Identities | Apply sum-of-row, alternating-sum, Vandermonde identity | COUNT_L3_BINO_EXP; COUNT_L2_PASC_PROP | AoPS Basics ch25 |

### Level 4 — AMC 12 / AIME (ELO 1600–2100)

#### Generating Functions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L4_GEN_POLY | Polynomial Generating Functions | Encode counting problems as coefficients of polynomial products | COUNT_L3_BINO_EXP; COUNT_L2_STAR_IDEN | AoPS Algebra II ch17; Competition archives |
| COUNT_L4_GEN_OGF | Ordinary Generating Functions | Use formal power series to solve recurrences | COUNT_L4_GEN_POLY; COUNT_L3_REC_SOLVE | AoPS Algebra II ch17 |
| COUNT_L4_GEN_PART | Integer Partition Generating Functions | Encode partition counts as infinite products | COUNT_L4_GEN_OGF | Competition archives |

#### Advanced Combinatorial Identities Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L4_IDEN_VAND | Vandermonde's Identity (Advanced) | Apply ΣC(m,k)C(n,r-k) = C(m+n,r) in non-trivial settings | COUNT_L3_BINO_IDEN | AoPS Algebra II ch17 |
| COUNT_L4_IDEN_HOCK | Hockey Stick Identity | Apply ΣC(i,r) = C(n+1,r+1) in summation problems | COUNT_L2_PASC_PROP | AoPS Basics ch25 |
| COUNT_L4_IDEN_CATA | Catalan Numbers | Recognize and apply C_n = C(2n,n)/(n+1) in path/tree/parenthesization problems | COUNT_L2_COMB_GRID; COUNT_L3_REC_SETUP | Competition archives |

#### Advanced Probability Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L4_APRB_RECR | Recursive Probability | Set up and solve probability recurrences (random walks, Gambler's Ruin) | COUNT_L3_REC_SETUP; COUNT_L3_COND_DEF | AIME archives |
| COUNT_L4_APRB_GPRB | Advanced Geometric Probability | 3D regions, conditional geometric probability, coordinate methods | COUNT_L3_GPRB_AREA; GEO_L2_3D_VOL | AIME archives |
| COUNT_L4_APRB_STATE | State Machine Probability | Model probability problems as Markov chains or state diagrams | COUNT_L4_APRB_RECR | AIME archives |
| COUNT_L4_APRB_EV | Advanced Expected Value | Expected value via indicator variables, states, and recursion | COUNT_L3_EV_LIN; COUNT_L4_APRB_RECR | Competition archives |

#### Advanced Counting Techniques Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L4_ADV_BURN | Burnside's Lemma | Count distinct objects under group symmetry (necklaces, colorings) | COUNT_L2_PERM_CIRC; COUNT_L3_PIE_GEN | Competition archives |
| COUNT_L4_ADV_STIR | Stirling Numbers | Apply Stirling numbers of the second kind for surjective distributions | COUNT_L2_STAR_DIST; COUNT_L3_PIE_GEN | Competition archives |
| COUNT_L4_ADV_BALL | Balls in Boxes (Twelvefold Way) | Classify and solve all 12 distribution cases systematically | COUNT_L2_STAR_IDEN; COUNT_L2_STAR_DIST | Competition archives |
| COUNT_L4_ADV_DCON | Double Counting | Prove identities or solve problems by counting the same set two ways | COUNT_L2_COMB_NCR | Competition archives |
| COUNT_L4_ADV_BIJEC | Bijective Proofs | Establish 1-1 correspondence between two counted sets | COUNT_L2_COMB_NCR | Competition archives |

#### Multinomial and Extended Binomial Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L4_MULTI_COEF | Multinomial Coefficients | Compute n!/(k1!k2!...km!) for multi-category selections | COUNT_L2_PERM_REP; COUNT_L3_BINO_EXP | AoPS Algebra II ch17 |
| COUNT_L4_MULTI_THOM | Multinomial Theorem | Expand (x1+x2+...+xm)^n and extract specific terms | COUNT_L4_MULTI_COEF; COUNT_L3_BINO_TERM | AoPS Algebra II ch17 |

### Level 5 — Olympiad Track (ELO 2100+)

#### Probabilistic Method Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L5_PMETHOD_EX | Existence via Expectation | Prove existence by showing E[X] > 0 | COUNT_L3_EV_LIN | Olympiad references |
| COUNT_L5_PMETHOD_LLL | Lovasz Local Lemma (Exposure) | Recognize when events are "mostly independent" for existence proofs | COUNT_L5_PMETHOD_EX | Olympiad references |

#### Algebraic Combinatorics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L5_ALGC_LATT | Lattice Path Advanced | Non-intersecting lattice paths, Lindstrom-Gessel-Viennot | COUNT_L2_COMB_GRID; COUNT_L4_IDEN_CATA | Olympiad references |
| COUNT_L5_ALGC_INCL | Advanced PIE Applications | PIE for Euler totient derivation, Mobius inversion (exposure) | COUNT_L3_PIE_GEN; NT_L3_EULER_PHI | Olympiad references |

#### Advanced Generating Functions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L5_AGEN_EGF | Exponential Generating Functions | Use EGF for labeled counting (permutations, set partitions) | COUNT_L4_GEN_OGF | Olympiad references |
| COUNT_L5_AGEN_COMP | Composition of Generating Functions | Apply composition formula for structured combinatorial objects | COUNT_L5_AGEN_EGF | Olympiad references |

#### Extremal Combinatorics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| COUNT_L5_EXTM_SPERNER | Sperner's Theorem | Maximum antichain in subset lattice | COUNT_L2_COMB_NCR | Olympiad references |
| COUNT_L5_EXTM_DILWTH | Dilworth's Theorem | Minimum chain partition equals maximum antichain | COUNT_L5_EXTM_SPERNER | Olympiad references |
| COUNT_L5_EXTM_RAMSEY | Ramsey Theory Basics | R(3,3)=6 and simple Ramsey arguments | LOGIC_L3_APIG_CONT | Olympiad references |
| COUNT_L5_EXTM_GRAPH | Extremal Graph Counting | Turan-type and forbidden-subgraph counting problems | COUNT_L5_EXTM_RAMSEY | Olympiad references |

---

## Domain 2: Algebra

### Level 1 — Foundations (ELO 400–1200)

#### Expressions & Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_EXPR_SUBST | Variable Substitution | Evaluate expressions by substituting given values | — | Batterson 1.1; AoPS Algebra I ch1 |
| ALG_L1_EXPR_DIST | Distribution and Combining | Distribute multiplication and combine like terms | ALG_L1_EXPR_SUBST | Batterson 1.1; AoPS Algebra I ch2 |
| ALG_L1_EXPR_OOPS | Order of Operations | Apply PEMDAS correctly including nested expressions | — | Batterson 1.1; AoPS Algebra I ch1 |
| ALG_L1_EXPR_SOLVE | Solving Linear Equations | Isolate variable in single-variable linear equations | ALG_L1_EXPR_DIST | AoPS Algebra I ch3 |

#### Word Problem Translation Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_WORD_DRT | Distance-Rate-Time | Translate and solve d=rt problems | ALG_L1_EXPR_SOLVE | Batterson 1.1; AoPS Algebra I ch4 |
| ALG_L1_WORD_CONS | Consecutive Integer Problems | Set up equations from consecutive integer constraints | ALG_L1_EXPR_SOLVE | Batterson 1.1 |
| ALG_L1_WORD_AGE | Age Problems | Set up equations relating present and past/future ages | ALG_L1_EXPR_SOLVE | Batterson 1.1; AoPS Algebra I ch4 |
| ALG_L1_WORD_WORK | Work/Rate Problems | Combine individual work rates to find joint rates | ALG_L1_EXPR_SOLVE | Batterson 1.1; AoPS Algebra I ch5 |

#### Linear Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_LINE_SLOPE | Slope and Intercepts | Compute slope, find x- and y-intercepts | ALG_L1_EXPR_SOLVE | Batterson 1.2; AoPS Algebra I ch8 |
| ALG_L1_LINE_FORMS | Equation Forms | Convert between slope-intercept, point-slope, standard form | ALG_L1_LINE_SLOPE | AoPS Algebra I ch8 |
| ALG_L1_LINE_PARPERP | Parallel and Perpendicular Lines | Identify and construct parallel/perpendicular lines from slopes | ALG_L1_LINE_SLOPE | AoPS Algebra I ch8 |

#### Systems of Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_SYS_SUBST | Substitution Method | Solve 2-variable systems by substitution | ALG_L1_EXPR_SOLVE | Batterson 1.3; AoPS Algebra I ch5 |
| ALG_L1_SYS_ELIM | Elimination Method | Solve 2-variable systems by adding/subtracting equations | ALG_L1_EXPR_SOLVE | Batterson 1.3; AoPS Algebra I ch5 |
| ALG_L1_SYS_WORD | System Word Problems | Translate word problems into 2-variable systems | ALG_L1_SYS_SUBST; ALG_L1_WORD_DRT | Batterson 1.3 |

#### Ratios & Proportions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_RAT_RATIO | Ratio Setup and Simplification | Express and simplify ratios, find parts from whole | — | Batterson 1.4; AoPS Algebra I ch6 |
| ALG_L1_RAT_PROP | Proportional Reasoning | Set up and solve proportions (cross-multiplication) | ALG_L1_RAT_RATIO | Batterson 1.4; AoPS Algebra I ch6 |
| ALG_L1_RAT_PCT | Percent Problems | Percent increase/decrease, successive percent changes | ALG_L1_RAT_PROP | Batterson 1.4; AoPS Algebra I ch7 |

#### Statistics Basics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_STAT_CENT | Measures of Central Tendency | Compute mean, median, mode for data sets | — | Batterson 1.8 |
| ALG_L1_STAT_WAVG | Weighted Average | Compute and apply weighted averages | ALG_L1_STAT_CENT | Batterson 1.8 |
| ALG_L1_STAT_RANGE | Range and Spread | Compute range; identify effect of adding/removing data | ALG_L1_STAT_CENT | Batterson 1.8 |

#### Arithmetic Sequences Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L1_ASEQ_NTH | Nth Term Formula | Find a_n = a_1 + (n-1)d | ALG_L1_EXPR_SOLVE | Batterson 1.9; Gelfand Algebra §43 |
| ALG_L1_ASEQ_SUM | Arithmetic Series | Compute sum using S_n = n(a_1+a_n)/2 | ALG_L1_ASEQ_NTH | Batterson 1.9; Gelfand Algebra §43 |

### Level 2 — Intermediate (ELO 1000–1450)

#### Distribution Tricks Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_DTRI_DIFF | Difference of Squares | Factor and apply a^2 - b^2 = (a-b)(a+b) | ALG_L1_EXPR_DIST | Batterson 1.5; Gelfand Algebra §26 |
| ALG_L2_DTRI_PSQR | Perfect Square Trinomials | Recognize and factor a^2 ± 2ab + b^2 | ALG_L2_DTRI_DIFF | Batterson 1.5; Gelfand Algebra §27 |
| ALG_L2_DTRI_CUBES | Sum/Difference of Cubes | Factor a^3 ± b^3 = (a±b)(a^2 ∓ ab + b^2) | ALG_L2_DTRI_DIFF | Gelfand Algebra §30 |
| ALG_L2_DTRI_SYMM | Symmetric Expressions | Compute xy+yz+zx, x^2+y^2+z^2 from sums/products | ALG_L2_DTRI_PSQR | Gelfand Algebra §28-29 |

#### Quadratic Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_QUAD_FACT | Factoring Quadratics | Factor ax^2+bx+c into (px+q)(rx+s) | ALG_L2_DTRI_DIFF | Batterson 1.6; AoPS Algebra I ch10 |
| ALG_L2_QUAD_FORM | Quadratic Formula | Apply x = (-b ± √(b^2-4ac))/(2a) | ALG_L2_QUAD_FACT | Batterson 1.6; AoPS Algebra I ch11 |
| ALG_L2_QUAD_COMP | Completing the Square | Rewrite ax^2+bx+c in vertex form a(x-h)^2+k | ALG_L2_QUAD_FACT | AoPS Algebra I ch11 |
| ALG_L2_QUAD_DISC | Discriminant Analysis | Use b^2-4ac to determine number/nature of roots | ALG_L2_QUAD_FORM | AoPS Algebra I ch11 |

#### Vieta's (Quadratic) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_VIET_SUMPROD | Sum and Product of Roots | Apply r+s = -b/a, rs = c/a for quadratics | ALG_L2_QUAD_FACT | Batterson 1.6; Gelfand Algebra §49 |
| ALG_L2_VIET_CONSTR | Constructing Equations from Roots | Build quadratic from given roots via Vieta's | ALG_L2_VIET_SUMPROD | Gelfand Algebra §49 |
| ALG_L2_VIET_SYMM | Symmetric Functions of Roots | Compute r^2+s^2, 1/r+1/s etc. from sum/product | ALG_L2_VIET_SUMPROD | Gelfand Algebra §49 |

#### Exponents & Radicals Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_EXP_LAWS | Laws of Exponents | Apply product, quotient, power rules for integer exponents | ALG_L1_EXPR_SUBST | Batterson 1.7; AoPS Algebra I ch19 |
| ALG_L2_EXP_FRAC | Fractional and Negative Exponents | Interpret a^(m/n) = n-th root of a^m and a^(-n) = 1/a^n | ALG_L2_EXP_LAWS | AoPS Algebra I ch19; Gelfand Algebra §22 |
| ALG_L2_EXP_RAD | Simplifying Radicals | Simplify, combine, and rationalize radical expressions | ALG_L2_EXP_FRAC | Batterson 1.7; Gelfand Algebra §23-24 |
| ALG_L2_EXP_RADEQ | Radical Equations | Solve equations with radicals, check for extraneous solutions | ALG_L2_EXP_RAD; ALG_L2_QUAD_FORM | AoPS Algebra I ch22 |

#### Geometric Sequences Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_GSEQ_NTH | Geometric Sequence Nth Term | Find a_n = a_1 * r^(n-1) | ALG_L2_EXP_LAWS | Batterson 1.9; Gelfand Algebra §44 |
| ALG_L2_GSEQ_FSUM | Finite Geometric Series | Compute S_n = a(1-r^n)/(1-r) | ALG_L2_GSEQ_NTH | Gelfand Algebra §45 |
| ALG_L2_GSEQ_ISUM | Infinite Geometric Series | Compute S = a/(1-r) for |r|<1 | ALG_L2_GSEQ_FSUM | Gelfand Algebra §46 |

#### Special Substitutions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_SSUB_NEST | Nested Radicals | Simplify and solve expressions with nested square roots | ALG_L2_EXP_RAD | Batterson 1.10 |
| ALG_L2_SSUB_CFRAC | Continued Fractions | Evaluate finite continued fractions and repeating patterns | ALG_L2_SSUB_NEST | Batterson 1.10; AoPS Algebra I ch22 |
| ALG_L2_SSUB_SELF | Self-Similar Equations | Solve equations where the expression repeats inside itself | ALG_L2_SSUB_NEST; ALG_L2_QUAD_FORM | AoPS Algebra I ch22 |

#### Graphing Quadratics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_GQUAD_PARA | Parabola Graphing | Graph y=ax^2+bx+c, identify vertex, axis of symmetry, direction | ALG_L2_QUAD_COMP | AoPS Algebra I ch14 |
| ALG_L2_GQUAD_INEQ | Quadratic Inequalities (Graphical) | Solve ax^2+bx+c > 0 using graph/sign analysis | ALG_L2_GQUAD_PARA; ALG_L2_QUAD_FACT | AoPS Algebra I ch15 |

#### Inequalities Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_INEQ_LIN | Linear Inequalities | Solve and graph one-variable linear inequalities | ALG_L1_EXPR_SOLVE | AoPS Algebra I ch9 |
| ALG_L2_INEQ_QUAD | Quadratic Inequalities | Solve via factoring and sign charts | ALG_L2_QUAD_FACT; ALG_L2_INEQ_LIN | AoPS Algebra I ch15; Gelfand Algebra §55 |
| ALG_L2_INEQ_ABS | Absolute Value Equations/Inequalities | Solve |f(x)| = k and |f(x)| < k type problems | ALG_L2_INEQ_LIN | AoPS Algebra I ch9; Gelfand Algebra §56-57 |

#### Functions (Intro) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L2_FUNC_DOM | Domain and Range | Find domain and range of algebraic functions | ALG_L1_EXPR_SUBST | AoPS Algebra I ch17 |
| ALG_L2_FUNC_COMP | Function Composition | Compute f(g(x)) and simplify compositions | ALG_L2_FUNC_DOM | AoPS Algebra I ch17 |
| ALG_L2_FUNC_INV | Inverse Functions | Find f^(-1)(x) algebraically, verify via composition | ALG_L2_FUNC_COMP | AoPS Algebra I ch18 |

### Level 3 — Advanced (ELO 1300–1650)

#### Polynomial Division Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_PDIV_SYNTH | Synthetic Division | Divide polynomial by (x-c) using synthetic division | ALG_L2_QUAD_FACT | AoPS Algebra II ch6 |
| ALG_L3_PDIV_LONG | Polynomial Long Division | Divide polynomial by multi-term divisor | ALG_L3_PDIV_SYNTH | AoPS Algebra II ch6 |
| ALG_L3_PDIV_REM | Remainder Theorem | f(c) equals the remainder when f(x) is divided by (x-c) | ALG_L3_PDIV_SYNTH | AoPS Algebra II ch6 |
| ALG_L3_PDIV_FACTOR | Factor Theorem | (x-c) is a factor iff f(c)=0 | ALG_L3_PDIV_REM | AoPS Algebra II ch6 |

#### Polynomial Roots Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_ROOT_RAT | Rational Root Theorem | List possible rational roots p/q and test systematically | ALG_L3_PDIV_FACTOR | AoPS Algebra II ch7 |
| ALG_L3_ROOT_FTA | Fundamental Theorem of Algebra | Degree n polynomial has exactly n complex roots (counted with multiplicity) | ALG_L3_ROOT_RAT | AoPS Algebra II ch7 |
| ALG_L3_ROOT_BOUND | Root Bounds | Apply Descartes' rule of signs, upper/lower bound tests | ALG_L3_ROOT_RAT | AoPS Algebra II ch7 |

#### Vieta's (General) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_VGEN_FORM | Vieta's for Degree n | Express e_1,...,e_n symmetric functions from coefficients | ALG_L2_VIET_SUMPROD; ALG_L3_ROOT_FTA | AoPS Algebra II ch8 |
| ALG_L3_VGEN_NEWT | Newton's Sums | Relate power sums p_k to elementary symmetric polynomials | ALG_L3_VGEN_FORM | AoPS Algebra II ch8 |
| ALG_L3_VGEN_CONSTR | Constructing Polynomials from Root Conditions | Build polynomials satisfying root sum/product constraints | ALG_L3_VGEN_FORM | AoPS Algebra II ch8 |

#### Advanced Factoring Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_AFAC_GROUP | Factoring by Grouping | Group terms strategically to extract common factors | ALG_L2_QUAD_FACT | AoPS Algebra I ch11 |
| ALG_L3_AFAC_SFFT | Simon's Favorite Factoring Trick | Rewrite xy + ax + by + c as (x+b)(y+a) + constant | ALG_L3_AFAC_GROUP | AoPS Algebra I ch11; Competition archives |
| ALG_L3_AFAC_MULTI | Multivariable Factoring | Factor expressions in multiple variables using symmetry | ALG_L3_AFAC_GROUP; ALG_L2_DTRI_SYMM | AoPS Algebra II ch9 |
| ALG_L3_AFAC_CYCL | Cyclotomic/Special Polynomial Factoring | Factor x^n-1, x^n+1, sum/difference of nth powers | ALG_L2_DTRI_CUBES; ALG_L3_ROOT_FTA | AoPS Algebra II ch9 |

#### Complex Numbers Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_CPLX_ARITH | Complex Arithmetic | Add, subtract, multiply, divide complex numbers | ALG_L2_EXP_RAD | AoPS Algebra I ch12; AoPS Algebra II ch3 |
| ALG_L3_CPLX_CONJ | Conjugates | Apply conjugate properties, rationalize complex denominators | ALG_L3_CPLX_ARITH | AoPS Algebra II ch3 |
| ALG_L3_CPLX_PLANE | Complex Plane | Plot complex numbers, interpret operations geometrically | ALG_L3_CPLX_ARITH | AoPS Algebra II ch3 |
| ALG_L3_CPLX_MOD | Modulus and Argument | Compute |z|, arg(z), convert between rectangular and polar | ALG_L3_CPLX_PLANE | AoPS Algebra II ch3 |

#### AM-GM Inequality Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_AMGM_TWO | Two-Variable AM-GM | Apply (a+b)/2 >= sqrt(ab) for optimization | ALG_L2_EXP_RAD | AoPS Algebra II ch12; Gelfand Algebra §58 |
| ALG_L3_AMGM_NVAR | N-Variable AM-GM | Generalize to n variables, weighted AM-GM | ALG_L3_AMGM_TWO | AoPS Algebra II ch12; Gelfand Algebra §59-65 |
| ALG_L3_AMGM_OPT | Optimization via AM-GM | Find extrema of expressions by choosing equality condition | ALG_L3_AMGM_TWO | AoPS Algebra II ch12 |

#### Logarithms Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_LOG_DEF | Logarithm Definition and Properties | Apply log_b(xy), log_b(x/y), log_b(x^k) | ALG_L2_EXP_LAWS | AoPS Algebra I ch19; AoPS Algebra II ch13 |
| ALG_L3_LOG_COB | Change of Base | Apply log_b(x) = log_a(x)/log_a(b) | ALG_L3_LOG_DEF | AoPS Algebra II ch13 |
| ALG_L3_LOG_EQ | Logarithmic and Exponential Equations | Solve equations involving logs and exponentials | ALG_L3_LOG_DEF; ALG_L3_LOG_COB | AoPS Algebra II ch13 |

#### Functional Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_FEQN_SUBST | Substitution Strategies | Find f by plugging in special values (0, 1, -x, 1/x) | ALG_L2_FUNC_COMP | AoPS Algebra II ch19 |
| ALG_L3_FEQN_CAUCH | Cauchy-Type Equations | Solve f(x+y)=f(x)+f(y) and variants under continuity | ALG_L3_FEQN_SUBST | AoPS Algebra II ch19 |
| ALG_L3_FEQN_ITER | Iterated Functions | Compute f(f(...f(x)...)) and find periodic functions | ALG_L2_FUNC_COMP; ALG_L3_FEQN_SUBST | AoPS Algebra II ch19 |

#### Advanced Sequences Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_ASEQ_TELE | Telescoping Series | Recognize and evaluate telescoping sums/products | ALG_L1_ASEQ_SUM | AoPS Algebra II ch17 |
| ALG_L3_ASEQ_AG | Arithmetico-Geometric Series | Sum sequences that are products of arithmetic and geometric | ALG_L1_ASEQ_SUM; ALG_L2_GSEQ_FSUM | AoPS Algebra II ch17 |
| ALG_L3_ASEQ_FDIF | Finite Differences | Compute successive differences to find polynomial formulas | ALG_L1_ASEQ_NTH | AoPS Algebra II ch17 |

#### Floor/Ceiling Functions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L3_FLOOR_DEF | Floor and Ceiling Definitions | Apply definitions, compute floor(x) and ceil(x) | — | AoPS Algebra I ch20 |
| ALG_L3_FLOOR_FRAC | Fractional Part | Use {x} = x - floor(x), solve fractional part equations | ALG_L3_FLOOR_DEF | AoPS Algebra II ch16 |
| ALG_L3_FLOOR_SUM | Floor Function Sums | Evaluate sums involving floor(n/k) | ALG_L3_FLOOR_DEF | AoPS Algebra II ch16; Competition archives |

### Level 4 — AMC 12 / AIME (ELO 1600–2100)

#### Advanced Polynomials Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_APOL_INTER | Polynomial Interpolation | Reconstruct polynomial from n+1 points (Lagrange) | ALG_L3_ROOT_FTA; ALG_L3_PDIV_REM | AoPS Algebra II ch7 |
| ALG_L4_APOL_CHEBY | Chebyshev Polynomials (Exposure) | Recognize T_n(cos θ) = cos(nθ) pattern in competition problems | ALG_L4_TRIG_MULT; ALG_L3_ROOT_FTA | AoPS Precalculus ch8; AIME archives |
| ALG_L4_APOL_SYMM | Symmetric Polynomial Manipulation | Express any symmetric polynomial via elementary symmetric polys | ALG_L3_VGEN_FORM; ALG_L3_AFAC_MULTI | AoPS Algebra II ch9 |
| ALG_L4_APOL_RESULT | Resultants and Polynomial GCD | Find common roots of two polynomials | ALG_L3_PDIV_LONG; ALG_L3_ROOT_FTA | Competition archives |

#### Complex Numbers (Advanced) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_CPLX_EULER | Euler's Formula | Apply e^(iθ) = cos θ + i sin θ | ALG_L3_CPLX_MOD | AoPS Precalculus ch8 |
| ALG_L4_CPLX_ROOT | Roots of Unity | Find and apply nth roots of unity, unity filter | ALG_L4_CPLX_EULER; ALG_L3_ROOT_FTA | AoPS Precalculus ch8; AoPS Algebra II ch3 |
| ALG_L4_CPLX_DEPOL | De Moivre's Theorem | Compute (cos θ + i sin θ)^n for powers and roots | ALG_L4_CPLX_EULER | AoPS Precalculus ch8 |
| ALG_L4_CPLX_GEOM | Complex Number Geometry | Solve geometry problems using complex multiplication/rotation | ALG_L4_CPLX_EULER; ALG_L3_CPLX_PLANE | AoPS Precalculus ch8 |

#### Trigonometric Identities Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_TRIG_FUND | Fundamental Trig Identities | Apply Pythagorean, reciprocal, and quotient identities | GEO_L3_TRIG_BASIC | AoPS Precalculus ch5; Gelfand Trigonometry ch1-2 |
| ALG_L4_TRIG_ADD | Addition Formulas | Apply sin(A±B), cos(A±B), tan(A±B) | ALG_L4_TRIG_FUND | AoPS Precalculus ch5; Gelfand Trigonometry ch3 |
| ALG_L4_TRIG_DOUB | Double and Half Angle Formulas | Apply sin 2A, cos 2A, tan 2A and half-angle variants | ALG_L4_TRIG_ADD | AoPS Precalculus ch5; Gelfand Trigonometry ch3 |
| ALG_L4_TRIG_MULT | Multiple Angle and Power Reduction | Express sin(nθ), cos(nθ) in terms of sin θ, cos θ | ALG_L4_TRIG_DOUB; ALG_L4_CPLX_DEPOL | AoPS Precalculus ch5 |
| ALG_L4_TRIG_PRODSUM | Product-to-Sum and Sum-to-Product | Convert between products and sums of trig functions | ALG_L4_TRIG_ADD | AoPS Precalculus ch5; Gelfand Trigonometry ch4 |
| ALG_L4_TRIG_EQ | Trigonometric Equations | Solve equations involving trig functions over specified domains | ALG_L4_TRIG_FUND; ALG_L4_TRIG_ADD | AoPS Precalculus ch5; Gelfand Trigonometry ch5 |

#### Sequences & Series (Advanced) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_SEQ_CHAREC | Characteristic Equation Method | Solve a_n = pa_{n-1} + qa_{n-2} via x^2 = px + q | ALG_L3_ASEQ_TELE; COUNT_L3_REC_SOLVE | AoPS Algebra II ch17 |
| ALG_L4_SEQ_NONHOM | Non-Homogeneous Recurrences | Solve recurrences with forcing terms (particular solution + homogeneous) | ALG_L4_SEQ_CHAREC | AoPS Algebra II ch17 |
| ALG_L4_SEQ_CONVG | Series Convergence Tests | Apply ratio, comparison, and geometric tests for convergence | ALG_L2_GSEQ_ISUM | AoPS Precalculus ch11 |

#### Vectors and Matrices Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_VEC_OPS | Vector Operations | Add, scale, compute dot product in 2D and 3D | ALG_L1_LINE_SLOPE | AoPS Precalculus ch9 |
| ALG_L4_VEC_DOT | Dot Product Applications | Compute projections, angles between vectors, perpendicularity | ALG_L4_VEC_OPS | AoPS Precalculus ch9 |
| ALG_L4_VEC_CROSS | Cross Product (3D) | Compute cross products, area of parallelogram, normal vectors | ALG_L4_VEC_OPS | AoPS Precalculus ch9 |
| ALG_L4_MAT_OPS | Matrix Operations | Multiply, add, and find determinants of 2x2 and 3x3 matrices | ALG_L4_VEC_OPS | AoPS Precalculus ch10 |
| ALG_L4_MAT_INV | Matrix Inverses and Systems | Solve systems via matrix inverse, Cramer's rule | ALG_L4_MAT_OPS; ALG_L1_SYS_ELIM | AoPS Precalculus ch10 |
| ALG_L4_MAT_TRANS | Matrix Transformations | Apply rotation, reflection, scaling as matrix multiplication | ALG_L4_MAT_OPS; GEO_L3_TRANS_COMP | AoPS Precalculus ch10 |

#### Advanced Inequalities Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L4_AINEQ_CAUCH | Cauchy-Schwarz Inequality | Apply (Σa_i^2)(Σb_i^2) >= (Σa_ib_i)^2 | ALG_L3_AMGM_NVAR | AoPS Algebra II ch12; Competition archives |
| ALG_L4_AINEQ_POWER | Power Mean Inequality | QM >= AM >= GM >= HM chain | ALG_L3_AMGM_NVAR | AoPS Algebra II ch12 |
| ALG_L4_AINEQ_SCHUR | Schur's Inequality | Apply Schur's inequality for symmetric optimization | ALG_L4_AINEQ_CAUCH; ALG_L4_APOL_SYMM | Competition archives |
| ALG_L4_AINEQ_SOS | Sum of Squares Method | Prove inequalities by decomposing into sum of squares | ALG_L3_AMGM_TWO | Competition archives |

### Level 5 — Olympiad Track (ELO 2100+)

#### Olympiad Algebra Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L5_OALG_FEQN | Olympiad Functional Equations | Solve f: R→R with injectivity/surjectivity arguments | ALG_L3_FEQN_CAUCH | Olympiad references |
| ALG_L5_OALG_INEQ | Olympiad Inequalities | Multi-variable inequalities requiring creative substitution | ALG_L4_AINEQ_CAUCH; ALG_L4_AINEQ_SOS | Olympiad references |
| ALG_L5_OALG_POLY | Olympiad Polynomial Problems | Irreducibility, polynomial maps, composition problems | ALG_L4_APOL_SYMM; ALG_L4_APOL_RESULT | Olympiad references |

#### Advanced Complex Analysis Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L5_ACPLX_TRANS | Mobius Transformations | Apply (az+b)/(cz+d) transformations of the complex plane | ALG_L4_CPLX_GEOM; ALG_L4_MAT_OPS | Olympiad references |
| ALG_L5_ACPLX_CYCLO | Cyclotomic Polynomials | Factor x^n-1 into cyclotomic components, minimal polynomials | ALG_L4_CPLX_ROOT; ALG_L3_AFAC_CYCL | Olympiad references |
| ALG_L5_ACPLX_UNITY | Unity Filter Technique | Use roots of unity to extract coefficients mod n | ALG_L4_CPLX_ROOT; COUNT_L4_GEN_POLY | Olympiad references |

#### Advanced Series Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L5_ASER_TAYLOR | Taylor/Power Series | Expand functions as power series, manipulate term-by-term | ALG_L4_SEQ_CONVG; ALG_L3_BINO_EXP | Olympiad references |
| ALG_L5_ASER_PARTFRAC | Partial Fractions for Series | Decompose rational functions to evaluate series | ALG_L3_PDIV_LONG; ALG_L3_ASEQ_TELE | Olympiad references |
| ALG_L5_ASER_PRODFORM | Infinite Products | Evaluate infinite products via logarithmic series | ALG_L4_SEQ_CONVG; ALG_L3_LOG_DEF | Olympiad references |

#### Optimization and Extremal Algebra Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ALG_L5_OPT_LAGR | Lagrange Multipliers (Exposure) | Constrained optimization with gradient condition | ALG_L4_AINEQ_CAUCH | Olympiad references |
| ALG_L5_OPT_CONVEX | Convexity and Jensen's Inequality | Apply Jensen's inequality for convex/concave functions | ALG_L4_AINEQ_POWER | Olympiad references |
| ALG_L5_OPT_SMOOTH | Smoothing and Mixing Variables | Prove extrema occur at boundary by smoothing arguments | ALG_L5_OPT_CONVEX; ALG_L3_AMGM_OPT | Olympiad references |

---

## Domain 3: Number Theory

### Level 1 — Foundations (ELO 400–1200)

#### Primes & Composites Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L1_PRIM_IDENT | Identifying Primes | Test primality for small numbers, recognize common primes | — | Batterson 4.1; AoPS Basics ch5 |
| NT_L1_PRIM_SIEVE | Sieve of Eratosthenes | Generate primes up to n using the sieve | NT_L1_PRIM_IDENT | Batterson 4.1 |
| NT_L1_PRIM_PFACT | Prime Factorization | Express any integer as product of prime powers | NT_L1_PRIM_IDENT | Batterson 4.1; AoPS Basics ch5 |
| NT_L1_PRIM_FTA | Fundamental Theorem of Arithmetic | Understand uniqueness of prime factorization | NT_L1_PRIM_PFACT | AoPS Basics ch5 |

#### Divisibility Rules Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L1_DIV_BASIC | Divisibility Rules (2-6) | Apply rules for 2, 3, 4, 5, 6 | — | Batterson 4.1 |
| NT_L1_DIV_ADV | Divisibility Rules (7-12) | Apply rules for 7, 8, 9, 10, 11, 12 | NT_L1_DIV_BASIC | Batterson 4.1 |
| NT_L1_DIV_DIGIT | Digit Sum Tests | Use digit sums for divisibility by 3, 9 and alternating sums for 11 | NT_L1_DIV_BASIC | Batterson 4.1 |

#### Factor Counting Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L1_FCNT_COUNT | Counting Divisors | If n = p1^a1 * ... then τ(n) = (a1+1)(a2+1)... | NT_L1_PRIM_PFACT | Batterson 4.2 |
| NT_L1_FCNT_LIST | Listing Factors | Systematically list all factors of n | NT_L1_FCNT_COUNT | Batterson 4.2 |
| NT_L1_FCNT_PAIRS | Factor Pairs | Find pairs (d, n/d) and apply to word problems | NT_L1_FCNT_LIST | Batterson 4.2 |

#### GCF & LCM Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L1_GCL_GCF | GCF from Prime Factorization | Compute GCF by taking min exponents | NT_L1_PRIM_PFACT | Batterson 4.3; AoPS Basics ch5 |
| NT_L1_GCL_LCM | LCM from Prime Factorization | Compute LCM by taking max exponents | NT_L1_PRIM_PFACT | Batterson 4.3; AoPS Basics ch5 |
| NT_L1_GCL_EUCL | Euclidean Algorithm | Find GCF via repeated division | NT_L1_GCL_GCF | AoPS Basics ch5 |
| NT_L1_GCL_WORD | GCF/LCM Word Problems | Apply GCF/LCM to cycling, overlap, and grouping problems | NT_L1_GCL_GCF; NT_L1_GCL_LCM | Batterson 4.3 |

#### Fractions & Decimals Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L1_FRAC_REP | Repeating Decimal Conversion | Convert between repeating decimals and fractions | NT_L1_PRIM_PFACT | Batterson 4.6 |
| NT_L1_FRAC_TERM | Terminating Decimal Criterion | Determine if a/b terminates (denominator has only 2s and 5s) | NT_L1_FRAC_REP; NT_L1_PRIM_PFACT | Batterson 4.6 |

### Level 2 — Intermediate (ELO 1000–1450)

#### Factor Tricks Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_FTRI_SUM | Sum of Divisors | Compute σ(n) from prime factorization using (p^(a+1)-1)/(p-1) | NT_L1_FCNT_COUNT | Batterson 4.3 |
| NT_L2_FTRI_PROD | Product of Divisors | Compute product of divisors as n^(τ(n)/2) | NT_L1_FCNT_COUNT | Batterson 4.3 |
| NT_L2_FTRI_PERF | Perfect, Abundant, Deficient Numbers | Classify n by comparing σ(n) to 2n | NT_L2_FTRI_SUM | Batterson 4.3 |

#### Factorials in NT Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_FACN_LEGDR | Legendre's Formula | Highest power of prime p dividing n! = Σ floor(n/p^k) | NT_L1_PRIM_PFACT | Batterson 4.3; AoPS Basics ch5 |
| NT_L2_FACN_TRAIL | Trailing Zeros | Count trailing zeros of n! (= highest power of 5 in n!) | NT_L2_FACN_LEGDR | Batterson 4.3 |
| NT_L2_FACN_DIV | Divisibility of Factorials | Determine if n! is divisible by a given number | NT_L2_FACN_LEGDR | Competition archives |

#### Number Bases Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_BASE_CONV | Base Conversion | Convert between base 10 and base b (including binary, octal, hex) | NT_L1_PRIM_PFACT | Batterson 4.4; AoPS Basics ch5 |
| NT_L2_BASE_ARITH | Arithmetic in Other Bases | Perform addition, subtraction, multiplication in base b | NT_L2_BASE_CONV | Batterson 4.4 |
| NT_L2_BASE_DIGIT | Base Representation Properties | Relate digit properties in base b to divisibility and remainders | NT_L2_BASE_CONV | AoPS Basics ch5 |

#### Units Digit Patterns Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_UNIT_CYCLE | Cyclicity of Powers | Determine the period of units digits for a^n | NT_L1_PRIM_IDENT | Batterson 4.5 |
| NT_L2_UNIT_PROD | Units Digit of Products/Sums | Compute last digit of large products or sums | NT_L2_UNIT_CYCLE | Batterson 4.5 |
| NT_L2_UNIT_LASTK | Last k Digits | Extend units digit analysis to last 2-3 digits (mod 100, 1000) | NT_L2_UNIT_CYCLE; NT_L2_MOD_BASIC | Competition archives |

#### Modular Arithmetic Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_MOD_BASIC | Modular Arithmetic Basics | Compute a mod m, addition and multiplication mod m | NT_L1_DIV_BASIC | Batterson 4.7; AoPS Basics ch5 |
| NT_L2_MOD_CONG | Congruence Properties | Apply transitivity, compatibility with +, -, ×, powers | NT_L2_MOD_BASIC | AoPS Basics ch5 |
| NT_L2_MOD_LINCONG | Solving Linear Congruences | Solve ax ≡ b (mod m) including existence conditions | NT_L2_MOD_CONG; NT_L1_GCL_GCF | AoPS Basics ch5 |
| NT_L2_MOD_INVMOD | Modular Inverses | Find a^(-1) mod m when gcd(a,m)=1 | NT_L2_MOD_LINCONG | AoPS Basics ch5 |

#### Perfect Squares Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L2_PSQR_PROP | Properties of Perfect Squares | Odd number of divisors, modular constraints (mod 4, mod 3) | NT_L1_FCNT_COUNT; NT_L2_MOD_BASIC | Batterson 4.5 |
| NT_L2_PSQR_DIGIT | Digit Constraints on Squares | Last digit restrictions, digital root properties | NT_L2_PSQR_PROP; NT_L2_UNIT_CYCLE | Batterson 4.5 |
| NT_L2_PSQR_FACTOR | Making Expressions Perfect Squares | Determine conditions for n to make f(n) a perfect square | NT_L2_PSQR_PROP; NT_L1_PRIM_PFACT | Competition archives |

### Level 3 — Advanced (ELO 1300–1650)

#### Fermat's Little Theorem Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_FLT_STATE | Fermat's Little Theorem Statement | a^(p-1) ≡ 1 (mod p) for gcd(a,p)=1, and a^p ≡ a (mod p) | NT_L2_MOD_CONG | AoPS Basics ch5 |
| NT_L3_FLT_REDUCE | Exponent Reduction via FLT | Reduce large exponents modulo p-1 to simplify a^n mod p | NT_L3_FLT_STATE | AoPS Basics ch5 |
| NT_L3_FLT_APPLY | FLT in Problem Solving | Apply FLT to find remainders, prove divisibility, test primality | NT_L3_FLT_REDUCE | Competition archives |

#### Euler's Totient Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_EULER_PHI | Euler's Totient Function | Compute φ(n) from prime factorization: φ(p^a) = p^a - p^(a-1) | NT_L1_PRIM_PFACT; NT_L2_MOD_BASIC | AoPS Basics ch5 |
| NT_L3_EULER_MULT | Multiplicativity of φ | Apply φ(mn) = φ(m)φ(n) when gcd(m,n)=1 | NT_L3_EULER_PHI | AoPS Basics ch5 |
| NT_L3_EULER_THM | Euler's Theorem | a^φ(n) ≡ 1 (mod n) for gcd(a,n)=1 (generalization of FLT) | NT_L3_EULER_PHI; NT_L3_FLT_STATE | AoPS Basics ch5 |
| NT_L3_EULER_SUMID | Totient Sum Identity | Σ_{d|n} φ(d) = n and applications | NT_L3_EULER_MULT | Competition archives |

#### Chinese Remainder Theorem Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_CRT_STATE | CRT Statement | Simultaneous congruences x ≡ a_i (mod m_i) have unique solution mod M when m_i pairwise coprime | NT_L2_MOD_LINCONG | Competition archives |
| NT_L3_CRT_CONSTR | CRT Construction | Explicitly construct solutions via the CRT algorithm | NT_L3_CRT_STATE | Competition archives |
| NT_L3_CRT_APPLY | CRT in Problem Solving | Use CRT to split mod n problems into coprime mod p^a components | NT_L3_CRT_CONSTR | Competition archives |

#### Wilson's Theorem Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_WILS_STATE | Wilson's Theorem Statement | (p-1)! ≡ -1 (mod p) for prime p | NT_L2_MOD_CONG | Competition archives |
| NT_L3_WILS_APPLY | Wilson's Theorem Applications | Apply to compute factorials mod p and primality connections | NT_L3_WILS_STATE | Competition archives |

#### Diophantine Equations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_DIOPH_LIN | Linear Diophantine Equations | Solve ax + by = c in integers, parametrize all solutions | NT_L1_GCL_EUCL; NT_L2_MOD_LINCONG | AoPS Basics ch5 |
| NT_L3_DIOPH_PYTH | Pythagorean Triple Generation | Generate all primitive triples via (m^2-n^2, 2mn, m^2+n^2) | NT_L3_DIOPH_LIN; GEO_L1_PYTH_TRIP | AoPS Basics ch5 |
| NT_L3_DIOPH_PELL | Pell Equations (Exposure) | Recognize x^2 - Dy^2 = 1 and find fundamental solution | NT_L3_DIOPH_LIN | Competition archives |
| NT_L3_DIOPH_MOD | Diophantine via Modular Constraints | Prove no solution exists by checking modular obstructions | NT_L3_DIOPH_LIN; NT_L2_MOD_CONG | Competition archives |

#### Order & Primitive Roots Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_ORD_DEF | Multiplicative Order | Find ord_m(a) = smallest k with a^k ≡ 1 (mod m) | NT_L3_EULER_THM | Competition archives |
| NT_L3_ORD_PRIM | Primitive Roots | Identify when primitive roots exist, find generators | NT_L3_ORD_DEF; NT_L3_EULER_PHI | Competition archives |
| NT_L3_ORD_APPLY | Order in Problem Solving | Use order to determine cycle length and periodicity mod m | NT_L3_ORD_DEF | Competition archives |

#### Advanced Divisibility Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L3_ADIV_LTE | Lifting the Exponent Lemma | v_p(a^n - b^n) for odd prime p and p | a-b | NT_L2_FACN_LEGDR; NT_L3_FLT_STATE | Competition archives |
| NT_L3_ADIV_ZSYG | Zsygmondy's Theorem (Exposure) | a^n - b^n has a prime factor not dividing a^k - b^k for k<n (exceptions) | NT_L3_ORD_DEF | Competition archives |
| NT_L3_ADIV_VALU | p-adic Valuation | Compute v_p(n) and apply v_p(ab)=v_p(a)+v_p(b), v_p(a+b)≥min(v_p(a),v_p(b)) | NT_L2_FACN_LEGDR | Competition archives |

### Level 4 — AMC 12 / AIME (ELO 1600–2100)

#### Quadratic Residues Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L4_QR_LEGEND | Legendre Symbol | Compute (a/p) and apply Euler's criterion a^((p-1)/2) ≡ (a/p) mod p | NT_L3_FLT_STATE; NT_L2_MOD_INVMOD | Competition archives; AIME archives |
| NT_L4_QR_RECIP | Quadratic Reciprocity | Apply (p/q)(q/p) = (-1)^((p-1)/2)((q-1)/2) for odd primes | NT_L4_QR_LEGEND | Competition archives |
| NT_L4_QR_APPLY | Quadratic Residue Applications | Determine solvability of x^2 ≡ a (mod p) in competition settings | NT_L4_QR_LEGEND | AIME archives |

#### Advanced Modular Arithmetic Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L4_AMOD_POLYMOD | Polynomial Congruences | Solve f(x) ≡ 0 (mod p^k) via Hensel's lemma | NT_L2_MOD_LINCONG; NT_L3_FLT_STATE | Competition archives |
| NT_L4_AMOD_DISCLOG | Discrete Logarithm (Exposure) | Solve a^x ≡ b (mod p) using order and baby-step/giant-step concept | NT_L3_ORD_DEF | Competition archives |
| NT_L4_AMOD_SUMCHAR | Character Sums (Exposure) | Recognize Gauss sums and Legendre symbol summation patterns | NT_L4_QR_LEGEND; ALG_L4_CPLX_ROOT | Olympiad references |

#### Arithmetic Functions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L4_AFUN_MULTF | Multiplicative Functions | Identify and apply multiplicative functions (σ, τ, φ, μ) | NT_L3_EULER_PHI; NT_L2_FTRI_SUM | Competition archives |
| NT_L4_AFUN_MOBIUS | Mobius Function and Inversion | Apply μ(n) and Mobius inversion formula | NT_L4_AFUN_MULTF; NT_L3_EULER_SUMID | Competition archives |
| NT_L4_AFUN_DIRICH | Dirichlet Convolution (Exposure) | Understand (f*g)(n) = Σ_{d|n} f(d)g(n/d) as ring operation | NT_L4_AFUN_MOBIUS | Competition archives |
| NT_L4_AFUN_PERFSQ | Perfect Power Detection | Determine when expressions yield perfect squares/cubes/powers | NT_L2_PSQR_FACTOR; NT_L3_ADIV_VALU | AIME archives |

#### Advanced Diophantine Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L4_ADIOPH_QUAD | Quadratic Diophantine Equations | Solve x^2 + y^2 = n, represent primes as sums of two squares | NT_L3_DIOPH_PYTH; NT_L4_QR_LEGEND | Competition archives |
| NT_L4_ADIOPH_FID | Factoring in Domains | Factor in Z[i], Z[ω] to solve Diophantine equations | ALG_L3_CPLX_ARITH; NT_L4_ADIOPH_QUAD | Competition archives; AIME archives |
| NT_L4_ADIOPH_DESCENT | Infinite Descent | Prove no solution via assuming minimal solution leads to smaller one | NT_L3_DIOPH_MOD | Competition archives |
| NT_L4_ADIOPH_APELL | Advanced Pell Equations | Solve x^2 - Dy^2 = ±1, ±4 and generalized Pell | NT_L3_DIOPH_PELL | Competition archives |

#### Competition Number Theory Techniques Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L4_COMP_CDGT | Clever Digit Arguments | Use digit properties in non-obvious ways (carrying analysis, base representation) | NT_L2_BASE_DIGIT; NT_L2_UNIT_CYCLE | AIME archives |
| NT_L4_COMP_SIZE | Size and Bounding Arguments | Bound variables to reduce Diophantine problems to finite search | NT_L3_DIOPH_LIN; ALG_L2_INEQ_QUAD | AIME archives |
| NT_L4_COMP_CONSTRUCT | Constructive Number Theory | Build explicit numbers satisfying given divisibility/residue conditions | NT_L3_CRT_CONSTR; NT_L3_DIOPH_LIN | AIME archives |

### Level 5 — Olympiad Track (ELO 2100+)

#### Olympiad Number Theory Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L5_ONT_VALU | Advanced Valuations | Deep p-adic valuation arguments, v_p in product/sum structures | NT_L3_ADIV_VALU; NT_L3_ADIV_LTE | Olympiad references |
| NT_L5_ONT_ALGNT | Algebraic Number Theory (Exposure) | Norms in Z[√d], unique factorization failure, class number concept | NT_L4_ADIOPH_FID | Olympiad references |
| NT_L5_ONT_PRMDIST | Prime Distribution | Bertrand's postulate, prime gaps, density arguments | NT_L1_PRIM_SIEVE | Olympiad references |

#### Olympiad Diophantine Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L5_ODIOPH_VIETA | Vieta Jumping | Use Vieta's to show root integrality and derive contradiction/descent | ALG_L2_VIET_SUMPROD; NT_L4_ADIOPH_DESCENT | Olympiad references (ISL) |
| NT_L5_ODIOPH_EXPNT | Exponent Chasing | Systematically track p-adic valuations through equations | NT_L5_ONT_VALU | Olympiad references |
| NT_L5_ODIOPH_FERM | Fermat's Method of Descent (Advanced) | Sophisticated descent on x^4+y^4=z^4 type equations | NT_L4_ADIOPH_DESCENT | Olympiad references |

#### Analytic Number Theory (Exposure) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| NT_L5_ANT_ESTIM | Estimation of Arithmetic Sums | Estimate Σ_{k≤n} f(k) for multiplicative f using heuristics | NT_L4_AFUN_MULTF | Olympiad references |
| NT_L5_ANT_SIEVE | Sieve Methods (Exposure) | Eratosthenes sieve as inclusion-exclusion, Legendre sieve concept | NT_L1_PRIM_SIEVE; COUNT_L3_PIE_GEN | Olympiad references |
| NT_L5_ANT_ERDOS | Erdos-Type Arguments | Probabilistic/extremal reasoning about prime factorizations | NT_L5_ONT_PRMDIST | Olympiad references |
| NT_L5_ANT_SUMDIV | Divisor Sum Estimates | Apply Σ_{d|n} 1 = O(n^ε) type bounds in problem solving | NT_L4_AFUN_MULTF | Olympiad references |

---

## Domain 4: Geometry

### Level 1 — Foundations (ELO 400–1200)

#### Angles Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_ANG_MEAS | Angle Measurement | Measure and classify angles (acute, right, obtuse, straight, reflex) | — | Batterson 5.1; AoPS Geometry ch2 |
| GEO_L1_ANG_VERT | Vertical and Linear Pair Angles | Apply vertical angle theorem and supplementary/complementary rules | GEO_L1_ANG_MEAS | Batterson 5.1; AoPS Geometry ch2 |
| GEO_L1_ANG_PARA | Parallel Line Angles | Apply corresponding, alternate interior/exterior, co-interior angle theorems | GEO_L1_ANG_VERT | Batterson 5.1; AoPS Geometry ch2 |

#### Triangles Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_TRI_CLASS | Triangle Classification | Classify by sides (scalene/isosceles/equilateral) and angles (acute/right/obtuse) | GEO_L1_ANG_MEAS | Batterson 5.1; AoPS Geometry ch3 |
| GEO_L1_TRI_ANGSUM | Triangle Angle Sum | Apply interior angle sum = 180° | GEO_L1_TRI_CLASS | Batterson 5.1; AoPS Geometry ch3 |
| GEO_L1_TRI_EXT | Exterior Angle Theorem | Exterior angle equals sum of non-adjacent interior angles | GEO_L1_TRI_ANGSUM | AoPS Geometry ch3 |
| GEO_L1_TRI_CONG | Triangle Congruence | Apply SSS, SAS, ASA, AAS, HL criteria | GEO_L1_TRI_CLASS | Batterson 5.1; AoPS Geometry ch3 |
| GEO_L1_TRI_ISOSC | Isosceles Triangle Properties | Base angles equal, altitude = median = bisector from apex | GEO_L1_TRI_CONG | AoPS Geometry ch3 |

#### Polygons Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_POLY_ANG | Polygon Angle Formulas | Interior angle sum = (n-2)×180°, each angle of regular n-gon | GEO_L1_TRI_ANGSUM | Batterson 5.1; AoPS Geometry ch9 |
| GEO_L1_POLY_EXT | Exterior Angles of Polygons | Exterior angles sum to 360° | GEO_L1_POLY_ANG | AoPS Geometry ch9 |
| GEO_L1_POLY_DIAG | Polygon Diagonals | Count diagonals: n(n-3)/2 | GEO_L1_POLY_ANG; COUNT_L1_PAT_HAND | AoPS Geometry ch9 |

#### Quadrilaterals Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_QUAD_PARA | Parallelogram Properties | Opposite sides/angles equal, diagonals bisect each other | GEO_L1_TRI_CONG | Batterson 5.1; AoPS Geometry ch8 |
| GEO_L1_QUAD_RECT | Rectangle/Rhombus/Square Properties | Special parallelograms and their diagonal properties | GEO_L1_QUAD_PARA | AoPS Geometry ch8 |
| GEO_L1_QUAD_TRAP | Trapezoid and Kite Properties | Midsegment of trapezoid, kite diagonal properties | GEO_L1_QUAD_PARA | Batterson 5.1; AoPS Geometry ch8 |

#### Basic Area Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_AREA_RECT | Rectangle and Parallelogram Area | A = bh for rectangles and parallelograms | — | Batterson 5.4; AoPS Geometry ch5 |
| GEO_L1_AREA_TRI | Triangle Area | A = (1/2)bh, identifying valid base-height pairs | GEO_L1_AREA_RECT | Batterson 5.4; AoPS Geometry ch5 |
| GEO_L1_AREA_TRAP | Trapezoid Area | A = (1/2)(b1+b2)h | GEO_L1_AREA_RECT | Batterson 5.4 |

#### Pythagorean Theorem Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L1_PYTH_BASIC | Pythagorean Theorem | Apply a^2 + b^2 = c^2 to find missing side | GEO_L1_TRI_CLASS | Batterson 5.3; AoPS Geometry ch6 |
| GEO_L1_PYTH_TRIP | Pythagorean Triples | Recognize and use common triples (3-4-5, 5-12-13, 8-15-17, 7-24-25) | GEO_L1_PYTH_BASIC | Batterson 5.3; AoPS Geometry ch6 |
| GEO_L1_PYTH_DIST | Distance Formula | Apply d = √((x2-x1)^2+(y2-y1)^2) | GEO_L1_PYTH_BASIC | Batterson 5.3; AoPS Geometry ch6 |

### Level 2 — Intermediate (ELO 1000–1450)

#### Circles (Properties) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_CIRC_BASIC | Circle Definitions | Radius, diameter, chord, arc, sector, segment terminology | — | Batterson 5.2; AoPS Geometry ch11 |
| GEO_L2_CIRC_CENTINS | Central and Inscribed Angles | Central angle = arc; inscribed angle = half arc | GEO_L2_CIRC_BASIC | Batterson 5.2; AoPS Geometry ch11 |
| GEO_L2_CIRC_CHORD | Chord Properties | Equal chords subtend equal arcs, perpendicular from center bisects chord | GEO_L2_CIRC_BASIC | AoPS Geometry ch11 |
| GEO_L2_CIRC_TANG | Tangent Lines | Tangent perpendicular to radius, tangent from external point properties | GEO_L2_CIRC_BASIC | Batterson 5.2; AoPS Geometry ch12 |
| GEO_L2_CIRC_SEC | Secant Properties | Secant-secant and secant-tangent angle theorems | GEO_L2_CIRC_CENTINS; GEO_L2_CIRC_TANG | AoPS Geometry ch12 |

#### Similarity Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_SIM_CRIT | Similarity Criteria | Apply AA, SAS, SSS similarity tests | GEO_L1_TRI_CONG | Batterson 5.6; AoPS Geometry ch5 |
| GEO_L2_SIM_RATIO | Ratio Applications of Similarity | Side ratios, area ratios (square of linear ratio) | GEO_L2_SIM_CRIT | Batterson 5.6; AoPS Geometry ch5 |
| GEO_L2_SIM_RANGLE | Right Triangle Similarity | Altitude to hypotenuse creates similar triangles, geometric mean relations | GEO_L2_SIM_CRIT; GEO_L1_PYTH_BASIC | AoPS Geometry ch6 |

#### Special Right Triangles Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_SRT_3060 | 30-60-90 Triangles | Side ratio 1:√3:2 | GEO_L1_PYTH_BASIC | Batterson 5.3; AoPS Geometry ch6 |
| GEO_L2_SRT_4545 | 45-45-90 Triangles | Side ratio 1:1:√2 | GEO_L1_PYTH_BASIC | Batterson 5.3; AoPS Geometry ch6 |
| GEO_L2_SRT_RECOG | Recognition in Complex Figures | Identify hidden special right triangles in larger diagrams | GEO_L2_SRT_3060; GEO_L2_SRT_4545 | Competition archives |

#### Advanced Area Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_AAREA_HERON | Heron's Formula | A = √(s(s-a)(s-b)(s-c)) where s = (a+b+c)/2 | GEO_L1_AREA_TRI | Batterson 5.4; AoPS Geometry ch5 |
| GEO_L2_AAREA_SHOE | Shoelace Formula | Area from coordinates: (1/2)|Σ(x_i*y_{i+1} - x_{i+1}*y_i)| | GEO_L1_AREA_TRI; GEO_L1_PYTH_DIST | AoPS Geometry ch5 |
| GEO_L2_AAREA_COMP | Composite Area Problems | Add/subtract standard areas to find irregular regions | GEO_L1_AREA_TRI; GEO_L1_AREA_TRAP | Batterson 5.4 |
| GEO_L2_AAREA_CIRC | Circle Area and Circumference | A = πr^2, C = 2πr, sector and segment areas | GEO_L2_CIRC_BASIC | Batterson 5.4; AoPS Geometry ch12 |

#### Special Triangle Parts Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_SPART_MED | Medians and Centroid | Median bisects opposite side, centroid divides medians 2:1 | GEO_L1_TRI_CLASS | AoPS Geometry ch7 |
| GEO_L2_SPART_ALT | Altitudes and Orthocenter | Altitude properties, orthocenter location for acute/right/obtuse | GEO_L1_TRI_CLASS; GEO_L1_PYTH_BASIC | AoPS Geometry ch7 |
| GEO_L2_SPART_BISECT | Angle Bisectors and Incenter | Angle bisector theorem, incircle, inradius | GEO_L2_SIM_RATIO | AoPS Geometry ch7 |
| GEO_L2_SPART_PBIS | Perpendicular Bisectors and Circumcenter | Circumcircle, circumradius, equidistance from vertices | GEO_L1_TRI_CONG | AoPS Geometry ch7 |

#### 3D Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_3D_PRISM | Prisms and Cylinders | Volume = Bh, surface area computations | GEO_L1_AREA_RECT | Batterson 5.5; AoPS Geometry ch14 |
| GEO_L2_3D_PYR | Pyramids and Cones | V = (1/3)Bh, slant height, lateral area | GEO_L1_AREA_TRI; GEO_L1_PYTH_BASIC | Batterson 5.5; AoPS Geometry ch14 |
| GEO_L2_3D_SPH | Spheres | V = (4/3)πr^3, SA = 4πr^2 | GEO_L2_AAREA_CIRC | Batterson 5.5; AoPS Geometry ch15 |
| GEO_L2_3D_VOL | Composite 3D Problems | Volume of intersections, cuts, and composite solids | GEO_L2_3D_PRISM; GEO_L2_3D_PYR | AoPS Geometry ch14-15 |

#### Coordinate Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L2_COORD_MID | Midpoint Formula | Find midpoint of segment from endpoints | GEO_L1_PYTH_DIST | AoPS Geometry ch17; Gelfand Method of Coordinates |
| GEO_L2_COORD_LINE | Line Equations in Coordinate Plane | Write and use equations of lines through given points | ALG_L1_LINE_FORMS; GEO_L2_COORD_MID | AoPS Geometry ch17 |
| GEO_L2_COORD_CIRC | Circle Equations | Standard form (x-h)^2+(y-k)^2=r^2, complete square to find center/radius | ALG_L2_QUAD_COMP; GEO_L2_CIRC_BASIC | AoPS Geometry ch17 |
| GEO_L2_COORD_DIST | Distance from Point to Line | Apply d = |ax+by+c|/√(a^2+b^2) | GEO_L2_COORD_LINE; GEO_L1_PYTH_DIST | AoPS Geometry ch17; Gelfand Method of Coordinates |

### Level 3 — Advanced (ELO 1300–1650)

#### Power of a Point Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_POP_CHORD | Intersecting Chords | PA·PB = PC·PD for chords through interior point P | GEO_L2_CIRC_CHORD; GEO_L2_SIM_CRIT | AoPS Geometry ch13; AoPS Basics ch18 |
| GEO_L3_POP_SECTAN | Secant-Tangent | PA·PB = PT^2 for external point P | GEO_L3_POP_CHORD; GEO_L2_CIRC_TANG | AoPS Geometry ch13 |
| GEO_L3_POP_SECSEC | Secant-Secant | PA·PB = PC·PD for two secants from external point P | GEO_L3_POP_CHORD | AoPS Geometry ch13 |
| GEO_L3_POP_APPLY | Power of a Point Applications | Use PoP to find segment lengths, prove collinearity/concyclicity | GEO_L3_POP_CHORD; GEO_L3_POP_SECTAN | Competition archives |

#### Circle Theorems Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_CTHM_INCIRC | Incircle and Inradius | Compute inradius r = Area/s, tangent length properties | GEO_L2_SPART_BISECT; GEO_L2_CIRC_TANG | AoPS Geometry ch11-12 |
| GEO_L3_CTHM_CIRCUMC | Circumcircle and Circumradius | Compute R = abc/(4K), apply extended law of sines | GEO_L2_SPART_PBIS | AoPS Geometry ch11 |
| GEO_L3_CTHM_PTOLEMY | Ptolemy's Theorem | AC·BD = AB·CD + AD·BC for cyclic quadrilateral ABCD | GEO_L3_POP_CHORD; GEO_L2_SIM_CRIT | AoPS Geometry ch13 |
| GEO_L3_CTHM_RADICAL | Radical Axes | Locus of equal power w.r.t. two circles, radical center of three circles | GEO_L3_POP_APPLY | AoPS Geometry ch13 |

#### Transformations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_TRANS_REFL | Reflections | Reflect points/shapes over lines, apply to shortest path problems | GEO_L2_COORD_LINE | AoPS Geometry ch16; Gelfand Geometry III |
| GEO_L3_TRANS_ROT | Rotations | Rotate figures about a point by given angle | GEO_L3_TRANS_REFL; GEO_L1_ANG_MEAS | AoPS Geometry ch16 |
| GEO_L3_TRANS_DILA | Dilations | Scale figures from a center by ratio k, homothety | GEO_L2_SIM_RATIO | AoPS Geometry ch16; Gelfand Geometry IV |
| GEO_L3_TRANS_COMP | Composition of Transformations | Combine reflections, rotations, translations, and dilations | GEO_L3_TRANS_REFL; GEO_L3_TRANS_ROT; GEO_L3_TRANS_DILA | AoPS Geometry ch16 |

#### Trigonometry in Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_TRIG_BASIC | Trig Ratios in Right Triangles | sin, cos, tan for solving right triangle problems | GEO_L2_SRT_3060; GEO_L2_SRT_4545 | AoPS Geometry ch18; Gelfand Trigonometry ch1 |
| GEO_L3_TRIG_LSIN | Law of Sines | Apply a/sin A = b/sin B = c/sin C = 2R | GEO_L3_TRIG_BASIC; GEO_L3_CTHM_CIRCUMC | AoPS Geometry ch18; Gelfand Trigonometry ch3 |
| GEO_L3_TRIG_LCOS | Law of Cosines | Apply c^2 = a^2 + b^2 - 2ab cos C | GEO_L3_TRIG_BASIC; GEO_L1_PYTH_BASIC | AoPS Geometry ch18; Gelfand Trigonometry ch3 |
| GEO_L3_TRIG_AREA | Trig Area Formula | Apply Area = (1/2)ab sin C | GEO_L3_TRIG_BASIC; GEO_L1_AREA_TRI | AoPS Geometry ch18 |

#### Geometric Inequalities Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_GINEQ_TRI | Triangle Inequality | Apply a+b > c and side-angle ordering | GEO_L1_TRI_CLASS | AoPS Geometry ch10 |
| GEO_L3_GINEQ_ANGSIDE | Angle-Side Relationships | Larger angle opposite longer side, Ravi substitution | GEO_L3_GINEQ_TRI | AoPS Geometry ch10 |
| GEO_L3_GINEQ_AREA | Area Inequalities | Isoperimetric inequality for triangles and quadrilaterals | GEO_L3_GINEQ_TRI; GEO_L1_AREA_TRI | AoPS Geometry ch10 |

#### Analytic Geometry Proofs Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_ANLT_PROOF | Coordinate Proofs | Place figures on coordinate plane and prove properties algebraically | GEO_L2_COORD_LINE; GEO_L2_COORD_MID | AoPS Geometry ch17; Gelfand Method of Coordinates |
| GEO_L3_ANLT_PARAM | Parametric Methods | Use parametric equations for lines and circles in proofs | GEO_L3_ANLT_PROOF; GEO_L2_COORD_CIRC | AoPS Geometry ch17 |
| GEO_L3_ANLT_LOCUS | Locus Problems | Determine the set of all points satisfying a geometric condition | GEO_L3_ANLT_PROOF | Gelfand Method of Coordinates |

#### Complex Numbers in Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L3_CPLXG_ROT | Rotation via Complex Multiplication | Multiply by e^(iθ) to rotate points in the plane | ALG_L3_CPLX_MOD; GEO_L3_TRANS_ROT | AoPS Precalculus ch8 |
| GEO_L3_CPLXG_SPIRAL | Spiral Similarity | Combine rotation and dilation as single complex multiplication | GEO_L3_CPLXG_ROT; GEO_L3_TRANS_DILA | AoPS Precalculus ch8 |

### Level 4 — AMC 12 / AIME (ELO 1600–2100)

#### Conic Sections Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_CONIC_PARA | Parabolas (Geometric) | Focus, directrix, reflective property, parametric form | ALG_L2_GQUAD_PARA; GEO_L2_COORD_LINE | AoPS Precalculus ch4 |
| GEO_L4_CONIC_ELLP | Ellipses | Standard form, foci, eccentricity, reflective property | GEO_L4_CONIC_PARA; GEO_L2_COORD_CIRC | AoPS Precalculus ch4 |
| GEO_L4_CONIC_HYPR | Hyperbolas | Standard form, asymptotes, foci, eccentricity | GEO_L4_CONIC_ELLP | AoPS Precalculus ch4 |
| GEO_L4_CONIC_GEN | General Conic Classification | Classify Ax^2+Bxy+Cy^2+Dx+Ey+F=0 by discriminant B^2-4AC | GEO_L4_CONIC_PARA; GEO_L4_CONIC_ELLP; GEO_L4_CONIC_HYPR | AoPS Precalculus ch4; AIME archives |

#### Advanced Triangle Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_ATRI_CEVA | Ceva's Theorem | Cevians AD, BE, CF concurrent iff (AF/FB)(BD/DC)(CE/EA)=1 | GEO_L2_SIM_RATIO; GEO_L2_SPART_MED | AoPS Geometry ch7 |
| GEO_L4_ATRI_MENEL | Menelaus' Theorem | Transversal cutting triangle sides gives signed ratio product = -1 | GEO_L4_ATRI_CEVA | AoPS Geometry ch7 |
| GEO_L4_ATRI_STEW | Stewart's Theorem | a^2n + b^2m - c^2d = mnd for cevian of length d | GEO_L2_SIM_RATIO; GEO_L3_TRIG_LCOS | AoPS Geometry ch7 |
| GEO_L4_ATRI_EULER | Euler Line | Circumcenter, centroid, orthocenter are collinear (OG:GH = 1:2) | GEO_L2_SPART_MED; GEO_L2_SPART_ALT; GEO_L2_SPART_PBIS | AoPS Geometry ch7 |
| GEO_L4_ATRI_NINEPC | Nine-Point Circle | Circle through midpoints, feet of altitudes, and Euler midpoints | GEO_L4_ATRI_EULER; GEO_L3_CTHM_CIRCUMC | AoPS Geometry ch13 |

#### Advanced Circle Geometry Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_ACIRC_INVRS | Circle Inversion | Map points P to P' with OP·OP'=r^2, lines/circles map to lines/circles | GEO_L3_POP_APPLY; GEO_L3_TRANS_DILA | AoPS Geometry ch13; Competition archives |
| GEO_L4_ACIRC_COAX | Coaxial Circles | Families of circles sharing a radical axis | GEO_L3_CTHM_RADICAL | Competition archives |
| GEO_L4_ACIRC_TANG | Advanced Tangent Circles | Descartes circle theorem, Apollonian gaskets (exposure) | GEO_L4_ACIRC_INVRS; GEO_L2_CIRC_TANG | AIME archives |

#### Trigonometric Geometry (Advanced) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_ATRIG_CEVTRI | Trig Cevian Applications | Combine trig with Ceva/Menelaus/Stewart | GEO_L4_ATRI_CEVA; GEO_L3_TRIG_LSIN | AoPS Geometry ch18 |
| GEO_L4_ATRIG_CIRCQ | Cyclic Quadrilateral Trigonometry | Apply Ptolemy + trig to cyclic quads, Brahmagupta's formula | GEO_L3_CTHM_PTOLEMY; GEO_L3_TRIG_AREA | Competition archives |
| GEO_L4_ATRIG_AREAS | Advanced Trig Area Methods | R·r·s relationships, area from angles and one side | GEO_L3_TRIG_AREA; GEO_L3_CTHM_INCIRC; GEO_L3_CTHM_CIRCUMC | AoPS Geometry ch18 |

#### Coordinate Geometry (Advanced) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_ACOORD_AFFINE | Affine Coordinates | Barycentric and areal coordinates for triangle problems | GEO_L2_COORD_LINE; GEO_L4_ATRI_CEVA | Competition archives |
| GEO_L4_ACOORD_CPLX | Complex Coordinate Geometry | Solve AIME-level geometry via complex numbers in the plane | ALG_L4_CPLX_GEOM; GEO_L3_CPLXG_SPIRAL | AIME archives |
| GEO_L4_ACOORD_POLAR | Polar Coordinates | Convert between polar/Cartesian, graph polar curves | GEO_L2_COORD_CIRC; ALG_L3_CPLX_MOD | AoPS Precalculus ch3 |

#### 3D Geometry (Advanced) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L4_A3D_CROSS | Cross Sections of Solids | Find cross-section shapes and areas when planes cut solids | GEO_L2_3D_VOL; GEO_L2_SIM_RATIO | AIME archives |
| GEO_L4_A3D_DIHED | Dihedral Angles | Compute angle between two planes meeting along a line | GEO_L2_3D_PYR; GEO_L3_TRIG_BASIC | AIME archives |
| GEO_L4_A3D_COORD | 3D Coordinates | Apply distance, midpoint, plane equations in 3D | GEO_L2_COORD_LINE; ALG_L4_VEC_OPS | AoPS Precalculus ch9 |
| GEO_L4_A3D_POLY | Regular Polyhedra | Platonic solids: vertex/edge/face counts, volumes, inscribed/circumscribed spheres | GEO_L2_3D_VOL; GEO_L1_POLY_ANG | Competition archives |

### Level 5 — Olympiad Track (ELO 2100+)

#### Projective Geometry (Exposure) Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L5_PROJ_HARMON | Harmonic Division | Cross-ratio = -1, harmonic conjugates, pole-polar duality | GEO_L4_ATRI_CEVA; GEO_L4_ATRI_MENEL | Olympiad references |
| GEO_L5_PROJ_PASCAL | Pascal's Theorem | Opposite sides of hexagon inscribed in conic meet collinearly | GEO_L3_CTHM_PTOLEMY | Olympiad references |
| GEO_L5_PROJ_BRIAN | Brianchon's Theorem | Diagonals of hexagon circumscribed about conic are concurrent | GEO_L5_PROJ_PASCAL | Olympiad references |

#### Inversion and Advanced Transformations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L5_AINV_PROB | Inversion Problem Solving | Apply inversion to simplify tangent circle and collinearity problems | GEO_L4_ACIRC_INVRS | Olympiad references |
| GEO_L5_AINV_SPIRAL | Spiral Centers and Miquel Points | Locate spiral center via two similar triangles, Miquel point theorem | GEO_L3_CPLXG_SPIRAL; GEO_L4_ATRI_CEVA | Olympiad references |

#### Olympiad Geometry Techniques Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| GEO_L5_OGEOM_ANGCH | Angle Chasing (Advanced) | Multi-step angle chasing through cyclic quads, tangent lines, and reflections | GEO_L3_POP_APPLY; GEO_L2_CIRC_CENTINS | Olympiad references |
| GEO_L5_OGEOM_MOVE | Moving Points Method | Reduce geometric claims to polynomial degree arguments via parametrization | GEO_L3_ANLT_PARAM; ALG_L4_APOL_INTER | Olympiad references |
| GEO_L5_OGEOM_TRIG | Trigonometric Bash | Solve olympiad geometry by converting everything to trig expressions | GEO_L4_ATRIG_CEVTRI; ALG_L4_TRIG_PRODSUM | Olympiad references |
| GEO_L5_OGEOM_BARY | Barycentric Coordinates (Advanced) | Full barycentric toolkit: displacement vectors, circumcircle equation | GEO_L4_ACOORD_AFFINE | Olympiad references |
| GEO_L5_OGEOM_CPLX | Complex Bash (Advanced) | Systematic complex-number approach to olympiad geometry | GEO_L4_ACOORD_CPLX; ALG_L4_CPLX_ROOT | Olympiad references |

---

## Domain 5: Arithmetic / Prealgebra

### Level 1 — Foundations (ELO 400–1200)

#### Integer Operations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L1_INT_ADD | Addition and Subtraction | Add and subtract signed integers correctly | — | Prealgebra |
| ARITH_L1_INT_MULT | Multiplication and Division | Multiply and divide signed integers, sign rules | ARITH_L1_INT_ADD | Prealgebra |
| ARITH_L1_INT_ORDER | Integer Ordering | Compare and order integers, number line reasoning | ARITH_L1_INT_ADD | Prealgebra |

#### Fractions Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L1_FRAC_OPS | Fraction Arithmetic | Add, subtract, multiply, divide fractions and mixed numbers | ARITH_L1_INT_MULT | Prealgebra |
| ARITH_L1_FRAC_SIMP | Fraction Simplification | Reduce fractions to lowest terms using GCF | ARITH_L1_FRAC_OPS | Prealgebra |
| ARITH_L1_FRAC_ORDER | Ordering Fractions | Compare fractions using common denominators or cross-multiplication | ARITH_L1_FRAC_OPS | Prealgebra |

#### Decimals Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L1_DEC_OPS | Decimal Operations | Add, subtract, multiply, divide decimals | ARITH_L1_INT_MULT | Prealgebra |
| ARITH_L1_DEC_CONV | Decimal-Fraction Conversion | Convert between decimal and fraction representations | ARITH_L1_DEC_OPS; ARITH_L1_FRAC_OPS | Prealgebra |
| ARITH_L1_DEC_ROUND | Rounding | Round decimals to given place value | ARITH_L1_DEC_OPS | Prealgebra |

#### Order of Operations Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L1_OOO_PEMDAS | PEMDAS | Apply order of operations correctly | ARITH_L1_INT_MULT | Prealgebra |
| ARITH_L1_OOO_NEST | Nested Expressions | Evaluate expressions with nested parentheses/brackets | ARITH_L1_OOO_PEMDAS | Prealgebra |

#### Absolute Value Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L1_ABS_DEF | Absolute Value Definition | Compute |x| and interpret as distance from zero | ARITH_L1_INT_ORDER | Prealgebra |

### Level 2 — Intermediate (ELO 1000–1450)

#### Ratios & Rates Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L2_RATE_UNIT | Unit Rates | Compute and compare unit rates (price per item, speed) | ARITH_L1_FRAC_OPS | Prealgebra; Batterson 1.4 |
| ARITH_L2_RATE_SDT | Speed-Distance-Time | Solve multi-step rate problems with multiple travelers or segments | ARITH_L2_RATE_UNIT | Batterson 1.1 |
| ARITH_L2_RATE_CONV | Unit Conversion | Convert between measurement systems (metric/imperial, time, etc.) | ARITH_L2_RATE_UNIT | Prealgebra |

#### Proportional Reasoning Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L2_PROP_SCALE | Scale Factors | Apply scale to maps, models, recipes | ARITH_L2_RATE_UNIT | Prealgebra |
| ARITH_L2_PROP_PCT | Percent Applications | Tax, tip, discount, markup, compound percent changes | ARITH_L2_PROP_SCALE | Batterson 1.4 |

#### Estimation Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L2_EST_MENTAL | Mental Math Strategies | Compute quickly using factoring, compensation, rounding tricks | ARITH_L1_INT_MULT | Competition practice |
| ARITH_L2_EST_APPROX | Approximation and Bounding | Estimate answers and determine if exact computation is needed | ARITH_L2_EST_MENTAL | Competition practice |
| ARITH_L2_EST_FERM | Fermi Estimation | Order-of-magnitude estimation for real-world quantities | ARITH_L2_EST_APPROX | Competition practice |

#### Basic Statistics Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L2_BSTAT_CENT | Central Tendency in Word Problems | Apply mean/median/mode in multi-step word problem contexts | ALG_L1_STAT_CENT | Batterson 1.8 |
| ARITH_L2_BSTAT_MISS | Missing Data Problems | Find the missing value given a target mean/median | ARITH_L2_BSTAT_CENT; ALG_L1_EXPR_SOLVE | Batterson 1.8 |
| ARITH_L2_BSTAT_INTER | Interpreting Data Displays | Read and analyze bar graphs, line plots, circle graphs, histograms | ARITH_L2_BSTAT_CENT | Batterson 1.8 |

### Level 3 — Advanced (ELO 1300–1650)

#### Competition Mental Math Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L3_CMM_SPEED | Speed Computation | Rapid mental arithmetic under countdown/sprint time pressure | ARITH_L2_EST_MENTAL | Competition practice |
| ARITH_L3_CMM_RECOG | Pattern Recognition in Computation | Spot shortcuts (factoring, telescoping, symmetry) in numeric computations | ARITH_L3_CMM_SPEED | Competition practice |

#### Advanced Word Problems Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L3_AWP_MULTI | Multi-Step Reasoning | Combine 3+ steps from different topic areas in a single word problem | ARITH_L2_RATE_SDT; ALG_L1_SYS_WORD | Competition archives |
| ARITH_L3_AWP_HIDDEN | Hidden Constraint Problems | Identify unstated constraints (integer solutions, positivity, boundary cases) | ARITH_L3_AWP_MULTI | Competition archives |
| ARITH_L3_AWP_OPT | Optimization Word Problems | Find maximum or minimum subject to real-world constraints | ARITH_L3_AWP_MULTI | Competition archives |

#### Harmonic Mean Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| ARITH_L3_HM_DEF | Harmonic Mean Definition | Compute HM = n / (1/x_1 + ... + 1/x_n) | ARITH_L1_FRAC_OPS | AoPS Algebra II ch12 |
| ARITH_L3_HM_APPLY | Harmonic Mean Applications | Apply HM to average speed, average rate problems | ARITH_L3_HM_DEF; ARITH_L2_RATE_SDT | AoPS Algebra II ch12 |
| ARITH_L3_HM_COMP | HM-GM-AM-QM Chain | Understand HM ≤ GM ≤ AM ≤ QM and when equality holds | ARITH_L3_HM_DEF; ALG_L3_AMGM_TWO | AoPS Algebra II ch12 |

---

## Domain 6: Logic & Strategy

### Level 1 — Foundations (ELO 400–1200)

#### Process of Elimination Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L1_POE_RULE | Systematic Ruling Out | Eliminate impossible answers using given constraints | — | AoPS Basics ch27 |
| LOGIC_L1_POE_GUESS | Strategic Guessing | Use answer choices to guide backward reasoning or narrowing | LOGIC_L1_POE_RULE | Competition strategy |
| LOGIC_L1_POE_TEST | Testing Values | Plug in specific values to test which answer satisfies conditions | LOGIC_L1_POE_RULE | Competition strategy |

#### Working Backwards Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L1_WB_REVERSE | Reversing Operations | Undo a sequence of operations to find the starting value | ALG_L1_EXPR_SOLVE | AoPS Basics ch27 |
| LOGIC_L1_WB_END | Working from End State | Start from a known final result and reverse-engineer the process | LOGIC_L1_WB_REVERSE | Competition strategy |

#### Organized Listing Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L1_OL_EXHAUST | Exhaustive Enumeration | List all possibilities systematically to find or count solutions | — | AoPS Basics ch27 |
| LOGIC_L1_OL_NODUP | Avoiding Overcounting | Ensure each case is counted exactly once in a listing | LOGIC_L1_OL_EXHAUST | AoPS Basics ch27 |

#### Pattern Recognition Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L1_PAT_SEQ | Sequence Pattern Recognition | Identify the rule generating a numerical sequence | — | AoPS Basics ch27 |
| LOGIC_L1_PAT_STRUCT | Structural Pattern Recognition | See repeating geometric, algebraic, or logical structures | LOGIC_L1_PAT_SEQ | AoPS Basics ch27 |
| LOGIC_L1_PAT_SMALL | Solve Small Cases First | Compute small cases to discover pattern, then generalize | LOGIC_L1_PAT_SEQ | Competition strategy |
| LOGIC_L1_PAT_GEN | Generalization from Examples | Formulate a conjecture from computed small cases | LOGIC_L1_PAT_SMALL | Competition strategy |

### Level 2 — Intermediate (ELO 1000–1450)

#### Pigeonhole Principle Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L2_PIG_BASIC | Basic Pigeonhole Principle | If n+1 items go into n bins, some bin has ≥2 | — | AoPS Basics ch28 |
| LOGIC_L2_PIG_GEN | Generalized Pigeonhole | If kn+1 items go into n bins, some bin has ≥k+1 | LOGIC_L2_PIG_BASIC | AoPS Basics ch28 |
| LOGIC_L2_PIG_EXIST | Existential Pigeonhole Applications | Use pigeonhole to prove existence of pair/group with given property | LOGIC_L2_PIG_BASIC | Competition archives |

#### Proof by Contradiction Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L2_CONTRA_SETUP | Contradiction Setup | Assume negation of desired statement, derive logical steps | — | AoPS Basics ch28 |
| LOGIC_L2_CONTRA_IRRAT | Irrationality Proofs | Prove √2 is irrational and similar via contradiction | LOGIC_L2_CONTRA_SETUP; NT_L1_PRIM_PFACT | AoPS Basics ch28 |
| LOGIC_L2_CONTRA_EXIST | Non-Existence Proofs | Show no solution exists by deriving contradiction from any candidate | LOGIC_L2_CONTRA_SETUP | AoPS Basics ch28 |

#### Invariants & Monovariants Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L2_INV_IDENT | Identifying Invariants | Find a quantity that stays constant through all operations | — | AoPS Basics ch28 |
| LOGIC_L2_INV_MONO | Monovariants | Find a quantity that strictly increases or decreases each step | LOGIC_L2_INV_IDENT | AoPS Basics ch28 |
| LOGIC_L2_INV_COLOR | Coloring Arguments | Assign colors/labels to show impossibility of tiling or covering | LOGIC_L2_INV_IDENT | Competition archives |

#### Parity Arguments Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L2_PAR_BASIC | Basic Parity | Use even/odd reasoning to prove impossibility or narrow cases | — | AoPS Basics ch28 |
| LOGIC_L2_PAR_ADV | Advanced Parity | Apply parity to sums, products, counts, and checkerboard arguments | LOGIC_L2_PAR_BASIC; LOGIC_L2_INV_COLOR | AoPS Basics ch28 |

### Level 3 — Advanced (ELO 1300–1650)

#### Mathematical Induction Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L3_IND_BASIC | Basic Induction | Prove P(n) for all n≥1 via base case + inductive step | LOGIC_L1_PAT_GEN | AoPS Basics ch28 |
| LOGIC_L3_IND_STRONG | Strong Induction | Assume P(1)...P(k) to prove P(k+1) | LOGIC_L3_IND_BASIC | AoPS Basics ch28 |
| LOGIC_L3_IND_STRUCT | Structural Induction | Apply induction on non-integer structures (trees, expressions, etc.) | LOGIC_L3_IND_STRONG | Competition archives |

#### Advanced Pigeonhole Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L3_APIG_CONT | Continuous Pigeonhole | Apply pigeonhole in continuous/geometric settings | LOGIC_L2_PIG_GEN | Competition archives |
| LOGIC_L3_APIG_RAMSEY | Ramsey-Type Arguments | Party problem, monochromatic structures in colorings | LOGIC_L3_APIG_CONT; LOGIC_L2_PIG_EXIST | Competition archives |

#### Strategy Games Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L3_GAME_SYMM | Symmetry Strategies | Win by mirroring opponent's moves | LOGIC_L2_INV_IDENT | AoPS Basics ch27 |
| LOGIC_L3_GAME_PAIR | Pairing Strategies | Partition positions into pairs, always move within partner's pair | LOGIC_L3_GAME_SYMM | AoPS Basics ch27 |
| LOGIC_L3_GAME_NIMVAL | Nim Values and Grundy Theory (Exposure) | Assign Grundy values to game positions, XOR strategy | LOGIC_L3_GAME_PAIR; NT_L2_BASE_CONV | Competition archives |

#### Extremal Principle Cluster

| ID | Skill Name | Description | Prerequisites | Source Mapping |
|----|-----------|-------------|---------------|---------------|
| LOGIC_L3_EXTR_MIN | Minimum Counterexample | Assume smallest counterexample and derive contradiction | LOGIC_L2_CONTRA_SETUP; LOGIC_L3_IND_BASIC | Competition archives |
| LOGIC_L3_EXTR_MAX | Extremal Element Selection | Choose the largest/smallest/leftmost element to anchor an argument | LOGIC_L3_EXTR_MIN | Competition archives |
| LOGIC_L3_EXTR_GREED | Greedy Algorithm Arguments | Prove greedy approach is optimal or use it to bound answers | LOGIC_L3_EXTR_MAX; LOGIC_L2_INV_MONO | Competition archives |

---

## Cross-Domain Prerequisite Index

The following atomic skills serve as critical cross-domain prerequisites (most commonly required by skills in other domains):

| Skill ID | Used By Domains | Role |
|----------|----------------|------|
| ALG_L1_EXPR_SOLVE | All | Foundation for any equation solving |
| ALG_L2_QUAD_FORM | COUNT (recurrences), NT (quadratic residues), GEO (law of cosines) | Quadratic solving |
| ALG_L3_CPLX_MOD | GEO (complex geometry), COUNT (roots of unity) | Complex number fluency |
| NT_L2_MOD_BASIC | COUNT (derangements), ALG (floor functions), LOGIC (parity) | Modular arithmetic |
| GEO_L1_PYTH_BASIC | ALG (distance), NT (Pythagorean triples), COUNT (geometric probability) | Right triangle computation |
| COUNT_L2_COMB_NCR | ALG (binomial), NT (divisor counting arguments), GEO (lattice paths) | Combination formula fluency |
| GEO_L2_SIM_CRIT | ALG (optimization), COUNT (geometric probability) | Similarity reasoning |
| ALG_L2_EXP_LAWS | NT (FLT), COUNT (generating functions) | Exponent fluency |
| LOGIC_L2_PAR_BASIC | NT (Diophantine), GEO (coloring), COUNT (parity in counting) | Parity reasoning |
| LOGIC_L2_CONTRA_SETUP | NT (irrationality), GEO (impossibility), COUNT (extremal) | Proof technique |

## Diagnostic Coverage Guide

For the adaptive diagnostic (see data-model.md), sample across atomic skills as follows:

| Domain | L1 Sample | L2 Sample | L3 Sample | L4 Sample (if qualified) |
|--------|-----------|-----------|-----------|--------------------------|
| Counting | 3-4 skills | 3-4 skills | 2-3 skills | 1-2 skills |
| Algebra | 3-4 skills | 3-4 skills | 2-3 skills | 1-2 skills |
| Number Theory | 2-3 skills | 2-3 skills | 2-3 skills | 1-2 skills |
| Geometry | 3-4 skills | 3-4 skills | 2-3 skills | 1-2 skills |
| Arithmetic | 2-3 skills | 2 skills | 1 skill | — |
| Logic | 2 skills | 2 skills | 1 skill | — |

Total diagnostic items: ~50-60, consistent with GAPS.md target.

## ELO-to-Level Gating Reference

Per rating-system.md, skill node ratings determine content unlock:

| Level | Gate Rating | Gate RD | Approx. Atomic Skills Exposed |
|-------|------------|---------|-------------------------------|
| L1 | 400 (always open) | — | 115 |
| L2 | 1000 | <150 | +137 (252 cumulative) |
| L3 | 1300 | <150 | +137 (389 cumulative) |
| L4 | 1600 | <150 | +97 (486 cumulative) |
| L5 | 1900 | <150 | +42 (528 cumulative) |
