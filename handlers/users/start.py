from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp, bot, ADMIN_ID


# ══════════════════════════════════════════
#  STATES
# ══════════════════════════════════════════
class VacancyForm(StatesGroup):
    vacancy    = State()
    full_name  = State()
    phone      = State()
    photo      = State()
    birth_year = State()
    experience = State()
    smm_skill  = State()
    confirm    = State()


VACANCY_MOBILOGRAM = "📱 Mobilograf"
VACANCY_SMM        = "📊 SMM"

# Tahrirlash rejimida ekanligini bilish uchun flag
EDIT_FLAG = "editing"


# ══════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════
def _vacancy_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(VACANCY_MOBILOGRAM, VACANCY_SMM)
    return kb

def _phone_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📞 Raqamimni yuborish", request_contact=True))
    return kb

def _exp_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ Ha, ishlagan", "❌ Yo'q")
    return kb

def _skill_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    kb.add("🟢 Boshlang'ich", "🟡 O'rta", "🔴 Professional")
    return kb


# ══════════════════════════════════════════
#  PREVIEW HELPER
# ══════════════════════════════════════════
async def show_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()

    preview = (
        "📋 <b>Arizangizni tekshiring:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
        f"👤 <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
        f"📱 <b>Telefon:</b> {data.get('phone', '—')}\n"
        f"🎂 <b>Tug'ilgan yil:</b> {data.get('birth_year', '—')}\n"
        f"💼 <b>Tajriba:</b> {data.get('experience', '—')}\n"
        f"📊 <b>Daraja:</b> {data.get('smm_skill', '—')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ma'lumotlar to'g'rimi?"
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ Ha, yuborish", "✏️ Tahrirlash")

    await VacancyForm.confirm.set()

    photo = data.get('photo')
    if photo:
        await message.answer_photo(
            photo=photo,
            caption=preview,
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        await message.answer(preview, parse_mode="HTML", reply_markup=kb)


# ══════════════════════════════════════════
#  /start
# ══════════════════════════════════════════
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 👋\n\n"
        "Vakansiyaga ariza topshirish uchun quyidagi tugmani bosing.",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton("📋 Ariza topshirish")]],
            resize_keyboard=True
        )
    )


# ══════════════════════════════════════════
#  BOSHLASH
# ══════════════════════════════════════════
@dp.message_handler(lambda m: m.text == "📋 Ariza topshirish")
async def start_form(message: types.Message):
    await VacancyForm.vacancy.set()
    await message.answer(
        "💼 Qaysi lavozimga ariza topshirmoqchisiz?",
        parse_mode="HTML",
        reply_markup=_vacancy_kb()
    )


# ══════════════════════════════════════════
#  STEP 0 — lavozim
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.vacancy)
async def get_vacancy(message: types.Message, state: FSMContext):
    if message.text not in [VACANCY_MOBILOGRAM, VACANCY_SMM]:
        await message.answer("❗ Iltimos, quyidagi tugmalardan birini tanlang.")
        return

    await state.update_data(vacancy=message.text)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.full_name.set()
    await message.answer(
        f"✅ <b>{message.text}</b> tanlandi!\n\n"
        "✍️ <b>1/6</b> — Ism va familiyangizni kiriting:\n"
        "<i>Misol: Aliyev Jasur</i>",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )


# ══════════════════════════════════════════
#  STEP 1 — ism familiya
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 5:
        await message.answer("❗ Iltimos, to'liq ism-familiyangizni kiriting.")
        return

    await state.update_data(full_name=name)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.phone.set()
    await message.answer(
        "📱 <b>2/6</b> — Telefon raqamingizni yuboring:",
        parse_mode="HTML",
        reply_markup=_phone_kb()
    )


# ══════════════════════════════════════════
#  STEP 2 — telefon
# ══════════════════════════════════════════
@dp.message_handler(content_types=["contact", "text"], state=VacancyForm.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 9:
            await message.answer(
                "❗ Iltimos, to'g'ri telefon raqam kiriting.\n"
                "Misol: +998901234567"
            )
            return

    await state.update_data(phone=phone)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.photo.set()
    await message.answer(
        "🤳 <b>3/6</b> — Rasmingizni yuboring (selfie yoki profil rasm):",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )


# ══════════════════════════════════════════
#  STEP 3 — rasm
# ══════════════════════════════════════════
@dp.message_handler(content_types=["photo"], state=VacancyForm.photo)
async def get_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.birth_year.set()
    await message.answer(
        "🎂 <b>4/6</b> — Tug'ilgan yilingizni kiriting:\n"
        "<i>Misol: 2000</i>",
        parse_mode="HTML"
    )


@dp.message_handler(
    content_types=["text", "document", "sticker", "video", "audio"],
    state=VacancyForm.photo
)
async def photo_wrong(message: types.Message):
    await message.answer("❗ Iltimos, faqat rasm yuboring (foto sifatida).")


# ══════════════════════════════════════════
#  STEP 4 — tug'ilgan yil
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.birth_year)
async def get_birth_year(message: types.Message, state: FSMContext):
    year = message.text.strip()
    if not year.isdigit() or not (1970 <= int(year) <= 2010):
        await message.answer("❗ To'g'ri yil kiriting (1970–2010 oralig'ida).")
        return

    await state.update_data(birth_year=year)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.experience.set()
    await message.answer(
        "💼 <b>5/6</b> — Oldin shu sohasida ishlaganmisiz?",
        parse_mode="HTML",
        reply_markup=_exp_kb()
    )


