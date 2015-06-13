#!/usr/bin/env python
# -*- encoding: utf-8 -*-

""" USB Rubber Duck python encoder """

import sys
import os.path
import pprint
import codecs

__author__ 		= "GoldraK & Roger Serentill"
__credits__ 	= "GoldraK & Roger Serentill"
__version__ 	= "0.1.1"
__maintainer__ 	= "GoldraK & Roger Serentill"
__email__ 		= "goldrak@gmail.com, hello@rogerserentill.com"
__status__ 		= "Development"

class Encoder:

	def __init__(self, debug=False):
		self.version = 0.1
		self.debug = debug
		self.bocabits = bytearray()
		self.inputFile = ""
		self.outputFile = "inject.bin"
		self.keyboardLayout = "us"
		self.helper = """Usage: duckencode -i [file ..]			encode specified file
   or: duckencode -i [file ..] -o [file ..]	encode to specified file

Arguments:
   -i [file ..] 		Input File
   -o [file ..] 		Output File
   -l [file ..] 		Keyboard Layout (us/es/it/pt/no/ru/gb ...)

Script Commands:
   ALT [key name] (ex: ALT F4, ALT SPACE)
   CTRL | CONTROL [key name] (ex: CTRL ESC)
   CTRL-ALT [key name] (ex: CTRL-ALT DEL)
   CTRL-SHIFT [key name] (ex: CTRL-SHIFT ESC)
   DEFAULT_DELAY | DEFAULTDELAY [Time in millisecond * 10] (change the delay between each command)
   DELAY [Time in millisecond * 10] (used to overide temporary the default delay)
   GUI | WINDOWS [key name] (ex: GUI r, GUI l)
   REM [anything] (used to comment your code, no obligation :) )
   ALT-SHIFT (swap language)
   SHIFT [key name] (ex: SHIFT DEL)
   STRING [any character of your layout]
   REPEAT [Number] (Repeat last instruction N times)
   [key name] (anything in the keyboard.properties)"""

   		print "Duck Encoder "+str(self.version)+" by Roger Serentill & GoldraK"

	# The main function to compile the input file and encode it to the output file
	def compile(self, arguments):
		self.__handleArguments(arguments)

		instructions = self.__read_file()

		# Let the games begin. Reading the input file and handling each instruction (line by line)
		for (command, arg) in instructions:

			# Delay command
			if command == 'DELAY':
				delay = int(arg)
				while delay > 0:
					self.__addByte(['0',]);
					if delay > 255:
						self.__addByte(['255',]);
						delay = delay - 255;
					else:
						self.__addByte([str(delay),]);
						delay = 0;

			# GUI or Windows key
			elif command == 'WINDOWS' or command == 'GUI':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					self.__addByte([self.props["MODIFIERKEY_LEFT_GUI"],])
				else:
					self.__addByte([self.props["MODIFIERKEY_LEFT_GUI"],])						
					self.__addByte(['0',])

			# CTRL key
			elif command == 'CONTROL' or command == 'CTRL':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					self.__addByte([self.props["MODIFIERKEY_CTRL"],])
				else:
					self.__addByte([self.props["KEY_LEFT_CTRL"],])						
					self.__addByte(['0',])

			# ALT key
			elif command == 'ALT':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					self.__addByte([self.props["MODIFIERKEY_ALT"],])
				else:
					self.__addByte([self.props["KEY_LEFT_ALT"],])						
					self.__addByte(['0',])

			# SHIFT key
			elif command == 'SHIFT':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					self.__addByte([self.props["MODIFIERKEY_SHIFT"],])
				else:
					self.__addByte([self.props["KEY_LEFT_SHIFT"],])						
					self.__addByte(['0',])

			# CTRL-ALT keys combination
			elif command == 'CTRL-ALT':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					# Add values from each key to get the resultant byte
					bytectrlalt = hex((int(self.props["MODIFIERKEY_CTRL"], 16)) + (int(self.props["MODIFIERKEY_ALT"], 16)))
					# Format the resultant value to 0xHH
					bytectrlalt = ("0x{:02x}".format(int(bytectrlalt, 16)))
					self.__addByte([bytectrlalt,])

			# CTRL-SHIFT keys combination
			elif command == 'CTRL-SHIFT':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					# Add values from each key to get the resultant byte
					bytectrlalt = hex((int(self.props["MODIFIERKEY_CTRL"], 16)) + (int(self.props["MODIFIERKEY_SHIFT"], 16)))
					# Format the resultant value to 0xHH
					bytectrlalt = ("0x{:02x}".format(int(bytectrlalt, 16)))
					self.__addByte([bytectrlalt,])

			# COMMAND-OPTION keys combination (Mac OS)
			elif command == 'COMMAND-OPTION':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					# Add values from each key to get the resultant byte
					bytectrlalt = hex((int(self.props["MODIFIERKEY_LEFT_GUI"], 16)) + (int(self.props["MODIFIERKEY_ALT"], 16)))
					# Format the resultant value to 0xHH
					bytectrlalt = ("0x{:02x}".format(int(bytectrlalt, 16)))
					self.__addByte([bytectrlalt,])

			# ALT-SHIFT keys combination
			elif command == 'ALT-SHIFT':
				if arg:
					# Add the instruction argument(s) as byte(s)
					self.__addByte([self.__strInstrToByte(arg),])
					# Add values from each key to get the resultant byte
					bytectrlalt = hex((int(self.props["MODIFIERKEY_LEFT_ALT"], 16)) + (int(self.props["MODIFIERKEY_SHIFT"], 16)))
					# Format the resultant value to 0xHH
					bytectrlalt = ("0x{:02x}".format(int(bytectrlalt, 16)))
					self.__addByte([bytectrlalt,])
				else:
					# Add the instruction ALT
					self.__addByte([self.props["KEY_LEFT_ALT"],])
					# Add values from each key to get the resultant byte
					bytectrlalt = hex((int(self.props["MODIFIERKEY_LEFT_ALT"], 16)) + (int(self.props["MODIFIERKEY_SHIFT"], 16)))
					# Format the resultant value to 0xHH
					bytectrlalt = ("0x{:02x}".format(int(bytectrlalt, 16)))
					self.__addByte([bytectrlalt,])

			# ALT-TAB keys combination
			elif command == 'ALT-TAB':
				if command and not arg:
					self.__addByte([self.props["KEY_TAB"],])
					self.__addByte([self.props["MODIFIERKEY_LEFT_ALT"],])
					self.__addByte([bytectrlalt,])


			# STRING instruction
			elif command == 'STRING':
				for c in arg:
					data_string = self.__charToByte(c)
					if type(data_string) is list:
						self.__addByte(data_string)
					else:
						self.__addByte([self.__charToByte(c),])
						self.__addByte(['0',])
			else:
				self.__addByte([self.__strInstrToByte(command),])
				self.__addByte(['0',])


		f = open(self.outputFile, 'wb')
		f.write(self.bocabits)
		f.close()

	# Handling the arguments of the script
	def __handleArguments(self, argument):
		# Possible keyboard layouts
		keyboards = ["be", "br", "ca", "ch", "de", "dk", "es", "fi", "fr", "gb", "hr", "it", "no", "pt", "ru", "si", "sv", "tr", "us"]
		if "-i" not in argument:
			while self.inputFile == "":
				print self.helper, "\n"
				self.inputFile = raw_input("Type the input file: ")
		for i,arg in enumerate(argument):
			if arg == argument[0]:
				continue
			elif arg == "--help" or arg == "-h":
				print self.helper
			elif arg == "-i": # Input file
				self.inputFile = argument[i+1]
				i += 1
			elif arg == "-o": # Output file
				self.outputFile = argument[i+1]
				i += 1
			elif arg == "-l": # Keyboard layout
				if argument[i+1] in keyboards:
					self.keyboardLayout = argument[i+1]
				else:
					while argument[i+1] not in keyboards:
						self.keyboardLayout = raw_input("Invalid keyboard layout, please re-enter it (us/es/it/pt/no/ru/gb ...): ")
				i += 1
			elif arg == "-d": # Debug
				self.debug = True

		self.props = self.__loadProperties(self.keyboardLayout)

	def __read_file(self):
		#Instrution dic
		instruntions_dic = {"WINDOWS","GUI","CONTROL","CTRL","ALT","SHIFT","CTRL-ALT","CTRL-SHIFT","COMMAND-OPTION","ALT-SHIFT","ALT-TAB","DELAY","DEFAULT-DELAY","DEFAULTDELAY","DEFAULT_DELAY","ENTER","REPEAT","REM","STRING","ESCAPE","DEL","BREAK","DOWN","UP","DOWNARROW","UPARROW","LEFTARROW","RIGHTARROW","MENU","PLAY","PAUSE","STOP","MUTE","VULUMEUP","VOLUMEDOWN","SCROLLLOCK","NUMLOCK","CAPSLOCK"}
		# Check if the input file exists and if we can open it in read mode
		if os.path.isfile(self.inputFile):
			try:
				if self.keyboardLayout == "es":
					file_read = codecs.open(self.inputFile, 'r', 'utf-8')
				else:
					file_read = open(self.inputFile, 'r')
			except IOError:
				print 'ERROR: Cannot open', inputFile
				sys.exit(-1)
		else:	
			print "ERROR: The given input file ", self.inputFile, " doesn't exist!"
			sys.exit(-1)

		instructions = []; last_ins = ""; delay = -1; current_ins = []
		# Handle REPEAT and DEFAULT-DELAY instructions
		for line in file_read:
			# Ignore empty lines
			if line != '\n':
				# Ignore the comments
				if '//'  not in line:
					# Check if the command has any arguments
					if " " in line:
						current_ins = line.strip().split(None, 1)
						if current_ins[0] not in instruntions_dic:
							print "Instrution not found "+line.strip()
							continue
					else:
						if line.strip() in instruntions_dic:
							current_ins = [line.strip(), None]
							#instructions.append(current_ins)
						else:
							print "Instrution not found "+line.strip()
							continue

					if current_ins[0] == "REPEAT":
						for i in range(current_ins[1]):
							if last_ins != "":
								instructions.append(last_ins)
								if delay != -1:
									instructions.append(["DELAY", delay])
							else:
								print "ERROR: REPEAT can't be the first instruction"
								sys.exit(-1)
					elif current_ins[0] == "DEFAULT_DELAY" or current_ins[0] == "DEFAULTDELAY" or current_ins[0] == "DEFAULT-DELAY":
						delay = int(current_ins[1])
					else:
						instructions.append(current_ins)
						if delay != -1:
							instructions.append(["DELAY", delay])
						# Keep the previous instruction in case we need to repeat it
						last_ins = current_ins
		if delay != -1:
			instructions.pop()

		file_read.close()
		return instructions

	# Loading the default properties and the properties of the layout keypoard
	def __loadProperties(self, lang):
		props_def = {}
		props_lang = {}
		file_props_def = 'resources/keyboard.properties'
		file_props_lng = 'resources/'+lang+'.properties'

		# Check if the default properties file exists and if we can open it in read mode
		if os.path.isfile(file_props_def):
			try:
				file_read = open(file_props_def, 'r')
				for line in file_read:
					if line != '\n':
						if line[:2] != '//':
							temp_list = line.split("=")
							temp_list[0] = temp_list[0].strip()
							temp_list[1] = temp_list[1].strip() 
							props_def.update(dict(zip(temp_list[0::2], temp_list[1::2])))
			except IOError:
				print 'ERROR: Cannot open', file_props_def
				sys.exit(-1)
		else:
			print "ERROR: The properties file ", file_props_def, " doesn't exist!"
			sys.exit(-1)

		# Check if the keyboard layout properties file exists and if we can open it in read mode
		if os.path.isfile(file_props_lng):
			try:
				file_read = open(file_props_lng, 'r')
				for line in file_read:
					if line != '\n':
						if '//'  not in line:
							temp_list = line.split("=")
							temp_list[0] = temp_list[0].strip()
							if ',' in temp_list[1]:
								temp_list[1] = temp_list[1].split(',')
								temp_list[1][0] =  props_def[temp_list[1][0].strip()]
								temp_list[1][1] =  props_def[temp_list[1][1].strip()]
							else:
								temp_list[1] = props_def[temp_list[1].strip()]
							props_lang.update(dict(zip(temp_list[0::2], temp_list[1::2])))
			except IOError:
				print 'ERROR: Cannot open', file_props_lng
				sys.exit(-1)
		else:
			print "ERROR: The keyboard layot properties file ", file_props_lng, " doesn't exist!"
			sys.exit(-1)

		# Combine both dictionaries in one containing all the properties
		props_def.update(props_lang)

		return props_def

	def __strInstrToByte(self,inst):
		dict_strByte = {"ESCAPE":"ESC","DEL":"DELETE","BREAK":"PAUSE","CONTROL":"CTRL","DOWNARROW":"DOWN","UPARROW":"UP","LEFTARROW":"LEFT","RIGHTARROW":"RIGHT","MENU":"UP","WINDOWS":"GUI","PLAY":"MEDIA_PLAY_PAUSE","PAUSE":"MEDIA_PLAY_PAUSE","STOP":"MEDIA_STOP","MUTE":"MEDIA_MUTE","VULUMEUP":"MEDIA_VOLUME_INC","VOLUMEDOWN":"MEDIA_VOLUME_DEC","SCROLLLOCK":"SCROLL_LOCK","NUMLOCK":"NUM_LOCK","CAPSLOCK":"CAPS_LOCK"}
		inst = inst.strip().upper()
		if self.props["KEY_"+inst]:
			return self.props["KEY_" + inst]
		elif self.props["KEY_" + dict_strByte[inst]]:
			return self.props["KEY_" + dict_strByte[inst]]
		else:
			return self.__charToByte(inst[0])

	def __charToByte(self, c):
		return self.__codeToBytes(self.__charToCode(c))

	def __charToCode(self, c):
		code = ""
		if ord(c) < 128:
			code = "ASCII_" + ("{:02x}".format(ord(c))) #String to hex
		elif ord(c) < 256:
			code = "ISO_8859_1_" + ("{:02x}".format(ord(c))) #String to hex
		else:
			code = "UNICODE_" + ("{:02x}".format(ord(c))) #String to hex

		return code.upper()

	def __codeToBytes(self, st):
		return self.props[st];

	def __addByte(self,st_list):
		for st in st_list:
			if st[:2] == '0x':
				self.bocabits += self.bocabits.fromhex(st[2:])
			else:
				self.bocabits.append(int(st))


if __name__ == "__main__":
	p = Encoder()
	p.compile(sys.argv)
