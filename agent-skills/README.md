# Agent Skills Collection

A curated collection of specialized agent skills for AI agents. Each skill provides focused, reusable instructions for specific tasks and domains.

## Overview

Agent Skills are packaged instructions that extend AI agent capabilities. They follow a standardized format making them easy to integrate into any LLM-powered application.

## Available Skills

### 🔍 Intelligence & Analysis
- **Intelligence Analyst** - Gather, synthesize and analyze information from multiple sources
- - **Market Researcher** - Identify trends, analyze competition, and research market opportunities
  - - **Risk Assessor** - Evaluate risks, identify vulnerabilities, and suggest mitigations
   
    - ### 🛠️ Development & Technical
    - - **System Architect** - Design scalable systems and technical solutions
      - - **API Designer** - Create RESTful APIs with clear specifications and documentation
        - - **Database Optimizer** - Optimize database queries and design schemas
         
          - ### 📚 Knowledge & Learning
          - - **Documentation Expert** - Create clear, comprehensive technical documentation
            - - **Tutorial Creator** - Develop step-by-step tutorials and learning materials
              - - **Knowledge Synthesizer** - Consolidate information into cohesive summaries
               
                - ### 💼 Business & Strategy
                - - **Business Analyst** - Analyze business requirements and propose solutions
                  - - **Proposal Writer** - Create compelling proposals and pitches
                    - - **Stakeholder Manager** - Manage stakeholder communication and expectations
                     
                      - ### ✨ Creative & Content
                      - - **Brand Strategist** - Develop brand positioning and messaging strategies
                        - - **UX Writer** - Create user-friendly copy and microcopy for interfaces
                          - - **Storyteller** - Craft engaging narratives and compelling stories
                           
                            - ## Skill Structure
                           
                            - Each skill follows this structure:
                           
                            - ```
                              skill-name/
                              ├── SKILL.md           # Required: Instructions for the agent
                              ├── examples/          # Optional: Usage examples
                              ├── templates/         # Optional: Reusable templates
                              └── README.md          # Optional: Extended documentation
                              ```

                              ## SKILL.md Format

                              Each skill contains a SKILL.md file with:

                              - **YAML Frontmatter**: Metadata (name, description, triggers, license)
                              - - **Instructions**: Detailed instructions for the agent
                                - - **Framework**: Step-by-step approach or methodology
                                  - - **Examples**: Real-world examples and use cases
                                    - - **Best Practices**: Tips and guidelines for optimal performance
                                     
                                      - ## How to Use
                                     
                                      - 1. Choose a skill relevant to your task
                                        2. 2. Copy the SKILL.md content to your agent's context
                                           3. 3. Use it with Claude, ChatGPT, or any compatible LLM
                                              4. 4. Customize instructions as needed for your specific use case
                                                
                                                 5. ## Integration
                                                
                                                 6. These skills can be used with:
                                                 7. - Claude (via projects or uploads)
                                                 - ChatGPT (via custom instructions)
                                                 - - Local LLMs (via system prompts)
                                                   - - LangChain & other frameworks
                                                     - - Custom AI applications
                                                      
                                                       - ## Contributing
                                                      
                                                       - To add new skills:
                                                       - 1. Create a new directory with a descriptive name
                                                         2. 2. Add a SKILL.md file following the standard format
                                                            3. 3. Include examples and documentation
                                                               4. 4. Submit a pull request
                                                                 
                                                                  5. ## License
                                                                 
                                                                  6. All skills are provided under the MIT License.
                                                                  7. 
