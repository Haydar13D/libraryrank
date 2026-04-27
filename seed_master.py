from leaderboard.models import PointPolicy, LevelTier, BadgeRule

PointPolicy.objects.get_or_create(action_type='visit', defaults={'points': 10})
PointPolicy.objects.get_or_create(action_type='borrow', defaults={'points': 25})

levels = [
    (0, 100, 'Visitor', 1, '#95a5a6'),
    (101, 300, 'Reader', 2, '#3498db'),
    (301, 700, 'Scholar', 3, '#2ecc71'),
    (701, 1500, 'Researcher', 4, '#9b59b6'),
    (1501, 3000, 'Sage', 5, '#e67e22'),
    (3001, None, 'Library Legend', 6, '#f1c40f')
]
for min_xp, max_xp, name, lv_num, color in levels:
    LevelTier.objects.get_or_create(level_num=lv_num, defaults={'name': name, 'min_xp': min_xp, 'max_xp': max_xp, 'color': color})

BadgeRule.objects.get_or_create(id_code='weekly_warrior', defaults={
    'name': 'Weekly Warrior', 'icon': '🥈', 'image_url': '/static/img/badges/weekly warior.png', 'color': '#bdc3c7',
    'desc': 'Datang ke perpus 3x dalam seminggu', 'criteria_type': 'visits_week', 'min_value': 3
})
BadgeRule.objects.get_or_create(id_code='library_legend', defaults={
    'name': 'Library Legend', 'icon': '🥇', 'image_url': '/static/img/badges/top 10 leaderboard.png', 'color': '#f1c40f',
    'desc': 'Top 10 Leaderboard bulan ini', 'criteria_type': 'visits_month_top10', 'min_value': 10
})
BadgeRule.objects.get_or_create(id_code='book_worm', defaults={
    'name': 'Book Worm', 'icon': '📚', 'image_url': '/static/img/badges/bookworm.png', 'color': '#9b59b6',
    'desc': 'Meminjam > 5 buku dalam 1 semester', 'criteria_type': 'borrows_semester', 'min_value': 6
})
print('Gamification Master Data Seeded!')
