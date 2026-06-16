"""
Atualiza entradas pendentes da fila com roteiros bíblicos do Daily Manna.
Uso: python _update_slots.py
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
QUEUE_DIR = BASE_DIR / "queue"

# ── Roteiros bíblicos (NIV, ~65-75 palavras, 30s) ─────────────────────────────

SCRIPTS = {
    # ── W23 pendentes ──────────────────────────────────────────────────────────
    "video_tue_0602_a": {
        "title": "Philippians 4:13 — You Can Do This",
        "narration": "Philippians 4 verse 13 — I can do all things through Christ who strengthens me. Paul wrote this from prison — not from prosperity or comfort. He wasn't promising you'll get everything you want. He was saying Christ gives you what you need to endure anything life throws at you. What situation in your life needs this strength today? Drop it in the comments. Subscribe for a verse every day.",
        "description": "Philippians 4:13 — One of the most powerful promises in scripture, written from a prison cell. Real strength doesn't come from circumstances. It comes from Christ. #BibleVerse #Philippians #Faith #DailyManna #Scripture",
        "tags": ["bible verse", "philippians 4:13", "faith", "strength", "daily manna", "christian shorts", "scripture", "verse of the day"],
        "publish_hour_brt": 8,
    },
    "video_tue_0602_b": {
        "title": "Jeremiah 29:11 — God Has a Plan for You",
        "narration": "Jeremiah 29 verse 11 — For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future. God said this to exiles — people who had lost everything. The hope wasn't immediate. It came after waiting. Are you in a season of uncertainty right now? Subscribe for a verse every day.",
        "description": "Jeremiah 29:11 — God spoke this promise to people in exile. If you're in a hard season, this verse is for you. His plans are bigger than your current circumstances. #BibleVerse #Jeremiah #Hope #DailyManna #Christian",
        "tags": ["bible verse", "jeremiah 29:11", "hope", "god's plan", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 14,
    },
    "video_tue_0602_c": {
        "title": "Romans 8:28 — Even This",
        "narration": "Romans 8 verse 28 — And we know that in all things God works for the good of those who love him, who have been called according to his purpose. All things. Not some things. Not the easy things. All of it — including the painful chapters, the failures, and the detours. What's the hardest thing you're trusting God with right now? Subscribe for a verse every day.",
        "description": "Romans 8:28 — All things. God doesn't waste a single season of your life. Even the hard parts are being woven into something good. #BibleVerse #Romans #Faith #DailyManna #Scripture",
        "tags": ["bible verse", "romans 8:28", "faith", "trust", "daily manna", "scripture", "christian shorts", "verse of the day"],
        "publish_hour_brt": 20,
    },
    "video_wed_0603_a": {
        "title": "Psalm 23:1 — You Shall Not Want",
        "narration": "Psalm 23 verse 1 — The Lord is my shepherd, I shall not want. David wrote this as a shepherd himself — someone who knew exactly what a good shepherd does. He leads. He protects. He provides. He goes looking when one is lost. If God is your shepherd, then no real need goes unmet. What do you need from Him today? Subscribe for a verse every day.",
        "description": "Psalm 23:1 — David wrote this knowing what a shepherd really does. If God is yours, you lack nothing that truly matters. #BibleVerse #Psalm23 #Faith #DailyManna #Scripture",
        "tags": ["bible verse", "psalm 23", "shepherd", "provision", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 8,
    },
    "video_wed_0603_b": {
        "title": "Matthew 11:28 — Bring Your Burden Here",
        "narration": "Matthew 11 verse 28 — Come to me, all you who are weary and burdened, and I will give you rest. Jesus said this to people crushed under religious rules and impossible standards. He wasn't offering a method or a program. He was offering himself. The rest he gives isn't passive — it's the peace of being carried. What burden are you carrying today? Subscribe for a verse every day.",
        "description": "Matthew 11:28 — Jesus didn't say 'figure it out.' He said come to me. Real rest isn't found in doing less — it's found in trusting him more. #BibleVerse #Matthew #Rest #DailyManna #Faith",
        "tags": ["bible verse", "matthew 11:28", "rest", "peace", "daily manna", "jesus", "scripture", "christian shorts"],
        "publish_hour_brt": 14,
    },
    "video_wed_0603_c": {
        "title": "Proverbs 3:5-6 — Trust Him With All of It",
        "narration": "Proverbs 3 verses 5 and 6 — Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight. All your heart — not half of it. The part that worries, too. Straight paths don't always mean easy paths. They mean paths that lead somewhere. Subscribe for a verse every day.",
        "description": "Proverbs 3:5-6 — Trusting God with all your heart means letting go of the part you're still trying to control. #BibleVerse #Proverbs #Trust #DailyManna #Faith",
        "tags": ["bible verse", "proverbs 3:5", "trust", "wisdom", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 20,
    },
    "video_fri_0605_a": {
        "title": "Isaiah 40:31 — Soar on Wings Like Eagles",
        "narration": "Isaiah 40 verse 31 — But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint. Notice the order — soaring comes before walking. The hardest thing isn't the big moments. It's the ordinary days. Hope renews you for both. What are you hoping in today? Subscribe for a verse every day.",
        "description": "Isaiah 40:31 — The renewal God promises isn't just for crisis moments. It's for the ordinary, exhausting days too. #BibleVerse #Isaiah #Strength #DailyManna #Faith",
        "tags": ["bible verse", "isaiah 40:31", "strength", "hope", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 8,
    },
    "video_fri_0605_b": {
        "title": "John 3:16 — The Verse That Changes Everything",
        "narration": "John 3 verse 16 — For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life. Notice what it doesn't say — it doesn't say God loved the good people or the religious people. It says the world. All of it. Including you on your worst day. Does this change how you see God? Subscribe for a verse every day.",
        "description": "John 3:16 — The most quoted verse in history. But read it slowly. 'Whoever' includes you — on your worst day, in your hardest season. #BibleVerse #John316 #Grace #DailyManna #Faith",
        "tags": ["bible verse", "john 3:16", "salvation", "god's love", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 14,
    },
    "video_fri_0605_c": {
        "title": "1 Corinthians 13:4 — What Love Actually Looks Like",
        "narration": "1 Corinthians 13 verse 4 — Love is patient, love is kind. It does not envy, it does not boast, it is not proud. Paul wasn't describing a feeling. He was describing a series of choices — patience is a choice, kindness is a choice. Real love isn't something you fall into. It's something you daily decide. Where is love hardest to live out for you? Subscribe for a verse every day.",
        "description": "1 Corinthians 13:4 — Love isn't a feeling that comes and goes. It's a daily decision. Paul described it as action, not emotion. #BibleVerse #Love #DailyManna #Faith #Scripture",
        "tags": ["bible verse", "1 corinthians 13", "love", "faith", "daily manna", "scripture", "christian shorts", "verse of the day"],
        "publish_hour_brt": 20,
    },
    "video_sat_0606_a": {
        "title": "Psalm 46:1 — Your Refuge Right Now",
        "narration": "Psalm 46 verse 1 — God is our refuge and strength, an ever-present help in trouble. Ever-present — not sometimes present, not present when you've got it together, not present after you've fixed it. Right now, in the middle of it, he's already there. The psalmist wrote this during national crisis. It held then. It holds now. What do you need refuge from today? Subscribe for a verse every day.",
        "description": "Psalm 46:1 — God isn't distant when things fall apart. He's ever-present — meaning right now, in the middle of whatever you're facing. #BibleVerse #Psalm46 #Refuge #DailyManna #Faith",
        "tags": ["bible verse", "psalm 46:1", "refuge", "strength", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 8,
    },
    "video_sat_0606_b": {
        "title": "2 Timothy 1:7 — Not a Spirit of Fear",
        "narration": "2 Timothy 1 verse 7 — For the Spirit God gave us does not make us timid, but gives us power, love and self-discipline. Fear is not from God. Not the kind that paralyzes, shrinks you down, or makes you quit. That spirit has a different source. The Spirit you've been given is powerful, loving, and clear-minded. What fear are you ready to hand back? Subscribe for a verse every day.",
        "description": "2 Timothy 1:7 — The Spirit God gives doesn't produce fear. It produces power. If fear is running your decisions, this verse is for you. #BibleVerse #2Timothy #NoFear #DailyManna #Faith",
        "tags": ["bible verse", "2 timothy 1:7", "fear", "power", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 14,
    },
    "video_sat_0606_c": {
        "title": "Hebrews 11:1 — This Is What Faith Is",
        "narration": "Hebrews 11 verse 1 — Now faith is confidence in what we hope for and assurance about what we do not see. Faith isn't blind. It's not pretending problems don't exist. It's holding certainty about something that hasn't arrived yet — like a seed that hasn't broken ground. You can't see it, but you trust the process. What are you believing God for that you can't see yet? Subscribe for a verse every day.",
        "description": "Hebrews 11:1 — Faith isn't ignoring reality. It's being certain of something real that you can't see yet. The entire chapter is proof it's always worked. #BibleVerse #Hebrews #Faith #DailyManna #Scripture",
        "tags": ["bible verse", "hebrews 11:1", "faith", "hope", "daily manna", "scripture", "christian shorts", "verse of the day"],
        "publish_hour_brt": 20,
    },
    "video_sun_0607_a": {
        "title": "Romans 8:38-39 — Nothing Can Separate You",
        "narration": "Romans 8 verses 38 and 39 — Neither death nor life, neither angels nor demons, neither the present nor the future, nor any powers, neither height nor depth, nor anything else in all creation, will be able to separate us from the love of God that is in Christ Jesus our Lord. Paul covered every category of threat he could think of. None of them cuts you off from God's love. Does knowing this change anything for you today? Subscribe for a verse every day.",
        "description": "Romans 8:38-39 — Paul listed every category of threat he could think of. None of them can cut you off from God's love. None. #BibleVerse #Romans8 #GodsLove #DailyManna #Faith",
        "tags": ["bible verse", "romans 8:38", "god's love", "faith", "daily manna", "scripture", "christian shorts", "verse of the day"],
        "publish_hour_brt": 8,
    },
    "video_sun_0607_b": {
        "title": "Lamentations 3:22-23 — New Every Morning",
        "narration": "Lamentations 3 verses 22 and 23 — Because of the Lord's great love we are not consumed, for his compassions never fail. They are new every morning; great is your faithfulness. This was written in the darkest book of the Bible — after Jerusalem was destroyed. And yet. Even there, the writer found something new every morning. Whatever yesterday looked like, today is a fresh start. Subscribe for a verse every day.",
        "description": "Lamentations 3:22-23 — Written in the middle of total devastation. If mercy could be found there, it can be found in your morning too. #BibleVerse #NewEveryMorning #Mercy #DailyManna #Faith",
        "tags": ["bible verse", "lamentations 3:22", "mercy", "new every morning", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 14,
    },
    "video_sun_0607_c": {
        "title": "Psalm 118:24 — Today Is the Day",
        "narration": "Psalm 118 verse 24 — This is the day the Lord has made; let us rejoice and be glad in it. Not yesterday with its regrets. Not tomorrow with its worries. This day — the one you're in right now. It was made by God, which means it has purpose built into it. You don't have to wait for a better day to be glad. What's one thing you're grateful for today? Subscribe for a verse every day.",
        "description": "Psalm 118:24 — This specific day — not a better one, not an easier one — was made by God and has purpose in it. #BibleVerse #Psalm118 #Gratitude #DailyManna #Faith",
        "tags": ["bible verse", "psalm 118:24", "gratitude", "joy", "daily manna", "faith", "scripture", "christian shorts"],
        "publish_hour_brt": 20,
    },
}

# ── Atualiza W23 ───────────────────────────────────────────────────────────────
w23_file = QUEUE_DIR / "2026_W23.json"
q = json.loads(w23_file.read_text(encoding="utf-8"))
updated = 0
for entry in q:
    slug = entry.get("slug")
    if slug in SCRIPTS and entry.get("status") in ("pending", "error"):
        s = SCRIPTS[slug]
        entry["narration"]        = s["narration"]
        entry["num_takes"]        = 3
        entry["duration"]         = 30
        entry["voice"]            = "rachel"
        entry["title"]            = s["title"]
        entry["description"]      = s["description"]
        entry["tags"]             = s["tags"]
        entry["publish_hour_brt"] = s["publish_hour_brt"]
        entry["status"]           = "pending"
        entry["error_msg"]        = ""
        updated += 1
        print(f"  W23 atualizado: {slug}")

w23_file.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nW23: {updated} entradas atualizadas com roteiros biblicos")
