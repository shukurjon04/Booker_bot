import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
import json
import os
from datetime import datetime

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ma'lumotlar fayllari
DATA_DIR = 'bot_data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
CARD_FILE = os.path.join(DATA_DIR, 'card.json')

# Admin ID
ADMIN_ID = [1968968950,7684493777]

# Conversation states
NAME = 0
PHONE = 1
PROFILE_REGION = 2
PROFILE_DISTRICT = 3
PROFILE_VILLAGE = 4
BOOK_SELECT = 5
PAYMENT_METHOD = 6
PAYMENT_RECEIPT = 7
FEEDBACK = 8
ADMIN_ADD_BOOK_NAME = 9
ADMIN_ADD_BOOK_CATEGORY = 10
ADMIN_ADD_BOOK_PRICE = 11
EDIT_BOOK_NAME = 12
EDIT_BOOK_CATEGORY = 13
EDIT_BOOK_PRICE = 14
PROFILE_EDIT_NAME = 15
PROFILE_EDIT_PHONE = 16
PROFILE_EDIT_REGION = 17
PROFILE_EDIT_DISTRICT = 18
PROFILE_EDIT_VILLAGE = 19
ADMIN_CARD_NUMBER = 20
ADMIN_CARD_OWNER = 21

os.makedirs(DATA_DIR, exist_ok=True)

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_books():
    books = load_data(BOOKS_FILE)
    if not books:
        books = {
            "1": {"name": "Python dasturlash", "category": "Dasturlash", "price": "50000"},
            "2": {"name": "O'tkan kunlar", "category": "Badiiy adabiyot", "price": "35000"},
            "3": {"name": "Algoritimlar va ma'lumotlar strukturasi", "category": "Dasturlash", "price": "60000"}
        }
        save_data(BOOKS_FILE, books)
    return books

def load_card_info():
    """Karta ma'lumotlarini yuklash"""
    card_data = load_data(CARD_FILE)
    if not card_data:
        card_data = {
            'card_number': '',
            'card_owner': ''
        }
        save_data(CARD_FILE, card_data)
    return card_data

def save_card_info(card_number, card_owner):
    """Karta ma'lumotlarini saqlash"""
    card_data = {
        'card_number': card_number,
        'card_owner': card_owner
    }
    save_data(CARD_FILE, card_data)
    return card_data

