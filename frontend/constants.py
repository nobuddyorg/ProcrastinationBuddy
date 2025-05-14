import os

LAYOUT = "centered"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

PAGE_ICON = "⏰"

TEXTS = {
    "en": {
        "language_long": "English",
        "main": {
            "title": "Procrastination Buddy ⏰🤷",
            "subtitle": "Your partner in crime for finding perfectly pointless tasks!",
            "generate_button": "Generate",
            "spinner_text": "Generating task...",
            "info_button": "ℹ️",
            "like_button": "❤",
            "config_button": "⚙️",
        },
        "help": {
            "title": "Why other tools don't help you!",
            "intro": "**Let's face it**, you’ll end up in the *'Urgent and Important'* quadrant of the Eisenhower Matrix anyway. Why waste time planning? Pomodoro? Sure, take a 25-minute break. Procrastination isn't a sprint, it's art.",
            "middle": "But hey, don’t stress, just enjoy your perfectly unbalanced balance of procrastination and productivity. And if you're still trying to stick to these methods against all reason, feel free to read more about them.",
            "pomodoro_title": "**Pomodoro Technique**",
            "pomodoro_desc": "It’s all about 25-minute bursts of productivity… or of pretending to focus until your next scheduled distraction. Maybe you get something done - or maybe you procrastinate harder, just to avoid the timer.",
            "pomodoro_link": "Learn more about Pomodoro Technique",
            "eisenhower_title": "**Eisenhower Matrix**",
            "eisenhower_desc": "It’s a fancy way of making all your tasks urgent and important at the same time. Congratulations, you're officially stressed - staring at one remaining quadrant with no method left to help with priorities anymore.",
            "eisenhower_link": "Learn more about Eisenhower Matrix",
            "summary": "In the end, these methods might help. But when you're truly embracing procrastination, remember: *all tasks will end up in 'Urgent and Important'.*",
            "irony": "**If you think this is sarcastic, just remember: it's still not as ironic as using a tomato or a 60-year-old matrix to boost your productivity in the 21st century as if the world hasn’t changed since.**",
            "close": "Close",
        },
    },
    "de": {
        "language_long": "Deutsch",
        "main": {
            "title": "Procrastination Buddy ⏰🤷",
            "subtitle": "Dein Komplize bei der Suche nach völlig sinnlosen Aufgaben!",
            "generate_button": "Generiere",
            "spinner_text": "Aufgabe wird generiert...",
            "info_button": "ℹ️",
            "like_button": "❤",
            "config_button": "⚙️",
        },
        "help": {
            "title": "Warum andere Tools dir nicht helfen!",
            "intro": "**Mal ehrlich**, du landest sowieso im *'Dringend und Wichtig'*-Quadranten der Eisenhower-Matrix. Warum also Zeit mit Planung verschwenden? Pomodoro? Klar, gönn dir eine 25-minütige Pause. Prokrastination ist kein Sprint, es ist Kunst.",
            "middle": "Aber hey, kein Stress! Genieße einfach dein perfekt unausgewogenes Gleichgewicht zwischen Prokrastination und Produktivität. Und wenn du trotzdem versuchst, dich an diese Methoden zu klammern, kannst du natürlich gern weiterlesen.",
            "pomodoro_title": "**Pomodoro-Technik**",
            "pomodoro_desc": "25 Minuten produktiv sein... oder so tun, als ob. Vielleicht schaffst du was oder aber du fühlst dich bei jedem Alarm wie morgens 5 Uhr aus dem Schlaf gerissen und kannst deine aktuellen Gedanken nicht mehr sammeln. Auf Wiedersehen Flow!",
            "pomodoro_link": "Mehr über die Pomodoro-Technik",
            "eisenhower_title": "**Eisenhower-Matrix**",
            "eisenhower_desc": "Eine elegante Methode, um alle Aufgaben gleichzeitig dringend und wichtig zu machen. Glückwunsch, du bist jetzt offiziell gestresst – und starrst auf den letzten Quadranten ohne jede Orientierung.",
            "eisenhower_link": "Mehr über die Eisenhower-Matrix",
            "summary": "Am Ende könnten diese Methoden helfen. Aber wenn du wahre Prokrastination lebst, denk daran: *alle Aufgaben enden im 'Dringend und Wichtig'-Quadranten.*",
            "irony": "**Wenn du denkst, das ist sarkastisch – denk dran: es ist immer noch weniger ironisch als mit einer Tomate oder einem 60 Jahre alten Modell die Produktivität im 21. Jahrhundert steigern zu wollen, als hätte sich seither nichts geändert.**",
            "close": "Schließen",
        },
    },
    "es": {
        "language_long": "Español",
        "main": {
            "title": "Procrastination Buddy ⏰🤷",
            "subtitle": "Tu cómplice perfecto para encontrar tareas absolutamente inútiles.",
            "generate_button": "Generar",
            "spinner_text": "Generando tarea...",
            "info_button": "ℹ️",
            "like_button": "❤",
            "config_button": "⚙️",
        },
        "help": {
            "title": "¡Por qué otras herramientas no te ayudan!",
            "intro": "**Seamos sinceros**, terminarás en el cuadrante *'Urgente e Importante'* de la Matriz Eisenhower de todas formas. ¿Para qué planear? ¿Pomodoro? Claro, tómate un descanso de 25 minutos. La procrastinación no es una carrera, es arte.",
            "middle": "Pero tranquilo, solo disfruta ese equilibrio perfectamente desequilibrado entre procrastinación y productividad. Y si aún así insistes en seguir estas técnicas contra todo sentido común, adelante, lee más.",
            "pomodoro_title": "**Técnica Pomodoro**",
            "pomodoro_desc": "Se trata de intervalos de 25 minutos de productividad… o de fingir que te concentras hasta la próxima distracción programada. Quizá hagas algo – o quizá procrastines con más ganas solo para evitar el temporizador.",
            "pomodoro_link": "Más sobre la Técnica Pomodoro",
            "eisenhower_title": "**Matriz Eisenhower**",
            "eisenhower_desc": "Una forma elegante de convertir todas tus tareas en urgentes e importantes al mismo tiempo. Felicidades, ahora estás oficialmente estresado, mirando fijamente ese único cuadrante que ya no sirve de nada.",
            "eisenhower_link": "Más sobre la Matriz Eisenhower",
            "summary": "Al final, estas técnicas podrían ayudar. Pero si estás abrazando la procrastinación de verdad, recuerda: *todas las tareas terminarán en 'Urgente e Importante'.*",
            "irony": "**Si esto te suena sarcástico, recuerda: no es tan irónico como usar un tomate o una matriz de hace 60 años para ser más productivo en pleno siglo XXI, como si el mundo no hubiera cambiado.**",
            "close": "Cerrar",
        },
    },
    "fr": {
        "language_long": "Français",
        "main": {
            "title": "Procrastination Buddy ⏰🤷",
            "subtitle": "Ton partenaire idéal pour dénicher des tâches totalement inutiles !",
            "generate_button": "Générer",
            "spinner_text": "Génération de tâche...",
            "info_button": "ℹ️",
            "like_button": "❤",
            "config_button": "⚙️",
        },
        "help": {
            "title": "Pourquoi les autres outils ne vous aident pas !",
            "intro": "**Soyons honnêtes**, tu finiras de toute façon dans le quadrant *'Urgent et Important'* de la matrice d’Eisenhower. Alors pourquoi perdre du temps à planifier ? Pomodoro ? Bien sûr, fais une pause de 25 minutes. La procrastination n’est pas un sprint, c’est un art.",
            "middle": "Mais pas de panique, profite juste de cet équilibre parfaitement déséquilibré entre productivité et procrastination. Et si tu veux encore croire à ces méthodes malgré tout, tu peux toujours en lire plus.",
            "pomodoro_title": "**Technique Pomodoro**",
            "pomodoro_desc": "Des sessions de 25 minutes de productivité… ou de concentration feinte jusqu’à la prochaine distraction planifiée. Peut-être que tu avances – ou peut-être que tu procrastines encore plus fort juste pour éviter le minuteur.",
            "pomodoro_link": "En savoir plus sur la Technique Pomodoro",
            "eisenhower_title": "**Matrice d’Eisenhower**",
            "eisenhower_desc": "Une méthode chic pour rendre toutes tes tâches urgentes et importantes en même temps. Bravo, tu es officiellement stressé – face à un dernier quadrant qui ne sert plus à rien.",
            "eisenhower_link": "En savoir plus sur la Matrice d’Eisenhower",
            "summary": "Au final, ces méthodes peuvent aider. Mais si tu assumes pleinement la procrastination, souviens-toi : *toutes les tâches finiront en 'Urgent et Important'.*",
            "irony": "**Si tu trouves ça sarcastique, rappelle-toi : c’est toujours moins ironique que d’utiliser une tomate ou une matrice vieille de 60 ans pour booster ta productivité au XXIe siècle, comme si le monde n’avait pas changé.**",
            "close": "Fermer",
        },
    },
}

SETTINGS = {
    "LANGUAGE": "fr",
    "MODEL": "mistral:instruct",
    "PAGE_SIZE": 10,
    "PAGE_NUMBER": 0
}
