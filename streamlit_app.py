import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import random

# ==========================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ==========================================
st.set_page_config(
    page_title="Недвижимость AI - Помощник риелтора",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================
# ЗАГРУЗКА МОДЕЛИ И ДАННЫХ (кэшируем)
# ==========================================
@st.cache_resource
def load_model():
    return joblib.load("models/rf_model.pkl")


@st.cache_resource
def load_data():
    df = pd.read_csv("data/cleaned_apartments_full.csv")
    feature_columns = [col for col in df.columns if col != "last_price"]
    return df, feature_columns


model = load_model()
df_full, feature_columns = load_data()


# ==========================================
# ФУНКЦИЯ ПРЕДСКАЗАНИЯ
# ==========================================
def predict_price(area, rooms, distance_to_center, kitchen, floors):
    input_data = {col: df_full[col].median() for col in feature_columns}
    input_data["total_area"] = area
    input_data["rooms"] = rooms
    input_data["cityCenters_nearest"] = distance_to_center
    input_data["kitchen_area"] = kitchen
    input_data["floors_total"] = floors

    df_input = pd.DataFrame([input_data])[feature_columns]
    predicted_price = model.predict(df_input)[0]
    return predicted_price


# ==========================================
# ГЕНЕРАЦИЯ КАРТЫ (кэшируем)
# ==========================================
@st.cache_data
def generate_map():
    m = folium.Map(location=[59.9343, 30.3351], zoom_start=11)

    folium.Marker(
        location=[59.9343, 30.3351],
        popup="Центр Санкт-Петербурга",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    for _ in range(20):
        lat = 59.9343 + random.uniform(-0.15, 0.15)
        lon = 30.3351 + random.uniform(-0.25, 0.25)
        price = random.randint(5000000, 15000000)

        folium.Marker(
            location=[lat, lon],
            popup=f"Квартира<br>Цена: {price:,.0f} руб.",
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(m)

    return m


# ==========================================
# ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ СЕАНСА
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"  # welcome, form_filled, showing_result
if "map_generated" not in st.session_state:
    st.session_state.map_generated = False

# ==========================================
# ШАПКА
# ==========================================
st.markdown(
    """
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
    <h1 style='color: white; margin: 0; text-align: center;'>🏠 Недвижимость AI - Помощник риелтора</h1>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# ОСНОВНОЙ LAYOUT (две колонки)
# ==========================================
col_left, col_right = st.columns([1, 1])

# ==========================================
# ЛЕВАЯ КОЛОНКА: Заставка / Форма / Карта + Инфо-блок
# ==========================================
with col_left:
    if st.session_state.stage == "welcome":
        st.markdown(
            """
        <div style='background: #f0f2f6; padding: 2rem; border-radius: 15px; text-align: center; margin-top: 1rem;'>
            <h2 style='color: #667eea;'>Добро пожаловать!</h2>
            <h3 style='color: #764ba2;'>Агентство элитной недвижимости "Премиум Хаус"</h3>
            <p style='font-size: 1.1rem; color: #555; margin-top: 1rem;'>
                AI-помощник для профессиональных риелторов.<br>
                Точная оценка стоимости квартир на основе машинного обучения.
            </p>
            <div style='margin-top: 2rem; padding: 1rem; background: white; border-radius: 10px;'>
                <h4>🚀 Возможности:</h4>
                <ul style='text-align: left; display: inline-block;'>
                    <li>Мгновенная оценка стоимости</li>
                    <li>Анализ рыночных данных</li>
                    <li>Поиск аналогичных объектов</li>
                    <li>Интерактивная карта</li>
                </ul>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif st.session_state.stage == "form_filled":
        st.markdown("### 📝 Параметры квартиры")
        with st.form("apartment_form"):
            area = st.number_input(
                "Общая площадь (м²)",
                min_value=10.0,
                max_value=500.0,
                value=55.0,
                step=1.0,
            )
            rooms = st.selectbox("Количество комнат", [1, 2, 3, 4, 5, 6])
            distance = st.number_input(
                "Расстояние до центра (м)",
                min_value=0,
                max_value=50000,
                value=10000,
                step=500,
            )
            kitchen = st.number_input(
                "Площадь кухни (м²)",
                min_value=3.0,
                max_value=100.0,
                value=9.0,
                step=0.5,
            )
            floors = st.number_input(
                "Этажность дома", min_value=1, max_value=50, value=9, step=1
            )

            submitted = st.form_submit_button(
                "💰 Оценить стоимость", type="primary", use_container_width=True
            )

            if submitted:
                price = predict_price(area, rooms, distance, kitchen, floors)

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": f"Площадь: {area} м², Комнат: {rooms}, До центра: {distance}м, Кухня: {kitchen} м², Этажей: {floors}",
                    }
                )

                location_text = (
                    "в центре" if distance < 10000 else "в отдалении от центра"
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"""
**Результат оценки:**

📍 **Параметры:** {area} м², {rooms} комн., кухня {kitchen} м², 
до центра ~{distance/1000:.1f} км ({location_text}), этажность: {floors}.

💰 **Рыночная стоимость:** {price:,.0f} руб.

💡 **Анализ:** Основная ценность формируется площадью ({area} м²). 
{'Отличная локация!' if distance < 10000 else 'Район спокойный, компенсируется площадью.'}

Продолжим оценку следующей квартиры?""",
                    }
                )

                st.session_state.stage = "showing_result"
                st.rerun()

    elif st.session_state.stage == "showing_result":
        st.markdown("### 🗺️ Похожие объекты на карте")
        map_obj = generate_map()
        st_folium(
            map_obj, width=700, height=500, key=f"map_{len(st.session_state.messages)}"
        )

    # ==========================================
    # ИНФО-БЛОК ВНИЗУ ЛЕВОЙ КОЛОНКИ
    # ==========================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
    <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; text-align: center; margin-top: auto;'>
        <p style='margin: 0; color: #333; font-size: 1rem; font-weight: bold;'>
            © 2026 Агентство "Премиум Хаус"
        </p>
        <p style='margin: 8px 0 0 0; color: #666; font-size: 0.9rem;'>
            Разработчик: Андрей Абрамов<br>
            <span style='font-size: 0.8rem; color: #888;'>AI-помощник для профессиональных риелторов</span>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ==========================================
# ПРАВАЯ КОЛОНКА: Чат с AI-агентом
# ==========================================
with col_right:
    st.markdown("### 💬 Диалог с AI-агентом")

    # Контейнер для сообщений с ФИКСИРОВАННОЙ высотой для скролла
    with st.container(height=550):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Управление кнопками в зависимости от стадии
    if st.session_state.stage == "welcome":
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🚀 Начать оценку квартиры", use_container_width=True, type="primary"
        ):
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Здравствуйте! Я AI-помощник агентства 'Премиум Хаус'. Помогу вам быстро оценить стоимость квартиры. Заполните параметры в форме слева 👈",
                }
            )
            st.session_state.stage = "form_filled"
            st.rerun()

    elif st.session_state.stage == "form_filled":
        st.info(
            "👈 Заполните параметры квартиры в форме слева и нажмите 'Оценить стоимость'"
        )

    elif st.session_state.stage == "showing_result":
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Да, оценить другую", use_container_width=True):
                st.session_state.messages.append(
                    {"role": "user", "content": "Да, продолжим"}
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "Отлично! Заполните параметры следующей квартиры в форме слева.",
                    }
                )
                st.session_state.stage = "form_filled"
                st.session_state.map_generated = False
                st.rerun()
        with col2:
            if st.button("❌ Нет, завершить", use_container_width=True):
                # ПОЛНЫЙ СБРОС СОСТОЯНИЯ
                st.session_state.messages = []
                st.session_state.stage = "welcome"
                st.session_state.map_generated = False
                st.rerun()
