import json
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp, bot, ADMIN_ID

VOICE_STORE_PATH = os.path.join(os.path.dirname(__file__), "voice_store.json")


def _load_voice_store() -> dict:
    if os.path.exists(VOICE_STORE_PATH):
        with open(VOICE_STORE_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_voice_store(data: dict):
    with open(VOICE_STORE_PATH, "w") as f:
        json.dump(data, f)


def _get_active_positions() -> list:
    store = _load_voice_store()
    statuses = store.get("positions", {})
    result = []
    for pos in ALL_POSITIONS:
        if statuses.get(pos, True):
            result.append(pos)
    return result

CANCEL_BTN = "❌ Bekor qilish"


# ══════════════════════════════════════════
#  STATES  (21 savol + tasdiqlash)
# ══════════════════════════════════════════
class VacancyForm(StatesGroup):
    vacancy          = State()   # 1
    full_name        = State()   # 2
    phone            = State()   # 3
    photo            = State()   # 4
    address          = State()   # 5
    birth_date       = State()   # 6
    prev_experience  = State()   # 7
    married          = State()   # 8
    voice_family     = State()   # 9
    russian_level    = State()   # 10
    english_level    = State()   # 11
    ref_consent      = State()   # 12
    ref_person       = State()   # 13
    work_duration    = State()   # 14
    overtime         = State()   # 15
    health_ok        = State()   # 16
    late_reason      = State()   # 17
    theft_reason     = State()   # 18
    perf_reason      = State()   # 19
    prev_salary      = State()   # 20
    expected_salary  = State()   # 21
    courses          = State()   # 22
    confirm          = State()


EDIT_FLAG = "editing"

CALL_CENTER_POSITIONS = [
    "1. 📞 Call-center operatori",
]

SMM_POSITIONS = [
    "2. 📱 Mobilograf",
    "3. 📊 SMM",
]

ALL_POSITIONS = CALL_CENTER_POSITIONS + SMM_POSITIONS

LANGUAGE_LEVELS   = ["🔴 Bilmayman", "🟡 O'rta", "🟢 Yaxshi"]
YES_NO            = ["✅ Ha", "❌ Yo'q"]
SMM_EXP           = ["✅ Ha, ishlagan", "❌ Yo'q"]
SMM_SKILL         = ["🟢 Boshlang'ich", "🟡 O'rta", "🔴 Professional"]
PREV_EXP_OPTIONS  = ["1-3 oy", "4-6 oy", "8-12 oy", "1 yildan ko'p"]
WORK_DUR_OPTIONS  = ["3 oy", "6 oy", "9 oy", "1 yil", "1 yil +", "🏠 Kelajagimni shu yerda quraman"]


# ══════════════════════════════════════════
#  SMM / MOBILOGRAF STATES
# ══════════════════════════════════════════
class SMMForm(StatesGroup):
    full_name  = State()
    phone      = State()
    photo      = State()
    birth_year = State()
    experience = State()
    smm_skill  = State()
    confirm    = State()


# ══════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════
def _vacancy_kb():
    active = _get_active_positions()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    cc = [p for p in active if p in CALL_CENTER_POSITIONS]
    smm = [p for p in active if p in SMM_POSITIONS]
    if cc:
        kb.add(*cc)
    if smm:
        kb.add(*smm)
    return kb

def _exp_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(*SMM_EXP)
    return kb

def _skill_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    kb.add(*SMM_SKILL)
    return kb

def _phone_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📞 Raqamimni yuborish", request_contact=True))
    return kb

def _yes_no_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(*YES_NO)
    return kb

def _lang_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(*LANGUAGE_LEVELS)
    return kb

def _prev_exp_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(*PREV_EXP_OPTIONS)
    return kb

def _work_dur_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    kb.add("3 oy", "6 oy", "9 oy", "1 yil", "1 yil +")
    kb.add("🏠 Kelajagimni shu yerda quraman")
    return kb


# ══════════════════════════════════════════
#  PREVIEW HELPER
# ══════════════════════════════════════════
async def show_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()

    preview = (
        "📋 <b>Arizangizni tekshiring:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"1.  <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
        f"2.  <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
        f"3.  <b>Telefon:</b> {data.get('phone', '—')}\n"
        f"4.  <b>Rasm:</b> {'✅ Yuborildi' if data.get('photo') else '—'}\n"
        f"5.  <b>Manzil:</b> {data.get('address', '—')}\n"
        f"6.  <b>Tug'ilgan kun:</b> {data.get('birth_date', '—')}\n"
        f"7.  <b>Oldingi tajriba:</b> {data.get('prev_experience', '—')}\n"
        f"8.  <b>Oila qurganmi:</b> {data.get('married', '—')}\n"
        f"9.  <b>Oila ovozi:</b> {'✅ Yuborildi' if data.get('voice_family') else '—'}\n"
        f"10. <b>Rus tili:</b> {data.get('russian_level', '—')}\n"
        f"11. <b>Ingliz tili:</b> {data.get('english_level', '—')}\n"
        f"12. <b>Surish. rozilik:</b> {data.get('ref_consent', '—')}\n"
        f"13. <b>Tavsiya kishi:</b> {data.get('ref_person', '—')}\n"
        f"14. <b>Ishlash muddati:</b> {data.get('work_duration', '—')}\n"
        f"15. <b>Ortiqcha ish:</b> {data.get('overtime', '—')}\n"
        f"16. <b>Sog'liq:</b> {data.get('health_ok', '—')}\n"
        f"17. <b>Kech kelish sababi:</b> {data.get('late_reason', '—')}\n"
        f"18. <b>O'g'rilik sababi:</b> {data.get('theft_reason', '—')}\n"
        f"19. <b>Ishlash sifati:</b> {data.get('perf_reason', '—')}\n"
        f"20. <b>Oldingi maosh:</b> {data.get('prev_salary', '—')}\n"
        f"21. <b>Kutilayotgan maosh:</b> {data.get('expected_salary', '—')}\n"
        f"22. <b>Kurslar:</b> {data.get('courses', '—')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ma'lumotlar to'g'rimi?"
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ Ha, yuborish", "✏️ Tahrirlash")
    await VacancyForm.confirm.set()
    photo = data.get('photo')
    if photo:
        await message.answer_photo(photo=photo, caption=preview, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(preview, parse_mode="HTML", reply_markup=kb)


async def show_preview_smm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    preview = (
        "📋 <b>Arizangizni tekshiring:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"1. <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
        f"2. <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
        f"3. <b>Telefon:</b> {data.get('phone', '—')}\n"
        f"4. <b>Tug'ilgan yil:</b> {data.get('birth_year', '—')}\n"
        f"5. <b>Tajriba:</b> {data.get('experience', '—')}\n"
        f"6. <b>Daraja:</b> {data.get('smm_skill', '—')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ma'lumotlar to'g'rimi?"
    )
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ Ha, yuborish", "✏️ Tahrirlash")
    await SMMForm.confirm.set()
    photo = data.get('photo')
    if photo:
        await message.answer_photo(photo=photo, caption=preview, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(preview, parse_mode="HTML", reply_markup=kb)


# ══════════════════════════════════════════
#  ADMIN — LAVOZIMLAR BOSHQARUVI
# ══════════════════════════════════════════
def _positions_admin_kb(statuses: dict) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    for pos in ALL_POSITIONS:
        is_active = statuses.get(pos, True)
        icon = "✅" if is_active else "❌"
        kb.add(types.InlineKeyboardButton(
            text=f"{icon} {pos}",
            callback_data=f"toggle_pos:{pos}"
        ))
    return kb


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    commands=["positions"],
    state="*"
)
async def admin_positions(message: types.Message):
    store = _load_voice_store()
    statuses = store.get("positions", {})
    await message.answer(
        "🗂 <b>Lavozimlar holati:</b>\n✅ — faol  |  ❌ — nofaol\n\nO'zgartirish uchun tugmani bosing:",
        parse_mode="HTML",
        reply_markup=_positions_admin_kb(statuses)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("toggle_pos:"), state="*")
async def toggle_position(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q.", show_alert=True)
        return
    pos = call.data.split("toggle_pos:", 1)[1]
    if pos not in ALL_POSITIONS:
        await call.answer("Noma'lum lavozim.")
        return
    store = _load_voice_store()
    statuses = store.get("positions", {})
    statuses[pos] = not statuses.get(pos, True)
    store["positions"] = statuses
    _save_voice_store(store)
    status_text = "faol ✅" if statuses[pos] else "nofaol ❌"
    await call.answer(f"{pos} — {status_text}")
    await call.message.edit_reply_markup(reply_markup=_positions_admin_kb(statuses))


# ══════════════════════════════════════════
#  ADMIN — OVOZ O'RNATISH
# ══════════════════════════════════════════
class AdminVoiceSet(StatesGroup):
    waiting_voice_q8  = State()
    waiting_intro_video = State()


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    commands=["setvideo"],
    state="*"
)
async def admin_cmd_setvideo(message: types.Message, state: FSMContext):
    await AdminVoiceSet.waiting_intro_video.set()
    await message.answer("🎬 Endi 1-savoldan oldin ko'rsatiladigan videoni yuboring:")


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    content_types=["video", "video_note"],
    state=AdminVoiceSet.waiting_intro_video
)
async def admin_save_intro_video(message: types.Message, state: FSMContext):
    store = _load_voice_store()
    if message.video:
        store["intro_video"] = {"file_id": message.video.file_id, "type": "video"}
    else:
        store["intro_video"] = {"file_id": message.video_note.file_id, "type": "video_note"}
    _save_voice_store(store)
    await state.finish()
    await message.answer("✅ Intro videosi saqlandi!")


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    state=AdminVoiceSet.waiting_intro_video
)
async def admin_intro_wrong(message: types.Message):
    await message.answer("❗ Iltimos, video yuboring.")


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    commands=["setvoice8"],
    state="*"
)
async def admin_cmd_setvoice8(message: types.Message, state: FSMContext):
    await AdminVoiceSet.waiting_voice_q8.set()
    await message.answer("🎙 Endi 8-savol uchun ovozli xabar yuboring:")


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    content_types=["voice"],
    state=AdminVoiceSet.waiting_voice_q8
)
async def admin_save_voice_q8(message: types.Message, state: FSMContext):
    store = _load_voice_store()
    store["q8"] = message.voice.file_id
    _save_voice_store(store)
    await state.finish()
    await message.answer("✅ 8-savol uchun ovozli xabar saqlandi!")


