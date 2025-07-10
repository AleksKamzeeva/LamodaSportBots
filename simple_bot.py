# ... (остальные импорты и настройки остаются без изменений)

# --- Хендлеры ---

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Нажми кнопку ниже, чтобы начать:", reply_markup=start_keyboard)

@dp.message_handler(Text(equals="🚀 Нет товара"), state="*")
async def start_survey(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем предыдущее состояние если было
    await message.answer("Выбери город:", reply_markup=city_keyboard)
    await RequestForm.city.set()

@dp.message_handler(state=RequestForm.city)
async def process_city(message: types.Message, state: FSMContext):
    if message.text not in cities:
        await message.reply("Пожалуйста, выбери город из предложенного списка.", reply_markup=city_keyboard)
        return
    
    await state.update_data(city=message.text)
    await message.answer("Теперь введи бренд:", reply_markup=ReplyKeyboardRemove())
    await RequestForm.brand.set()

@dp.message_handler(state=RequestForm.brand)
async def process_brand(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Введи размер:")
    await RequestForm.size.set()

@dp.message_handler(state=RequestForm.size)
async def process_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("Введи модель:")
    await RequestForm.model.set()

@dp.message_handler(state=RequestForm.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Выбери цвет из списка:", reply_markup=color_keyboard)
    await RequestForm.color.set()

@dp.message_handler(state=RequestForm.color)
async def process_color(message: types.Message, state: FSMContext):
    if message.text.lower() not in COLORS:
        await message.reply("Пожалуйста, выбери цвет из предложенного списка.", reply_markup=color_keyboard)
        return
    
    await state.update_data(color=message.text.lower())
    data = await state.get_data()

    # Сохраняем в БД
    cursor.execute('''
        INSERT INTO requests (user_id, city, brand, size, model, color, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.from_user.id,
        data['city'],
        data['brand'],
        data.get('size'),
        data.get('model'),
        data.get('color'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

    await message.answer(
        "Спасибо! Запись сохранена.\n"
        "Если нужно добавить ещё один товар - снова нажми 🚀 Нет товара.", 
        reply_markup=start_keyboard
    )
    await state.finish()

# ... (остальной код остается без изменений)
