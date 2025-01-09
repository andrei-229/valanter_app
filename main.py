import sys

import gspread

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget, QFileDialog
from PyQt5.QtCore import Qt

from dotenv import load_dotenv

import subprocess
import os
import pandas as pd
import openpyxl
import requests


def check_update():
        global version_installed

        headers = {'Authorization': f'Bearer {TOKEN}'}
        # version_installed = open('updater/version.v', 'r').readline()
        response = requests.get(url, headers=headers)
        release_data = response.json()
        version_release = release_data['tag_name']  # Получите версию релиза
        # print(version_installed, release_data, version_release != version_installed)
        return version_release != version_installed


class MainWindow(QMainWindow):  # главное окно 
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/меин.ui', self)

        self.create_event.clicked.connect(self.openCreate)
        self.events_but.clicked.connect(self.events)
        self.update_but.clicked.connect(self.update)
        self.student.clicked.connect(self.student_f)


    def openCreate(self):
        self.CreateEvent = CreateEvent(self, '')
        self.CreateEvent.show()
        self.close()

    def events(self):
        self.Events_List = Events_List(self, '')
        self.Events_List.show()
        self.close()


    def update(self):
        print(check_update())
        if not(check_update()):
            self.NoN_Update = NoN_Update()
            self.NoN_Update.show()
            return
        self.Update = Update_App()
        self.Update.show()

    def student_f(self):
        self.Pred_Load_Add = Pred_Load_Add(self)
        self.Pred_Load_Add.show()
        self.close()


