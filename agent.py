"""
Agriculture Agent Module
Implements LangGraph-based intelligent routing and RAG orchestration
"""

import os
from typing import Dict, List, Literal
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """State object for agent workflow"""
    question: str
    intent: str
    disease_context: str
    scheme_context: str
    answer: str
    sources: List[Dict]

class AgricultureAgent:
    """
    Intelligent agent that:
    1. Detects farmer intent (Disease/Scheme/Hybrid)
    2. Routes queries to appropriate knowledge base(s)
    3. Retrieves relevant context
    4. Generates farmer-friendly responses
    """
    
    def __init__(self, disease_vectorstore, scheme_vectorstore):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.disease_vectorstore = disease_vectorstore
        self.scheme_vectorstore = scheme_vectorstore
        
        # Create retrievers
        self.disease_retriever = disease_vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )
        self.scheme_retriever = scheme_vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph state machine for query routing"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("detect_intent", self._detect_intent_node)
        workflow.add_node("retrieve_disease", self._retrieve_disease_node)
        workflow.add_node("retrieve_scheme", self._retrieve_scheme_node)
        workflow.add_node("retrieve_hybrid", self._retrieve_hybrid_node)
        workflow.add_node("generate_answer", self._generate_answer_node)
        
        # Set entry point
        workflow.set_entry_point("detect_intent")
        
        # Add conditional routing based on intent
        workflow.add_conditional_edges(
            "detect_intent",
            self._route_by_intent,
            {
                "disease": "retrieve_disease",
                "scheme": "retrieve_scheme",
                "hybrid": "retrieve_hybrid"
            }
        )
        
        # Connect retrieval nodes to answer generation
        workflow.add_edge("retrieve_disease", "generate_answer")
        workflow.add_edge("retrieve_scheme", "generate_answer")
        workflow.add_edge("retrieve_hybrid", "generate_answer")
        
        # End after answer generation
        workflow.add_edge("generate_answer", END)
        
        return workflow.compile()
    
    def _detect_intent_node(self, state: AgentState) -> AgentState:
        """Node: Detect farmer's intent"""
        intent = self.detect_intent(state["question"])
        state["intent"] = intent
        return state
    
    def _route_by_intent(self, state: AgentState) -> Literal["disease", "scheme", "hybrid"]:
        """Router: Direct to appropriate retrieval node"""
        return state["intent"]
    
    def _retrieve_disease_node(self, state: AgentState) -> AgentState:
        """Node: Retrieve from Disease KB"""
        docs = self.disease_retriever.get_relevant_documents(state["question"])
        state["disease_context"] = self._format_context(docs)
        state["scheme_context"] = ""
        state["sources"] = [{"source": doc.metadata.get("source_file"), "page": doc.metadata.get("page")} 
                           for doc in docs]
        return state
    
    def _retrieve_scheme_node(self, state: AgentState) -> AgentState:
        """Node: Retrieve from Scheme KB"""
        docs = self.scheme_retriever.get_relevant_documents(state["question"])
        state["scheme_context"] = self._format_context(docs)
        state["disease_context"] = ""
        state["sources"] = [{"source": doc.metadata.get("source_file"), "page": doc.metadata.get("page")} 
                           for doc in docs]
        return state
    
    def _retrieve_hybrid_node(self, state: AgentState) -> AgentState:
        """Node: Retrieve from BOTH KBs"""
        disease_docs = self.disease_retriever.get_relevant_documents(state["question"])
        scheme_docs = self.scheme_retriever.get_relevant_documents(state["question"])
        
        state["disease_context"] = self._format_context(disease_docs)
        state["scheme_context"] = self._format_context(scheme_docs)
        
        sources = []
        for doc in disease_docs + scheme_docs:
            sources.append({
                "source": doc.metadata.get("source_file"),
                "page": doc.metadata.get("page")
            })
        state["sources"] = sources
        
        return state
    
    def _generate_answer_node(self, state: AgentState) -> AgentState:
        """Node: Generate final answer using LLM"""
        answer = self._generate_response(
            question=state["question"],
            intent=state["intent"],
            disease_context=state.get("disease_context", ""),
            scheme_context=state.get("scheme_context", "")
        )
        state["answer"] = answer
        return state
    
    def _format_context(self, docs: List) -> str:
        """Format retrieved documents into context string"""
        return "\n\n".join([doc.page_content for doc in docs])
    
    def detect_intent(self, question: str) -> str:
        """
        Classify farmer's query into one of three intents:
        - disease: Questions about pests, diseases, symptoms, treatment
        - scheme: Questions about subsidies, eligibility, application process
        - hybrid: Questions combining both (e.g., schemes for disease management)
        """
        
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at understanding farmer queries in India.
            
