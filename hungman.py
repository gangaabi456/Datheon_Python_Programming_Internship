
import random
import sys
import textwrap
 
# Windows terminal-la ♥ ✔ ★ maadhiri symbols nalla theriya
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
 
# ---------- Settings ----------
MAX_ATTEMPTS = 6
W = 48  
 
words = [
    # Programming Languages
    {
        "word": "python",
        "category": "Programming Language",
        "hint": "A popular programming language",
        "fact": "Python was created by Guido van Rossum and first released in 1991."
    },
    {
        "word": "javascript",
        "category": "Programming Language",
        "hint": "A programming language commonly used for web development",
        "fact": "JavaScript was created by Brendan Eich in 1995 and is primarily used for client-side scripting."
    },
    {
        "word": "java",
        "category": "Programming Language",
        "hint": "A versatile programming language used for building applications",
        "fact": "Java was developed by James Gosling at Sun Microsystems and released in 1995."
    },
    {
        "word": "csharp",
        "category": "Programming Language",
        "hint": "A programming language developed by Microsoft",
        "fact": "C# (C-sharp) was created by Microsoft as part of its .NET initiative and was first released in 2000."
    },
    {
        "word": "ruby",
        "category": "Programming Language",
        "hint": "A dynamic programming language known for its simplicity",
        "fact": "Ruby was designed and developed by Yukihiro 'Matz' Matsumoto in the mid-1990s."
    },
    # Authors
    {
        "word": "tagore",
        "category": "Author",
        "hint": "First Asian to win the Nobel Prize in Literature",
        "fact": "Rabindranath Tagore won the Nobel Prize in 1913 and wrote India's national anthem."
    },
    {
        "word": "shakespeare",
        "category": "Author",
        "hint": "English playwright from Stratford-upon-Avon",
        "fact": "William Shakespeare wrote Hamlet, Macbeth and Romeo and Juliet."
    },
    {
        "word": "orwell",
        "category": "Author",
        "hint": "Wrote a famous novel about Big Brother",
        "fact": "George Orwell, whose real name was Eric Blair, wrote 1984 and Animal Farm."
    },
    # Seven Wonders
    {
        "word": "colosseum",
        "category": "Seven Wonders",
        "hint": "Ancient amphitheatre in Rome",
        "fact": "The Colosseum in Rome could hold around 50,000 spectators."
    },
    {
        "word": "petra",
        "category": "Seven Wonders",
        "hint": "Rose-red city carved into rock in Jordan",
        "fact": "Petra was built by the Nabataeans and is one of the New Seven Wonders of the World."
    },
    {
        "word": "giza",
        "category": "Seven Wonders",
        "hint": "Home of the Great Pyramid in Egypt",
        "fact": "The Great Pyramid of Giza is the only ancient wonder that still stands today."
    },
    # Important Places
    {
        "word": "everest",
        "category": "Important Place",
        "hint": "Highest mountain above sea level",
        "fact": "Mount Everest stands at about 8,849 metres."
    },
    {
        "word": "amazon",
        "category": "Important Place",
        "hint": "Largest tropical rainforest in the world",
        "fact": "The Amazon rainforest spreads across nine countries in South America."
    },
]
 
KEYBOARD_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
 
 
# ---------- Box helpers ----------
def banner(lines):
    """Double-line box (title, victory, defeat screens)."""
    print("╔" + "═" * W + "╗")
    for line in lines:
        print("║" + line.center(W) + "║")
    print("╚" + "═" * W + "╝")
 
 
def box_top(title):
    print("┌─ " + title + " " + "─" * (W - len(title) - 3) + "┐")
 
 
def box_line(text="", center=False):
    text = text.center(W) if center else text.ljust(W)
    print("│" + text + "│")
 
 
def box_bottom():
    print("└" + "─" * W + "┘")
 
 
# ---------- Game functions ----------
def get_masked_word(word, guessed_letters):
    """Guess panna letters-a kaattum, mathadhu '_' kaattum."""
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter.upper() + " "
        else:
            display += "_ "
    return display.strip()
 
 
def draw_gallows(wrong):
    """Thappu guess count-ku ethapadi gallows drawing."""
    head = "O" if wrong >= 1 else " "
    body = "|" if wrong >= 2 else " "
    left_arm = "/" if wrong >= 3 else " "
    right_arm = "\\" if wrong >= 4 else " "
    left_leg = "/" if wrong >= 5 else " "
    right_leg = "\\" if wrong >= 6 else " "
 
    print("        ┌───────┐")
    print("        │       │")
    print("        │       " + head)
    print("        │      " + left_arm + body + right_arm)
    print("        │      " + left_leg + " " + right_leg)
    print("        │")
    print("   ═════╧═════")
 
 
