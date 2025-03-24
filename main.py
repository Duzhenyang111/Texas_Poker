import random
import os
import datetime
from typing import List, Tuple

# 定义扑克牌类
class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.suit}{self.rank}"

# 定义玩家类
class Player:
    def __init__(self, name: str, chips: int, is_ai: bool = False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_ai = is_ai
        self.current_bet = 0
        self.folded = False
        self.actions = []  # 记录玩家在当前局的所有行动

# 定义德州扑克游戏类
class TexasHoldem:
    def __init__(self):
        self.deck = []
        self.community_cards = []
        self.pot = 0
        self.players = []
        self.current_bet = 0
        self.suits = ['♠', '♥', '♣', '♦']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.init_deck()
        self.game_log = []  # 记录游戏日志
        self.round_number = 0  # 记录当前是第几局
        
    def init_deck(self):
        self.deck = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.deck)
    
    def deal_initial_cards(self):
        for _ in range(2):
            for player in self.players:
                if not player.folded:
                    player.hand.append(self.deck.pop())
    
    def deal_community_cards(self, count: int):
        for _ in range(count):
            self.community_cards.append(self.deck.pop())
    
    def ai_decision(self, player: Player) -> Tuple[str, int]:
        # 简单AI决策逻辑
        hand_strength = random.random()  # 在实际应用中应该基于手牌强度计算
        if hand_strength > 0.7:
            return 'raise', self.current_bet * 2
        elif hand_strength > 0.3:
            return 'call', self.current_bet
        else:
            return 'fold', 0
    
    def play_round(self):
        # 初始化新一轮
        self.round_number += 1
        self.pot = 0
        self.community_cards = []
        self.current_bet = 10  # 小盲注
        self.game_log.append(f"\n===== 第 {self.round_number} 局开始 =====")
        
        # 重置玩家状态
        for player in self.players:
            player.hand = []
            player.folded = False
            player.current_bet = 0
            player.actions = []  # 重置玩家行动记录
        
        # 初始化牌组
        self.init_deck()
        
        # 发初始手牌
        self.deal_initial_cards()
        self.log_player_hands()  # 记录玩家手牌
        
        # 下注轮次
        betting_rounds = ['preflop', 'flop', 'turn', 'river']
        for round_name in betting_rounds:
            self.game_log.append(f"\n--- {self.translate_round(round_name)}阶段 ---")
            
            if round_name == 'flop':
                self.deal_community_cards(3)
                self.log_community_cards()
            elif round_name in ['turn', 'river']:
                self.deal_community_cards(1)
                self.log_community_cards()
            
            # 显示当前状态
            self.display_game_state()
            
            # 玩家行动
            active_players = [p for p in self.players if not p.folded]
            if len(active_players) <= 1:
                self.game_log.append("只剩一名玩家，本轮结束")
                break  # 如果只剩一个玩家，结束当前轮次
                
            for player in self.players:
                if player.folded:
                    continue
                    
                if player.is_ai:
                    action, amount = self.ai_decision(player)
                    action_str = self.translate_action(action)
                    print(f"\n{player.name} 选择: {action_str}")
                    
                    if action == 'fold':
                        player.folded = True
                        print(f"{player.name} 弃牌")
                        player.actions.append(f"弃牌")
                        self.game_log.append(f"{player.name} 弃牌")
                    elif action == 'call':
                        bet_amount = self.current_bet - player.current_bet
                        self.pot += bet_amount
                        player.chips -= bet_amount
                        player.current_bet = self.current_bet
                        print(f"{player.name} 跟注 ${bet_amount}")
                        player.actions.append(f"跟注 ${bet_amount}")
                        self.game_log.append(f"{player.name} 跟注 ${bet_amount}")
                    else:  # raise
                        bet_amount = amount - player.current_bet
                        self.current_bet = amount
                        self.pot += bet_amount
                        player.chips -= bet_amount
                        player.current_bet = amount
                        print(f"{player.name} 加注到 ${amount}")
                        player.actions.append(f"加注到 ${amount}")
                        self.game_log.append(f"{player.name} 加注到 ${amount}")
                else:
                    self.handle_human_player_turn(player)
    
    def handle_human_player_turn(self, player: Player):
        while True:
            self.display_player_options(player)
            try:
                choice = int(input("请输入你的选择 (1-3): "))
                if choice == 1:  # 跟注
                    bet_amount = self.current_bet - player.current_bet
                    if bet_amount > player.chips:
                        print("你的筹码不足以跟注!")
                        continue
                    self.pot += bet_amount
                    player.chips -= bet_amount
                    player.current_bet = self.current_bet
                    print(f"{player.name} 跟注 ${bet_amount}")
                    player.actions.append(f"跟注 ${bet_amount}")
                    self.game_log.append(f"{player.name} 跟注 ${bet_amount}")
                    break
                elif choice == 2:  # 加注
                    min_raise = self.current_bet * 2
                    try:
                        amount = int(input(f"请输入加注金额 (最小 ${min_raise}): "))
                        if amount < min_raise:
                            print(f"加注金额必须至少为 ${min_raise}!")
                            continue
                        if amount > player.chips:
                            print("你的筹码不足!")
                            continue
                        bet_amount = amount - player.current_bet
                        self.current_bet = amount
                        self.pot += bet_amount
                        player.chips -= bet_amount
                        player.current_bet = amount
                        print(f"{player.name} 加注到 ${amount}")
                        player.actions.append(f"加注到 ${amount}")
                        self.game_log.append(f"{player.name} 加注到 ${amount}")
                        break
                    except ValueError:
                        print("请输入有效的数字!")
                elif choice == 3:  # 弃牌
                    player.folded = True
                    print(f"{player.name} 弃牌")
                    player.actions.append(f"弃牌")
                    self.game_log.append(f"{player.name} 弃牌")
                    break
                else:
                    print("无效的选择，请重试!")
            except ValueError:
                print("请输入有效的数字!")
    
    def translate_action(self, action: str) -> str:
        if action == 'fold':
            return "弃牌"
        elif action == 'call':
            return "跟注"
        elif action == 'raise':
            return "加注"
        return action
    
    def translate_round(self, round_name: str) -> str:
        if round_name == 'preflop':
            return "底牌"
        elif round_name == 'flop':
            return "翻牌"
        elif round_name == 'turn':
            return "转牌"
        elif round_name == 'river':
            return "河牌"
        return round_name
    
    def display_game_state(self):
        print("\n" + "="*50)
        
        for player in self.players:
            status = "已弃牌" if player.folded else "游戏中"
            if not player.is_ai:
                
                print(f"\n{player.name} | 筹码: ${player.chips} | 状态: {status}")
            else:
                print(f"\n{player.name} | 筹码: ${player.chips} | 状态: {status}")
    
    def display_player_options(self, player: Player):
        print(f"公共牌: {' '.join(str(card) for card in self.community_cards)}")
        print(f"下注池: ${self.pot}")
        print(f"\n{player.name}的回合")
        print(f"\n{player.name}的手牌: {' '.join(str(card) for card in player.hand)}")
        print(f"当前下注: ${self.current_bet}")
        print("选项: 1)跟注 2)加注 3)弃牌")
    
    def get_card_value(self, rank: str) -> int:
        """获取牌面点数的数值"""
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                 '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return values.get(rank, 0)
    
    def evaluate_hand(self, player: Player) -> tuple:
        """评估玩家手牌的牌型和大小
        返回格式: (牌型等级, [牌型组成的牌值], [剩余牌值])
        牌型等级: 9-同花顺, 8-四条, 7-葫芦, 6-同花, 5-顺子, 4-三条, 3-两对, 2-一对, 1-高牌
        """
        # 合并玩家手牌和公共牌
        all_cards = player.hand + self.community_cards
        
        # 按花色分组
        suits = {}
        for card in all_cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        # 按点数分组
        ranks = {}
        for card in all_cards:
            value = self.get_card_value(card.rank)
            if value not in ranks:
                ranks[value] = []
            ranks[value].append(card)
        
        # 检查同花
        flush_cards = None
        for suit, cards in suits.items():
            if len(cards) >= 5:
                flush_cards = sorted(cards, key=lambda c: self.get_card_value(c.rank), reverse=True)
                break
        
        # 检查顺子
        straight = []
        values = sorted(ranks.keys(), reverse=True)
        
        # 特殊情况: A-5-4-3-2 顺子
        if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
            # A在这里算作1
            straight = [ranks[5][0], ranks[4][0], ranks[3][0], ranks[2][0], ranks[14][0]]
        
        # 常规顺子检查
        if not straight:
            for i in range(len(values) - 4):
                if values[i] - values[i+4] == 4:
                    straight = [ranks[values[i]][0], ranks[values[i+1]][0], 
                               ranks[values[i+2]][0], ranks[values[i+3]][0], 
                               ranks[values[i+4]][0]]
                    break
        
        # 检查同花顺
        straight_flush = None
        if flush_cards and len(flush_cards) >= 5:
            flush_values = [self.get_card_value(card.rank) for card in flush_cards]
            
            # 检查常规同花顺
            for i in range(len(flush_values) - 4):
                if flush_values[i] - flush_values[i+4] == 4:
                    straight_flush = flush_cards[i:i+5]
                    break
            
            # 检查A-5-4-3-2同花顺
            if not straight_flush and 14 in flush_values and all(v in flush_values for v in [2, 3, 4, 5]):
                ace = next(card for card in flush_cards if self.get_card_value(card.rank) == 14)
                two = next(card for card in flush_cards if self.get_card_value(card.rank) == 2)
                three = next(card for card in flush_cards if self.get_card_value(card.rank) == 3)
                four = next(card for card in flush_cards if self.get_card_value(card.rank) == 4)
                five = next(card for card in flush_cards if self.get_card_value(card.rank) == 5)
                straight_flush = [five, four, three, two, ace]
        
        # 检查四条、三条、对子等
        quads = []  # 四条
        trips = []  # 三条
        pairs = []  # 对子
        
        for value, cards in ranks.items():
            if len(cards) == 4:
                quads.append((value, cards))
            elif len(cards) == 3:
                trips.append((value, cards))
            elif len(cards) == 2:
                pairs.append((value, cards))
        
        # 按牌值排序
        quads.sort(reverse=True)
        trips.sort(reverse=True)
        pairs.sort(reverse=True)
        
        # 单牌(用于比较同等牌型的大小)
        singles = sorted([self.get_card_value(card.rank) for card in all_cards], reverse=True)
        
        # 判断牌型
        if straight_flush:
            # 同花顺
            return (9, [self.get_card_value(card.rank) for card in straight_flush], [])
        
        if quads:
            # 四条
            kicker = next(v for v in singles if v != quads[0][0])
            return (8, [quads[0][0]], [kicker])
        
        if trips and pairs:
            # 葫芦(三条+对子)
            return (7, [trips[0][0]], [pairs[0][0]])
        
        if flush_cards:
            # 同花
            return (6, [self.get_card_value(card.rank) for card in flush_cards[:5]], [])
        
        if straight:
            # 顺子
            return (5, [self.get_card_value(card.rank) for card in straight], [])
        
        if trips:
            # 三条
            kickers = [v for v in singles if v != trips[0][0]][:2]
            return (4, [trips[0][0]], kickers)
        
        if len(pairs) >= 2:
            # 两对
            kicker = next(v for v in singles if v != pairs[0][0] and v != pairs[1][0])
            return (3, [pairs[0][0], pairs[1][0]], [kicker])
        
        if pairs:
            # 一对
            kickers = [v for v in singles if v != pairs[0][0]][:3]
            return (2, [pairs[0][0]], kickers)
        
        # 高牌
        return (1, [], singles[:5])
    
    def compare_hands(self, hand1: tuple, hand2: tuple) -> int:
        """比较两手牌的大小
        返回: 1表示hand1更大, -1表示hand2更大, 0表示平局
        """
        # 首先比较牌型等级
        if hand1[0] > hand2[0]:
            return 1
        if hand1[0] < hand2[0]:
            return -1
        
        # 牌型相同，比较牌型组成的牌值
        for v1, v2 in zip(hand1[1], hand2[1]):
            if v1 > v2:
                return 1
            if v1 < v2:
                return -1
        
        # 牌型组成相同，比较剩余牌值
        for v1, v2 in zip(hand1[2], hand2[2]):
            if v1 > v2:
                return 1
            if v1 < v2:
                return -1
        
        # 完全相同，平局
        return 0
    
    def get_hand_type_name(self, hand_type: int) -> str:
        """获取牌型的名称"""
        hand_types = {
            9: "同花顺",
            8: "四条",
            7: "葫芦",
            6: "同花",
            5: "顺子",
            4: "三条",
            3: "两对",
            2: "一对",
            1: "高牌"
        }
        return hand_types.get(hand_type, "未知")
    
    def determine_winner(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n{winner.name} 获胜! 赢得 ${self.pot}")
            self.game_log.append(f"\n{winner.name} 获胜! 赢得 ${self.pot}")
            winner.chips += self.pot
            self.display_round_summary(winner)
            return
        
        # 评估每个玩家的手牌
        player_hands = []
        for player in active_players:
            hand_value = self.evaluate_hand(player)
            player_hands.append((player, hand_value))
            
            # 记录玩家的牌型
            hand_type = self.get_hand_type_name(hand_value[0])
            self.game_log.append(f"{player.name} 的牌型: {hand_type}")
            print(f"{player.name} 的牌型: {hand_type}")
        
        # 找出最大的手牌
        best_player = player_hands[0][0]
        best_hand = player_hands[0][1]
        
        for player, hand in player_hands[1:]:
            if self.compare_hands(hand, best_hand) > 0:
                best_player = player
                best_hand = hand
        
        # 检查是否有平局
        tied_players = [p for p, h in player_hands if self.compare_hands(h, best_hand) == 0]
        
        if len(tied_players) > 1:
            # 平局情况，多个玩家平分奖池
            share = self.pot // len(tied_players)
            remainder = self.pot % len(tied_players)
            
            print(f"\n平局! {', '.join(p.name for p in tied_players)} 平分奖池")
            self.game_log.append(f"\n平局! {', '.join(p.name for p in tied_players)} 平分奖池")
            
            for player in tied_players:
                player.chips += share
            
            # 如果有余数，随机分配给一个玩家
            if remainder > 0:
                lucky_player = random.choice(tied_players)
                lucky_player.chips += remainder
                print(f"{lucky_player.name} 获得额外的 ${remainder} 筹码")
                self.game_log.append(f"{lucky_player.name} 获得额外的 ${remainder} 筹码")
            
            self.display_round_summary(None, tied_players)
        else:
            # 单一赢家
            winner = best_player
            print(f"\n{winner.name} 获胜! 赢得 ${self.pot}")
            self.game_log.append(f"\n{winner.name} 获胜! 赢得 ${self.pot}")
            winner.chips += self.pot
            self.display_round_summary(winner)
    
    def display_round_summary(self, winner=None, tied_players=None):
        """显示本局游戏的详细信息"""
        print("\n" + "="*50)
        print(f"第 {self.round_number} 局结束")
        print("="*50)
        print(f"公共牌: {' '.join(str(card) for card in self.community_cards)}")
        print(f"下注池: ${self.pot}")
        print("\n所有玩家手牌和状态:")
        
        for player in self.players:
            status = "已弃牌" if player.folded else "游戏中"
            
            if tied_players and player in tied_players:
                winner_mark = " (平局获胜)"
            elif player == winner:
                winner_mark = " (获胜者)"
            else:
                winner_mark = ""
                
            print(f"\n{player.name}{winner_mark}:")
            print(f"手牌: {' '.join(str(card) for card in player.hand)}")
            print(f"筹码: ${player.chips} | 状态: {status}")
            print(f"本局行动: {', '.join(player.actions)}")
            
            if not player.folded:
                hand_value = self.evaluate_hand(player)
                hand_type = self.get_hand_type_name(hand_value[0])
                print(f"牌型: {hand_type}")
        
        self.game_log.append("\n--- 本局总结 ---")
        self.game_log.append(f"公共牌: {' '.join(str(card) for card in self.community_cards)}")
        self.game_log.append(f"下注池: ${self.pot}")
        
        for player in self.players:
            status = "已弃牌" if player.folded else "游戏中"
            
            if tied_players and player in tied_players:
                winner_mark = " (平局获胜)"
            elif player == winner:
                winner_mark = " (获胜者)"
            else:
                winner_mark = ""
                
            self.game_log.append(f"\n{player.name}{winner_mark}:")
            self.game_log.append(f"手牌: {' '.join(str(card) for card in player.hand)}")
            self.game_log.append(f"筹码: ${player.chips} | 状态: {status}")
            self.game_log.append(f"本局行动: {', '.join(player.actions)}")
            
            if not player.folded:
                hand_value = self.evaluate_hand(player)
                hand_type = self.get_hand_type_name(hand_value[0])
                self.game_log.append(f"牌型: {hand_type}")
    
    def log_player_hands(self):
        """记录所有玩家的手牌"""
        self.game_log.append("\n玩家手牌:")
        for player in self.players:
            self.game_log.append(f"{player.name}: {' '.join(str(card) for card in player.hand)}")
    
    def log_community_cards(self):
        """记录当前的公共牌"""
        self.game_log.append(f"公共牌: {' '.join(str(card) for card in self.community_cards)}")
    
    def save_game_log(self):
        """保存游戏日志到文件"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"F:\\Vscode_all\\Puke_Game\\log_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.game_log))
        print(f"\n游戏记录已保存到: {filename}")

def setup_game():
    game = TexasHoldem()
    
    # 设置玩家数量
    while True:
        try:
            human_count = int(input("请输入人类玩家数量: "))
            if human_count < 1:
                print("至少需要1名人类玩家!")
                continue
            break
        except ValueError:
            print("请输入有效的数字!")
    
    # 设置AI数量
    while True:
        try:
            ai_count = int(input("请输入AI玩家数量: "))
            if ai_count < 0:
                print("AI玩家数量不能为负数!")
                continue
            if human_count + ai_count < 2:
                print("游戏至少需要2名玩家!")
                continue
            if human_count + ai_count > 10:
                print("游戏最多支持10名玩家!")
                continue
            break
        except ValueError:
            print("请输入有效的数字!")
    
    # 创建人类玩家
    for i in range(human_count):
        name = input(f"请输入玩家 {i+1} 的名字: ")
        chips = 1000  # 默认筹码数量
        game.players.append(Player(name, chips))
    
    # 创建AI玩家
    for i in range(ai_count):
        game.players.append(Player(f"AI-{i+1}", 1000, is_ai=True))
    
    # 记录游戏初始状态
    game.game_log.append("===== 游戏开始 =====")
    game.game_log.append(f"玩家数量: {len(game.players)}")
    for player in game.players:
        game.game_log.append(f"{player.name}: ${player.chips} 筹码")
    
    return game

def main():
    print("="*50)
    print("欢迎来到德州扑克游戏!")
    print("="*50)
    
    game = setup_game()
    rounds_played = 0
    
    try:
        while True:
            rounds_played += 1
            print(f"\n开始第 {rounds_played} 局游戏...")
            
            # 检查玩家筹码
            for player in game.players:
                if player.chips <= 0:
                    print(f"{player.name} 已经没有筹码，退出游戏!")
                    game.game_log.append(f"{player.name} 已经没有筹码，退出游戏!")
            
            # 移除没有筹码的玩家
            game.players = [p for p in game.players if p.chips > 0]
            
            # 检查是否有足够的玩家继续游戏
            if len(game.players) < 2:
                print("\n游戏结束! 玩家数量不足.")
                if game.players:
                    print(f"{game.players[0].name} 是最后的赢家!")
                    game.game_log.append(f"\n游戏结束! {game.players[0].name} 是最后的赢家!")
                else:
                    game.game_log.append("\n游戏结束! 没有玩家剩余.")
                break
            
            # 进行一局游戏
            game.play_round()
            game.determine_winner()
            
            # 显示玩家当前状态
            print("\n当前玩家状态:")
            for player in game.players:
                print(f"{player.name}: ${player.chips} 筹码")
            
            # 询问是否继续游戏
            play_again = input("\n是否继续游戏? (y/n): ").lower()
            if play_again != 'y':
                print("\n游戏结束!")
                game.game_log.append("\n玩家选择结束游戏.")
                
                # 显示最终结果
                print("\n最终结果:")
                sorted_players = sorted(game.players, key=lambda p: p.chips, reverse=True)
                for i, player in enumerate(sorted_players):
                    print(f"{i+1}. {player.name}: ${player.chips} 筹码")
                    game.game_log.append(f"{i+1}. {player.name}: ${player.chips} 筹码")
                
                break
    except KeyboardInterrupt:
        print("\n\n游戏被中断!")
        game.game_log.append("\n游戏被用户中断.")
    finally:
        # 保存游戏记录
        game.save_game_log()
        print("\n感谢您的参与，再见!")

if __name__ == "__main__":
    main()
