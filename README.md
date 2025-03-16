# Workshop Setting – Team Captain Generative AI / Davis Copilot

## Considerations
- Held in English
- Stay in time, but make use of the available time
- Feel free to make assumptions, but clearly state these

## Agenda (roughly 1.5 hrs)

### **Introduction (5 minutes) – All Participants**
- Quick introduction of all participants.

### **Task 1 (10 minutes) – Candidate**
- Kick it off by presenting one of your career highlights!
- Re-purpose a presentation if you happen to have one or prepare slides about something of which you are proud.
- Explain why, your role, and how you delivered value with the team(s).
- Share the key use case (limit to one) and challenges along the way with us.

### **Task 2 (10 minutes) – The Team Captain Role**
Your understanding of the Team Captain role:
Based on your current understanding of the role as well as the information passed along in previous interviewing rounds, please provide your thoughts on the following:
- What are the key responsibilities that must be addressed? What falls outside the scope of a Team Captain?
- What is the principal value that a Team Captain brings to the team you would be leading?
- What is the ideal division of responsibilities between a Team Captain and a Product Owner?

### **Task 3 (20 minutes) – Leadership Challenges**
The key aspect of leadership as a Team Captain is to lead a team without direct authority or power over the team members – *primus inter pares*.

Guiding questions:
- What are the fundamental aspects of that leadership style?
- How can it be successfully implemented and lived every day?
- Which challenges might arise and how can these be resolved?
- (Feel free to add additional topics you want to cover.)

### **Task 4 (25-30 minutes) – Technical Part**
Business analytics is concerned with generating data-driven summaries for decision-making. The data required for these reports is stored in relational databases, and SQL is used to retrieve the data.

With the advent of LLMs, there is now the possibility to formulate a reporting task in natural language and let AI generate the required SQL statements. This makes data easily accessible and should allow business analysts to focus on data questions instead of thinking about SQL syntax.

#### **Goal**
Develop a natural language (NL) interface for generating SQL queries to ease the search in *The History of Baseball* database. This involves:
1. Creating a prompting concept.
2. Defining a way to test results for regression or improvements when modifying the initial prompt.

---

#### **[Part A] Development of a Prompt (Theoretical Part)**
- Create a prompting concept to produce SQL queries from NL for execution on the database.
- Consider how a prompt for such queries could look, including:
  - Instruction
  - Context describing the database
  - User input
- Use an example from a test set like [KaggleDBQA](https://github.com/chiahsuan156/KaggleDBQA).
- Prepare a written prompt template with placeholders and one specific example of how it would be sent to the LLM.
- Explain which sections of the prompt contain what information, why it is relevant, and what prompting concepts were used.

---

#### **[Part B] Implementation of a Test Approach for Generated Queries (Practical Part)**
- Assume that the prompt in Part A is implemented and can generate SQL statements from NL.
- The file `examples_queries_test.json` contains exemplary NL queries and expected SQL responses (ground truth).
- The file `generated_queries.json` contains LLM-generated pairs.

However, the generated responses only partially match the expected SQL queries. Your task is to:
- Investigate the validity of the differences.
- Develop a test framework (e.g., using Python) for automated assessment of differences.
- Ensure the framework can be reused for multiple evaluation runs.
- Consider how the framework could be integrated into a CI/CD pipeline to monitor improvements or regressions after code changes.
- Present and explain your test framework, provide examples, and justify your implementation choices.

---

### **Remarks**
- **Part A** is theoretical and does not require working code. However, be specific about wording and structure, and discuss potential implementations (e.g., templates).
- **Part B** focuses on problem-solving and coding capabilities.
  - We will review and discuss your solution and code together.
  - Production-ready code is not expected, but we may discuss additional steps needed to reach that level.
- While we might discuss the topic more broadly, it is **not necessary** to prepare insights on the general working principles of an LLM beyond the given tasks.

---

### **Closing & Feedback Round (5 minutes) – All Participants**