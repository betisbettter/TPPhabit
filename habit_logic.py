# habit_logic.py
from datetime import date, timedelta

CHALLENGE_START = date(2025, 5, 10)
CHALLENGE_END = date(2025, 6, 21)

habit_list = [
    "Move your body for 30 min",
    "Mother's day",
    "Track you workout",
    "Hit 7000 steps",
    "Take one form check video",
    "Train a neglected body part"
    "Stretch 10 min before bed",
    "10 min digestion walk",
    "Plan your meals for the week",
    "Eat 30g of protein in your first meal",
    "Drink 75 percent of body weight in fluid ounces",
    "Eat 2 different colors of fruit and veggies today",
    "Remove all processed foods",
    "Try one new healthy recipie or healthy option",
    "No phone for the first 30 min of the day",
    "3 things you are greatful for",
    "Set a 15-min timer for 1 hr. Write down what you did in each 15 min",
    "Read of listen to somehing that inspires you for 10 min",
    "Do 1 random act of kindness",
    "Do 1 thing that you have been avoiding",
    "Write down 3 lessons you learned of yourself this week",
    "Name the emotion you felt most last week",
    "Uncover 2 negative thoughts you've had, and reframe them",
    "Write a short note to someone you appreciate",
    "Spend 15 min doing something that makes you calm",
    "Take 5 physiological sighs each time you feel stressed",
    "Celebrate a small emotional win",
    "Forgive someone tofay or forgive youself",
    "Spend 5 min when you wake up for prayer or meditation",
    "Reflect: What does 'purpose' mean to you?",
    "Spend 20 min in nature",
    "Start a gratitude journal",
    "Do something that aligns with your core values",
    "Create a 3 line affirmation to speak into exisitance",
    "Celebrate your consistency",
    "Pick 2 habit from each week to carry on for this week",
    "Train without music or distraction today",
    "Teach someone else 1 thing that ou have learned from this challenge",
    "Revisit your 'Why'",
    "Do your hardest workout of the challenge",
    "Review your weak spots and adress 2 of them",
    "Commit to 2 goals for the next 30 days"
]

# Create a dictionary linking each date to a new habit
habit_by_date = {
    CHALLENGE_START + timedelta(days=i): habit_list[i]
    for i in range(len(habit_list))
}

def get_habits_for_date(target_date: date):
    """Returns all habits up to and including the given date."""
    if target_date < CHALLENGE_START or target_date > CHALLENGE_END:
        return []
    num_days = (target_date - CHALLENGE_START).days + 1
    return habit_list[:num_days]

def total_days():
    return len(habit_list)
