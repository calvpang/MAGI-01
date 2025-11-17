"""
Streamlit Web Interface for MAGI System
A multi-agent AI council with streaming responses
"""

import streamlit as st
from datetime import datetime
import time

from agents.magi_system import MagiSystem
from config import LLM_PROVIDER, LM_STUDIO_MODEL, GEMINI_MODEL


# Page configuration
st.set_page_config(
    page_title="MAGI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .agent-response {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .agent-name {
        font-size: 20px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .deliberation-section {
        background-color: #e8f4f8;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border-left: 5px solid #1f77b4;
    }
    .final-answer {
        background-color: #d4edda;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'magi_system' not in st.session_state:
        st.session_state.magi_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False


def initialize_magi_system():
    """Initialize the MAGI System"""
    with st.spinner("Initializing MAGI System..."):
        try:
            st.session_state.magi_system = MagiSystem()
            st.session_state.initialized = True
            return True
        except Exception as e:
            st.error(f"Failed to initialize MAGI System: {str(e)}")
            return False


def stream_text(text, container, delay=0.01):
    """Stream text character by character to a container"""
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(displayed_text)
        time.sleep(delay)
    return displayed_text


def display_agent_response(agent_name, response_text, stream=True):
    """Display an agent's response with optional streaming"""
    st.markdown(f'<div class="agent-name">🤖 {agent_name}</div>', unsafe_allow_html=True)
    
    if stream:
        response_container = st.empty()
        stream_text(response_text, response_container, delay=0.005)
    else:
        st.markdown(response_text)


def display_deliberation(evaluation):
    """Display the deliberation results"""
    st.markdown('<div class="deliberation-section">', unsafe_allow_html=True)
    st.markdown("### ⚖️ MAGI DELIBERATION")
    
    if evaluation.get("evaluations"):
        st.markdown("#### Individual Scores:")
        
        cols = st.columns(len(evaluation["evaluations"]))
        for idx, eval_item in enumerate(evaluation["evaluations"]):
            with cols[idx]:
                score = eval_item.get("score", "N/A")
                agent = eval_item.get("agent", "Unknown")
                reasoning = eval_item.get("reasoning", "No reasoning provided")
                
                st.metric(
                    label=agent,
                    value=f"{score}/10"
                )
                with st.expander("View reasoning"):
                    st.write(reasoning)
    
    if evaluation.get("synthesis"):
        st.markdown("#### Synthesis:")
        st.info(evaluation["synthesis"])
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_final_answer(final_answer, stream=True):
    """Display the final synthesized answer"""
    st.markdown('<div class="final-answer">', unsafe_allow_html=True)
    st.markdown("### ✅ FINAL SYNTHESIZED ANSWER")
    
    if stream:
        answer_container = st.empty()
        stream_text(final_answer, answer_container, delay=0.005)
    else:
        st.markdown(final_answer)
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ MAGI System Settings")
        
        # System info
        st.markdown("### System Information")
        provider = LLM_PROVIDER
        model = LM_STUDIO_MODEL if provider.lower() != "gemini" else GEMINI_MODEL
        st.info(f"**Provider:** {provider}\n\n**Model:** {model}")
        
        if st.session_state.initialized:
            st.success("✓ System Initialized")
            session_id = st.session_state.magi_system.session_id
            st.text(f"Session: {session_id[:8]}...")
            
            agent_names = [agent.name for agent in st.session_state.magi_system.agents]
            st.markdown("**Active Agents:**")
            for name in agent_names:
                st.markdown(f"- {name}")
        else:
            st.warning("⚠️ System Not Initialized")
        
        st.markdown("---")
        
        # Controls
        st.markdown("### Controls")
        
        if not st.session_state.initialized:
            if st.button("🚀 Initialize System", use_container_width=True):
                initialize_magi_system()
                st.rerun()
        
        if st.session_state.initialized:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("🔄 Clear Agent Memory", use_container_width=True):
                st.session_state.magi_system.clear_all_memory()
                st.success("Agent memory cleared!")
            
            if st.button("♻️ Restart System", use_container_width=True):
                st.session_state.magi_system = None
                st.session_state.initialized = False
                st.session_state.chat_history = []
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Streaming Options")
        stream_responses = st.checkbox("Stream Agent Responses", value=True)
        stream_final = st.checkbox("Stream Final Answer", value=True)
        
        st.session_state.stream_responses = stream_responses
        st.session_state.stream_final = stream_final
    
    # Main content
    st.title("🤖 MAGI System")
    st.markdown("### Multi-Agent Intelligence Council")
    st.markdown("Ask complex questions and receive analyzed responses from multiple AI personalities.")
    
    # Initialize system if not done
    if not st.session_state.initialized:
        st.info("👈 Click 'Initialize System' in the sidebar to begin.")
        if st.button("Initialize Now", type="primary"):
            if initialize_magi_system():
                st.rerun()
        return
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("## 💬 Conversation History")
        
        for idx, item in enumerate(st.session_state.chat_history):
            with st.expander(f"Query {idx + 1}: {item['question'][:60]}...", expanded=(idx == len(st.session_state.chat_history) - 1)):
                st.markdown(f"**📝 Question:** {item['question']}")
                st.markdown(f"**🕒 Time:** {item['timestamp']}")
                
                st.markdown("---")
                st.markdown("#### Agent Responses:")
                
                for response in item['agent_responses']:
                    if response['success']:
                        with st.container():
                            st.markdown(f'<div class="agent-response">', unsafe_allow_html=True)
                            display_agent_response(response['agent'], response['response'], stream=False)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"**{response['agent']}:** {response['response']}")
                
                st.markdown("---")
                display_deliberation(item['evaluation'])
                
                st.markdown("---")
                display_final_answer(item['final_answer'], stream=False)
    
    # Query input section
    st.markdown("---")
    st.markdown("## 🎯 New Query")
    
    # Use a form for better UX
    with st.form(key="query_form", clear_on_submit=True):
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the most important considerations when developing AI systems?",
            height=100,
            help="Ask a complex question that benefits from multiple perspectives"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 Submit Query", type="primary", use_container_width=True)
        with col2:
            debug_mode = st.checkbox("Debug Mode", value=False)
    
    # Process query
    if submit_button and query:
        st.markdown("---")
        st.markdown("## 🔄 Processing Query...")
        
        # Display the question
        st.markdown(f"**Question:** {query}")
        st.markdown("---")
        
        try:
            # Query each agent with streaming
            st.markdown("### 🤖 Agent Responses")
            
            responses = []
            for agent in st.session_state.magi_system.agents:
                with st.container():
                    st.markdown(f'<div class="agent-response">', unsafe_allow_html=True)
                    
                    status_container = st.empty()
                    status_container.info(f"⏳ {agent.name} is analyzing...")
                    
                    # Get response with optional debug mode
                    response = agent.respond(query, debug=debug_mode)
                    responses.append(response)
                    
                    status_container.empty()
                    
                    if response['success']:
                        display_agent_response(
                            response['agent'], 
                            response['response'],
                            stream=st.session_state.get('stream_responses', True)
                        )
                    else:
                        st.error(f"**{response['agent']}:** {response['response']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Deliberation
            st.markdown("---")
            with st.spinner("⚖️ Deliberating..."):
                result = st.session_state.magi_system.deliberator.process_magi_decision(query, responses)
            
            display_deliberation(result['evaluation'])
            
            # Final answer
            st.markdown("---")
            display_final_answer(result['final_answer'], stream=st.session_state.get('stream_final', True))
            
            # Save to history
            chat_entry = {
                'question': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'agent_responses': responses,
                'evaluation': result['evaluation'],
                'final_answer': result['final_answer']
            }
            st.session_state.chat_history.append(chat_entry)
            
            st.success("✅ Query completed successfully!")
            
            # Scroll to top button
            if st.button("⬆️ Back to Top"):
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error processing query: {str(e)}")
            if debug_mode:
                st.exception(e)


if __name__ == "__main__":
    main()
