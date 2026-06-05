import joblib
import pandas as pd
import folium
import random
import os

# ==========================================
# 1. ЗАГРУЗКА МОДЕЛИ И ДАННЫХ
# ==========================================
print("🔄 Загрузка модели и данных...")

# Пути к файлам (относительно корня проекта)
MODEL_PATH = "models/rf_model.pkl"
DATA_PATH = "data/cleaned_apartments_full.csv"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Модель не найдена по пути: {MODEL_PATH}")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Датасет не найден по пути: {DATA_PATH}")

# Загружаем "мозги" Random Forest (вместе с Pipeline и импутером)
model = joblib.load(MODEL_PATH)
print("✅ Модель Random Forest успешно загружена!")

# Загружаем полный датасет, чтобы знать ВСЕ признаки, которые ждет модель
df_full = pd.read_csv(DATA_PATH)
# Исключаем целевую переменную, оставляем только признаки (X)
feature_columns = [col for col in df_full.columns if col != "last_price"]
print(f"✅ Датасет загружен. Модель ожидает {len(feature_columns)} признаков.")


# ==========================================
# 2. ЛОГИКА AI-АГЕНТА (Оркестратор LLM + ML)
# ==========================================
def ai_agent_predict(area, rooms, distance_to_center, kitchen, floors):
    """
    Имитирует работу AI-агента: формирует корректный вектор признаков,
    делает предсказание через Random Forest и генерирует человеческий ответ.
    """
    # 1. Создаем шаблон строки со медианными значениями для ВСЕХ признаков модели
    input_data = {col: df_full[col].median() for col in feature_columns}

    # 2. Перезаписываем только те параметры, которые указал пользователь
    input_data["total_area"] = area
    input_data["rooms"] = rooms
    input_data["cityCenters_nearest"] = distance_to_center
    input_data["kitchen_area"] = kitchen
    input_data["floors_total"] = floors

    # 3. Преобразуем в DataFrame строго в том порядке колонок, который ждет модель
    df_input = pd.DataFrame([input_data])[feature_columns]

    # 4. Магия: модель делает предсказание за доли миллисекунды
    predicted_price = model.predict(df_input)[0]

    # 5. Генерация ответа (имитация LLM, которая получила результат от Tool)
    response = f"🏠 **Оценка стоимости вашей квартиры**\n\n"
    response += f"📍 **Параметры:** {area} м², {rooms} комн., кухня {kitchen} м², до центра ~{distance_to_center/1000:.1f} км, этажность дома: {floors}.\n"
    response += (
        f"💰 **Прогнозируемая рыночная стоимость:** {predicted_price:,.0f} руб.\n\n"
    )
    response += "💡 **Анализ от AI-агента:**\n"
    response += f"Основную ценность квартиры формирует её общая площадь ({area} м²). "

    if distance_to_center < 10000:
        response += "Отличная локация: близость к центру города является сильным фاкторoм, повышающим стоимость.\n"
    else:
        response += "Квартира находится в отдалении от центра, что немного снижает базовую стоимость, но это часто компенсируется большей площадью и экологичностью района.\n"

    response += "\n*Оценка сделана алгоритмом машинного обучения (Random Forest) на основе актуальных рыночных данных.*"
    return response


# ==========================================
# 3. ГЕНЕРАЦИЯ КАРТЫ (Folium)
# ==========================================
def generate_spb_map():
    print("🗺️ Генерация карты Санкт-Петербурга...")
    # Центр Питера
    m = folium.Map(location=[59.9343, 30.3351], zoom_start=11)

    # Маркер центра
    folium.Marker(
        location=[59.9343, 30.3351],
        popup="Центр Санкт-Петербурга",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Добавляем 20 случайных "квартир" для антуража (имитация данных из БД)
    for _ in range(20):
        lat = 59.9343 + random.uniform(-0.15, 0.15)
        lon = 30.3351 + random.uniform(-0.25, 0.25)
        price = random.randint(5000000, 15000000)

        folium.Marker(
            location=[lat, lon],
            popup=f"Квартира<br>Цена: {price:,.0f} руб.",
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(m)

    map_filename = "spb_map.html"
    m.save(map_filename)
    print(f"✅ Карта сохранена как '{map_filename}'. Открой её в браузере!")


# ==========================================
# 4. ЗАПУСК И ТЕСТИРОВАНИЕ
# ==========================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 ЗАПУСК AI-АГЕНТА ПО НЕДВИЖИМОСТИ (DEMO)")
    print("=" * 60 + "\n")

    # Тестируем агента на конкретных параметрах
    result = ai_agent_predict(
        area=55.0, rooms=2, distance_to_center=12000.0, kitchen=9.0, floors=9.0
    )
    print(result)

    print("\n" + "=" * 60)
    # Генерируем карту
    generate_spb_map()
    print("=" * 60)
    print("🎉 Проект готов к демонстрации!")
