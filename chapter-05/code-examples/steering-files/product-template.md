# Product Overview Template

Use this template to create your own `product.md` steering file. Place the completed file in `.kiro/steering/product.md`.

---

````markdown
---
inclusion: always
---

# Product Overview

## [Product Name]

[Provide a clear, one-paragraph description of what the product is and the
problem it solves. This should give anyone reading it an immediate understanding
of the product's purpose.]

## Core Features

List the primary capabilities of your product. Each feature should include
a brief description of what it does and why it matters.

- **[Feature Name 1]**: [What it does and the benefit it provides]
- **[Feature Name 2]**: [What it does and the benefit it provides]
- **[Feature Name 3]**: [What it does and the benefit it provides]
- **[Feature Name 4]**: [What it does and the benefit it provides]

## Persona & Voice (Optional)

If your product has a specific personality or communication style, describe
it here. This helps maintain consistency in generated content.

The application maintains a "[Persona Name]" persona that:
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]
- [Characteristic 4]

## Target Users

Describe who will use this product. Be specific about their roles,
technical expertise, and what they need from the product.

- [User Type 1]: [Brief description of their needs]
- [User Type 2]: [Brief description of their needs]
- [User Type 3]: [Brief description of their needs]

## Business Objectives

What business goals does this product support? These help agents understand
the "why" behind technical decisions.

- [Objective 1]
- [Objective 2]
- [Objective 3]

## Success Metrics (Optional)

How will success be measured? This helps prioritize features and trade-offs.

- [Metric 1]: [Target value]
- [Metric 2]: [Target value]
- [Metric 3]: [Target value]

## Non-Goals (Optional)

What is explicitly out of scope? This prevents scope creep in generated code.

- [Non-goal 1]
- [Non-goal 2]
````

---

## Example: Tech News Aggregator

````markdown
---
inclusion: always
---

# Product Overview

## Tech News Aggregator

A web application that serves as a tech news aggregator with a distinctive
"Witty Tech Journalist" persona. The system curates technology stories from
various sources and presents them with sharp, concise, and slightly cynical
summaries that prioritize substance over hype.

## Core Features

- **Automated Story Collection**: Collects tech news from multiple sources
  (starting with Hacker News)
- **AI-Powered Summaries**: Uses Amazon Bedrock (Claude models) to generate
  witty, cynical commentary
- **Quality Curation**: Filters stories based on relevance, quality scores,
  and timeliness
- **Responsive Web Interface**: Clean, distraction-free design optimized for
  readability
- **Daily Briefings**: Automated generation of daily tech news briefings in
  markdown format

## Persona & Voice

The application maintains a "Witty Tech Journalist" persona that:
- Cuts through tech industry hype and marketing language
- Provides skeptical, substance-focused commentary
- Translates complex technical concepts into accessible language
- Maintains sharp, slightly cynical tone while being informative
- Prioritizes meaningful insights over promotional content

## Target Users

- Tech-savvy professionals seeking curated, quality content
- Busy developers and engineers who want efficient news consumption
- Readers who appreciate skeptical takes on tech industry trends
- Anyone looking for substance over hype in technology news

## Business Objectives

- Provide reliable daily briefings that save users time
- Establish a distinctive voice in tech news aggregation
- Build a platform that can expand to additional news sources
- Demonstrate effective use of AI for content curation
````

---

## Tips for Writing product.md

1. **Be Specific**: Vague descriptions lead to vague implementations
2. **Focus on Value**: Emphasize what problems you're solving
3. **Know Your Users**: Clear user definitions help prioritize features
4. **Set Boundaries**: Non-goals prevent unnecessary complexity
5. **Keep It Current**: Update as product direction evolves
