import sys

import gspread

from PyQt5 import uic

from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget


class MainWindow(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('qt/меин.ui', self)

        self.create_event.clicked.connect(self.openCreate)
        self.events_but.clicked.connect(self.events)

    def openCreate(self):
        self.CreateEvent = CreateEvent(self, '')
        self.CreateEvent.show()
        self.close()

    def events(self):
        self.Events_List = Events_List(self, '')
        self.Events_List.show()
        self.close()


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
        try:
            wks1.update([[max(list_id) + 1, name_event, date_event, hours_event, "Внутреннее" if vnut_radio else "Внешнее", author_event]], f'A{len(list_id)+2}')
        except ValueError:
            wks1.update([[1, name_event, date_event, hours_event, "Внутреннее" if vnut_radio else "Внешнее", author_event]], f'A2')
        all_events = wks1.get("A:F")
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

        for i in all_events[1:]:
            self.list_events.addItem(f"{str(i[1])} - {str(i[2])}")

    def back_main(self):
        self.myclose = False
        self.Main = MainWindow(self, '')
        self.Main.show()
        self.close()

    def download_event(self):
        self.list_stud = wks2.get("A:H")

        self.event.setColumnCount(3)

        self.event.setRowCount(0)
        self.event.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.event.setHorizontalHeaderItem(1, QTableWidgetItem("Курс"))
        self.event.setHorizontalHeaderItem(2, QTableWidgetItem("Группа"))

        # list_id = wks2.col_values(8)
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                ide = i[0]
                break

        list_stud = []
        for i in self.list_stud:
            if str(ide) in str(i[-1]).split(';'):
                list_stud.append(i)

        # Заполняем таблицу элементами

        for i, row in enumerate(list_stud):

            self.event.setRowCount(

                self.event.rowCount() + 1)

            for j, elem in enumerate(row[1:]):

                self.event.setItem(

                    i, j, QTableWidgetItem(str(elem)))
                
    def delete_event_window(self):
        self.delete_window = DeleteWindow(self, "Вы дествительно хотети удалить выбранное мероприятие?")
        self.delete_window.show()

    def delete_stud_window(self):
        rows = list(set([i.row() for i in self.event.selectedItems()]))

        ids = [[self.event.item(i, j).text() for j in range(3)] for i in rows]
        s = 'Вы дествительно хотети удалить выбранного студента?' if len(ids)==1 else 'Вы дествительно хотети удалить выбранных студентов?'
        self.delete_window = DeleteWindow(self, s)
        self.delete_window.show()
                
    def delete_event(self):
        global wks1, wks2, all_events
        selected_value = self.list_events.currentText().split(' - ')[0]

        ide = 0
        id_for_s = 0
        for i in all_events[1:]:
            if str(i[1]) == str(selected_value):
                id_for_s = i[0]
                break
            ide += 1
        
        cnt = 1
        for i in self.list_stud:
            events_s = i[-1].split(';')
            try:
                events_s.remove(str(id_for_s))
                events_s = ';'.join(events_s)
                wks2.update([[events_s]], f'H{cnt}')
            except ValueError:
                pass
            cnt += 1
        
        self.list_events.setCurrentIndex(ide+1)
        self.list_events.removeItem(int(ide))
        wks1.delete_rows(ide+2)
        self.event.clear()
        all_events = wks1.get("A:F")

    def add_student(self):
        event_list = 0
        selected_value = self.list_events.currentText().split(' - ')[0]
        ide = 0
        all_events = wks1.get("A:F")
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
                    
                    events_s = self.list_stud[i][-1].split(';')
                    events_s.remove(str(ev[0]))
                    events_s = ';'.join(events_s)
                    dlit = str(int(self.list_stud[i][6]) - int(ev[3]))
                    cnt_vnut = int(self.list_stud[i][4]) - 1 if ev[4] == 'Внутреннее' else self.list_stud[i][4]
                    cnt_vnesh = int(self.list_stud[i][5]) - 1 if ev[4] == 'Внешнее' else self.list_stud[i][5]
                    
                    arr = [None, 
                          None, 
                          None, 
                          None, 
                          cnt_vnut,
                          cnt_vnesh,
                          dlit,
                          events_s]
                    self.list_stud[i] = arr
                    break
                else:
                    сount += 1
            if сount == len(ids):
                self.list_stud[i] = [None]*8
        wks2.update(self.list_stud, 'A1')
        self.download_event()


class DeleteWindow(QMainWindow): # Класс для удаления события.
    def __init__(self, parent, mes):
        super().__init__()

        uic.loadUi('qt/delete_pod.ui', self)

        self.parent = parent
        self.label.setText(mes)
        self.mes = mes

        self.yes_but.clicked.connect(self.delete_event)
        self.no_but.clicked.connect(self.back_main)

    def delete_event(self):
        if self.mes == 'Вы дествительно хотети удалить выбранное мероприятие?':
            self.parent.delete_event()
        self.parent.delete_student()
        self.close()

    def back_main(self):
        self.close()


class Add_Stud(QMainWindow): # Класс для добавления нового студента к событию.
    def __init__(self, parent, event_list):
        super().__init__()

        uic.loadUi('qt/add_s.ui', self)

        self.new_s.clicked.connect(self.new_student)
        self.iz_baz_but.clicked.connect(self.iz_baz)

        self.parent = parent
        self.event_list = event_list

    def new_student(self):
        self.Create_And_Add = Create_And_Add(self.parent, self.event_list)
        self.Create_And_Add.show()
        self.close()

    def iz_baz(self):
        self.Add_Student_Baz = Add_Student_Baz(self.parent, self.event_list)
        self.Add_Student_Baz.show()
        self.close()
        

class Create_And_Add(QMainWindow): # Класс для создания нового студента и добавления его к событию.
    def __init__(self, parent, event_list):
        super().__init__()

        uic.loadUi('qt/create_and_add.ui', self)

        self.add_but.clicked.connect(self.create_and_add)
        self.back_but.clicked.connect(self.back_add)

        self.parent = parent
        self.event_list = event_list

    def create_and_add(self):
        if self.input_name.text() and self.input_cours.text() and self.input_group.text():
            list_id = [int(i) for i in wks2.col_values(1)]
            cnt_vnut = 0 if self.event_list[4] != 'Внутреннее' else 1
            cnt_vnesh = 0 if self.event_list[4]!= 'Внешнее' else 1
            wks2.update([[max(list_id) + 1, self.input_name.text(), self.input_cours.text(), self.input_group.text(), cnt_vnut, cnt_vnesh, self.event_list[3], self.event_list[0]]], f'A{len(list_id)+1}')
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
    def __init__(self, parent, event_list):
        super().__init__()

        uic.loadUi('qt/only_add.ui', self)

        self.parent = parent
        self.event_list = event_list
        self.list_studs = wks2.get('A:H')

        self.load_table()

        self.back_but.clicked.connect(self.back_add)
        self.search_but.clicked.connect(self.search_student)
        self.add_but.clicked.connect(self.add_student)

    def draw_columns(self, list_stud):
        self.table_students.clear()
        self.table_students.setColumnCount(6)

        self.table_students.setRowCount(0)
        self.table_students.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self.table_students.setHorizontalHeaderItem(1, QTableWidgetItem("Курс"))
        self.table_students.setHorizontalHeaderItem(2, QTableWidgetItem("Группа"))
        self.table_students.setHorizontalHeaderItem(3, QTableWidgetItem("Кол-во внут."))
        self.table_students.setHorizontalHeaderItem(4, QTableWidgetItem("Кол-во внеш."))
        self.table_students.setHorizontalHeaderItem(5, QTableWidgetItem("Суммарные часы"))

        for i, row in enumerate(list_stud):

            self.table_students.setRowCount(

                self.table_students.rowCount() + 1)

            for j, elem in enumerate(row[1:]):

                self.table_students.setItem(

                    i, j, QTableWidgetItem(str(elem)))

    def load_table(self):
        
        list_stud = []

        for i in self.list_studs:
            if str(self.event_list[0]) not in str(i[-1]).split(';'):
                list_stud.append(i)
        
        self.draw_columns(list_stud)
                
    def search_student(self):
        search_text = self.input_name.text()
        if search_text == '':
            self.load_table()
            return
        
        new_list = []
        for i in self.list_studs:
            if search_text.lower() in str(i[1]).lower():
                new_list.append(i)

        self.draw_columns(new_list)

    def add_student(self):
        rows = list(set([i.row() for i in self.table_students.selectedItems()]))

        ids = [[self.table_students.item(i, j).text() for j in range(6)] for i in rows]
        for i in range(len(self.list_studs)):
            сount = 0
            for j in ids:
                if j[0] == self.list_studs[i][1]:
                    
                    a = self.list_studs[i][-1].split(';')
                    a.append(str(self.event_list[0]))
                    a = ';'.join(a)
                    arr = [None, 
                          None, 
                          None, 
                          None, 
                          int(j[3])+1 if self.event_list[4] == 'Внутреннее' else j[3],
                          int(j[4])+1 if self.event_list[4] == 'Внешнее' else j[4],
                          int(j[5])+int(self.event_list[3]),
                          a]
                    self.list_studs[i] = arr
                    break
                else:
                    сount += 1
            if сount == len(ids):
                self.list_studs[i] = [None]*8
        wks2.update(self.list_studs, 'A1')

        self.parent.download_event()  # необходимо перезагрузить таблицу, чтобы добавленный студент увиделся в ней. Внешний
        self.close()

    def back_add(self):
        self.Add_Student = Add_Stud(self.parent, self.event_list)
        self.Add_Student.show()
        self.close()


class NonWifi(QMainWindow): # Заглушка для экрана без интернета
    def __init__(self):
        super().__init__()

        uic.loadUi('qt/non_wifi.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # try:
    sheets = gspread.service_account(filename='kay_new.json')
    wks1 = sheets.open("val_event").get_worksheet(0)
    wks2 = sheets.open("val_event").get_worksheet(1)
    all_events = wks1.get("A:F")
    main = MainWindow()

    main.show()
    # except Exception:
    #     non_wifi = NonWifi()
    #     non_wifi.show()
    
    sys.exit(app.exec())