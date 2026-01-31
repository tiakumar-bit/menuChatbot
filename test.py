import streamlit as st
import requests
import pdfplumber
import os
import requests
from bs4 import BeautifulSoup
import base64

# -------------------------
# CONFIG
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="Fusion F&B Menu Assistant",
    page_icon="🍽️"
)

# styling
st.markdown("""
<style>

.logo-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 0px;
}


.centered {
    text-align: center;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #DE8900, #C20202);
    color: black;
}

/* Title */
h1, h2, h3 {
    color: black;
    font-weight: 700;
}

/* Paragraphs */
p {
    color: white;
}

/* Buttons */
button {
    background: #000000 !important;
    color: white !important;
    border-radius: 12px;
    padding: 10px 24px;
    border: none;
    font-size: 16px;
    transition: all 0.2s ease;
}

/* Button hover */
button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
}


#cap {
    color: black;
    font-size: 20px;
}

/* Chat bubbles */
.stChatMessage {
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    font-size: 16px;
    line-height: 1.4;
}

/* Assistant message */
div[data-testid="chat-message-assistant"]  {
    background: black;
    border: 1px solid rgba(255,255,255,0.1);
    margin-right: auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* User message */
div[data-testid="chat-message-user"] {
    border: 1px solid rgba(99,102,241,0.3);
    margin-left: 100px;
    background: white;
    margin-right: 0;
    text-align: right;
    box-shadow: 0 4px 10px rgba(220,38,38,0.25);
}

div[data-testid="stImage"] {
    margin-top: -170px;
    display: flex;
    justify-content: center;
}


</style>
""", unsafe_allow_html=True)


def load_google_doc(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(separator="\n")


DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vQ0Q0QceG5t-qs8BuhXZrK_tRz4iCu11nzF70NwjGr6_Na6Zu2lEotsM-vxKEyUFBqZwBbpOOjc4IkP/pub"
doc_text = load_google_doc(DOC_URL)


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


img_base64 = img_to_base64("FusionLogo.png")

st.markdown(
    f"""
    <div class="logo-wrapper">
        <img src="data:image/png;base64,{img_base64}" width="110">
    </div>
    """,
    unsafe_allow_html=True
)

# choose language before starting

if "language" not in st.session_state:
    st.session_state.language = None

if st.session_state.language is None:
    st.markdown(
        "<h3 class='centered'>Choose your language to start!<br>Wählen Sie Ihre Sprache, um zu beginnen!</h3>",
        unsafe_allow_html=True
    )

    # One centered column
    _, center_col, _ = st.columns([1, 1, 1])

    with center_col:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = "English"
            st.rerun()

        if st.button("🇩🇪 Deutsch", use_container_width=True):
            st.session_state.language = "German"
            st.rerun()

    st.stop()


# -------------------------
# LOAD MENU FROM PDF
# -------------------------
def load_menu():
    text = ""
    with pdfplumber.open("FusionMenu.pdf") as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )


menu_text = load_menu()

# -------------------------
# SYSTEM PROMPT
# -------------------------
SYSTEM_PROMPT = (
    f"You are a helpful AI assistant for the restaurant Fusion F&B. "
    f"The menu is: {menu_text}. Help the user based on their input—"
    f"you can e.g. recommend dishes from the menu or"
    f"compare items, or answer any other menu-related questions. You are talking directly to the customer."
    f"They are not ordering directly from you. When you give names of dishes, make sure u include the number of the"
    f"dish. Do NOT invent items. You MUST respond in {st.session_state.language}. "
    f"Additionally, for extra info, before replying, ALWAYS look at these notes first: {doc_text}"
    f"But don't just randomly throw that info everywhere, apply it ONLY when applicable. And using that info from the doc"
    f"doesn't mean you're using ONLY that info - say what you were already going to say, and adjust it according to the doc."
    f"By this, I mean, if the user asks a question, and the answer is on that doc - don't constrain the answer to ONLY what"
    f"was written on that doc, but make sure to add it."
)


# -------------------------
# OPENAI CALL
# -------------------------
def call_openai(messages):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


# -------------------------
# STREAMLIT UI
# -------------------------

if st.session_state.language == "English":
    st.markdown(
        "<h1 class='centered'>️   Fusion F&B Menu Assistant</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='centered'>Ask me anything about our menu!</p>",
        unsafe_allow_html=True
    )
elif st.session_state.language == "German":
    st.markdown(
        "<h1 class='centered'>    Fusion F&B Menüassistent</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='centered'>Gerne beantworte ich Ihre Fragen zu unserer Speisekarte</p>",
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Display chat history (skip system message)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about the menu...")

if user_input:
    # Add user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call OpenAI
    with st.chat_message("assistant", avatar="FusionLogo.png"):
        if st.session_state.language == "English":
            with st.spinner("Typing…"):
                assistant_reply = call_openai(st.session_state.messages)
                st.markdown(assistant_reply)
        elif st.session_state.language == "German":
            with st.spinner("Schreibt…"):
                assistant_reply = call_openai(st.session_state.messages)
                st.markdown(assistant_reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )






