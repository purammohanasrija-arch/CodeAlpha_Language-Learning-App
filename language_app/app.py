from flask import Flask, render_template, request, jsonify
from firebase_config import db

app = Flask(__name__)

# ── English lessons data ────────────────────────────────────────────────────
LOCAL_LESSONS = {
    "vocabulary": [
        {"word": "Hello",       "meaning": "A greeting",              "pronunciation": "HEH-loh",         "example": "Hello! How are you?"},
        {"word": "Thank you",   "meaning": "Express gratitude",       "pronunciation": "THANK-yoo",        "example": "Thank you for your help."},
        {"word": "Goodbye",     "meaning": "Farewell greeting",       "pronunciation": "good-BYE",         "example": "Goodbye! See you tomorrow."},
        {"word": "Please",      "meaning": "Polite request word",     "pronunciation": "PLEEZ",            "example": "Please pass me the water."},
        {"word": "Sorry",       "meaning": "Apology expression",      "pronunciation": "SOH-ree",          "example": "I am sorry for being late."},
        {"word": "Beautiful",   "meaning": "Very attractive/pleasing","pronunciation": "BYOO-tih-ful",     "example": "What a beautiful day!"},
        {"word": "Important",   "meaning": "Of great significance",   "pronunciation": "im-POR-tant",      "example": "This is very important."},
        {"word": "Understand",  "meaning": "To comprehend meaning",   "pronunciation": "un-der-STAND",     "example": "Do you understand me?"},
        {"word": "Wonderful",   "meaning": "Extremely good",          "pronunciation": "WUN-der-ful",      "example": "You did a wonderful job!"},
        {"word": "Expensive",   "meaning": "Costs a lot of money",    "pronunciation": "ek-SPEN-siv",      "example": "This phone is expensive."},
    ],
    "grammar": [
        {"word": "I am happy",         "meaning": "Present state of being", "pronunciation": "eye am HAP-ee",          "example": "I am happy today."},
        {"word": "She is reading",     "meaning": "Present continuous tense","pronunciation": "shee iz REE-ding",       "example": "She is reading a book."},
        {"word": "They were late",     "meaning": "Simple past tense",       "pronunciation": "thay wer LAYT",          "example": "They were late to class."},
        {"word": "He will come",       "meaning": "Simple future tense",     "pronunciation": "hee wil KUM",            "example": "He will come tomorrow."},
        {"word": "We have eaten",      "meaning": "Present perfect tense",   "pronunciation": "wee hav EE-ten",         "example": "We have eaten already."},
        {"word": "Can you help me?",   "meaning": "Asking for assistance",   "pronunciation": "kan yoo HELP mee",       "example": "Can you help me please?"},
        {"word": "I would like...",    "meaning": "Polite way to request",   "pronunciation": "eye wood LYK",           "example": "I would like some water."},
        {"word": "There is / There are","meaning": "Indicating existence",   "pronunciation": "thair iz / thair ar",    "example": "There is a cat here."},
    ],
    "phrases": [
        {"word": "How are you?",           "meaning": "Asking about someone's wellbeing",  "pronunciation": "how ar YOO",              "example": "How are you today?"},
        {"word": "What is your name?",     "meaning": "Asking someone's name",             "pronunciation": "wot iz yor NAYM",         "example": "What is your name?"},
        {"word": "Where are you from?",    "meaning": "Asking about origin",               "pronunciation": "wair ar yoo FRUM",        "example": "Where are you from?"},
        {"word": "I don't understand",     "meaning": "Saying you are confused",           "pronunciation": "eye dohnt un-der-STAND",  "example": "Sorry, I don't understand."},
        {"word": "Could you repeat that?", "meaning": "Ask to say something again",        "pronunciation": "kood yoo ri-PEET that",   "example": "Could you repeat that please?"},
        {"word": "How much does it cost?", "meaning": "Asking the price",                  "pronunciation": "how much duz it KOST",    "example": "How much does it cost?"},
        {"word": "Nice to meet you",       "meaning": "Greeting when first meeting",       "pronunciation": "nys to MEET yoo",         "example": "Nice to meet you, John!"},
        {"word": "I need help",            "meaning": "Requesting assistance",             "pronunciation": "eye need HELP",           "example": "I need help with this."},
    ],
    "sentences": [
        {"word": "The weather is nice today.",      "meaning": "Comment on good weather",      "pronunciation": "thuh WEH-ther iz nys tuh-DAY",          "example": "The weather is nice today. Let's go outside."},
        {"word": "I would like to order food.",     "meaning": "Ordering at a restaurant",     "pronunciation": "eye wood lyk to OR-der FOOD",           "example": "I would like to order food, please."},
        {"word": "Could you show me the way?",      "meaning": "Asking for directions",        "pronunciation": "kood yoo shoh mee thuh WAY",            "example": "Could you show me the way to the station?"},
        {"word": "I enjoy learning English.",       "meaning": "Expressing enjoyment",         "pronunciation": "eye en-JOY LER-ning ING-glish",         "example": "I enjoy learning English every day."},
        {"word": "She works very hard.",            "meaning": "Describing effort/dedication", "pronunciation": "shee wurks VEH-ree HARD",               "example": "She works very hard at her job."},
        {"word": "We should leave early.",          "meaning": "Giving a suggestion",          "pronunciation": "wee shood LEEV ER-lee",                 "example": "We should leave early to avoid traffic."},
    ],
}