def draw_word_box(secret_word, guessed):
    box_top("WORD")
    box_line()
    box_line(get_masked_word(secret_word, guessed).replace(" ", "  "), center=True)
    box_line()
    box_bottom()
 
 
def draw_lives_box(wrong):
    left = MAX_ATTEMPTS - wrong
    hearts = "♥ " * left + "♡ " * wrong
    box_top("LIVES")
    box_line("   " + hearts.strip() + "        " + str(left) + " / " + str(MAX_ATTEMPTS) + " left")
    box_bottom()
 
 
def draw_hint_box(secret, wrong):
    box_top("HINT")
    box_line("  Category : " + secret["category"])
    if wrong >= MAX_ATTEMPTS - 1:
        box_line("  Clue     : " + secret["hint"][:W - 14])
    else:
        box_line("  Clue     : (unlocks on your last life...)")
    box_bottom()
 
 
def draw_keyboard(secret_word, guessed):
    box_top("KEYBOARD")
    box_line()
    for row in KEYBOARD_ROWS:
        cells = []
        for letter in row:
            if letter.lower() in guessed:
                if letter.lower() in secret_word:
                    cells.append("[" + letter + "]")   # correct
                else:
                    cells.append("-" + letter + "-")   # wrong
            else:
                cells.append(" " + letter + " ")       # innum guess pannala
        box_line(" ".join(cells), center=True)
    box_line()
    box_line("  [X] = correct letter      -X- = wrong letter")
    box_bottom()
 
 
def draw_screen(secret, guessed, wrong, message):
    print("\n" * 2)
    banner(["H A N G M A N   G A M E"])
    print()
    draw_gallows(wrong)
    print()
    draw_word_box(secret["word"], guessed)
    draw_lives_box(wrong)
    draw_hint_box(secret, wrong)
    draw_keyboard(secret["word"], guessed)
    print()
    if message:
        print("  " + message)
        print()
 
 
def get_valid_guess(guessed, secret_word):
    """Letter keppom. Returns (letter, message). Invalid/duplicate na letter None."""
    guess = input("  ➤ Enter a letter: ").strip().lower()
 
    if len(guess) != 1 or not guess.isalpha():
        return None, "⚠ Please enter a single letter (A-Z) only."
 
    if guess in guessed:
        return None, "⚠ You already guessed '" + guess.upper() + "'. No life lost, try another!"
 
    return guess, ""
 
 
def show_result(won, secret, wrong):
    print("\n")
    if won:
        left = MAX_ATTEMPTS - wrong
        banner([
            "★  Y O U   W I N !  ★",
            "",
            "The word was  " + " ".join(secret["word"].upper()),
            "Lives left: " + "♥ " * left,
        ])
    else:
        banner([
            "✖  G A M E   O V E R  ✖",
            "",
            "The word was  " + " ".join(secret["word"].upper()),
            "Better luck next time!",
        ])
 
    print()
    print("  Did you know?")
    for line in textwrap.wrap(secret["fact"], W):
        print("  " + line)
    print()
 
 
def play_game():
    secret = random.choice(words)
    secret_word = secret["word"]
    guessed_letters = set()
    wrong_guesses = 0
    won = False
    message = ""
 
    while wrong_guesses < MAX_ATTEMPTS:
        draw_screen(secret, guessed_letters, wrong_guesses, message)
 
        guess, message = get_valid_guess(guessed_letters, secret_word)
        if guess is None:          # invalid / duplicate: penalty illa
            continue
 
        guessed_letters.add(guess)
 
        if guess in secret_word:
            message = "✔ Great! '" + guess.upper() + "' is in the word."
        else:
            wrong_guesses += 1
            message = "✘ Oops! '" + guess.upper() + "' is not in the word."
 
        if "_" not in get_masked_word(secret_word, guessed_letters):
            won = True
            break
 
    show_result(won, secret, wrong_guesses)
 
 
# ---------- Program start ----------
if __name__ == "__main__":
    while True:
        play_game()
        again = input("  Play again? (y/n): ").strip().lower()
        if again != "y":
            print("\n  Thanks for playing! 👋\n")
            break

