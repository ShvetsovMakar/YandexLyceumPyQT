import sys

from PyQt6.QtWidgets import *

from database.config import cur, db

from core.classes.TaskGroup import TaskGroup
from core.phrases import (add_task_group_phrases, add_task_phrases, main_menu_phrases, task_group_menu_phrases,
                          watch_task_groups_phrases)
from core.functions.scroll_functions import is_forward, is_backward

LENGTH = 750  # window length
WIDTH = 500  # window width

TASK_GROUP_NAME_MAX_LENGTH = 10
TASK_NAME_MAX_LENGTH = 32


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
        self.to_main_menu_btn.setText(main_menu_phrases.to_main_menu)
        self.to_main_menu_btn.clicked.connect(self.to_main_menu)
        self.to_main_menu_btn.hide()

        # Main menu
        self.main_menu = QLabel(self)
        self.main_menu.setGeometry(LENGTH // 2 - 60, 50, 400, 50)
        self.main_menu.setText(main_menu_phrases.main_menu)

        self.main_menu_message = QLabel(self)
        self.main_menu_message.setGeometry(LENGTH // 2 - 100, 0, 400, 50)
        self.main_menu_message.setText("")

        self.add_task_group_choice = QPushButton(self)
        self.add_task_group_choice.setGeometry(0, WIDTH // 4, LENGTH // 2, int(WIDTH * 0.75))
        self.add_task_group_choice.setText(main_menu_phrases.add_task_group)
        self.add_task_group_choice.clicked.connect(self.add_task_group_choice_clicked)

        self.watch_task_groups_choice = QPushButton(self)
        self.watch_task_groups_choice.setGeometry(LENGTH // 2, WIDTH // 4, LENGTH // 2, int(WIDTH * 0.75))
        self.watch_task_groups_choice.setText(main_menu_phrases.watch_task_groups)
        self.watch_task_groups_choice.clicked.connect(self.watch_task_groups_choice_clicked)

        self.main_menu_widgets = [self.main_menu, self.add_task_group_choice, self.watch_task_groups_choice,
                                  self.main_menu_message]

        self.window_widgets.extend(self.main_menu_widgets)
        self.changing_widgets.extend([self.main_menu_message])

        # Adding new task groups
        self.task_group_name_input = QLabel(self)
        self.task_group_name_input.setGeometry(LENGTH // 2 - 200, 0, 400, 50)
        self.task_group_name_input.setText(add_task_group_phrases.new_task_group)

        self.task_group_name = QLineEdit(self)
        self.task_group_name.setGeometry(LENGTH // 2 - 200, 50, 400, 50)
        self.task_group_name.setText('')

        self.add_task_group = QPushButton(self)
        self.add_task_group.setGeometry(LENGTH // 2 - 100, 100, 200, 50)
        self.add_task_group.setText(add_task_group_phrases.add_group)
        self.add_task_group.clicked.connect(self.add_task_group_clicked)

        self.add_task_group_error = QLabel(self)
        self.add_task_group_error.setGeometry(LENGTH // 2 - 200, 150, 450, 50)
        self.add_task_group_error.setText('')

        self.add_task_group_widgets = [self.task_group_name_input, self.task_group_name, self.add_task_group,
                                       self.add_task_group_error, self.to_main_menu_btn]

        self.window_widgets.extend(self.add_task_group_widgets)
        self.changing_widgets.extend([self.task_group_name, self.add_task_group_error])

        for i in self.add_task_group_widgets:
            i.hide()
            
        # Watching task groups
        self.cur_task_groups = []
        for i in range(2):
            self.cur_task_groups.append([])
            for j in range(3):
                new = QPushButton(self)
                new.setGeometry(LENGTH // 5 * (1 + i) + 100 * i - 50,
                                WIDTH // 5 * (1 + j) - 50,
                                200,
                                50)
                new.clicked.connect(self.task_group_clicked)
                self.cur_task_groups[-1].append(new)

        self.watch_task_groups_forward = QPushButton(self)
        self.watch_task_groups_forward.setGeometry(LENGTH // 5 * 3 + 150, WIDTH // 5 - 50, 150, 50)
        self.watch_task_groups_forward.setText(watch_task_groups_phrases.forward)
        self.watch_task_groups_forward.clicked.connect(self.watch_task_groups_forward_clicked)

        self.watch_task_groups_backward = QPushButton(self)
        self.watch_task_groups_backward.setGeometry(LENGTH // 5 * 3 + 150, WIDTH // 5 * 3 - 50, 150, 50)
        self.watch_task_groups_backward.setText(watch_task_groups_phrases.backward)
        self.watch_task_groups_backward.clicked.connect(self.watch_task_groups_backward_clicked)

        self.watch_task_groups_widgets = []
        self.watch_task_groups_widgets.extend(self.cur_task_groups[0])
        self.watch_task_groups_widgets.extend(self.cur_task_groups[1])
        self.watch_task_groups_widgets.extend([self.watch_task_groups_forward, self.watch_task_groups_backward,
                                               self.to_main_menu_btn])

        self.window_widgets.extend(self.watch_task_groups_widgets)

        self.changing_widgets.extend(self.cur_task_groups[0])
        self.changing_widgets.extend(self.cur_task_groups[1])

        for i in self.watch_task_groups_widgets:
            i.hide()

        # Task group menu
        self.delete_task_group = QPushButton(self)
        self.delete_task_group.setGeometry(LENGTH // 5 - 125, WIDTH // 2 - 25, 200, 50)
        self.delete_task_group.setText(task_group_menu_phrases.delete_task_group)
        self.delete_task_group.clicked.connect(self.delete_task_group_clicked)

        self.show_tasks = QPushButton(self)
        self.show_tasks.setGeometry(LENGTH // 5 + 100, WIDTH // 2 - 25, 200, 50)
        self.show_tasks.setText(task_group_menu_phrases.go_to_tasks)

        self.add_task_btn = QPushButton(self)
        self.add_task_btn.setGeometry(LENGTH // 5 + 325, WIDTH // 2 - 25, 200, 50)
        self.add_task_btn.setText(task_group_menu_phrases.add_task)
        self.add_task_btn.clicked.connect(self.add_task)

        self.group_task_name = QLabel(self)
        self.group_task_name.setGeometry(LENGTH // 5 - 125, WIDTH // 2 - 100, 200, 40)
        self.group_task_name.setText('')

        self.progress = QLabel(self)
        self.progress.setGeometry(LENGTH // 5 + 325, WIDTH // 2 - 100, 200, 40)
        self.progress.setText('')

        self.task_group_menu_widgets = [self.delete_task_group, self.show_tasks, self.add_task_btn,
                                        self.group_task_name, self.progress,
                                        self.to_main_menu_btn]

        self.window_widgets.extend(self.task_group_menu_widgets)
        self.changing_widgets.extend([self.group_task_name, self.progress])

        for i in self.task_group_menu_widgets:
            i.hide()

        # Add task
        self.add_new_task_btn = QPushButton(self)
        self.add_new_task_btn.setGeometry(LENGTH // 2 + 150, WIDTH // 2 - 125, 200, 40)
        self.add_new_task_btn.setText(add_task_phrases.add_task)
        self.add_new_task_btn.clicked.connect(self.add_new_task)

        self.task_name_input = QLabel(self)
        self.task_name_input.setGeometry(LENGTH // 5 - 125, WIDTH // 2 - 150, 200, 40)
        self.task_name_input.setText(add_task_phrases.task_name)

        self.task_name = QLineEdit(self)
        self.task_name.setGeometry(LENGTH // 5 - 125, WIDTH // 2 - 100, 200, 40)
        self.task_name.setText('')

        self.task_name_error = QLabel(self)
        self.task_name_error.setGeometry(LENGTH // 5 - 125, WIDTH // 2 - 50, 400, 40)
        self.task_name_error.setText('')

        self.important = QCheckBox(self)
        self.important.setGeometry(LENGTH // 4 + 100, WIDTH // 2 - 150, 200, 40)
        self.important.setText(add_task_phrases.importance)

        self.urgent = QCheckBox(self)
        self.urgent.setGeometry(LENGTH // 4 + 100, WIDTH // 2 - 100, 200, 40)
        self.urgent.setText(add_task_phrases.urgency)

        self.add_task_group_name = QLabel(self)
        self.add_task_group_name.setGeometry(0, WIDTH - 50, 400, 50)
        self.add_task_group_name.setText('')

        self.add_task_widgets = [self.add_new_task_btn, self.task_name_input, self.task_name, self.task_name_error,
                                 self.important, self.urgent,
                                 self.add_task_group_name,
                                 self.to_main_menu_btn]

        self.changing_widgets.extend([self.task_name, self.task_name_error, self.add_task_group_name])
        self.window_widgets.extend(self.add_task_widgets)

        for i in self.add_task_widgets:
            i.hide()

        # Watch tasks

    def to_main_menu(self):
        for i in self.window_widgets:
            i.hide()
        for i in self.changing_widgets:
            i.setText('')
        for i in self.main_menu_widgets:
            i.show()

        self.important.setChecked(False)
        self.urgent.setChecked(False)

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
            if i[0].startswith("Группа") and len(i[0]) > 6:
                try:
                    cnt = max(int(i[0][6:]), cnt)
                except (ValueError, TypeError):
                    pass

        self.task_group_name.setText("Группа" + str(cnt + 1))

    def add_task_group_clicked(self):
        name = self.task_group_name.text()
        if not name:
            self.add_task_group_error.setText(add_task_group_phrases.task_group_name_empty)
            return

        if len(name) > TASK_GROUP_NAME_MAX_LENGTH:
            self.add_task_group_error.setText(add_task_group_phrases.task_group_name_too_long)
            return

        cur.execute("SELECT name FROM task_groups")
        task_groups_names = cur.fetchall()

        for i in task_groups_names:
            if name == i[0]:
                self.add_task_group_error.setText(add_task_group_phrases.task_group_name_exists)
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
            for i in self.main_menu_widgets:
                i.hide()

            for i in self.watch_task_groups_widgets:
                i.show()

            # Scroll buttons
            self.watch_task_groups_forward.hide()
            self.watch_task_groups_backward.hide()
            if is_forward(self.task_groups):
                self.watch_task_groups_forward.show()
            self.watch_task_groups_backward.hide()

            # Task Groups buttons
            for i in range(2):
                for j in range(3):
                    if i * 3 + j >= min(len(self.task_groups), 6):
                        self.cur_task_groups[i][j].hide()
                    else:
                        self.cur_task_groups[i][j].setText(self.task_groups[i * 3 + j].name)
                        self.cur_task_groups[i][j].show()

        else:
            self.main_menu_message.setText(main_menu_phrases.no_task_groups)

    def watch_task_groups_forward_clicked(self):
        name = self.cur_task_groups[0][0].text()
        for i in range(len(self.task_groups)):
            if self.task_groups[i].name == name:
                index = i
                break

        for i in range(2):
            for j in range(3):
                if index + i * 3 + j + 6 >= len(self.task_groups):
                    self.cur_task_groups[i][j].setText('')
                    self.cur_task_groups[i][j].hide()
                else:
                    self.cur_task_groups[i][j].setText(self.task_groups[index + i * 3 + j + 6].name)
        first_btn = self.cur_task_groups[0][0].text()

        # Scroll buttons
        self.watch_task_groups_forward.hide()
        self.watch_task_groups_backward.hide()
        if is_forward(self.task_groups, first_btn):
            self.watch_task_groups_forward.show()
        if is_backward(self.task_groups, first_btn):
            self.watch_task_groups_backward.show()

    def watch_task_groups_backward_clicked(self):
        name = self.cur_task_groups[0][0].text()
        for i in range(len(self.task_groups)):
            if self.task_groups[i].name == name:
                index = i
                break

        for i in range(2):
            for j in range(3):
                self.cur_task_groups[i][j].setText(self.task_groups[index + i * 3 + j - 6].name)
                self.cur_task_groups[i][j].show()
        first_btn = self.cur_task_groups[0][0].text()

        # Scroll buttons
        self.watch_task_groups_forward.hide()
        self.watch_task_groups_backward.hide()
        if is_forward(self.task_groups, first_btn):
            self.watch_task_groups_forward.show()
        if is_backward(self.task_groups, first_btn):
            self.watch_task_groups_backward.show()

    def task_group_clicked(self):
        name = self.sender().text()

        for i in self.window_widgets:
            i.hide()
        for i in self.task_group_menu_widgets:
            i.show()

        completed = 0
        for i in self.task_groups:
            if i.name == name:
                amount = len(i.tasks)
                for j in i.tasks:
                    completed += j.completion
        self.progress.setText(f"Выполнено: {completed}/{amount}")
        self.group_task_name.setText(f"Группа: {name}")

    def add_task(self):
        for i in self.window_widgets:
            i.hide()
        for i in self.add_task_widgets:
            i.show()
        self.add_task_group_name.setText(self.group_task_name.text())

        cnt = 0
        for i in self.task_groups:
            if i.name == self.group_task_name.text()[8:]:
                for j in i.tasks:
                    if j.name.startswith("Задача") and len(j.name) > 6:
                        try:
                            cnt = max(int(j.name[6:]), cnt)
                        except (ValueError, TypeError):
                            pass

        self.task_name.setText("Задача" + str(cnt + 1))

    def add_new_task(self):
        name = self.task_name.text()
        if not name:
            self.task_name_error.setText(add_task_phrases.task_name_empty)
            return

        if len(name) > TASK_NAME_MAX_LENGTH:
            self.task_name_error.setText(add_task_phrases.task_name_too_long)
            return

        group_name = self.add_task_group_name.text()[8:]
        urgency = int(self.urgent.isChecked())
        importance = int(self.important.isChecked())

        for i in self.task_groups:
            if i.name == group_name:
                for j in i.tasks:
                    if j.name == name:
                        self.task_name_error.setText(add_task_phrases.task_name_exists)
                        return

                i.add_task(name, urgency, importance, 0)
                cur.execute(f"SELECT id FROM task_groups WHERE name = \"{group_name}\"")

                task_group_id = cur.fetchall()[0][0]

                cur.execute(f"INSERT INTO task_group_{task_group_id} VALUES (?, ?, ?, ?)",
                            (name, urgency, importance, 0))
                db.commit()

            break

        for i in self.window_widgets:
            i.hide()
        for i in [self.task_name, self.task_name_error, self.add_task_group_name]:
            i.setText('')

        self.important.setChecked(False)
        self.urgent.setChecked(False)

        for i in self.watch_task_groups_widgets:
            if i.text():
                i.show()

        if not is_forward(self.task_groups, self.cur_task_groups[0][0].text()):
            self.watch_task_groups_forward.hide()
        if not is_backward(self.task_groups, self.cur_task_groups[0][0].text()):
            self.watch_task_groups_backward.hide()

    def delete_task_group_clicked(self):
        name = self.group_task_name.text()[8:]
        for i in self.task_groups:
            if i.name == name:
                self.task_groups.remove(i)
                break
        cur.execute(f"SELECT id FROM task_groups WHERE name = \"{name}\"")
        task_group_id = cur.fetchall()[0][0]

        cur.execute(f"DELETE FROM task_groups WHERE id = {task_group_id}")
        cur.execute(f"DROP TABLE task_group_{task_group_id}")
        db.commit()

        cur.execute(f"SELECT id FROM task_groups WHERE id > {task_group_id}")
        task_groups_ids = cur.fetchall()

        for i in task_groups_ids:
            cur.execute(f"UPDATE task_groups SET id = {i[0] - 1} WHERE id = {i[0]}")
            cur.execute(f"ALTER TABLE task_group_{i[0]} "
                        f"RENAME TO task_group_{i[0] - 1}")
            db.commit()

        for i in self.window_widgets:
            i.hide()
        for i in self.changing_widgets:
            i.setText('')
        for i in self.main_menu_widgets:
            i.show()

        self.main_menu_message.setText(main_menu_phrases.task_group_deleted)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Planner()

    window.show()
    sys.exit(app.exec())
