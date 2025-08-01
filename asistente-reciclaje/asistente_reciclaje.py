# 📦 1. Importación de librerías
import streamlit as st
import pandas as pd
import unicodedata
from fuzzywuzzy import fuzz
import os
import random

# ⚙️ 2. Configuración de la página
st.set_page_config(page_title="Asistente de Reciclaje", page_icon="♻️")
emojis = ["♻️", "🌱", "🗑️", "🚮", "🔄"]
st.markdown(f"# {random.choice(emojis)} Bienvenido al asistente de reciclaje")
st.markdown("Consulta cómo clasificar correctamente tus residuos.")

# 📂 3. Cargar archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("clasificacion_residuos.xlsx")
    return df

data = cargar_datos()

# 🧹 4. Función para limpiar texto
def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = texto.replace("\n", "").replace("\r", "")
    return texto

# 🧼 5. Aplicar limpieza a la columna de residuos
data["RESIDUO"] = data["RESIDUO"].apply(limpiar_texto)

# 🔍 6. Entrada del usuario y búsqueda por semejanza
residuo_input = st.text_input("🔍 Escribe el nombre del residuo que quieres clasificar:")

if residuo_input:
    residuo_limpio = limpiar_texto(residuo_input)
    data["similaridad"] = data["RESIDUO"].apply(lambda x: fuzz.partial_ratio(residuo_limpio, x))
    resultado = data[data["similaridad"] >= 80].sort_values(by="similaridad", ascending=False)

    if not resultado.empty:
        st.success("✅ Clasificación encontrada:")
        st.dataframe(resultado.drop(columns=["similaridad"]))

        # 🖼️ 7. Mostrar imagen según CONTENEDOR
        if "CONTENEDOR" in resultado.columns and pd.notna(resultado.iloc[0]["CONTENEDOR"]):
            contenedor = resultado.iloc[0]["CONTENEDOR"].lower()
            imagen = None

            if "verde" in contenedor:
                imagen = "contenedor_verde.jpeg"
            elif "blanco" in contenedor:
                imagen = "contenedor_blanco.jpeg"
            elif "negro" in contenedor:
                imagen = "contenedor_negro.jpeg"
            elif "manejo especial" in contenedor:
                imagen = "manejo_especial.jpeg"
            elif "recoleccion" in contenedor:
                imagen = "punto_recoleccion.jpeg"
            elif "reincorporacion" in contenedor:
                imagen = "reincorporacion.jpeg"

            if imagen and os.path.exists(imagen):
                st.image(imagen, caption=f"Contenedor sugerido: {contenedor.capitalize()}", width=150)
            else:
                st.warning("⚠️ Imagen del contenedor no disponible.")

        # 🎨 8. Mostrar icono, imagen adicional y consejo
        if "APROVECHABLE" in resultado.columns and pd.notna(resultado.iloc[0]["APROVECHABLE"]):
            tipo = resultado.iloc[0]["APROVECHABLE"].lower()
            residuo_nombre = resultado.iloc[0]["RESIDUO"].lower()

            # Imagen específica para papel
            if "papel" in residuo_nombre:
                st.image("papel_reciclable.jpeg", caption="Ejemplo de papel reciclable", width=250)

            # Consejo especial para vidrio
            if "vidrio" in residuo_nombre or "cristal" in residuo_nombre:
                st.warning("⚠️🧤🔒 Para evitar lesiones en el personal de recolección, los vidrios se deben separar en una caja de cartón bien sellada y marcada por fuera para indicar su contenido.")

            # Icono de aprovechabilidad
            icono = {
                "si": "♻️",
                "no": "🚫",
                "especial": "⚠️"
            }.get(tipo, "❓")
            st.markdown(f"### {icono} ¿Aprovechable?: {tipo.capitalize()}")

            # Consejos personalizados
            consejos_personalizados = {
                "servilleta": "Las servilletas usadas no son reciclables. Deposítalas en el contenedor negro.",
                "llanta": "Consulta en tu taller si reciben llantas viejas o llévalas a un punto de recolección especializado.",
                "botella pet": "Este residuo es reciclable. Asegúrate de que esté limpio y seco.",
                "cascara de fruta": "Ideal para compostaje. Deposítala en el contenedor verde.",
                "pila": "Este residuo requiere manejo especial. Llévalo a un punto limpio."
            }

            consejo = consejos_personalizados.get(residuo_nombre)

            if consejo:
                st.info(consejo)
            else:
                consejos_generales = {
                    "si": "Este residuo puede reciclarse. Asegúrate de que esté limpio y seco.",
                    "no": "Este residuo no es reciclable. Deposítalo en el contenedor adecuado.",
                    "especial": "Este residuo requiere manejo especial. Llévalo a un punto limpio."
                }
                st.info(consejos_generales.get(tipo, "Consulta con tu entidad ambiental local."))
        else:
            st.warning("⚠️ No se encontró información sobre si el residuo es aprovechable.")
    else:
        st.warning("❌ No se encontró ese residuo en la base de datos.")

# 📚 9. Sección educativa: ¿Sabías que...?
sabias_que = [
    "♻️ Reciclar una lata de aluminio ahorra suficiente energía para hacer funcionar una TV por 3 horas.",
    "🌱 Los residuos orgánicos representan más del 50% de la basura doméstica.",
    "🔋 Una pila puede contaminar hasta 600,000 litros de agua si no se dispone correctamente.",
    "📦 El cartón reciclado puede convertirse en papel higiénico, cajas nuevas o incluso muebles."
]

st.sidebar.markdown("### ¿Sabías que...?")
st.sidebar.success(random.choice(sabias_que))


