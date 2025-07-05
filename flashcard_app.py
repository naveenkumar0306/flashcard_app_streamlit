import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta

FLASHCARD_FILE = "flashcards.json"

# ----------------- Utility Functions -----------------

def load_flashcards():
    if os.path.exists(FLASHCARD_FILE):
        with open(FLASHCARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_flashcards(cards):
    with open(FLASHCARD_FILE, "w") as f:
        json.dump(cards, f, indent=2)

def add_flashcard(question, answer):
    today = datetime.today().date().isoformat()
    new_card = {
        "question": question,
        "answer": answer,
        "interval": 1,
        "next_review": today,
        "correct_count": 0
    }
    cards = load_flashcards()
    cards.append(new_card)
    save_flashcards(cards)

def get_due_cards():
    today = datetime.today().date()
    return [card for card in load_flashcards() if datetime.strptime(card["next_review"], "%Y-%m-%d").date() <= today]

def update_card(card, correct=True):
    if correct:
        card["correct_count"] += 1
        card["interval"] *= 2
    else:
        card["correct_count"] = 0
        card["interval"] = 1
    card["next_review"] = (datetime.today().date() + timedelta(days=card["interval"])).isoformat()

    cards = load_flashcards()
    for i, c in enumerate(cards):
        if c["question"] == card["question"]:
            cards[i] = card
            break
    save_flashcards(cards)

def delete_flashcard(index):
    cards = load_flashcards()
    if 0 <= index < len(cards):
        del cards[index]
        save_flashcards(cards)

# ----------------- Streamlit App -----------------

st.set_page_config(page_title="Flashcards", page_icon="📚")
st.title("📚 Flashcard Learning App")

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add a Flashcard", 
    "📖 Review Flashcards", 
    "🎯 Quiz Mode", 
    "📋 All Flashcards"
])

# ----------------- Add Flashcard Tab -----------------

with tab1:
    st.subheader("Add a Flashcard")
    with st.form("add_flashcard_form", clear_on_submit=True):
        question = st.text_input("Question", key="new_question")
        answer = st.text_input("Answer", key="new_answer")
        submitted = st.form_submit_button("Add Flashcard")
        if submitted:
            if question.strip() and answer.strip():
                add_flashcard(question.strip(), answer.strip())
                st.success("✅ Flashcard added.")
            else:
                st.warning("⚠️ Please enter both question and answer.")

# ----------------- Review Flashcards Tab -----------------

with tab2:
    st.subheader("Review Due Flashcards")
    due_cards = get_due_cards()
    if due_cards:
        card = random.choice(due_cards)
        st.write(f"**Question:** {card['question']}")
        if "show_answer" not in st.session_state:
            st.session_state.show_answer = False
        if st.button("Show Answer"):
            st.session_state.show_answer = True
        if st.session_state.show_answer:
            st.markdown(f"**Answer:** {card['answer']}")
            col1, col2 = st.columns(2)
            if col1.button("✅ I knew this"):
                update_card(card, correct=True)
                st.session_state.show_answer = False
                st.rerun()
            if col2.button("❌ I forgot"):
                update_card(card, correct=False)
                st.session_state.show_answer = False
                st.rerun()
    else:
        st.success("🎉 No flashcards are due for review today.")

# ----------------- Quiz Mode Tab -----------------

with tab3:
    st.subheader("Quiz Mode")
    cards = load_flashcards()
    if cards:
        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = random.randint(0, len(cards) - 1)
            st.session_state.quiz_feedback = None
        quiz_card = cards[st.session_state.quiz_index]
        st.write(f"**Question:** {quiz_card['question']}")
        user_answer = st.text_input("Your Answer", key="quiz_input")
        if st.button("Check Answer"):
            correct_answer = quiz_card["answer"].strip().lower()
            user_input = user_answer.strip().lower()
            if user_input == correct_answer:
                st.session_state.quiz_feedback = "✅ Correct!"
            else:
                st.session_state.quiz_feedback = f"❌ Incorrect. Correct answer: {quiz_card['answer']}"
        if st.session_state.get("quiz_feedback"):
            st.write(st.session_state.quiz_feedback)
            if st.button("Next Question"):
                st.session_state.quiz_index = random.randint(0, len(cards) - 1)
                st.session_state.quiz_feedback = None
                st.session_state.quiz_input = ""
                st.rerun()
    else:
        st.warning("No flashcards available. Add some first.")

# ----------------- All Flashcards Tab -----------------

with tab4:
    st.subheader("📋 All Flashcards")
    cards = load_flashcards()
    if cards:
        for index, card in enumerate(cards):
            with st.expander(f"📝 {card['question']}"):
                st.markdown(f"**Answer:** {card['answer']}")
                st.markdown(f"**Correct Count:** {card['correct_count']}")
                st.markdown(f"**Interval:** {card['interval']} days")
                st.markdown(f"**Next Review:** {card['next_review']}")
                if st.button("🗑️ Delete", key=f"delete_{index}"):
                    delete_flashcard(index)
                    st.success("✅ Flashcard deleted.")
                    st.rerun()
    else:
        st.info("No flashcards available yet.")
