from aiogram.dispatcher.filters.state import State, StatesGroup

class ReminderStates(StatesGroup):
    """Состояния FSM."""
    waiting_for_time = State()