"""
Multilingual spoken-summary templates for TTS.

Two template sets:
  SEVERITY_TEXT_SHORT — concise (3-4 sentences) for TTS synthesis on CPU.
                        Kept short so parler-tts can generate in ~15-30 seconds.
  SEVERITY_TEXT_FULL  — detailed first-aid guidance for on-screen display
                        (used if we add a "show full guidance" UI feature later).

WHY THIS EXISTS: tts.py's `language` param only picks a VOICE, it does not
translate text. severity_class and antivenom_required are ENUMS, so we can
safely pre-translate every combination as a fixed lookup table.

⚠️ IMPORTANT: these translations were drafted by Claude, not reviewed by a
native speaker. Have a Telugu/Hindi/Tamil/Kannada speaker verify wording
accuracy before relying on this in any real triage use.
"""

SEVERITY_TEXT = {
    "en": {
        "LOW": (
            "Attention. This is a Smart Snakebite diagnostic report. "
            "The risk level is LOW. The bite appears non-venomous. "
            "Wash the wound with clean water and soap. Apply a clean bandage. "
            "Do not cut the wound or apply a tourniquet. "
            "Monitor the patient for twenty four hours. "
            "If swelling, numbness, or breathing difficulty appears, go to a hospital immediately."
        ),
        "MODERATE": (
            "Attention. This is a Smart Snakebite diagnostic report. "
            "The risk level is MODERATE. The patient shows signs of mild envenomation. "
            "Hospital treatment is needed within two hours. "
            "Keep the patient calm and still. Remove rings and watches near the bite. "
            "Immobilize the bitten limb with a splint. "
            "Do not apply ice, tourniquet, or cut the wound. "
            "Do not give aspirin. Transport to the nearest hospital now."
        ),
        "HIGH": (
            "Warning. This is an urgent Smart Snakebite report. "
            "The risk level is HIGH. The patient shows significant envenomation symptoms. "
            "The patient must reach a hospital within thirty minutes. "
            "Keep the patient completely still. Do not let them walk. "
            "Remove all jewelry near the bite. Do not apply a tourniquet or herbal remedies. "
            "Call an ambulance immediately. Every minute matters. "
            "Inform the hospital in advance to prepare antivenom."
        ),
        "CRITICAL": (
            "Emergency alert. This is a critical Smart Snakebite report. "
            "The risk level is CRITICAL. The patient is in immediate danger. "
            "Call an ambulance right now. Do not wait even one minute. "
            "Keep the patient lying down and completely still. "
            "If breathing stops, begin mouth to mouth resuscitation. "
            "Monitor airway, breathing, and pulse continuously. "
            "The patient needs ICU care with ventilator support urgently. "
            "Do not attempt any traditional remedies. Act now to save the life."
        ),
    },
    "te": {
        "LOW": (
            "శ్రద్ధ. ఇది స్మార్ట్ స్నేక్‌బైట్ నివేదిక. "
            "ప్రమాద స్థాయి తక్కువ. కాటు విషం లేని పాము నుండి అయి ఉండవచ్చు. "
            "గాయాన్ని శుభ్రమైన నీటితో కడగండి. శుభ్రమైన బ్యాండేజ్ వేయండి. "
            "గాయాన్ని కోయకండి. టోర్నిక్వెట్ వేయకండి. "
            "రోగిని ఇరవై నాలుగు గంటల పాటు పర్యవేక్షించండి. "
            "వాపు లేదా శ్వాస ఇబ్బంది వస్తే వెంటనే ఆసుపత్రికి వెళ్ళండి."
        ),
        "MODERATE": (
            "శ్రద్ధ. ఇది స్మార్ట్ స్నేక్‌బైట్ నివేదిక. "
            "ప్రమాద స్థాయి మధ్యస్థం. రెండు గంటల్లో ఆసుపత్రి చికిత్స అవసరం. "
            "రోగిని ప్రశాంతంగా ఉంచండి. కాటు దగ్గర ఉంగరాలు తీసేయండి. "
            "కాటు వేసిన అవయవాన్ని స్ప్లింట్ వేసి స్థిరం చేయండి. "
            "మంచు లేదా టోర్నిక్వెట్ వేయకండి. గాయాన్ని కోయకండి. "
            "రోగిని వెంటనే సమీపంలోని ఆసుపత్రికి తరలించండి."
        ),
        "HIGH": (
            "హెచ్చరిక. ఇది అత్యవసర స్నేక్‌బైట్ నివేదిక. "
            "ప్రమాద స్థాయి ఎక్కువ. ముప్పై నిమిషాల్లో ఆసుపత్రికి చేరాలి. "
            "రోగిని పూర్తిగా నిశ్చలంగా ఉంచండి. నడవనివ్వకండి. "
            "టోర్నిక్వెట్ వేయకండి. మూలికా ఔషధాలు వేయకండి. "
            "వెంటనే అంబులెన్స్ పిలవండి. ప్రతి నిమిషం ముఖ్యం. "
            "ఆసుపత్రికి ముందే ఫోన్ చేసి యాంటీవెనమ్ సిద్ధం చేయమని చెప్పండి."
        ),
        "CRITICAL": (
            "అత్యవసర హెచ్చరిక. ప్రమాద స్థాయి అత్యంత తీవ్రం. "
            "రోగి తక్షణ ప్రమాదంలో ఉన్నారు. ఇప్పుడే అంబులెన్స్ పిలవండి. ఆగకండి. "
            "రోగిని పడుకోబెట్టండి. నిలబడనివ్వకండి. "
            "శ్వాస ఆగితే నోటి ద్వారా శ్వాస అందించండి. "
            "రోగికి ఐసీయూ మరియు యాంటీవెనమ్ అత్యవసరంగా అవసరం. "
            "సంప్రదాయ వైద్యం ప్రయత్నించకండి. వెంటనే చర్య తీసుకోండి."
        ),
    },
    "hi": {
        "LOW": (
            "ध्यान दीजिए। यह स्मार्ट स्नेकबाइट रिपोर्ट है। "
            "जोखिम स्तर कम है। काटने वाला सांप विषहीन प्रतीत होता है। "
            "घाव को साफ पानी और साबुन से धोएं। साफ पट्टी बांधें। "
            "घाव में चीरा न लगाएं। टूर्निकेट न बांधें। "
            "मरीज़ को चौबीस घंटे तक निगरानी में रखें। "
            "सूजन या सांस लेने में तकलीफ हो तो तुरंत अस्पताल जाएं।"
        ),
        "MODERATE": (
            "ध्यान दीजिए। यह स्मार्ट स्नेकबाइट रिपोर्ट है। "
            "जोखिम स्तर मध्यम है। दो घंटे के भीतर अस्पताल में इलाज ज़रूरी है। "
            "मरीज़ को शांत रखें। काटने की जगह से अंगूठियां हटाएं। "
            "काटे गए अंग को स्प्लिंट से स्थिर करें। "
            "बर्फ या टूर्निकेट न लगाएं। घाव में चीरा न लगाएं। "
            "मरीज़ को तुरंत नज़दीकी अस्पताल ले जाएं।"
        ),
        "HIGH": (
            "चेतावनी। यह ज़रूरी स्नेकबाइट रिपोर्ट है। "
            "जोखिम स्तर उच्च है। तीस मिनट के भीतर अस्पताल पहुंचना ज़रूरी है। "
            "मरीज़ को बिल्कुल हिलने न दें। चलने न दें। "
            "टूर्निकेट न बांधें। जड़ी-बूटी न लगाएं। "
            "तुरंत एम्बुलेंस बुलाएं। हर मिनट कीमती है। "
            "अस्पताल को पहले से फोन करके एंटीवेनम तैयार रखने को कहें।"
        ),
        "CRITICAL": (
            "आपातकालीन चेतावनी। जोखिम स्तर अत्यंत गंभीर है। "
            "मरीज़ तत्काल खतरे में है। अभी एम्बुलेंस बुलाएं। एक पल भी न रुकें। "
            "मरीज़ को लिटा दें। खड़े न होने दें। "
            "सांस रुके तो मुंह से सांस दें। "
            "मरीज़ को आईसीयू और एंटीवेनम तुरंत चाहिए। "
            "झाड़-फूंक न कराएं। अभी कार्रवाई करें।"
        ),
    },
    "ta": {
        "LOW": (
            "கவனிக்கவும். இது ஸ்மார்ட் ஸ்னேக்பைட் அறிக்கை. "
            "ஆபத்து நிலை குறைவு. கடித்தது விஷமற்ற பாம்பாக இருக்கலாம். "
            "காயத்தை சுத்தமான நீரால் கழுவுங்கள். சுத்தமான கட்டு போடுங்கள். "
            "காயத்தை வெட்டாதீர்கள். டூர்னிக்வெட் வைக்காதீர்கள். "
            "நோயாளியை இருபத்தி நான்கு மணி நேரம் கண்காணிக்கவும். "
            "வீக்கம் அல்லது சுவாச சிரமம் ஏற்பட்டால் உடனே மருத்துவமனைக்குச் செல்லவும்."
        ),
        "MODERATE": (
            "கவனிக்கவும். இது ஸ்மார்ட் ஸ்னேக்பைட் அறிக்கை. "
            "ஆபத்து நிலை மிதமானது. இரண்டு மணி நேரத்திற்குள் மருத்துவமனை சிகிச்சை தேவை. "
            "நோயாளியை அமைதியாக வையுங்கள். கடி அருகே மோதிரங்கள் அகற்றுங்கள். "
            "கடிக்கப்பட்ட அங்கத்தை ஸ்ப்ளிண்ட் மூலம் நிலைப்படுத்துங்கள். "
            "பனிக்கட்டி அல்லது டூர்னிக்வெட் வைக்காதீர்கள். "
            "நோயாளியை உடனே அருகிலுள்ள மருத்துவமனைக்கு அழைத்துச் செல்லுங்கள்."
        ),
        "HIGH": (
            "எச்சரிக்கை. இது அவசர ஸ்னேக்பைட் அறிக்கை. "
            "ஆபத்து நிலை அதிகம். முப்பது நிமிடங்களுக்குள் மருத்துவமனை சேர வேண்டும். "
            "நோயாளியை நடக்க விடாதீர்கள். முழுமையாக அசையாமல் வையுங்கள். "
            "டூர்னிக்வெட் வைக்காதீர்கள். மூலிகை மருந்துகள் போடாதீர்கள். "
            "உடனடியாக ஆம்புலன்ஸ் அழைக்கவும். ஒவ்வொரு நிமிடமும் முக்கியம். "
            "மருத்துவமனைக்கு முன்கூட்டியே தெரிவித்து ஆண்டிவெனம் தயார் செய்யச் சொல்லுங்கள்."
        ),
        "CRITICAL": (
            "அவசர எச்சரிக்கை. ஆபத்து நிலை மிகவும் கடுமையானது. "
            "நோயாளி உடனடி ஆபத்தில் உள்ளார். இப்போதே ஆம்புலன்ஸ் அழைக்கவும். காத்திருக்க வேண்டாம். "
            "நோயாளியை படுக்க வையுங்கள். நிற்க விடாதீர்கள். "
            "சுவாசம் நின்றால் வாய் வழி சுவாசம் கொடுங்கள். "
            "நோயாளிக்கு ஐசியூ மற்றும் ஆண்டிவெனம் உடனடியாக தேவை. "
            "பாரம்பரிய மருத்துவம் முயற்சிக்காதீர்கள். இப்போதே செயல்படுங்கள்."
        ),
    },
    "kn": {
        "LOW": (
            "ಗಮನಿಸಿ. ಇದು ಸ್ಮಾರ್ಟ್ ಸ್ನೇಕ್‌ಬೈಟ್ ವರದಿ. "
            "ಅಪಾಯದ ಮಟ್ಟ ಕಡಿಮೆ. ಕಡಿದ ಹಾವು ವಿಷವಿಲ್ಲದ ಹಾವಾಗಿರಬಹುದು. "
            "ಗಾಯವನ್ನು ಶುದ್ಧ ನೀರಿನಿಂದ ತೊಳೆಯಿರಿ. ಶುಚಿ ಬ್ಯಾಂಡೇಜ್ ಹಾಕಿ. "
            "ಗಾಯ ಕತ್ತರಿಸಬೇಡಿ. ಟೂರ್ನಿಕ್ವೆಟ್ ಹಾಕಬೇಡಿ. "
            "ರೋಗಿಯನ್ನು ಇಪ್ಪತ್ತನಾಲ್ಕು ಗಂಟೆ ಗಮನಿಸಿ. "
            "ಊತ ಅಥವಾ ಉಸಿರಾಟ ತೊಂದರೆ ಕಂಡರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ."
        ),
        "MODERATE": (
            "ಗಮನಿಸಿ. ಇದು ಸ್ಮಾರ್ಟ್ ಸ್ನೇಕ್‌ಬೈಟ್ ವರದಿ. "
            "ಅಪಾಯದ ಮಟ್ಟ ಮಧ್ಯಮ. ಎರಡು ಗಂಟೆಗಳಲ್ಲಿ ಆಸ್ಪತ್ರೆ ಚಿಕಿತ್ಸೆ ಅಗತ್ಯ. "
            "ರೋಗಿಯನ್ನು ಶಾಂತವಾಗಿ ಇಡಿ. ಕಡಿತದ ಬಳಿ ಉಂಗುರ ತೆಗೆಯಿರಿ. "
            "ಕಡಿಸಿದ ಅಂಗವನ್ನು ಸ್ಪ್ಲಿಂಟ್ ಮೂಲಕ ಸ್ಥಿರಪಡಿಸಿ. "
            "ಐಸ್ ಅಥವಾ ಟೂರ್ನಿಕ್ವೆಟ್ ಹಾಕಬೇಡಿ. "
            "ರೋಗಿಯನ್ನು ತಕ್ಷಣ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಕರೆದೊಯ್ಯಿರಿ."
        ),
        "HIGH": (
            "ಎಚ್ಚರಿಕೆ. ಇದು ತುರ್ತು ಸ್ನೇಕ್‌ಬೈಟ್ ವರದಿ. "
            "ಅಪಾಯದ ಮಟ್ಟ ಹೆಚ್ಚು. ಮೂವತ್ತು ನಿಮಿಷಗಳಲ್ಲಿ ಆಸ್ಪತ್ರೆ ತಲುಪಬೇಕು. "
            "ರೋಗಿಯನ್ನು ನಡೆಸಬೇಡಿ. ಪೂರ್ತಿಯಾಗಿ ಸ್ಥಿರವಾಗಿ ಇಡಿ. "
            "ಟೂರ್ನಿಕ್ವೆಟ್ ಹಾಕಬೇಡಿ. ಗಿಡಮೂಲಿಕೆ ಹಾಕಬೇಡಿ. "
            "ಕೂಡಲೇ ಆಂಬ್ಯುಲೆನ್ಸ್ ಕರೆ ಮಾಡಿ. ಪ್ರತಿ ನಿಮಿಷ ಮುಖ್ಯ. "
            "ಆಸ್ಪತ್ರೆಗೆ ಮೊದಲೇ ತಿಳಿಸಿ ಆಂಟಿವೆನಮ್ ಸಿದ್ಧಪಡಿಸಲು ಹೇಳಿ."
        ),
        "CRITICAL": (
            "ತುರ್ತು ಎಚ್ಚರಿಕೆ. ಅಪಾಯದ ಮಟ್ಟ ಅತ್ಯಂತ ತೀವ್ರ. "
            "ರೋಗಿ ತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದಾರೆ. ಈಗಲೇ ಆಂಬ್ಯುಲೆನ್ಸ್ ಕರೆ ಮಾಡಿ. ಕಾಯಬೇಡಿ. "
            "ರೋಗಿಯನ್ನು ಮಲಗಿಸಿ. ನಿಲ್ಲಲು ಬಿಡಬೇಡಿ. "
            "ಉಸಿರಾಟ ನಿಂತರೆ ಬಾಯಿ ಮೂಲಕ ಉಸಿರಾಟ ನೀಡಿ. "
            "ರೋಗಿಗೆ ಐಸಿಯು ಮತ್ತು ಆಂಟಿವೆನಮ್ ತಕ್ಷಣ ಬೇಕು. "
            "ಸಾಂಪ್ರದಾಯಿಕ ಚಿಕಿತ್ಸೆ ಪ್ರಯತ್ನಿಸಬೇಡಿ. ಈಗಲೇ ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳಿ."
        ),
    },
}

