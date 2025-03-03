import random
from collections import defaultdict

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name, is_robot=False, chips=1000):
        self.name = name
        self.hand = []
        self.chips = chips
        self.is_robot = is_robot
        self.folded = False
        self.current_bet = 0

    def reset(self):
        self.hand = []
        self.folded = False
        self.current_bet = 0

    def decide_action(self, current_bet, min_raise):
        if self.is_robot:
            return self.robot_strategy(current_bet, min_raise)
        else:
            return self.human_input(current_bet)

    def robot_strategy(self, current_bet, min_raise):
        if self.chips <= 0:
            return ('check', 0)

        action_options = ['call', 'fold']
        if current_bet == 0:
            action_options.append('check')
        if self.chips >= min_raise:
            action_options.append('raise')

        choice = random.choice(action_options)
        
        if choice == 'raise':
            raise_amount = random.randint(min_raise, min(self.chips, min_raise*2))
            return ('raise', raise_amount)
        elif choice == 'call' and current_bet > 0:
            return ('call', current_bet)
        elif choice == 'fold':
            return ('fold', 0)
        else:
            return ('check', 0)

    def human_input(self, current_bet):
        print(f"\nYour hand: {self.hand}")
        print(f"Current bet: {current_bet}, Your chips: {self.chips}")
        while True:
            action = input("Choose action (call/raise/fold/check): ").lower()
            if action == 'raise':
                amount = int(input("Enter raise amount: "))
                if amount >= current_bet * 2 and amount <= self.chips:
                    return ('raise', amount)
            elif action == 'call':
                if current_bet <= self.chips:
                    return ('call', current_bet)
            elif action == 'fold':
                return ('fold', 0)
            elif action == 'check' and current_bet == 0:
                return ('check', 0)
            print("Invalid action!")

class PokerGame:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = 50

    def reset_game(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        for player in self.players:
            player.reset()

    def deal_hole_cards(self):
        for _ in range(2):
            for player in self.players:
                if not player.folded:
                    player.hand.append(self.deck.deal())

    def betting_round(self, is_preflop=False):
        active_players = [p for p in self.players if not p.folded]
        last_raiser = None
        bets_cleared = False

        while not bets_cleared:
            bets_cleared = True
            for player in active_players:
                if player.folded or player == last_raiser:
                    continue

                action, amount = player.decide_action(self.current_bet, self.min_raise)
                print(f"{player.name} {action}s {amount if amount else ''}")

                if action == 'fold':
                    player.folded = True
                elif action == 'call':
                    diff = self.current_bet - player.current_bet
                    player.chips -= diff
                    player.current_bet += diff
                    self.pot += diff
                elif action == 'raise':
                    self.current_bet += amount
                    player.chips -= amount
                    player.current_bet += amount
                    self.pot += amount
                    last_raiser = player
                    bets_cleared = False
                elif action == 'check':
                    continue

            # 检查所有玩家是否平注
            active_players = [p for p in self.players if not p.folded]
            if all(p.current_bet == self.current_bet for p in active_players):
                break

    def deal_community_cards(self, num_cards):
        for _ in range(num_cards):
            self.community_cards.append(self.deck.deal())

    def evaluate_hand_strength(self):
        """评估手牌强度（0-1范围）"""
        if len(self.hand) < 2:
            return 0.0

        rank_values = {'2':2, '3':3, '4':4, '5':5, '6':6, 
                      '7':7, '8':8, '9':9, '10':10, 
                      'J':11, 'Q':12, 'K':13, 'A':14}
        c1, c2 = self.hand
        r1, r2 = rank_values[c1.rank], rank_values[c2.rank]
        max_r, min_r = max(r1, r2), min(r1, r2)
        
        # 对子判断
        if r1 == r2:
            return 0.8 + max_r/140  # 对子基础强度0.8-0.95
        
        suited = c1.suit == c2.suit
        gap = max_r - min_r
        connected = gap == 1
        
        # 强度计算
        strength = max_r/140 + min_r/280
        if suited: strength += 0.12
        if connected: strength += 0.1
        if gap == 0: strength += 0.15  # 对子已处理
        if gap == 2: strength += 0.05
        
        return min(strength, 1.0)

    def robot_strategy(self, current_bet, min_raise):
        """改进的机器人策略"""
        strength = self.evaluate_hand_strength()
        chips_ratio = self.chips / 1000  # 初始筹码比例
        
        action_prob = {
            'fold': max(0, 0.4 - strength*0.8),
            'call': 0.3 + strength*0.3,
            'raise': 0.3 + strength*0.5,
            'check': 0.2 - strength*0.1
        }
        
        # 根据当前注额调整选项
        valid_actions = []
        if current_bet == 0:
            valid_actions.extend(['check', 'raise'])
        else:
            valid_actions.extend(['call', 'fold', 'raise'])
        
        # 移除无效选项
        action_prob = {k:v for k,v in action_prob.items() if k in valid_actions}
        
        # 标准化概率
        total = sum(action_prob.values())
        rand = random.uniform(0, total)
        cumulative = 0
        for action, prob in action_prob.items():
            cumulative += prob
            if rand <= cumulative:
                chosen_action = action
                break
        
        # 处理具体动作
        if chosen_action == 'raise':
            base_raise = max(min_raise, int(current_bet * 1.5))
            raise_amount = int(base_raise * (0.8 + strength*0.5))
            raise_amount = min(raise_amount, self.chips)
            return ('raise', raise_amount) if raise_amount >= min_raise else ('call', current_bet)
        
        if chosen_action == 'call':
            call_amount = min(current_bet, self.chips)
            return ('call', call_amount)
        
        if chosen_action == 'check':
            return ('check', 0)
        
        return ('fold', 0)

    def show_down(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            return [active_players[0]]

        scores = []
        for player in active_players:
            full_hand = player.hand + self.community_cards
            score = self.evaluate_hand(full_hand)
            scores.append((score, player))
        
        max_score = max(scores)[0]
        winners = [p for s, p in scores if s == max_score]
        return winners

    def play_round(self):
        self.reset_game()
        self.deal_hole_cards()
        
        # Pre-flop
        print("\n--- Pre-flop ---")
        self.betting_round(is_preflop=True)
        
        # Flop
        print("\n--- Flop ---")
        self.deal_community_cards(3)
        print(f"Community cards: {self.community_cards[:3]}")
        self.betting_round()
        
        # Turn
        print("\n--- Turn ---")
        self.deal_community_cards(1)
        print(f"Community cards: {self.community_cards[:4]}")
        self.betting_round()
        
        # River
        print("\n--- River ---")
        self.deal_community_cards(1)
        print(f"Community cards: {self.community_cards}")
        self.betting_round()
        
        # Showdown
        winners = self.show_down()
        prize = self.pot // len(winners)
        for winner in winners:
            winner.chips += prize
            print(f"{winner.name} wins {prize} chips!")
        
        # 显示玩家筹码
        print("\nFinal chips:")
        for player in self.players:
            print(f"{player.name}: {player.chips}")

        # 新增显示手牌部分
        print("\nPlayers' hands:")
        for player in self.players:
            status = "(folded)" if player.folded else ""
            print(f"{player.name} {status}: {player.hand}")



if __name__ == "__main__":
    # 创建玩家
    players = [
        Player("Human", is_robot=False),
        Player("Robot1", is_robot=True),
        Player("Robot2", is_robot=True)
    ]

    # 开始游戏
    game = PokerGame(players)
    while True:
        game.play_round()
        if any(player.chips <= 0 for player in players):
            print("Game over!")
            break
        cont = input("\nPlay another round? (y/n): ")
        if cont.lower() != 'y':
            break