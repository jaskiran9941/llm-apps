from typing import List, Dict

class DemoScenarios:
    """Pre-built demo scenarios to showcase memory capabilities."""

    @staticmethod
    def get_all_scenarios() -> Dict[str, Dict]:
        """Get all available demo scenarios."""
        return {
            "episodic_demo": {
                "name": "Episodic Memory Demo",
                "description": "Shows how conversation context helps",
                "messages": [
                    "I'm planning a team event for 20 people",
                    "What's a good budget per person?",
                    "Can you suggest some activities?"
                ],
                "expected_with_memory": "Bot remembers 'team event for 20 people' throughout",
                "expected_without_memory": "Bot confused about context in later messages"
            },
            "semantic_demo": {
                "name": "Semantic Memory Demo",
                "description": "Shows knowledge retrieval from documents",
                "messages": [
                    "How many vacation days do TechCorp employees get?",
                    "Can I carry over unused days?",
                    "What holidays does the company observe?"
                ],
                "expected_with_memory": "Accurate answers from vacation policy document",
                "expected_without_memory": "Generic answers, no specific information"
            },
            "combined_demo": {
                "name": "Combined Memory Demo",
                "description": "Shows episodic + semantic working together",
                "messages": [
                    "Tell me about TechCorp's parental leave policy",
                    "Does that include adoptive parents?",
                    "How does this compare to the vacation policy we discussed earlier?"
                ],
                "expected_with_memory": "Accurate, contextual answers using both document retrieval and conversation history",
                "expected_without_memory": "Confused, can't connect to previous discussion"
            },
            "remote_work_demo": {
                "name": "Remote Work Policy Demo",
                "description": "Ask about remote work policies",
                "messages": [
                    "Can I work remotely?",
                    "How many days per week do I need to come to the office?",
                    "What equipment will the company provide?"
                ],
                "expected_with_memory": "Specific details from remote work policy",
                "expected_without_memory": "Generic advice about remote work"
            },
            "expense_demo": {
                "name": "Expense Reimbursement Demo",
                "description": "Ask about expense policies",
                "messages": [
                    "What's the meal reimbursement limit for dinner?",
                    "I'm traveling for work. What about hotel costs?",
                    "Can I expense a professional development course?"
                ],
                "expected_with_memory": "Specific dollar amounts and policies",
                "expected_without_memory": "Vague suggestions"
            },
            "context_memory_test": {
                "name": "Context Memory Test",
                "description": "Tests if LLM remembers earlier conversation",
                "messages": [
                    "My name is Sarah and I work in Engineering",
                    "I'm interested in taking some vacation next month",
                    "What did I tell you my name was?",
                    "Which department do I work in?"
                ],
                "expected_with_memory": "Correctly recalls Sarah and Engineering",
                "expected_without_memory": "Cannot answer - no memory of earlier statements"
            },
            "multi_topic_demo": {
                "name": "Multi-Topic Navigation",
                "description": "Jump between different topics",
                "messages": [
                    "What's the vacation policy?",
                    "Now tell me about remote work",
                    "Back to vacation - can I carry days over?",
                    "And for remote work - how many office days?"
                ],
                "expected_with_memory": "Seamlessly handles topic switches, remembers context",
                "expected_without_memory": "Confused by topic switches"
            }
        }

    @staticmethod
    def get_scenario_names() -> List[str]:
        """Get list of scenario names for selection."""
        scenarios = DemoScenarios.get_all_scenarios()
        return [f"{key}: {info['name']}" for key, info in scenarios.items()]

    @staticmethod
    def get_scenario_by_key(key: str) -> Dict:
        """Get specific scenario by key."""
        scenarios = DemoScenarios.get_all_scenarios()
        return scenarios.get(key, None)

    @staticmethod
    def get_quick_questions() -> List[str]:
        """Get quick example questions."""
        return [
            "How many vacation days do I get?",
            "Can I work remotely?",
            "What's the parental leave policy?",
            "What can I expense for meals?",
            "Tell me about the holidays",
            "What equipment does the company provide for remote work?",
            "How do I request time off?",
            "What's the sick leave policy?"
        ]
