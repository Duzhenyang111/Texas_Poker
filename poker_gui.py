import sys
import random
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGridLayout, QLineEdit, QMessageBox, 
                             QInputDialog, QFrame, QSizePolicy, QSpacerItem, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette, QBrush

# 导入游戏逻辑
from test11 import Card, Player, TexasHoldem

# 定义扑克牌显示类
class CardWidget(QLabel):
    def __init__(self, card=None, hidden=False, parent=None):
        super().__init__(parent)
        self.card = card
        self.hidden = hidden
        self.setFixedSize(80, 120)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid black;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.update_display()
    
    def update_display(self):
        if self.hidden:
            self.setText("🂠")
            self.setStyleSheet("""
                QLabel {
                    background-color: #2E86C1;
                    color: white;
                    border: 2px solid black;
                    border-radius: 5px;
                    font-size: 40px;
                    font-weight: bold;
                }
            """)
        elif self.card:
            # 设置花色颜色
            color = "black"
            if self.card.suit in ['♥', '♦']:
                color = "red"
            
            self.setText(f"{self.card.suit}{self.card.rank}")
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: white;
                    color: {color};
                    border: 2px solid black;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setText("")
            self.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)

# 定义玩家信息显示类
class PlayerInfoWidget(QWidget):
    def __init__(self, player, is_current=False, parent=None):
        super().__init__(parent)
        self.player = player
        self.is_current = is_current
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 玩家名称和筹码信息
        self.name_label = QLabel(f"{player.name}")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.chips_label = QLabel(f"筹码: ${player.chips}")
        self.chips_label.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel("游戏中")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.bet_label = QLabel(f"当前下注: ${player.current_bet}")
        self.bet_label.setAlignment(Qt.AlignCenter)
        
        # 添加到布局
        layout.addWidget(self.name_label)
        layout.addWidget(self.chips_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.bet_label)
        
        # 设置样式
        self.update_style()
    
    def update_info(self):
        self.chips_label.setText(f"筹码: ${self.player.chips}")
        self.status_label.setText("已弃牌" if self.player.folded else "游戏中")
        self.bet_label.setText(f"当前下注: ${self.player.current_bet}")
        self.update_style()
    
    def update_style(self):
        base_style = """
            QLabel {
                font-size: 14px;
                padding: 2px;
                border-radius: 4px;
            }
        """
        
        if self.is_current:
            self.setStyleSheet(f"""
                PlayerInfoWidget {{
                    background-color: rgba(46, 134, 193, 0.3);
                    border: 2px solid #2E86C1;
                    border-radius: 8px;
                    padding: 5px;
                }}
                {base_style}
                QLabel {{
                    background-color: rgba(255, 255, 255, 0.7);
                }}
                {self.name_label.objectName()} {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #2E86C1;
                }}
            """)
        else:
            status_color = "#E74C3C" if self.player.folded else "#2ECC71"
            self.setStyleSheet(f"""
                PlayerInfoWidget {{
                    background-color: rgba(200, 200, 200, 0.2);
                    border: 1px solid #AAAAAA;
                    border-radius: 8px;
                    padding: 5px;
                }}
                {base_style}
                QLabel {{
                    background-color: rgba(255, 255, 255, 0.5);
                }}
                {self.status_label.objectName()} {{
                    color: {status_color};
                    font-weight: bold;
                }}
            """)

