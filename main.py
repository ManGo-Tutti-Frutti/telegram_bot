import logging
from random import randint
from PIL import Image
from io import BytesIO
from aiogram import Bot, Dispatcher, executor, types
from data import db_session
from data.users import User


API_TOKEN = '5900412050:AAGXme_konhsN-DfxLkulnCGqTA37X7JGXk'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def generate_image(colors):
    image = Image.new("RGB", (512, 512), colors)
    bio = BytesIO()
    bio.name = 'image.jpeg'
    image.save(bio, 'JPEG')
    bio.seek(0)
    return bio


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    db_sess = db_session.create_session()
    if not db_sess.query(User).filter(User.username == message.chat.id).first():
        user = User()
        user.username = message.chat.id
        db_sess.add(user)
        db_sess.commit()
    await message.reply("Здравствуйте! Я RGB-tester! С моей помощью Вы сможете генерировать цвета со случайными " +
                        "значениями, а также проверить, насколько хорошо Вы можете определять цвета. Для того " +
                        "чтобы получить список команд напишите /help")


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("Вот список того, на что я способен:\n\t/random_color - сгенерировать случайный цвет" +
                        "\n\t/guess - проверить Ваши умения" +
                        "\n\t/completed_colours - узнать угаданное количество цветов" +
                        "\n\t/failed_colours - узнать неугаданное количество цветов" +
                        "\n\t/create - сгенерировать заданный цвет"
                        "\n\nВ ближайшее время должно появиться ещё больше функций" +
                        ", так что не забывайте заходить почаще!")


@dp.message_handler(commands=['random_color'])
async def c(message: types.Message):
    r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
    img = generate_image((r, g, b))
    await bot.send_photo(chat_id=message.chat.id, photo=img, caption="Был сгенерирован цвет со значениями "
                                                                     f"{r}, {g}, {b}")


@dp.message_handler(commands=['completed_colours'])
async def c_cols(message: types.Message):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == message.chat.id).first()
    await message.answer(f'Пока что Вы угадали количество цветов: {user.completed_colours}.\n\n' +
                         'Но это ведь не предел ваших возможностей? Продолжайте в том же духе и совсем скоро Вы ' +
                         "выучите все цвета виде rgb наизусть ;)")


@dp.message_handler(commands=['failed_colours'])
async def f_cols(message: types.Message):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == message.chat.id).first()
    await message.answer('В попытках разгадать загадку цветового спектра Вы не угадали количество цветов: ' +
                         f'{user.failed_colours}.\n\nНе расстраивайтесь, ведь это только начала Вашего путешествия ' +
                         "в мире цвета!")


@dp.message_handler(commands=['create'])
async def guess(message: types.Message):
    if open("start_create_colour.txt").read() == "0":
        open("start_create_colour.txt", "w").write("1")
        await message.answer("Введите, пожалуйста, цвет в формате RGB. Например:\n20, 50, 40\nИ ждите результат!")


@dp.message_handler()
async def sekond(message: types.Message):
    if open("start_create_colour.txt").read() == "1":
        spisokchek = message.text.split(', ')
        r = int(spisokchek[0])
        g = int(spisokchek[1])
        b = int(spisokchek[2])
        img = generate_image((r, g, b))
        open("start_create_colour.txt", "w").write("0")
        await bot.send_photo(chat_id=message.chat.id, photo=img, caption="Был сгенерирован цвет со значениями " +
                                                                         f'{r}, {g}, {b}')


@dp.message_handler(commands=['guess'])
async def guess(message: types.Message):
    if open("waiting_for_answer.txt").read() == "0":
        color_list = list()
        while len(color_list) != 3:
            r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
            if (r, g, b) not in color_list:
                color_list.append((r, g, b))
        ans = randint(0, 2) + 1
        open("answer.txt", "w").write(str(ans))
        open("waiting_for_answer.txt", "w").write("1")
        await bot.send_photo(chat_id=message.chat.id, photo=generate_image(color_list[ans - 1]),
                             caption="Какому из этих цветовых значений соответствует данная картинка?\n\n" +
                                     f"  1. {color_list[0]}\n" + f"  2. {color_list[1]}\n" + f"  3. {color_list[2]}\n" +
                                     "\nВ качестве ответа отправьте цифру, под которой (по Вашему мнению)" +
                                     " указано правильное цветовое значение")
    else:
        await message.answer("От Вас всё ещё ожидается ответ на вопрос")


@dp.message_handler()
async def answer(message: types.Message):
    if open("waiting_for_answer.txt").read() == "1":
        if message.text == open("answer.txt").read():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == message.chat.id).first()
            user.completed_colours = user.completed_colours + 1
            db_sess.commit()
            await message.answer("Мои поздравления, Вы угадали!\n\nЕсли хотите попробовать свои силы ещё раз, " +
                                 "просто введите команду\n/guess ещё раз!")
        else:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == message.chat.id).first()
            user.failed_colours = user.failed_colours + 1
            db_sess.commit()
            await message.answer("Мои соболезнования, Вы не угадали...\n\nЕсли хотите попробовать свои силы ещё раз, " +
                                 "просто введите команду\n/guess ещё раз!")
        open("waiting_for_answer.txt", "w").write("0")
    else:
        if int(message.text) in range(1, 4):
            await message.answer("От Вас пока что не ожидается ответ на вопрос. Если Вы хотите начать, используйте " +
                                 "команду /guess")
        else:
            await message.answer(f'Я получил сообщение "{message.text}", но я не знаю как на него отвечать :(\n\n' +
                                 'Лучше воспользуйтесь теми командами, которые я знаю (их можно получить с помощью ' +
                                 'команды /help)')


if __name__ == '__main__':
    db_session.global_init("db/rgb_tester.db")
    executor.start_polling(dp, skip_updates=True)