Classify the farmer's question into ONE of these intents:

**disease** - Questions about:
- Disease symptoms and identification
- Pest problems and infestations  
- Treatment and prevention methods
- Nutritional deficiencies
- Plant health issues
- Citrus diseases like canker, greening, foot rot, etc.

**scheme** - Questions about:
- Government subsidies and financial assistance
- Agricultural support programs
- Eligibility criteria for schemes
- Application processes
- Available benefits for farmers
- Schemes like MIDH, PMKSY, PM-KISAN, etc.

**hybrid** - Questions about:
- Financial support FOR disease management
- Schemes that help WITH specific pest control
- Government assistance COMBINED with agricultural problems
- Any query connecting schemes with diseases/pests

Respond with ONLY ONE WORD: disease, scheme, or hybrid"""),
            ("human", "{question}")
        ])
        
        chain = intent_prompt | self.llm | StrOutputParser()
        intent = chain.invoke({"question": question}).strip().lower()
        
        # Validate intent
        if intent not in ["disease", "scheme", "hybrid"]:
            intent = "disease"  # Default fallback
        
        return intent
    
    def _generate_response(self, question: str, intent: str, 
                          disease_context: str, scheme_context: str) -> str:
        """Generate farmer-friendly response using retrieved context"""
        
        if intent == "disease":
            context = disease_context
            prompt_template = """You are an expert agricultural advisor helping farmers in India.

Based on the following information about citrus diseases and pests, provide a clear, actionable answer to the farmer's question.

CONTEXT FROM DISEASE KNOWLEDGE BASE:
{context}

FARMER'S QUESTION: {question}

Provide a comprehensive answer that includes:
1. Clear identification of the problem (if applicable)
2. Symptoms to look for
3. Management strategies (cultural, organic, and chemical options)
4. Preventive measures
5. When to seek expert help

Use simple language suitable for farmers. Be specific with dosages and timing when mentioning treatments.

ANSWER:"""
        
        elif intent == "scheme":
            context = scheme_context
            prompt_template = """You are an expert agricultural advisor helping farmers in India understand government schemes.

Based on the following information about government agricultural schemes, provide a clear, helpful answer to the farmer's question.

CONTEXT FROM SCHEME KNOWLEDGE BASE:
{context}

FARMER'S QUESTION: {question}

Provide a comprehensive answer that includes:
1. Relevant scheme names and purposes
2. Eligibility criteria
3. Subsidy amounts or benefits
4. Application process
5. Required documents
6. Contact information if available

Use simple language suitable for farmers. Be specific with amounts, percentages, and procedures.

ANSWER:"""
        
        else:  # hybrid
            context = f"DISEASE INFORMATION:\n{disease_context}\n\nSCHEME INFORMATION:\n{scheme_context}"
            prompt_template = """You are an expert agricultural advisor helping farmers in India.

The farmer has a question that involves BOTH disease management AND government schemes.

CONTEXT:
{context}

FARMER'S QUESTION: {question}

Provide a comprehensive answer with two clear sections:

**DISEASE MANAGEMENT:**
- Problem identification and symptoms
- Treatment and prevention strategies
- Management recommendations

**GOVERNMENT SUPPORT:**
- Relevant schemes that can help
- Financial assistance available
- Application process and eligibility

Use simple language suitable for farmers. Be specific and actionable.

ANSWER:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        
        answer = chain.invoke({
            "question": question,
            "context": context
        })
        
        return answer
    
    def process_query(self, question: str) -> Dict:
        """
        Main entry point: Process farmer's query through the workflow
        
        Returns:
            Dict with intent, answer, and sources
        """
        
        # Initialize state
        initial_state = {
            "question": question,
            "intent": "",
            "disease_context": "",
            "scheme_context": "",
            "answer": "",
            "sources": []
        }
        
        # Run through workflow
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "intent": final_state["intent"],
            "answer": final_state["answer"],
            "sources": final_state.get("sources", [])
        }

if __name__ == "__main__":
    print("Agent module loaded successfully!")
