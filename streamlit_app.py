import random
import re
import json
import unicodedata
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Carregar mapeamentos do TXT
# -----------------------------
@st.cache_data
def load_mappings(path: str = "emoji_mapping.txt"):
    """
    Lê o arquivo emoji_mapping.txt no formato:
    A,emoji1,emoji2,...
    ...
    Z,emoji1,emoji2,...

    Retorna:
        LETTER_TO_EMOJIS (dict[str, list[str]])
        EMOJI_TO_LETTER (dict[str, str])
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de mapeamento não encontrado: {file_path.resolve()}"
        )

    letter_to_emojis = {}
    emoji_to_letter = {}

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            letter = parts[0].strip().upper()
            emojis = [p for p in parts[1:] if p]

            if not letter.isalpha() or len(letter) != 1:
                continue

            letter_to_emojis[letter] = emojis
            for e in emojis:
                emoji_to_letter[e] = letter

    return letter_to_emojis, emoji_to_letter


LETTER_TO_EMOJIS, EMOJI_TO_LETTER = load_mappings("emoji_mapping.txt")
# lista de emojis ordenada por tamanho (nº de codepoints) decrescente,
# para conseguir casar primeiro os emojis "compridos" (com ZWJ etc.)
EMOJI_LIST_SORTED = sorted(EMOJI_TO_LETTER.keys(), key=len, reverse=True)

# -----------------------------
# Funções auxiliares
# -----------------------------

def remove_accents(ch: str) -> str:
    """Remove acentos de um caractere (ex.: 'é' -> 'e', 'ã' -> 'a')."""
    normalized = unicodedata.normalize("NFD", ch)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def encode_text(text: str) -> str:
    """
    Gera UMA sequência de emojis para o texto (case-insensitive).

    - Remove acentos antes de mapear (ex.: 'é' -> 'e').
    - Letras viram emojis.
    - Outros caracteres são mantidos.
    - Um espaço simples ' ' entre palavras vira DOIS espaços na saída.
    """
    tokens = []
    for ch in text:
        if ch.isalpha():
            base = remove_accents(ch)
            base_letter = base[0] if base else ch
            letter = base_letter.upper()

            if letter in LETTER_TO_EMOJIS:
                tokens.append(random.choice(LETTER_TO_EMOJIS[letter]))
            else:
                tokens.append(ch)
        elif ch == " ":
            # espaço simples vira dois espaços na saída
            tokens.append("  ")
        else:
            # mantém pontuação, quebras de linha etc.
            tokens.append(ch)

    return "".join(tokens)


def decode_emojis(emoji_string: str) -> str:
    """
    Decodifica uma sequência de emojis gerada pela função encode_text.

    - Conjuntos de espaços (um ou mais) viram UM espaço na saída.
    - Emojis são identificados tentando casar os mais longos primeiro.
    - Qualquer coisa que não seja reconhecida como emoji é copiada tal qual.
    """
    if not emoji_string:
        return ""

    s = emoji_string
    decoded_chars = []
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]

        # Bloco de espaços / quebras de linha
        if ch.isspace():
            # consome todos os caracteres de espaço consecutivos
            while i < n and s[i].isspace():
                i += 1
            # representa como um único espaço no texto decodificado
            decoded_chars.append(" ")
            continue

        # Tenta casar um emoji começando em i, pegando primeiro os maiores
        matched = False
        for emoji in EMOJI_LIST_SORTED:
            if s.startswith(emoji, i):
                decoded_chars.append(EMOJI_TO_LETTER[emoji])
                i += len(emoji)
                matched = True
                break

        if not matched:
            # não é emoji conhecido: copia caractere literal
            decoded_chars.append(ch)
            i += 1

    return "".join(decoded_chars)


def copy_button(text: str, label: str = "Copiar para área de transferência"):
    """Cria um botão simples de copiar para o clipboard via JS."""
    if not text:
        return
    js_text = json.dumps(text)
    html = f"""
    <button onclick='navigator.clipboard.writeText({js_text})'>
        {label}
    </button>
    """
    components.html(html, height=40)

# -----------------------------
# App Streamlit
# -----------------------------
st.set_page_config(
    page_title="Emoji Cipher",
    page_icon="🔐",
    layout="centered",
)

st.title("🔤 ➜ 😊 Emoji Cipher")
st.caption("Digite texto e brinque de codificar/decodificar com o alfabeto de emojis.")

tab_encode, tab_decode = st.tabs(
    ["Codificar (texto ➜ emojis)", "Decodificar (emojis ➜ texto)"]
)

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
        placeholder="Ex.: Oi gente!!!",
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
        placeholder="Ex.: (cole aqui o resultado copiado da outra aba)",
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