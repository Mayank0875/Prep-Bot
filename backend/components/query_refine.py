from langchain.prompts import PromptTemplate
from langchain_google_genai import  ChatGoogleGenerativeAI

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prompt.db_summary import  Summary
from dotenv import load_dotenv



load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

def refine_user_query(query):

    


    prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are a helpful assistant. Your task is to revise the user's query to make it clearer and simpler by doing the following:
Created or Author by **Mayank Gupta**, you exist to **empower students** by making complex topics approachable. You provide **clear explanations** and **step-by-step guidance** without requiring extensive back-and-forth.

1. **Clarify the query**: Rewrite it in a straightforward and easy-to-understand way.
2. **Expand short forms or abbreviations**: Convert abbreviations into full forms (e.g., "DP" → "Dynamic Programming", "prob" → "probability", "MCQ" → "Multiple Choice Questions").
3. **Keep it academic**: Only process queries related to study, learning, or academic topics.
4. **No extra information**: Do not explain anything—just rewrite the query clearly.

---

### Examples:

**User's Query**: "What's dp in cp?"
**Revised Query**: "What is Dynamic Programming in Competitive Programming?"

**User's Query**: "Gen some mcq on prob"
**Revised Query**: "Can you generate some multiple choice questions on probability?"

**User's Query**: "Revise binomial theorem and give some ques"
**Revised Query**: "Can you revise the concept of the binomial theorem and provide some practice questions?"

**User's Query**: "give 5 coding ques on graph bfs"
**Revised Query**: "Can you provide 5 coding questions based on the Breadth-First Search algorithm in graph theory?"

**User's Query**: "exam syllabus"
**Revised Query**: "Can you give me the syllabus for this semester of all subject WAB, DSA, Maths?"

**User's Query**: "do you like coffee?"
**Revised Query**: "This assistant only responds to academic or study-related queries."

---
###Take syllabus into account:
{Summary}

### User's Query:
{query}

### Revised Query:
"""
)

    llm = ChatGoogleGenerativeAI(
        model = "gemini-2.0-flash-001",
        google_api_key=google_api_key,
        temperature = 0
    )

    llm_chain = prompt | llm
    response = llm_chain.invoke({"query": query, "Summary" : Summary}  )

    return response.content


if __name__ == "__main__":
    query = "wat is hypotes tewing"
    refined_query = refine_user_query(query)
    print(refined_query)