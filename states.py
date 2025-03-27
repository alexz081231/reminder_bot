from aiogram.dispatcher.filters.state import State, StatesGroup

class ReminderStates(StatesGroup):
    waiting_for_time = State() 