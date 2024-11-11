import sys

from PyQt6.QtWidgets import *

from database.config import cur, db

from classes.TaskGroup import TaskGroup

from phrases import main_menu_phrases

LENGTH = 750  # window length
WIDTH = 500  # window width


class Planner(QWidget):
    def __init__(self):
        super().__init__()

        # DB -> Task/TaskGroup
        cur.execute("SELECT * FROM task_groups")
        task_groups = cur.fetchall()
        self.task_groups = []
        for i in task_groups:
            cur_task_group = TaskGroup(i[0], i[1])

            cur.execute(f"SELECT * FROM task_group_{i[0]}")
            cur_tasks = cur.fetchall()
            for j in cur_tasks:
                cur_task_group.add_task(*j)

            self.task_groups.append(cur_task_group)

        # Initializing window
        self.init_ui()

    def init_ui(self):
        # Initializing window
        self.setGeometry(0, 0, LENGTH, WIDTH)
        self.setWindowTitle('Планировщик')
        # Setting background colour
        self.setStyleSheet("""
        background-color: #262626;
        color: #FFFFFF;
        font-family: Titillium;
        font-size: 18px;
        """)

        # Widgets lists
        self.window_widgets = []
        self.changing_widgets = []

        # Initializing widgets
        # Button for returning to main menu
        self.to_main_menu_btn = QPushButton(self)
        self.to_main_menu_btn.setGeometry(LENGTH - 150, WIDTH - 50, 150, 50)
        self.to_main_menu_btn.setText("В главное меню")
        self.to_main_menu_btn.clicked.connect(self.to_main_menu)
        self.to_main_menu_btn.hide()

        # Main menu
        self.main_menu = QLabel(self)
        self.main_menu.setGeometry(LENGTH // 2 - 100, 50, 400, 50)
        self.main_menu.setText("Вы находитесь в главном меню.\n"
                               "Выберите действие.")

        self.main_menu_message = QLabel(self)
        self.main_menu_message.setGeometry(LENGTH // 2 - 100, 0, 400, 50)
        self.main_menu_message.setText("")

        self.add_task_group_choice = QPushButton(self)
        self.add_task_group_choice.setGeometry(0, WIDTH // 4, LENGTH // 2, int(WIDTH * 0.75))
        self.add_task_group_choice.setText("Добавить группу задач")
        self.add_task_group_choice.clicked.connect(self.add_task_group_choice_clicked)

        self.watch_task_groups_choice = QPushButton(self)
        self.watch_task_groups_choice.setGeometry(LENGTH // 2, WIDTH // 4, LENGTH // 2, int(WIDTH * 0.75))
        self.watch_task_groups_choice.setText("Просмотреть группы задач")
        self.watch_task_groups_choice.clicked.connect(self.watch_task_groups_choice_clicked)

        self.main_menu_widgets = [self.main_menu, self.add_task_group_choice, self.watch_task_groups_choice,
                                  self.main_menu_message]

        self.window_widgets.extend(self.main_menu_widgets)
        self.changing_widgets.extend([self.main_menu_message])

        # Adding new group of tasks
        self.task_group_name_input = QLabel(self)
        self.task_group_name_input.setGeometry(LENGTH // 2 - 200, 0, 400, 50)
        self.task_group_name_input.setText("Введите название новой группы.\n"
                                           "Новое название должно быть уникальным.")

        self.task_group_name = QLineEdit(self)
        self.task_group_name.setGeometry(LENGTH // 2 - 200, 50, 400, 50)
        self.task_group_name.setText("Группа")

        self.add_task_group = QPushButton(self)
        self.add_task_group.setGeometry(LENGTH // 2 - 100, 100, 200, 50)
        self.add_task_group.setText("Добавить группу")
        self.add_task_group.clicked.connect(self.add_task_group_clicked)

        self.task_group_name_exists = QLabel(self)
        self.task_group_name_exists.setGeometry(LENGTH // 2 - 200, 150, 450, 50)
        self.task_group_name_exists.setText('')

        self.add_task_group_widgets = [self.task_group_name_input, self.task_group_name, self.add_task_group,
                                       self.task_group_name_exists, self.to_main_menu_btn]

        self.window_widgets.extend(self.add_task_group_widgets)
        self.changing_widgets.extend([self.task_group_name, self.task_group_name_exists])

        for i in self.add_task_group_widgets:
            i.hide()
            
        # Watching task groups

    def to_main_menu(self):
        for i in self.window_widgets:
            i.hide()
        for i in self.changing_widgets:
            i.setText('')
        for i in self.main_menu_widgets:
            i.show()
        self.main_menu_message.setText(main_menu_phrases.back_to_main_menu)

    def add_task_group_choice_clicked(self):
        for i in self.main_menu_widgets:
            i.hide()

        for i in self.add_task_group_widgets:
            i.show()

        # Setting default name for new group of tasks
        cur.execute(f"SELECT name FROM task_groups")
        task_groups = cur.fetchall()
        cnt = 0
        for i in task_groups:
            if i[0][:6] == "Группа" and len(i[0]) > 6:
                try:
                    cur_cnt = int(i[0][6:])
                    cnt = max(cur_cnt, cnt)
                except (ValueError, TypeError):
                    pass

        self.task_group_name.setText("Группа" + str(cnt + 1))

    def add_task_group_clicked(self):
        name = self.task_group_name.text()

        cur.execute("SELECT name FROM task_groups")
        task_groups_names = cur.fetchall()

        for i in task_groups_names:
            if name == i[0]:
                self.task_group_name_exists.setText('Группа задач с таким названием уже существует.')
                break
        else:
            cur.execute("SELECT MAX(id) FROM task_groups")

            try:
                new_id = cur.fetchall()[0][0] + 1
            except (TypeError, IndexError):
                new_id = 0

            self.task_groups.append(TaskGroup(new_id, name))

            cur.execute(f"INSERT INTO task_groups VALUES (?, ?)", (new_id, name))
            cur.execute(f"CREATE TABLE task_group_{new_id} ("
                        f"name TEXT,"
                        f"urgency INTEGER,"
                        f"importance INTEGER,"
                        f"completion INTEGER"
                        f")")
            db.commit()

            # Main menu transition
            for i in self.add_task_group_widgets:
                i.hide()

            for i in self.main_menu_widgets:
                i.show()
            self.main_menu_message.setText(main_menu_phrases.new_task_group_added)

    def watch_task_groups_choice_clicked(self):
        if self.task_groups:
            pass
        else:
            self.main_menu_message.setText(main_menu_phrases.no_task_groups)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Planner()

    window.show()
    sys.exit(app.exec())
