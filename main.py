from model import modeling
from ui.smo_ui import Ui_Dialog
from ui.output import Ui_Dialog_Output
from PyQt5.QtWidgets import QDialog, QApplication
import sys
from model import servers


class MyUiDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.output = UiOutput()
        self.radioButton.toggled.connect(self.choice)
        self.radioButton_2.toggled.connect(self.choice)
        self.pushButton.pressed.connect(self.btn_click)
        self.pushButton_2.pressed.connect(self.clear_data)

    def choice(self):
        if self.radioButton.isChecked():
            self.lineEdit_5.setDisabled(True)
            self.lineEdit_6.setDisabled(True)
            self.lineEdit.setDisabled(False)
            self.lineEdit_2.setDisabled(False)
            self.lineEdit_3.setDisabled(False)
            self.lineEdit_4.setDisabled(False)
        else:
            self.lineEdit.setDisabled(True)
            self.lineEdit_2.setDisabled(True)
            self.lineEdit_3.setDisabled(True)
            self.lineEdit_4.setDisabled(True)
            self.lineEdit_5.setDisabled(False)
            self.lineEdit_6.setDisabled(False)

    def clear_data(self):
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.textBrowser.clear()

    def check_data(self, value):
        if value == "":
            self.textBrowser.append("Значения не должны быть пустыми.")

        else:
            temp = eval(value)
            if temp < 0:
                self.textBrowser.append("Значения не должны быть меньше 0.")
            else:
                return temp

    def btn_click(self):
        self.textBrowser.clear()

        if not self.radioButton.isChecked() and not self.radioButton_2.isChecked():
            self.textBrowser.append("Выберите закон распределения.")
            return

        elif self.radioButton.isChecked():
            mode = self.radioButton.text().replace(' ', '')
            tz_min = self.check_data(self.lineEdit.text())
            if tz_min is None:
                return

            tz_max = self.check_data(self.lineEdit_2.text())
            if tz_max is None:
                return

            ts_min = self.check_data(self.lineEdit_4.text())
            if ts_min is None:
                return

            ts_max = self.check_data(self.lineEdit_3.text())
            if ts_max is None:
                return

            count_s1, count_s2, denied_req, total_req, dt_s1, dt_s2, p0, p1, p2, p_otk, q, s, t_p0, \
            t_p1, t_p2, t_q, t_s, t_k, t_p_otk, mode = modeling({"tz_min": tz_min, "tz_max": tz_max,
                                                                 "ts_min": ts_min, "ts_max": ts_max, "mode": mode})

        else:
            mode = self.radioButton_2.text().replace(' ', '')
            t_obr = self.check_data(self.lineEdit_5.text())
            if t_obr is None:
                return

            elif t_obr == 0:
                self.textBrowser.append("Тобр не должно быть равным 0.")

            _lambda = self.check_data(self.lineEdit_6.text())
            if _lambda is None:
                return

            elif _lambda == 0:
                self.textBrowser.append("Lambda не должна быть равной 0.")

            if t_obr == 0 and _lambda == 0:
                return

            count_s1, count_s2, denied_req, total_req, dt_s1, dt_s2, p0, p1, p2, p_otk, q, s, t_p0, \
            t_p1, t_p2, t_q, t_s, t_k, t_p_otk, mode = modeling({"t_obr": t_obr, "lambda": _lambda, "mode": mode})

        if mode == "Линейный":
            _type = "Линейный закон распределения"

        else:
            _type = "Экспоненциальный закон распределения"

        self.output.textBrowser.append(f"{_type}\n"
                                       f"{'--' * len(_type)}\n"
                                       "Результат работы СМО за час:\n"
                                       f"1-ый сервер обработал {count_s1} заявок, 2-ой сервер обработал {count_s2} заявок.\n"
                                       f"Время простоя 1-ого сервера {round(dt_s1 // 60 % 60)} минут {round(dt_s1 % 60)} секунд, "
                                       f"2-ого сервера {round(dt_s2 // 60 % 60)} минут {round(dt_s2 % 60)} секунд.\n"
                                       f"Общее число необслуженных заявок составило {denied_req}.\nОбщее число заявок {total_req}.\n"
                                       f"Характеристики во время моделирования СМО:\n"
                                       f"P0 = {round(p0, 5)}\nP1 = {round(p1, 5)}\nP2 = {round(p2, 5)}\nP отк = {round(p_otk, 5)}\nQ = {round(q, 5)}\n"
                                       f"S = {round(s, 5)}\nK = {round(0 * p0 + 1 * p1 + 2 * p2, 5)}\n"
                                       f"Сумма вероятностей (P0 + P1 + P2) = {round(p0 + p1 + p2, 5)}.\n\n"
                                       f"Теоретические характеристики СМО:\n"
                                       f"P0 = {round(t_p0, 5)}\nP1 = {round(t_p1, 5)}\nP2 = {round(t_p2, 5)}\nP отк = {round(t_p_otk, 5)}\nQ = {round(t_q, 5)}\n"
                                       f"S = {round(t_s, 5)}\nK = {round(t_k, 5)}\n\n")

        self.output.show()
        servers.clear()


class UiOutput(QDialog, Ui_Dialog_Output):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.pushButton.pressed.connect(self.clear_window)

    def clear_window(self):
        self.textBrowser.clear()


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    window = MyUiDialog()
    window.show()
    sys.exit(app.exec_())
