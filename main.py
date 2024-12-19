import time
import os
import datetime
import math

from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.common.by import By
from tqdm import tqdm

from config import Config


def start_browser():
    # start browser
    if config.browser_type == "chrome":
        options = webdriver.ChromeOptions()
        if config.mute_audio:
            options.add_argument("--mute-audio")
        options.add_argument(
            '--unsafely-disable-devtools-self-xss-warnings'
        )  # 禁用站点隔离功能
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': config.save_dir,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(options=options)
    elif config.browser_type == "edge":
        options = webdriver.EdgeOptions()
        if config.mute_audio:
            options.add_argument("--mute-audio")
        options.add_argument('--unsafely-disable-devtools-self-xss-warnings')
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': config.save_dir,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Edge(options=options)
    else:
        raise ValueError("Invalid browser type")
    return browser


def save_current_to_local(msg=None):
    '''
    var bw_save_local_callback = function callback(saves) {
        if (saves) {
            var content = {
                "name": core.firstData.name,
                "version": core.firstData.version,
                "data": saves
            };
            core.download({save_path}, LZString.compressToBase64(JSON.stringify(content)))
        }
    };
    '''
    # 首先需要保存一下
    browser.execute_script('core.control.doSL(core.saves.saveIndex, "save");')

    if msg is None:
        msg = ''
    file_name = "_".join(
        [
            "NekoTower",
            datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
            f'{msg}.h5save',
        ]
    )
    callback = (
        'bw_save_local_callback = function callback(saves){if (saves){var content = {"name": core.firstData.name, "version": core.firstData.version, "data": saves}; core.download("'
        + file_name
        + '", LZString.compressToBase64(JSON.stringify(content)))}};'
    )
    save_command = 'core.getSave(core.saves.saveIndex, bw_save_local_callback);'
    browser.execute_script(callback + save_command)
    time.sleep(0.5)


def get_legend_buffs():
    result = browser.execute_script('return core.getFlag("legendBuffs", 0);')
    return [math.floor(x) for x in result]


def get_legend_buff_infos():
    '''
    [[1, '怪物金币+30%(0.00%)'],    # 此词条作为占位用, 等同null
    [2, '幸运金币收益+50%(0.00%)'],
    [3, '血瓶收益+50%(乘算基准:1.00)'],
    [4, '宝石收益+25%(红蓝基准:1.00/1.00)'],
    [5, '攻防+15%'],
    [6, '攻击+20%'],
    [7, '防御+20%'],
    [8, '生命翻倍'],
    [9, '金币+2000'],
    [10, '获得一克破墙镐'],
    [11, '获得一台中心对称飞'],
    [12, '获得一杯上楼器'],
    [13, '重置商店购买次数'],
    [14, '获得一块圣水'],
    [15, '金币翻倍'],
    [16, '金币-2000,获得一栋地震卷轴(可欠钱)'],
    [17, '攻防互换'],
    [18, '怪物金币+30%(0.00%)']]
    '''
    return browser.execute_script('return core.enemys.getLegendBuffs();')


def get_legend_rounds():
    all_rounds = browser.execute_script('return core.getFlag("randomBuffs", 0);')
    legend_rounds = []
    for i, p in enumerate(all_rounds):
        if p < 1:
            legend_rounds.append(i + 1)
    legend_rounds = [x for x in legend_rounds if x < config.total_monster_num]
    return legend_rounds


def get_legend_options():
    buffs = get_legend_buffs()
    buff_infos = get_legend_buff_infos()
    options = []
    assert len(buffs) % 2 == 0
    for i in range(0, len(buffs), 2):
        options.append([buff_infos[buffs[i]], buff_infos[buffs[i + 1]]])
    return options


def reset_game():
    # browser.execute_script('core.events.startGame("");')
    # browser.execute_script(
    #     'core.resetGame(core.firstData.hero, "", null, core.cloneArray(core.initStatus.maps));'
    # )

    browser.execute_script(
        '''
        bw_func = function(){
            var normalBuff = [];
            var badBuff = [];
            var legendBuff = [];
            var randomBuff = [];
            var normalBuffTime = 0;
            var badBuffTime = 0;
            var legendBuffTime = 0;
            var randomBuffTime = 0;
            core.setFlag("allLegendBuff", 0);
            for (var i = 0; i < 2000; i++) {
                normalBuff[i] = Math.abs(core.rand()) * 64 + 1;
                badBuff[i] = Math.abs(core.rand()) * 36 + 1;
                legendBuff[i] = Math.abs(core.rand()) * 17 + 1;
                randomBuff[i] = Math.abs(core.rand()) * 100;
            }
            core.setFlag("normalBuffs", normalBuff);
            core.setFlag("badBuffs", badBuff);
            core.setFlag("legendBuffs", legendBuff);
            core.setFlag("randomBuffs", randomBuff)
            core.setFlag("normalBuffTimes", normalBuffTime);
            core.setFlag("badBuffTimes", badBuffTime);
            core.setFlag("legendBuffTimes", legendBuffTime);
            core.setFlag("randomBuffTimes", randomBuffTime)
        };
        bw_func();
    '''
    )


if __name__ == "__main__":
    config = Config()
    if not os.path.exists(config.save_dir):
        os.makedirs(config.save_dir)
    browser: WebDriver = start_browser()
    browser.get(config.url)
    browser.implicitly_wait(30)
    # start game
    while True:
        try:
            # 查找 id="playGame" 的 span 元素
            element = browser.find_element(By.ID, 'playGame')

            # 判断元素是否可见
            if element.is_displayed():
                break
        except:
            time.sleep(0.3)
            continue
    browser.execute_script('main.dom.playGame.click()')
    time.sleep(1)
    t_bar = tqdm()
    t_bar.set_postfix_str("success_cnt: 0")
    retry_count = 0
    max_retry = 10
    success_count = 0
    while retry_count < max_retry:
        try:
            while True:
                reset_game()
                t_bar.update()
                legend_rounds = get_legend_rounds()
                if (
                    len(legend_rounds) < config.min_extra_legend_round_num
                    or legend_rounds[0] > 3
                ):
                    continue
                legend_options = get_legend_options()
                if not any([option[0] == 16 for option in legend_options[0]]):
                    continue
                double_cnt = 0
                for option in legend_options[
                    : len(legend_rounds) + config.valid_legend_round_num
                ]:
                    if any([x[0] == 15 for x in option]):
                        double_cnt += 1
                if double_cnt < config.min_double_money_num:
                    continue
                save_current_to_local(
                    '地震卷轴开局_{}_{}双倍金钱'.format(
                        double_cnt, config.valid_legend_round_num + len(legend_rounds)
                    )
                )
                success_count += 1
                t_bar.set_postfix_str(f"success_cnt: {success_count}")
                break
        except Exception as e:
            retry_count += 1
            print(e)
            continue
        retry_count = 0
    t_bar.close()
    browser.quit()
    print('done')
