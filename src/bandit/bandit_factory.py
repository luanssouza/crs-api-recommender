from src.bandit.base_bandit import Bandit
from src.bandit.egreedy import EGreedyBandit
from src.bandit.random import RandomBandit
from src.bandit.thompson_sampling import ThompsonSamplingBandit
from src.bandit.ucb import UCBBandit

def bandit_factory(algorithm:str = "ThompsonSampling", arms:int = 2) -> Bandit:
    """
    Bandit Factory Method

    Parameters
    ----------
    algorithm : str
        EGreedy, Random, ThompsonSampling or UCB.
        Default ThompsonSampling.

    arms : int
        Probability distribution of each arm.
        Default 2.

    Returns:
    ----------
    A Bandit instance.
    """

    bandits = {
        "EGreedy": EGreedyBandit,
        "Random": RandomBandit,
        "ThompsonSampling": ThompsonSamplingBandit,
        "UCB": UCBBandit
    }

    return bandits[algorithm](arms)