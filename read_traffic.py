# -*- coding: shift_jis -*-
from xml.etree import ElementTree
traffic = ElementTree.parse('traffic.xml')#読み取らせる
root = traffic.getroot()
