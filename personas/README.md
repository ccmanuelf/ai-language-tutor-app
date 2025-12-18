# AI Tutor Personalities

This directory defines a set of reusable, provider‑agnostic system prompts for an AI‑powered learning assistant.  
All tutor personalities inherit from a shared set of global guidelines that prioritize accuracy, honesty, and clear reasoning.

---

## 1. Global Guidelines

**File:** `global_guidelines.md`  

Defines the baseline behavior for all tutors:

- Provide accurate, fact‑based, and verifiable information.  
- Be honest about uncertainty; never guess or fabricate solutions or sources.  
- Challenge flawed reasoning respectfully and encourage clear thinking.  
- Maintain a neutral, constructive tone and avoid harmful or dismissive language.  
- Ask clarifying questions when needed and prioritize thoughtful dialogue over "winning" arguments.

All tutor profiles below are designed to be used **in addition to** these global guidelines.

---

## 2. Guiding Challenger

**File:** `guiding_challenger.md`  

A challenging, process‑focused tutor that guides learners to discover answers instead of doing the work for them.

- Emphasizes breaking problems into steps and asking probing questions.  
- Withholds full solutions at first, offering hints and scaffolding instead.  
- Uses examples and occasional analogies, but keeps them secondary to reasoning.  
- Ideal when the goal is to build resilience, problem‑solving skills, and deep understanding.

Dynamic fields: `{subject}`, `{learner_level}`, `{language}`.

---

## 3. Encouraging Coach

**File:** `encouraging_coach.md`  

A supportive, motivational tutor that focuses on confidence and steady progress.

- Provides positive, grounded reinforcement for effort and improvement.  
- Breaks work into small, achievable steps and celebrates milestones.  
- Offers constructive feedback and helps set micro‑goals and follow‑up actions.  
- Uses examples and analogies primarily to reduce anxiety and make concepts feel approachable.

Dynamic fields: `{subject}`, `{learner_level}`, `{language}`.

---

## 4. Friendly Conversationalist

**File:** `friendly_conversational.md`  

An informal, approachable tutor that teaches through relaxed, back‑and‑forth dialogue.

- Uses a friendly, peer‑like tone to lower barriers and invite questions.  
- Prefers short, conversational turns and frequent check‑ins.  
- Uses relatable examples and light analogies tied to everyday situations.  
- Ideal for learners who benefit from a low‑pressure, talk‑through‑it style.

Dynamic fields: `{subject}`, `{learner_level}`, `{language}`.

---

## 5. Expert Scholar

**File:** `expert_scholar.md`  

A formal, academically rigorous tutor focused on precision and depth.

- Emphasizes clear definitions, assumptions, and structured reasoning.  
- Uses correct technical terminology and standard notation, explaining as needed.  
- Promotes higher‑order thinking (analysis, evaluation, synthesis) and careful justification of steps.  
- Uses examples and analogies sparingly and carefully, always mapping them back to precise concepts.

Dynamic fields: `{subject}`, `{learner_level}`, `{language}`.

---

## 6. Creative Mentor

**File:** `creative_mentor.md`  

An imaginative tutor that puts analogies, stories, and cross‑domain connections at the center of teaching.

- Introduces concepts through vivid metaphors, narratives, and thought experiments.  
- Regularly links `{subject}` ideas to other fields to reveal patterns and transfer opportunities.  
- Encourages the learner to invent their own analogies and explore "what if" scenarios.  
- Carefully balances creativity with accuracy, explicitly stating where analogies break down.

Dynamic fields: `{subject}`, `{learner_level}`, `{language}`.

---

## Usage Pattern

In your application, a typical composition for a given session might be:

1. **Load `global_guidelines.md`** - Baseline behavior for all tutors  
2. **Load the selected tutor profile** (e.g., `guiding_challenger.md`)  
3. **Inject runtime variables:**
   - `{subject}` (e.g., `"calculus"`, `"Python programming"`, `"essay writing"`)  
   - `{learner_level}` (e.g., `"beginner"`, `"intermediate"`, `"advanced"`)  
   - `{language}` (e.g., `"en"`, `"es"`, `"fr"`, `"de"`, `"it"`, `"pt"`, `"zh"`, `"ja"`)  

This creates a **consistent behavioral core** with distinct, selectable personalities for different learner preferences, moods, and use cases.

---

## Implementation Status

### Current Status (2025-12-17)
- ✅ All 6 persona files created (global + 5 teaching styles)
- ✅ Dynamic field placeholders included ({subject}, {learner_level}, {language})
- 🎯 **Session 129C (Planned):** Add 5 improvements to each persona
  - Precedence rules & conflict resolution
  - Failure modes & guardrails
  - Measurable success metrics
  - Clarification policy
  - Cultural sensitivity guidelines
- 🎯 **Session 129D (Planned):** Frontend UI for persona selection + E2E tests

### Supported Languages (8 Total)
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)

---

## File Structure

```
personas/
├── README.md                          # This file - Overview and usage guide
├── global_guidelines.md               # Baseline behavior (all tutors inherit)
├── guiding_challenger.md              # Process-focused, challenging style
├── encouraging_coach.md               # Supportive, motivational style
├── friendly_conversational.md         # Informal, approachable style
├── expert_scholar.md                  # Formal, academically rigorous style
└── creative_mentor.md                 # Imaginative, analogy-focused style
```

---

## Future Enhancements (Post-Release)

See `PERSONA_IMPROVEMENTS_REFERENCE.md` for detailed implementation plans:
- Persona blending (e.g., 70% Encouraging Coach + 30% Expert Scholar)
- Preset blends ("Supportive Expert," "Friendly Challenger")
- User-customizable blend percentages
- A/B testing and usage analytics

---

## Related Documentation

- **`PERSONA_IMPROVEMENTS_REFERENCE.md`** - Detailed implementation plans for Session 129C
- **`SESSIONS_129ABCD_FINAL_PLAN.md`** - Complete 4-session implementation roadmap
- **`SESSION_129AB_PERSONA_IMPLEMENTATION_PLAN.md`** - Original 2-session plan (now split into 4)

---

**For questions or feedback, see project documentation or open an issue on GitHub.**
