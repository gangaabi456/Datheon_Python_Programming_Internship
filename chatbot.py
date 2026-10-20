

import json
import random
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

W = 64                                    # box width
BOT_NAME = "NovaBot"
STORE = "TechNova Electronics"
FAQ_FILE = Path(__file__).resolve().parent / "faq.json"

EXIT_PATTERN = re.compile(r"\b(bye|exit|quit|goodbye)\b")
NO_PATTERN = re.compile(r"^(no|nope|nah|nothing|nothing else|that'?s all|no thanks|no thank you|i'?m (good|done)|done)$")
MORE_PATTERN = re.compile(r"^(more|tell me more|more details|details|elaborate|go on)$")
NAME_PATTERN = re.compile(r"\bmy name is ([a-z]+)")
ORDER_ID_PATTERN = re.compile(r"#?\b(\d{5,8})\b")


def hours_reply(message):
    """Ippo open-aa closed-aa nu time paathu sollum."""
    now = datetime.now()
    open_now = now.weekday() < 6 and 9 <= now.hour < 18      # Mon-Sat, 9 AM - 6 PM
    status = "We are OPEN right now. 🟢" if open_now else "We are CLOSED right now. 🔴"
    return ("Our business hours:\n"
            "  Mon - Sat : 9:00 AM - 6:00 PM\n"
            "  Sunday    : Closed\n\n" + status)


def order_reply(message):
    match = ORDER_ID_PATTERN.search(message)
    if match:
        return ("Order #" + match.group(1) + " is being processed and will be shipped "
                "within 24 hours. You will get a tracking link by email. (demo reply)")
    return ("I can help you track your order! Please type your order number "
            "(for example: order status #12345).")


INTENTS = {
    "greeting": {
        "patterns": [r"\b(hi+|hello+|hey+|vanakkam|namaste)\b", r"\bgood (morning|afternoon|evening)\b"],
        "responses": ["Hello! Welcome to " + STORE + ". How can I help you today?",
                      "Hi there! I'm " + BOT_NAME + ". Ask me anything about our store."],
    },
    "hours": {
        "patterns": [r"\b(hours?|timings?|timing)\b", r"\b(open|opening|close|closing|closed)\b",
                     r"\bwhat time\b", r"\bworking days?\b"],
        "handler": hours_reply,
        "more": "Holiday timings are announced on our website. Online orders are accepted 24/7.",
    },
    "products": {
        "patterns": [r"\b(products?|items?|catalog(ue)?)\b", r"\b(laptops?|phones?|mobiles?|smartphones?)\b",
                     r"\b(headphones?|earbuds?|smartwatch(es)?|watch(es)?)\b", r"\b(sell|selling|buy|stock)\b"],
        "responses": ["We sell laptops, smartphones, headphones, smartwatches and accessories "
                      "from top brands."],
        "more": "Popular picks: Student laptops, 5G smartphones, noise-cancelling headphones "
                "and fitness smartwatches.",
    },
    "pricing": {
        "patterns": [r"\b(price|prices|pricing|cost|costs|how much|rate|cheap|cheapest)\b",
                     r"\b(discount|offers?|deals?|sale|coupon)\b"],
        "responses": ["Prices start at Rs. 999 for accessories, Rs. 8,999 for smartphones and "
                      "Rs. 29,999 for laptops. Check our weekly offers for discounts!"],
        "more": "Students get an extra 5% discount with a valid ID card.",
    },
    "shipping": {
        "patterns": [r"\b(shipping|delivery|deliver|delivered|ship|shipped|courier)\b",
                     r"\bhow long\b", r"\bfree delivery\b"],
        "responses": ["Delivery takes 3-5 working days. Shipping is FREE on orders above Rs. 999."],
        "more": "Express delivery (1-2 days) is available in metro cities for Rs. 99.",
    },
    "order_status": {
        "patterns": [r"\border\b", r"\b(track|tracking|status)\b", r"\bwhere is my\b"],
        "handler": order_reply,
        "min_score": 1,
    },
    "returns": {
        "patterns": [r"\b(return|returns|refund|refunds|exchange|replace|replacement)\b",
                     r"\bmoney back\b", r"\bcancel(lation)?\b"],
        "responses": ["You can return any product within 7 days of delivery if it is unused and "
                      "in original packaging. Refunds reach you in 5-7 working days."],
        "more": "To start a return, email support with your order number and reason.",
    },
    "warranty": {
        "patterns": [r"\b(warranty|guarantee|repair|repairs|service centre|service center|defect(ive)?)\b"],
        "responses": ["All products come with a 1-year manufacturer warranty. "
                      "Extended 2-year warranty is available at checkout."],
        "more": "Warranty does not cover physical or water damage.",
    },
    "payment": {
        "patterns": [r"\b(pay|payment|payments|upi|card|cards|emi|cod|cash on delivery|net banking)\b"],
        "responses": ["We accept UPI, credit/debit cards, net banking, EMI and Cash on Delivery."],
        "more": "No-cost EMI is available on orders above Rs. 10,000.",
    },
    "contact": {
        "patterns": [r"\b(contact|phone|call|email|mail|address|location|human|agent|support)\b",
                     r"\b(talk to|speak to)\b"],
        "responses": ["You can reach our support team:\n"
                      "  Email : support@technova.example\n"
                      "  Phone : 1800-000-0000 (toll free)\n"
                      "  Hours : Mon - Sat, 9 AM - 6 PM"],
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank you|thankyou|thx|nandri|great|awesome|nice)\b"],
        "responses": ["You're welcome! 😊", "Happy to help!"],
    },
    "about_bot": {
        "patterns": [r"\bwho are you\b", r"\byour name\b", r"\bwhat can you do\b", r"\bhelp\b"],
        "responses": ["I'm " + BOT_NAME + ", the virtual assistant of " + STORE + ". "
                      "I can help with business hours, products, prices, shipping, orders, "
                      "returns, warranty, payments and contact details."],
    },
}

