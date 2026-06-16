"""
Gera filas W25 (Jun 15-21) e W26 (Jun 22-28) com roteiros bíblicos Daily Manna.
Hooks psicológicos éticos: curiosidade, reconhecimento emocional, contexto surpreendente.
"""
import json
from pathlib import Path
from datetime import date as dt

QUEUE_DIR = Path(__file__).parent / "queue"


def make_entry(day, day_pt, date_str, slot, slug, title, narration, description, tags, hour):
    return {
        "day": day, "day_pt": day_pt, "date": date_str, "slot": slot, "slug": slug,
        "narration": narration, "num_takes": 3, "duration": 30, "voice": "rachel",
        "title": title, "description": description, "tags": tags,
        "publish_hour_brt": hour, "status": "pending", "error_msg": "",
    }


# ── W25: Jun 15-21 ─────────────────────────────────────────────────────────────
W25 = [
    # Jun 15 Mon
    make_entry("monday","Segunda","2026-06-15","a","video_mon_0615_a",
        "Joshua 1:9 — God Said This When Everything Changed",
        "God gave Joshua this command the day Moses died — when leadership, direction, and safety all vanished at once. Joshua 1 verse 9: Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go. He didn't wait for Joshua to feel ready. He spoke into the overwhelm. What moment in your life needs this word right now? Subscribe for a verse every day.",
        "Joshua 1:9 — God gave this command on the hardest day, not the easiest. Strong and courageous wasn't a feeling — it was a decision made in the middle of change. #BibleVerse #Joshua #Courage #DailyManna #Faith",
        ["bible verse","joshua 1:9","courage","strength","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("monday","Segunda","2026-06-15","b","video_mon_0615_b",
        "John 14:27 — Not the Peace the World Offers",
        "The night before he was crucified, Jesus said this. John 14 verse 27: Peace I leave with you; my peace I give you. I do not give to you as the world gives. Do not let your hearts be troubled and do not be afraid. The world's peace requires circumstances to cooperate. Jesus's peace exists inside of impossible circumstances. That is a completely different thing. What is disturbing your peace today? Subscribe for a verse every day.",
        "John 14:27 — Jesus said this the night before his death. The peace He offered wasn't about circumstances improving. It was peace that exists inside of impossible ones. #BibleVerse #John14 #Peace #DailyManna #Faith",
        ["bible verse","john 14:27","peace","faith","daily manna","scripture","christian shorts","verse of the day"], 14),

    make_entry("monday","Segunda","2026-06-15","c","video_mon_0615_c",
        "Psalm 91:1 — The Condition Most People Miss",
        "Psalm 91 is one of the most powerful protection passages in scripture — but most people quote the promises and skip the condition. Verse 1: Whoever dwells in the shelter of the Most High will rest in the shadow of the Almighty. Dwells — not visits. Not stops by when things get hard. The protection is inseparable from the proximity. How close are you staying to God right now? Subscribe for a verse every day.",
        "Psalm 91:1 — The protection in this psalm has a condition most people overlook. Dwell — not visit. Nearness is where the shelter lives. #BibleVerse #Psalm91 #Protection #DailyManna #Faith",
        ["bible verse","psalm 91","protection","shelter","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 16 Tue
    make_entry("tuesday","Terca","2026-06-16","a","video_tue_0616_a",
        "Romans 5:3-4 — What Hard Seasons Are Actually Doing",
        "If you're in a painful season right now, this verse explains what's happening underneath it. Romans 5 verses 3 and 4: We also glory in our sufferings, because suffering produces perseverance; perseverance, character; and character, hope. That word 'produces' means it's manufacturing something. You're not just enduring — you're being built. What character is your current struggle making in you? Subscribe for a verse every day.",
        "Romans 5:3-4 — Suffering produces. It's not just something to survive. It's manufacturing perseverance, character, and hope in you. Paul knew this from experience. #BibleVerse #Romans5 #Perseverance #DailyManna #Faith",
        ["bible verse","romans 5:3","suffering","perseverance","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("tuesday","Terca","2026-06-16","b","video_tue_0616_b",
        "1 Peter 5:7 — You Were Never Supposed to Carry This",
        "Peter wrote to people being actively persecuted. And his instruction wasn't 'be stronger.' It was this: 1 Peter 5 verse 7 — Cast all your anxiety on him because he cares for you. That word 'cast' is an active throw. Not a gentle set-down. Not holding it and hoping. A decisive throw. What have you been holding that was never yours to carry? Subscribe for a verse every day.",
        "1 Peter 5:7 — Peter wrote this to people under real persecution. His instruction wasn't to toughen up — it was to throw your anxiety on God. Cast it. All of it. #BibleVerse #1Peter #Anxiety #DailyManna #Faith",
        ["bible verse","1 peter 5:7","anxiety","peace","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("tuesday","Terca","2026-06-16","c","video_tue_0616_c",
        "Psalm 139:14 — Before You Were Born, God Was Intentional",
        "David wrote Psalm 139 after meditating on the fact that God formed him before birth, knew every day of his life in advance, and is present everywhere he goes. Then he wrote verse 14: I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well. Not despite my flaws — including them. Do you actually believe that about yourself? Subscribe for a verse every day.",
        "Psalm 139:14 — David wrote this after sitting with the truth that God formed him intentionally before birth. Fearfully and wonderfully made isn't encouragement. It's a fact. #BibleVerse #Psalm139 #Identity #DailyManna #Faith",
        ["bible verse","psalm 139:14","identity","worth","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 17 Wed
    make_entry("wednesday","Quarta","2026-06-17","a","video_wed_0617_a",
        "Matthew 6:33 — Jesus Said This Right After Talking About Worry",
        "Jesus had just told his disciples not to worry about food, clothes, or tomorrow. Then came this: Matthew 6 verse 33 — But seek first his kingdom and his righteousness, and all these things will be given to you as well. It's not that the needs don't matter. It's that there's an order. Get the order right and God covers the rest. What are you placing first right now? Subscribe for a verse every day.",
        "Matthew 6:33 — Jesus didn't say stop caring about your needs. He said get the order right. Seek His kingdom first and the rest gets covered. That's the promise. #BibleVerse #Matthew6 #Priority #DailyManna #Faith",
        ["bible verse","matthew 6:33","seek first","kingdom","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("wednesday","Quarta","2026-06-17","b","video_wed_0617_b",
        "Ephesians 2:8-9 — You Cannot Earn This, and You Cannot Lose It",
        "If you've ever wondered whether you're good enough for God — this verse answers it permanently. Ephesians 2 verses 8 and 9: For it is by grace you have been saved, through faith — and this is not from yourselves, it is the gift of God — not by works, so that no one can boast. You didn't earn it on your best day. You can't lose it on your worst. Is there a part of you still trying to earn it? Subscribe for a verse every day.",
        "Ephesians 2:8-9 — You didn't earn salvation on your best day. You can't lose it on your worst. It's a gift — that's what makes it grace. #BibleVerse #Ephesians2 #Grace #DailyManna #Faith",
        ["bible verse","ephesians 2:8","grace","salvation","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("wednesday","Quarta","2026-06-17","c","video_wed_0617_c",
        "Colossians 3:23 — Paul Wrote This to Slaves",
        "Paul wrote Colossians 3 verse 23 to people whose work was never recognized, never rewarded, and never chosen: Whatever you do, work at it with all your heart, as working for the Lord, not for human masters. He wasn't minimizing their situation. He was giving them a new audience. When the audience is God, the standard — and the motivation — completely change. What would shift in your work today if you believed this? Subscribe for a verse every day.",
        "Colossians 3:23 — Paul wrote this to slaves. People whose work was never seen. His answer: change your audience. Work for the Lord and the standard changes entirely. #BibleVerse #Colossians #Work #DailyManna #Faith",
        ["bible verse","colossians 3:23","work","faithfulness","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 18 Thu
    make_entry("thursday","Quinta","2026-06-18","a","video_thu_0618_a",
        "1 Thessalonians 5:16-18 — God's Will Is Simpler Than You Think",
        "Most people wonder what God's will is for their life. Paul gave part of the answer in three commands: 1 Thessalonians 5 verses 16 to 18 — Rejoice always, pray continually, give thanks in all circumstances; for this is God's will for you in Christ Jesus. Not feelings. Three daily decisions. In all circumstances — not after they improve. Where does this feel hardest for you right now? Subscribe for a verse every day.",
        "1 Thessalonians 5:16-18 — Part of God's will isn't a mystery. Three commands: rejoice, pray, give thanks. In all circumstances. Not feelings — decisions. #BibleVerse #1Thessalonians #Joy #DailyManna #Faith",
        ["bible verse","1 thessalonians 5:16","rejoice","prayer","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("thursday","Quinta","2026-06-18","b","video_thu_0618_b",
        "James 1:2-3 — 'Pure Joy' in Trials Sounds Crazy Until You Read Why",
        "James says something that sounds impossible: James 1 verses 2 and 3 — Consider it pure joy whenever you face trials of many kinds, because you know that the testing of your faith produces perseverance. The word 'because' is everything. It's not blind positivity. It's joy rooted in understanding what a test is doing in you. The trial means there's something worth developing. What is yours developing right now? Subscribe for a verse every day.",
        "James 1:2-3 — Pure joy in trials sounds impossible until you see the 'because.' It's not denial. It's knowing what a test is building in you. Perseverance carries you through everything else. #BibleVerse #James1 #Trials #DailyManna #Faith",
        ["bible verse","james 1:2","trials","perseverance","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("thursday","Quinta","2026-06-18","c","video_thu_0618_c",
        "Galatians 5:22-23 — It's Called Fruit for a Reason",
        "You cannot force an apple tree to produce apples. You can only tend to the root and the tree does what it was made to do. That's exactly how Paul describes this: Galatians 5 verses 22 and 23 — The fruit of the Spirit is love, joy, peace, forbearance, kindness, goodness, faithfulness, gentleness and self-control. It's not a performance list. It's what naturally grows when the Spirit is alive in you. Are you tending to that connection? Subscribe for a verse every day.",
        "Galatians 5:22-23 — You don't force fruit. You tend the root. These qualities aren't a checklist — they're what naturally grows when the Spirit is alive in you. #BibleVerse #Galatians5 #HolySpirit #DailyManna #Faith",
        ["bible verse","galatians 5:22","fruit of the spirit","holy spirit","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 19 Fri
    make_entry("friday","Sexta","2026-06-19","a","video_fri_0619_a",
        "Proverbs 4:23 — The Most Important Guard You Will Ever Set",
        "You lock your house. You protect your phone. But Solomon says there's something that matters far more. Proverbs 4 verse 23: Above all else, guard your heart, for everything you do flows from it. Above all else. Not one item on the list — the top priority. What you allow in determines what flows out — your decisions, your words, your relationships. What are you letting in right now? Subscribe for a verse every day.",
        "Proverbs 4:23 — You guard your house. Your phone. Solomon says guard something that matters more. Everything you become flows from what you let into your heart. #BibleVerse #Proverbs4 #Wisdom #DailyManna #Faith",
        ["bible verse","proverbs 4:23","heart","wisdom","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("friday","Sexta","2026-06-19","b","video_fri_0619_b",
        "Romans 12:2 — The World Has a Pattern and It Is Working on You",
        "You don't have to try to be shaped by the culture around you. It happens by default. Paul knew this. Romans 12 verse 2: Do not conform to the pattern of this world, but be transformed by the renewing of your mind. The pattern is passive. Transformation is active — it starts in how you think. Renew the mind and everything else shifts. What is currently forming your thinking? Subscribe for a verse every day.",
        "Romans 12:2 — You don't have to try to be shaped by the world. It happens by default. Transformation is the active counter — a mind being renewed from the inside out. #BibleVerse #Romans12 #Transformation #DailyManna #Faith",
        ["bible verse","romans 12:2","transformation","renew","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("friday","Sexta","2026-06-19","c","video_fri_0619_c",
        "Psalm 37:4 — This Is Not a Prosperity Gospel Verse",
        "A lot of people use Psalm 37 verse 4 as a wish list: Take delight in the Lord, and he will give you the desires of your heart. But here's what that actually means — when you truly delight in God, your desires start to align with his. He isn't just granting requests. He's reshaping what you want. The deepest desires of a heart close to God are always answered. Do you believe that? Subscribe for a verse every day.",
        "Psalm 37:4 — This isn't a wish-granting verse. Delighting in God changes what you desire. When your heart aligns with His, the answer is always yes. #BibleVerse #Psalm37 #Delight #DailyManna #Faith",
        ["bible verse","psalm 37:4","delight","desires","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 20 Sat
    make_entry("saturday","Sabado","2026-06-20","a","video_sat_0620_a",
        "Matthew 5:14 — Jesus Did Not Say 'Become' the Light",
        "He said 'you are.' Present tense. Matthew 5 verse 14: You are the light of the world. A town built on a hill cannot be hidden. Jesus wasn't asking you to earn something. He was declaring something already true. Light doesn't announce itself. It doesn't argue for its presence. It just shines — and people are drawn to it or they're not. Where are you being called to shine right now? Subscribe for a verse every day.",
        "Matthew 5:14 — Jesus didn't say try to become the light. He said you ARE. Present tense. That changes everything about how you show up. #BibleVerse #Matthew5 #Light #DailyManna #Faith",
        ["bible verse","matthew 5:14","light","calling","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("saturday","Sabado","2026-06-20","b","video_sat_0620_b",
        "Philippians 4:6-7 — Peace That Makes No Logical Sense",
        "Paul wrote this from prison — and what he described is scientifically unexplainable. Philippians 4 verses 6 and 7: Do not be anxious about anything, but in every situation present your requests to God with thanksgiving. And the peace of God, which transcends all understanding, will guard your hearts and minds in Christ Jesus. Transcends understanding — it surpasses what the situation says is possible. Are you carrying something you could bring to God right now? Subscribe for a verse every day.",
        "Philippians 4:6-7 — Written from prison. The peace Paul describes isn't logical for the circumstances. It surpasses them. Bring what you're carrying to God and see what happens. #BibleVerse #Philippians4 #Anxiety #Peace #DailyManna #Faith",
        ["bible verse","philippians 4:6","anxiety","peace","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("saturday","Sabado","2026-06-20","c","video_sat_0620_c",
        "1 John 4:18 — Fear and Love Cannot Fully Coexist",
        "Think about what you're most afraid of right now. Then hear this. 1 John 4 verse 18: There is no fear in love. But perfect love drives out fear, because fear has to do with punishment. The one who fears is not made perfect in love. Fear is often rooted in the belief that you'll pay for your mistakes. Perfect love says the debt is already gone. The more you understand that, the less grip fear has. What fear needs to go? Subscribe for a verse every day.",
        "1 John 4:18 — Fear and love cannot fully coexist. The more you grasp how completely God loves you — no punishment, debt cleared — the weaker fear's hold becomes. #BibleVerse #1John4 #Fear #Love #DailyManna #Faith",
        ["bible verse","1 john 4:18","perfect love","fear","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 21 Sun
    make_entry("sunday","Domingo","2026-06-21","a","video_sun_0621_a",
        "John 15:5 — Jesus Used a Farming Metaphor for a Reason",
        "A branch disconnected from a vine doesn't die immediately. It just slowly stops producing — and most of the time, it doesn't even notice at first. John 15 verse 5: I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing. Fruit isn't manufactured. It's what happens when you stay. Are you staying connected? Subscribe for a verse every day.",
        "John 15:5 — A branch doesn't force fruit. It stays connected to the vine. Jesus said the same is true for you. Connection first. Everything else follows. #BibleVerse #John15 #Abide #DailyManna #Faith",
        ["bible verse","john 15:5","abide","fruit","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("sunday","Domingo","2026-06-21","b","video_sun_0621_b",
        "Deuteronomy 31:8 — Moses Said This to Someone Terrified",
        "Joshua was about to lead millions of people into an unknown land — without Moses, without a roadmap, with enemies waiting. Moses's final words to him: Deuteronomy 31 verse 8 — The Lord himself goes before you and will be with you; he will never leave you nor forsake you. Do not be afraid; do not be discouraged. What unknown are you stepping into this week? He's already there. Subscribe for a verse every day.",
        "Deuteronomy 31:8 — Moses gave this to a man who was terrified and completely in over his head. God goes before you into whatever you're facing — He doesn't just follow. #BibleVerse #Deuteronomy #NeverAlone #DailyManna #Faith",
        ["bible verse","deuteronomy 31:8","never alone","presence","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("sunday","Domingo","2026-06-21","c","video_sun_0621_c",
        "Revelation 21:4 — God Named Every Hard Thing You Are Going Through",
        "This verse wasn't written as a distant future hope. It was written to people actively experiencing every item on this list. Revelation 21 verse 4: He will wipe every tear from their eyes. There will be no more death or mourning or crying or pain, for the old order of things has passed away. He named them all — and said not forever. Whatever chapter you're in, it is not the final one. What are you holding through? Subscribe for a verse every day.",
        "Revelation 21:4 — God didn't give a vague promise. He named death, mourning, crying, pain specifically — and said not forever. Whatever chapter you're in isn't the last one. #BibleVerse #Revelation21 #Hope #Eternity #DailyManna #Faith",
        ["bible verse","revelation 21:4","hope","eternity","daily manna","faith","scripture","christian shorts"], 20),
]

# ── W26: Jun 22-28 ─────────────────────────────────────────────────────────────
W26 = [
    # Jun 22 Mon
    make_entry("monday","Segunda","2026-06-22","a","video_mon_0622_a",
        "Psalm 34:18 — God Is Nearest When You Feel Most Alone",
        "This seems counterintuitive — but it's one of the most consistent truths in scripture. Psalm 34 verse 18: The Lord is close to the brokenhearted and saves those who are crushed in spirit. Not distant, waiting for you to recover. Close. The very condition that makes you feel most isolated is what draws God nearest to you. David wrote this after pretending to be insane to survive. He knew this from the inside. Are you letting him be close? Subscribe for a verse every day.",
        "Psalm 34:18 — The condition that makes you feel most alone is what draws God closest. Brokenhearted isn't where He's absent. It's where He arrives. #BibleVerse #Psalm34 #Comfort #DailyManna #Faith",
        ["bible verse","psalm 34:18","brokenhearted","comfort","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("monday","Segunda","2026-06-22","b","video_mon_0622_b",
        "Matthew 28:20 — Jesus's Last Words Were Not a Goodbye",
        "His very last words before ascending weren't a farewell. They were a permanent promise. Matthew 28 verse 20: And surely I am with you always, to the very end of the age. Always. Not when you have it together. Not on Sundays or during prayer. The very end of the age. Nothing in your life — not your worst week, not your most ordinary Monday — falls outside of that always. Does knowing that change anything today? Subscribe for a verse every day.",
        "Matthew 28:20 — Jesus's last words weren't a goodbye. They were a permanent promise. Always. Nothing in your week falls outside of that word. #BibleVerse #Matthew28 #Presence #DailyManna #Faith",
        ["bible verse","matthew 28:20","always","presence","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("monday","Segunda","2026-06-22","c","video_mon_0622_c",
        "Isaiah 41:10 — Five Promises Packed Into One Verse",
        "When God says 'do not fear,' He never just leaves you with the command. He backs it up. Isaiah 41 verse 10: So do not fear, for I am with you; do not be dismayed, for I am your God. I will strengthen you and help you; I will uphold you with my righteous right hand. Count them: presence, identity, strength, help, and being held up. Five things. For the one thing you're afraid of. Which of these do you need most right now? Subscribe for a verse every day.",
        "Isaiah 41:10 — God doesn't just say 'don't be afraid' and leave you with the command. He backs it with five specific promises. Presence. Identity. Strength. Help. Being held. #BibleVerse #Isaiah41 #Fear #DailyManna #Faith",
        ["bible verse","isaiah 41:10","fear","strength","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 23 Tue
    make_entry("tuesday","Terca","2026-06-23","a","video_tue_0623_a",
        "Micah 6:8 — God Stripped Religion Down to Three Things",
        "When Israel was asking 'what does God actually want?', Micah gave them the most distilled answer in the entire Old Testament. Micah 6 verse 8: What does the Lord require of you? To act justly and to love mercy and to walk humbly with your God. Three things. Not a system. Not a calendar. Act justly in everyday decisions. Love mercy, not just practice it. Walk humbly — with Him, not ahead. Which of the three is hardest for you? Subscribe for a verse every day.",
        "Micah 6:8 — Three things. Act justly. Love mercy. Walk humbly. Not a religious checklist — a way of being in ordinary moments. Which one needs your attention? #BibleVerse #Micah6 #Justice #DailyManna #Faith",
        ["bible verse","micah 6:8","justice","mercy","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("tuesday","Terca","2026-06-23","b","video_tue_0623_b",
        "Romans 15:13 — Paul Did Not Pray for Enough. He Prayed for Overflow.",
        "When Paul prayed for people under real persecution, he didn't pray that they'd barely make it through. Romans 15 verse 13: May the God of hope fill you with all joy and peace as you trust in him, so that you may overflow with hope by the power of the Holy Spirit. Overflow. Enough to give away. That kind of hope can't be manufactured — it comes from the Spirit. What would overflow look like in your life today? Subscribe for a verse every day.",
        "Romans 15:13 — Paul didn't pray for enough hope to survive. He prayed for overflow. Hope that spills into others. That's what the Spirit produces when you trust. #BibleVerse #Romans15 #Hope #DailyManna #Faith",
        ["bible verse","romans 15:13","hope","joy","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("tuesday","Terca","2026-06-23","c","video_tue_0623_c",
        "2 Corinthians 12:9 — Paul Asked God Three Times. God Said No.",
        "Paul begged God to take away a painful, unnamed 'thorn.' Three times. And God said no. But here's what He did say: 2 Corinthians 12 verse 9 — My grace is sufficient for you, for my power is made perfect in weakness. God didn't remove the limitation — He showed up perfectly inside of it. The weakness wasn't the problem. It was where His power became most visible. What weakness are you still ashamed of? Subscribe for a verse every day.",
        "2 Corinthians 12:9 — Paul begged three times for removal. God said no — but said His power shows up perfectly in weakness. The limitation isn't the problem. It's the location. #BibleVerse #2Corinthians12 #Grace #Weakness #DailyManna #Faith",
        ["bible verse","2 corinthians 12:9","grace","weakness","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 24 Wed
    make_entry("wednesday","Quarta","2026-06-24","a","video_wed_0624_a",
        "Psalm 27:1 — David Was Not Asking a Question. He Was Making a Declaration.",
        "When David wrote 'whom shall I fear?' — he already knew the answer. He'd already decided. Psalm 27 verse 1: The Lord is my light and my salvation — whom shall I fear? The Lord is the stronghold of my life — of whom shall I be afraid? This wasn't uncertainty. This was a settled conviction reached by choosing God again and again. Fear loses its grip when God is your foundation. What would you have to decide today to say this with the same certainty? Subscribe for a verse every day.",
        "Psalm 27:1 — David wasn't asking 'whom shall I fear?' He already knew. He was declaring what he'd decided. Settled conviction is what makes fear lose its grip. #BibleVerse #Psalm27 #Fear #DailyManna #Faith",
        ["bible verse","psalm 27:1","light","salvation","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("wednesday","Quarta","2026-06-24","b","video_wed_0624_b",
        "Proverbs 18:10 — The Tower Does Not Come to You",
        "Safety doesn't find you. You run to it. That's the entire point of Proverbs 18 verse 10: The name of the Lord is a fortified tower; the righteous run to it and are safe. A tower sits. You move. The righteous don't wait to feel safe and then go — they run first and find safety there. When something goes wrong, where is your first instinct taking you? Subscribe for a verse every day.",
        "Proverbs 18:10 — The tower doesn't come to you. You run to it. Where you run first when trouble hits reveals where you actually believe safety lives. #BibleVerse #Proverbs18 #Refuge #DailyManna #Faith",
        ["bible verse","proverbs 18:10","refuge","safety","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("wednesday","Quarta","2026-06-24","c","video_wed_0624_c",
        "John 8:32 — Jesus Said This to People Who Thought They Were Already Free",
        "The people Jesus was speaking to in John 8 believed they had never been enslaved to anyone. And then Jesus said: John 8 verse 32 — Then you will know the truth, and the truth will set you free. The freedom He meant wasn't political. It was freedom from sin, shame, and the lies we believe about ourselves and about God. Truth sets free — but first it confronts. What truth have you been avoiding? Subscribe for a verse every day.",
        "John 8:32 — Jesus said this to people who thought they were already free. The truth He meant confronts first. Then it liberates. What truth are you avoiding? #BibleVerse #John8 #Truth #Freedom #DailyManna #Faith",
        ["bible verse","john 8:32","truth","freedom","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 25 Thu
    make_entry("thursday","Quinta","2026-06-25","a","video_thu_0625_a",
        "Ephesians 3:20 — Your Biggest Prayer Is Not the Limit",
        "Think about the biggest thing you've ever asked God for. Now hear this. Ephesians 3 verse 20: Now to him who is able to do immeasurably more than all we ask or imagine, according to his power that is at work within us. Immeasurably more than ALL you ask or imagine. Your boldest prayer isn't the ceiling — it's the floor. His power working in you is the ceiling. What would you ask if you believed that fully? Subscribe for a verse every day.",
        "Ephesians 3:20 — Your boldest prayer isn't the ceiling. It's the floor. Immeasurably more than all you ask or imagine. What would you pray if you actually believed that? #BibleVerse #Ephesians3 #Prayer #DailyManna #Faith",
        ["bible verse","ephesians 3:20","prayer","faith","daily manna","scripture","christian shorts","verse of the day"], 8),

    make_entry("thursday","Quinta","2026-06-25","b","video_thu_0625_b",
        "Lamentations 3:25 — Written in the Rubble, Not After It",
        "The writer of Lamentations had just watched Jerusalem destroyed. He was sitting in the aftermath. And from inside that — not after it was over — he wrote this: Lamentations 3 verse 25 — The Lord is good to those whose hope is in him, to the one who seeks him. Waiting and seeking at the same time. God's goodness wasn't only at the destination. It was present in the seeking. Are you still seeking while you wait? Subscribe for a verse every day.",
        "Lamentations 3:25 — Written in rubble, not after the rubble was cleared. Seeking God in the middle of the wait — that's where His goodness is found, not just at the end. #BibleVerse #Lamentations #Waiting #DailyManna #Faith",
        ["bible verse","lamentations 3:25","waiting","hope","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("thursday","Quinta","2026-06-25","c","video_thu_0625_c",
        "Psalm 16:8 — What You Look at Determines What Shakes You",
        "David said something simple with enormous implications. Psalm 16 verse 8: I keep my eyes always on the Lord. With him at my right hand, I will not be shaken. The stability came from the focus, not the circumstances. He didn't say conditions improved. He said he kept his eyes in one place. Whatever is shaking you right now reveals what you've been looking at. What would shift if you looked at God instead? Subscribe for a verse every day.",
        "Psalm 16:8 — I will not be shaken. But the stability comes from the focus — I keep my eyes always on the Lord. What you look at determines what moves you. #BibleVerse #Psalm16 #Focus #DailyManna #Faith",
        ["bible verse","psalm 16:8","focus","stability","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 26 Fri
    make_entry("friday","Sexta","2026-06-26","a","video_fri_0626_a",
        "Romans 8:1 — Paul Wrote This Right After Describing His Own Failure",
        "In chapter 7, Paul described doing the exact things he didn't want to do and failing to do the things he intended. It's the most honest account of human struggle in the New Testament. And then chapter 8 opens with this: Romans 8 verse 1 — Therefore, there is now no condemnation for those who are in Christ Jesus. No condemnation. After all of that. Are you still condemning yourself for something that no longer condemns you? Subscribe for a verse every day.",
        "Romans 8:1 — Paul wrote this directly after his most honest description of failure. No condemnation — after all of that. Are you still holding against yourself what God has already cleared? #BibleVerse #Romans8 #NoCondemnation #DailyManna #Faith",
        ["bible verse","romans 8:1","condemnation","forgiveness","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("friday","Sexta","2026-06-26","b","video_fri_0626_b",
        "Isaiah 43:2 — Notice the Word God Chose: Through, Not Around",
        "God could have promised to remove every hard thing. He didn't. He promised something else. Isaiah 43 verse 2: When you pass through the waters, I will be with you; and when you pass through the rivers, they will not sweep over you. Through. Not around. Not removed. Not avoided. You pass through — and He's inside of it with you. The waters you're currently in are something you pass through. What are you in right now? Subscribe for a verse every day.",
        "Isaiah 43:2 — God didn't promise to remove the hard thing. He said through. With you inside of it. The word He chose changes everything about how you face it. #BibleVerse #Isaiah43 #Presence #DailyManna #Faith",
        ["bible verse","isaiah 43:2","through the waters","presence","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("friday","Sexta","2026-06-26","c","video_fri_0626_c",
        "Philippians 2:13 — God Is Not Waiting for You to Fix Yourself",
        "A lot of people live as if God is waiting on the sidelines for them to get their act together before He starts working. Philippians 2 verse 13 says the opposite: For it is God who works in you to will and to act in order to fulfill his good purpose. He's not waiting on you — He's already at work in you. Shaping what you want. Giving you power to act on it. What's one area you can see Him working in you right now? Subscribe for a verse every day.",
        "Philippians 2:13 — God isn't waiting for you to be ready. He's already at work in you — shaping your desires and powering your actions. You're a work He hasn't abandoned. #BibleVerse #Philippians2 #Growth #DailyManna #Faith",
        ["bible verse","philippians 2:13","growth","transformation","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 27 Sat
    make_entry("saturday","Sabado","2026-06-27","a","video_sat_0627_a",
        "Psalm 32:8 — God Does Not Instruct From a Distance",
        "This is what separates God's guidance from every other kind. Psalm 32 verse 8: I will instruct you and teach you in the way you should go; I will counsel you with my loving eye on you. Notice: a loving eye. Not an impatient one. Not a disappointed one. He teaches because He loves — and He watches as He guides. He knows where you are and He's directing you from right there. Are you asking for that guidance right now? Subscribe for a verse every day.",
        "Psalm 32:8 — God doesn't guide from a distance with a checklist. He counsels with a loving eye. Right where you are. He teaches because He loves you. #BibleVerse #Psalm32 #Guidance #DailyManna #Faith",
        ["bible verse","psalm 32:8","guidance","teaching","daily manna","faith","scripture","christian shorts"], 8),

    make_entry("saturday","Sabado","2026-06-27","b","video_sat_0627_b",
        "1 Corinthians 10:13 — Every Temptation Has a Built-In Exit",
        "Paul says something most people don't notice: the exit is already there before you get in. 1 Corinthians 10 verse 13: No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear. But when you are tempted, he will also provide a way out so that you can endure it. The question isn't whether there's a way out. It's whether you're looking for it. What temptation feels inescapable right now? Subscribe for a verse every day.",
        "1 Corinthians 10:13 — God provides the way out before you need it. The question isn't whether the exit exists. It's whether you're looking for it when you're in the temptation. #BibleVerse #1Corinthians10 #Temptation #DailyManna #Faith",
        ["bible verse","1 corinthians 10:13","temptation","strength","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("saturday","Sabado","2026-06-27","c","video_sat_0627_c",
        "Nehemiah 8:10 — This Was Not Said at a Celebration",
        "Nehemiah said this to a crowd that was weeping — people who had just heard God's law read aloud and realized how far they had fallen short. In that moment, he said: Nehemiah 8 verse 10 — Do not grieve, for the joy of the Lord is your strength. Joy isn't the reward for getting it right. It's the source of power that lets you keep going after you've gotten it wrong. Where is your joy coming from today? Subscribe for a verse every day.",
        "Nehemiah 8:10 — Nehemiah said this to people who were weeping over their failures. Joy isn't a reward for performance. It's what carries you forward after falling short. #BibleVerse #Nehemiah #Joy #DailyManna #Faith",
        ["bible verse","nehemiah 8:10","joy","strength","daily manna","faith","scripture","christian shorts"], 20),

    # Jun 28 Sun
    make_entry("sunday","Domingo","2026-06-28","a","video_sun_0628_a",
        "John 1:1 — John Started His Gospel Before Creation Did",
        "Matthew, Mark, and Luke all begin with Jesus's birth or ministry. John went further back. John 1 verse 1: In the beginning was the Word, and the Word was with God, and the Word was God. Before creation, before time, the Word already existed — already with God, already God. When you open scripture, you're not reading about God from a distance. You're hearing from someone who was there before everything began. Does that change how you approach it? Subscribe for a verse every day.",
        "John 1:1 — John didn't start with the manger. He started before creation. The Word was already God, already there. Scripture isn't history about God — it's His voice. #BibleVerse #John1 #Scripture #DailyManna #Faith",
        ["bible verse","john 1:1","word of god","scripture","daily manna","faith","christian shorts","verse of the day"], 8),

    make_entry("sunday","Domingo","2026-06-28","b","video_sun_0628_b",
        "2 Corinthians 5:17 — Not Improved. Entirely New.",
        "Paul didn't say God improves people who come to Christ. He said something far more radical. 2 Corinthians 5 verse 17: If anyone is in Christ, the new creation has come: The old has gone, the new is here. Not reformed. Not a better version. New creation. The old isn't just forgiven — it's gone. The person you were before doesn't get to define the person you're becoming. Do you actually see yourself that way? Subscribe for a verse every day.",
        "2 Corinthians 5:17 — God didn't say improved. He said new creation. The old is gone. The person you were before doesn't get to define who you're becoming in Christ. #BibleVerse #2Corinthians5 #NewCreation #DailyManna #Faith",
        ["bible verse","2 corinthians 5:17","new creation","identity","daily manna","faith","scripture","christian shorts"], 14),

    make_entry("sunday","Domingo","2026-06-28","c","video_sun_0628_c",
        "Psalm 23:6 — Surely. Not Hopefully. Not Maybe.",
        "Most people treat the blessings of God as possibilities. David treated them as certainties. Psalm 23 verse 6: Surely goodness and love will follow me all the days of my life, and I will dwell in the house of the Lord forever. Surely. David had been hunted, betrayed, and broken. And he still wrote 'surely.' Goodness and mercy aren't waiting at the destination. They're following you through every day of the journey — including today. Can you see them behind you? Subscribe for a verse every day.",
        "Psalm 23:6 — Surely. Not hopefully. Not probably. David wrote this after years of being hunted and broken. Goodness and mercy follow you through every day — including the hard ones. #BibleVerse #Psalm23 #Goodness #DailyManna #Faith",
        ["bible verse","psalm 23:6","goodness","mercy","daily manna","faith","scripture","christian shorts"], 20),
]

# ── Salva W25 ──────────────────────────────────────────────────────────────────
d25 = dt.fromisoformat("2026-06-15")
y25, w25, _ = d25.isocalendar()
f25 = QUEUE_DIR / f"{y25}_W{w25:02d}.json"
f25.write_text(json.dumps(W25, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"W25 criada: {f25.name} ({len(W25)} entradas)")

# ── Salva W26 ──────────────────────────────────────────────────────────────────
d26 = dt.fromisoformat("2026-06-22")
y26, w26, _ = d26.isocalendar()
f26 = QUEUE_DIR / f"{y26}_W{w26:02d}.json"
f26.write_text(json.dumps(W26, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"W26 criada: {f26.name} ({len(W26)} entradas)")

print("\nDone.")
