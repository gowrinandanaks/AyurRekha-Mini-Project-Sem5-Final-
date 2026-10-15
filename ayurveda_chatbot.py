"""
DocAyu - Ayurveda AI Assistant
Responds to Ayurveda-related queries with guidance. Uses knowledge base;
optional OpenAI integration can be added via settings.
"""
import re
import random
from django.conf import settings

DISCLAIMER = " ⚠️ I am an Ayurvedic assistant, not a physician. I help you learn about Ayurveda. Always consult a qualified Ayurvedic practitioner or doctor for medical advice."

# Ayurveda knowledge base: keywords -> responses
KNOWLEDGE = [
    # Doshas
    (r"\b(vata|vatha)\b", [
        "Vata is the dosha of air and space. Vata types are often creative, quick-thinking, and energetic. Balancing tips: warm, grounding foods; regular routine; oil massage (Abhyanga); avoid cold, raw foods.",
        "Vata governs movement. To balance Vata: eat warm, moist, nourishing foods; maintain a calm routine; practice gentle yoga; stay warm.",
    ]),
    (r"\b(pitta|pitha)\b", [
        "Pitta represents fire and water. Pitta types tend to be intense, focused, and driven. Balancing tips: cool foods; avoid spicy; favor sweet, bitter, astringent tastes; practice cooling pranayama.",
        "Pitta governs digestion and transformation. To balance Pitta: eat cooling foods; avoid overheating; favor coconut, cucumber; practice moderation.",
    ]),
    (r"\b(kapha|kafa)\b", [
        "Kapha is earth and water. Kapha types are calm, nurturing, and strong. Balancing tips: light, warm, stimulating foods; regular exercise; avoid heavy, oily foods.",
        "Kapha governs structure and lubrication. To balance Kapha: favor light, warm, dry foods; stay active; avoid excess sleep and heavy foods.",
    ]),
   
    (r"\bdosha\b", [
        "The three doshas—Vata, Pitta, Kapha—form your unique constitution (Prakriti). Take our Dosha Quiz to discover yours!",
    ]),
    (r"\b(what is ayurveda)\b", [
        "Ayurveda is an ancient system of natural medicine that started in India more than 5,000 years ago.It focuses on keeping the body, mind, and spirit healthy and balanced using natural methods like healthy food, herbs, yoga, and daily lifestyle habits.The main goal of Ayurveda is to prevent illness and promote overall well-being. 🌿",
    ]),
     (r"\b(ayurveda help in keep body and mind calm|body and mind calm)\b", [
        "Ayurveda helps keep the mind and body calm by promoting balance in daily life.*It encourages healthy food and proper digestion.*It recommends yoga and pranayama to relax the body.*It recommends yoga and pranayama to relax the body.*It recommends yoga and pranayama to relax the body.",
    ]),
    # Diet
    (r"\b(diet|food|eat|eating)\b", [
        "Ayurveda says: eat according to your dosha, favor seasonal foods, and eat mindfully. Warm food aids digestion.",
        "Eat when hungry; avoid overeating. Favor fresh, whole foods. Lunch is the main meal when digestion is strongest.",
    ]),
    (r"\b(digestion|digest|agni)\b", [
        "Agni (digestive fire) is key in Ayurveda. Strengthen it with: ginger tea, warm water, regular meals, and avoiding cold drinks with meals.",
    ]),
    # Herbs
    (r"\b(turmeric|haldi)\b", [
        "Turmeric (Haridra) is anti-inflammatory, supports digestion, and purifies blood. Use in warm milk (golden milk) or with meals.",
    ]),
    (r"\b(tulsi|holy basil)\b", [
        "Tulsi (Holy Basil) supports immunity, respiration, and stress. Make tea with fresh leaves for a calming effect.",
    ]),
    (r"\b(ginger|adrak)\b", [
        "Ginger (Adrak) kindles Agni, aids digestion, and relieves nausea. Add to tea or meals.",
    ]),
    
    (r"\b(triphala)\b", [
        "Triphala supports digestion, detoxification, and regularity. Often taken at night with warm water.",
    ]),
    (r"\b(ashwagandha)\b", [
        "Ashwagandha supports energy, sleep, and stress resilience. It is grounding—good for Vata.",
    ]),
     (r"\b(three doshas|tridosha)\b", [
        "In Ayurveda, there are three doshas that control how the body works: vata,pitta,kapha.#Vata – controls movement like breathing and blood flow,#Pitta – controls digestion and body heat.#Kapha – controls strength, stability, and body structure.Every person has all three doshas, but one or two are usually stronger. Keeping them balanced helps maintain good health. 🌿",
    ]),
    
    
    # Practices
    (r"\b(yoga|asana)\b", [
        "Yoga aligns body and mind. Sunrise is ideal for practice. Match asanas to your dosha: grounding for Vata, cooling for Pitta, stimulating for Kapha.",
    ]),
    (r"\b(pranayama|pranayama for heart health)\b", [
        "Pranayama is good for heart health because it helps the body and mind relax.It improves oxygen supply to the body through better breathing.It improves blood circulation",
        "pranayama reduces stress, which lowers strain on the heart."
    ]),
    (r"\b(pranayama types|types of pranayama)\b", [
        "#Anulom Vilom – Helps improve blood circulation and calm the mind.#Bhramari – Reduces stress and helps relax the heart.#Deep Breathing (Dirga Pranayama) – Helps the body get more oxygen and relax.",
    ]),
    (r"\b(anulom Vilom)\b", [
        "Anulom Vilom is a type of pranayama (breathing exercise) in yoga where you breathe in through one nostril and breathe out through the other.In this practice, you close one nostril with your finger, inhale through the open nostril, then switch and exhale through the other nostril.It helps to calm the mind, reduce stress, improve breathing, and balance the body’s energy. Practicing it regularly can support overall health and relaxation. 🌿🫁",
    ]),
    (r"\b(meditation|meditate)\b", [
        "Meditation balances the mind. Even 10 minutes daily helps. Pitta benefits from cooling visualization; Vata from grounding.",
    ]),
    (r"\b(abhyanga|oil massage)\b", [
        "Abhyanga is self-massage with warm oil. It calms Vata, nourishes the skin, and promotes relaxation. Best in the morning.",
    ]),
    (r"\b(dinacharya|daily routine)\b", [
        "Dinacharya: wake before sunrise, scrape tongue, drink warm water, evacuate, oil massage if possible, then yoga/meditation. Align with natural rhythms.",
    ]),
    # General
    (r"\b(hello|hi|namaste|hey)\b", [
        "Namaste! I'm DocAyu, your Ayurvedic assistant. Ask me about doshas, diet, herbs, yoga, or wellness tips.",
    ]),
    (r"\b(thank|thanks)\b", [
        "You're welcome! May you find balance and wellness. Feel free to ask more anytime.",
    ]),
    (r"\b(help|what can you)\b", [
        "I can help with: doshas (Vata, Pitta, Kapha), diet tips, herbs (turmeric, tulsi, ashwagandha), daily routine (Dinacharya), yoga, and general Ayurvedic wellness.",
    ]),
    
]


def get_ayurveda_response(user_message: str, conversation_history: list) -> str:
    """
    Generate an Ayurveda-focused response using the knowledge base.
    Falls back to a helpful default if no match.
    """
    msg_lower = user_message.lower().strip()
    if not msg_lower:
        return "Please type your question. I can help with doshas, diet, herbs, yoga, and Ayurvedic wellness." + DISCLAIMER

    matched_responses = []
    for pattern, responses in KNOWLEDGE:
        if re.search(pattern, msg_lower, re.IGNORECASE):
            matched_responses.extend(responses)

    if matched_responses:
        reply = random.choice(matched_responses)
    else:
        defaults = [
            "Ayurveda focuses on balance of body, mind, and spirit. You could ask about doshas, diet, herbs like turmeric or tulsi, yoga, or daily routine (Dinacharya).",
            "I'm here to share Ayurvedic tips. Try asking about your dosha, digestion, herbs, or wellness practices.",
        ]
        reply = random.choice(defaults) + DISCLAIMER

    return reply