@dp.message_handler(
    lambda m: m.from_user.id == ADMIN_ID,
    state=AdminVoiceSet.waiting_voice_q8
)
async def admin_voice_wrong(message: types.Message):
    await message.answer("❗ Iltimos, ovozli xabar yuboring.")


# ══════════════════════════════════════════
#  /start
# ══════════════════════════════════════════
@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
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
    intro = _load_voice_store().get("intro_video")
    if intro:
        try:
            if intro["type"] == "video":
                await bot.send_video(chat_id=message.chat.id, video=intro["file_id"])
            else:
                await bot.send_video_note(chat_id=message.chat.id, video_note=intro["file_id"])
        except Exception:
            pass
    await VacancyForm.vacancy.set()
    await message.answer(
        "💼 Kompaniyamizda qaysi lavozimga ariza topshirmoqchisiz?",
        parse_mode="HTML",
        reply_markup=_vacancy_kb()
    )


# ══════════════════════════════════════════
#  STEP 1 — Lavozim
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.vacancy)
async def get_vacancy(message: types.Message, state: FSMContext):
    if message.text not in _get_active_positions():
        await message.answer("❗ Iltimos, quyidagi tugmalardan birini tanlang.")
        return
    await state.update_data(vacancy=message.text)
    data = await state.get_data()
    if data.get(EDIT_FLAG):
        if message.text in SMM_POSITIONS:
            await show_preview_smm(message, state)
        else:
            await show_preview(message, state)
        return
    if message.text in SMM_POSITIONS:
        await SMMForm.full_name.set()
        await message.answer(
            f"✅ <b>{message.text}</b> tanlandi!\n\n"
            "✍️ <b>1/6</b> — Ism va familiyangizni kiriting:\n<i>Misol: Aliyev Jasur</i>",
            parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await VacancyForm.full_name.set()
        await message.answer(
            "✍️ <b>2/22</b> — Ism va familiyangizni kiriting:\n<i>Misol: Aliyev Jasur</i>",
            parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
        )


# ══════════════════════════════════════════
#  STEP 2 — Ism-familiya
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 5:
        await message.answer("❗ Iltimos, to'liq ism-familiyangizni kiriting."); return
    await state.update_data(full_name=name)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.phone.set()
    await message.answer(
        "📱 <b>3/22</b> — Telefon raqamingizni yuboring:",
        parse_mode="HTML", reply_markup=_phone_kb()
    )


# ══════════════════════════════════════════
#  STEP 3 — Telefon
# ══════════════════════════════════════════
@dp.message_handler(content_types=["contact", "text"], state=VacancyForm.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 9:
            await message.answer("❗ To'g'ri telefon raqam kiriting.\nMisol: +998901234567"); return
    await state.update_data(phone=phone)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.photo.set()
    await message.answer(
        "🤳 <b>4/22</b> — Rasmingizni yuboring (selfie yoki profil rasm):",
        parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
    )


# ══════════════════════════════════════════
#  STEP 4 — Rasm
# ══════════════════════════════════════════
@dp.message_handler(content_types=["photo"], state=VacancyForm.photo)
async def get_photo_cc(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.address.set()
    await message.answer(
        "🏠 <b>5/22</b> — Doimiy yashash manzilingizni yozing (propiska):\n"
        "<i>Misol: Samarqand shahar</i>",
        parse_mode="HTML"
    )

@dp.message_handler(
    content_types=["text", "document", "sticker", "video", "audio"],
    state=VacancyForm.photo
)
async def photo_cc_wrong(message: types.Message):
    await message.answer("❗ Iltimos, faqat rasm yuboring (foto sifatida).")


# ══════════════════════════════════════════
#  STEP 5 — Manzil (propiska)
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.address)
async def get_address(message: types.Message, state: FSMContext):
    addr = message.text.strip()
    if len(addr) < 5:
        await message.answer("❗ Iltimos, to'liq manzilingizni kiriting."); return
    await state.update_data(address=addr)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.birth_date.set()
    await message.answer(
        "🎂 <b>6/22</b> — O'z tug'ilgan kuningizni yozing:\n<i>Format: 01.01.2000</i>",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 6 — Tug'ilgan kun
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.birth_date)
async def get_birth_date(message: types.Message, state: FSMContext):
    import re
    val = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", val):
        await message.answer("❗ Iltimos, 01.01.2000 formatida kiriting."); return
    await state.update_data(birth_date=val)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.prev_experience.set()
    await message.answer(
        "💼 <b>7/22</b> — Oldingi ish tajribangiz qancha?",
        parse_mode="HTML", reply_markup=_prev_exp_kb()
    )


# ══════════════════════════════════════════
#  STEP 7 — Oldingi tajriba
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.prev_experience)
async def get_prev_experience(message: types.Message, state: FSMContext):
    if message.text not in PREV_EXP_OPTIONS:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(prev_experience=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.married.set()
    await message.answer(
        "👨‍👩‍👧 <b>8/22</b> — Oila qurganmisiz?",
        parse_mode="HTML", reply_markup=_yes_no_kb()
    )


# ══════════════════════════════════════════
#  STEP 7 — Oila qurganmisiz
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.married)
async def get_married(message: types.Message, state: FSMContext):
    if message.text not in YES_NO:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(married=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.voice_family.set()
    q8_voice_id = _load_voice_store().get("q8")
    if q8_voice_id:
        await bot.send_voice(
            chat_id=message.chat.id,
            voice=q8_voice_id,
            caption="🎙 <b>9/22</b> — Oilangiz haqida <b>1 daqiqa ichida</b> ovozli xabar yuboring:",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "🎙 <b>9/22</b> — Oilangiz haqida <b>1 daqiqa ichida</b> ovozli xabar yuboring:",
            parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
        )


# ══════════════════════════════════════════
#  STEP 8 — Ovozli xabar (oila haqida)
# ══════════════════════════════════════════
@dp.message_handler(content_types=["voice"], state=VacancyForm.voice_family)
async def get_voice_family(message: types.Message, state: FSMContext):
    await state.update_data(voice_family=message.voice.file_id)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.russian_level.set()
    await message.answer(
        "🇷🇺 <b>10/22</b> — Rus tilini qay darajada bilasiz?",
        parse_mode="HTML", reply_markup=_lang_kb()
    )

@dp.message_handler(
    content_types=["text", "document", "sticker", "video", "audio", "photo"],
    state=VacancyForm.voice_family
)
async def voice_wrong(message: types.Message):
    await message.answer("🎙 Iltimos, faqat ovozli xabar yuboring (mikrofon tugmasidan foydalaning).")


# ══════════════════════════════════════════
#  STEP 9 — Rus tili
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.russian_level)
async def get_russian_level(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGE_LEVELS:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(russian_level=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.english_level.set()
    await message.answer(
        "🇬🇧 <b>11/22</b> — Ingliz tilini qay darajada bilasiz?",
        parse_mode="HTML", reply_markup=_lang_kb()
    )


# ══════════════════════════════════════════
#  STEP 10 — Ingliz tili
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.english_level)
async def get_english_level(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGE_LEVELS:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(english_level=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.ref_consent.set()
    await message.answer(
        "🔍 <b>12/22</b> — Oxirgi ish joyingizdan siz haqingizda surishtirishimizga rozimisiz?",
        parse_mode="HTML", reply_markup=_yes_no_kb()
    )


# ══════════════════════════════════════════
#  STEP 11 — Surishtirishga rozilik
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.ref_consent)
async def get_ref_consent(message: types.Message, state: FSMContext):
    if message.text not in YES_NO:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(ref_consent=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.ref_person.set()
    await message.answer(
        "📝 <b>13/22</b> — Oxirgi ish joyingizdan kim sizga tavsiya xati bera oladi?\n"
        "<i>Nomi, ishlash joyi, lavozimi, telefon raqami:</i>",
        parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
    )


# ══════════════════════════════════════════
#  STEP 12 — Tavsiya kishi
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.ref_person)
async def get_ref_person(message: types.Message, state: FSMContext):
    await state.update_data(ref_person=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.work_duration.set()
    await message.answer(
        "⏳ <b>14/22</b> — Bizning korxonada qancha muddat ishlamoqchisiz?",
        parse_mode="HTML", reply_markup=_work_dur_kb()
    )


# ══════════════════════════════════════════
#  STEP 13 — Ishlash muddati
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.work_duration)
async def get_work_duration(message: types.Message, state: FSMContext):
    if message.text not in WORK_DUR_OPTIONS:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(work_duration=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.overtime.set()
    await message.answer(
        "🕐 <b>15/22</b> — Korxonada ishdan keyin ham qolib ishlash kerak bo'lib qolsa ishlaysizmi?",
        parse_mode="HTML", reply_markup=_yes_no_kb()
    )


# ══════════════════════════════════════════
#  STEP 14 — Ortiqcha ish vaqti
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.overtime)
async def get_overtime(message: types.Message, state: FSMContext):
    if message.text not in YES_NO:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(overtime=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.health_ok.set()
    await message.answer(
        "🏥 <b>16/22</b> — Sog'ligingizda muammo yo'qmi?",
        parse_mode="HTML", reply_markup=_yes_no_kb()
    )


# ══════════════════════════════════════════
#  STEP 15 — Sog'liq
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.health_ok)
async def get_health_ok(message: types.Message, state: FSMContext):
    if message.text not in YES_NO:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(health_ok=message.text)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.late_reason.set()
    await message.answer(
        "<b>17/22</b> — Nima uchun ayrim odamlar ishga kech kelishadi?",
        parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
    )


# ══════════════════════════════════════════
#  STEP 16 — Kech kelish sababi
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.late_reason)
async def get_late_reason(message: types.Message, state: FSMContext):
    await state.update_data(late_reason=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.theft_reason.set()
    await message.answer(
        "<b>18/22</b> — Nima uchun ayrim insonlar o'g'rilik qilishadi?",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 17 — O'g'rilik sababi
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.theft_reason)
async def get_theft_reason(message: types.Message, state: FSMContext):
    await state.update_data(theft_reason=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.perf_reason.set()
    await message.answer(
        "🤔 <b>19/22</b> — Nima uchun ayrim ishchilar yaxshi ishlashadi, ayrimlari yomon?\n"
        "Bunga sabab nima?",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 18 — Ishlash sifati sababi
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.perf_reason)
async def get_perf_reason(message: types.Message, state: FSMContext):
    await state.update_data(perf_reason=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.prev_salary.set()
    await message.answer(
        "💰 <b>110/22</b> — Oldingi ishxonangizda qancha maoshga ishlagansiz?\n"
        "<i>Misol: 3 000 000 so'm</i>",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 19 — Oldingi maosh
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.prev_salary)
async def get_prev_salary(message: types.Message, state: FSMContext):
    digits = message.text.strip().replace(" ", "").replace(",", "")
    if not digits.isdigit():
        await message.answer("❗ Iltimos, faqat son kiriting.\n<i>Misol: 3000000</i>", parse_mode="HTML"); return
    await state.update_data(prev_salary=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.expected_salary.set()
    await message.answer(
        "💵 <b>21/22</b> — Bizning ishxonamizda qancha maoshga ishlamoqchisiz?\n"
        "<i>Misol: 5000000</i>",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 20 — Kutilayotgan maosh
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.expected_salary)
async def get_expected_salary(message: types.Message, state: FSMContext):
    digits = message.text.strip().replace(" ", "").replace(",", "")
    if not digits.isdigit():
        await message.answer("❗ Iltimos, faqat son kiriting.\n<i>Misol: 5000000</i>", parse_mode="HTML"); return
    await state.update_data(expected_salary=message.text.strip())
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview(message, state); return
    await VacancyForm.courses.set()
    await message.answer(
        "📚 <b>22/22</b> — Qanday kurslarda o'qigansiz?\n"
        "<i>Misol: Moliya asoslari, Call-center asoslari</i>",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════
#  STEP 21 — Kurslar
# ══════════════════════════════════════════
@dp.message_handler(state=VacancyForm.courses)
async def get_courses(message: types.Message, state: FSMContext):
    await state.update_data(courses=message.text.strip())
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
            "📬 <b>Yangi Call-center arizasi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"1.  <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
            f"2.  <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
            f"3.  <b>Telefon:</b> {data.get('phone', '—')}\n"
            f"5.  <b>Manzil:</b> {data.get('address', '—')}\n"
            f"6.  <b>Tug'ilgan kun:</b> {data.get('birth_date', '—')}\n"
            f"7.  <b>Oldingi tajriba:</b> {data.get('prev_experience', '—')}\n"
            f"8.  <b>Oila qurganmi:</b> {data.get('married', '—')}\n"
            f"10. <b>Rus tili:</b> {data.get('russian_level', '—')}\n"
            f"11. <b>Ingliz tili:</b> {data.get('english_level', '—')}\n"
            f"12. <b>Surish. rozilik:</b> {data.get('ref_consent', '—')}\n"
            f"13. <b>Tavsiya kishi:</b> {data.get('ref_person', '—')}\n"
            f"14. <b>Ishlash muddati:</b> {data.get('work_duration', '—')}\n"
            f"15. <b>Ortiqcha ish:</b> {data.get('overtime', '—')}\n"
            f"16. <b>Sog'liq:</b> {data.get('health_ok', '—')}\n"
            f"17. <b>Kech kelish:</b> {data.get('late_reason', '—')}\n"
            f"18. <b>O'g'rilik:</b> {data.get('theft_reason', '—')}\n"
            f"19. <b>Ishlash sifati:</b> {data.get('perf_reason', '—')}\n"
            f"20. <b>Oldingi maosh:</b> {data.get('prev_salary', '—')}\n"
            f"21. <b>Kutilayotgan maosh:</b> {data.get('expected_salary', '—')}\n"
            f"22. <b>Kurslar:</b> {data.get('courses', '—')}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 Username: @{user.username if user.username else 'yoq'}\n"
            f"📛 To'liq ism: {user.full_name}"
        )

        try:
            photo_id = data.get('photo')
            if photo_id:
                await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=caption, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="HTML")

            voice_id = data.get('voice_family')
            if voice_id:
                await bot.send_voice(
                    chat_id=ADMIN_ID,
                    voice=voice_id,
                    caption="🎙 9-savol: Oila haqida ovozli xabar"
                )

            await message.answer(
                "✅ <b>Arizangiz muvaffaqiyatli yuborildi!</b>\n\n"
                "Tez orada siz bilan bog'lanamiz. 🙏",
                parse_mode="HTML",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton("📋 Ariza topshirish")]],
                    resize_keyboard=True
                )
            )
        except Exception as e:
            await message.answer(f"⚠️ Yuborishda xato:\n<code>{e}</code>", parse_mode="HTML")

        await state.finish()
        return

    # ── ✏️ TAHRIRLASH ──
    if message.text == "✏️ Tahrirlash":
        await state.update_data(**{EDIT_FLAG: True})

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            "1 Lavozim",        "2 Ism-Familiya",
            "3 Telefon",        "4 Rasm",
            "5 Manzil",         "6 Tug'ilgan kun",
            "7 Tajriba",        "8 Oila",
            "9 Ovozli xabar",   "10 Rus tili",
            "11 Ingliz tili",   "12 Rozilik",
            "13 Tavsiya",       "14 Muddat",
            "15 Ortiqcha ish",  "16 Sog'liq",
            "17 Kech kelish",   "18 O'g'rilik",
            "19 Ishlash sifati","20 Oldingi maosh",
            "21 Kutilayotgan",  "22 Kurslar",
        )
        kb.add("🔙 Orqaga")
        await message.answer("✏️ Qaysi ma'lumotni o'zgartirmoqchisiz?", reply_markup=kb)
        return

    # ── MAYDON TANLANDI ──
    edit_map = {
        "1 Lavozim":        (VacancyForm.vacancy,         _vacancy_kb,                         "💼 Qaysi lavozimni tanlaysiz?"),
        "2 Ism-Familiya":   (VacancyForm.full_name,       lambda: types.ReplyKeyboardRemove(), "✍️ Yangi ism-familiyangizni kiriting:"),
        "3 Telefon":        (VacancyForm.phone,           _phone_kb,                           "📱 Yangi telefon raqamingizni yuboring:"),
        "4 Rasm":           (VacancyForm.photo,           lambda: types.ReplyKeyboardRemove(), "🤳 Yangi rasmingizni yuboring:"),
        "5 Manzil":         (VacancyForm.address,         lambda: types.ReplyKeyboardRemove(), "🏠 Yangi manzilingizni kiriting:"),
        "6 Tug'ilgan kun":  (VacancyForm.birth_date,      lambda: types.ReplyKeyboardRemove(), "🎂 Tug'ilgan kuningizni kiriting (01.01.2000):"),
        "7 Tajriba":        (VacancyForm.prev_experience, _prev_exp_kb,                        "💼 Oldingi ish tajribangiz qancha?"),
        "8 Oila":           (VacancyForm.married,         _yes_no_kb,                          "👨‍👩‍👧 Oila qurganmisiz?"),
        "9 Ovozli xabar":   (VacancyForm.voice_family,    lambda: types.ReplyKeyboardRemove(), "🎙 <b>9/22</b> — Oila haqida yangi ovozli xabar yuboring:"),
        "10 Rus tili":      (VacancyForm.russian_level,   _lang_kb,                            "🇷🇺 Rus tili darajangizni tanlang:"),
        "11 Ingliz tili":   (VacancyForm.english_level,   _lang_kb,                            "🇬🇧 Ingliz tili darajangizni tanlang:"),
        "12 Rozilik":       (VacancyForm.ref_consent,     _yes_no_kb,                          "🔍 Surishtirishga rozimisiz?"),
        "13 Tavsiya":       (VacancyForm.ref_person,      lambda: types.ReplyKeyboardRemove(), "📝 Tavsiya xati bera oladigan kishini yozing:"),
        "14 Muddat":        (VacancyForm.work_duration,   _work_dur_kb,                        "⏳ Qancha muddat ishlamoqchisiz?"),
        "15 Ortiqcha ish":  (VacancyForm.overtime,        _yes_no_kb,                          "🕐 Ortiqcha ish vaqtida ishlaysizmi?"),
        "16 Sog'liq":       (VacancyForm.health_ok,       _yes_no_kb,                          "🏥 Sog'ligingizda muammo yo'qmi?"),
        "17 Kech kelish":   (VacancyForm.late_reason,     lambda: types.ReplyKeyboardRemove(), "🤔 Nima uchun kech kelishadi?"),
        "18 O'g'rilik":     (VacancyForm.theft_reason,    lambda: types.ReplyKeyboardRemove(), "🤔 Nima uchun o'g'rilik qilishadi?"),
        "19 Ishlash sifati":(VacancyForm.perf_reason,     lambda: types.ReplyKeyboardRemove(), "🤔 Yaxshi/yomon ishlash sababi:"),
        "20 Oldingi maosh": (VacancyForm.prev_salary,     lambda: types.ReplyKeyboardRemove(), "💰 Oldingi maoshingizni kiriting:"),
        "21 Kutilayotgan":  (VacancyForm.expected_salary, lambda: types.ReplyKeyboardRemove(), "💵 Kutilayotgan maoshingizni kiriting:"),
        "22 Kurslar":       (VacancyForm.courses,         lambda: types.ReplyKeyboardRemove(), "📚 Qanday kurslarda o'qigansiz?"),
    }

    if message.text in edit_map:
        next_state, kb_fn, prompt = edit_map[message.text]
        await next_state.set()
        if next_state == VacancyForm.voice_family:
            q8_voice_id = _load_voice_store().get("q8")
            if q8_voice_id:
                await bot.send_voice(
                    chat_id=message.chat.id,
                    voice=q8_voice_id,
                    caption=prompt,
                    parse_mode="HTML",
                    reply_markup=kb_fn()
                )
                return
        if next_state == VacancyForm.photo:
            await message.answer("🤳 Yangi rasmingizni yuboring:", reply_markup=types.ReplyKeyboardRemove())
            return
        await message.answer(prompt, parse_mode="HTML", reply_markup=kb_fn())
        return

    if message.text == "🔙 Orqaga":
        await show_preview(message, state)
        return

    await message.answer("❗ Iltimos, tugmalardan birini tanlang.")


# ══════════════════════════════════════════════════════════════
#  SMM / MOBILOGRAF FORM HANDLERS
# ══════════════════════════════════════════════════════════════

@dp.message_handler(state=SMMForm.full_name)
async def smm_get_full_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 5:
        await message.answer("❗ Iltimos, to'liq ism-familiyangizni kiriting."); return
    await state.update_data(full_name=name)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview_smm(message, state); return
    await SMMForm.phone.set()
    await message.answer("📱 <b>2/6</b> — Telefon raqamingizni yuboring:", parse_mode="HTML", reply_markup=_phone_kb())


@dp.message_handler(content_types=["contact", "text"], state=SMMForm.phone)
async def smm_get_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 9:
            await message.answer("❗ Iltimos, to'g'ri telefon raqam kiriting.\nMisol: +998901234567"); return
    await state.update_data(phone=phone)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview_smm(message, state); return
    await SMMForm.photo.set()
    await message.answer("🤳 <b>3/6</b> — Rasmingizni yuboring (selfie yoki profil rasm):", parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=["photo"], state=SMMForm.photo)
async def smm_get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview_smm(message, state); return
    await SMMForm.birth_year.set()
    await message.answer("🎂 <b>4/6</b> — Tug'ilgan yilingizni kiriting:\n<i>Misol: 2000</i>", parse_mode="HTML")


@dp.message_handler(content_types=["text", "document", "sticker", "video", "audio"], state=SMMForm.photo)
async def smm_photo_wrong(message: types.Message):
    await message.answer("❗ Iltimos, faqat rasm yuboring (foto sifatida).")


@dp.message_handler(state=SMMForm.birth_year)
async def smm_get_birth_year(message: types.Message, state: FSMContext):
    year = message.text.strip()
    if not year.isdigit() or not (1970 <= int(year) <= 2010):
        await message.answer("❗ To'g'ri yil kiriting (1970–2010 oralig'ida)."); return
    await state.update_data(birth_year=year)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview_smm(message, state); return
    await SMMForm.experience.set()
    await message.answer("💼 <b>5/6</b> — Oldin shu sohasida ishlaganmisiz?", parse_mode="HTML", reply_markup=_exp_kb())


@dp.message_handler(state=SMMForm.experience)
async def smm_get_experience(message: types.Message, state: FSMContext):
    if message.text not in SMM_EXP:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    exp = "Ha" if message.text == "✅ Ha, ishlagan" else "Yo'q"
    await state.update_data(experience=exp)
    if (await state.get_data()).get(EDIT_FLAG):
        await show_preview_smm(message, state); return
    await SMMForm.smm_skill.set()
    await message.answer("📊 <b>6/6</b> — Darajangizni tanlang:", parse_mode="HTML", reply_markup=_skill_kb())


@dp.message_handler(state=SMMForm.smm_skill)
async def smm_get_skill(message: types.Message, state: FSMContext):
    if message.text not in SMM_SKILL:
        await message.answer("❗ Iltimos, tugmalardan birini tanlang."); return
    await state.update_data(smm_skill=message.text)
    await show_preview_smm(message, state)


@dp.message_handler(state=SMMForm.confirm)
async def smm_confirm_form(message: types.Message, state: FSMContext):
    if message.text == "✅ Ha, yuborish":
        data = await state.get_data()
        user = message.from_user
        caption = (
            "📬 <b>Yangi vakansiya arizasi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"1. <b>Lavozim:</b> {data.get('vacancy', '—')}\n"
            f"2. <b>Ism-Familiya:</b> {data.get('full_name', '—')}\n"
            f"3. <b>Telefon:</b> {data.get('phone', '—')}\n"
            f"4. <b>Tug'ilgan yil:</b> {data.get('birth_year', '—')}\n"
            f"5. <b>Tajriba:</b> {data.get('experience', '—')}\n"
            f"6. <b>Daraja:</b> {data.get('smm_skill', '—')}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 Username: @{user.username if user.username else 'yoq'}\n"
            f"📛 To'liq ism: {user.full_name}"
        )
        try:
            photo = data.get('photo')
            if photo:
                await bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="HTML")
            await message.answer(
                "✅ <b>Arizangiz yuborildi!</b>\n\nTez orada siz bilan bog'lanamiz. 🙏",
                parse_mode="HTML",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton("📋 Ariza topshirish")]],
                    resize_keyboard=True
                )
            )
        except Exception as e:
            await message.answer(f"⚠️ Yuborishda xato:\n<code>{e}</code>", parse_mode="HTML")
        await state.finish()
        return

    if message.text == "✏️ Tahrirlash":
        await state.update_data(**{EDIT_FLAG: True})
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add("💼 Lavozim", "👤 Ism-Familiya", "📱 Telefon", "🤳 Rasm", "🎂 Tug'ilgan yil", "💼 Tajriba", "📊 Daraja")
        kb.add("🔙 Orqaga")
        await message.answer("✏️ Qaysi ma'lumotni o'zgartirmoqchisiz?", reply_markup=kb)
        return

    smm_edit_map = {
        "💼 Lavozim":       (VacancyForm.vacancy,  _vacancy_kb,                        "💼 Qaysi lavozimga ariza topshirmoqchisiz?"),
        "👤 Ism-Familiya":  (SMMForm.full_name,    lambda: types.ReplyKeyboardRemove(), "✍️ Yangi ism-familiyangizni kiriting:"),
        "📱 Telefon":        (SMMForm.phone,        _phone_kb,                          "📱 Yangi telefon raqamingizni yuboring:"),
        "🤳 Rasm":           (SMMForm.photo,        lambda: types.ReplyKeyboardRemove(), "🤳 Yangi rasmingizni yuboring:"),
        "🎂 Tug'ilgan yil":  (SMMForm.birth_year,  lambda: types.ReplyKeyboardRemove(), "🎂 Yangi tug'ilgan yilingizni kiriting:"),
        "💼 Tajriba":        (SMMForm.experience,  _exp_kb,                            "💼 Oldin shu sohasida ishlaganmisiz?"),
        "📊 Daraja":         (SMMForm.smm_skill,   _skill_kb,                          "📊 Darajangizni tanlang:"),
    }
    if message.text in smm_edit_map:
        next_state, kb_fn, prompt = smm_edit_map[message.text]
        await next_state.set()
        await message.answer(prompt, parse_mode="HTML", reply_markup=kb_fn())
        return
    if message.text == "🔙 Orqaga":
        await show_preview_smm(message, state)
        return
    await message.answer("❗ Iltimos, tugmalardan birini tanlang.")