QUIZ_QUESTIONS = [
    # Vocabulary
    {"question": "Which word means 'a greeting'?",              "options": ["Goodbye","Hello","Sorry","Please"],        "answer": "Hello",        "category": "vocabulary"},
    {"question": "What does 'expensive' mean?",                 "options": ["Very cheap","Very fast","Costs a lot","Very easy"],"answer": "Costs a lot","category": "vocabulary"},
    {"question": "Which word is used to apologise?",            "options": ["Please","Thank you","Sorry","Hello"],      "answer": "Sorry",        "category": "vocabulary"},
    {"question": "How do you pronounce 'beautiful'?",           "options": ["beh-OOT-ful","BYOO-tih-ful","boo-TEE-ful","BEE-yoo-ful"],"answer": "BYOO-tih-ful","category": "vocabulary"},
    # Grammar
    {"question": "Which is correct present continuous tense?",  "options": ["She read","She is reading","She reads","She readed"],"answer": "She is reading","category": "grammar"},
    {"question": "Which sentence is in simple past tense?",     "options": ["They are late","They will be late","They were late","They have been late"],"answer": "They were late","category": "grammar"},
    {"question": "What is the polite way to make a request?",   "options": ["I want...","Give me...","I would like...","I need..."], "answer": "I would like...","category": "grammar"},
    {"question": "Which uses present perfect tense?",           "options": ["We eat","We ate","We have eaten","We eating"],"answer": "We have eaten","category": "grammar"},
    # Phrases
    {"question": "How do you ask someone's name in English?",   "options": ["How are you?","What is your name?","Where are you from?","Nice to meet you"],"answer": "What is your name?","category": "phrases"},
    {"question": "What do you say when you don't understand?",  "options": ["I need help","I don't understand","Could you repeat?","How much?"],"answer": "I don't understand","category": "phrases"},
    {"question": "How do you ask for the price of something?",  "options": ["Where are you from?","How are you?","How much does it cost?","Can you help?"],"answer": "How much does it cost?","category": "phrases"},
    {"question": "What do you say when meeting someone new?",   "options": ["Goodbye","How much?","Nice to meet you","I need help"],"answer": "Nice to meet you","category": "phrases"},
    # Sentences
    {"question": "Which sentence is used for ordering food?",   "options": ["The weather is nice.","I would like to order food.","Could you show me the way?","We should leave early."],"answer": "I would like to order food.","category": "sentences"},
    {"question": "How do you ask for directions?",              "options": ["I enjoy learning English.","She works very hard.","Could you show me the way?","I need help"],"answer": "Could you show me the way?","category": "sentences"},
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/lessons")
def lessons():
    category = request.args.get("category", "vocabulary")
    try:
        docs = db.collection("lessons").where("category", "==", category).stream()
        lesson_list = [doc.to_dict() for doc in docs]
        if not lesson_list:
            lesson_list = LOCAL_LESSONS.get(category, LOCAL_LESSONS["vocabulary"])
    except Exception:
        lesson_list = LOCAL_LESSONS.get(category, LOCAL_LESSONS["vocabulary"])
    return render_template("lessons.html", lessons=lesson_list, category=category,
                           categories=list(LOCAL_LESSONS.keys()))

@app.route("/flashcards")
def flashcards():
    category = request.args.get("category", "vocabulary")
    lesson_list = LOCAL_LESSONS.get(category, LOCAL_LESSONS["vocabulary"])
    return render_template("flashcards.html", lessons=lesson_list, category=category,
                           categories=list(LOCAL_LESSONS.keys()))

@app.route("/quiz")
def quiz():
    import json
    category = request.args.get("category", "all")
    if category == "all":
        questions = QUIZ_QUESTIONS
    else:
        questions = [q for q in QUIZ_QUESTIONS if q["category"] == category]
    return render_template("quiz.html", questions=json.dumps(questions), category=category,
                           categories=list(LOCAL_LESSONS.keys()))

@app.route("/progress")
def progress():
    return render_template("progress.html")

@app.route("/api/save_progress", methods=["POST"])
def save_progress():
    data = request.get_json()
    try:
        db.collection("progress").document("user_progress").set(data, merge=True)
        return jsonify({"status": "saved_firebase"})
    except Exception:
        return jsonify({"status": "saved_local"})

@app.route("/api/get_progress")
def get_progress():
    try:
        doc = db.collection("progress").document("user_progress").get()
        if doc.exists:
            return jsonify(doc.to_dict())
    except Exception:
        pass
    return jsonify({"quizzes_taken": 0, "best_score": 0, "lessons_viewed": [], "flashcards_done": 0})

if __name__ == "__main__":
    app.run(debug=True)
