import random
import re
import json

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Mapeamento letra -> lista de emojis
# -----------------------------
LETTER_TO_EMOJIS = {
    "A": ["🙏","🙈","🌲","🎫","🎪","⛺️","🪤","🪜","🖇️","🅰️"],
    "B": ["😘","😚","😙","😗","😽","🅱️","🇳🇵","3️⃣"],
    "C": ["🌜","🌗","🌘","🌊","🍋‍🟩","🥐","🇲🇻"],
    "D": ["🌓","🌔","🍺","🪉","🥠"],
    "E": ["🌿","🥞","🎙️","💶","💷","🛡️","🚪","🪟","📧","🗄️","📚","🇦🇲"],
    "F": ["🍜","🎏"],
    "G": ["👩🏻‍🦽‍➡️","🧑‍🦽‍➡️","👨‍🦽‍➡️","🪢","🐳","🎬","🪝","📽️","☪️"],
    "H": ["😭","🫁","🧌","💆‍♀️","💆","💆‍♂️","👯‍♀️","👯","👯‍♂️","🐰","🙉","🚧","🏨","🏩","♓️"],
    "I": ["🤫","🖕🏿","🕴️","🧍‍♀️","🧍","🧍‍♂️","📍","ℹ️","🕕","🕧","🕡"],
    "J": ["🫸","👆","🥷","🧏‍♂️","🧏","🧏‍♀️","🤳","👩‍🦽","🧑‍🦽","👨‍🦽","🧦","🌶️","🃏","🕗","🕚"],
    "K": ["🕺","🏃‍♀️‍➡️","🏃‍➡️","🏃‍♂️‍➡️","🦇","🐦‍🔥","🌬️","🔏"],
    "L": ["🤔","🫷","💪","🦾","🤙","🙋‍♀️","🙋","🙋‍♂️","👢","🪿","🦕","🦭","💺","🚬","🕒"],
    "M": ["😂","😖","🫣","😹","🦷","🧝‍♀️","🧝‍♂️","👫","👭","👬","🐫","♏️","♍️","♒️","〽️","Ⓜ️"],
    "N": ["👡","🎭","📈","♑️","🎶"],
    "O": ["👁️","🙆‍♀️","🙆","🙆‍♂️","🌕","🌑","🍩","🚇","💿","🅾️","⭕️","⏺️","🔘","🇯🇵"],
    "P": ["😮","👎","📫","📬","🅿️","🚩"],
    "Q": ["😋","🤥","🤤","🫠","😪","🧐","💥","🍳","🥘","🍭","📿","⚗️","🔍","👁️‍🗨️","🎐","🎈"],
    "R": ["🤑","💇‍♀️","💃","🪡","🐕‍🦺","🎋","💸","🎞️","🛝"],
    "S": ["🧞","🧞‍♂️","🧞‍♀️","🪱","🦎","🍃","⚡️","🌩️","🧩","🏦","💵","💰","💞"],
    "T": ["⛑️","👘","🦩","🌴","🌱","🍄","🍄‍🟫","☂️","🚡","⛱️","🏣","🏥","🎚️","🪧","✝️","🀄️","🇨🇭","➕"],
    "U": ["👅","👥","🧛🏻‍♀️","🐋","🪹","⛎"],
    "V": ["✌️","🫰","🖖","🌷","🏅","💎","♈️","✅","☑️","✔️"],
    "W": ["🥴","👻","👾","👐","🙌","🫅","🦹‍♀️","🧜🏿","🧜🏻‍♀️","🧜‍♂️","🤷🏻‍♀️","🤷","🤷‍♂️","👑","🪷","🔱","〰️"],
    "X": ["😵","😣","🤞","🧚‍♀️","🙅‍♀️","🙅","🙅‍♂️","🍀","🎿","🎻","✂️","❌","✖️","❎","🇯🇪","🏴","💠","⚔️"],
    "Y": ["👔","🧣","🦞","🪳","🌵","🌟","⛄️","🏆","💴"],
    "Z": ["😴","🔋","🪫","💤"],
}

# Mapeamento inverso emoji -> letra
EMOJI_TO_LETTER = {emoji: letter for letter, emojis in LETTER_TO_EMOJIS.items() for emoji in emojis}

# -----------------------------
# Funções auxiliares
# -----------------------------
def encode_text(text: str, n_variants: int = 5):
    """Gera n_variants sequências de emojis para um texto (case-insensitive)."""
    variants = []
    for _ in range(n_variants):
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
        variants.append(" ".join(tokens))
    return variants

def decode_emojis(emoji_string: str) -> str:
    """Decodifica uma sequência de emojis gerada pela função encode_text."""
    if not emoji_string:
        return ""
    # preserva blocos de espaços como tokens separados
    parts = re.split(r"(\s+)", emoji_string)
    decoded = []
    for part in parts:
        if part == "":
            continue
        if part.isspace():
            # qualquer bloco de espaço/linha vira um único espaço no texto final
            decoded.append(" ")
        else:
            decoded.append(EMOJI_TO_LETTER.get(part, part))
    return "".join(decoded)

def copy_button(text: str, label: str = "Copiar para área de transferência"):
    """Cria um botão simples de copiar para o clipboard via JS."""
    if not text:
        return
    js_text = json.dumps(text)  # string segura para JS
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

tab_encode, tab_decode = st.tabs(["Codificar (texto ➜ emojis)", "Decodificar (emojis ➜ texto)"])

# Estado inicial
if "encode_variants" not in st.session_state:
    st.session_state["encode_variants"] = None

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

    if st.button("Gerar sequências de emojis", type="primary"):
        if not text.strip():
            st.warning("Digite algum texto antes de codificar.")
        else:
            st.session_state["encode_variants"] = encode_text(text, n_variants=5)

    variants = st.session_state.get("encode_variants")

    if variants:
        main_variant = variants[0]

        st.markdown("#### Resultado principal")
        st.code(main_variant, language="text")
        copy_button(main_variant, "Copiar resultado principal")

        st.markdown("#### Outras variações (aleatórias)")
        options = {f"Variação {i+1}": variants[i] for i in range(1, len(variants))}
        selected_label = st.selectbox(
            "Escolha outra formação de emojis:",
            list(options.keys()),
        )
        selected_variant = options[selected_label]
        st.code(selected_variant, language="text")
        copy_button(selected_variant, f"Copiar {selected_label}")

        st.caption("Dica: você pode gerar novas combinações clicando novamente em “Gerar sequências de emojis”.")

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
