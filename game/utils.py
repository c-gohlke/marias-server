# -*- coding: utf-8 -*-

def get_card(card_val):
    color = int((card_val - 1) / 13)

    strength = card_val % 13
    if strength == 0:  # is king
        strength = 13
    elif strength == 10:
        strength = 14  # 0 is better than king
    elif strength == 1:
        strength = 15  # ace beats evertything
    return [color, strength]


def valid_plays(hand, first_played_card, second_played_card, trump):
    fcard1_info = None

    fcard1_info = get_card(first_played_card)
    fcard2_info = None
    if second_played_card:
        fcard2_info = get_card(second_played_card)

    # check if has color
    hand_info = [
        get_card(card)
        for card in hand]

    play_validity = [False for i in range(len(hand_info))]
    same_color = [False for i in range(len(hand_info))]
    is_trump = [False for i in range(len(hand_info))]

    for i in range(len(hand_info)):
        card = hand_info[i]
        if card[0] == fcard1_info[0]:
            same_color[i] = True
            # player has color of first played card
            # if there is a second card played (we are player 3)
            if fcard2_info:
                """first 2 cards are same colour -> play higher than max,
                or trump"""
                if fcard2_info[0] == fcard1_info[0]:
                    if card[1] > max(fcard2_info[1], fcard1_info[1]):
                        play_validity[i] = True
                # player2 doesn't have colour and trumped
                elif fcard2_info[0] == trump:
                    # must play any card of initial colour
                    play_validity[i] = True
                else:  # player2 played no trump or initial colour
                    if card[1] > fcard1_info[1]:
                        play_validity[i] = True
            elif card[1] > fcard1_info[1]:
                play_validity[i] = True

    if (not any(play_validity)) and any(same_color):
        """if there are cards of the same color, but none was allowed
        to be played in first checking round
        than play any card of that colour"""
        play_validity = same_color

    if not any(play_validity):
        # still no valid plays until now -> must play trump
        for i in range(len(hand_info)):
            card = hand_info[i]
            if card[0] == trump:
                is_trump[i] = True
                if (not fcard2_info or
                    (fcard2_info[0] == trump and card[1] > fcard2_info[1])
                        or not trump == fcard2_info[0]):
                    """we are player 2, our card is trump and first card
                    is not trump
                    -> play any trump
                    we are player 3, first card is not trump and player2
                    didn't play trump. We don't have first cards color
                    (else would have resolved round 1)
                    -> play any trump
                    we are player 3, first card is not trump and player 2
                    played trump. We know player 1 didn't play trump or
                    else valid plays would have resolved in first round
                    (same colour) we know current player(3) doesn't have
                    first played card's colour, or it would have
                    resolved in round1
                    -> we play any trump higher than player2's trump
                    """
                    play_validity[i] = True

    if not any(play_validity) and any(is_trump):
        """none of the trumps we have were allowed during round3 of
        validation checks (means player 2 played trump bigger than any
        we have), but we must still play trump because we don't have
        player 1s color -> play any trump"""
        play_validity = is_trump

    if not any(play_validity):
        """still no valid plays untill now -> we have no trump
        or cards of initial colour
        -> play anything"""
        play_validity = [True for i in range(len(hand))]

    return play_validity
