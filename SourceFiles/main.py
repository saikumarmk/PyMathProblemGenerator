from mainwindow import Ui_MainWindow  # importing our generated file
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
from wolframclient.language import wl
from wolframclient.language import wlexpr
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import Global
from PyQt5.QtGui import QIcon, QPixmap
import sys
import oauthlib
import oauthlib.oauth1
import wolframclient.utils.json
import packaging.specifiers
import zmq
import packaging.requirements

class mywindow(QtWidgets.QMainWindow):
 
	def __init__(self):

		super(mywindow, self).__init__()
		print(session.evaluate('''Directory[]'''))
		self.imageQuestion = False
		self.setFixedSize(1200,700)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.white = False
		self.textcolor = "white"
		self.bg = self.palette().window().color()
		self.cl = (self.bg.redF(),self.bg.greenF(), self.bg.blueF()) # Makes the color of the textbox the same as the app
		if self.cl[0] > 0.5 and self.cl[1] > 0.5 and self.cl[2] >0.5:
			self.white = True
			self.textcolor = "black"

		# https://stackoverflow.com/questions/41247109/pyqt-how-to-switch-widgets-in-qstackedwidget
		# We can set up button functionality here instead.
		self.ui.toMainMenu.clicked.connect(self.refreshMenu)
		# then at either point regenerate the question by running the function

		# self.whatever.clicked.connect(self.newQuestion)
		self.ui.toMainMenu_2.clicked.connect(self.refreshMenu)
		self.ui.toMainMenu_3.clicked.connect(self.refreshMenu)

		self.ui.toSettings.clicked.connect(self.refreshSettings)

		self.ui.toQuestion.clicked.connect(self.newQuestion)
		self.ui.toQuestion_2.clicked.connect(self.deleteOldQuestion)

		self.ui.toAnswer.clicked.connect(lambda : self.ui.stackedWidget.setCurrentIndex(3))
		self.ui.difficultybox.addItems(["Easy","Normal","Hard"])
		topics=session.evaluate('''Keys[questionRepo["Easy"]]''')
		self.ui.topicbox.addItems(list(topics))

		# to access difficulty do self.ui.difficultybox.currentText()

	# For when you exit a menu and a question has been generated, this will remove the previous question and answer.
	def refresh(self):
		if self.ui.verticalLayout_5.count() < 2:
			return
		else:
			if self.ui.verticalLayout.count() == 3:
				self.ui.verticalLayout.removeWidget(self.label1)
				self.label1.deleteLater()
				self.label1 = None

			qBox = self.ui.verticalLayout_5.itemAt(1)
			self.ui.verticalLayout_5.removeItem(qBox)

			self.ui.verticalLayout.removeWidget(self.canvasA)
			self.canvasA.deleteLater()
			self.canvasA = None


	def refreshSettings(self):
		self.ui.stackedWidget.setCurrentIndex(1)
		self.refresh()

	def refreshMenu(self):
		self.ui.stackedWidget.setCurrentIndex(0)
		self.refresh()


	def newQuestion(self):

		topic=self.ui.topicbox.currentText()
		difficulty=self.ui.difficultybox.currentText()
		chk = session.evaluate(wlexpr('''TopicLength["'''+str(topic)+'''","'''+str(difficulty)+'''"]'''))
		if chk == 0:
			return
		self.ui.stackedWidget.setCurrentIndex(2) # Go to question menu


		qa=session.evaluate(wlexpr('''evalQuestion["'''+str(topic)+'''","'''+str(difficulty)+'''"]'''))
		q =qa[0]
		a=qa[1]
		img = qa[2]

		self.questionDisplay = QtWidgets.QHBoxLayout()
		self.questionDisplay.setObjectName("questionDisplay")
		spaceLeft= QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		self.questionDisplay.addItem(spaceLeft)

		self.question = Figure(facecolor=self.cl,edgecolor=self.cl)
		self.canvasQ = FigureCanvas(self.question)
		self.questionDisplay.addWidget(self.canvasQ)

		self.question.suptitle(q,
				x=0.0, y=0.5, 
				horizontalalignment='left',
				verticalalignment='bottom',
				fontsize=10,
				color=self.textcolor)

		self.canvasQ.draw()

		spaceRight = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		self.questionDisplay.addItem(spaceRight)
		self.ui.verticalLayout_5.addLayout(self.questionDisplay)		



		self.answer = Figure(facecolor=self.cl,edgecolor=self.cl)
		self.canvasA = FigureCanvas(self.answer)
		self.ui.verticalLayout.addWidget(self.canvasA)
		self.answer.suptitle(a,
				x=0.0, y=0.6, 
				horizontalalignment='left',
				verticalalignment='top',
				fontsize=10,
				color=self.textcolor)

		self.canvasA.draw()

		# Image handling, if there is a 0 that means there is no image, otherwise do:
		if img != 0:
			self.imageQuestion = True
			self.label1 = QtWidgets.QLabel(self)
			self.pixmap1 = QPixmap(img)
			self.label1.setPixmap(self.pixmap1)
			self.resize(self.pixmap1.width(), self.pixmap1.height())
			self.ui.verticalLayout.addWidget(self.label1)
			self.show()

		else:
			self.imageQuestion = False



		
		# add bit with getting information from mathematica then setting all the required fields

	def deleteOldQuestion(self):

		qBox = self.ui.verticalLayout_5.itemAt(1)
		self.ui.verticalLayout_5.removeItem(qBox)


		self.ui.verticalLayout.removeWidget(self.canvasA)
		self.canvasA.deleteLater()
		self.canvasA = None

		if self.imageQuestion == True:

			self.ui.verticalLayout.removeWidget(self.label1)
			self.label1.deleteLater()
			self.label1 = None


		self.newQuestion()





if __name__ == '__main__':
	session = WolframLanguageSession()
	commands = [
	'''Get["definitions.mx"];''',
	'''questionRepo=Quiet@Import["repo.mx"];'''
	]
	for i in commands:
		session.evaluate(wlexpr(i))
		
	app = QtWidgets.QApplication([])
	application = mywindow()
	application.show()
	try:
		sys.exit(app.exec())
	except SystemExit:
		session.terminate()		
		print("Wolfram Link has been terminated.")