FALLBACKS = [
    "Sorry, I didn't quite get that. Could you rephrase it?",
    "Hmm, I'm not sure about that. Can you ask in a different way?",
]

TOPIC_MENU = ("I can help with these topics:\n"
              "  • Business hours      • Products\n"
              "  • Prices & offers     • Shipping & delivery\n"
              "  • Order status        • Returns & refunds\n"
              "  • Warranty            • Payment options\n"
              "  • Contact support\n\n"
              "Try typing one of them!")


def banner(lines):
    print("╔" + "═" * W + "╗")
    for line in lines:
        print("║" + line.center(W) + "║")
    print("╚" + "═" * W + "╝")


def bot_say(text):
    """Bot-oda reply-a box-la azhagaa kaattum (long lines auto wrap aagum)."""
    print()
    print("┌─ " + BOT_NAME + " " + "─" * (W - len(BOT_NAME) - 3) + "┐")
    for paragraph in text.split("\n"):
        wrapped = textwrap.wrap(paragraph, W - 4, subsequent_indent="  ") if paragraph.strip() else [""]
        for line in wrapped:
            print("│ " + line.ljust(W - 1) + "│")
    print("└" + "─" * W + "┘")
    print()


def compile_patterns(patterns):
    compiled = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error:
            compiled.append(re.compile(re.escape(pattern)))   # thappu regex-na plain text-a eduthukkum
    return compiled


STOP_WORDS = {"what", "when", "where", "which", "does", "have", "with", "your", "about",
              "can", "how", "the", "are", "you", "for", "and", "this", "that", "from", "will"}


