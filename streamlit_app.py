import random
import re
import json
import streamlit as st
import streamlit.components.v1 as components

MAPPING_FILE = "emoji_mapping.txt"  # nome do TXT com o alfabeto

# -----------------------------
# Carregar mapeamento do TXT
# -----------------------------
def load_mapping_from_txt(path: str):
    """
    Lê um arquivo com linhas no formato:
    A[emoji1][emoji2]...[emojiN]
    (também tolera coisas como 'A - [emoji1][emoji2]...')
    e retorna dict { 'A': [emoji1, emoji2, ...], ... }.
    """
    mapping = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # primeira letra da linha é a chave (A-Z)
            m = re.match(r"^([A-Za-z])(.*)$", line)
            if not m:
                continue
            letter = m.group(1).upper()
            rest = m.group(2)

            # pega tudo que estiver entre colchetes [ ... ]
            emojis = re.findall(r"\[(.*?)\]", rest)
            if emojis:
                mapping[letter] = emojis

    return mapping


# -----------------------------
# App Streamlit - config
# -----------------------------
st.set_page_config(
    page_title="Emoji Cipher",
    page_icon="🔐",
    layout="centered",
)

st.title("🔤 ➜ 😊 Emoji Cipher")
st.caption("Digite texto e brinque de codificar/decodificar com o alfabeto de emojis.")

# tenta carregar o arquivo de mapeamento
try:
    LETTER_TO_EMOJIS = load_mapping_from_txt(MAPPING_FILE)
except FileNotFoundError:
    LETTER_TO_EMOJIS = {}

if not LETTER_TO_EMOJIS:
    st.error(
        f"Arquivo de mapeamento não encontrado ou vazio.\n"
        f"Verifique se '{MAPPING_FILE}' existe e está no formato correto."
    )
    st.stop()

# mapeamento inverso emoji -> letra
EMOJI_TO_LETTER = {
    emoji: letter
    for letter, emojis in LETTER_TO_EMOJIS.items()
    for emoji in emojis
}

# -----------------------------
# Funções auxiliares
# -----------------------------
def encode_text(text: str) -> str:
    """Gera UMA sequência de emojis para o texto (case-insensitive)."""
    tokens = []
    for ch in text:
        if ch.isalpha():
            letter = ch.upper()
            if letter in LETTER_TO_EMOJIS:
                tokens.append(random.choice(LETTER_TO_EMOJIS[letter]))
            else:
                tokens.append(ch)
        else:
            # mantém espaços, pontuação, quebras de linha etc.
            tokens.append(ch)
    # espaço entre tokens para facilitar ler/copiar
    return " ".join(tokens)


def decode_emojis(emoji_string: str) -> str:
    """Decodifica uma sequência de emojis gerada pela função encode_text."""
    if not emoji_string:
        return ""
    # separa preservando blocos de espaço
    parts = re.split(r"(\s+)", emoji_string)
    decoded = []
    for part in parts:
        if part == "":
            continue
        if part.isspace():
            decoded.append(" ")
        else:
            decoded.append(EMOJI_TO_LETTER.get(part, part))
    return "".join(decoded)


def copy_button(text: str, label: str = "Copiar para área de transferência"):
    """Cria um botão simples de copiar para o clipboard via JS."""
    if not text:
        return
    js_text = json.dumps(text)  # escapa bonitinho pra JS
    html = f"""
    <button onclick='navigator.clipboard.writeText({js_text})'>
        {label}
    </button>
    """
    components.html(html, height=40)


# -----------------------------
# Layout principal
# -----------------------------
tab_encode, tab_decode = st.tabs(
    ["Codificar (texto ➜ emojis)", "Decodificar (emojis ➜ texto)"]
)

# Estado pra guardar o último resultado encodado
if "encoded_text" not in st.session_state:
    st.session_state["encoded_text"] = ""

# -----------------------------
# Aba de codificação
# -----------------------------
with tab_encode:
    st.subheader("Codificar texto em emojis")

    text = st.text_area(
        "Digite o texto para codificar (case-insensitive):",
        height=150,
        placeholder="Ex.: Hello World",
    )

    if st.button("Gerar sequência de emojis", type="primary"):
        if not text.strip():
            st.warning("Digite algum texto antes de codificar.")
        else:
            st.session_state["encoded_text"] = encode_text(text)

    if st.session_state["encoded_text"]:
        st.markdown("#### Resultado")
        st.code(st.session_state["encoded_text"], language="text")
        copy_button(st.session_state["encoded_text"], "Copiar resultado")
        st.info(
            "Se quiser **outra sequência aleatória** para o mesmo texto, "
            "é só clicar de novo em “Gerar sequência de emojis”."
        )

# -----------------------------
# Aba de decodificação
# -----------------------------
with tab_decode:
    st.subheader("Decodificar emojis em texto")

    emoji_input = st.text_area(
        "Cole aqui a sequência de emojis (como gerada na aba anterior):",
        height=150,
        placeholder="Ex.: 🙉 📧 💺 🦕 🇯🇵 ,   🤙 🐋 🌊 🎪 🧩 !",
    )

    decoded_text = ""
    if st.button("Decodificar", type="primary"):
        if not emoji_input.strip():
            st.warning("Cole uma sequência de emojis para decodificar.")
        else:
            decoded_text = decode_emojis(emoji_input)

    if decoded_text:
        st.markdown("#### Texto decodificado")
        st.code(decoded_text, language="text")
        copy_button(decoded_text, "Copiar texto decodificado")