class NoN_Update(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('qt/non_update.ui', self)


class Update_App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('qt/update.ui', self)
        self.new_student_btn.clicked.connect(self.update)

    def update(self):
        exe_path = "./updater/up.exe"
        os.chdir(d)
        subprocess.Popen(exe_path) # Запуск .exe файла
        self.close()
        QApplication.quit()


class Pred_Load_Add(QMainWindow):  # окно выбора добавления или поиска студента
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/add_and_find_s.ui', self)
        self.new_student_btn.clicked.connect(self.open_create)
        self.from_baze_btn.clicked.connect(self.open_search)
        self.back_but.clicked.connect(self.back)

    def open_create(self):
        self.Create_St = Create_St(self)
        self.Create_St.show()
        self.close()

    def open_search(self):
        self.Load_Student = Load_Student(self)
        self.Load_Student.show()
        self.close()
    def back(self):
        self.myclose = False
        self.Main = MainWindow(self, '')
        self.Main.show()
        self.close()


class Create_St(QMainWindow): # Создание нового студентаs
    def __init__(self, *args):
        global wks2
        super().__init__()
        uic.loadUi('qt/create_and_add.ui', self)

        self.add_student_btn.clicked.connect(self.create_and_add)
        self.back_but.clicked.connect(self.back_add)

    def create_and_add(self):
        if self.input_fio.text() and self.num_kurs.text() and self.num_group.text() and self.num_inst.text():
            list_stud = wks2.get('A:I')
            list_id = [int(i) for i in wks2.col_values(1)]
            new_list = [[max(list_id) + 1, self.input_fio.text(), self.num_kurs.text(), self.num_group.text(), '0', '0', '0', '-1', self.num_inst.text()]]
            list_stud.append(new_list[0])
            list_stud = sorted(list_stud, key=lambda x: x[1].title())  # сортировка по ФИО
            wks2.update(list_stud, f'A1')
            print(list_stud)
            self.Student = Student(new_list[0])
            self.Student.show()
            self.close()  # необходимо перезагрузить таблицу, чтобы добавленный студент увиделся в ней.
        else:
            pass

    def back_add(self):
        self.Pred_Load_Add = Pred_Load_Add(self)
        self.Pred_Load_Add.show()
        self.close()


class Load_Student(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/load_student.ui', self)

        self.back_but.clicked.connect(self.back_main)
        self.download_btn.clicked.connect(self.load)
        self.find_student.clicked.connect(self.search_student)
        self.delete_student_but.clicked.connect(self.delet_win)
        self.list_students.horizontalHeader().sectionClicked.connect(self.sort_column)
        self.type_sort = 0

        self.list_studs = wks2.get("A:I")
        self.draw_columns(self.list_studs)

    def draw_columns(self, list_stud):
        print(type(self.list_students))
        self.list_students.clear()
        self.list_students.setColumnCount(7)

        self.list_students.setRowCount(0)
        self.list_students.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.list_students.setHorizontalHeaderItem(1, QTableWidgetItem("№ Института"))
        self.list_students.setHorizontalHeaderItem(2, QTableWidgetItem("Курс"))
        self.list_students.setHorizontalHeaderItem(3, QTableWidgetItem("Группа"))
        self.list_students.setHorizontalHeaderItem(4, QTableWidgetItem("Кол-во внут."))
        self.list_students.setHorizontalHeaderItem(5, QTableWidgetItem("Кол-во внеш."))
        self.list_students.setHorizontalHeaderItem(6, QTableWidgetItem("Суммарные часы"))

        for i, row in enumerate(list_stud):

            self.list_students.setRowCount(

                self.list_students.rowCount() + 1)
            row = [row[0], row[1], row[8], row[2], row[3], row[4], row[5], row[6], row[7]]

            for j, elem in enumerate(row[1:]):

                self.list_students.setItem(

                    i, j, QTableWidgetItem(str(elem)))

    def back_main(self):
        self.Pred_Load_Add = Pred_Load_Add(self, '')
        self.Pred_Load_Add.show()
        self.close()

    def search_student(self):
        search_text = self.input_fio.text()
        if search_text == '':
            self.draw_columns(self.list_studs)
            return
        
        new_list = []
        for i in self.list_studs:
            if search_text.lower() in str(i[1]).lower():
                new_list.append(i)

        self.draw_columns(new_list)

    def delet_win(self):
        rows = list(set([i.row() for i in self.list_students.selectedItems()]))

        ids = [[self.list_students.item(i, j).text() for j in range(7)] for i in rows]
        if len(ids) > 0:
            mes = 'Вы действительно хотите удалить выбранного студента?' if len(ids) == 1 else 'Вы действительно хотите удалить выбранных студентов?'
            self.Delet_S = DeleteWindow(self, mes)
            self.Delet_S.show()

    def load(self):
        global wks1, all_students
        rows = list(set([i.row() for i in self.list_students.selectedItems()]))

        ids = [[self.list_students.item(i, j).text() for j in range(7)] for i in rows]
        new_list = []
        if len(ids) > 0:
            for i in self.list_studs:
                if ids[0][0].lower() == str(i[1]).lower():
                    new_list.append(i)
                    break
            self.Student = Student(new_list[0])
            self.Student.show()
            self.close()
    
    def sort_column(self, index):
        self.type_sort += 1
        list_stud = []

        for i in self.list_studs:
            list_stud.append([i[0], i[1], int(i[8]), int(i[2]), i[3], int(i[4]), int(i[5]), int(i[6]), i[7]])
        list_stud = sorted(list_stud, key=lambda x: x[index+1], reverse=self.type_sort%2)
        for i in range(len(list_stud)):
            list_stud[i] = [list_stud[i][0], list_stud[i][1], list_stud[i][3], list_stud[i][4], list_stud[i][5], list_stud[i][6], list_stud[i][7], list_stud[i][8], list_stud[i][2]]
        self.draw_columns(list_stud)

    def delete_student(self):
        self.list_studs = wks2.get("A:I")
        rows = list(set([i.row() for i in self.list_students.selectedItems()]))

        ids = [[self.list_students.item(i, j).text() for j in range(7)] for i in rows]
        if len(ids) > 0:
            for i in ids:
                for j in self.list_studs:
                    if i[0].lower() == str(j[1]).lower():
                        self.list_studs.remove(j)
            wks2.clear()
            self.list_studs = sorted(self.list_studs, key=lambda x: x[1].title())  # сортировка по ФИО
            wks2.update(self.list_studs, "A1")
            self.draw_columns(self.list_studs)   
        

class Student(MainWindow):
    def __init__(self, student):
        super().__init__()
        uic.loadUi('qt/student.ui', self)

        self.student = student
        print(self.student)
        self.back_but.clicked.connect(self.back)
        self.save_btn.clicked.connect(self.save)
        self.events_list_btn.clicked.connect(self.events_list_s)

        self.input_fio.setText(self.student[1])
        self.num_inst.setText(self.student[8])
        self.num_kurs.setText(self.student[2])
        self.num_group.setText(self.student[3])
        self.in_events.setText(self.student[4])
        self.out_events.setText(self.student[5])
        self.time_total.setText(self.student[6])

    def save(self):
        self.list_studs = wks2.get("A:I")
        new_fio = self.input_fio.text()
        new_num_inst = self.num_inst.text()
        new_num_kurs = self.num_kurs.text()
        new_num_group = self.num_group.text()
        new_in_events = self.in_events.text()
        new_out_events = self.out_events.text()
        new_time_total = self.time_total.text()

        for i in range(len(self.list_studs)):
            if str(self.student[0]) == str(self.list_studs[i][0]):
                self.list_studs[i][1] = new_fio
                self.list_studs[i][8] = new_num_inst
                self.list_studs[i][2] = new_num_kurs
                self.list_studs[i][3] = new_num_group
                self.list_studs[i][4] = str(int(new_in_events))
                self.list_studs[i][5] = str(int(new_out_events))
                self.list_studs[i][6] = str(int(new_time_total))
                break
        print(self.list_studs)
        self.list_studs = sorted(self.list_studs, key=lambda x: x[1].title())  # сортировка по ФИО
        wks2.update(self.list_studs, f'A1')

    def events_list_s(self):
        self.Events_List_Stedent = Events_List_Stedent(self.student)
        self.Events_List_Stedent.show()
        self.close()


    def back(self):
        self.myclose = False
        self.Load_Student = Load_Student(self)
        self.Load_Student.show()
        self.close()


class Events_List_Stedent(QMainWindow):
    def __init__(self, student):
        super().__init__()
        uic.loadUi('qt/list_of_events.ui', self)
        self.student = student
        self.event_list = []
        self.itog = []
        self.draw_columns()

        self.but_back.clicked.connect(self.back)
        self.delete_student_but.clicked.connect(self.delet_event_window)
        self.add_student_but.clicked.connect(self.add_event_window)

    def draw_columns(self):
        self.event.clear()
        self.event.setColumnCount(6)

        self.event.setRowCount(0)
        self.event.setHorizontalHeaderItem(0, QTableWidgetItem("Название"))
        self.event.setHorizontalHeaderItem(1, QTableWidgetItem("Дата"))
        self.event.setHorizontalHeaderItem(2, QTableWidgetItem("Длительность"))
        self.event.setHorizontalHeaderItem(3, QTableWidgetItem("Тип (Внут/внеш)"))
        self.event.setHorizontalHeaderItem(4, QTableWidgetItem("Организатор"))
        self.event.setHorizontalHeaderItem(5, QTableWidgetItem("Площадка"))
        self.event_list = wks1.get("A:G")
        stud_list = self.student[7].split(';')
        self.itog = []
        for i in stud_list:
            for j in self.event_list[1:]:
                if str(i) == str(j[0]):
                    self.itog.append(j)
                    break

        for i, row in enumerate(self.itog):

            self.event.setRowCount(

                self.event.rowCount() + 1)

            for j, elem in enumerate(row[1:]):

                self.event.setItem(

                    i, j, QTableWidgetItem(str(elem)))

    def delete_event(self):
        global wks2
        rows = list(set([i.row() for i in self.event.selectedItems()]))

        ids = [[self.event.item(i, j).text() for j in range(6)] for i in rows]
        ev = self.student[7].split(';')
        all_s = wks2.get("A:I")
        for i in ids:
            print(i)
            for j in self.event_list:
                if i[0] == j[1] and i[1] == j[2]:
                    ev.remove(j[0])
                    print(i)
                    self.student[4] = str(int(self.student[4]) - 1 if i[3] == 'Внутреннее' else self.student[4])
                    self.student[5] = str(int(self.student[5]) - 1 if i[3] == 'Внешнее' else self.student[5])
                    self.student[6] = str(int(self.student[6]) - int(i[2]))
                    break
                    
        self.student[7] = ";".join(ev) if len(ev) > 0 else '-1'
        for i in range(len(all_s)):
            if all_s[i][0] == self.student[0]:
                all_s[i][4] = self.student[4]
                all_s[i][5] = self.student[5]
                all_s[i][6] = self.student[6]
                all_s[i][7] = self.student[7]
                wks2.update(all_s, f'A1')
                self.draw_columns()
                break


    def delet_event_window(self):
        rows = list(set([i.row() for i in self.event.selectedItems()]))
        print(rows)
        ids = [[self.event.item(i, j).text() for j in range(6)] for i in rows]
        mes = "Вы действительно хотите удалить выбранное мероприятие?" if len(ids) == 1 else "Вы действительно хотите удалить выбранные мероприятия?"
        self.delete_window = DeleteWindow(self, mes)
        self.delete_window.show()

    def add_event_window(self):
        self.Add_event_S = Add_event_S(self.itog, self.student, self)
        self.Add_event_S.show()
                
    def back(self):
        self.Student = Student(self.student)
        self.Student.show()
        self.close()


class Add_event_S(QMainWindow):
    def __init__(self, list_events, student, parent):
        super().__init__()
        uic.loadUi('qt/only_add.ui', self)
        self.list_events = list_events
        self.add_btn.clicked.connect(self.add_e)
        self.add_btn.setText('Добавить мероприятие')
        self.back_but.hide()
        self.search_btn.clicked.connect(self.search_event)
        self.new_list = []
        self.student = student
        self.parent = parent
        self.all_list = wks1.get("A:G")
        self.add_event()

    def draw_columns(self, list_events):
        self.table_students.clear()
        self.table_students.setColumnCount(6)

        self.table_students.setRowCount(0)
        self.table_students.setHorizontalHeaderItem(0, QTableWidgetItem("Название"))
        self.table_students.setHorizontalHeaderItem(1, QTableWidgetItem("Дата"))
        self.table_students.setHorizontalHeaderItem(2, QTableWidgetItem("Длительность"))
        self.table_students.setHorizontalHeaderItem(3, QTableWidgetItem("Тип (Внут/внеш)"))
        self.table_students.setHorizontalHeaderItem(4, QTableWidgetItem("Организатор"))
        self.table_students.setHorizontalHeaderItem(5, QTableWidgetItem("Площадка"))

        for i, row in enumerate(list_events):

            self.table_students.setRowCount(

                self.table_students.rowCount() + 1)

            for j, elem in enumerate(row[1:]):

                self.table_students.setItem(

                    i, j, QTableWidgetItem(str(elem)))

    def add_event(self):
        self.new_list = []
        for i in self.all_list[1:]:
            if i not in self.list_events:
                self.new_list.append(i)

        self.draw_columns(self.new_list)

    def search_event(self):
        search_text = self.input_name.text()
        if search_text == '':
            self.add_event()
            return
        
        new_lists = []
        for i in self.new_list:
            print(i)
            if search_text.lower() in str(i[1]).lower():
                new_lists.append(i)

        self.draw_columns(new_lists)

    def add_e(self):
        rows = list(set([i.row() for i in self.table_students.selectedItems()]))

        ids = [[self.table_students.item(i, j).text() for j in range(6)] for i in rows]

        ev = self.student[7].split(';')
        for i in ids:
            print(i)
            for j in self.all_list:
                print(i, j, i[0] == j[1] and i[1] == j[2])
                if i[0] == j[1] and i[1] == j[2]:
                    print(i)
                    self.student[4] = str(int(self.student[4]) + 1 if i[3] == 'Внутреннее' else self.student[4])
                    self.student[5] = str(int(self.student[5]) + 1 if i[3] == 'Внешнее' else self.student[5])
                    self.student[6] = str(int(self.student[6]) + int(i[2]))
                    ev.append(j[0])
                    break
        self.student[7] = ";".join(ev) if len(ev) > 0 else '-1'
        print(self.student)
        all_s = wks2.get("A:I")
        for i in range(len(all_s)):
            if all_s[i][0] == self.student[0]:
                all_s[i][4] = self.student[4]
                all_s[i][5] = self.student[5]
                all_s[i][6] = self.student[6]
                all_s[i][7] = self.student[7]
                wks2.update(all_s, f'A1')
                self.parent.draw_columns()
        self.close()


class Not_Update(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/non_update.ui', self)


class CreateEvent(QMainWindow):

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/create_event.ui', self)
        self.myclose = True
        self.back_but.clicked.connect(self.back_main)
        self.but_create.clicked.connect(self.create_event)


    def create_event(self):
        global wks1, all_events
        name_event = str(self.name_event.text())
        date_event = str(self.date_event.text())
        hours_event = str(self.hours_event.text())
        vnut_radio = self.vnut_radio.isChecked()
        author_event = str(self.author_event.text())
        list_id = [int(i) for i in wks1.col_values(1)[1:]]
        platform_event = str(self.input_platform.text())
        try:
            wks1.update([[max(list_id) + 1, name_event, date_event, hours_event, "Внутреннее" if vnut_radio else "Внешнее", author_event, platform_event]], f'A{len(list_id)+2}')
        except ValueError:
            wks1.update([[1, name_event, date_event, hours_event, "Внутреннее" if vnut_radio else "Внешнее", author_event, platform_event]], f'A2')
        all_events = wks1.get("A:G")
        self.back_main()

    def back_main(self):
        self.myclose = False
        self.Main = MainWindow(self, '')
        self.Main.show()
        self.close()


class Events_List(QMainWindow):

    def __init__(self, *args):
        super().__init__()

        uic.loadUi('qt/event.ui', self)

        self.but_back.clicked.connect(self.back_main)
        self.download_but.clicked.connect(self.download_event)
        self.delete_but.clicked.connect(self.delete_event_window)
        self.add_student_but.clicked.connect(self.add_student)
        self.delete_student_but.clicked.connect(self.delete_stud_window)
        self.export_btn.clicked.connect(self.export)
        self.edit_but.clicked.connect(self.edit_event_window)

        for i in all_events[1:]:
            self.list_events.addItem(f"{str(i[1])} - {str(i[2])}")

    def back_main(self):
        self.myclose = False
        self.Main = MainWindow(self, '')
        self.Main.show()
        self.close()

    def download_event(self):
        self.list_stud = wks2.get("A:I")

        self.event.setColumnCount(4)

        self.event.setRowCount(0)
        self.event.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.event.setHorizontalHeaderItem(1, QTableWidgetItem("№ Института"))
        self.event.setHorizontalHeaderItem(2, QTableWidgetItem("Курс"))
        self.event.setHorizontalHeaderItem(3, QTableWidgetItem("Группа"))

        # list_id = wks2.col_values(8)
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                ide = i[0]
                break

        list_stud = []
        for i in self.list_stud:
            # print(str(ide) in str(i[7]).split(';'))
            if str(ide) in str(i[7]).split(';'):
                # print(i)
                list_stud.append([i[1], i[8], i[2], i[3]])

        # Заполняем таблицу элементами

        for i, row in enumerate(list_stud):

            self.event.setRowCount(

                self.event.rowCount() + 1)

            for j, elem in enumerate(row):

                self.event.setItem(

                    i, j, QTableWidgetItem(str(elem)))
                
    def delete_event_window(self):
        self.delete_window = DeleteWindow(self, "Вы действительно хотите удалить выбранное мероприятие?")
        self.delete_window.show()

    def delete_stud_window(self):
        rows = list(set([i.row() for i in self.event.selectedItems()]))

        ids = [[self.event.item(i, j).text() for j in range(3)] for i in rows]
        s = 'Вы действительно хотите удалить выбранного студента?' if len(ids)==1 else 'Вы действительно хотите удалить выбранных студентов?'
        self.delete_window = DeleteWindow(self, s)
        self.delete_window.show()
                
    def delete_event(self):
        global wks1, wks2, all_events

        self.list_stud = wks2.get("A:I")
        selected_value = self.list_events.currentText().split(' - ')[0]

        ide = 0
        id_for_s = 0
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                id_for_s = i
                break
            ide += 1

        for i in range(len(self.list_stud)):
            events_s = self.list_stud[i][7].split(';')
            if str(id_for_s[0]) in events_s:
                events_s.remove(str(id_for_s[0]))
                self.list_stud[i][4] = int(self.list_stud[i][4]) - 1 if id_for_s[4] == 'Внутреннее' else self.list_stud[i][4]
                self.list_stud[i][5] = int(self.list_stud[i][5]) - 1 if id_for_s[4] == 'Внешнее' else self.list_stud[i][5]
                self.list_stud[i][6] = int(self.list_stud[i][6]) - int(id_for_s[3])
                self.list_stud[i][7] = ';'.join(events_s) if len(events_s) > 0 else '-1'
        wks2.update(self.list_stud, f'A1')
        
        self.list_events.setCurrentIndex(ide+1)
        self.list_events.removeItem(int(ide))
        wks1.delete_rows(ide+2)
        self.event.clear()
        all_events = wks1.get("A:G")

    def add_student(self):
        event_list = 0
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        all_events = wks1.get("A:G")
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                ide = i[0]
                event_list = i
                break
        self.Add_Stud = Add_Stud(self, event_list)
        self.Add_Stud.show()

    def delete_student(self):
        global wks1, wks2, all_events
        ev = 0
        rows = list(set([i.row() for i in self.event.selectedItems()]))

        ids = [[self.event.item(i, j).text() for j in range(3)] for i in rows]
        selected_value = self.list_events.currentText().split(' - ')[0]
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                ev = i
                break

        for i in range(len(self.list_stud)):
            сount = 0
            for j in ids:
                if j[0] == self.list_stud[i][1]:
                    print(self.list_stud[i][7])
                    events_s = self.list_stud[i][7].split(';')
                    events_s.remove(str(ev[0]))
                    events_s = ';'.join(events_s)
                    events_s = -1 if events_s == '' else events_s
                    dlit = str(int(self.list_stud[i][6]) - int(ev[3]))
                    cnt_vnut = int(self.list_stud[i][4]) - 1 if ev[4] == 'Внутреннее' else self.list_stud[i][4]
                    cnt_vnesh = int(self.list_stud[i][5]) - 1 if ev[4] == 'Внешнее' else self.list_stud[i][5]

                    self.list_stud[i][4] = int(self.list_stud[i][4]) - 1 if ev[4] == 'Внутреннее' else self.list_stud[i][4]
                    self.list_stud[i][5] = int(self.list_stud[i][5]) - 1 if ev[4] == 'Внешнее' else self.list_stud[i][5]
                    self.list_stud[i][6] = str(int(self.list_stud[i][6]) - int(ev[3]))
                    self.list_stud[i][7] = events_s
                    break
        self.list_stud = sorted(self.list_stud, key=lambda x: x[1].title())
        wks2.update(self.list_stud, 'A1')
        self.download_event()

    def export(self):
        dirlist = QFileDialog.getExistingDirectory(self,"Выбрать папку",".")
        print(dirlist)
        if dirlist == '': return
        global wks1, wks2, all_events
        ev = 0
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        id_for_s = 0
        event_author = ''
        event_dlit = ''
        event_type = ''
        event_date = ''
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                id_for_s = i[0]
                event_date = i[2]
                event_dlit = i[3]
                event_type = i[4]
                event_author = i[5]
                event_platform = i[6]
                break
            ide += 1
        try:
            stud = self.list_stud
        except AttributeError:
            stud = wks2.get("A:I")
        arr = {'ФИО': [], '№ Института': [], 'Курс': [], 'Группа': [], 'Кол-во внутренних': [], 'Кол-во внешних': [], 'Сумма часов': []}
        for i in range(len(stud)):
            studq = stud[i][7].split(';')
            if str(id_for_s) in studq:
                arr['ФИО'].append(stud[i][1])
                arr['№ Института'].append(stud[i][8])
                arr['Курс'].append(stud[i][2])
                arr['Группа'].append(stud[i][3])
                arr['Кол-во внутренних'].append(stud[i][4])
                arr['Кол-во внешних'].append(stud[i][5])
                arr['Сумма часов'].append(stud[i][6])
        print(arr)
        
        df = pd.DataFrame(arr, index=[i for i in range(1, len(arr['ФИО'])+1)])

        try:
            df.to_excel(f'{dirlist}/Отчет по \'{str(selected_value)}\'.xlsx')
        except PermissionError:
            print('Закрой файл, ДЕБИЛ')

        wb = openpyxl.load_workbook(f'{dirlist}/Отчет по \'{str(selected_value)}\'.xlsx')
        sheet = wb['Sheet1']

        sheet['J1'].value = f'Событие:'
        sheet['K1'].value = str(selected_value)

        sheet['J2'].value = f'Автор:'
        sheet['K2'].value = str(event_author)

        sheet['J3'].value = f'Дата проведения:'
        sheet['K3'].value = str(event_date)

        sheet['J4'].value = f'Длительность проведения:'
        sheet['K4'].value = str(event_dlit)

        sheet['J5'].value = f'Тип события:'
        sheet['K5'].value = str(event_type)

        sheet['J6'].value = f'Площадка проведения:'
        sheet['K6'].value = str(event_platform)
        try:
            wb.save(f'{dirlist}/Отчет по \'{str(selected_value)}\'.xlsx')
        except PermissionError:
            print('Закрой файл, ДЕБИЛ')
        print('Done')

    def edit_event_window(self):
        global wks1, wks2, all_events
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                ide = i
                break
        try:
            self.Edit_Event = Edit_Event(self, ide, self.list_stud)
        except AttributeError:
            self.list_stud = wks2.get("A:I")
            self.Edit_Event = Edit_Event(self, ide, self.list_stud)
        self.Edit_Event.show()
        self.close()


class Edit_Event(QMainWindow): # Класс для редактирования события.
    def __init__(self, parent, event_list, list_stud):
        super().__init__()
        uic.loadUi('qt/edit_event.ui', self)
        self.back_but.clicked.connect(self.back_main)

        self.event_list = event_list
        self.list_stud = list_stud

        self.name_event.setText(event_list[1])
        self.date_event.setText(event_list[2])
        self.hours_event.setText(event_list[3])
        self.author_event.setText(event_list[5])
        self.input_platform.setText(event_list[6])
        self.vnesh_radio.setChecked(True if event_list[4] == 'Внешнее' else False)
        self.vnut_radio.setChecked(True if event_list[4] == 'Внутреннее' else False)
        self.save_but.clicked.connect(self.save_event)

    def back_main(self):
        self.Event = Events_List()
        self.Event.show()
        self.close()

    def save_event(self):
        global wks1, wks2, all_events
        self.event_list2 = self.event_list[:]  # ID
        self.event_list2[1] = self.name_event.text()
        self.event_list2[2] = self.date_event.text()
        delta = int(self.hours_event.text()) - int(self.event_list[3])
        self.event_list2[3] = self.hours_event.text()
        self.event_list2[4] = 'Внутреннее' if self.vnut_radio.isChecked() else 'Внешнее'
        self.event_list2[5] = self.author_event.text()
        self.event_list2[6] = self.input_platform.text()
        if delta != 0:
            for j in range(len(self.list_stud)):
                studq = self.list_stud[j][7].split(';')
                if str(self.event_list[0]) in studq:
                    self.list_stud[j][6] = str(int(self.list_stud[j][6]) + delta)
        print(self.event_list[4], self.event_list[4] == 'Внутреннее', self.vnut_radio.isChecked(), self.event_list[4] == 'Внешнее', self.vnesh_radio.isChecked())
        if not((self.event_list[4] == 'Внутреннее') == self.vnut_radio.isChecked()) or not((self.event_list[4] == 'Внешнее') == self.vnesh_radio.isChecked()):
            print(1)
            for j in range(len(self.list_stud)):
                studq = self.list_stud[j][7].split(';')
                if str(self.event_list[0]) in studq:
                    self.list_stud[j][4] = int(self.list_stud[j][4]) + 1 if self.vnut_radio.isChecked() else int(self.list_stud[j][4]) -1
                    self.list_stud[j][5] = int(self.list_stud[j][5]) + 1 if self.vnesh_radio.isChecked() else int(self.list_stud[j][5]) -1
        for i in range(len(all_events)):
            if str(all_events[i][0]) == str(self.event_list[0]):
                all_events[i] = self.event_list2
                break
        wks1.update(all_events, 'A1')
        wks2.update(self.list_stud, 'A1')
        self.back_main()


class DeleteWindow(QMainWindow): # Класс для удаления события.
    def __init__(self, parent, mes):
        super().__init__()

        uic.loadUi('qt/delete_pod.ui', self)

        self.parent = parent
        self.label.setText(mes)
        self.mes = mes

        self.yes_btn.clicked.connect(self.delete_event)
        self.no_btn.clicked.connect(self.back_main)

    def delete_event(self):
        print(self.mes)
        print(self.mes == 'Вы действительно хотите удалить выбранное мероприятие?')
        if self.mes == 'Вы действительно хотите удалить выбранное мероприятие?' or self.mes == 'Вы действительно хотите удалить выбранные мероприятия?':
            self.parent.delete_event()
        else:
            self.parent.delete_student()
        self.close()

    def back_main(self):
        self.close()


class Add_Stud(QMainWindow): # Класс для добавления нового студента к событию.
    def __init__(self, parent, event_list):
        super().__init__()

        uic.loadUi('qt/add_s.ui', self)

        self.new_student_btn.clicked.connect(self.new_student)
        self.from_baze_btn.clicked.connect(self.iz_baz)

        self.parent = parent
        self.event_list = event_list

    def new_student(self):
        self.Create_And_Add = Create_And_Add(self.parent, self.event_list)
        self.Create_And_Add.show()
        self.close()

    def iz_baz(self):
        self.Add_Student_Baz = Add_Student_Baz(self.parent, self.event_list, [])
        self.Add_Student_Baz.show()
        self.close()
        

class Create_And_Add(QMainWindow): # Класс для создания нового студента и добавления его к событию.
    def __init__(self, parent, event_list):
        super().__init__()

        uic.loadUi('qt/create_and_add.ui', self)

        self.add_student_btn.clicked.connect(self.create_and_add)
        self.back_but.clicked.connect(self.back_add)

        self.parent = parent
        self.event_list = event_list

    def create_and_add(self):
        if self.input_fio.text() and self.num_kurs.text() and self.num_group.text() and self.num_inst.text():
            list_id = [int(i) for i in wks2.col_values(1)]
            cnt_vnut = 0 if self.event_list[4] != 'Внутреннее' else 1
            cnt_vnesh = 0 if self.event_list[4]!= 'Внешнее' else 1
            list_stud = wks2.get("A:I")
            list_stud.append([max(list_id) + 1, self.input_fio.text(), self.num_kurs.text(), self.num_group.text(), cnt_vnut, cnt_vnesh, self.event_list[3], self.event_list[0], self.num_inst.text()])
            list_stud = sorted(list_stud, key=lambda x: x[1].title())  # сортировка студентов по фамилии
            wks2.update(list_stud, f'A1')
            self.parent.download_event()
            self.close()
            self.parent.download_event()  # необходимо перезагрузить таблицу, чтобы добавленный студент увиделся в ней. Внешни
        else:
            pass

    def back_add(self):
        self.Add_Student = Add_Stud(self.parent, self.event_list)
        self.Add_Student.show()
        self.close()


class Add_Student_Baz(QMainWindow): # Класс для добавления студента из базы к событию.
    def __init__(self, parent, event_list, total=[]):
        super().__init__()

        uic.loadUi('qt/only_add.ui', self)

        self.parent = parent
        self.event_list = event_list
        self.list_studs = wks2.get('A:I')

        self.load_table()

        self.back_but.clicked.connect(self.back_add)
        self.search_btn.clicked.connect(self.search_student)
        self.add_btn.clicked.connect(self.add_student)
        self.vibork_but.clicked.connect(self.select_student)
        self.table_students.cellClicked.connect(self.add_to_list)
        self.total_list = total
        self.table_students.horizontalHeader().sectionClicked.connect(self.sort_column)
        self.type_sort = 0
        print(self.total_list)

    def draw_columns(self, list_stud):
        self.table_students.clear()
        self.table_students.setColumnCount(7)

        self.table_students.setRowCount(0)
        self.table_students.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.table_students.setHorizontalHeaderItem(1, QTableWidgetItem("№ Института"))
        self.table_students.setHorizontalHeaderItem(2, QTableWidgetItem("Курс"))
        self.table_students.setHorizontalHeaderItem(3, QTableWidgetItem("Группа"))
        self.table_students.setHorizontalHeaderItem(4, QTableWidgetItem("Кол-во внут."))
        self.table_students.setHorizontalHeaderItem(5, QTableWidgetItem("Кол-во внеш."))
        self.table_students.setHorizontalHeaderItem(6, QTableWidgetItem("Суммарные часы"))
        
        for i, row in enumerate(list_stud):
            print(row)
            self.table_students.setRowCount(

                self.table_students.rowCount() + 1)



            for j, elem in enumerate(row[1:]):

                self.table_students.setItem(

                    i, j, QTableWidgetItem(str(elem)))
                
    def sort_column(self, index):
        self.type_sort += 1
        list_stud = []

        for i in self.list_studs:
            if str(self.event_list[0]) not in str(i[7]).split(';'):
                list_stud.append([i[0], i[1], int(i[8]), int(i[2]), i[3], int(i[4]), int(i[5]), int(i[6]), i[7]])
        list_stud = sorted(list_stud, key=lambda x: x[index+1], reverse=self.type_sort%2)
        print(list_stud, index) 
        self.draw_columns(list_stud)

    def load_table(self):
        
        list_stud = []

        for i in self.list_studs:
            if str(self.event_list[0]) not in str(i[7]).split(';'):
                list_stud.append([i[0], i[1], i[8], i[2], i[3], i[4], i[5], i[6], i[7]])
        
        self.draw_columns(list_stud)

    def add_to_list(self, row, column):
        row_items = []
        for col in range(self.table_students.columnCount()):
            item = self.table_students.item(row, col)
            if item:
                row_items.append(item.text())
        if row_items not in self.total_list:  # убираем повторяющиеся студенты
            self.total_list.append(row_items)
    def search_student(self):
        list_stud = []

        for i in self.list_studs:
            if str(self.event_list[0]) not in str(i[7]).split(';'):
                list_stud.append([i[0], i[1], i[8], i[2], i[3], i[4], i[5], i[6], i[7]])
        search_text = self.input_name.text()
        if search_text == '':
            self.load_table()
            return
        
        new_list = []
        for i in list_stud:
            if search_text.lower() in str(i[1]).lower():
                new_list.append(i)

        self.draw_columns(new_list)
        

    def add_student(self):
        rows = list(set([i.row() for i in self.table_students.selectedItems()]))

        ids = [[self.table_students.item(i, j).text() for j in range(7)] for i in rows] + self.total_list
        # ids = self.total_list[::]
        for j in ids:
            сount = 0
            j = [j[0], j[2], j[3], j[4], j[5], j[6], j[1]]
            for i in range(len(self.list_studs)):
                print(j)
                if j[0] == self.list_studs[i][1]:
                    if self.list_studs[i][7] != str(-1):
                        a = self.list_studs[i][7].split(';')
                        a.append(str(self.event_list[0]))
                        a = ';'.join(a)
                    else: 
                        a = str(self.event_list[0])
                    print(j, self.event_list)
                    self.list_studs[i][4] = int(j[3])+1 if self.event_list[4] == 'Внутреннее' else j[3]
                    self.list_studs[i][5] = int(j[4])+1 if self.event_list[4] == 'Внешнее' else j[4]
                    self.list_studs[i][6] = int(j[5])+int(self.event_list[3])
                    self.list_studs[i][7] = a
                    break
                else:
                    сount += 1
            # if сount == len(ids):
            #     self.list_studs[i] = [None]*8
        print(self.list_studs)
        self.list_studs = sorted(self.list_studs, key=lambda x: x[1].title())  # сортировка студентов по фамилии
        wks2.update(self.list_studs, 'A1')

        self.parent.download_event()  # необходимо перезагрузить таблицу, чтобы добавленный студент увиделся в ней. Внешний
        
        self.close()

    def select_student(self):
        self.Viborka = Viborka(self, self.parent, self.total_list, self.event_list)
        self.Viborka.show()
        self.close()

    def back_add(self):
        self.Add_Student = Add_Stud(self.parent, self.event_list)
        self.Add_Student.show()
        self.close()


class Viborka(QMainWindow):
    def __init__(self, add_baz, parent, total_list, event_list):
        super().__init__()
        uic.loadUi('qt/list_of_vibork.ui', self)
        self.total_list = total_list
        self.parent = parent
        self.add_baz = add_baz
        self.event_list = event_list
        self.draw_columns(total_list)
        self.but_back.clicked.connect(self.back)
        self.delete_student_but.clicked.connect(self.delete_student)

    def draw_columns(self, list_stud):
        self.table_students.clear()
        self.table_students.setColumnCount(7)

        self.table_students.setRowCount(0)
        self.table_students.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.table_students.setHorizontalHeaderItem(1, QTableWidgetItem("№ Института"))
        self.table_students.setHorizontalHeaderItem(2, QTableWidgetItem("Курс"))
        self.table_students.setHorizontalHeaderItem(3, QTableWidgetItem("Группа"))
        self.table_students.setHorizontalHeaderItem(4, QTableWidgetItem("Кол-во внут."))
        self.table_students.setHorizontalHeaderItem(5, QTableWidgetItem("Кол-во внеш."))
        self.table_students.setHorizontalHeaderItem(6, QTableWidgetItem("Суммарные часы"))
        
        for i, row in enumerate(list_stud):
            print(row)
            self.table_students.setRowCount(

                self.table_students.rowCount() + 1)



            for j, elem in enumerate(row):

                self.table_students.setItem(

                    i, j, QTableWidgetItem(str(elem)))
                
    def delete_student(self):
        rows = list(set([i.row() for i in self.table_students.selectedItems()]))

        ids = [[self.table_students.item(i, j).text() for j in range(7)] for i in rows]
        for j in ids:
            self.total_list.remove(j)
        self.draw_columns(self.total_list)


    def back(self):
        self.Add_Student_Baz = Add_Student_Baz(self.parent, self.event_list, self.total_list)
        self.Add_Student_Baz.show()
        self.close()


class NonWifi(QMainWindow): # Заглушка для экрана без интернета
    def __init__(self):
        super().__init__()

        uic.loadUi('qt/non_wifi.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        sheets = gspread.service_account(filename='kay_new.json')
        wks1 = sheets.open("val_event").get_worksheet(0)
        wks2 = sheets.open("val_event").get_worksheet(1)
        all_events = wks1.get("A:G")
        
        path = getattr(sys, '_MEIPASS', os.getcwd())  # Дерриктория внутри exe файла
        d = str(os.getcwd()).replace('\\', '/')  # Запоминаем где были
        os.chdir(path)  # Сменяем рабочудеррикторию, чтобы подгрузить окошки и .env

        load_dotenv()
        TOKEN = os.getenv('TOKEN_GIT')
        url = os.getenv('GIT_LINK')
        repo_owner = os.getenv('REPO_OWNER')  # Имя владельца репозитория
        repo_name = os.getenv('REPO_NAME')   # Имя репозитория
        version_installed = os.getenv('VERSION_APP')

        main = MainWindow()

        main.show()
    except Exception:
        path = getattr(sys, '_MEIPASS', os.getcwd())  # Дерриктория внутри exe файла
        os.chdir(path)  # Сменяем рабочудеррикторию, чтобы подгрузить окошки и .env
        non_wifi = NonWifi()
        non_wifi.show()
    
    sys.exit(app.exec())