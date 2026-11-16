import random

from otree.api import Bot, Submission, SubmissionMustFail, cu, expect

from . import C, Consent, Contribute, Instructions, Results, Survey


class PlayerBot(Bot):
    """Joue la partie avec des contributions aléatoires et vérifie les règles."""

    def play_round(self):
        if self.round_number == 1:
            # Sans consentement, on ne passe pas
            yield SubmissionMustFail(Consent, dict())  # case non cochée
            yield Consent, dict(consent=True)
            # Une mauvaise réponse au test de compréhension est refusée
            yield SubmissionMustFail(Instructions, dict(comprehension=0))
            yield Instructions, dict(comprehension=int(C.ENDOWMENT))

        # On ne peut pas verser plus que sa dotation
        yield SubmissionMustFail(Contribute, dict(contribution=C.ENDOWMENT + 1))
        contribution = cu(random.randint(0, int(C.ENDOWMENT)))
        yield Submission(Contribute, dict(contribution=contribution, decision_seconds=1.0), check_html=False)

        # Gain = ce qu'on garde + part égale de la réserve multipliée
        g = self.group
        expected = C.ENDOWMENT - contribution + g.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
        expect(abs(float(self.player.payoff - expected)) < 0.01, True)
        yield Results

        if self.round_number == C.NUM_ROUNDS:
            yield Survey, dict(age=40, profession='Viticulteur ou viticultrice', strategy='Test')
            # Un seul tour payé
            paid = [p for p in self.player.in_all_rounds() if p.payoff > 0]
            expect(len(paid) <= 1, True)