ANTIVENOM_TEXT = {
    "en": {
        True: "Antivenom treatment is required. Inform the hospital to prepare antivenom before arrival.",
        False: "Antivenom is not indicated at this time. Continue monitoring the patient closely for any changes.",
    },
    "te": {
        True: "యాంటీవెనమ్ చికిత్స అవసరం. ఆసుపత్రికి ముందే చెప్పి యాంటీవెనమ్ సిద్ధం చేయించండి.",
        False: "ఇప్పుడు యాంటీవెనమ్ అవసరం లేదు. రోగిని జాగ్రత్తగా పర్యవేక్షిస్తూ ఉండండి.",
    },
    "hi": {
        True: "एंटीवेनम उपचार आवश्यक है। अस्पताल को पहले से बताकर एंटीवेनम तैयार कराएं।",
        False: "अभी एंटीवेनम की आवश्यकता नहीं है। मरीज़ पर करीबी नज़र रखें।",
    },
    "ta": {
        True: "ஆண்டிவெனம் சிகிச்சை தேவை. மருத்துவமனைக்கு முன்கூட்டியே தெரிவித்து ஆண்டிவெனம் தயார் செய்யச் சொல்லுங்கள்.",
        False: "இப்போது ஆண்டிவெனம் தேவையில்லை. நோயாளியை கவனமாக கண்காணிக்கவும்.",
    },
    "kn": {
        True: "ಆಂಟಿವೆನಮ್ ಚಿಕಿತ್ಸೆ ಅಗತ್ಯ. ಆಸ್ಪತ್ರೆಗೆ ಮೊದಲೇ ತಿಳಿಸಿ ಆಂಟಿವೆನಮ್ ಸಿದ್ಧಪಡಿಸಲು ಹೇಳಿ.",
        False: "ಈಗ ಆಂಟಿವೆನಮ್ ಅಗತ್ಯವಿಲ್ಲ. ರೋಗಿಯನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಗಮನಿಸಿ.",
    },
}

SUPPORTED_LANGUAGES = ["en", "te", "hi", "ta", "kn"]


def build_spoken_summary(severity_class: str, antivenom_required: bool, language: str = "en") -> str:
    """Builds a spoken-summary string that is GUARANTEED to be in the
    requested language (bounded template lookup, not free-text translation)."""
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    severity_class = (severity_class or "MODERATE").upper()

    severity_line = SEVERITY_TEXT.get(lang, SEVERITY_TEXT["en"]).get(
        severity_class, SEVERITY_TEXT[lang]["MODERATE"]
    )
    antivenom_line = ANTIVENOM_TEXT.get(lang, ANTIVENOM_TEXT["en"])[bool(antivenom_required)]

    return f"{severity_line} {antivenom_line}"
