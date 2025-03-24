import random
from itertools import combinations
import sys

HAND_RANKS = {
    'HIGH_CARD': 0,
    'ONE_PAIR': 1,
    'TWO_PAIR': 2,
    'THREE_OF_KIND': 3,
    'STRAIGHT': 4,
    'FLUSH': 5,
    'FULL_HOUSE': 6,
    'FOUR_OF_KIND': 7,
    'STRAIGHT_FLUSH': 8,
    'ROYAL_FLUSH': 9
}

class Card:
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    VALUE_MAP = {rank:i for i, rank in enumerate(RANKS)}
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    
    def value(self):
        return self.VALUE_MAP[self.rank]

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = []
        self.is_ai = is_ai
        self.folded = False
        self.chips = 1000
        self.bet = 0
        
    def __repr__(self):
        return f"{self.name}({'AI' if self.is_ai else 'Human'}, 筹码:{self.chips})"

class TexasHoldem:
    def __init__(self, num_players, num_ais):
        self.deck = self._create_deck()
        self.players = [Player(f"玩家{i+1}") for i in range(num_players)]
        self.players += [Player(f"AI-{i+1}", is_ai=True) for i in range(num_ais)]
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.stage = "pre-flop"
        self.round_count = 1
        
    def _create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        deck = [Card(s, r) for s in suits for r in ranks]
        random.shuffle(deck)
        return deck
    
    def deal_hole_cards(self):
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.pop())
                
    def deal_community(self, num_cards):
        for _ in range(num_cards):
            self.community_cards.append(self.deck.pop())
            
    def evaluate_hand(self, player):
        all_cards = player.hand + self.community_cards
        best_rank = (-1, [])
        
        for combo in combinations(all_cards, 5):
            sorted_values = sorted([c.value() for c in combo], reverse=True)
            suits = [c.suit for c in combo]
            
            is_flush = len(set(suits)) == 1
            straight = self._check_straight(sorted_values)
            
            if straight and is_flush:
                rank = HAND_RANKS['ROYAL_FLUSH'] if sorted_values == [12,11,10,9,8] else HAND_RANKS['STRAIGHT_FLUSH']
            elif self._check_kind(4, sorted_values):
                rank = HAND_RANKS['FOUR_OF_KIND']
            elif self._check_kind(3, sorted_values) and self._check_kind(2, sorted_values):
                rank = HAND_RANKS['FULL_HOUSE']
            elif is_flush:
                rank = HAND_RANKS['FLUSH']
            elif straight:
                rank = HAND_RANKS['STRAIGHT']
            elif self._check_kind(3, sorted_values):
                rank = HAND_RANKS['THREE_OF_KIND']
            elif self._check_two_pair(sorted_values):
                rank = HAND_RANKS['TWO_PAIR']
            elif self._check_kind(2, sorted_values):
                rank = HAND_RANKS['ONE_PAIR']
            else:
                rank = HAND_RANKS['HIGH_CARD']
            
            if rank > best_rank[0]:
                best_rank = (rank, sorted_values)
                
        return best_rank

    def _check_straight(self, values):
        if len(set(values)) < 5:
            return False
        if sorted(values) == [0,1,2,3,12]:
            return True
        return all(values[i] == values[0]-i for i in range(5))

    def _check_kind(self, count, values):
        return any(values.count(v) >= count for v in set(values))
    
    def _check_two_pair(self, values):
        pairs = [v for v in set(values) if values.count(v) >= 2]
        return len(pairs) >= 2

    def ai_decision(self, player):
        hand_strength = self.evaluate_hand(player)[0]
        pot_odds = self.pot / (self.current_bet - player.bet + 1e-8)
        
        if hand_strength >= HAND_RANKS['STRAIGHT']:
            return 'raise'
        if hand_strength >= HAND_RANKS['TWO_PAIR'] and pot_odds > 2:
            return 'call'
        if random.random() < 0.15:
            return 'raise'
        return 'fold'

    def clear_line(self):
        """使用ANSI控制符清除当前行 <button class="citation-flag" data-index="6">"""
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()

    def print_status(self, player):
        """格式化覆盖输出当前状态 <button class="citation-flag" data-index="3"><button class="citation-flag" data-index="6">"""
        self.clear_line()
        sys.stdout.write(f"------ 第{self.round_count}轮 ------\n")
        sys.stdout.write(f"池注：{self.pot}  当前注：{self.current_bet}\n")
        sys.stdout.write(f"公共牌：{self.community_cards}\n")
        sys.stdout.write(f"您（{player.name}）的手牌：{player.hand}\n")
        sys.stdout.write(f"操作选择(call/raise/fold)：")
        sys.stdout.flush()
        
    def betting_round(self):
        active_players = [p for p in self.players if not p.folded]
        for player in active_players:
            if player.folded:
                continue
                
            if player.is_ai:
                action = self.ai_decision(player)
                self.clear_line()
                print(f"\n{player.name} 选择 {action.upper()}")
            else:
                self.print_status(player)
                action = input().strip().lower()
                
            if action == 'fold':
                player.folded = True
            elif action == 'raise':
                self.pot += self.current_bet * 2
                player.chips -= self.current_bet * 2
                self.current_bet *= 2
            elif action == 'call':
                self.pot += self.current_bet
                player.chips -= self.current_bet
                
            self.round_count += 1

    def show_all_hands(self):
        print("\n=== 所有手牌公示 ===")
        for player in self.players:
            status = "存活" if not player.folded else "弃牌"
            print(f"{player.name} ({status}): {player.hand} -> {self.evaluate_hand(player)[0]}")
            
    def play(self):
        self.deal_hole_cards()
        stages = [
            ("翻牌前", 0),
            ("翻牌", 3),
            ("转牌", 1),
            ("河牌", 1)
        ]
        
        for stage_name, num_cards in stages:
            self.stage = stage_name
            if num_cards > 0:
                self.deal_community(num_cards)
                print(f"\n=== {stage_name}阶段 ===")
                print("公共牌:", self.community_cards)
                
            self.betting_round()
            
        self.show_all_hands()
        winner = max(self.players, key=lambda p: self.evaluate_hand(p)[0])
        print(f"\n胜者: {winner.name} 获得{self.pot}筹码！")

if __name__ == "__main__":
    game = TexasHoldem(num_players=1, num_ais=2)
    game.play()