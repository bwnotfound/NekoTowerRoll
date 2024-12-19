from dataclasses import dataclass
import os
import winreg
import json


@dataclass
class Config:
    url: str = "https://h5mota.com/games/51_neko_very_color_roguelike/"
    browser_type: str = "edge"  # ["chrome", "edge"]
    save_dir: str = "save"
    min_double_money_num: int = 10
    min_extra_legend_round_num: int = 8
    valid_legend_round_num: int = 26
    total_monster_num: int = 494
    mute_audio: bool = True

    def __post_init__(self):
        if ":" not in self.save_dir:
            self.save_dir = os.path.join(os.getcwd(), self.save_dir)
