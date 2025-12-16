
@dp.message(Command("tasks"))
async def tasks(message: Message):
    response = requests.get("http://web:8000/api/tasks/")
    await message.answer(response.text)
