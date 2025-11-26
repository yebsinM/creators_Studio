import os
import torch
import subprocess
import platform
from dotenv import load_dotenv
import requests
import shutil
import threading
import sys
import math 
import re
import psutil
from datetime import datetime
import uuid
import json
from pathlib import Path 
from transformers import AutoTokenizer, AutoModelForCausalLM
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGraphicsView, QGraphicsScene, QDockWidget,
    QListWidget, QTextEdit, QLineEdit, QComboBox, QColorDialog,
    QInputDialog, QMessageBox, QMenu, QStatusBar, QApplication,
    QFileSystemModel, QTreeView, QSplitter, QToolBar, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsItem, QSlider,
    QFileDialog, QScrollArea, QGroupBox, QRadioButton, QCheckBox,
    QSizePolicy, QTabWidget, QTextEdit, QDialog,
    QPlainTextEdit, QListWidgetItem, QStyledItemDelegate, QToolBox, 
    QScrollArea, QButtonGroup, QGridLayout, QToolBar, QStatusBar,  
    QGraphicsPathItem, QGraphicsLineItem, QGraphicsItemGroup,QFrame, QGraphicsTextItem
)

from PySide6.QtSvg import QSvgGenerator

from PySide6.QtGui import (
    QIcon, QAction, QCursor, QColor, QBrush, QTextCursor, QFont,
    QPen, QPainter, QTextFormat, QSyntaxHighlighter, QTextCharFormat, 
    QPalette, QShortcut, QKeySequence, QPixmap, QPainter, 
    QLinearGradient, QRadialGradient, QMouseEvent, QPainterPath, QPolygonF
)
from PySide6.QtCore import (
    Qt, QSize, QPoint, Signal, QDir, QRectF, QSettings, QThread, 
    Signal as pyqtSignal, QEvent, QTimer, QRect, QRegularExpression, QDateTime, QPointF
)