class DealKeywords:
    deal_types: dict[int, str] = {
        0: 'long',
        1: 'short'
    }

    entry_signals: dict[int, str] = {
        0: 'Open Long',
        1: 'Open Short',
        2: 'Open Long #1',
        3: 'Open Long #2',
        4: 'Open Long #3',
        5: 'Open Long #4',
        6: 'Open Long #5',
        7: 'Open Long #6',
        8: 'Open Long #7',
        9: 'Open Long #8',
        10: 'Open Long #9',
        11: 'Open Long #10',
        12: 'Open Short #1',
        13: 'Open Short #2',
        14: 'Open Short #3',
        15: 'Open Short #4',
        16: 'Open Short #5',
        17: 'Open Short #6',
        18: 'Open Short #7',
        19: 'Open Short #8',
        20: 'Open Short #9',
        21: 'Open Short #10'
    }

    exit_signals: dict[int, str] = {
        0: 'Liquidation',
        1: 'Stop-loss',
        2: 'Take-profit #1',
        3: 'Take-profit #2',
        4: 'Take-profit #3',
        5: 'Take-profit #4',
        6: 'Take-profit #5',
        7: 'Take-profit #6',
        8: 'Take-profit #7',
        9: 'Take-profit #8',
        10: 'Take-profit #9',
        11: 'Take-profit #10',
        12: 'Take-profit',
        13: 'Close Long',
        14: 'Close Short'
    }