def load_faq_file(path):
    """Optional faq.json-a padichu INTENTS-la serkkum."""
    if not path.exists():
        return 0
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        print("  ⚠ faq.json padikka mudiyala, built-in answers mattum use aagum.")
        return 0

    if isinstance(data, dict):
        for key in ("faqs", "questions", "data", "intents"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break

    added = 0
    if isinstance(data, dict):                                  # Format B
        for name, item in data.items():
            if isinstance(item, dict) and "patterns" in item and "responses" in item:
                INTENTS["json_" + name] = {"patterns": item["patterns"], "responses": item["responses"]}
                added += 1
    elif isinstance(data, list):                                # Format A
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            question = str(item.get("question", item.get("q", "")))
            answer = str(item.get("answer", item.get("a", "")))
            if not question or not answer:
                continue
            words = [w for w in re.findall(r"[a-z0-9]+", question.lower())
                     if len(w) > 3 and w not in STOP_WORDS]
            if not words:
                continue
            INTENTS["faq_" + str(index)] = {
                "patterns": [r"\b" + re.escape(w) + r"\b" for w in words],
                "responses": [answer],
                "min_score": 2 if len(words) > 1 else 1,
            }
            added += 1
    return added


def prepare_intents():
    for intent in INTENTS.values():
        intent["compiled"] = compile_patterns(intent["patterns"])


def normalize(text):
    """lowercase + strip + punctuation remove + extra spaces remove."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9#'\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_intents(message):
    """Matching intents list return pannum (best score mudhalla)."""
    results = []
    for name, intent in INTENTS.items():
        score = sum(1 for pattern in intent["compiled"] if pattern.search(message))
        if score >= intent.get("min_score", 1):
            results.append((score, name))

    results.sort(key=lambda item: -item[0])
    names = [name for _, name in results]

    if len(names) > 1:
        names = [n for n in names if n not in ("greeting", "thanks")] or names
    return names[:3]


def build_reply(names, message, user_name):
    parts = []
    for name in names:
        intent = INTENTS[name]
        if "handler" in intent:
            parts.append(intent["handler"](message))
        else:
            text = random.choice(intent["responses"])
            if name == "greeting" and user_name:
                text = "Hello " + user_name.title() + "! How can I help you today?"
            parts.append(text)
    return "\n\n".join(parts)


def farewell(user_name):
    who = " " + user_name.title() if user_name else ""
    bot_say("Thank you for chatting with " + STORE + "," + who + "! Have a great day. 👋")


def main():
    prepare_intents()
    extra = load_faq_file(FAQ_FILE)
    if extra:
        prepare_intents()

    print()
    banner(["", B_TITLE, "", "Type 'bye', 'exit' or 'quit' to leave", ""])

    state = "greeting"        
    user_name = ""
    last_intent = None
    fallback_count = 0

    bot_say("Hello! I'm " + BOT_NAME + ", the virtual assistant of " + STORE + ".\n"
            "Ask me about business hours, products, prices, shipping, orders, returns or warranty.")
    state = "identify"

    while True:
        try:
            raw = input("  You ▸ ")
        except (EOFError, KeyboardInterrupt):
            print()
            farewell(user_name)
            break

        message = normalize(raw)

        if not message:
            print("  ⚠ Please type something.")
            continue

        if EXIT_PATTERN.search(message):
            farewell(user_name)
            break

        if state == "resolution" and NO_PATTERN.match(message):
            farewell(user_name)
            break

        name_match = NAME_PATTERN.search(message)
        if name_match:
            user_name = name_match.group(1)
            bot_say("Nice to meet you, " + user_name.title() + "! How can I help you today?")
            state = "identify"
            continue

        if MORE_PATTERN.match(message):
            if last_intent and "more" in INTENTS[last_intent]:
                bot_say(INTENTS[last_intent]["more"] + "\n\nAnything else I can help with?")
            else:
                bot_say("What would you like to know more about? Try asking about hours, "
                        "products, shipping or returns.")
            state = "resolution"
            continue

        names = match_intents(message)

        if not names:
            fallback_count += 1
            if fallback_count >= 2:
                bot_say(random.choice(FALLBACKS) + "\n\n" + TOPIC_MENU)
            else:
                bot_say(random.choice(FALLBACKS))
            if fallback_count >= 3:
                bot_say("If you still need help, our team is happy to assist:\n"
                        "  Email : support@technova.example\n  Phone : 1800-000-0000")
            continue

        fallback_count = 0
        reply = build_reply(names, message, user_name)
        last_intent = names[0]

        if names[0] in ("greeting", "thanks"):
            state = "identify" if names[0] == "greeting" else "resolution"
            bot_say(reply)
        else:
            state = "resolution"
            bot_say(reply + "\n\nAnything else I can help with?")


B_TITLE = "N O V A B O T  -  S U P P O R T   A S S I S T A N T"

if __name__ == "__main__":
    main()