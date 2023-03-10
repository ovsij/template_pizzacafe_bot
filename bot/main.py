from aiogram.utils import executor
import logging

from loader import dp

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
)
sys.path.append(PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    from handlers import dp
    from database.crud import import_test_db
    import_test_db(227184505)
    executor.start_polling(dp, skip_updates=True)