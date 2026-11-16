"""Jeu de bien public : l'eau partagée entre viticulteurs.

Chaque participant reçoit une dotation de jetons (« unités d'eau ») et décide
combien en verser dans la réserve commune. La réserve est multipliée puis
répartie à parts égales. Deux conditions : avec ou sans information sur la
contribution moyenne du groupe au tour précédent (norme sociale).
"""
import random

from otree.api import *

doc = __doc__


class C(BaseConstants):
    NAME_IN_URL = 'irrigation'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 5
    ENDOWMENT = cu(20)
    MULTIPLIER = 1.8


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    # Groupes fixes sur toute la partie (partenaires), mélangés au tour 1.
    if subsession.round_number == 1:
        subsession.group_randomly()
    else:
        subsession.group_like_round(1)
    # Un tour tiré au hasard sera payé (fixé une fois, reproductible via le seed).
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.payoff_round = random.randint(1, C.NUM_ROUNDS)


class Group(BaseGroup):
    total_contribution = models.CurrencyField(initial=0)
    individual_share = models.CurrencyField(initial=0)


class Player(BasePlayer):
    consent = models.BooleanField(
        label="J'accepte de participer et que mes réponses soient enregistrées de façon anonyme.",
        widget=widgets.CheckboxInput,
        blank=True,
    )
    contribution = models.CurrencyField(
        min=0,
        max=C.ENDOWMENT,
        label="Combien de points d'eau versez-vous dans la réserve commune ?",
    )
    comprehension = models.IntegerField(
        label="Si personne ne verse rien, combien de points d'eau gardez-vous à la fin du tour ?",
        min=0,
    )
    decision_seconds = models.FloatField(blank=True)
    # Questionnaire final
    age = models.IntegerField(label='Votre âge', min=16, max=99)
    profession = models.StringField(
        label='Votre activité',
        choices=['Viticulteur ou viticultrice', 'Étudiant ou étudiante', 'Autre'],
    )
    strategy = models.LongStringField(
        label='En quelques mots, comment avez-vous choisi vos contributions ?',
        blank=True,
    )


# ---------- Fonctions ----------

def set_payoffs(group: Group):
    players = group.get_players()
    group.total_contribution = sum(p.contribution for p in players)
    group.individual_share = group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    for p in players:
        p.payoff = C.ENDOWMENT - p.contribution + group.individual_share


def previous_group_average(player: Player):
    if player.round_number == 1:
        return None
    prev = player.group.in_round(player.round_number - 1)
    return prev.total_contribution / C.PLAYERS_PER_GROUP


def comprehension_error_message(player: Player, value):
    if value != C.ENDOWMENT:
        return "Pas tout à fait : sans versement, vous gardez toute votre dotation. Relisez les règles."


def custom_export(players):
    """Export « une ligne par décision », prêt pour R ou pandas."""
    yield [
        'session', 'participant', 'round', 'group', 'condition',
        'contribution', 'group_total', 'round_gain', 'paid_round', 'decision_seconds',
    ]
    for p in players:
        if p.field_maybe_none('contribution') is None:
            continue
        yield [
            p.session.code,
            p.participant.code,
            p.round_number,
            p.group.id_in_subsession,
            'norme' if p.session.config.get('show_norm') else 'base',
            p.contribution,
            p.group.total_contribution,
            C.ENDOWMENT - p.contribution + p.group.individual_share,
            p.round_number == p.participant.vars.get('payoff_round'),
            p.field_maybe_none('decision_seconds'),
        ]


# ---------- Pages ----------

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if not values['consent']:
            return 'Le consentement est nécessaire pour participer.'


class Instructions(Page):
    form_model = 'player'
    form_fields = ['comprehension']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution', 'decision_seconds']

    @staticmethod
    def vars_for_template(player: Player):
        avg = previous_group_average(player)
        return dict(
            show_norm=player.session.config.get('show_norm') and avg is not None,
            previous_average=avg,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = 'Les autres viticulteurs décident encore…'


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            kept=C.ENDOWMENT - player.contribution,
            others=', '.join(str(p.contribution) for p in player.get_others_in_group()),
        )


class Survey(Page):
    form_model = 'player'
    form_fields = ['age', 'profession', 'strategy']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        paid = player.participant.payoff_round
        paid_payoff = player.in_round(paid).payoff
        # Seul le tour tiré au sort compte : on remet les autres à zéro.
        for p in player.in_all_rounds():
            p.payoff = paid_payoff if p.round_number == paid else cu(0)


class End(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            paid_round=player.participant.payoff_round,
            total=player.participant.payoff_plus_participation_fee(),
        )


page_sequence = [Consent, Instructions, Contribute, ResultsWaitPage, Results, Survey, End]
