# Telegram bot with the maze game

This is a project for the subject “High-Level Interpreted Programming Language” within the 2nd year of RTU MIREA.

По идее во время игры нужно использовать Reply клавиатуру, потому что ее распложение удобнее. Однако для игровых кнопок была выбрана Inline клавиатура, так как в процессе игры мы изменяем отправленное сообщение, в то время как пользователь ничего не отправляет в чат (иначе сообщение сдвиниться наверх в чате, или пришлось бы отправлять каждый раз новое сообщение с обновленным игровым полем, что не очень красиво).

### Sources
maze: https://habr.com/ru/articles/262345/

lambda: https://habr.com/ru/companies/piter/articles/674234/

sqlite3: https://pyneng.readthedocs.io/ru/latest/book/25_db/sqlite3.html