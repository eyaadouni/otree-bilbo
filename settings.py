from os import environ

SESSION_CONFIGS = [
    dict(
        name='irrigation_base',
        display_name="Bien commun : l'eau partagée (condition de base)",
        app_sequence=['irrigation'],
        num_demo_participants=3,
        show_norm=False,
    ),
    dict(
        name='irrigation_norme',
        display_name="Bien commun : l'eau partagée (avec information sur le groupe)",
        app_sequence=['irrigation'],
        num_demo_participants=3,
        show_norm=True,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.10,
    participation_fee=5.00,
    doc="Jeu de bien public présenté comme la gestion d'une réserve d'eau commune entre viticulteurs.",
)

PARTICIPANT_FIELDS = ['payoff_round']
SESSION_FIELDS = []

LANGUAGE_CODE = 'fr'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ROOMS = [
    dict(name='labo', display_name='Salle du laboratoire (tablettes)'),
    dict(name='terrain', display_name='Session sur le terrain'),
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Démo d'une expérience d'économie comportementale : trois viticulteurs décident
combien d'eau verser dans une réserve commune.
"""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'dev-only-change-me')
