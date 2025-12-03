import random
import re
import json
import unicodedata
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ZWSP = "\u200b"  # zero-width space (separador invisível)

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

# -----------------------------
# Funções auxiliares
# -----------------------------

def remove_accents(ch: str) -> str:
    """Remove acentos de um caractere (ex.: 'é' -> 'e', 'ã' -> 'a')."""
    # Normaliza em NFD e remove caracteres de marcação (Mn = Mark, Nonspacing)
    normalized = unicodedata.normalize("NFD", ch)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")

def encode_text(text: str) -> str:
    """
    Gera UMA sequência de emojis para o texto (case-insensitive).

    Antes de mapear, remove acentos das letras:
    ex.: 'coé galera' -> 'coe galera' -> emojis.
    As “unidades” (emojis, espaços, pontuação) são separadas por um
    zero-width space (ZWSP), que não aparece visualmente, mas
    permite decodificar depois.
    """
    tokens = []
    for ch in text:
        if ch.isalpha():
            # remove acento (é -> e, ã -> a, ç -> c, etc.)
            base = remove_accents(ch)
            # pode acontecer de virar mais de um char (tipo ß -> ss); pego o primeiro
            base_letter = base[0] if base else ch
            letter = base_letter.upper()

            if letter in LETTER_TO_EMOJIS:
                tokens.append(random.choice(LETTER_TO_EMOJIS[letter]))
            else:
                # se não tiver mapeamento, mantém o caractere original
                tokens.append(ch)
        else:
            # mantém espaços, pontuação, quebras de linha etc. como tokens próprios
            tokens.append(ch)

    # junta com separador invisível (sem espaços visíveis entre emojis)
    return ZWSP.join(tokens)


def decode_emojis(emoji_string: str) -> str:
    """
    Decodifica uma sequência de emojis gerada pela função encode_text.

    Primeiro tenta separar pelo ZWSP; se por algum motivo não houver,
    cai num fallback que separa por espaços (para textos “manuais”).
    """
    if not emoji_string:
        return ""

    if ZWSP in emoji_string:
        parts = emoji_string.split(ZWSP)
    else:
        # fallback: separa por espaços, preservando blocos de espaço
        parts = re.split(r"(\s+)", emoji_string)

    decoded = []
    for part in parts:
        if part == "":
            continue
        if part.isspace():
            # preserva espaços/linhas exatamente como estão
            decoded.append(part)
        else:
            decoded.append(EMOJI_TO_LETTER.get(part, part))
    return "".join(decoded)


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