# 主游戏界面
class PokerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("德州扑克游戏")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建游戏实例
        self.game = None
        self.human_player = None
        self.current_player_idx = 0
        self.round_in_progress = False
        
        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建堆叠窗口部件用于切换不同界面
        self.stacked_widget = QStackedWidget()
        
        # 创建开始界面
        self.create_start_screen()
        
        # 创建游戏界面
        self.create_game_screen()
        
        # 将堆叠窗口添加到主窗口
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)
        
        # 设置背景
        self.set_background()
        
        # 显示开始界面
        self.stacked_widget.setCurrentIndex(0)
    
    def set_background(self):
        # 设置背景颜色为深绿色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 100, 0))
        self.setPalette(palette)
    
    def create_start_screen(self):
        start_widget = QWidget()
        start_layout = QVBoxLayout(start_widget)
        
        # 添加标题
        title_label = QLabel("德州扑克游戏")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                margin: 20px;
            }
        """)
        
        # 添加输入区域
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # 玩家名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("玩家名称:")
        name_label.setStyleSheet("color: white; font-size: 16px;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入您的名称")
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border-radius: 4px;
                background-color: white;
            }
        """)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        # AI玩家数量输入
        ai_layout = QHBoxLayout()
        ai_label = QLabel("AI玩家数量:")
        ai_label.setStyleSheet("color: white; font-size: 16px;")
        self.ai_input = QLineEdit("3")
        self.ai_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border-radius: 4px;
                background-color: white;
            }
        """)
        ai_layout.addWidget(ai_label)
        ai_layout.addWidget(self.ai_input)
        
        # 添加到输入布局
        input_layout.addLayout(name_layout)
        input_layout.addLayout(ai_layout)
        
        # 开始游戏按钮
        start_button = QPushButton("开始游戏")
        start_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px 20px;
                background-color: #2E86C1;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #1A5276;
            }
        """)
        start_button.clicked.connect(self.start_game)
        
        # 添加到开始界面布局
        start_layout.addStretch(1)
        start_layout.addWidget(title_label)
        start_layout.addWidget(input_widget)
        start_layout.addWidget(start_button, alignment=Qt.AlignCenter)
        start_layout.addStretch(1)
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(start_widget)
    
    def create_game_screen(self):
        game_widget = QWidget()
        self.game_layout = QVBoxLayout(game_widget)
        
        # 创建顶部区域 - AI玩家信息
        self.top_area = QWidget()
        self.top_layout = QHBoxLayout(self.top_area)
        
        # 创建中间区域 - 公共牌和下注池
        self.middle_area = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_area)
        
        # 公共牌区域
        self.community_cards_widget = QWidget()
        self.community_cards_layout = QHBoxLayout(self.community_cards_widget)
        self.community_cards_layout.setAlignment(Qt.AlignCenter)
        self.community_cards = []
        
        # 下注池和当前下注信息
        self.pot_info = QLabel("下注池: $0")
        self.pot_info.setAlignment(Qt.AlignCenter)
        self.pot_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.3);
                padding: 5px;
                border-radius: 5px;
            }
        """)
        
        self.current_bet_info = QLabel("当前下注: $0")
        self.current_bet_info.setAlignment(Qt.AlignCenter)
        self.current_bet_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.3);
                padding: 5px;
                border-radius: 5px;
            }
        """)
        
        # 游戏状态信息
        self.game_status = QLabel("游戏准备中...")
        self.game_status.setAlignment(Qt.AlignCenter)
        self.game_status.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                background-color: rgba(0, 0, 0, 0.3);
                padding: 5px;
                border-radius: 5px;
            }
        """)
        
        # 添加到中间布局
        self.middle_layout.addWidget(self.pot_info)
        self.middle_layout.addWidget(self.current_bet_info)
        self.middle_layout.addWidget(self.community_cards_widget)
        self.middle_layout.addWidget(self.game_status)
        
        # 创建底部区域 - 玩家手牌和操作按钮
        self.bottom_area = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_area)
        
        # 玩家手牌区域
        self.player_hand_widget = QWidget()
        self.player_hand_layout = QHBoxLayout(self.player_hand_widget)
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.player_cards = []
        
        # 玩家操作按钮
        self.action_widget = QWidget()
        self.action_layout = QHBoxLayout(self.action_widget)
        
        # 创建操作按钮
        self.call_button = QPushButton("跟注")
        self.raise_button = QPushButton("加注")
        self.fold_button = QPushButton("弃牌")
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 8px 15px;
                background-color: white;
                border: 2px solid #4A4A4A;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """
        
        self.call_button.setStyleSheet(button_style)
        self.raise_button.setStyleSheet(button_style)
        self.fold_button.setStyleSheet(button_style)
        
        # 连接按钮信号
        self.call_button.clicked.connect(self.on_call)
        self.raise_button.clicked.connect(self.on_raise)
        self.fold_button.clicked.connect(self.on_fold)
        
        # 添加按钮到布局
        self.action_layout.addWidget(self.call_button)
        self.action_layout.addWidget(self.raise_button)
        self.action_layout.addWidget(self.fold_button)
        
        # 禁用按钮，直到游戏开始
        self.call_button.setEnabled(False)
        self.raise_button.setEnabled(False)
        self.fold_button.setEnabled(False)
        
        # 添加到底部布局
        self.bottom_layout.addWidget(self.player_hand_widget)
        self.bottom_layout.addWidget(self.action_widget)
        
        # 添加所有区域到游戏布局
        self.game_layout.addWidget(self.top_area)
        self.game_layout.addWidget(self.middle_area)
        self.game_layout.addWidget(self.bottom_area)
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(game_widget)
    
    def start_game(self):
        # 获取玩家名称和AI数量
        player_name = self.name_input.text().strip()
        if not player_name:
            player_name = "玩家"
        
        try:
            ai_count = int(self.ai_input.text())
            if ai_count < 1:
                ai_count = 1
            elif ai_count > 9:
                ai_count = 9
        except ValueError:
            ai_count = 3
        
        # 创建游戏实例
        self.game = TexasHoldem()
        
        # 添加人类玩家
        self.human_player = Player(player_name, 1000, is_ai=False)
        self.game.players.append(self.human_player)
        
        # 添加AI玩家
        for i in range(ai_count):
            self.game.players.append(Player(f"AI-{i+1}", 1000, is_ai=True))
        
        # 初始化游戏界面
        self.init_game_ui()
        
        # 切换到游戏界面
        self.stacked_widget.setCurrentIndex(1)
        
        # 开始第一局游戏
        self.start_new_round()
    
    def init_game_ui(self):
        # 清空顶部区域（AI玩家信息）
        self.clear_layout(self.top_layout)
        
        # 添加AI玩家信息
        self.player_info_widgets = []
        for player in self.game.players:
            if player != self.human_player:
                player_widget = PlayerInfoWidget(player)
                self.top_layout.addWidget(player_widget)
                self.player_info_widgets.append(player_widget)
        
        # 清空公共牌区域
        self.clear_layout(self.community_cards_layout)
        self.community_cards = []
        
        # 清空玩家手牌区域
        self.clear_layout(self.player_hand_layout)
        self.player_cards = []
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
    
    def start_new_round(self):
        # 初始化新一轮
        self.game.round_number += 1
        self.game.pot = 0
        self.game.community_cards = []
        self.game.current_bet = 10  # 小盲注
        
        # 重置玩家状态
        for player in self.game.players:
            player.hand = []
            player.folded = False
            player.current_bet = 0
            player.actions = []
        
        # 初始化牌组
        self.game.init_deck()
        
        # 发初始手牌
        self.game.deal_initial_cards()
        
        # 更新界面
        self.update_game_ui()
        
        # 开始第一轮下注
        self.start_betting_round('preflop')
    
    def update_game_ui(self):
        # 更新玩家信息
        for widget in self.player_info_widgets:
            widget.update_info()
        
        # 更新下注池和当前下注信息
        self.pot_info.setText(f"下注池: ${self.game.pot}")
        self.current_bet_info.setText(f"当前下注: ${self.game.current_bet}")
        
        # 更新公共牌
        self.update_community_cards()
        
        # 更新玩家手牌
        self.update_player_hand()
    
    def update_community_cards(self):
        # 清空现有公共牌
        self.clear_layout(self.community_cards_layout)
        self.community_cards = []
        
        # 添加公共牌
        for card in self.game.community_cards:
            card_widget = CardWidget(card)
            self.community_cards_layout.addWidget(card_widget)
            self.community_cards.append(card_widget)
        
        # 如果公共牌不足5张，添加空白位置
        for _ in range(5 - len(self.game.community_cards)):
            empty_card = CardWidget()
            self.community_cards_layout.addWidget(empty_card)
    
    def update_player_hand(self):
        # 清空现有手牌
        self.clear_layout(self.player_hand_layout)
        self.player_cards = []
        
        # 添加玩家手牌
        for card in self.human_player.hand:
            card_widget = CardWidget(card)
            self.player_hand_layout.addWidget(card_widget)
            self.player_cards.append(card_widget)
    
    def start_betting_round(self, round_name):
        # 更新游戏状态
        self.game_status.setText(f"{self.game.translate_round(round_name)}阶段")
        
        # 如果是翻牌、转牌或河牌阶段，发公共牌
        if round_name == 'flop':
            self.game.deal_community_cards(3)
        elif round_name in ['turn', 'river']:
            self.game.deal_community_cards(1)
        
        # 更新界面
        self.update_game_ui()
        
        # 开始玩家行动
        self.current_player_idx = 0
        self.handle_player_turn()
    
    def handle_player_turn(self):
        # 获取当前玩家
        player = self.game.players[self.current_player_idx]
        
        # 如果玩家已弃牌，跳到下一个玩家
        if player.folded:
            self.next_player()
            return
        
        # 更新当前玩家高亮
        for i, widget in enumerate(self.player_info_widgets):
            if i + 1 == self.current_player_idx:  # +1是因为人类玩家不在player_info_widgets中
                widget.is_current = True
            else:
                widget.is_current = False
            widget.update_style()
        
        # 如果是人类玩家的回合
        if player == self.human_player:
            # 启用操作按钮
            self.call_button.setEnabled(True)
            self.raise_button.setEnabled(True)
            self.fold_button.setEnabled(True)
            
            # 更新按钮文本
            bet_amount = self.game.current_bet - player.current_bet
            if bet_amount > 0:
                self.call_button.setText(f"跟注 ${bet_amount}")
            else:
                self.call_button.setText("过牌")
        else:
            # 禁用操作按钮
            self.call_button.setEnabled(False)
            self.raise_button.setEnabled(False)
            self.fold_button.setEnabled(False)
            
            # AI玩家自动行动
            QTimer.singleShot(1000, self.handle_ai_turn)
    
    def handle_ai_turn(self):
        player = self.game.players[self.current_player_idx]
        if player.is_ai:
            action, amount = self.game.ai_decision(player)
            
            if action == 'fold':
                player.folded = True
                self.game_status.setText(f"{player.name} 弃牌")
            elif action == 'call':
                bet_amount = self.game.current_bet - player.current_bet
                self.game.pot += bet_amount
                player.chips -= bet_amount
                player.current_bet = self.game.current_bet
                self.game_status.setText(f"{player.name} 跟注 ${bet_amount}")
            else:  # raise
                bet_amount = amount - player.current_bet
                self.game.current_bet = amount
                self.game.pot += bet_amount
                player.chips -= bet_amount
                player.current_bet = amount
                self.game_status.setText(f"{player.name} 加注到 ${amount}")
            
            # 更新界面
            self.update_game_ui()
            
            # 延迟一下，让玩家看清AI的行动
            QTimer.singleShot(1000, self.next_player)
    
    def next_player(self):
        # 移动到下一个玩家
        self.current_player_idx = (self.current_player_idx + 1) % len(self.game.players)
        
        # 检查是否所有玩家都行动过一次
        if self.current_player_idx == 0:
            # 检查是否所有玩家的下注都相等
            active_players = [p for p in self.game.players if not p.folded]
            bets_equal = all(p.current_bet == self.game.current_bet for p in active_players)
            
            if bets_equal:
                # 当前下注轮结束
                self.end_betting_round()
            else:
                # 继续下一个玩家行动
                self.handle_player_turn()
        else:
            # 继续下一个玩家行动
            self.handle_player_turn()
    
    def end_betting_round(self):
        # 确定当前是哪个下注轮
        if not self.game.community_cards:
            next_round = 'flop'
        elif len(self.game.community_cards) == 3:
            next_round = 'turn'
        elif len(self.game.community_cards) == 4:
            next_round = 'river'
        else:
            # 所有下注轮结束，进行摊牌
            self.showdown()
            return
        
        # 开始下一个下注轮
        self.start_betting_round(next_round)
    
    def showdown(self):
        # 更新游戏状态
        self.game_status.setText("摊牌阶段")
        
        # 确定赢家
        self.game.determine_winner()
        
        # 更新界面
        self.update_game_ui()
        
        # 显示结果
        active_players = [p for p in self.game.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            QMessageBox.information(self, "游戏结果", f"{winner.name} 获胜! 赢得 ${self.game.pot}")
        else:
            # 评估每个玩家的手牌
            player_hands = []
            for player in active_players:
                hand_value = self.game.evaluate_hand(player)
                hand_type = self.game.get_hand_type_name(hand_value[0])
                player_hands.append((player, hand_value, hand_type))
            
            # 找出最大的手牌
            best_player = player_hands[0][0]
            best_hand = player_hands[0][1]
            best_type = player_hands[0][2]
            
            for player, hand, hand_type in player_hands[1:]:
                if self.game.compare_hands(hand, best_hand) > 0:
                    best_player = player
                    best_hand = hand
                    best_type = hand_type
            
            result_text = f"{best_player.name} 获胜! 赢得 ${self.game.pot}\n\n牌型: {best_type}"
            QMessageBox.information(self, "游戏结果", result_text)
        
        # 询问是否继续游戏
        reply = QMessageBox.question(self, "继续游戏", "是否开始新一局游戏?", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            # 检查玩家筹码
            for player in self.game.players:
                if player.chips <= 0:
                    QMessageBox.information(self, "游戏提示", f"{player.name} 已经没有筹码，退出游戏!")
            
            # 移除没有筹码的玩家
            self.game.players = [p for p in self.game.players if p.chips > 0]
            
            # 检查是否有足够的玩家继续游戏
            if len(self.game.players) < 2:
                QMessageBox.information(self, "游戏结束", "游戏结束! 玩家数量不足.")
                if self.game.players:
                    QMessageBox.information(self, "最终赢家", f"{self.game.players[0].name} 是最后的赢家!")
                self.stacked_widget.setCurrentIndex(0)  # 返回开始界面
                return
            
            # 开始新一局
            self.start_new_round()
        else:
            # 显示最终结果
            result_text = "最终结果:\n"
            sorted_players = sorted(self.game.players, key=lambda p: p.chips, reverse=True)
            for i, player in enumerate(sorted_players):
                result_text += f"{i+1}. {player.name}: ${player.chips} 筹码\n"
            
            QMessageBox.information(self, "游戏结束", result_text)
            self.stacked_widget.setCurrentIndex(0)  # 返回开始界面
    
    def on_call(self):
        player = self.human_player
        bet_amount = self.game.current_bet - player.current_bet
        
        # 检查筹码是否足够
        if bet_amount > player.chips:
            QMessageBox.warning(self, "操作失败", "你的筹码不足以跟注!")
            return
        
        # 执行跟注
        self.game.pot += bet_amount
        player.chips -= bet_amount
        player.current_bet = self.game.current_bet
        player.actions.append(f"跟注 ${bet_amount}")
        
        # 更新游戏状态
        if bet_amount > 0:
            self.game_status.setText(f"{player.name} 跟注 ${bet_amount}")
        else:
            self.game_status.setText(f"{player.name} 过牌")
        
        # 禁用操作按钮
        self.call_button.setEnabled(False)
        self.raise_button.setEnabled(False)
        self.fold_button.setEnabled(False)
        
        # 更新界面
        self.update_game_ui()
        
        # 进入下一个玩家
        QTimer.singleShot(500, self.next_player)
    
    def on_raise(self):
        player = self.human_player
        min_raise = self.game.current_bet * 2
        
        # 获取加注金额
        amount, ok = QInputDialog.getInt(self, "加注", f"请输入加注金额 (最小 ${min_raise}):", 
                                        min_raise, min_raise, player.chips, 10)
        if not ok:
            return
        
        # 检查加注金额是否有效
        if amount < min_raise:
            QMessageBox.warning(self, "操作失败", f"加注金额必须至少为 ${min_raise}!")
            return
        
        # 执行加注
        bet_amount = amount - player.current_bet
        self.game.current_bet = amount
        self.game.pot += bet_amount
        player.chips -= bet_amount
        player.current_bet = amount
        player.actions.append(f"加注到 ${amount}")
        
        # 更新游戏状态
        self.game_status.setText(f"{player.name} 加注到 ${amount}")
        
        # 禁用操作按钮
        self.call_button.setEnabled(False)
        self.raise_button.setEnabled(False)
        self.fold_button.setEnabled(False)
        
        # 更新界面
        self.update_game_ui()
        
        # 进入下一个玩家
        QTimer.singleShot(500, self.next_player)
    
    def on_fold(self):
        player = self.human_player
        
        # 执行弃牌
        player.folded = True
        player.actions.append("弃牌")
        
        # 更新游戏状态
        self.game_status.setText(f"{player.name} 弃牌")
        
        # 禁用操作按钮
        self.call_button.setEnabled(False)
        self.raise_button.setEnabled(False)
        self.fold_button.setEnabled(False)
        
        # 更新界面
        self.update_game_ui()
        
        # 进入下一个玩家
        QTimer.singleShot(500, self.next_player)

# 主函数
def main():
    app = QApplication(sys.argv)
    window = PokerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()