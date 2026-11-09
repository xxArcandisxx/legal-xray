SAMPLE_TEXT = """RENTAL AGREEMENT

This agreement is made between Mr. R. Sharma (Landlord) and the Tenant for the property at 12, 3rd Cross, Indiranagar, Bengaluru.

1. Rent is Rs 25,000 per month, payable by the 1st of each month.
2. The tenant shall pay a security deposit of Rs 3,00,000, which is non-refundable if the tenant vacates before 24 months.
3. The landlord may increase the rent by 20% every year at his sole discretion.
4. The landlord or his representatives may enter the premises at any time without prior notice.
5. The tenant shall pay all repair and maintenance costs, including structural repairs.
6. A penalty of Rs 1,000 per day will be charged for any delay in rent payment.
7. The tenant must give 3 months' notice to vacate, while the landlord may ask the tenant to vacate with 7 days' notice."""


def t(en, hi, kn):
    return {"en": en, "hi": hi, "kn": kn}


SAMPLE_RESULT = {
    "doc_type": "Rental agreement",
    "overall_risk": 78,
    "summary": t(
        "This agreement heavily favours the landlord. The deposit, rent hikes, entry and notice rules could cost you money and peace of mind.",
        "यह समझौता मकान मालिक के पक्ष में बहुत झुका है। डिपॉज़िट, किराया बढ़ोतरी, घर में प्रवेश और नोटिस के नियम आपको पैसे और मानसिक शांति का नुकसान करा सकते हैं।",
        "ಈ ಒಪ್ಪಂದ ಮಾಲೀಕರ ಪರವಾಗಿ ಹೆಚ್ಚು ಇದೆ. ಠೇವಣಿ, ಬಾಡಿಗೆ ಹೆಚ್ಚಳ, ಮನೆ ಪ್ರವೇಶ ಮತ್ತು ಸೂಚನೆಯ ನಿಯಮಗಳು ನಿಮ್ಮ ಹಣ ಮತ್ತು ನೆಮ್ಮದಿಗೆ ಹಾನಿ ಮಾಡಬಹುದು."),
    "clauses": [
        {"quote": "non-refundable if the tenant vacates before 24 months", "risk": "high", "category": "Deposit",
         "why_risky": t("You could lose your entire ₹3,00,000 deposit if you move out in the first two years, even for a good reason.",
                        "अगर आप पहले दो साल में घर छोड़ते हैं तो आपका पूरा ₹3,00,000 का डिपॉज़िट डूब सकता है, चाहे वजह कुछ भी हो।",
                        "ಮೊದಲ ಎರಡು ವರ್ಷಗಳಲ್ಲಿ ಮನೆ ಖಾಲಿ ಮಾಡಿದರೆ ನಿಮ್ಮ ₹3,00,000 ಠೇವಣಿ ಪೂರ್ತಿ ಕಳೆದುಕೊಳ್ಳಬಹುದು, ಕಾರಣ ಏನೇ ಇದ್ದರೂ."),
         "negotiate": t("Ask to refund the deposit minus actual damages, or limit any deduction to one month's rent.",
                        "डिपॉज़िट से केवल वास्तविक नुकसान काटकर बाकी वापस करने को कहें, या कटौती एक महीने के किराए तक सीमित करें।",
                        "ನಿಜವಾದ ಹಾನಿಯನ್ನು ಮಾತ್ರ ಕಡಿತಗೊಳಿಸಿ ಉಳಿದ ಠೇವಣಿ ಹಿಂದಿರುಗಿಸಲು ಕೇಳಿ, ಅಥವಾ ಕಡಿತವನ್ನು ಒಂದು ತಿಂಗಳ ಬಾಡಿಗೆಗೆ ಮಿತಿಗೊಳಿಸಿ.")},
        {"quote": "increase the rent by 20% every year at his sole discretion", "risk": "high", "category": "Rent increase",
         "why_risky": t("A 20% hike every year is very steep and the landlord decides alone, so your rent could jump suddenly.",
                        "हर साल 20% बढ़ोतरी बहुत ज़्यादा है और फ़ैसला सिर्फ़ मकान मालिक का है, इसलिए किराया अचानक बढ़ सकता है।",
                        "ಪ್ರತಿ ವರ್ಷ 20% ಹೆಚ್ಚಳ ತುಂಬಾ ಹೆಚ್ಚು, ಮತ್ತು ನಿರ್ಧಾರ ಮಾಲೀಕರದ್ದೇ, ಹಾಗಾಗಿ ಬಾಡಿಗೆ ಏಕಾಏಕಿ ಹೆಚ್ಚಾಗಬಹುದು."),
         "negotiate": t("Ask for a fixed yearly increase of 5-8%, agreed in writing, instead of 'sole discretion'.",
                        "'अपनी मर्ज़ी' की जगह लिखित में हर साल 5-8% की तय बढ़ोतरी माँगें।",
                        "'ಸ್ವಂತ ವಿವೇಚನೆ' ಬದಲು ಲಿಖಿತವಾಗಿ ವರ್ಷಕ್ಕೆ 5-8% ನಿಗದಿತ ಹೆಚ್ಚಳ ಕೇಳಿ.")},
        {"quote": "enter the premises at any time without prior notice", "risk": "high", "category": "Privacy",
         "why_risky": t("The landlord can walk into your home any time with no warning, which hurts your privacy and safety.",
                        "मकान मालिक बिना बताए कभी भी आपके घर में आ सकता है, जो आपकी निजता और सुरक्षा के लिए ठीक नहीं है।",
                        "ಮಾಲೀಕರು ಯಾವುದೇ ಸೂಚನೆ ಇಲ್ಲದೆ ಯಾವಾಗ ಬೇಕಾದರೂ ಮನೆಗೆ ಬರಬಹುದು, ಇದು ನಿಮ್ಮ ಗೌಪ್ಯತೆ ಮತ್ತು ಸುರಕ್ಷತೆಗೆ ಅಪಾಯ."),
         "negotiate": t("Ask for at least 24 hours' notice, and entry only at reasonable hours or in emergencies.",
                        "कम से कम 24 घंटे पहले सूचना और केवल उचित समय या आपात स्थिति में प्रवेश की शर्त माँगें।",
                        "ಕನಿಷ್ಠ 24 ಗಂಟೆ ಮುಂಚಿನ ಸೂಚನೆ ಮತ್ತು ಸೂಕ್ತ ಸಮಯದಲ್ಲಿ ಅಥವಾ ತುರ್ತು ಸಂದರ್ಭದಲ್ಲಿ ಮಾತ್ರ ಪ್ರವೇಶ ಎಂದು ಕೇಳಿ.")},
        {"quote": "A penalty of Rs 1,000 per day will be charged for any delay in rent payment", "risk": "medium", "category": "Late penalty",
         "why_risky": t("₹1,000 a day is about 4% of a month's rent for every day you are late, which adds up very fast.",
                        "₹1,000 प्रतिदिन यानी हर देरी के दिन पर महीने के किराए का लगभग 4%, जो बहुत जल्दी बढ़ जाता है।",
                        "ದಿನಕ್ಕೆ ₹1,000 ಎಂದರೆ ತಡವಾದ ಪ್ರತಿ ದಿನಕ್ಕೆ ತಿಂಗಳ ಬಾಡಿಗೆಯ ಸುಮಾರು 4%, ಇದು ಬಹಳ ಬೇಗ ಹೆಚ್ಚಾಗುತ್ತದೆ."),
         "negotiate": t("Ask for a 5-day grace period and a small capped late fee, like 1-2% of the rent.",
                        "5 दिन की छूट और किराए के 1-2% जैसी सीमित लेट फ़ीस माँगें।",
                        "5 ದಿನಗಳ ರಿಯಾಯಿತಿ ಮತ್ತು ಬಾಡಿಗೆಯ 1-2% ರಂತೆ ಮಿತಿಯುಳ್ಳ ವಿಳಂಬ ಶುಲ್ಕ ಕೇಳಿ.")},
        {"quote": "the landlord may ask the tenant to vacate with 7 days' notice", "risk": "high", "category": "Notice period",
         "why_risky": t("You must give 3 months' notice but the landlord can ask you to leave in 7 days, so you could be forced out suddenly.",
                        "आपको 3 महीने का नोटिस देना है, लेकिन मकान मालिक सिर्फ़ 7 दिन में घर खाली करवा सकता है।",
                        "ನೀವು 3 ತಿಂಗಳ ಸೂಚನೆ ನೀಡಬೇಕು, ಆದರೆ ಮಾಲೀಕರು ಕೇವಲ 7 ದಿನಗಳಲ್ಲಿ ಖಾಲಿ ಮಾಡಲು ಹೇಳಬಹುದು."),
         "negotiate": t("Ask for the same notice period for both sides, ideally 1-2 months.",
                        "दोनों पक्षों के लिए समान नोटिस अवधि माँगें, बेहतर होगा 1-2 महीने।",
                        "ಎರಡೂ ಪಕ್ಷಗಳಿಗೆ ಒಂದೇ ಸೂಚನಾ ಅವಧಿ ಕೇಳಿ, ಸೂಕ್ತವಾಗಿ 1-2 ತಿಂಗಳು.")},
    ],
}
