from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from training.episode import Episode


@dataclass
class TrainingReport:
    completed_episodes: int
    failed_episodes: int
    average_turns: float
    reward_distribution: Dict[str, int]


class Trainer:
    def train(self, episodes: Iterable[Episode]) -> TrainingReport:
        episodes_list: List[Episode] = list(episodes)
        completed = [episode for episode in episodes_list if episode.status == "completed"]
        failed = [episode for episode in episodes_list if episode.status == "failed"]
        average_turns = (
            sum(len(episode.turns) for episode in completed) / len(completed)
            if completed
            else 0.0
        )
        reward_distribution = {
            "positive": sum(1 for episode in completed if (episode.final_reward or 0) > 0),
            "zero": sum(1 for episode in completed if (episode.final_reward or 0) == 0),
            "negative": sum(1 for episode in completed if (episode.final_reward or 0) < 0),
        }
        return TrainingReport(
            completed_episodes=len(completed),
            failed_episodes=len(failed),
            average_turns=average_turns,
            reward_distribution=reward_distribution,
        )