def main_menu_keyboard():
    keyboard = [
        ['📚 Kitoblar', '🛒 Buyurtma berish'],
        ['📋 Mening buyurtmalarim', '👤 Profilni tahrirlash'],
        ['ℹ️ Biz haqimizda', '/cancel']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu_keyboard():
    keyboard = [
        ['📊 Statistika', '📦 Buyurtmalar'],
        ['➕ Yangi kitob qo\'shish', '📚 Kitoblar ro\'yxati'],
        ['👥 Foydalanuvchilar', '/cancel',
         '💳 Karta sozlamalari']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data(USERS_FILE)

    if user.id in ADMIN_ID:
        await update.message.reply_text(
            f"Assalomu alaykum Admin! 👋\n\nAdmin paneliga xush kelibsiz.",
            reply_markup=admin_menu_keyboard()
        )
        return ConversationHandler.END

    if str(user.id) in users:
        await update.message.reply_text(
            f"Xush kelibsiz, {users[str(user.id)]['name']}! 👋\n\n"
            f"Sizga qanday yordam bera olaman?",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        """
        Sardorbek Rustamov, Bahodirjon Yulchiyev "Milliy sertifikat" kitobi 
Assalomu alaykum!
Ushbu bot orqali "Milliy Sertifikat TARIX" kitobiga buyurtma berishingiz mumkin. Kitobda:

✔️ 20 ta variant (javoblari bilan)
✔️ Namunayiv testlar
✔️ A+ darajadagi tushuntirishlar
✔️ Sirtqi, kunduzgi va milliy sertifikat imtihonlariga tayyorlanish uchun eng qulay qo'llanma

Tez yetkazib berish mavjud!

Ismingiz va familiyangizni kiriting:
        """
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text

    keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Telefon raqamingizni yuboring:",
        reply_markup=reply_markup
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    users = load_data(USERS_FILE)
    users[str(user.id)] = {
        'name': context.user_data.get('name', ''),
        'phone': phone,
        'username': user.username or 'N/A',
        'registered_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'region': users.get(str(user.id), {}).get('region', ''),
        'district': users.get(str(user.id), {}).get('district', ''),
        'village': users.get(str(user.id), {}).get('village', '')
    }
    save_data(USERS_FILE, users)

    await update.message.reply_text(
        "Iltimos, viloyatingizni (masalan: Farg'ona) kiriting:"
    )
    return PROFILE_REGION

async def profile_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    region = update.message.text.strip()

    users = load_data(USERS_FILE)
    if str(user.id) not in users:
        users[str(user.id)] = {}
    users[str(user.id)]['region'] = region
    save_data(USERS_FILE, users)

    await update.message.reply_text("Tumaningiz nomini kiriting:")
    return PROFILE_DISTRICT

async def profile_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    district = update.message.text.strip()

    users = load_data(USERS_FILE)
    users[str(user.id)]['district'] = district
    save_data(USERS_FILE, users)

    await update.message.reply_text("Qishloqingiz nomini kiriting:")
    return PROFILE_VILLAGE

async def profile_village(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    village = update.message.text.strip()

    users = load_data(USERS_FILE)
    users[str(user.id)]['village'] = village
    save_data(USERS_FILE, users)

    await update.message.reply_text(
        "Ro'yxatdan o'tish tugallandi! ✅\n\n"
        "Sizning ma'lumotlaringiz saqlandi.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def show_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = load_data(BOOKS_FILE)
    user = update.effective_user

    if not books:
        await update.message.reply_text("Hozircha kitoblar mavjud emas.")
        return

    if user.id in ADMIN_ID:
        for book_id, book in books.items():
            keyboard = [
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"editbook_{book_id}"),
                 InlineKeyboardButton("🗑 O'chirish", callback_data=f"deletebook_{book_id}")]
            ]
            reply = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"📖 {book['name']}\n   Kategoriya: {book['category']}\n   Narxi: {book['price']} so'm",
                reply_markup=reply
            )
    else:
        message = "📚 Mavjud kitoblar:\n\n"
        for book_id, book in books.items():
            message += f"📖 {book['name']}\n"
            message += f"   Kategoriya: {book['category']}\n"
            message += f"   Narxi: {book['price']} so'm\n\n"
        await update.message.reply_text(message)

async def delete_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split('_', 1)
    if len(parts) < 2:
        await query.message.reply_text("Xatolik: noto'g'ri buyruq.")
        return

    book_id = parts[1]
    books = load_data(BOOKS_FILE)
    if book_id not in books:
        await query.message.edit_message_text("Kitob topilmadi yoki allaqachon o'chirilgan.")
        return

    deleted = books.pop(book_id)
    new_books = {}
    idx = 1
    for k, v in books.items():
        new_books[str(idx)] = v
        idx += 1
    save_data(BOOKS_FILE, new_books)

    try:
        await query.edit_message_text(f"🗑 Kitob '{deleted.get('name')}' muvaffaqiyatli o'chirildi.")
    except:
        await query.message.reply_text(f"🗑 Kitob '{deleted.get('name')}' muvaffaqiyatli o'chirildi.")

async def edit_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split('_', 1)
    if len(parts) < 2:
        await query.message.reply_text("Xatolik: noto'g'ri buyruq.")
        return ConversationHandler.END

    book_id = parts[1]
    books = load_data(BOOKS_FILE)
    book = books.get(book_id)
    if not book:
        await query.message.reply_text("Kitob topilmadi.")
        return ConversationHandler.END

    context.user_data['edit_book_id'] = book_id
    await query.message.reply_text(f"Tahrirlash: eski nom: {book.get('name')}\nYangi nomni kiriting:")
    return EDIT_BOOK_NAME

async def edit_book_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_book_name'] = update.message.text.strip()
    await update.message.reply_text("Yangi kategoriyani kiriting:")
    return EDIT_BOOK_CATEGORY

async def edit_book_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_book_category'] = update.message.text.strip()
    await update.message.reply_text("Yangi narxni kiriting (so'mda):")
    return EDIT_BOOK_PRICE

async def edit_book_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_price = update.message.text.strip()
    book_id = context.user_data.get('edit_book_id')
    new_name = context.user_data.get('edit_book_name')
    new_category = context.user_data.get('edit_book_category')

    books = load_data(BOOKS_FILE)
    if book_id not in books:
        await update.message.reply_text("Kitob topilmadi, yangilab bo'lmadi.")
        return ConversationHandler.END

    books[book_id] = {
        'name': new_name,
        'category': new_category,
        'price': new_price
    }
    save_data(BOOKS_FILE, books)

    await update.message.reply_text(f"✅ Kitob muvaffaqiyatli yangilandi!\nNomi: {new_name}\nKategoriya: {new_category}\nNarx: {new_price} so'm", reply_markup=admin_menu_keyboard())
    return ConversationHandler.END

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data(USERS_FILE)

    if str(user.id) not in users:
        await update.message.reply_text(
            "Buyurtma berish uchun avval ro'yxatdan o'tishingiz kerak.\n"
            "/start buyrug'ini bosing."
        )
        return ConversationHandler.END

    books = load_data(BOOKS_FILE)
    if not books:
        await update.message.reply_text("Hozircha kitoblar mavjud emas.")
        return ConversationHandler.END

    # Kitoblar ro'yxatini matn ko'rinishida tayyorlaymiz
    message = "📚 Mavjud kitoblar:\n\n"
    for book_id, book in books.items():
        message += f"{book_id}. {book['name']}\n"

    # Sahifalash uchun context ga ma'lumot saqlaymiz
    context.user_data['current_page'] = 0
    context.user_data['books_list'] = list(books.keys())
    
    # Inline tugmalarni tayyorlaymiz
    keyboard = []
    books_list = list(books.items())
    
    # Har bir sahifada 10 ta kitob
    books_per_page = 10
    page = 0
    start_idx = page * books_per_page
    end_idx = start_idx + books_per_page
    page_books = books_list[start_idx:end_idx]
    
    # Kitob tugmalari - 5 tadan 2 qatorda (jami 10 ta)
    for i in range(0, len(page_books), 5):
        row = []
        for book_id, book in page_books[i:i+5]:
            row.append(InlineKeyboardButton(book_id, callback_data=f"book_{book_id}"))
        keyboard.append(row)
    
    # Navigatsiya tugmalari - 3 ta alohida qatorda
    total_pages = (len(books_list) + books_per_page - 1) // books_per_page
    
    if total_pages > 1:
        # Orqaga tugmasi (agar 1-sahifadan keyin bo'lsa)
        if page > 0:
            keyboard.append([InlineKeyboardButton("⬅️", callback_data="page_prev")])
        else:
            keyboard.append([InlineKeyboardButton(" ", callback_data="page_empty")])
        
        # Yopish tugmasi
        keyboard.append([InlineKeyboardButton("❌", callback_data="page_close")])
        
        # Keyingi tugmasi (agar oxirgi sahifa bo'lmasa)
        if end_idx < len(books_list):
            keyboard.append([InlineKeyboardButton("➡️", callback_data="page_next")])
        else:
            keyboard.append([InlineKeyboardButton(" ", callback_data="page_empty")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return BOOK_SELECT

async def book_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Sahifalash uchun
    if query.data in ["page_next", "page_prev", "page_empty"]:
        await handle_pagination(update, context)
        return BOOK_SELECT
    
    # Yopish tugmasi
    if query.data == "page_close":
        try:
            await query.message.delete()
        except:
            await query.message.reply_text("Bekor qilindi.", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    book_id = query.data.split('_')[1]
    books = load_data(BOOKS_FILE)
    book = books.get(book_id)

    if not book:
        await query.message.reply_text("Kitob topilmadi.")
        return ConversationHandler.END

    context.user_data['book_id'] = book_id
    context.user_data['book_name'] = book['name']
    context.user_data['book_price'] = book['price']

    keyboard = [
        [InlineKeyboardButton("💳 Click", callback_data="payment_click")],
        [InlineKeyboardButton("💵 Naqd pul", callback_data="payment_cash")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        f"Tanlangan kitob: {book['name']}\n"
        f"Narxi: {book['price']} so'm\n\n"
        f"To'lov usulini tanlang:",
        reply_markup=reply_markup
    )

    return PAYMENT_METHOD

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sahifalashni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    books = load_data(BOOKS_FILE)
    books_list = list(books.items())
    
    # Sahifa raqamini yangilash
    current_page = context.user_data.get('current_page', 0)
    
    if query.data == "page_next":
        current_page += 1
    elif query.data == "page_prev":
        current_page -= 1
    elif query.data == "page_info":
        # Sahifa info bosilsa hech narsa qilmaymiz
        return BOOK_SELECT
    
    context.user_data['current_page'] = current_page
    
    # Kitoblar ro'yxatini matn ko'rinishida tayyorlaymiz
    message = "📚 Mavjud kitoblar:\n\n"
    for book_id, book in books.items():
        message += f"{book_id}. {book['name']}\n"
        message += f"   💰 Narxi: {book['price']} so'm\n\n"
    
    # Inline tugmalarni tayyorlaymiz
    keyboard = []
    books_per_page = 10
    start_idx = current_page * books_per_page
    end_idx = start_idx + books_per_page
    page_books = books_list[start_idx:end_idx]
    
    # Kitob tugmalari - har 5 tadan qatorlarda
    current_row = []
    for idx, (book_id, book) in enumerate(page_books):
        current_row.append(InlineKeyboardButton(book_id, callback_data=f"book_{book_id}"))
        # Har 5 ta kitobdan keyin yangi qator
        if (idx + 1) % 5 == 0:
            keyboard.append(current_row)
            current_row = []
    
    # Qolgan kitoblarni qo'shish
    if current_row:
        keyboard.append(current_row)
    
    # Navigatsiya tugmalari
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton("◀️ Orqaga", callback_data="page_prev"))
    
    # Sahifa raqami
    total_pages = (len(books_list) + books_per_page - 1) // books_per_page
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="page_info"))
    
    if end_idx < len(books_list):
        nav_row.append(InlineKeyboardButton("▶️ Keyingi", callback_data="page_next"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup
        )
    except:
        await query.message.reply_text(
            message,
            reply_markup=reply_markup
        )
    
    return BOOK_SELECT

async def payment_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payment_method = query.data.split('_')[1]
    context.user_data['payment_method'] = payment_method

    if payment_method == 'click':
        # Karta ma'lumotlarini olish
        card_info = load_card_info()
        card_number = card_info.get('card_number', '')
        card_owner = card_info.get('card_owner', '')
        
        if card_number:
            card_message = (
                f"💳 To'lov usuli: Click orqali to'lov\n\n"
                f"📌 Quyidagi karta raqamiga pul o'tkazing:\n\n"
                f"💳 Karta raqami: `{card_number}`\n"
                f"👤 Egasi: {card_owner}\n\n"
                f"To'lovni amalga oshirgandan so'ng, to'lov chekini (rasm yoki PDF) yuboring:"
            )
        else:
            card_message = (
                f"💳 To'lov usuli: Click orqali to'lov\n\n"
                f"⚠️ Karta ma'lumotlari hali kiritilmagan.\n"
                f"Iltimos admin bilan bog'laning.\n\n"
                f"To'lov chekini (rasm yoki PDF) yuboring:"
            )
        
        await query.message.reply_text(card_message, parse_mode='Markdown')
        return PAYMENT_RECEIPT
    else:
        # Naqd pul - chek so'ralmasin
        context.user_data['receipt_file_id'] = None
        context.user_data['receipt_file_type'] = None
        
        keyboard = [
            [InlineKeyboardButton("✅ Buyurtmani yakunlash", callback_data="finish_order")],
            [InlineKeyboardButton("💬 Fikr qoldirish", callback_data="leave_feedback")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "To'lov usuli: Naqd pul ✅\n\n"
            "Buyurtmani yakunlaysizmi yoki fikr qoldirmoqchimisiz?",
            reply_markup=reply_markup
        )
        return FEEDBACK

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = 'photo'
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = 'document'
    else:
        await update.message.reply_text("Iltimos, rasm yoki PDF fayl yuboring.")
        return PAYMENT_RECEIPT

    context.user_data['receipt_file_id'] = file_id
    context.user_data['receipt_file_type'] = file_type

    keyboard = [
        [InlineKeyboardButton("✅ Buyurtmani yakunlash", callback_data="finish_order")],
        [InlineKeyboardButton("💬 Fikr qoldirish", callback_data="leave_feedback")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "To'lov cheki qabul qilindi! ✅\n\n"
        "Buyurtmani yakunlaysizmi yoki fikr qoldirmoqchimisiz?",
        reply_markup=reply_markup
    )

    return FEEDBACK

async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    users = load_data(USERS_FILE)
    user_data = users.get(str(user.id))
    if not user_data:
        await query.message.reply_text("Foydalanuvchi ma'lumotlari topilmadi. Iltimos qayta /start bering.")
        return ConversationHandler.END

    orders = load_data(ORDERS_FILE)
    order_number = len(orders) + 1

    order = {
        'order_number': order_number,
        'user_id': user.id,
        'user_name': user_data['name'],
        'user_phone': user_data['phone'],
        'user_region': user_data.get('region', '-'),
        'user_district': user_data.get('district', '-'),
        'user_village': user_data.get('village', '-'),
        'book_id': context.user_data.get('book_id'),
        'book_name': context.user_data.get('book_name'),
        'book_price': context.user_data.get('book_price'),
        'payment_method': context.user_data.get('payment_method'),
        'receipt_file_id': context.user_data.get('receipt_file_id'),
        'receipt_file_type': context.user_data.get('receipt_file_type'),
        'feedback': context.user_data.get('feedback', 'Yo\'q'),
        'status': 'pending',
        'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    orders[str(order_number)] = order
    save_data(ORDERS_FILE, orders)

    await query.message.reply_text(
        f"Buyurtma muvaffaqiyatli yuborildi! 🎉\n\n"
        f"Buyurtma raqami: #{order_number}\n"
        f"Kitob: {order['book_name']}\n"
        f"Narxi: {order['book_price']} so'm\n\n"
        f"Buyurtmangiz tez orada ko'rib chiqiladi va tasdiqlash xabari yuboriladi.",
        reply_markup=main_menu_keyboard()
    )

    # Admin uchun xabar inline tugmalar bilan
    payment_text = "Click" if order['payment_method'] == 'click' else "Naqd pul"
    
    admin_message = (
        f"🔔 YANGI BUYURTMA!\n\n"
        f"Buyurtma raqami: #{order_number}\n"
        f"Mijoz: {order['user_name']}\n"
        f"Telefon: {order['user_phone']}\n"
        f"Manzil: {order['user_region']}, {order['user_district']}, {order['user_village']}\n"
        f"Kitob: {order['book_name']}\n"
        f"Narxi: {order['book_price']} so'm\n"
        f"To'lov: {payment_text}\n"
        f"Fikr: {order['feedback']}\n"
        f"Sana: {order['order_date']}"
    )

    # Inline tugmalarni to'lov usuliga qarab tayyorlaymiz
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{order_number}"),
         InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject_{order_number}")]
    ]
    
    # Agar Click to'lovi bo'lsa, chekni ko'rish tugmasini qo'shamiz
    if order['payment_method'] == 'click' and order.get('receipt_file_id'):
        keyboard.insert(0, [InlineKeyboardButton("👁 Chekni ko'rish", callback_data=f"view_receipt_{order_number}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Adminga xabar yuborishda xatolik: {e}")

    return ConversationHandler.END

async def leave_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Fikringizni yozing:")
    return FEEDBACK

async def feedback_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("✅ Buyurtmani yakunlash", callback_data="finish_order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Fikringiz qabul qilindi! Rahmat! 🙏\n\n"
        "Buyurtmani yakunlash uchun tugmani bosing:",
        reply_markup=reply_markup
    )
    return FEEDBACK

async def view_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_number = query.data.split('_')[-1]
    orders = load_data(ORDERS_FILE)
    order = orders.get(order_number)

    if not order:
        await query.message.reply_text("Buyurtma topilmadi.")
        return

    if order.get('receipt_file_type') == 'photo':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=order.get('receipt_file_id'),
            caption=f"Buyurtma #{order_number} to'lov cheki"
        )
    elif order.get('receipt_file_type') == 'document':
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=order.get('receipt_file_id'),
            caption=f"Buyurtma #{order_number} to'lov cheki"
        )
    else:
        await query.message.reply_text("Bu buyurtma naqd pul orqali amalga oshirilgan, chek mavjud emas.")

async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_number = query.data.split('_')[1]
    orders = load_data(ORDERS_FILE)
    order = orders.get(order_number)

    if not order:
        await query.message.reply_text("Buyurtma topilmadi.")
        return

    order['status'] = 'approved'
    orders[order_number] = order
    save_data(ORDERS_FILE, orders)

    try:
        await query.message.edit_text(
            query.message.text + "\n\n✅ TASDIQLANDI"
        )
    except:
        pass

    try:
        await context.bot.send_message(
            chat_id=order['user_id'],
            text=f"✅ Buyurtmangiz tasdiqlandi!\n\n"
                 f"Buyurtma raqami: #{order_number}\n"
                 f"Kitob: {order['book_name']}\n\n"
                 f"Tez orada siz bilan bog'lanamiz!"
        )
    except Exception as e:
        logger.error(f"Mijozga xabar yuborishda xatolik: {e}")

async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_number = query.data.split('_')[1]
    orders = load_data(ORDERS_FILE)
    order = orders.get(order_number)

    if not order:
        await query.message.reply_text("Buyurtma topilmadi.")
        return

    order['status'] = 'rejected'
    orders[order_number] = order
    save_data(ORDERS_FILE, orders)

    try:
        await query.message.edit_text(
            query.message.text + "\n\n❌ BEKOR QILINDI"
        )
    except:
        pass

    try:
        await context.bot.send_message(
            chat_id=order['user_id'],
            text=f"❌ Buyurtmangiz bekor qilindi.\n\n"
                 f"Buyurtma raqami: #{order_number}\n"
                 f"Kitob: {order['book_name']}\n\n"
                 f"Qo'shimcha ma'lumot uchun biz bilan bog'laning."
        )
    except Exception as e:
        logger.error(f"Mijozga xabar yuborishda xatolik: {e}")

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_data(USERS_FILE)
    orders = load_data(ORDERS_FILE)
    books = load_data(BOOKS_FILE)

    pending = sum(1 for o in orders.values() if o.get('status') == 'pending')
    approved = sum(1 for o in orders.values() if o.get('status') == 'approved')
    rejected = sum(1 for o in orders.values() if o.get('status') == 'rejected')

    message = (
        f"📊 STATISTIKA\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"📚 Kitoblar: {len(books)}\n"
        f"📦 Jami buyurtmalar: {len(orders)}\n\n"
        f"⏳ Kutilayotgan: {pending}\n"
        f"✅ Tasdiqlangan: {approved}\n"
        f"❌ Bekor qilingan: {rejected}"
    )

    await update.message.reply_text(message)

async def show_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏳ Kutilayotgan", callback_data="orders_pending")],
        [InlineKeyboardButton("✅ Tasdiqlangan", callback_data="orders_approved")],
        [InlineKeyboardButton("❌ Bekor qilingan", callback_data="orders_rejected")],
        [InlineKeyboardButton("📋 Barcha buyurtmalar", callback_data="orders_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Qaysi buyurtmalarni ko'rmoqchisiz?",
        reply_markup=reply_markup
    )

async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    status_filter = query.data.split('_')[1]
    orders = load_data(ORDERS_FILE)

    if status_filter == 'all':
        filtered_orders = orders
        title = "📋 Barcha buyurtmalar"
    else:
        filtered_orders = {k: v for k, v in orders.items() if v.get('status') == status_filter}
        status_names = {'pending': '⏳ Kutilayotgan', 'approved': '✅ Tasdiqlangan', 'rejected': '❌ Bekor qilingan'}
        title = status_names.get(status_filter, "Buyurtmalar")

    if not filtered_orders:
        await query.message.reply_text("Buyurtmalar mavjud emas.")
        return

    # Har bir buyurtma uchun alohida xabar
    for order_num, order in filtered_orders.items():
        status_emoji = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}
        payment_text = "Click" if order.get('payment_method') == 'click' else "Naqd pul"
        
        message = (
            f"{status_emoji.get(order.get('status', ''), '❓')} Buyurtma #{order_num}\n"
            f"Mijoz: {order.get('user_name', '-')}\n"
            f"Telefon: {order.get('user_phone', '-')}\n"
            f"Manzil: {order.get('user_region', '-')}, {order.get('user_district', '-')}, {order.get('user_village', '-')}\n"
            f"Kitob: {order.get('book_name', '-')}\n"
            f"Narxi: {order.get('book_price', '-')} so'm\n"
            f"To'lov: {payment_text}\n"
            f"Sana: {order.get('order_date', '-')}\n"
        )
        
        # Inline tugmalar - faqat pending buyurtmalar uchun
        if order.get('status') == 'pending':
            keyboard = [
                [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{order_num}"),
                 InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject_{order_num}")]
            ]
            
            # Agar Click to'lovi bo'lsa, 3-tugma qo'shamiz
            if order.get('payment_method') == 'click' and order.get('receipt_file_id'):
                keyboard.insert(0, [InlineKeyboardButton("👁 Chekni ko'rish", callback_data=f"view_receipt_{order_num}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(message, reply_markup=reply_markup)
        else:
            await query.message.reply_text(message)

async def start_add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yangi kitob nomini kiriting:")
    return ADMIN_ADD_BOOK_NAME

async def get_book_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_book_name'] = update.message.text
    await update.message.reply_text("Kitob tasnifini (kategoriyasini) kiriting:")
    return ADMIN_ADD_BOOK_CATEGORY

async def get_book_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_book_category'] = update.message.text
    await update.message.reply_text("Kitob narxini kiriting (so'mda):")
    return ADMIN_ADD_BOOK_PRICE

async def get_book_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_book_price'] = update.message.text

    books = load_data(BOOKS_FILE)
    new_book_id = str(len(books) + 1)

    books[new_book_id] = {
        'name': context.user_data['new_book_name'],
        'category': context.user_data['new_book_category'],
        'price': context.user_data['new_book_price']
    }

    save_data(BOOKS_FILE, books)

    await update.message.reply_text(
        f"✅ Kitob muvaffaqiyatli qo'shildi!\n\n"
        f"Nomi: {books[new_book_id]['name']}\n"
        f"Kategoriya: {books[new_book_id]['category']}\n"
        f"Narxi: {books[new_book_id]['price']} so'm",
        reply_markup=admin_menu_keyboard()
    )

    return ConversationHandler.END

async def start_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data(USERS_FILE)
    profile = users.get(str(user.id), {})

    msg = (
        f"👤 Profilingiz:\n\n"
        f"Ism: {profile.get('name','-')}\n"
        f"Telefon: {profile.get('phone','-')}\n"
        f"Viloyat: {profile.get('region','-')}\n"
        f"Tuman: {profile.get('district','-')}\n"
        f"Qishloq: {profile.get('village','-')}\n\n"
        "Yangi ma'lumotlarni kiritish uchun ismingizni yozing (yoki eskisini takrorlang):"
    )
    await update.message.reply_text(msg)
    return PROFILE_EDIT_NAME

async def profile_edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profile_edit_name'] = update.message.text.strip()
    keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Yangi telefon raqamini yuboring yoki (agar o'zgarmasa) matn sifatida eskisini kiriting:", reply_markup=reply_markup)
    return PROFILE_EDIT_PHONE

async def profile_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    context.user_data['profile_edit_phone'] = phone
    await update.message.reply_text("Viloyatingizni kiriting:")
    return PROFILE_EDIT_REGION

async def profile_edit_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profile_edit_region'] = update.message.text.strip()
    await update.message.reply_text("Tuman nomini kiriting:")
    return PROFILE_EDIT_DISTRICT

async def profile_edit_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profile_edit_district'] = update.message.text.strip()
    await update.message.reply_text("Qishloq/mahalla nomini kiriting:")
    return PROFILE_EDIT_VILLAGE

async def profile_edit_village(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data(USERS_FILE)
    users.setdefault(str(user.id), {})
    users[str(user.id)]['name'] = context.user_data.get('profile_edit_name', users[str(user.id)].get('name',''))
    users[str(user.id)]['phone'] = context.user_data.get('profile_edit_phone', users[str(user.id)].get('phone',''))
    users[str(user.id)]['region'] = context.user_data.get('profile_edit_region', users[str(user.id)].get('region',''))
    users[str(user.id)]['district'] = context.user_data.get('profile_edit_district', users[str(user.id)].get('district',''))
    users[str(user.id)]['village'] = update.message.text.strip()
    save_data(USERS_FILE, users)

    await update.message.reply_text("✅ Profilingiz yangilandi.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ============= KARTA SOZLAMALARI =============

async def card_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Karta sozlamalarini ko'rsatish"""
    card_info = load_card_info()
    card_number = card_info.get('card_number', 'Kiritilmagan')
    card_owner = card_info.get('card_owner', 'Kiritilmagan')
    
    message = (
        f"💳 KARTA SOZLAMALARI\n\n"
        f"Karta raqami: {card_number}\n"
        f"Egasi: {card_owner}\n\n"
        f"Kartani tahrirlash uchun 'Kartani tahrirlash' tugmasini bosing."
    )
    
    keyboard = [
        [InlineKeyboardButton("✏️ Kartani tahrirlash", callback_data="edit_card")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def edit_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Karta tahrirlashni boshlash"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Clear any previous data
        if 'new_card_number' in context.user_data:
            del context.user_data['new_card_number']
        
        # Set conversation state
        context.user_data['in_conversation'] = True
        
        await query.message.reply_text(
            "💳 Yangi karta raqamini kiriting:\n"
            "(Masalan: 8600 1234 5678 9012)"
        )
        return ADMIN_CARD_NUMBER
    except Exception as e:
        print(f"Error in edit_card_start: {e}")
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(
                "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                reply_markup=admin_menu_keyboard()
            )
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        return ConversationHandler.END

async def get_card_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Karta raqamini qabul qilish"""
    try:
        if not update.message or not update.message.text:
            await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
            if 'in_conversation' in context.user_data:
                del context.user_data['in_conversation']
            return ConversationHandler.END
            
        card_number = update.message.text.strip()
        if not card_number:
            await update.message.reply_text("❌ Iltimos, karta raqamini kiriting!")
            return ADMIN_CARD_NUMBER
            
        context.user_data['new_card_number'] = card_number
        
        await update.message.reply_text(
            "👤 Karta egasining ismini kiriting:\n"
            "(Masalan: Azim Mullahonov)"
        )
        return ADMIN_CARD_OWNER
        
    except Exception as e:
        print(f"Error in get_card_number: {e}")
        if update.message:
            await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        return ConversationHandler.END

async def get_card_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Karta egasi ismini qabul qilish va saqlash"""
    try:
        if not update.message or not update.message.text:
            await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
            if 'in_conversation' in context.user_data:
                del context.user_data['in_conversation']
            return ConversationHandler.END
            
        card_owner = update.message.text.strip()
        if not card_owner:
            await update.message.reply_text("❌ Iltimos, karta egasining ismini kiriting!")
            return ADMIN_CARD_OWNER
            
        card_number = context.user_data.get('new_card_number', '')
        if not card_number:
            await update.message.reply_text("❌ Karta raqami topilmadi. Iltimos, qaytadan urinib ko'ring.")
            if 'in_conversation' in context.user_data:
                del context.user_data['in_conversation']
            return ConversationHandler.END
        
        # Saqlash
        save_card_info(card_number, card_owner)
        
        # Clear the stored data
        if 'new_card_number' in context.user_data:
            del context.user_data['new_card_number']
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        
        await update.message.reply_text(
            f"✅ Karta ma'lumotlari saqlandi!\n\n"
            f"💳 Karta: {card_number}\n"
            f"👤 Egasi: {card_owner}",
            reply_markup=admin_menu_keyboard()
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Error in get_card_owner: {e}")
        if update.message:
            await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        return ConversationHandler.END
    return ConversationHandler.END

async def back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin menyuga qaytish"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Clear conversation state
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        if 'new_card_number' in context.user_data:
            del context.user_data['new_card_number']
        
        await query.message.reply_text(
            "Admin paneli:",
            reply_markup=admin_menu_keyboard()
        )
        return ConversationHandler.END
    except Exception as e:
        print(f"Error in back_to_admin: {e}")
        if 'in_conversation' in context.user_data:
            del context.user_data['in_conversation']
        return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Skip if this is part of an active conversation
    if context.user_data.get('in_conversation'):
        return None
        
    text = update.message.text
    user_id = update.effective_user.id

    if user_id in ADMIN_ID:
        if text == '📊 Statistika':
            await show_statistics(update, context)
        elif text == '📦 Buyurtmalar':
            await show_orders_menu(update, context)
        elif text == '📚 Kitoblar ro\'yxati':
            await show_books(update, context)
        elif text == '💳 Karta sozlamalari':
            await card_settings(update, context)
        elif text == '👥 Foydalanuvchilar':
            users = load_data(USERS_FILE)
            message = f"👥 Foydalanuvchilar soni: {len(users)}\n\n"
            for uid, user in list(users.items())[:10]:
                message += f"• {user['name']} - {user['phone']}\n"
            await update.message.reply_text(message)
        elif text == '🔙 Orqaga':
            await update.message.reply_text("Asosiy menyu:", reply_markup=admin_menu_keyboard())
        elif text == '📚 Kitoblar':
            await show_books(update, context)
    else:
        if text == '📚 Kitoblar':
            await show_books(update, context)
        elif text == '📋 Mening buyurtmalarim':
            await my_orders(update, context)
        elif text == '👤 Profilni tahrirlash':
            return await start_profile_edit(update, context)
        elif text == 'ℹ️ Biz haqimizda':
            await update.message.reply_text(
                "📚 Kitob do'koni boti\n\n"
                "Bu bot orqali siz kitoblarni ko'rishingiz va buyurtma berishingiz mumkin.\n\n"
                "Savol va takliflar uchun biz bilan bog'laning."
            )

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    orders = load_data(ORDERS_FILE)

    if not orders:
        await update.message.reply_text("Sizda buyurtmalar mavjud emas.", reply_markup=main_menu_keyboard())
        return

    user_orders = {k: v for k, v in orders.items() if str(v.get('user_id')) == str(user.id) or v.get('user_id') == user.id}

    if not user_orders:
        await update.message.reply_text("Sizda buyurtmalar mavjud emas.", reply_markup=main_menu_keyboard())
        return

    message = "📦 Sizning buyurtmalaringiz:\n\n"
    status_emoji = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}
    for order_num, order in sorted(user_orders.items(), key=lambda x: int(x[0])):
        message += (
            f"{status_emoji.get(order.get('status', ''), '')} Buyurtma #{order_num}\n"
            f"Kitob: {order.get('book_name', 'Noma\'lum')}\n"
            f"Narxi: {order.get('book_price', '-')} so'm\n"
            f"Sana: {order.get('order_date', '-')}\n"
            f"Holat: {order.get('status', '-')}\n\n"
        )

    await update.message.reply_text(message[:4000], reply_markup=main_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Jarayon bekor qilindi.",
        reply_markup=main_menu_keyboard() if update.effective_user.id not in ADMIN_ID else admin_menu_keyboard()
    )
    return ConversationHandler.END

def main():
    TOKEN = "8232601370:AAGploAq_byjeWEJj9g2EtydsL0U_hRSw7w"

    init_books()

    application = Application.builder().token(TOKEN).build()

    register_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler((filters.CONTACT | filters.TEXT) & ~filters.COMMAND, get_phone)],
            PROFILE_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_region)],
            PROFILE_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_district)],
            PROFILE_VILLAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_village)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    order_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛒 Buyurtma berish'), start_order)],
        states={
            BOOK_SELECT: [CallbackQueryHandler(book_selected, pattern='^book_')],
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method_selected, pattern='^payment_')],
            PAYMENT_RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_received)],
            FEEDBACK: [
                CallbackQueryHandler(finish_order, pattern='^finish_order'),
                CallbackQueryHandler(leave_feedback, pattern='^leave_feedback'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_received)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    add_book_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ Yangi kitob qo\'shish'), start_add_book)],
        states={
            ADMIN_ADD_BOOK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_name)],
            ADMIN_ADD_BOOK_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_category)],
            ADMIN_ADD_BOOK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    edit_book_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_book_start, pattern='^editbook_')],
        states={
            EDIT_BOOK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_book_name)],
            EDIT_BOOK_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_book_category)],
            EDIT_BOOK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_book_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,
    )

    profile_edit_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^👤 Profilni tahrirlash'), start_profile_edit)],
        states={
            PROFILE_EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_name)],
            PROFILE_EDIT_PHONE: [MessageHandler((filters.CONTACT | filters.TEXT) & ~filters.COMMAND, profile_edit_phone)],
            PROFILE_EDIT_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_region)],
            PROFILE_EDIT_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_district)],
            PROFILE_EDIT_VILLAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_village)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    card_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_card_start, pattern='^edit_card$')],

        states={
            ADMIN_CARD_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_card_number)
            ],
            ADMIN_CARD_OWNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_card_owner)
            ],
        },

        fallbacks=[CallbackQueryHandler(back_to_admin, pattern='^back_admin$')]
    )

    application.add_handler(card_conv)

    application.add_handler(register_conv)
    application.add_handler(order_conv)
    application.add_handler(add_book_conv)
    application.add_handler(edit_book_conv)
    application.add_handler(profile_edit_conv)

    application.add_handler(CallbackQueryHandler(view_receipt, pattern='^view_receipt_'))
    application.add_handler(CallbackQueryHandler(approve_order, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(reject_order, pattern='^reject_'))
    application.add_handler(CallbackQueryHandler(list_orders, pattern='^orders_'))
    application.add_handler(CallbackQueryHandler(delete_book, pattern='^deletebook_'))
    application.add_handler(CallbackQueryHandler(edit_book_start, pattern='^editbook_'))
    
    # Add card settings handlers
    application.add_handler(CallbackQueryHandler(card_settings, pattern='^card_settings$'))
    application.add_handler(CallbackQueryHandler(back_to_admin, pattern='^back_admin$'))
    
    # Card edit conversation handler
    card_edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_card_start, pattern='^edit_card$')],
        states={
            ADMIN_CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_card_number)],
            ADMIN_CARD_OWNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_card_owner)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True
    )
    application.add_handler(card_edit_conv)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()