# ══════════════════════════════════════════
#  STEP 5 — tajriba
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.experience)
async def get_experience(message: types.Message, state: FSMContext):
    if message.text not in ["✅ Ha, ishlagan", "❌ Yo'q"]:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang.")
        return

    exp = "Ha" if message.text == "✅ Ha, ishlagan" else "Yo'q"
    await state.update_data(experience=exp)
    data = await state.get_data()
    is_editing = data.get(EDIT_FLAG, False)

    if is_editing:
        await show_preview(message, state)
        return

    await VacancyForm.smm_skill.set()
    await message.answer(
        "📊 <b>6/6</b> — Darajangizni tanlang:",
        parse_mode="HTML",
        reply_markup=_skill_kb()
    )


# ══════════════════════════════════════════
#  STEP 6 — daraja
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.smm_skill)
async def get_smm_skill(message: types.Message, state: FSMContext):
    levels = ["🟢 Boshlang'ich", "🟡 O'rta", "🔴 Professional"]
    if message.text not in levels:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang.")
        return

    await state.update_data(smm_skill=message.text)
    # Daraja har doim preview ga qaytadi (normal va tahrirlash)
    await show_preview(message, state)


# ══════════════════════════════════════════
#  CONFIRM
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.confirm)
async def confirm_form(message: types.Message, state: FSMContext):

    # ── ✅ YUBORISH ──
    if message.text == "✅ Ha, yuborish":
        data = await state.get_data()
        user = message.from_user

        caption = (
            "📬 <b>Yangi vakansiya arizasi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💼 <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
            f"👤 <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
            f"📱 <b>Telefon:</b> {data.get('phone', '—')}\n"
            f"🎂 <b>Tug'ilgan yil:</b> {data.get('birth_year', '—')}\n"
            f"💼 <b>Tajriba:</b> {data.get('experience', '—')}\n"
            f"📊 <b>Daraja:</b> {data.get('smm_skill', '—')}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 Username: @{user.username if user.username else 'yoq'}\n"
            f"📛 To'liq ism: {user.full_name}"
        )

        try:
            photo = data.get('photo')
            if photo:
                await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo,
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=caption,
                    parse_mode="HTML"
                )

            await message.answer(
                "✅ <b>Arizangiz yuborildi!</b>\n\n"
                "Tez orada siz bilan bog'lanamiz. 🙏",
                parse_mode="HTML",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton("📋 Ariza topshirish")]],
                    resize_keyboard=True
                )
            )
        except Exception as e:
            await message.answer(
                f"⚠️ Yuborishda xato:\n<code>{e}</code>",
                parse_mode="HTML"
            )

        await state.finish()
        return

    # ── ✏️ TAHRIRLASH — maydon tanlash ──
    if message.text == "✏️ Tahrirlash":
        # editing flagini yoqamiz
        await state.update_data(**{EDIT_FLAG: True})

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            "💼 Lavozim",
            "👤 Ism-Familiya",
            "📱 Telefon",
            "🤳 Rasm",
            "🎂 Tug'ilgan yil",
            "💼 Tajriba",
            "📊 Daraja",
        )
        kb.add("🔙 Orqaga")
        await message.answer(
            "✏️ Qaysi ma'lumotni o'zgartirmoqchisiz?",
            reply_markup=kb
        )
        return

    # ── MAYDON TANLANDI ──
    edit_map = {
        "💼 Lavozim":       (VacancyForm.vacancy,    _vacancy_kb,                   "💼 Qaysi lavozimga ariza topshirmoqchisiz?"),
        "👤 Ism-Familiya":  (VacancyForm.full_name,  lambda: types.ReplyKeyboardRemove(), "✍️ Yangi ism-familiyangizni kiriting:"),
        "📱 Telefon":        (VacancyForm.phone,      _phone_kb,                     "📱 Yangi telefon raqamingizni yuboring:"),
        "🤳 Rasm":           (VacancyForm.photo,      lambda: types.ReplyKeyboardRemove(), "🤳 Yangi rasmingizni yuboring:"),
        "🎂 Tug'ilgan yil":  (VacancyForm.birth_year, lambda: types.ReplyKeyboardRemove(), "🎂 Yangi tug'ilgan yilingizni kiriting:"),
        "💼 Tajriba":        (VacancyForm.experience, _exp_kb,                       "💼 Oldin shu sohasida ishlaganmisiz?"),
        "📊 Daraja":         (VacancyForm.smm_skill,  _skill_kb,                     "📊 Darajangizni tanlang:"),
    }

    if message.text in edit_map:
        next_state, kb_fn, prompt = edit_map[message.text]
        await next_state.set()
        await message.answer(prompt, parse_mode="HTML", reply_markup=kb_fn())
        return

    # ── 🔙 ORQAGA ──
    if message.text == "🔙 Orqaga":
        await show_preview(message, state)
        return

    await message.answer("❗ Iltimos, tugmalardan birini tanlang.")